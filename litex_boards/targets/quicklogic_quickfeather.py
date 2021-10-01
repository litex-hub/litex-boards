#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

import os
import argparse

from migen import *

from litex_boards.platforms import quicklogic_quickfeather

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform):
        self.clock_domains.cd_sys = ClockDomain()

        # # #

        class Open(Signal): pass

        self.specials += Instance("qlal4s3b_cell_macro",
            o_Sys_Clk0     = self.cd_sys.clk,
            o_Sys_Clk0_Rst = self.cd_sys.rst,
            o_Sys_Clk1     = Open(),
            o_Sys_Clk1_Rst = Open(),
        )

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(60e6), with_led_chaser=True, **kwargs):
        platform = quicklogic_quickfeather.Platform()

        # SoCCore ----------------------------------------------------------------------------------
        kwargs["cpu_type"]  = None
        kwargs["with_uart"] = False
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident          = "LiteX SoC on QuickLogic QuickFeather",
            ident_version  = True,
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on Quicklogic QuickFeather")
    parser.add_argument("--build", action="store_true", help="Build bitstream")
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(**soc_core_argdict(args))
    builder = Builder(soc, compile_software=False)
    builder.build(run=args.build)

if __name__ == "__main__":
    main()
