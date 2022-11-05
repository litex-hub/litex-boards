#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2014-2020 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2013-2014 Sebastien Bourdeauducq <sb@m-labs.hk>
# SPDX-License-Identifier: BSD-2-Clause

import importlib

from migen import *

from litex.gen import LiteXModule

from litex.build.io import CRG

from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

from litex.soc.cores.led import LedChaser

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, platform, with_ethernet=False, with_led_chaser=True, **kwargs):
        sys_clk_freq = int(1e9/platform.default_clk_period)

        # CRG --------------------------------------------------------------------------------------
        self.crg = CRG(platform.request(platform.default_clk_name))

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX Simple SoC", **kwargs)

        # Leds -------------------------------------------------------------------------------------
        try:
            if with_led_chaser:
                self.leds = LedChaser(
                    pads         = platform.request_all("user_led"),
                    sys_clk_freq = sys_clk_freq)
        except:
            pass

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.argument_parser import LiteXArgumentParser
    parser = LiteXArgumentParser(description="Generic LiteX SoC")
    parser.add_target_argument("platform", help="Module name of the platform to build for.")
    args = parser.parse_args()

    platform_module = importlib.import_module(args.platform)
    platform_kwargs = {}
    if args.toolchain is not None:
        platform_kwargs["toolchain"] = args.toolchain
    platform = platform_module.Platform(**platform_kwargs)
    soc = BaseSoC(platform,**parser.soc_core_argdict)
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
