#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Nathaniel Lewis <github@nrlewis.dev>
# SPDX-License-Identifier: BSD-2-Clause

# Testing build for HDMI
# - The main trouble with HDMI demos are that they require many SLICEMs, which are a very limited
#   resource on the XC6SLX9. Many of these examples are just trying to reduce usage of them.
#
# # Simple colorbar output
# ./alchitry_mojo.py \
#     --build \
#     --with-hdmi-shield \
#     --with-video-colorbars \
#     --csr-csv=build/alchitry_mojo/csr.csv
#
# # Video Terminal (lower SRAM size to allow for text buffer)
# ./alchitry_mojo.py \
#     --build \
#     --with-hdmi-shield \
#     --with-video-terminal \
#     --csr-csv=build/alchitry_mojo/csr.csv \
#     --integrated-rom-size 32768 \
#     --integrated-sram-size 4096
#
# # Video Framebuffer (double sdram speed to have enough bandwidth)
# # Lower the fifo_depth in litex/litex/soc/cores/video.py "class VideoFrameBuffer" to 1024
# ./alchitry_mojo.py \
#     --build \
#     --with-hdmi-shield \
#     --with-video-framebuffer \
#     --csr-csv=build/alchitry_mojo/csr.csv \
#     --integrated-rom-size 32768 \
#     --sdram-rate 1:2
#
# litex> # Turn screen Red
# litex> mem_write 0x40c00000 0xffff0000 307200

from migen import *

from litex.build.io import DDROutput
from litex_boards.platforms import alchitry_mojo

from litex.soc.interconnect.csr import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

from litex.soc.cores.clock import *
from litex.soc.cores.video import VideoS6HDMIPHY
from litex.soc.cores.led import LedChaser

from litedram.modules import MT48LC32M8, SDRModule
from litedram.phy import GENSDRPHY, HalfRateGENSDRPHY

# CRG ----------------------------------------------------------------------------------------------

class CRG(Module):
    def __init__(self, platform, sys_clk_freq, sdram_rate="1:1"):
        self.rst = Signal()
        self.clock_domains.cd_sys = ClockDomain()
        self.clock_domains.cd_hdmi   = ClockDomain()
        self.clock_domains.cd_hdmi5x = ClockDomain()
        if sdram_rate == "1:2":
            self.clock_domains.cd_sys2x    = ClockDomain()
            self.clock_domains.cd_sys2x_ps = ClockDomain()
        else:
            self.clock_domains.cd_sys_ps = ClockDomain()

        # Clk/Rst
        clk50 = platform.request("clk50")
        rst = platform.request("cpu_reset")
        avr_ready = platform.request("cclk")

        # PLL
        self.submodules.pll = pll = S6PLL()
        self.comb += pll.reset.eq(~rst | ~avr_ready | self.rst)
        pll.register_clkin(clk50, 50e6)
        pll.create_clkout(self.cd_sys,    sys_clk_freq)
        pll.create_clkout(self.cd_hdmi,   25e6,  margin=0)
        pll.create_clkout(self.cd_hdmi5x, 125e6, margin=0)
        if sdram_rate == "1:2":
            pll.create_clkout(self.cd_sys2x,    2*sys_clk_freq)
            pll.create_clkout(self.cd_sys2x_ps, 2*sys_clk_freq, phase=90)
        else:
            pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=90)

# BaseSoC -----------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(62.5e6), sdram_rate="1:1", with_hdmi_shield=False,
                 with_sdram_shield=False, with_led_chaser=True, with_video_terminal=False,
                 with_video_framebuffer=False, with_video_colorbars=False, **kwargs):
        platform = alchitry_mojo.Platform()

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident = "LiteX SoC on Alchitry Mojo",
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = CRG(platform, sys_clk_freq, sdram_rate)

        # HDMI Shield ------------------------------------------------------------------------------
        if with_hdmi_shield:
            self.platform.add_extension(alchitry_mojo._hdmi_shield)

        # SDRAM Shield -----------------------------------------------------------------------------
        if with_sdram_shield:
            self.platform.add_extension(alchitry_mojo._sdram_shield)

        # Add SDRAM if a shield with RAM has been added
        if not self.integrated_main_ram_size and (with_hdmi_shield or with_sdram_shield):
            sdram_clk = ClockSignal("sys2x_ps" if sdram_rate == "1:2" else "sys_ps")
            self.crg.specials += DDROutput(1, 0, platform.request("sdram_clock"), sdram_clk)

            sdrphy_cls = HalfRateGENSDRPHY if sdram_rate == "1:2" else GENSDRPHY
            self.submodules.sdrphy = sdrphy_cls(platform.request("sdram"), sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.sdrphy,
                module        = MT48LC32M8(sys_clk_freq, sdram_rate),
                l2_cache_size = kwargs.get("l2_size", 1024)
            )
        
        # HDMI Options -----------------------------------------------------------------------------
        if with_hdmi_shield and (with_video_colorbars or with_video_framebuffer or with_video_terminal):
            self.submodules.videophy = VideoS6HDMIPHY(platform.request("hdmi_out"), clock_domain="hdmi")
            if with_video_colorbars:
                self.add_video_colorbars(phy=self.videophy, timings="640x480@60Hz", clock_domain="hdmi")
            if with_video_terminal:
                self.add_video_terminal(phy=self.videophy, timings="640x480@60Hz", clock_domain="hdmi")
            if with_video_framebuffer:
                self.add_video_framebuffer(phy=self.videophy, timings="640x480@60Hz", clock_domain="hdmi")

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on Alchitry Mojo")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",                  action="store_true", help="Build bitstream.")
    target_group.add_argument("--sys-clk-freq",           default=62.5e6,      help="System clock frequency.")
    target_group.add_argument("--sdram-rate",             default="1:1",       help="SDRAM Rate: (1:1 Full Rate or 1:2 Half Rate).")
    shields1 = target_group.add_mutually_exclusive_group()
    shields1.add_argument("--with-hdmi-shield",     action="store_true", help="Enable HDMI Shield.")
    shields1.add_argument("--with-sdram-shield",    action="store_true", help="Enable SDRAM Shield.")
    viopts = target_group.add_mutually_exclusive_group()
    viopts.add_argument("--with-video-terminal",    action="store_true", help="Enable Video Terminal (HDMI).")
    viopts.add_argument("--with-video-framebuffer", action="store_true", help="Enable Video Framebuffer (HDMI).")
    viopts.add_argument("--with-video-colorbars",   action="store_true", help="Enable Video Colorbars (HDMI).")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    # Note: baudrate is fixed because regardless of USB->TTL baud, the AVR <-> FPGA baudrate is
    #       set to a fixed rate of 500 kilobaud.
    soc = BaseSoC(
        sys_clk_freq           = int(float(args.sys_clk_freq)),
        sdram_rate             = args.sdram_rate,
        with_hdmi_shield       = args.with_hdmi_shield,
        with_sdram_shield      = args.with_sdram_shield,
        with_video_terminal    = args.with_video_terminal,
        with_video_framebuffer = args.with_video_framebuffer,
        with_video_colorbars   = args.with_video_colorbars,
        **soc_core_argdict(args)
    )

    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

if __name__ == "__main__":
    main()
