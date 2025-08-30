#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import *

from litex.build.io import CRG
from litex.build.io import DDROutput

from litex_boards.platforms import icepi_zero

from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.video import VideoHDMIPHY
from litex.soc.cores.clock import *
from litex.soc.cores.led import LedChaser

from litedram import modules as litedram_modules
from litedram.phy import GENSDRPHY, HalfRateGENSDRPHY

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_usb_pll=False, with_video_pll=False, video_pll_type="video", sdram_rate="1:1"):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()
        if sdram_rate == "1:2":
            self.cd_sys2x    = ClockDomain()
            self.cd_sys2x_ps = ClockDomain()
        else:
            self.cd_sys_ps = ClockDomain()

        # Clock
        clk50 = platform.request("clk50")
        rst   = platform.request("rst")

        # PLL
        self.pll = pll = ECP5PLL()
        self.comb += pll.reset.eq(~rst)
        pll.register_clkin(clk50, 50e6)
        pll.create_clkout(self.cd_sys,    sys_clk_freq)
        if sdram_rate == "1:2":
            pll.create_clkout(self.cd_sys2x,    2*sys_clk_freq)
            pll.create_clkout(self.cd_sys2x_ps, 2*sys_clk_freq, phase=180) # Idealy 90° but needs to be increased.
        else:
           pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=90)

        # USB PLL
        if with_usb_pll:
            self.usb_pll = usb_pll = ECP5PLL()
            self.comb += usb_pll.reset.eq(~rst)
            usb_pll.register_clkin(clk50, 50e6)
            self.cd_usb_12 = ClockDomain()
            self.cd_usb_48 = ClockDomain()
            usb_pll.create_clkout(self.cd_usb_12, 12e6, margin=0)
            usb_pll.create_clkout(self.cd_usb_48, 48e6, margin=0)

        # Video PLL
        if with_video_pll:
            self.video_pll = video_pll = ECP5PLL()
            self.comb += video_pll.reset.eq(~rst)
            video_pll.register_clkin(clk50, 50e6)
            self.cd_hdmi   = ClockDomain()
            self.cd_hdmi5x = ClockDomain()

            if video_pll_type == "video":
                video_pll.create_clkout(self.cd_hdmi,    25e6, margin=0)
                video_pll.create_clkout(self.cd_hdmi5x, 125e6, margin=0)
            if video_pll_type == "terminal":
                video_pll.create_clkout(self.cd_hdmi,    40e6, margin=0)
                video_pll.create_clkout(self.cd_hdmi5x, 200e6, margin=0)

        # SDRAM clock
        sdram_clk = ClockSignal("sys2x_ps" if sdram_rate == "1:2" else "sys_ps")
        self.specials += DDROutput(1, 0, platform.request("sdram_clock"), sdram_clk)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, device="LFE5U-25F", toolchain="trellis", sys_clk_freq=50e6,
        sdram_module_cls       = "W9825G6KH6",
        sdram_rate             = "1:1",
        with_led_chaser        = True,
        with_video_terminal    = False,
        with_video_framebuffer = False,
        with_spi_flash         = False,
        **kwargs):
        platform = icepi_zero.Platform(device=device, toolchain=toolchain)

        # CRG --------------------------------------------------------------------------------------
        with_usb_pll   = kwargs.get("uart_name", None) == "usb_acm"
        with_video_pll = with_video_terminal or with_video_framebuffer
        video_pll_type = "video" if with_video_framebuffer else "terminal"
        self.crg = _CRG(platform, sys_clk_freq, with_usb_pll, with_video_pll, video_pll_type, sdram_rate=sdram_rate)

        # SoCCore ----------------------------------------------------------------------------------
        # Disable Integrated ROM since too large for iCE40.
        # kwargs["integrated_rom_size"]  = 0
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Icepi Zero", **kwargs)

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

        # SPI Flash --------------------------------------------------------------------------------
        if with_spi_flash:
            from litespi.modules import W25Q128JV
            from litespi.opcodes import SpiNorFlashOpCodes as Codes
            self.add_spi_flash(mode="4x", module=W25Q128JV(Codes.READ_1_1_4)) # with_master=False?

        # Video ------------------------------------------------------------------------------------
        if with_video_terminal or with_video_framebuffer:
            self.videophy = VideoHDMIPHY(platform.request("gpdi"), clock_domain="hdmi")
            if with_video_terminal:
                self.add_video_terminal(phy=self.videophy, timings="800x600@60Hz", clock_domain="hdmi")
            if with_video_framebuffer:
                self.add_video_framebuffer(phy=self.videophy, timings="640x480@60Hz", clock_domain="hdmi")

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser or True:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=icepi_zero.Platform, description="LiteX SoC on Icepi Zero.")
    parser.add_target_argument("--device",            default="LFE5U-25F",      help="FPGA device (LFE5U-25F).")
    parser.add_target_argument("--sdram-module",      default="W9825G6KH6",      help="SDRAM module (W9825G6KH6).")
    parser.add_target_argument("--sdram-rate", default="1:1",       help="SDRAM Rate (1:1 Full Rate or 1:2 Half Rate).")
    parser.add_target_argument("--with-spi-flash",  action="store_true",      help="Enable SPI Flash (MMAPed).")
    parser.add_target_argument("--sys-clk-freq",      default=50e6, type=float,  help="System clock frequency.")

    sdopts = parser.target_group.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-sdcard",   action="store_true", help="Enable SPI-mode SDCard support.")
    sdopts.add_argument("--with-sdcard",       action="store_true", help="Enable SDCard support.")

    viopts = parser.target_group.add_mutually_exclusive_group()
    viopts.add_argument("--with-video-terminal",    action="store_true", help="Enable Video Terminal (HDMI).")
    viopts.add_argument("--with-video-framebuffer", action="store_true", help="Enable Video Framebuffer (HDMI).")

    args = parser.parse_args()

    soc = BaseSoC(
        device                 = args.device,
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

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram", ext=".bit"))


if __name__ == "__main__":
    main()
