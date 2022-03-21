#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Primesh Pinto <primeshp@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.build.generic_platform import *
from litex.build.xilinx.vivado import vivado_build_args, vivado_build_argdict

from litex_boards.platforms import spartan_edge_accelerator

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

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq, with_video_pll):
        self.rst = Signal()
        self.clock_domains.cd_sys       = ClockDomain()
        self.clock_domains.cd_hdmi      = ClockDomain()
        self.clock_domains.cd_hdmi5x    = ClockDomain()

        # # #

        clk100 = platform.request("clk100")
        rst_n  = platform.request("rst_n")

        self.submodules.pll = pll = S7PLL(speedgrade=-1)
        self.comb += pll.reset.eq(~rst_n | self.rst)
        pll.register_clkin(clk100, sys_clk_freq)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
      
        if with_video_pll:
            self.submodules.video_pll = video_pll = S7PLL(speedgrade=-1)
            video_pll.reset.eq(~rst_n | self.rst)
            video_pll.register_clkin(clk100, 100e6)
            video_pll.create_clkout(self.cd_hdmi,   25e6)
            video_pll.create_clkout(self.cd_hdmi5x, 5*25e6)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    
    def __init__(self, sys_clk_freq=int(100e6),
        with_led_chaser     = True,
        with_jtagbone       = False,
        with_video_terminal = True,
        with_neopixel       = False,
        **kwargs):
        platform = spartan_edge_accelerator.Platform()
        platform.add_extension(_serial_io)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident = "LiteX SoC on Seeedstudio Spartan Edge Accelerator",
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq, with_video_pll=with_video_terminal)

        # Jtagbone ---------------------------------------------------------------------------------
        if with_jtagbone:
            self.add_jtagbone()

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq
            )

        # Video ------------------------------------------------------------------------------------
        if with_video_terminal:
            self.submodules.videophy = VideoHDMIPHY(platform.request("hdmi"), clock_domain="hdmi")
            self.add_video_colorbars(phy=self.videophy, timings="640x480@75Hz", clock_domain="hdmi")
            #self.add_video_terminal(phy=self.videophy, timings="640x480@75Hz", clock_domain="hdmi") #Fixme Not enough BRAM
        
        # Neopixel ---------------------------------------------------------------------------------
        # To test Nexpixel with LiteX BIOS:
        # - mem_list (to get ws2812_base).
        # - mem_write <ws2812_base> 0x00100000
        if with_neopixel:
            self.submodules.ws2812 = WS2812(platform.request("rgb"), nleds=2, sys_clk_freq=sys_clk_freq)
            self.bus.add_slave(name="ws2812", slave=self.ws2812.bus, region=SoCRegion(size=2*4))

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on Spartan Edge Accelerator")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",               action="store_true",  help="Build bitstream.")
    target_group.add_argument("--sys-clk-freq",        default=100e6,        help="System clock frequency.")
    target_group.add_argument("--with-jtagbone",       action="store_true",  help="Enable Jtagbone support.")
    target_group.add_argument("--with-video-terminal", action="store_true",  help="Enable Video Colorbars (HDMI).")
    target_group.add_argument("--with-neopixel",       action="store_true",  help="Enable onboard 2 Neopixels Leds.")

    builder_args(parser)
    soc_core_args(parser)
    vivado_build_args(parser)
    args = parser.parse_args()
    soc = BaseSoC(
        sys_clk_freq        = int(float(args.sys_clk_freq)),
        with_jtagbone       = args.with_jtagbone,
        with_video_terminal = args.with_video_terminal,
        with_neopixel       = args.with_neopixel,
        **soc_core_argdict(args)
    )

    builder = Builder(soc, **builder_argdict(args))
    builder_kwargs = vivado_build_argdict(args)
    builder.build(**builder_kwargs, run=args.build)

if __name__ == "__main__":
    main()
