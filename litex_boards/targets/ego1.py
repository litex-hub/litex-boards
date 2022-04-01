#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Shinken Sanada <sanadashinken@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex_boards.platforms import ego1
from litex.build.xilinx.vivado import vivado_build_args, vivado_build_argdict

from litex.soc.cores.clock import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.video import VideoVGAPHY

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_sys       = ClockDomain()
        self.clock_domains.cd_vga       = ClockDomain()

        self.submodules.pll = pll = S7PLL(speedgrade=-1)
        self.comb += pll.reset.eq(~platform.request("cpu_reset") | self.rst)
        pll.register_clkin(platform.request("clk100"), 100e6)
        pll.create_clkout(self.cd_sys,       sys_clk_freq)
        pll.create_clkout(self.cd_vga,       25e6)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(100e6), with_led_chaser=True, with_video_terminal=False, **kwargs):
        platform = ego1.Platform()

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident = "LiteX SoC on EGO1 Board",
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # VGA terminal -----------------------------------------------------------------------------
        if with_video_terminal:
            self.submodules.videophy = VideoVGAPHY(platform.request("vga"), clock_domain="vga")
            self.add_video_terminal(phy=self.videophy, timings="640x480@75Hz", clock_domain="vga")

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)
            self.add_csr("leds")

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on EGO1")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",               action="store_true", help="Build bitstream.")
    target_group.add_argument("--load",                action="store_true", help="Load bitstream.")
    target_group.add_argument("--flash",               action="store_true", help="Flash bitstream.")
    target_group.add_argument("--with-video-terminal", action="store_true", help="Enable Video Terminal.")
    target_group.add_argument("--sys-clk-freq",        default=100e6,       help="System clock frequency.")

    builder_args(parser)
    soc_core_args(parser)
    vivado_build_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq        = int(float(args.sys_clk_freq)),
        with_video_terminal = args.with_video_terminal,
        **soc_core_argdict(args)
    )

    builder = Builder(soc, **builder_argdict(args))

    builder.build(**vivado_build_argdict(args), run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="flash"))

if __name__ == "__main__":
    main()

