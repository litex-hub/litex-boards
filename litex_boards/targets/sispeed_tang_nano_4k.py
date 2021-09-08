#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

import os
import argparse

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litex_boards.platforms import tang_nano_4k

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_sys   = ClockDomain()

        # # #

        # Clk / Rst
        clk27 = platform.request("clk27")
        rst_n = platform.request("rst_n")
        self.comb += self.cd_sys.clk.eq(clk27)
        self.specials += AsyncResetSynchronizer(self.cd_sys, ~rst_n)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(27e6), with_led_chaser=True, **kwargs):
        platform = tang_nano_4k.Platform()

        # Disable CPU/UART for now.
        kwargs["cpu_type"]  = None
        kwargs["with_uart"] = False

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident         = "LiteX SoC on Tang Nano 4K",
            ident_version = True,
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on Tang Nano 4K")
    parser.add_argument("--build",       action="store_true", help="Build bitstream")
    parser.add_argument("--load",        action="store_true", help="Load bitstream")
    parser.add_argument("--sys-clk-freq",default=27e6,        help="System clock frequency (default: 25MHz)")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq      = int(float(args.sys_clk_freq)),
        **soc_core_argdict(args)
    )

    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, "impl", "pnr", "project.fs"))

if __name__ == "__main__":
    main()
