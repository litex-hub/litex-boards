#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Primesh Pinto <primeshp@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import *

from litex.build.generic_platform import *

from litex_boards.platforms import seeedstudio_spartan_edge_accelerator

from litex.soc.cores.clock import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser,WS2812
from litex.soc.cores.video import *

# Serial Port --------------------------------------------------------------------------------------

_serial_io = [
    # Use J10 connectors 0/1 IOs + GND.
    ("serial", 0,
        Subsignal("tx", Pins("j10:j10_0")),
        Subsignal("rx", Pins("j10:j10_1")),
        IOStandard("LVCMOS33")
    ),
]

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_video_pll):
        self.rst       = Signal()
        self.cd_sys    = ClockDomain()
        self.cd_hdmi   = ClockDomain()
        self.cd_hdmi5x = ClockDomain()

        # # #

        clk100 = platform.request("clk100")
        rst_n  = platform.request("rst_n")

        self.pll = pll = S7PLL(speedgrade=-1)
        self.comb += pll.reset.eq(~rst_n | self.rst)
        pll.register_clkin(clk100, sys_clk_freq)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
      
        if with_video_pll:
            self.video_pll = video_pll = S7PLL(speedgrade=-1)
            video_pll.reset.eq(~rst_n | self.rst)
            video_pll.register_clkin(clk100, 100e6)
            video_pll.create_clkout(self.cd_hdmi,   25e6)
            video_pll.create_clkout(self.cd_hdmi5x, 5*25e6)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    
    def __init__(self, sys_clk_freq=100e6,
        with_led_chaser     = True,
        with_jtagbone       = False,
        with_video_terminal = True,
        with_neopixel       = False,
        **kwargs):
        platform = seeedstudio_spartan_edge_accelerator.Platform()
        platform.add_extension(_serial_io)

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, with_video_pll=with_video_terminal)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident = "LiteX SoC on Seeedstudio Spartan Edge Accelerator", **kwargs)

        # Jtagbone ---------------------------------------------------------------------------------
        if with_jtagbone:
            self.add_jtagbone()

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq
            )

        # Video ------------------------------------------------------------------------------------
        if with_video_terminal:
            self.videophy = VideoHDMIPHY(platform.request("hdmi"), clock_domain="hdmi")
            self.add_video_colorbars(phy=self.videophy, timings="640x480@75Hz", clock_domain="hdmi")
            #self.add_video_terminal(phy=self.videophy, timings="640x480@75Hz", clock_domain="hdmi") #Fixme Not enough BRAM
        
        # Neopixel ---------------------------------------------------------------------------------
        # To test Nexpixel with LiteX BIOS:
        # - mem_list (to get ws2812_base).
        # - mem_write <ws2812_base> 0x00100000
        if with_neopixel:
            self.ws2812 = WS2812(platform.request("rgb"), nleds=2, sys_clk_freq=sys_clk_freq)
            self.bus.add_slave(name="ws2812", slave=self.ws2812.bus, region=SoCRegion(size=2*4))

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=seeedstudio_spartan_edge_accelerator.Platform, description="LiteX SoC on Spartan Edge Accelerator.")
    parser.add_target_argument("--sys-clk-freq",        default=100e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-jtagbone",       action="store_true",       help="Enable Jtagbone support.")
    parser.add_target_argument("--with-video-terminal", action="store_true",       help="Enable Video Colorbars (HDMI).")
    parser.add_target_argument("--with-neopixel",       action="store_true",       help="Enable onboard 2 Neopixels Leds.")

    args = parser.parse_args()
    soc = BaseSoC(
        sys_clk_freq        = args.sys_clk_freq,
        with_jtagbone       = args.with_jtagbone,
        with_video_terminal = args.with_video_terminal,
        with_neopixel       = args.with_neopixel,
        **parser.soc_argdict
    )

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

if __name__ == "__main__":
    main()
