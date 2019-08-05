#!/usr/bin/env python3

# This file is Copyright (c) 2019 Arnaud Durand <arnaud.durand@unifr.ch>
# License: BSD

import argparse
from warnings import warn

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex_boards.community.platforms import ecp5_evn

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.clock_domains.cd_sys = ClockDomain()

        # # #

        self.cd_sys.clk.attr.add("keep")

        # clk / rst
        clk12 = platform.request("clk12")
        rst_n = platform.request("rst_n")
        platform.add_period_constraint(clk12, 83.33)

        # pll
        # self.submodules.pll = pll = ECP5PLL()
        # self.comb += pll.reset.eq(~rst_n)
        # pll.register_clkin(clk12, 12e6)
        # pll.create_clkout(self.cd_sys, sys_clk_freq)
        # self.specials += AsyncResetSynchronizer(self.cd_sys, ~rst_n)
        self.comb += self.cd_sys.clk.eq(clk12)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(12e6), toolchain="diamond", **kwargs):
        platform = ecp5_evn.Platform(toolchain=toolchain)
        SoCCore.__init__(self, platform, clk_freq=sys_clk_freq,
                          integrated_rom_size=0x8000,
                          **kwargs)

        # crg
        crg = _CRG(platform, sys_clk_freq)
        self.submodules.crg = crg

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on ECP5 Evaluation Board")
    parser.add_argument("--gateware-toolchain", dest="toolchain", default="diamond",
        help='gateware toolchain to use, diamond (default) or  trellis')
    builder_args(parser)
    soc_core_args(parser)
    parser.add_argument("--sys-clk-freq", default=12e6,
                        help="system clock frequency (default=50MHz)")
    args = parser.parse_args()

    cls = BaseSoC
    soc = cls(toolchain=args.toolchain, sys_clk_freq=int(float(args.sys_clk_freq)), **soc_core_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder.build()

if __name__ == "__main__":
    main()
