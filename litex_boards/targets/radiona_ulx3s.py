#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2018-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2018 David Shah <dave@ds0.me>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from litex.build.io import DDROutput

from litex_boards.platforms import radiona_ulx3s

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.video import VideoHDMIPHY
from litex.soc.cores.led import LedChaser
from litex.soc.cores.spi import SPIMaster
from litex.soc.cores.gpio import GPIOOut

from litedram import modules as litedram_modules
from litedram.phy import GENSDRPHY, HalfRateGENSDRPHY

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_usb_pll=False, with_video_pll=False, sdram_rate="1:1"):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()
        if sdram_rate == "1:2":
            self.cd_sys2x    = ClockDomain()
            self.cd_sys2x_ps = ClockDomain()
        else:
            self.cd_sys_ps = ClockDomain()

        # # #

        # Clk / Rst
        clk25 = platform.request("clk25")
        rst   = platform.request("rst")

        # PLL
        self.pll = pll = ECP5PLL()
        self.comb += pll.reset.eq(rst | self.rst)
        pll.register_clkin(clk25, 25e6)
        pll.create_clkout(self.cd_sys,    sys_clk_freq)
        if sdram_rate == "1:2":
            pll.create_clkout(self.cd_sys2x,    2*sys_clk_freq)
            pll.create_clkout(self.cd_sys2x_ps, 2*sys_clk_freq, phase=180) # Idealy 90° but needs to be increased.
        else:
           pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=90)

        # USB PLL
        if with_usb_pll:
            self.usb_pll = usb_pll = ECP5PLL()
            self.comb += usb_pll.reset.eq(rst | self.rst)
            usb_pll.register_clkin(clk25, 25e6)
            self.cd_usb_12 = ClockDomain()
            self.cd_usb_48 = ClockDomain()
            usb_pll.create_clkout(self.cd_usb_12, 12e6, margin=0)
            usb_pll.create_clkout(self.cd_usb_48, 48e6, margin=0)

        # Video PLL
        if with_video_pll:
            self.video_pll = video_pll = ECP5PLL()
            self.comb += video_pll.reset.eq(rst | self.rst)
            video_pll.register_clkin(clk25, 25e6)
            self.cd_hdmi   = ClockDomain()
            self.cd_hdmi5x = ClockDomain()
            video_pll.create_clkout(self.cd_hdmi,    25e6, margin=0)
            video_pll.create_clkout(self.cd_hdmi5x, 125e6, margin=0)

        # SDRAM clock
        sdram_clk = ClockSignal("sys2x_ps" if sdram_rate == "1:2" else "sys_ps")
        self.specials += DDROutput(1, 0, platform.request("sdram_clock"), sdram_clk)

        # Prevent ESP32 from resetting FPGA
        self.comb += platform.request("wifi_gpio0").eq(1)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, device="LFE5U-45F", revision="2.0", toolchain="trellis", sys_clk_freq=50e6,
        sdram_module_cls       = "MT48LC16M16",
        sdram_rate             = "1:1",
        with_led_chaser        = True,
        with_video_terminal    = False,
        with_video_framebuffer = False,
        with_spi_flash         = False,
        **kwargs):
        platform = radiona_ulx3s.Platform(device=device, revision=revision, toolchain=toolchain)

        # CRG --------------------------------------------------------------------------------------
        with_usb_pll   = kwargs.get("uart_name", None) == "usb_acm"
        with_video_pll = with_video_terminal or with_video_framebuffer
        self.crg = _CRG(platform, sys_clk_freq, with_usb_pll, with_video_pll, sdram_rate=sdram_rate)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on ULX3S", **kwargs)

        # SDR SDRAM --------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            sdrphy_cls = HalfRateGENSDRPHY if sdram_rate == "1:2" else GENSDRPHY
            self.sdrphy = sdrphy_cls(platform.request("sdram"), sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.sdrphy,
                module        = getattr(litedram_modules, sdram_module_cls)(sys_clk_freq, sdram_rate),
                size          = 0x40000000,
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Video ------------------------------------------------------------------------------------
        if with_video_terminal or with_video_framebuffer:
            self.videophy = VideoHDMIPHY(platform.request("gpdi"), clock_domain="hdmi")
            if with_video_terminal:
                self.add_video_terminal(phy=self.videophy, timings="640x480@75Hz", clock_domain="hdmi")
            if with_video_framebuffer:
                self.add_video_framebuffer(phy=self.videophy, timings="640x480@75Hz", clock_domain="hdmi")

        # SPI Flash --------------------------------------------------------------------------------
        if with_spi_flash:
            from litespi.modules import IS25LP128
            from litespi.opcodes import SpiNorFlashOpCodes as Codes
            self.add_spi_flash(mode="4x", module=IS25LP128(Codes.READ_1_1_4))

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

    def add_oled(self):
        pads = self.platform.request("oled_spi")
        pads.miso = Signal()
        self.oled_spi = SPIMaster(pads, 8, self.sys_clk_freq, 8e6)
        self.oled_spi.add_clk_divider()

        self.oled_ctl = GPIOOut(self.platform.request("oled_ctl"))

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=radiona_ulx3s.Platform, description="LiteX SoC on ULX3S")
    parser.add_target_argument("--device",          default="LFE5U-45F",      help="FPGA device (LFE5U-12F, LFE5U-25F, LFE5U-45F or LFE5U-85F).")
    parser.add_target_argument("--revision",        default="2.0",            help="Board revision (2.0 or 1.7).")
    parser.add_target_argument("--sys-clk-freq",    default=50e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--sdram-module",    default="MT48LC16M16",    help="SDRAM module (MT48LC16M16, AS4C32M16 or AS4C16M16).")
    parser.add_target_argument("--with-spi-flash",  action="store_true",      help="Enable SPI Flash (MMAPed).")
    sdopts = parser.target_group.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-sdcard",   action="store_true", help="Enable SPI-mode SDCard support.")
    sdopts.add_argument("--with-sdcard",       action="store_true", help="Enable SDCard support.")
    parser.add_target_argument("--with-oled",  action="store_true", help="Enable SDD1331 OLED support.")
    parser.add_target_argument("--sdram-rate", default="1:1",       help="SDRAM Rate (1:1 Full Rate or 1:2 Half Rate).")
    viopts = parser.target_group.add_mutually_exclusive_group()
    viopts.add_argument("--with-video-terminal",    action="store_true", help="Enable Video Terminal (HDMI).")
    viopts.add_argument("--with-video-framebuffer", action="store_true", help="Enable Video Framebuffer (HDMI).")
    args = parser.parse_args()

    soc = BaseSoC(
        device                 = args.device,
        revision               = args.revision,
        toolchain              = args.toolchain,
        sys_clk_freq           = args.sys_clk_freq,
        sdram_module_cls       = args.sdram_module,
        sdram_rate             = args.sdram_rate,
        with_video_terminal    = args.with_video_terminal,
        with_video_framebuffer = args.with_video_framebuffer,
        with_spi_flash         = args.with_spi_flash,
        **parser.soc_argdict)
    if args.with_spi_sdcard:
        soc.add_spi_sdcard()
    if args.with_sdcard:
        soc.add_sdcard()
    if args.with_oled:
        soc.add_oled()

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram", ext=".svf")) # FIXME

if __name__ == "__main__":
    main()
