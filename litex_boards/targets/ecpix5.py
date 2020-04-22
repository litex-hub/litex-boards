#!/usr/bin/env python3

# This file is Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# License: BSD

import argparse
import sys

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex_boards.platforms import ecpix5

from litex.build.lattice.trellis import trellis_args, trellis_argdict

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.clock_domains.cd_sys    = ClockDomain()

        # # #

        # Clk / Rst
        clk100 = platform.request("clk100")
        rst_n  = platform.request("rst_n")
        platform.add_period_constraint(clk100, 1e9/100e6)

        # PLL
        self.submodules.pll = pll = ECP5PLL()

        pll.register_clkin(clk100, 100e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        self.specials += AsyncResetSynchronizer(self.cd_sys, ~pll.locked | ~rst_n)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(100e6), **kwargs):
        platform = ecpix5.Platform(toolchain="trellis")

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, clk_freq=sys_clk_freq, **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

# Load ---------------------------------------------------------------------------------------------

def load():
    import os
    f = open("openocd.cfg", "w")
    f.write(
"""
interface ftdi
ftdi_vid_pid 0x0403 0x6010
ftdi_channel 0
ftdi_layout_init 0x00e8 0x60eb
reset_config none
adapter_khz 25000
jtag newtap ecp5 tap -irlen 8 -expected-id 0x41111043
""")
    f.close()
    os.system("openocd -f openocd.cfg -c \"transport select jtag; init; svf soc_basesoc_ecpix5/gateware/top.svf; exit\"")
    exit()

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on ECPIX-5")
    builder_args(parser)
    soc_core_args(parser)
    trellis_args(parser)
    parser.add_argument("--load", action="store_true", help="load bitstream")
    args = parser.parse_args()

    if args.load:
        load()

    soc     = BaseSoC(**soc_core_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder.build(**trellis_argdict(args))

if __name__ == "__main__":
    main()
