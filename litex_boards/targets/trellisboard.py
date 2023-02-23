#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019 David Shah <dave@ds0.me>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from litex_boards.platforms import trellisboard

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.gpio import GPIOTristate
from litex.soc.cores.video import VideoDVIPHY
from litex.soc.cores.bitbang import I2CMaster

from litedram.modules import MT41J256M16
from litedram.phy import ECP5DDRPHY

from liteeth.phy.ecp5rgmii import LiteEthPHYRGMII

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst    = Signal()
        self.cd_por = ClockDomain()
        self.cd_sys = ClockDomain()

        # # #

        # Clk / Rst
        clk12 = platform.request("clk12")
        rst   = platform.request("user_btn", 0)

        # Power on reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += self.cd_por.clk.eq(clk12)
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # PLL
        self.pll = pll = ECP5PLL()
        self.comb += pll.reset.eq(~por_done | rst | self.rst)
        pll.register_clkin(clk12, 12e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)


class _CRGSDRAM(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst        = Signal()
        self.cd_init    = ClockDomain()
        self.cd_por     = ClockDomain()
        self.cd_sys     = ClockDomain()
        self.cd_sys2x   = ClockDomain()
        self.cd_sys2x_i = ClockDomain()

        # # #

        self.stop  = Signal()
        self.reset = Signal()

        # Clk / Rst
        clk12 = platform.request("clk12")
        rst   = platform.request("user_btn", 0)

        # Power on reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += self.cd_por.clk.eq(clk12)
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # PLL
        sys2x_clk_ecsout = Signal()
        self.pll = pll = ECP5PLL()
        self.comb += pll.reset.eq(~por_done | rst | self.rst)
        pll.register_clkin(clk12, 12e6)
        pll.create_clkout(self.cd_sys2x_i, 2*sys_clk_freq)
        pll.create_clkout(self.cd_init,   25e6)
        self.specials += [
            Instance("ECLKBRIDGECS",
                i_CLK0   = self.cd_sys2x_i.clk,
                i_SEL    = 0,
                o_ECSOUT = sys2x_clk_ecsout,
            ),
            Instance("ECLKSYNCB",
                i_ECLKI = sys2x_clk_ecsout,
                i_STOP  = self.stop,
                o_ECLKO = self.cd_sys2x.clk),
            Instance("CLKDIVF",
                p_DIV     = "2.0",
                i_ALIGNWD = 0,
                i_CLKI    = self.cd_sys2x.clk,
                i_RST     = self.reset,
                o_CDIVX   = self.cd_sys.clk),
            AsyncResetSynchronizer(self.cd_sys, ~pll.locked | self.reset),
        ]

        self.comb += platform.request("dram_vtt_en").eq(1)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=75e6, toolchain="trellis",
        with_ethernet          = False,
        with_video_terminal    = False,
        with_video_framebuffer = False,
        with_led_chaser        = True,
        with_pmod_gpio         = False,
        **kwargs):
        platform = trellisboard.Platform(toolchain=toolchain)

        # CRG --------------------------------------------------------------------------------------
        crg_cls = _CRGSDRAM if kwargs.get("integrated_main_ram_size", 0) == 0 else _CRG
        self.crg = crg_cls(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Trellis Board", **kwargs)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.ddrphy = ECP5DDRPHY(
                platform.request("ddram"),
                sys_clk_freq=sys_clk_freq)
            self.comb += self.crg.stop.eq(self.ddrphy.init.stop)
            self.comb += self.crg.reset.eq(self.ddrphy.init.reset)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT41J256M16(sys_clk_freq, "1:2"),
                l2_cache_size = kwargs.get("l2_size", 8192),
            )

        # Ethernet ---------------------------------------------------------------------------------
        if with_ethernet:
            self.ethphy = LiteEthPHYRGMII(
                clock_pads = self.platform.request("eth_clocks"),
                pads       = self.platform.request("eth"))
            self.add_ethernet(phy=self.ethphy)

        # HDMI -------------------------------------------------------------------------------------
        if with_video_terminal or with_video_framebuffer:
            # PHY + TP410 I2C initialization.
            hdmi_pads = platform.request("hdmi")
            self.videophy = VideoDVIPHY(hdmi_pads, clock_domain="init")
            self.videoi2c = I2CMaster(hdmi_pads)
            self.videoi2c.add_init(addr=0x38, init=[
                (0x08, 0x35) # CTL_1_MODE: Normal operation, 24-bit, HSYNC/VSYNC.
            ])

            # Video Terminal/Framebuffer.
            if with_video_terminal:
                self.add_video_terminal(phy=self.videophy, timings="640x480@75Hz", clock_domain="init")
            if with_video_framebuffer:
                self.add_video_framebuffer(phy=self.videophy, timings="640x480@75Hz", clock_domain="init")

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

        # GPIOs ------------------------------------------------------------------------------------
        if with_pmod_gpio:
            platform.add_extension(trellisboard.raw_pmod_io("pmoda"))
            self.gpio = GPIOTristate(platform.request("pmoda"))

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=trellisboard.Platform, description="LiteX SoC on Trellis Board.")
    parser.add_target_argument("--sys-clk-freq",    default=75e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-ethernet",   action="store_true",      help="Enable Ethernet support.")
    viopts = parser.target_group.add_mutually_exclusive_group()
    viopts.add_argument("--with-video-terminal",    action="store_true", help="Enable Video Terminal (HDMI).")
    viopts.add_argument("--with-video-framebuffer", action="store_true", help="Enable Video Framebuffer (HDMI).")
    sdopts = parser.target_group.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-sdcard",       action="store_true", help="Enable SPI-mode SDCard support.")
    sdopts.add_argument("--with-sdcard",           action="store_true", help="Enable SDCard support.")
    parser.add_target_argument("--with-pmod-gpio", action="store_true", help="Enable GPIOs through PMOD.") # FIXME: Temporary test.
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq           = args.sys_clk_freq,
        toolchain              = args.toolchain,
        with_ethernet          = args.with_ethernet,
        with_video_terminal    = args.with_video_terminal,
        with_video_framebuffer = args.with_video_framebuffer,
        with_pmod_gpio         = args.with_pmod_gpio,
        **parser.soc_argdict
    )
    if args.with_spi_sdcard:
        soc.add_spi_sdcard()
    if args.with_sdcard:
        soc.add_sdcard()
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram", ext=".svf")) # FIXME

if __name__ == "__main__":
    main()
