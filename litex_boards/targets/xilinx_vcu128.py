#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Fei Gao <feig@princeton.edu>
# Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2022 Jiajie Chen <c@jia.je>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import *

from litex_boards.platforms import xilinx_vcu128
from litex_boards.utils.accelerator import (
    HBM_DEFAULT_BASE,
    HBM_HIGH_BASE,
    add_hbm_pseudochannels,
    ensure_hbm_xci,
    hbm_channel_origins,
    hbm_window_end,
    parse_hbm_channels,
)

from litex.soc.cores.clock import *
from litex.soc.cores.ram.xilinx_usp_hbm2 import USPHBM2
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litedram.modules import MT40A512M16
from litedram.phy import usddrphy

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_hbm):
        self.rst       = Signal()
        self.cd_sys    = ClockDomain()
        if with_hbm:
            self.cd_hbm_ref = ClockDomain()
            self.cd_apb     = ClockDomain()
        else: # DDR4
            self.cd_sys4x  = ClockDomain()
            self.cd_pll4x  = ClockDomain()
            self.cd_idelay = ClockDomain()

        # # #

        self.pll = pll = USMMCM(speedgrade=-2)
        self.comb += pll.reset.eq(platform.request("cpu_reset") | self.rst)
        pll.register_clkin(platform.request("clk100_ddr4"), 100e6)
        if with_hbm:
            pll.create_clkout(self.cd_sys,     sys_clk_freq)
            pll.create_clkout(self.cd_hbm_ref, 100e6)
            pll.create_clkout(self.cd_apb,     100e6)
            platform.add_false_path_constraints(self.cd_sys.clk, self.cd_apb.clk)
        else:
            pll.create_clkout(self.cd_pll4x, sys_clk_freq*4, buf=None, with_reset=False)
            pll.create_clkout(self.cd_idelay, 500e6)
            platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

            self.specials += [
                Instance("BUFGCE_DIV",
                    p_BUFGCE_DIVIDE=4,
                    i_CE=1, i_I=self.cd_pll4x.clk, o_O=self.cd_sys.clk),
                Instance("BUFGCE",
                    i_CE=1, i_I=self.cd_pll4x.clk, o_O=self.cd_sys4x.clk),
            ]

            self.idelayctrl = USIDELAYCTRL(cd_ref=self.cd_idelay, cd_sys=self.cd_sys)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=125e6,
        with_led_chaser  = True,
        with_hbm         = False,
        hbm_channels     = (0, 1, 2, 3),
        hbm_main_channel = 0,
        hbm_base         = HBM_DEFAULT_BASE,
        hbm_high_base    = HBM_HIGH_BASE,
        hbm_strip_origin = False,
        **kwargs):
        platform = xilinx_vcu128.Platform()
        if with_hbm:
            assert 225e6 <= sys_clk_freq <= 450e6
            hbm_channels = parse_hbm_channels(hbm_channels)
            if hbm_main_channel not in hbm_channels:
                raise ValueError("HBM main channel must be one of the mapped HBM channels")
            hbm_origins = hbm_channel_origins(hbm_channels, hbm_base, hbm_high_base)
            hbm_end = hbm_window_end(hbm_origins)
            if hbm_end > 2**kwargs.get("bus_address_width", 32):
                kwargs["bus_address_width"] = 64
            if hbm_end > 2**33:
                hbm_strip_origin = True

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, with_hbm)

        # SoCCore ----------------------------------------------------------------------------------
        if with_hbm:
            kwargs["jtagbone_chain"] = 2 # Chain 1 already used by HBM2 debug probes.
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on VCU128", **kwargs)

        # HBM --------------------------------------------------------------------------------------
        if with_hbm:
            # Add HBM Core.
            self.hbm = hbm = ClockDomainsRenamer({"axi": "sys"})(USPHBM2(platform))
            ensure_hbm_xci("https://github.com/litex-hub/litex-boards/files/6893157/hbm_0.xci.txt")
            add_hbm_pseudochannels(
                soc              = self,
                hbm              = hbm,
                channels         = hbm_channels,
                main_channel     = hbm_main_channel,
                origins          = hbm_origins,
                hbm_high_base    = hbm_high_base,
                hbm_strip_origin = hbm_strip_origin)
        elif not self.integrated_main_ram_size:
            # DDR4 SDRAM -------------------------------------------------------------------------------
            self.ddrphy = usddrphy.USPDDRPHY(
                pads             = platform.request("ddram"),
                memtype          = "DDR4",
                sys_clk_freq     = sys_clk_freq,
                is_clam_shell    = True,
                iodelay_clk_freq = 500e6)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT40A512M16(sys_clk_freq, "1:4"),
                size          = 0x40000000,
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=xilinx_vcu128.Platform, description="LiteX SoC on VCU128.")
    parser.add_target_argument("--sys-clk-freq", default=125e6, type=float,       help="System clock frequency.")
    parser.add_target_argument("--with-hbm",     action="store_true",             help="Use HBM2.")
    parser.add_target_argument("--hbm-channels", default="0,1,2,3",               help="HBM channels to map (comma/range list or all).")
    parser.add_target_argument("--hbm-main-channel", default=0, type=int,         help="Mapped HBM channel used as main RAM.")
    parser.add_target_argument("--hbm-base",     default=HBM_DEFAULT_BASE, type=lambda x: int(x, 0), help="HBM bus base address.")
    parser.add_target_argument("--hbm-high-base", default=HBM_HIGH_BASE, type=lambda x: int(x, 0),   help="HBM bus base for channels above the low 32-bit cached window.")
    parser.add_target_argument("--hbm-strip-origin", action="store_true",         help="Expose each mapped HBM channel with local AXI addresses.")
    args = parser.parse_args()
    try:
        hbm_channels = parse_hbm_channels(args.hbm_channels)
    except ValueError as e:
        parser.error(str(e))

    if args.with_hbm and args.sys_clk_freq == 125e6:
        args.sys_clk_freq = 250e6

    soc = BaseSoC(
        sys_clk_freq     = args.sys_clk_freq,
        with_hbm         = args.with_hbm,
        hbm_channels     = hbm_channels,
        hbm_main_channel = args.hbm_main_channel,
        hbm_base         = args.hbm_base,
        hbm_high_base    = args.hbm_high_base,
        hbm_strip_origin = args.hbm_strip_origin,
        **parser.soc_argdict
    )
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
