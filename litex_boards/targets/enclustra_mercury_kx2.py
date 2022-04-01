#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Mark Standke <mstandke@cern.ch>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex_boards.platforms import mercury_kx2

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litedram.modules import H5TC4G63CFR
from litedram.phy import s7ddrphy

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_sys    = ClockDomain()
        self.clock_domains.cd_sys4x  = ClockDomain()
        self.clock_domains.cd_idelay = ClockDomain()

        # # #

        self.submodules.pll = pll = S7MMCM(speedgrade=-2)
        self.comb += pll.reset.eq(~platform.request("cpu_reset_n") | self.rst)
        pll.register_clkin(platform.request("clk200"), 200e6)
        pll.create_clkout(self.cd_sys,    sys_clk_freq)
        pll.create_clkout(self.cd_sys4x,  4*sys_clk_freq)
        pll.create_clkout(self.cd_idelay, 200e6)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        self.submodules.idelayctrl = S7IDELAYCTRL(self.cd_idelay)


# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(125e6), with_led_chaser=True, **kwargs):
        platform = mercury_kx2.Platform()

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident = "LiteX SoC on KX2",
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.submodules.ddrphy = s7ddrphy.K7DDRPHY(platform.request("ddram"),
                memtype      = "DDR3",
                nphases      = 4,
                sys_clk_freq = sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = H5TC4G63CFR(sys_clk_freq, "1:4"),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on KX2")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",        action="store_true", help="Build bitstream.")
    target_group.add_argument("--load",         action="store_true", help="Load bitstream.")
    target_group.add_argument("--sys-clk-freq", default=100e6,       help="System clock frequency.")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq = int(float(args.sys_clk_freq)),
        **soc_core_argdict(args)
    )
    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
