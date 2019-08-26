#!/usr/bin/env python3

# This file is Copyright (c) 2019 Arnaud Durand <arnaud.durand@unifr.ch>
# License: BSD

import argparse

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex_boards.platforms import ecp5_evn

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq, x5_clk_freq):
        self.clock_domains.cd_sys = ClockDomain()

        # # #

        self.cd_sys.clk.attr.add("keep")

        # clk / rst
        clk = clk12 = platform.request("clk12")
        rst_n = platform.request("rst_n")
        platform.add_period_constraint(clk12, 1e9/12e6)
        if x5_clk_freq is not None:
            clk = clk50 = platform.request("ext_clk50")
            self.comb += platform.request("ext_clk50_en").eq(1)
            platform.add_period_constraint(clk50, 1e9/x5_clk_freq)

        # pll
        self.submodules.pll = pll = ECP5PLL()
        self.comb += pll.reset.eq(~rst_n)
        pll.register_clkin(clk, x5_clk_freq or 12e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        self.specials += AsyncResetSynchronizer(self.cd_sys, ~rst_n)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(50e6), x5_clk_freq=None, toolchain="diamond", **kwargs):
        platform = ecp5_evn.Platform(toolchain=toolchain)
        SoCCore.__init__(self, platform, clk_freq=sys_clk_freq,
                          integrated_rom_size=0x8000,
                          **kwargs)

        # crg
        crg = _CRG(platform, sys_clk_freq, x5_clk_freq)
        self.submodules.crg = crg

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on ECP5 Evaluation Board")
    parser.add_argument("--gateware-toolchain", dest="toolchain", default="diamond",
        help='gateware toolchain to use, diamond (default) or  trellis')
    builder_args(parser)
    soc_core_args(parser)
    parser.add_argument("--sys-clk-freq", default=60e6,
                        help="system clock frequency (default=60MHz)")
    parser.add_argument("--x5-clk-freq", type=int,
                        help="use X5 oscillator as system clock at the specified frequency")
    args = parser.parse_args()

    cls = BaseSoC
    soc = cls(toolchain=args.toolchain,
        sys_clk_freq=int(float(args.sys_clk_freq)),
        x5_clk_freq=args.x5_clk_freq,
        **soc_core_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder.build()

if __name__ == "__main__":
    main()
