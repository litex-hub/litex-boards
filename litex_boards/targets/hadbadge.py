#!/usr/bin/env python3

# This file is Copyright (c) 2020 Michael Welling <mwelling@ieee.org>
# This file is Copyright (c) 2020 Sean Cross <sean@xobs.io>
# This file is Copyright (c) 2020 Drew Fustini <drew@pdp7.com>
# This file is Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# License: BSD

import argparse
import sys

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex_boards.platforms import hadbadge

from litex.build.lattice.trellis import trellis_args, trellis_argdict

from litex.soc.cores.clock import *
from litex.soc.integration.soc_sdram import *
from litex.soc.integration.builder import *

from litedram import modules as litedram_modules
from litedram.phy import GENSDRPHY
from litedram.modules import AS4C32M8

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.clock_domains.cd_sys    = ClockDomain()
        self.clock_domains.cd_sys_ps = ClockDomain(reset_less=True)

        # # #

        # Clk / Rst
        clk8  = platform.request("clk8")
        platform.add_period_constraint(clk8, 1e9/8e6)

        # PLL
        self.submodules.pll = pll = ECP5PLL()
        pll.register_clkin(clk8, 8e6)
        pll.create_clkout(self.cd_sys,    sys_clk_freq, phase=11)
        pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=20)
        self.specials += AsyncResetSynchronizer(self.cd_sys, ~pll.locked)

        # SDRAM clock
        self.comb += platform.request("sdram_clock").eq(self.cd_sys_ps.clk)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCSDRAM):
    def __init__(self, toolchain="trellis", sys_clk_freq=int(48e6), sdram_module_cls="AS4C32M8", **kwargs):
        platform = hadbadge.Platform(toolchain=toolchain)

        # SoCSDRAM ---------------------------------------------------------------------------------
        SoCSDRAM.__init__(self, platform, clk_freq=sys_clk_freq, **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # SDR SDRAM --------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.submodules.sdrphy = GENSDRPHY(platform.request("sdram"), cl=2)
            sdram_module = AS4C32M8(sys_clk_freq, "1:1")
            self.register_sdram(self.sdrphy,
                                sdram_module.geom_settings,
                                sdram_module.timing_settings)

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on Hackaday Badge")
    parser.add_argument("--gateware-toolchain", dest="toolchain", default="trellis",
        help='gateware toolchain to use, trellis (default) or diamond')
    parser.add_argument("--sys-clk-freq", default=48e6,
                        help="system clock frequency (default=48MHz)")
    builder_args(parser)
    soc_sdram_args(parser)
    trellis_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(toolchain=args.toolchain,
        sys_clk_freq=int(float(args.sys_clk_freq)),
        **soc_sdram_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder_kargs = trellis_argdict(args) if args.toolchain == "trellis" else {}
    builder.build(**builder_kargs)

if __name__ == "__main__":
    main()
