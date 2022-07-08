#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2014-2020 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2013-2014 Sebastien Bourdeauducq <sb@m-labs.hk>
# SPDX-License-Identifier: BSD-2-Clause

import importlib

from migen import *

from litex.build.io import CRG

from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

from litex.soc.cores.led import LedChaser

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, platform, with_ethernet=False, with_led_chaser=True, **kwargs):
        sys_clk_freq = int(1e9/platform.default_clk_period)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = CRG(platform.request(platform.default_clk_name))

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX Simple SoC", **kwargs)

        # Leds -------------------------------------------------------------------------------------
        try:
            if with_led_chaser:
                self.submodules.leds = LedChaser(
                    pads         = platform.request_all("user_led"),
                    sys_clk_freq = sys_clk_freq)
        except:
            pass

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="Generic LiteX SoC")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("platform",                             help="Module name of the platform to build for.")
    target_group.add_argument("--build",         action="store_true", help="Build design.")
    target_group.add_argument("--load",          action="store_true", help="Load bitstream.")
    target_group.add_argument("--toolchain",     default=None,        help="FPGA toolchain.")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    platform_module = importlib.import_module(args.platform)
    platform_kwargs = {}
    if args.toolchain is not None:
        platform_kwargs["toolchain"] = args.toolchain
    platform = platform_module.Platform(**platform_kwargs)
    soc = BaseSoC(platform,**soc_core_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    if args.build:
        builder.build()

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
