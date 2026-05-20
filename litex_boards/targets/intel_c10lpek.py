#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019 Antti Lukats <antti.lukats@gmail.com>
# Copyright (c) 2019 msloniewski <marcin.sloniewski@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import *

from litex_boards.platforms import intel_c10lpek

from litex.soc.cores.hyperbus import HyperRAM
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()

        # # #

        if sys_clk_freq != 50e6:
            raise ValueError("intel_c10lpek currently supports a 50MHz system clock.")

        clk50 = platform.request("clk50")
        self.comb += [
            self.cd_sys.clk.eq(clk50),
            self.cd_sys.rst.eq(~platform.request("cpu_reset_n") | self.rst),
        ]

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=50e6,
        with_hyperram   = False,
        with_led_chaser = True,
        **kwargs):
        platform = intel_c10lpek.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on C10LP Evaluation Kit", **kwargs)

        # HyperRAM ---------------------------------------------------------------------------------
        if with_hyperram:
            self.hyperram = HyperRAM(platform.request("hyperram"), sys_clk_freq=sys_clk_freq)
            self.bus.add_slave("hyperram", slave=self.hyperram.bus, region=SoCRegion(
                origin = 0x20000000,
                size   = 8*MEGABYTE,
                mode   = "rwx",
            ))

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=intel_c10lpek.Platform, description="LiteX SoC on C10LP Evaluation Kit.")
    parser.add_target_argument("--sys-clk-freq", default=50e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-hyperram", action="store_true",    help="Enable HyperRAM support.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq  = args.sys_clk_freq,
        with_hyperram = args.with_hyperram,
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
