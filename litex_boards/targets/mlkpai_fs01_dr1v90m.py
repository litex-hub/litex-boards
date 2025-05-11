#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 Junhui Liu <junhui.liu@pigmoral.tech>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from litex_boards.platforms import mlkpai_fs01_dr1v90m

from litex.build.generic_platform import *

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()

        # Clk / Rst.
        clk25 = platform.request("clk25")
        rst_n = platform.request("user_btn", 0)

        self.comb += self.cd_sys.clk.eq(clk25)
        self.specials += AsyncResetSynchronizer(self.cd_sys, ~rst_n | self.rst)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=25e6, with_led_chaser=True, **kwargs):
        platform = mlkpai_fs01_dr1v90m.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on MLKPAI FS01 DR1V90M", **kwargs)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq,
                polarity     = 1)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=mlkpai_fs01_dr1v90m.Platform, description="LiteX SoC on MLKPAI FS01 DR1V90M.")
    parser.add_target_argument("--sys-clk-freq", default=25e6, type=float, help="System clock frequency.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq = args.sys_clk_freq,
        **parser.soc_argdict
    )

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
