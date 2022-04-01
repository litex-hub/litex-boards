#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Lucas Teske <lucas@teske.com.br>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.build.io import DDROutput

from litex_boards.platforms import muselab_icesugar_pro

from litex.build.lattice.trellis import trellis_args, trellis_argdict

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.video import VideoHDMIPHY
from litex.soc.cores.led import LedChaser

from litex.soc.interconnect.csr import *

from litedram.modules import IS42S16160
from litedram.phy import GENSDRPHY, HalfRateGENSDRPHY

from liteeth.phy.ecp5rgmii import LiteEthPHYRGMII

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq, use_internal_osc=False, with_video_pll=False, sdram_rate="1:1"):
        self.rst = Signal()
        self.clock_domains.cd_sys    = ClockDomain()
        if sdram_rate == "1:2":
            self.clock_domains.cd_sys2x    = ClockDomain()
            self.clock_domains.cd_sys2x_ps = ClockDomain()
        else:
            self.clock_domains.cd_sys_ps = ClockDomain()

        # # #

        # Clk / Rst
        if not use_internal_osc:
            clk = platform.request("clk25")
            clk_freq = 25e6
        else:
            clk = Signal()
            div = 5
            self.specials += Instance("OSCG",
                p_DIV = div,
                o_OSC = clk
            )
            clk_freq = 310e6/div

        rst_n = platform.request("cpu_reset_n")

        # PLL
        self.submodules.pll = pll = ECP5PLL()
        self.comb += pll.reset.eq(~rst_n | self.rst)
        pll.register_clkin(clk, clk_freq)
        pll.create_clkout(self.cd_sys,    sys_clk_freq)
        if sdram_rate == "1:2":
            pll.create_clkout(self.cd_sys2x,    2*sys_clk_freq)
            pll.create_clkout(self.cd_sys2x_ps, 2*sys_clk_freq, phase=180) # Idealy 90° but needs to be increased.
        else:
           pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=180) # Idealy 90° but needs to be increased.

        # Video PLL
        if with_video_pll:
            self.submodules.video_pll = video_pll = ECP5PLL()
            self.comb += video_pll.reset.eq(~rst_n | self.rst)
            video_pll.register_clkin(clk, clk_freq)
            self.clock_domains.cd_hdmi   = ClockDomain()
            self.clock_domains.cd_hdmi5x = ClockDomain()
            video_pll.create_clkout(self.cd_hdmi,    40e6, margin=0)
            video_pll.create_clkout(self.cd_hdmi5x, 200e6, margin=0)

        # SDRAM clock
        sdram_clk = ClockSignal("sys2x_ps" if sdram_rate == "1:2" else "sys_ps")
        self.specials += DDROutput(1, 0, platform.request("sdram_clock"), sdram_clk)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=60e6, with_led_chaser=True, with_spi_flash=False,
                 use_internal_osc=False, sdram_rate="1:1", with_video_terminal=False,
                 with_video_framebuffer=False, **kwargs):
        platform = muselab_icesugar_pro.Platform()

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, int(sys_clk_freq),
            ident = "LiteX SoC on Muselab iCESugar Pro",
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        with_video_pll = with_video_terminal or with_video_framebuffer
        self.submodules.crg = _CRG(platform, sys_clk_freq, use_internal_osc=use_internal_osc, with_video_pll=with_video_pll, sdram_rate=sdram_rate)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            ledn = platform.request_all("user_led_n")
            self.submodules.leds = LedChaser(pads=ledn, sys_clk_freq=sys_clk_freq)

        # SPI Flash --------------------------------------------------------------------------------
        if with_spi_flash:
            from litespi.modules import W25Q256
            from litespi.opcodes import SpiNorFlashOpCodes as Codes
            self.add_spi_flash(mode="1x", module=W25Q256(Codes.READ_1_1_1))

        # SDR SDRAM --------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            sdrphy_cls = HalfRateGENSDRPHY if sdram_rate == "1:2" else GENSDRPHY
            self.submodules.sdrphy = sdrphy_cls(platform.request("sdram"))
            self.add_sdram("sdram",
                phy           = self.sdrphy,
                module        = IS42S16160(sys_clk_freq, sdram_rate),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Video ------------------------------------------------------------------------------------
        if with_video_terminal or with_video_framebuffer:
            self.submodules.videophy = VideoHDMIPHY(platform.request("gpdi"), clock_domain="hdmi")
            if with_video_terminal:
                self.add_video_terminal(phy=self.videophy, timings="800x600@60Hz", clock_domain="hdmi")
            if with_video_framebuffer:
                self.add_video_framebuffer(phy=self.videophy, timings="800x600@60Hz", clock_domain="hdmi")

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on Colorlight i5")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",            action="store_true",      help="Build bitstream.")
    target_group.add_argument("--load",             action="store_true",      help="Load bitstream.")
    target_group.add_argument("--sys-clk-freq",     default=60e6,             help="System clock frequency.")
    sdopts = target_group.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-sdcard",  action="store_true",  help="Enable SPI-mode SDCard support.")
    sdopts.add_argument("--with-sdcard",      action="store_true",  help="Enable SDCard support.")
    target_group.add_argument("--with-spi-flash",   action="store_true",  help="Enable SPI Flash (MMAPed).")
    target_group.add_argument("--use-internal-osc", action="store_true",  help="Use internal oscillator.")
    target_group.add_argument("--sdram-rate",       default="1:1",        help="SDRAM Rate (1:1 Full Rate or 1:2 Half Rate).")
    viopts = target_group.add_mutually_exclusive_group()
    viopts.add_argument("--with-video-terminal",    action="store_true", help="Enable Video Terminal (HDMI).")
    viopts.add_argument("--with-video-framebuffer", action="store_true", help="Enable Video Framebuffer (HDMI).")
    builder_args(parser)
    soc_core_args(parser)
    trellis_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq           = int(float(args.sys_clk_freq)),
        use_internal_osc       = args.use_internal_osc,
        sdram_rate             = args.sdram_rate,
        with_spi_flash         = args.with_spi_flash,
        with_video_terminal    = args.with_video_terminal,
        with_video_framebuffer = args.with_video_framebuffer,
        **soc_core_argdict(args)
    )
    if args.with_spi_sdcard:
        soc.add_spi_sdcard()
    if args.with_sdcard:
        soc.add_sdcard()

    builder = Builder(soc, **builder_argdict(args))

    builder.build(**trellis_argdict(args), run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
