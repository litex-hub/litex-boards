#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Michael Welling <mwelling@ieee.org>
# Copyright (c) 2020 Sean Cross <sean@xobs.io>
# Copyright (c) 2020 Drew Fustini <drew@pdp7.com>
# Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.build.io import DDROutput

from litex_boards.platforms import hadbadge

from litex.build.lattice.trellis import trellis_args, trellis_argdict

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

from litedram import modules as litedram_modules
from litedram.phy import GENSDRPHY
from litedram.modules import AS4C32M8

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_sys    = ClockDomain()
        self.clock_domains.cd_sys_ps = ClockDomain()

        # # #

        # Clk / Rst
        clk8  = platform.request("clk8")

        # PLL
        self.submodules.pll = pll = ECP5PLL()
        pll.pfd_freq_range = (8e6, 400e6) # Lower Min from 10MHz to 8MHz.
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk8, 8e6)
        pll.create_clkout(self.cd_sys,    sys_clk_freq)
        pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=90)

        # SDRAM clock
        self.specials += DDROutput(1, 0, platform.request("sdram_clock"), ClockSignal("sys_ps"))

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, toolchain="trellis", sys_clk_freq=int(48e6), sdram_module_cls="AS4C32M8", **kwargs):
        platform = hadbadge.Platform(toolchain=toolchain)

        # SoCCore ---------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident = "LiteX SoC on Hackaday Badge",
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # SDR SDRAM --------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.submodules.sdrphy = GENSDRPHY(platform.request("sdram"), sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.sdrphy,
                module        = AS4C32M8(sys_clk_freq, "1:1"),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on Hackaday Badge")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",        action="store_true", help="Build bitstream.")
    target_group.add_argument("--toolchain",    default="trellis",   help="FPGA toolchain (trellis or diamond).")
    target_group.add_argument("--sys-clk-freq", default=48e6,        help="System clock frequency.")
    builder_args(parser)
    soc_core_args(parser)
    trellis_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        toolchain    = args.toolchain,
        sys_clk_freq = int(float(args.sys_clk_freq)),
        **soc_core_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder_kargs = trellis_argdict(args) if args.toolchain == "trellis" else {}
    builder.build(**builder_kargs, run=args.build)

if __name__ == "__main__":
    main()
