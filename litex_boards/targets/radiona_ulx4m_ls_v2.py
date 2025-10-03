#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 Gwenhael Goavec-Merou <gwenhael.goavec-merou@trabucayre.com>
# Copyright (c) 2022 Goran Mahovlic <goran.mahovlic@gmail.com>
# Copyright (c) 2021 Greg Davill <greg.davill@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

import os
import sys
import argparse

from migen import *

from litex.build.io import DDROutput

from litex.gen import *

from litex_boards.platforms import radiona_ulx4m_ls_v2

from litex.soc.cores.clock import *

from litex.soc.integration.soc_core import *
from litex.soc.integration.builder  import *

from litex.soc.cores.led   import LedChaser
from litex.soc.cores.video import VideoHDMIPHY

from litedram     import modules as litedram_modules
from litedram.phy import GENSDRPHY, HalfRateGENSDRPHY

from liteeth.phy.rmii import LiteEthPHYRMII

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq,
        with_video_pll = True,
        sdram_rate     = "1:1",
        with_usb_pll   = False,
        with_eth       = False,
        ):

        self.rst    = Signal()
        self.cd_por = ClockDomain(reset_less=True)
        self.cd_sys = ClockDomain()

        if with_eth:
            self.cd_eth = ClockDomain()

        if sdram_rate == "1:2":
            self.cd_sys2x    = ClockDomain()
            self.cd_sys2x_ps = ClockDomain()
        else:
            self.cd_sys_ps = ClockDomain()

        # # #

        # Clk / Rst
        clk25 = platform.request("clk25")
        rst_n = platform.request("rst_n", 0)

        # Power on reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += self.cd_por.clk.eq(clk25)
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # Video PLL
        if with_video_pll:
            self.video_pll = video_pll = ECP5PLL()
            self.comb += video_pll.reset.eq(rst_n | self.rst)
            video_pll.register_clkin(clk25, 25e6)
            self.cd_hdmi   = ClockDomain()
            self.cd_hdmi5x = ClockDomain()
            video_pll.create_clkout(self.cd_hdmi,    25e6, margin=0)
            video_pll.create_clkout(self.cd_hdmi5x, 125e6, margin=0)

        # PLL
        self.pll = pll = ECP5PLL()
        self.comb += pll.reset.eq(~por_done | rst_n | self.rst)
        pll.register_clkin(clk25, 25e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        if sdram_rate == "1:2":
            pll.create_clkout(self.cd_sys2x,    2*sys_clk_freq)
            pll.create_clkout(self.cd_sys2x_ps, 2*sys_clk_freq, phase=180) # Idealy 90° but needs to be increased.
        else:
            pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=180) # Idealy 90° but needs to be increased.

        # Eth clock (25MHz because LAN8720A is in REF_CLK Out Mode)
        if with_eth:
            pll.create_clkout(self.cd_eth, 25e6)
            self.comb += platform.request("eth_phy_clk").eq(self.cd_eth.clk)

        # SDRAM clock
        sdram_clk = ClockSignal("sys2x_ps" if sdram_rate == "1:2" else "sys_ps")
        self.specials += DDROutput(1, 0, platform.request("sdram_clock"), sdram_clk)

        # USB PLL
        if with_usb_pll:
            self.usb_pll = usb_pll = ECP5PLL()
            self.comb += usb_pll.reset.eq(~rst_n | self.rst)
            usb_pll.register_clkin(clk25, 25e6)
            self.cd_usb_12 = ClockDomain()
            self.cd_usb_48 = ClockDomain()
            usb_pll.create_clkout(self.cd_usb_12, 12e6, margin=0)
            usb_pll.create_clkout(self.cd_usb_48, 48e6, margin=0)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, revision="0.1", device="85F", toolchain="trellis", sys_clk_freq=int(50e6),
        sdram_module_cls       = "IS42S16160",
        sdram_rate             = "1:1",
        with_ethernet          = False,
        with_etherbone         = False,
        with_video_terminal    = False,
        with_video_framebuffer = False,
        eth_ip                 = "192.168.1.50",
        remote_ip              = "192.168.1.100",
        eth_dynamic_ip         = False,
        with_spi_flash         = False,
        with_led_chaser        = True,
        **kwargs)       :
        platform = radiona_ulx4m_ls_v2.Platform(revision="0.1", device=device ,toolchain=toolchain)

        # CRG --------------------------------------------------------------------------------------
        with_usb_pll = kwargs["uart_name"] in ["usb_acm"]
        with_video_pll = with_video_terminal or with_video_framebuffer
        self.submodules.crg = _CRG(platform, sys_clk_freq,
            with_video_pll = with_video_pll,
            sdram_rate     = sdram_rate,
            with_usb_pll   = with_usb_pll,
            with_eth       = with_etherbone or with_ethernet,
        )

        # SoCCore ----------------------------------------------------------------------------------
        if kwargs["uart_name"] in ["serial", "usb_acm"]:
            kwargs["uart_name"] = "serial"
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on ULX4M-LS-V2", **kwargs)

        # SDR SDRAM --------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            sdrphy_cls = HalfRateGENSDRPHY if sdram_rate == "1:2" else GENSDRPHY
            self.sdrphy = sdrphy_cls(platform.request("sdram"), sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.sdrphy,
                module        = getattr(litedram_modules, sdram_module_cls)(sys_clk_freq, sdram_rate),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            self.ethphy = LiteEthPHYRMII(
                clock_pads = self.platform.request("eth_clocks"),
                pads       = self.platform.request("eth"),
                refclk_cd  = None,
            )
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy, dynamic_ip=eth_dynamic_ip, local_ip=eth_ip, remote_ip=remote_ip)
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, ip_address=eth_ip)

        # SPI Flash --------------------------------------------------------------------------------
        if with_spi_flash:
            from litespi.modules import IS25LP128
            from litespi.opcodes import SpiNorFlashOpCodes as Codes
            self.add_spi_flash(mode="4x", module=IS25LP128(Codes.READ_1_1_4))

        # Video ------------------------------------------------------------------------------------
        if with_video_terminal or with_video_framebuffer:
            self.submodules.videophy = VideoHDMIPHY(platform.request("gpdi"), clock_domain="hdmi")
            if with_video_terminal:
                self.add_video_terminal(phy=self.videophy, timings="640x480@75Hz", clock_domain="hdmi")
            if with_video_framebuffer:
                self.add_video_framebuffer(phy=self.videophy, timings="640x480@75Hz", clock_domain="hdmi")

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=radiona_ulx4m_ls_v2.Platform, description="LiteX SoC on ULX4M-LS-V2")
    parser.add_argument("--sys-clk-freq",    default=50e6,           help="System clock frequency.")
    parser.add_argument("--revision",        default="1.0",          help="Board Revision (1.0).")
    parser.add_argument("--device",          default="12F",          help="ECP5 device (25F, 45F, 85F).")

    # SDRAM.
    parser.add_argument("--sdram-device",    default="IS42S16160",   help="SDRAM device (IS42S16320).")
    parser.add_argument("--sdram-rate",      default="1:1",          help="SDRAM Rate (1:1 Full Rate or 1:2 Half Rate).")

    # Ethernet.
    ethopts = parser.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",  action="store_true",     help="Add Ethernet.")
    ethopts.add_argument("--with-etherbone", action="store_true",     help="Add EtherBone.")
    parser.add_argument("--eth-ip",          default="192.168.1.50",  help="Ethernet/Etherbone IP address.")
    parser.add_argument("--eth-dynamic-ip",  action="store_true",     help="Enable dynamic Ethernet IP addresses setting.")
    parser.add_argument("--remote-ip",       default="192.168.1.100", help="Remote IP address of TFTP server.")
    parser.add_argument("--with-spi-flash",  action="store_true",     help="Enable SPI Flash (MMAPed).")

    # SDCard.
    sdopts = parser.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-sdcard", action="store_true", help="Enable SPI-mode SDCard support.")
    sdopts.add_argument("--with-sdcard",     action="store_true", help="Enable SDCard support.")

    # Video.
    viopts = parser.add_mutually_exclusive_group()
    viopts.add_argument("--with-video-terminal",    action="store_true", help="Enable Video Terminal (HDMI).")
    viopts.add_argument("--with-video-framebuffer", action="store_true", help="Enable Video Framebuffer (HDMI).")
    args = parser.parse_args()

    assert not (args.with_etherbone and args.eth_dynamic_ip)

    # Hack: 12F and 25F have same die
    # when device == 12F_25F the gateware is built for
    # a 25F but the bitstream IDCODE is overwritten for a 12F
    if args.device == "12F_25F":
        soc_device          = "25F"
        args.ecppack_idcode = "0x21111043"
    else:
        soc_device          = args.device

    soc = BaseSoC(
        toolchain              = args.toolchain,
        revision               = args.revision,
        device                 = soc_device,
        sdram_module_cls       = args.sdram_device,
        sdram_rate             = args.sdram_rate,
        sys_clk_freq           = int(float(args.sys_clk_freq)),
        with_ethernet          = args.with_ethernet,
        with_etherbone         = args.with_etherbone,
        eth_ip                 = args.eth_ip,
        remote_ip              = args.remote_ip,
        eth_dynamic_ip         = args.eth_dynamic_ip,
        with_spi_flash         = args.with_spi_flash,
        with_video_terminal    = args.with_video_terminal,
        with_video_framebuffer = args.with_video_framebuffer,
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
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
