#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Sergiu Mosanu <sm7ed@virginia.edu>
# Copyright (c) 2020-2021 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2020 Antmicro <www.antmicro.com>
#
# SPDX-License-Identifier: BSD-2-Clause

# To interface via the serial port use:
#     lxterm /dev/ttyUSBx --speed=115200

import os

from migen import *

from litex.gen import *

from litex_boards.platforms import xilinx_alveo_u280
from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.interconnect.csr import *
from litex.soc.cores.ram.xilinx_usp_hbm2 import (
    USPHBM2,
    USPHBM2_DEFAULT_BASE,
    USPHBM2_HIGH_BASE,
    add_usphbm2_pseudochannels,
    parse_usphbm2_channels,
    usphbm2_channel_origins,
    usphbm2_window_end,
)

from litex.soc.cores.led import LedChaser
from litedram.modules import MTA18ASF2G72PZ
from litedram.phy import usddrphy

from litepcie.phy.usppciephy import USPPCIEPHY
from litepcie.software import generate_litepcie_software

from litedram.common import *
from litedram.frontend.axi import *

# HBM XCI ------------------------------------------------------------------------------------------

def ensure_hbm_xci(url, hbm_xci=os.path.join("ip", "hbm", "hbm_0.xci")):
    if not os.path.exists(hbm_xci):
        os.makedirs(os.path.dirname(hbm_xci), exist_ok=True)
        os.system(f"wget -O {hbm_xci} {url}")

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, ddram_channel, with_hbm):
        if with_hbm:
            self.rst        = Signal()
            self.cd_sys     = ClockDomain()
            self.cd_hbm_ref = ClockDomain()
            self.cd_apb     = ClockDomain()
        else: # ddr4
            self.rst = Signal()
            self.cd_sys    = ClockDomain()
            self.cd_sys4x  = ClockDomain()
            self.cd_pll4x  = ClockDomain()
            self.cd_idelay = ClockDomain()

        # # #

        if with_hbm:
            self.pll = pll = USMMCM(speedgrade=-2)
            self.comb += pll.reset.eq(self.rst)
            pll.register_clkin(platform.request("sysclk", ddram_channel), 100e6)
            pll.create_clkout(self.cd_sys,     sys_clk_freq)
            pll.create_clkout(self.cd_hbm_ref, 100e6)
            pll.create_clkout(self.cd_apb,     100e6)
            platform.add_false_path_constraints(self.cd_sys.clk, self.cd_apb.clk)
        else: # ddr4
            self.pll = pll = USMMCM(speedgrade=-2)
            self.comb += pll.reset.eq(self.rst)
            pll.register_clkin(platform.request("sysclk", ddram_channel), 100e6)
            pll.create_clkout(self.cd_pll4x, sys_clk_freq*4, buf=None, with_reset=False)
            pll.create_clkout(self.cd_idelay, 600e6) #, with_reset=False
            platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

            self.specials += [
                Instance("BUFGCE_DIV",
                    p_BUFGCE_DIVIDE=4,
                    i_CE=1, i_I=self.cd_pll4x.clk, o_O=self.cd_sys.clk),
                Instance("BUFGCE",
                    i_CE=1, i_I=self.cd_pll4x.clk, o_O=self.cd_sys4x.clk),
                # AsyncResetSynchronizer(self.cd_idelay, ~pll.locked),
            ]

            self.idelayctrl = USIDELAYCTRL(cd_ref=self.cd_idelay, cd_sys=self.cd_sys)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=150e6, ddram_channel=0,
        with_pcie             = False,
        pcie_lanes            = 4,
        pcie_ndmas            = 1,
        pcie_address_width    = 32,
        with_pcie_dma_status  = False,
        with_pcie_dma_monitor = False,
        with_led_chaser       = False,
        with_hbm              = False,
        hbm_channels          = (0, 1, 2, 3),
        hbm_main_channel      = 0,
        hbm_base              = USPHBM2_DEFAULT_BASE,
        hbm_high_base         = USPHBM2_HIGH_BASE,
        hbm_strip_origin      = False,
        **kwargs):
        platform = xilinx_alveo_u280.Platform()
        if ddram_channel not in range(2):
            raise ValueError("DDRAM channel must be 0 or 1")
        if with_hbm:
            assert 225e6 <= sys_clk_freq <= 450e6
            hbm_channels = parse_usphbm2_channels(hbm_channels)
            if hbm_main_channel not in hbm_channels:
                raise ValueError("HBM main channel must be one of the mapped HBM channels")
            hbm_origins = usphbm2_channel_origins(hbm_channels, hbm_base, hbm_high_base)
            hbm_end = usphbm2_window_end(hbm_origins)
            if hbm_end > 2**kwargs.get("bus_address_width", 32):
                kwargs["bus_address_width"] = 64
            if hbm_end > 2**pcie_address_width:
                pcie_address_width = 64
            if hbm_end > 2**33:
                hbm_strip_origin = True

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, ddram_channel, with_hbm)

        # SoCCore ----------------------------------------------------------------------------------
        kwargs["jtagbone_chain"] = 2 # Chain 1 already used by HBM2 debug probes.

        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Alveo U280 (ES1)", **kwargs)

        # HBM / DRAM -------------------------------------------------------------------------------
        if with_hbm:
            # Add HBM Core.
            self.hbm = hbm = ClockDomainsRenamer({"axi": "sys"})(USPHBM2(platform))
            ensure_hbm_xci("https://github.com/litex-hub/litex-boards/files/6893157/hbm_0.xci.txt")
            add_usphbm2_pseudochannels(
                soc              = self,
                hbm              = hbm,
                channels         = hbm_channels,
                main_channel     = hbm_main_channel,
                origins          = hbm_origins,
                hbm_high_base    = hbm_high_base,
                hbm_strip_origin = hbm_strip_origin)

        else:
            # DDR4 SDRAM -------------------------------------------------------------------------------
            if not self.integrated_main_ram_size:
                self.ddrphy = usddrphy.USPDDRPHY(platform.request("ddram", ddram_channel),
                    memtype          = "DDR4",
                    cmd_latency      = 1, # seems to work better with cmd_latency=1
                    sys_clk_freq     = sys_clk_freq,
                    iodelay_clk_freq = 600e6,
                    is_rdimm         = True)
                self.add_sdram("sdram",
                    phy           = self.ddrphy,
                    module        = MTA18ASF2G72PZ(sys_clk_freq, "1:4"),
                    size          = 0x40000000,
                    l2_cache_size = kwargs.get("l2_size", 8192)
                )

            # Firmware RAM (To ease initial LiteDRAM calibration support) --------------------------
            self.add_ram("firmware_ram", 0x20000000, 0x8000)

        # PCIe -------------------------------------------------------------------------------------
        if with_pcie:
            self.pcie_phy = USPPCIEPHY(platform, platform.request(f"pcie_x{pcie_lanes}"),
                data_width = {4: 128, 16: 512}[pcie_lanes],
                bar0_size  = 0x20000)
            self.add_pcie(
                phy              = self.pcie_phy,
                ndmas            = pcie_ndmas,
                address_width    = pcie_address_width,
                with_dma_status  = with_pcie_dma_status,
                with_dma_monitor = with_pcie_dma_monitor)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("gpio_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=xilinx_alveo_u280.Platform, description="LiteX SoC on Alveo U280.")
    parser.add_target_argument("--sys-clk-freq",    default=150e6, type=float, help="System clock frequency.") # HBM2 with 250MHz, DDR4 with 150MHz (1:4)
    parser.add_target_argument("--ddram-channel",   default=0, type=lambda x: int(x, 0), choices=range(2), help="DDRAM channel (0 or 1).") # also selects clk 0 or 1
    parser.add_target_argument("--with-pcie",       action="store_true",        help="Enable PCIe support.")
    parser.add_target_argument("--pcie-lanes",      default=4, type=int,        choices=[4, 16], help="PCIe lane count.")
    parser.add_target_argument("--pcie-ndmas",      default=1, type=int,        help="Number of PCIe DMA channels.")
    parser.add_target_argument("--pcie-address-width", default=32, type=int, choices=[32, 64], help="PCIe address width.")
    parser.add_target_argument("--pcie-with-dma-status",  action="store_true",        help="Enable PCIe DMA status CSRs.")
    parser.add_target_argument("--pcie-with-dma-monitor", action="store_true",        help="Enable PCIe DMA monitor CSRs.")
    parser.add_target_argument("--driver",                action="store_true",        help="Generate PCIe driver.")
    parser.add_target_argument("--with-hbm",              action="store_true",        help="Use HBM2.")
    parser.add_target_argument("--hbm-channels",    default="0,1,2,3",          help="HBM channels to map (comma/range list or all).")
    parser.add_target_argument("--hbm-main-channel", default=0, type=int,       help="Mapped HBM channel used as main RAM.")
    parser.add_target_argument("--hbm-base",        default=USPHBM2_DEFAULT_BASE,
        type=lambda x: int(x, 0), help="HBM bus base address.")
    parser.add_target_argument("--hbm-high-base",   default=USPHBM2_HIGH_BASE,
        type=lambda x: int(x, 0), help="HBM bus base for channels above the low 32-bit cached window.")
    parser.add_target_argument("--hbm-strip-origin", action="store_true",       help="Expose each mapped HBM channel with local AXI addresses.")
    parser.add_target_argument("--with-analyzer",   action="store_true",        help="Enable Analyzer.")
    parser.add_target_argument("--with-led-chaser", action="store_true",        help="Enable LED Chaser.")
    args = parser.parse_args()
    if args.pcie_ndmas < 0:
        parser.error("--pcie-ndmas must be >= 0")
    try:
        hbm_channels = parse_usphbm2_channels(args.hbm_channels)
    except ValueError as e:
        parser.error(str(e))

    if args.with_hbm and args.sys_clk_freq == 150e6:
        args.sys_clk_freq = 250e6

    soc = BaseSoC(
        sys_clk_freq          = args.sys_clk_freq,
        ddram_channel         = args.ddram_channel,
        with_pcie             = args.with_pcie,
        pcie_lanes            = args.pcie_lanes,
        pcie_ndmas            = args.pcie_ndmas,
        pcie_address_width    = args.pcie_address_width,
        with_pcie_dma_status  = args.pcie_with_dma_status,
        with_pcie_dma_monitor = args.pcie_with_dma_monitor,
        with_led_chaser       = args.with_led_chaser,
        with_hbm              = args.with_hbm,
        hbm_channels          = hbm_channels,
        hbm_main_channel      = args.hbm_main_channel,
        hbm_base              = args.hbm_base,
        hbm_high_base         = args.hbm_high_base,
        hbm_strip_origin      = args.hbm_strip_origin,
        with_analyzer         = args.with_analyzer,
        **parser.soc_argdict
    )
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.driver:
        generate_litepcie_software(soc, os.path.join(builder.output_dir, "driver"))

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
