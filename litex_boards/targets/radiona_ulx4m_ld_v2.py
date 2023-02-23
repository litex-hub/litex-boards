#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Goran Mahovlic <goran.mahovlic@gmail.com>
# Copyright (c) 2021 Greg Davill <greg.davill@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

# Build/Use:
# ./radiona_ulx4m_ld_v3.py  --uart-name=uart --uart-baudrate=115200 --sdram-device MT41K64M16 --csr-csv=csr.csv --build

import os
import sys
import argparse

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *
from litex_boards.platforms import radiona_ulx4m_ld_v2

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.gpio import GPIOTristate
from litex.soc.cores.video import VideoHDMIPHY

from litedram.common import PHYPadsReducer
from litedram.modules import MT41K64M16,MT41K128M16,MT41K256M16,MT41K512M16
from litedram.phy import ECP5DDRPHY

from liteeth.phy.ecp5rgmii import LiteEthPHYRGMII

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_video_pll=True):
        self.rst = Signal()
        self.cd_init    = ClockDomain()
        self.cd_por     = ClockDomain(reset_less=True)
        self.cd_sys     = ClockDomain()
        self.cd_sys2x   = ClockDomain()
        self.cd_sys2x_i = ClockDomain(reset_less=True)

        # # #

        self.stop  = Signal()
        self.reset = Signal()

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
        pll.create_clkout(self.cd_sys2x_i, 2*sys_clk_freq)
        pll.create_clkout(self.cd_init,   25e6)
        self.specials += [
            Instance("ECLKSYNCB",
                i_ECLKI = self.cd_sys2x_i.clk,
                i_STOP  = self.stop,
                o_ECLKO = self.cd_sys2x.clk),
            Instance("CLKDIVF",
                p_DIV     = "1.0",
                i_ALIGNWD = 0,
                i_CLKI    = self.cd_sys2x.clk,
                i_RST     = self.reset,
                o_CDIVX   = self.cd_sys.clk),
            AsyncResetSynchronizer(self.cd_sys,    ~pll.locked | self.reset),
            AsyncResetSynchronizer(self.cd_sys2x,  ~pll.locked | self.reset),
        ]

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, revision="0.1", device="85F", toolchain="trellis", sys_clk_freq=int(100e6),
        sdram_device           = "MT41K512M16",
        with_ethernet          = False,
        with_etherbone         = False,
        with_video_terminal    = True,
        with_video_framebuffer = False,
        eth_ip                 = "192.168.1.50",
        eth_dynamic_ip         = False,
        with_spi_flash         = False,
        with_led_chaser        = True,
        with_syzygy_gpio       = False,
        **kwargs)       :
        platform = radiona_ulx4m_ld_v2.Platform(revision="0.1", device=device ,toolchain=toolchain)

        # CRG --------------------------------------------------------------------------------------
        with_video_pll = with_video_terminal or with_video_framebuffer
        self.submodules.crg = _CRG(platform, sys_clk_freq, with_video_pll)

        # SoCCore ----------------------------------------------------------------------------------
        if kwargs["uart_name"] in ["serial", "usb_acm"]:
            kwargs["uart_name"] = "serial"
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on ULX4M-LD-V2", **kwargs)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            available_sdram_modules = {
                "MT41K64M16":  MT41K64M16,
                "MT41K128M16": MT41K128M16,
                "MT41K256M16": MT41K256M16,
                "MT41K512M16": MT41K256M16,
            }
            sdram_module = available_sdram_modules.get(sdram_device)

            self.submodules.ddrphy = ECP5DDRPHY(
                pads = PHYPadsReducer(platform.request("ddram"), [0, 1]),
                sys_clk_freq=sys_clk_freq)
            self.comb += self.crg.stop.eq(self.ddrphy.init.stop)
            self.comb += self.crg.reset.eq(self.ddrphy.init.reset)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = sdram_module(sys_clk_freq, "1:4"),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            self.submodules.ethphy = LiteEthPHYRGMII(
                clock_pads = self.platform.request("eth_clocks"),
                pads       = self.platform.request("eth"))
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy, dynamic_ip=eth_dynamic_ip)
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


        # GPIOs ------------------------------------------------------------------------------------
        if with_syzygy_gpio:
            platform.add_extension(ulx4m_ld_v2.raw_syzygy_io("SYZYGY0"))
            self.submodules.gpio = GPIOTristate(platform.request("SYZYGY0"))

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=radiona_ulx4m_ld_v2.Platform, description="LiteX SoC on ULX4M-LD-V2")
    parser.add_argument("--sys-clk-freq",    default=100e6,          help="System clock frequency.")
    parser.add_argument("--revision",        default="1.0",          help="Board Revision (1.0).")
    parser.add_argument("--device",          default="85F",          help="ECP5 device (25F, 45F, 85F).")
    parser.add_argument("--sdram-device",    default="MT41K512M16",  help="SDRAM device (MT41K64M16, MT41K128M16, MT41K256M16 or MT41K512M16).")
    ethopts = parser.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",  action="store_true",    help="Add Ethernet.")
    ethopts.add_argument("--with-etherbone", action="store_true",    help="Add EtherBone.")
    parser.add_argument("--eth-ip",          default="192.168.1.50", help="Ethernet/Etherbone IP address.")
    parser.add_argument("--eth-dynamic-ip",  action="store_true",    help="Enable dynamic Ethernet IP addresses setting.")
    parser.add_argument("--with-spi-flash",  action="store_true",    help="Enable SPI Flash (MMAPed).")
    sdopts = parser.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-sdcard", action="store_true", help="Enable SPI-mode SDCard support.")
    sdopts.add_argument("--with-sdcard",     action="store_true", help="Enable SDCard support.")
    parser.add_argument("--with-syzygy-gpio",action="store_true", help="Enable GPIOs through SYZYGY Breakout on Port-A.")
    viopts = parser.add_mutually_exclusive_group()
    viopts.add_argument("--with-video-terminal",    action="store_true", help="Enable Video Terminal (HDMI).")
    viopts.add_argument("--with-video-framebuffer", action="store_true", help="Enable Video Framebuffer (HDMI).")
    args = parser.parse_args()

    assert not (args.with_etherbone and args.eth_dynamic_ip)

    soc = BaseSoC(
        toolchain              = args.toolchain,
        revision               = args.revision,
        device                 = args.device,
        sdram_device           = args.sdram_device,
        sys_clk_freq           = int(float(args.sys_clk_freq)),
        with_ethernet          = args.with_ethernet,
        with_etherbone         = args.with_etherbone,
        eth_ip                 = args.eth_ip,
        eth_dynamic_ip         = args.eth_dynamic_ip,
        with_spi_flash         = args.with_spi_flash,
        with_video_terminal    = args.with_video_terminal,
        with_video_framebuffer = args.with_video_framebuffer,
        with_syzygy_gpio       = args.with_syzygy_gpio,
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
