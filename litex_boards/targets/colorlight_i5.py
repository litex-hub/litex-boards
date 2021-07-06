#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Kazumoto Kojima <kkojima@rr.iij4u.or.jp>
# SPDX-License-Identifier: BSD-2-Clause

import os
import argparse
import sys

from migen import *

from litex.build.io import DDROutput

from litex_boards.platforms import colorlight_i5

from litex.build.lattice.trellis import trellis_args, trellis_argdict

from litex.soc.cores.clock import *
from litex.soc.cores.spi_flash import SpiFlash
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.video import VideoECP5HDMIPHY
from litex.soc.cores.led import LedChaser

from litex.soc.interconnect.csr import *

from litedram.modules import M12L64322A # Compatible with EM638325-6H.
from litedram.phy import GENSDRPHY, HalfRateGENSDRPHY

from liteeth.phy.ecp5rgmii import LiteEthPHYRGMII

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq, use_internal_osc=False, with_usb_pll=False, with_video_pll=False, sdram_rate="1:1"):
        self.rst = Signal()
        self.clock_domains.cd_sys    = ClockDomain()
        if sdram_rate == "1:2":
            self.clock_domains.cd_sys2x    = ClockDomain()
            self.clock_domains.cd_sys2x_ps = ClockDomain(reset_less=True)
        else:
            self.clock_domains.cd_sys_ps = ClockDomain(reset_less=True)

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
                                o_OSC = clk)
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

        # USB PLL
        if with_usb_pll:
            self.submodules.usb_pll = usb_pll = ECP5PLL()
            self.comb += usb_pll.reset.eq(~rst_n | self.rst)
            usb_pll.register_clkin(clk, clk_freq)
            self.clock_domains.cd_usb_12 = ClockDomain()
            self.clock_domains.cd_usb_48 = ClockDomain()
            usb_pll.create_clkout(self.cd_usb_12, 12e6, margin=0)
            usb_pll.create_clkout(self.cd_usb_48, 48e6, margin=0)

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
    mem_map = {**SoCCore.mem_map, **{"spiflash": 0xd0000000}}
    def __init__(self, board="i5", revision="7.0", sys_clk_freq=60e6, with_ethernet=False,
                 with_etherbone=False, local_ip="", remote_ip="", eth_phy=0, with_led_chaser=True, 
                 use_internal_osc=False, sdram_rate="1:1", with_video_terminal=False,
                 with_video_framebuffer=False, **kwargs):
        board = board.lower()
        assert board in ["i5"]
        if board == "i5":
            platform = colorlight_i5.Platform(revision=revision)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, int(sys_clk_freq),
            ident          = "LiteX SoC on Colorlight " + board.upper(),
            ident_version  = True,
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        with_usb_pll = kwargs.get("uart_name", None) == "usb_acm"
        with_video_pll = with_video_terminal or with_video_framebuffer
        self.submodules.crg = _CRG(platform, sys_clk_freq, use_internal_osc=use_internal_osc, with_usb_pll=with_usb_pll, with_video_pll=with_video_pll, sdram_rate=sdram_rate)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            ledn = platform.request_all("user_led_n")
            self.submodules.leds = LedChaser(pads=ledn, sys_clk_freq=sys_clk_freq)

        # SPI Flash --------------------------------------------------------------------------------
        self.add_spi_flash(mode="1x", dummy_cycles=8)
        self.add_constant("SPIFLASH_PAGE_SIZE", 256)
        self.add_constant("SPIFLASH_SECTOR_SIZE", 4096)

        # SDR SDRAM --------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            sdrphy_cls = HalfRateGENSDRPHY if sdram_rate == "1:2" else GENSDRPHY
            self.submodules.sdrphy = sdrphy_cls(platform.request("sdram"))
            self.add_sdram("sdram",
                phy           = self.sdrphy,
                module        = M12L64322A(sys_clk_freq, sdram_rate),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            self.submodules.ethphy = LiteEthPHYRGMII(
                clock_pads = self.platform.request("eth_clocks", eth_phy),
                pads       = self.platform.request("eth", eth_phy),
                tx_delay = 0)
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy)
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy)

        if local_ip:
            local_ip = local_ip.split(".")
            self.add_constant("LOCALIP1", int(local_ip[0]))
            self.add_constant("LOCALIP2", int(local_ip[1]))
            self.add_constant("LOCALIP3", int(local_ip[2]))
            self.add_constant("LOCALIP4", int(local_ip[3]))

        if remote_ip:
            remote_ip = remote_ip.split(".")
            self.add_constant("REMOTEIP1", int(remote_ip[0]))
            self.add_constant("REMOTEIP2", int(remote_ip[1]))
            self.add_constant("REMOTEIP3", int(remote_ip[2]))
            self.add_constant("REMOTEIP4", int(remote_ip[3]))

        # Video ------------------------------------------------------------------------------------
        if with_video_terminal or with_video_framebuffer:
            self.submodules.videophy = VideoECP5HDMIPHY(platform.request("gpdi"), clock_domain="hdmi")
            if with_video_terminal:
                self.add_video_terminal(phy=self.videophy, timings="800x600@60Hz", clock_domain="hdmi")
            if with_video_framebuffer:
                self.add_video_framebuffer(phy=self.videophy, timings="800x600@60Hz", clock_domain="hdmi")

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on Colorlight i5")
    parser.add_argument("--build",            action="store_true",      help="Build bitstream")
    parser.add_argument("--load",             action="store_true",      help="Load bitstream")
    parser.add_argument("--board",            default="i5",         help="Board type: i5 (default)")
    parser.add_argument("--revision",         default="7.0", type=str,  help="Board revision: 7.0 (default)")
    parser.add_argument("--sys-clk-freq",     default=60e6,             help="System clock frequency (default: 60MHz)")
    ethopts = parser.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",   action="store_true",      help="Enable Ethernet support")
    ethopts.add_argument("--with-etherbone",  action="store_true",      help="Enable Etherbone support")
    parser.add_argument("--remote-ip",        default="192.168.1.100",  help="Remote IP address of TFTP server")
    parser.add_argument("--local-ip",         default="192.168.1.50",   help="Local IP address")
    sdopts = parser.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-sdcard",  action="store_true",	help="Enable SPI-mode SDCard support")
    sdopts.add_argument("--with-sdcard",      action="store_true",	help="Enable SDCard support")
    parser.add_argument("--eth-phy",          default=0, type=int,      help="Ethernet PHY: 0 (default) or 1")
    parser.add_argument("--use-internal-osc", action="store_true",      help="Use internal oscillator")
    parser.add_argument("--sdram-rate",       default="1:1",            help="SDRAM Rate: 1:1 Full Rate (default), 1:2 Half Rate")
    viopts = parser.add_mutually_exclusive_group()
    viopts.add_argument("--with-video-terminal",    action="store_true", help="Enable Video Terminal (HDMI)")
    viopts.add_argument("--with-video-framebuffer", action="store_true", help="Enable Video Framebuffer (HDMI)")
    builder_args(parser)
    soc_core_args(parser)
    trellis_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(board=args.board, revision=args.revision,
        sys_clk_freq           = int(float(args.sys_clk_freq)),
        with_ethernet          = args.with_ethernet,
        with_etherbone         = args.with_etherbone,
        local_ip               = args.local_ip,
        remote_ip              = args.remote_ip,
        eth_phy                = args.eth_phy,
        use_internal_osc       = args.use_internal_osc,
        sdram_rate             = args.sdram_rate,
        l2_size	               = args.l2_size,
        with_video_terminal    = args.with_video_terminal,
        with_video_framebuffer = args.with_video_framebuffer,
        **soc_core_argdict(args)
    )
    soc.platform.add_extension(colorlight_i5._sdcard_pmod_io)
    if args.with_spi_sdcard:
        soc.add_spi_sdcard()
    if args.with_sdcard:
        soc.add_sdcard()

    builder = Builder(soc, **builder_argdict(args))

    builder.build(**trellis_argdict(args), run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".bit"))

if __name__ == "__main__":
    main()
