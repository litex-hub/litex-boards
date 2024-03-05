#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2024 Gwenhael Goavec-merou<gwenhael.goavec-merou@trabucayre.com>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import *

from litex_boards.platforms import olimex_gatemate_a1_evb

from litex.build.io import CRG

from litex.soc.cores.clock.colognechip import GateMatePLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

from litex.build.generic_platform import Pins

from litex.soc.cores.led import LedChaser
from litex.soc.cores.video import VideoVGAPHY


# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_video_terminal):
        self.rst    = Signal()
        rst_n       = Signal()
        self.cd_sys = ClockDomain()
        if with_video_terminal:
            self.cd_vga = ClockDomain()

        # # #

        # Clk / Rst
        clk0     = platform.request("clk0")
        self.rst = ~platform.request("user_btn_n", 0)

        self.specials += Instance("CC_USR_RSTN", o_USR_RSTN = rst_n)

        # PLL
        self.pll = pll = GateMatePLL(perf_mode="economy")
        self.comb += pll.reset.eq(~rst_n | self.rst)
        pll.register_clkin(clk0, 10e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)

        if with_video_terminal:
            self.pll_video = pll_video = GateMatePLL(perf_mode="economy")
            self.comb += pll_video.reset.eq(~rst_n | self.rst)
            pll_video.register_clkin(clk0, 10e6)
            pll_video.create_clkout(self.cd_vga, 65e6)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=24e6,
        with_video_terminal = False,
        with_led_chaser     = True,
        **kwargs):
        platform = olimex_gatemate_a1_evb.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, with_video_terminal)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on GateMate EVB", **kwargs)

        # Video Terminal ---------------------------------------------------------------------------
        if with_video_terminal:
            vga_pads = platform.request("vga")
            self.videophy = VideoVGAPHY(vga_pads, clock_domain="vga")
            self.add_video_terminal(phy=self.videophy, timings="1024x768@60Hz", clock_domain="vga")
            #self.add_video_colorbars(phy=self.videophy, timings="1024x768@60Hz", clock_domain="vga")

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led_n"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=olimex_gatemate_a1_evb.Platform, description="LiteX SoC on Olimex Gatemate A1 EVB")
    parser.add_target_argument("--sys-clk-freq",        default=24e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-video-terminal", action="store_true",      help="Enable Video Terminal (VGA).")
    parser.add_target_argument("--flash",               action="store_true",      help="Flash bitstream.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq        = args.sys_clk_freq,
        with_video_terminal = args.with_video_terminal,
        **parser.soc_argdict)
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.flash(0, builder.get_bitstream_filename(mode="flash"))

if __name__ == "__main__":
    main()
