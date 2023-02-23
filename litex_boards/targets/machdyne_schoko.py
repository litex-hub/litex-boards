#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) Lone Dynamics Corporation <info@lonedynamics.com>
#
# SPDX-License-Identifier: BSD-2-Clause
#

import os
import sys
import json

from migen import *

from litex.gen import *

from litex_boards.platforms import machdyne_schoko

from litex.build.io import DDROutput

from litex.soc.cores.clock import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.usb_ohci import USBOHCI
from litex.soc.cores.video import VideoVGAPHY
from litex.soc.cores.video import VideoHDMIPHY

from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

from litedram.modules import W9825G6KH6
from litedram.phy import GENSDRPHY, HalfRateGENSDRPHY
#from litedram.phy import QuarterRateGENSDRPHY

from litex.soc.integration.soc import SoCRegion

# CRG ---------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, sdram_rate):
        self.rst        = Signal()
        self.cd_por     = ClockDomain()
        self.cd_sys     = ClockDomain()
        self.cd_video   = ClockDomain()
        self.cd_video5x = ClockDomain()

        # Clk / Rst
        clk48 = platform.request("clk48")

        # Power on reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += self.cd_por.clk.eq(clk48)
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # PLL
        self.pll = pll = ECP5PLL()
        self.comb += pll.reset.eq(~por_done | self.rst)
        pll.register_clkin(clk48, 48e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)

        if sdram_rate == "1:2":
            self.cd_sys2x = ClockDomain()
            self.cd_sys2x_ps = ClockDomain()
            pll.create_clkout(self.cd_sys2x,    2*sys_clk_freq)
            pll.create_clkout(self.cd_sys2x_ps, 2*sys_clk_freq, phase=180)
        elif sdram_rate == "1:4":
            self.cd_sys2x = ClockDomain()
            self.cd_sys4x = ClockDomain()
            self.cd_sys4x_ps = ClockDomain()
            pll.create_clkout(self.cd_sys2x,    2*sys_clk_freq)
            pll.create_clkout(self.cd_sys4x,    4*sys_clk_freq)
            pll.create_clkout(self.cd_sys4x_ps, 4*sys_clk_freq, phase=180)
        else:
            self.cd_sys_ps = ClockDomain()
            pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=90)

        if sdram_rate == "1:2":
            sdram_clk = ClockSignal("sys2x_ps")
        elif sdram_rate == "1:4":
            sdram_clk = ClockSignal("sys4x_ps")
        else:
            sdram_clk = ClockSignal("sys_ps")

        self.specials += DDROutput(1, 0, platform.request("sdram_clock"), sdram_clk)
        pll2 = ECP5PLL()
        self.pll2 = pll2
        pll2.register_clkin(clk48, 48e6)
        pll2.create_clkout(self.cd_video, 25e6)
        pll2.create_clkout(self.cd_video5x, 125e6)

        self.cd_usb_12 = ClockDomain()
        self.cd_usb = ClockDomain()
        self.cd_usb_48 = ClockDomain()
        self.cd_usb_48 = self.cd_usb
        pll2.create_clkout(self.cd_usb, 48e6)
        pll2.create_clkout(self.cd_usb_12, 12e6)
        self.comb += pll2.reset.eq(~por_done)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    mem_map = {**SoCCore.mem_map, **{
        "usb_ohci":     0xc0000000,
    }}
    def __init__(self, revision="v1", device="45F",  sys_clk_freq=40e6, toolchain="trellis",
        sdram_rate      = "1:2",
        with_led_chaser = True,
        with_usb_host   = False,
        **kwargs):
        platform = machdyne_schoko.Platform(revision=revision, device=device ,toolchain=toolchain)

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, sdram_rate=sdram_rate)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Schoko", **kwargs)

        # DRAM -------------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            if sdram_rate == "1:2":
                sdrphy_cls = HalfRateGENSDRPHY
            elif sdram_rate == "1:4":
                sdrphy_cls = QuarterRateGENSDRPHY
            else:
                sdrphy_cls = GENSDRPHY

            self.sdrphy = sdrphy_cls(platform.request("sdram"), sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.sdrphy,
                module        = W9825G6KH6(sys_clk_freq, sdram_rate),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # USB Host ---------------------------------------------------------------------------------
        if with_usb_host:
            self.usb_ohci = USBOHCI(platform, platform.request("usb_host"), usb_clk_freq=int(48e6))
            self.bus.add_slave("usb_ohci_ctrl", self.usb_ohci.wb_ctrl, region=SoCRegion(origin=self.mem_map["usb_ohci"], size=0x100000, cached=False))
            self.dma_bus.add_master("usb_ohci_dma", master=self.usb_ohci.wb_dma)
            self.comb += self.cpu.interrupt[16].eq(self.usb_ohci.interrupt)

        # VGA Framebuffer --------------------------------------------------------------------------
        #self.videophy = VideoVGAPHY(platform.request("vga"),
        #    clock_domain="video")
        #self.add_video_framebuffer(phy=self.videophy, timings="640x480@60Hz",
        #    clock_domain="video", format="rgb565")

        # VGA Terminal -------------------------------------------------------------------------------------
        #self.videophy = VideoVGAPHY(platform.request("vga"),
        #    clock_domain="video")
        #self.add_video_terminal(phy=self.videophy, timings="640x480@60Hz",
        #    clock_domain="video")

        # DDMI Framebuffer -------------------------------------------------------------------------------------
        self.videophy = VideoHDMIPHY(platform.request("ddmi"),
            clock_domain="video")
        self.add_video_framebuffer(phy=self.videophy, timings="640x480@60Hz",
            clock_domain="video", format="rgb565")

        # DDMI Terminal -------------------------------------------------------------------------------------
        #self.videophy = VideoHDMIPHY(platform.request("ddmi"),
        #    clock_domain="video")
        #self.add_video_terminal(phy=self.videophy, timings="640x480@60Hz",
        #    clock_domain="video")

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=machdyne_schoko.Platform, description="LiteX SoC on Schoko.")
    parser.add_target_argument("--flash",           action="store_true",       help="Flash bitstream to MMOD.")
    parser.add_target_argument("--sys-clk-freq",    default=40e6,  type=float, help="System clock frequency.")
    parser.add_target_argument("--revision",        default="v1",              help="Board Revision (v1, v2).")
    parser.add_target_argument("--device",          default="45F",             help="ECP5 device (25F, 45F or 85F).")
    parser.add_target_argument("--cable",           default="usb-blaster",     help="Specify an openFPGALoader cable.")
    parser.add_target_argument("--with-sdcard",     action="store_true",       help="Enable SDCard support.")
    parser.add_target_argument("--with-spi-sdcard", action="store_true",       help="Enable SPI-mode SDCard support.")
    parser.add_target_argument("--with-usb-host",   action="store_true",       help="Enable USB host support.")
    args = parser.parse_args()

    soc = BaseSoC(
        toolchain    = args.toolchain,
        revision     = args.revision,
        device       = args.device,
        sys_clk_freq = args.sys_clk_freq,
        **parser.soc_argdict)

    if args.with_sdcard:
        soc.add_sdcard()

    if args.with_spi_sdcard:
        soc.add_spi_sdcard()

    builder = Builder(soc, **parser.builder_argdict)

    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer(args.cable)
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer(args.cable)
        prog.flash(0x100000, builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
