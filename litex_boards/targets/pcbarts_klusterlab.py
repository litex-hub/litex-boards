#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2023 Hans Baier <hansfbaier@gmail.com>
#
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import *

from litex_boards.platforms import pcbarts_klusterlab

from litex.soc.cores.clock          import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder  import *
from litex.soc.cores.led            import LedChaser
from litex.soc.cores.video          import VideoS7HDMIPHY

from liteeth.phy.k7_1000basex import K7_1000BASEX

from litedram.modules import MT41J256M16
from litedram.common import PHYPadsReducer
from litedram.phy import s7ddrphy

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_video_pll=False):
        self.rst       = Signal()
        self.cd_sys    = ClockDomain()
        self.cd_sys4x  = ClockDomain()
        self.cd_hdmi   = ClockDomain()
        self.cd_hdmi5x = ClockDomain()
        self.cd_idelay = ClockDomain()

        # # #
        cpu_reset = Signal()
        self.pll = pll = S7PLL(speedgrade=-2)

        pll.register_clkin(platform.request("clk200"), 200e6)
        pll.create_clkout(self.cd_sys,    sys_clk_freq)
        pll.create_clkout(self.cd_sys4x,  4*sys_clk_freq)
        pll.create_clkout(self.cd_idelay, 200e6)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        self.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

        self.comb += [
            cpu_reset.eq(platform.request("cpu_reset")),
            pll.reset.eq(cpu_reset | self.rst),
        ]

        # Video PLL.
        if with_video_pll:
            self.video_pll = video_pll = S7MMCM(speedgrade=-1)
            video_pll.reset.eq(cpu_reset | self.rst)
            video_pll.register_clkin(ClockSignal(), sys_clk_freq)
            video_pll.create_clkout(self.cd_hdmi,   40e6)
            video_pll.create_clkout(self.cd_hdmi5x, 5*40e6)



# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=100e6,
        with_ethernet          = False,
        with_led_chaser        = True,
        with_video_terminal    = False,
        with_video_framebuffer = False,
        with_video_colorbars   = False,
        **kwargs):
        platform = pcbarts_klusterlab.Platform()

        # CRG --------------------------------------------------------------------------------------
        with_video_pll = (with_video_terminal or with_video_framebuffer or with_video_colorbars)
        self.crg = _CRG(platform, sys_clk_freq, with_video_pll=with_video_pll)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on PCBArts KlusterLab", **kwargs)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.ddrphy = s7ddrphy.K7DDRPHY(
                pads         = PHYPadsReducer(platform.request("ddram"), [0, 1]),
                memtype      = "DDR3",
                nphases      = 4,
                sys_clk_freq = sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT41J256M16(sys_clk_freq, "1:4"),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Ethernet ---------------------------------------------------------------------------------
        if with_ethernet:
            # phy
            refclk = Signal()
            self.comb += [
                refclk.eq(ClockSignal("idelay")),
                self.platform.request("sfp_tx_disable_n", 0).eq(1)
            ]
            self.ethphy = K7_1000BASEX(
                refclk_or_clk_pads = refclk,
                data_pads    = self.platform.request("sfp", 0),
                sys_clk_freq = self.clk_freq)

            self.add_ethernet(phy=self.ethphy)
            self.add_etherbone(phy=self.ethphy, ip_address="192.168.0.222")
            platform.add_platform_command("set_property SEVERITY {{Warning}} [get_drc_checks REQP-52]")

        # Video ------------------------------------------------------------------------------------
        if (with_video_colorbars or with_video_framebuffer or with_video_terminal):
            self.submodules.videophy = VideoS7HDMIPHY(platform.request("hdmi_out"), clock_domain="hdmi")
            if with_video_colorbars:
                self.add_video_colorbars(phy=self.videophy, timings="640x480@60Hz", clock_domain="hdmi")
            if with_video_terminal:
                self.add_video_terminal(phy=self.videophy, timings="800x600@60Hz", clock_domain="hdmi")
            if with_video_framebuffer:
                self.add_video_framebuffer(phy=self.videophy, timings="800x600@60Hz", clock_domain="hdmi")

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=pcbarts_klusterlab.Platform, description="LiteX SoC on PCBArts KlusterLab")
    parser.add_target_argument("--sys-clk-freq", default=100e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-ethernet",  action="store_true",        help="Enable Ethernet support.")
    sdopts = parser.target_group.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-sdcard", action="store_true", help="Enable SPI-mode SDCard support.")
    sdopts.add_argument("--with-sdcard",     action="store_true", help="Enable SDCard support.")
    viopts = parser.target_group.add_mutually_exclusive_group()
    viopts.add_argument("--with-video-terminal",    action="store_true", help="Enable Video Terminal (HDMI).")
    viopts.add_argument("--with-video-framebuffer", action="store_true", help="Enable Video Framebuffer (HDMI).")
    viopts.add_argument("--with-video-colorbars",   action="store_true", help="Enable Video Colorbars (HDMI).")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq           = args.sys_clk_freq,
        with_ethernet          = args.with_ethernet,
        with_video_colorbars   = args.with_video_colorbars,
        with_video_framebuffer = args.with_video_framebuffer,
        with_video_terminal    = args.with_video_terminal,
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
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
