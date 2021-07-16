#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Shinken Sanada <sanadashinken@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

import os
import argparse

from migen import *

from litex_boards.platforms import qmtech_wukong
from litex.build.xilinx.vivado import vivado_build_args, vivado_build_argdict

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.video import VideoS7HDMIPHY
from litex.soc.cores.video import video_timings
from litex.soc.cores.led import LedChaser
from litex.soc.cores.gpio import GPIOIn

from litedram.modules import MT41K128M16
from litedram.phy import s7ddrphy

from liteeth.phy import LiteEthPHY
from liteeth.phy import LiteEthPHYMII

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq, with_video_pll=False, pix_clk=25.175e6):
        self.rst = Signal()
        self.clock_domains.cd_sys       = ClockDomain()
        self.clock_domains.cd_sys4x     = ClockDomain(reset_less=True)
        self.clock_domains.cd_sys4x_dqs = ClockDomain(reset_less=True)
        self.clock_domains.cd_idelay    = ClockDomain()
        self.clock_domains.cd_clk100    = ClockDomain()
        self.clock_domains.cd_hdmi      = ClockDomain()
        self.clock_domains.cd_hdmi5x    = ClockDomain()

        # # #

        plls_reset = platform.request("cpu_reset")
        plls_clk50 = platform.request("clk50")

        self.submodules.pll = pll = S7MMCM(speedgrade=-2)
        self.comb += pll.reset.eq(~plls_reset | self.rst)
        pll.register_clkin(plls_clk50, 50e6)
        pll.create_clkout(self.cd_sys,       sys_clk_freq)
        pll.create_clkout(self.cd_sys4x,     4*sys_clk_freq)
        pll.create_clkout(self.cd_sys4x_dqs, 4*sys_clk_freq, phase=90)
        #pll.create_clkout(self.cd_idelay,    200e6)

        # idelay PLL
        self.submodules.pll_idelay = pll_idelay = S7PLL(speedgrade=-2)
        self.comb += pll_idelay.reset.eq(~plls_reset | self.rst)
        pll_idelay.register_clkin(plls_clk50, 50e6)
        pll_idelay.create_clkout(self.cd_idelay, 200e6)
        pll_idelay.create_clkout(self.cd_clk100, 100e6)

        self.submodules.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

        # Video PLL.
        if with_video_pll:
            self.submodules.video_pll = video_pll = S7MMCM(speedgrade=-2)
            self.comb += video_pll.reset.eq(~plls_reset | self.rst)
            video_pll.register_clkin(plls_clk50, 50e6)
            video_pll.create_clkout(self.cd_hdmi,   pix_clk)
            video_pll.create_clkout(self.cd_hdmi5x, 5*pix_clk)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(100e6), with_ethernet=False, with_etherbone=False,
                 eth_ip="192.168.1.50", with_led_chaser=True, with_video_terminal=False,
                 with_video_framebuffer=False, video_timing="640x480@60Hz", **kwargs):
        platform = qmtech_wukong.Platform()

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident          = "LiteX SoC on QMTECH Wukong Board",
            ident_version  = True,
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        with_video_pll = (with_video_terminal or with_video_framebuffer)
        self.submodules.crg = _CRG(platform, sys_clk_freq, with_video_pll=with_video_pll, pix_clk = video_timings[video_timing]["pix_clk"])

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.submodules.ddrphy = s7ddrphy.A7DDRPHY(platform.request("ddram"),
                memtype        = "DDR3",
                nphases        = 4,
                sys_clk_freq   = sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT41K128M16(sys_clk_freq, "1:4"),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            self.submodules.ethphy = LiteEthPHY(
                clock_pads = self.platform.request("eth_clocks"),
                pads       = self.platform.request("eth"),
                clk_freq   = sys_clk_freq)
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy, nrxslots=2)
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, ip_address=eth_ip)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

        # Video ------------------------------------------------------------------------------------
        if with_video_terminal or with_video_framebuffer:
            self.submodules.videophy = VideoS7HDMIPHY(platform.request("hdmi_out"), clock_domain="hdmi")
            if with_video_terminal:
                self.add_video_terminal(phy=self.videophy, timings=video_timing, clock_domain="hdmi")
            if with_video_framebuffer:
                self.add_video_framebuffer(phy=self.videophy, timings=video_timing, clock_domain="hdmi")
# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on QMTECH Wukong Board")
    parser.add_argument("--build",           action="store_true",              help="Build bitstream")
    parser.add_argument("--load",            action="store_true",              help="Load bitstream")
    parser.add_argument("--sys-clk-freq",    default=100e6,                    help="System clock frequency (default: 100MHz)")
    ethopts = parser.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",  action="store_true",              help="Enable Ethernet support")
    ethopts.add_argument("--with-etherbone", action="store_true",              help="Enable Etherbone support")
    parser.add_argument("--eth-ip",          default="192.168.1.50", type=str, help="Ethernet/Etherbone IP address")
    sdopts = parser.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-sdcard", action="store_true",              help="Enable SPI-mode SDCard support")
    sdopts.add_argument("--with-sdcard",     action="store_true",              help="Enable SDCard support")
    viopts = parser.add_mutually_exclusive_group()
    viopts.add_argument("--with-video-terminal",    action="store_true", help="Enable Video Terminal (HDMI)")
    viopts.add_argument("--with-video-framebuffer", action="store_true", help="Enable Video Framebuffer (HDMI)")
    builder_args(parser)
    soc_core_args(parser)
    vivado_build_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq   = int(float(args.sys_clk_freq)),
        with_ethernet  = args.with_ethernet,
        with_etherbone = args.with_etherbone,
        eth_ip         = args.eth_ip,
        with_video_terminal    = args.with_video_terminal,
        with_video_framebuffer = args.with_video_framebuffer,
        **soc_core_argdict(args)
    )
    if args.with_spi_sdcard:
        soc.platform.add_extension(qmtech_wukong._sdcard_pmod_io)
        soc.add_spi_sdcard()
    if args.with_sdcard:
        soc.platform.add_extension(qmtech_wukong._sdcard_pmod_io)
        soc.add_sdcard()

    builder = Builder(soc, **builder_argdict(args))

    builder.build(**vivado_build_argdict(args), run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".bit"))

if __name__ == "__main__":
    main()
