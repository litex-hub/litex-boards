#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Hans Baier <hansfbaier@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

# https://www.aliexpress.com/item/1000006630084.html

from migen import *

from litex.gen import *

from litex_boards.platforms import qmtech_xc7a35t

from litex.soc.cores.clock import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.video import VideoVGAPHY
from litex.soc.cores.led import LedChaser

from litedram.modules import MT41J128M16
from litedram.phy import s7ddrphy

from liteeth.phy.mii import LiteEthPHYMII

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_ethernet, with_vga):
        self.rst          = Signal()
        self.cd_sys       = ClockDomain()
        self.cd_sys4x     = ClockDomain()
        self.cd_sys4x_dqs = ClockDomain()
        self.cd_idelay    = ClockDomain()
        self.cd_eth       = ClockDomain()
        if with_ethernet:
            self.cd_eth   = ClockDomain()
        if with_vga:
            self.cd_vga   = ClockDomain()

        # # #

        self.pll = pll = S7PLL(speedgrade=-1)
        try:
            reset_button = platform.request("cpu_reset")
            self.comb += pll.reset.eq(~reset_button | self.rst)
        except:
            self.comb += pll.reset.eq(self.rst)

        pll.register_clkin(platform.request("clk50"), 50e6)
        pll.create_clkout(self.cd_sys,       sys_clk_freq)
        pll.create_clkout(self.cd_sys4x,     4*sys_clk_freq)
        pll.create_clkout(self.cd_sys4x_dqs, 4*sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_idelay,    200e6)
        if with_ethernet:
            pll.create_clkout(self.cd_eth,   25e6)
        if with_vga:
            pll.create_clkout(self.cd_vga,   40e6)

        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        self.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, toolchain="vivado", sys_clk_freq=100e6, with_daughterboard=False,
        with_ethernet          = False,
        with_etherbone         = False,
        eth_ip                 = "192.168.1.50",
        eth_dynamic_ip         = False,
        with_led_chaser        = True,
        with_video_terminal    = False,
        with_video_framebuffer = False,
        with_jtagbone          = True,
        with_spi_flash         = False,
        **kwargs):
        platform = qmtech_xc7a35t.Platform(toolchain=toolchain, with_daughterboard=with_daughterboard)

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq,
            with_ethernet = (with_ethernet or with_etherbone),
            with_vga      = (with_video_terminal or with_video_framebuffer)
        )

        # SoCCore ----------------------------------------------------------------------------------
        if (kwargs["uart_name"] == "serial") and (not with_daughterboard):
            kwargs["uart_name"] = "gpio_serial"
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident = "LiteX SoC on QMTech XC7A35T" + (" + Daughterboard" if with_daughterboard else ""),
            **kwargs)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.ddrphy = s7ddrphy.A7DDRPHY(platform.request("ddram"),
                memtype        = "DDR3",
                nphases        = 4,
                sys_clk_freq   = sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT41J128M16(sys_clk_freq, "1:4"),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            self.ethphy = LiteEthPHYMII(
                clock_pads = self.platform.request("eth_clocks"),
                pads       = self.platform.request("eth"))
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy, dynamic_ip=eth_dynamic_ip)
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, ip_address=eth_ip)
            # The daughterboard has the tx clock wired to a non-clock pin, so we can't help it
            self.platform.add_platform_command("set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets eth_clocks_tx_IBUF]")

        # Jtagbone ---------------------------------------------------------------------------------
        if with_jtagbone:
            self.add_jtagbone()

        # SPI Flash --------------------------------------------------------------------------------
        if with_spi_flash:
            from litespi.modules import MT25QL128
            from litespi.opcodes import SpiNorFlashOpCodes as Codes
            self.add_spi_flash(mode="4x", module=MT25QL128(Codes.READ_1_1_1), with_master=True)

        # Video ------------------------------------------------------------------------------------
        if with_video_terminal or with_video_framebuffer:
            self.videophy = VideoVGAPHY(platform.request("vga"), clock_domain="vga")
            if with_video_terminal:
                self.add_video_terminal(phy=self.videophy, timings="800x600@60Hz", clock_domain="vga")
            if with_video_framebuffer:
                self.add_video_framebuffer(phy=self.videophy, timings="800x600@60Hz", clock_domain="vga")

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

        if not with_daughterboard and kwargs["uart_name"] == "serial":
            kwargs["uart_name"] = "jtag_serial"

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=qmtech_xc7a35t.Platform, description="LiteX SoC on QMTech XC7A35T.")
    parser.add_target_argument("--sys-clk-freq",        default=100e6, type=float,  help="System clock frequency.")
    parser.add_target_argument("--with-daughterboard",  action="store_true",        help="Board plugged into the QMTech daughterboard.")
    ethopts = parser.target_group.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",        action="store_true",    help="Enable Ethernet support.")
    ethopts.add_argument("--with-etherbone",       action="store_true",    help="Enable Etherbone support.")
    parser.add_target_argument("--eth-ip",         default="192.168.1.50", help="Ethernet/Etherbone IP address.")
    parser.add_target_argument("--eth-dynamic-ip", action="store_true",    help="Enable dynamic Ethernet IP addresses setting.")
    sdopts = parser.target_group.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-sdcard",       action="store_true", help="Enable SPI-mode SDCard support.")
    sdopts.add_argument("--with-sdcard",           action="store_true", help="Enable SDCard support.")
    parser.add_target_argument("--with-jtagbone",  action="store_true", help="Enable Jtagbone support.")
    parser.add_target_argument("--with-spi-flash", action="store_true", help="Enable SPI Flash (MMAPed).")
    viopts = parser.target_group.add_mutually_exclusive_group()
    viopts.add_argument("--with-video-terminal",    action="store_true", help="Enable Video Terminal (VGA).")
    viopts.add_argument("--with-video-framebuffer", action="store_true", help="Enable Video Framebuffer (VGA).")
    args = parser.parse_args()

    soc = BaseSoC(
        toolchain              = args.toolchain,
        sys_clk_freq           = args.sys_clk_freq,
        with_daughterboard     = args.with_daughterboard,
        with_ethernet          = args.with_ethernet,
        with_etherbone         = args.with_etherbone,
        eth_ip                 = args.eth_ip,
        eth_dynamic_ip         = args.eth_dynamic_ip,
        with_jtagbone          = args.with_jtagbone,
        with_spi_flash         = args.with_spi_flash,
        with_video_terminal    = args.with_video_terminal,
        with_video_framebuffer = args.with_video_framebuffer,
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
