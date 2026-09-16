#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Gwenhael Goavec-Merou <gwenhael.goavec-merou@trabucayre.com>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from litex.soc.integration.soc import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.gpio import GPIOIn
from litex.soc.cores.seven_seg import SevenSegmentDisplay

from litex_boards.platforms import myminieye_runber

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()

        # # #

        # Clk / Rst
        clk12 = platform.request("clk12")
        rst_n = platform.request("user_btn_n", 0)
        self.comb += self.cd_sys.clk.eq(clk12)
        self.specials += AsyncResetSynchronizer(self.cd_sys, ~rst_n)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=12e6,
        with_led_chaser     = True,
        with_buttons        = True,
        with_switches       = True,
        with_rgb_led        = True,
        with_seven_segment  = True,
        **kwargs):
        platform = myminieye_runber.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        # Disable CPU for now.
        kwargs["cpu_type"]             = None
        kwargs["integrated_sram_size"] = 0
        kwargs["integrated_rom_size"]  = 0
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Runber", **kwargs)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

        # Buttons ---------------------------------------------------------------------------------
        if with_buttons:
            self.buttons = GPIOIn(Cat(platform.request_all("user_btn_n")))

        # Switches --------------------------------------------------------------------------------
        if with_switches:
            self.switches = GPIOIn(Cat(platform.request_all("user_sw")))

        # RGB Leds --------------------------------------------------------------------------------
        if with_rgb_led:
            rgb_led_pads = []
            for i in range(4):
                rgb_led = platform.request("rgb_led", i)
                rgb_led_pads += [rgb_led.r, rgb_led.g, rgb_led.b]
            rgb_led_pads = Cat(rgb_led_pads)
            self.rgb_led = CSRStorage(len(rgb_led_pads))
            self.comb += rgb_led_pads.eq(~self.rgb_led.storage)

        # Seven Segment ---------------------------------------------------------------------------
        if with_seven_segment:
            self.seven_segment = SevenSegmentDisplay(
                sys_clk_freq = sys_clk_freq,
                segments_pads = platform.request("seven_seg"),
                anodes_pads   = platform.request_all("seven_seg_dig"),
            )

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=myminieye_runber.Platform, description="LiteX SoC on Runber.")
    parser.add_target_argument("--flash",        action="store_true",      help="Flash bitstream.")
    parser.add_target_argument("--sys-clk-freq", default=12e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-buttons",        action="store_true", help="Enable Buttons.")
    parser.add_target_argument("--with-switches",       action="store_true", help="Enable Switches.")
    parser.add_target_argument("--with-rgb-led",        action="store_true", help="Enable RGB Leds.")
    parser.add_target_argument("--with-seven-segment",  action="store_true", help="Enable Seven-Segment Display.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq = args.sys_clk_freq,
        with_buttons       = args.with_buttons,
        with_switches      = args.with_switches,
        with_rgb_led       = args.with_rgb_led,
        with_seven_segment = args.with_seven_segment,
        **parser.soc_argdict
    )

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.flash(0, builder.get_bitstream_filename(mode="flash", ext=".fs")) # FIXME

if __name__ == "__main__":
    main()
