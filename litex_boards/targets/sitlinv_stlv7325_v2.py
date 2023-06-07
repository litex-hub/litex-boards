#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2023 Gabriel Somlo <gsomlo@gmail.com>
# Copyright (c) 2022 Andrew Gillham <gillham@roadsign.com>
# Copyright (c) 2014-2015 Sebastien Bourdeauducq <sb@m-labs.hk>
# Copyright (c) 2014-2020 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2014-2015 Yann Sionneau <ys@m-labs.hk>
# SPDX-License-Identifier: BSD-2-Clause

import os

from migen import *

from litex.gen import *

from litex_boards.platforms import sitlinv_stlv7325_v2

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.bitbang import I2CMaster
from litex.soc.cores.video   import VideoS7HDMIPHY

from litedram.modules import MT8JTF12864
from litedram.phy import s7ddrphy

from liteeth.phy.s7rgmii import LiteEthPHYRGMII

from litepcie.phy.s7pciephy import S7PCIEPHY
from litepcie.software import generate_litepcie_software

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst       = Signal()
        self.cd_sys    = ClockDomain()
        self.cd_sys4x  = ClockDomain()
        self.cd_idelay = ClockDomain()
        self.cd_hdmi   = ClockDomain()
        self.cd_hdmi5x = ClockDomain()

        # # #

        # Clk/Rst.
        clk200 = platform.request("clk200")
        clk50  = platform.request("clk50")
        rst_n  = platform.request("cpu_reset_n")

        # PLL.
        self.pll = pll = S7PLL(speedgrade=-2)
        self.comb += pll.reset.eq(~rst_n | self.rst)
        pll.register_clkin(clk200, 200e6)
        pll.create_clkout(self.cd_sys,    sys_clk_freq)
        pll.create_clkout(self.cd_sys4x,  4*sys_clk_freq)
        pll.create_clkout(self.cd_idelay, 200e6)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        self.submodules.pll2 = pll2 = S7PLL(speedgrade=-2)
        self.comb += pll2.reset.eq(~rst_n | self.rst)
        pll2.register_clkin(clk50, 50e6)
        pll2.create_clkout(self.cd_hdmi,   25e6,  margin=0)
        pll2.create_clkout(self.cd_hdmi5x, 125e6, margin=0)

        self.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=100e6,
        vccio                  = "3.3V",
        with_ethernet          = False,
        with_led_chaser        = True,
        with_pcie              = False,
        with_sata              = False, sata_gen="gen2",
        with_jtagbone          = False,
        with_video_colorbars   = False,
        with_video_framebuffer = False,
        with_video_terminal    = False,
        **kwargs):
        platform = sitlinv_stlv7325_v2.Platform(vccio)

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Sitlinv STLV7325-v2", **kwargs)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.ddrphy = s7ddrphy.K7DDRPHY(platform.request("ddram"),
                memtype      = "DDR3",
                nphases      = 4,
                sys_clk_freq = sys_clk_freq,
            )
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT8JTF12864(sys_clk_freq, "1:4"),
                l2_cache_size = kwargs.get("l2_size", 8192),
            )

        # Jtagbone ---------------------------------------------------------------------------------
        if with_jtagbone:
            self.add_jtagbone()

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet:
            self.ethphy = LiteEthPHYRGMII(
                clock_pads = self.platform.request("eth_clocks", 0),
                pads       = self.platform.request("eth", 0),
                tx_delay = 1.417e-9,
                rx_delay = 1.417e-9,
            )
            self.add_ethernet(phy=self.ethphy)

        # PCIe -------------------------------------------------------------------------------------
        if with_pcie:
            self.pcie_phy = S7PCIEPHY(platform, platform.request("pcie_x4"),
                data_width = 128,
                bar0_size  = 0x20000)
            self.add_pcie(phy=self.pcie_phy, ndmas=1)

        # TODO verify / test
        # SATA -------------------------------------------------------------------------------------
        if with_sata:
            from litex.build.generic_platform import Subsignal, Pins
            from litesata.phy import LiteSATAPHY

            # RefClk, Generate 150MHz from PLL.
            self.cd_sata_refclk = ClockDomain()
            self.crg.pll.create_clkout(self.cd_sata_refclk, 150e6)
            sata_refclk = ClockSignal("sata_refclk")
            platform.add_platform_command("set_property SEVERITY {{Warning}} [get_drc_checks REQP-52]")

            # PHY
            self.sata_phy = LiteSATAPHY(platform.device,
                refclk     = sata_refclk,
                pads       = platform.request("sata", 0),
                gen        = sata_gen,
                clk_freq   = sys_clk_freq,
                data_width = 16)

            # Core
            self.add_sata(phy=self.sata_phy, mode="read+write")

        # HDMI Options -----------------------------------------------------------------------------
        if (with_video_colorbars or with_video_framebuffer or with_video_terminal):
            self.submodules.videophy = VideoS7HDMIPHY(platform.request("hdmi_out"), clock_domain="hdmi")
            if with_video_colorbars:
                self.add_video_colorbars(phy=self.videophy, timings="640x480@60Hz", clock_domain="hdmi")
            if with_video_terminal:
                self.add_video_terminal(phy=self.videophy, timings="640x480@60Hz", clock_domain="hdmi")
            if with_video_framebuffer:
                self.add_video_framebuffer(phy=self.videophy, timings="640x480@60Hz", clock_domain="hdmi")

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led_n"),
                sys_clk_freq = sys_clk_freq)

        # I2C --------------------------------------------------------------------------------------
        self.i2c = I2CMaster(platform.request("i2c"))

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=sitlinv_stlv7325_v2.Platform, description="LiteX SoC on AliExpress STLV7325-v2.")
    parser.add_target_argument("--sys-clk-freq",  default=100e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--vccio",         default="3.3V", type=str, help="IO Voltage (set by J4), can be 2.5V or 3.3V")
    parser.add_target_argument("--with-pcie",       action="store_true",    help="Enable PCIe support.")
    parser.add_target_argument("--driver",          action="store_true",    help="Generate PCIe driver.")
    parser.add_target_argument("--with-ethernet",   action="store_true",    help="Enable Ethernet support.")
    parser.add_target_argument("--with-sata",       action="store_true",    help="Enable SATA support.")
    parser.add_target_argument("--sata-gen",        default="2",    help="SATA Gen..", choices=["1", "2", "3"])
    parser.add_target_argument("--with-jtagbone",   action="store_true",    help="Enable Jtagbone support.")
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
        vccio                  = args.vccio,
        with_ethernet          = args.with_ethernet,
        with_pcie              = args.with_pcie,
        with_sata              = args.with_sata,
        sata_gen               = "gen" + args.sata_gen,
        with_jtagbone          = args.with_jtagbone,
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

    if args.driver:
        generate_litepcie_software(soc, os.path.join(builder.output_dir, "driver"))

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
