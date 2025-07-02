#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 Miodrag Milanovic <mmicko@gmail.com>
#
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import *

from litex_boards.platforms import machdyne_kolsch

from litex.soc.cores.clock.colognechip import GateMatePLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.build.io import DDROutput
from litex.build.generic_platform import Pins

from litex.soc.cores.led import LedChaser
from litex.soc.cores.video import VideoVGAPHY

from litedram.modules import W989D6DBGX6

from litedram.phy import GENSDRPHY

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_video_terminal):
        self.rst        = Signal()
        rst_n           = Signal()
        self.cd_sys     = ClockDomain()
        self.cd_sys_ps  = ClockDomain()
        if with_video_terminal:
            self.cd_vga = ClockDomain()

        # Clk / Rst
        clk48 = platform.request("clk48")

        self.specials += Instance("CC_USR_RSTN", o_USR_RSTN = rst_n)

        # PLL
        self.pll = pll = GateMatePLL(perf_mode="economy")
        self.comb += pll.reset.eq(~rst_n)
        pll.register_clkin(clk48, 48e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=90)
        platform.add_period_constraint(self.cd_sys.clk, 1e9/sys_clk_freq)
        self.specials += DDROutput(1, 0, platform.request("sdram_clock"), ClockSignal("sys_ps"))

        if with_video_terminal:
            self.pll_video = pll_video = GateMatePLL(perf_mode="economy")
            self.comb += pll_video.reset.eq(~rst_n)
            pll_video.register_clkin(clk48, 48e6)
            pll_video.create_clkout(self.cd_vga, 65e6)
            platform.add_period_constraint(self.cd_vga.clk, 1e9/65e6)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=24e6, toolchain="colognechip",
        with_video_terminal = False,
        with_ethernet       = False,
        with_etherbone      = False,
        eth_ip              = "192.168.1.50",
        remote_ip           = None,
        with_led_chaser     = True,
        **kwargs):
        platform = machdyne_kolsch.Platform(toolchain)

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, with_video_terminal)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Kolsch", **kwargs)

        # Video Terminal ---------------------------------------------------------------------------
        if with_video_terminal:
            vga_pads = platform.request("vga")
            self.videophy = VideoVGAPHY(vga_pads, clock_domain="vga")
            self.add_video_terminal(phy=self.videophy, timings="1024x768@60Hz", clock_domain="vga")

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led_n"),
                sys_clk_freq = sys_clk_freq)

        # DRAM -------------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.sdrphy = GENSDRPHY(platform.request("sdram"), sys_clk_freq)

            self.add_sdram("sdram",
                phy           = self.sdrphy,
                module        = W989D6DBGX6(sys_clk_freq, "1:1"),
                l2_cache_size = kwargs.get("l2_size", 0)
            )

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            from litex.build.generic_platform import Subsignal
            def eth_lan8720_rmii_pmod_io(pmod):
                # Lan8720 RMII PHY "PMOD": To be used as a PMOD, MDIO should be disconnected and TX1 connected to PMOD8 IO.
                return [
                    ("eth_rmii_clocks", 0,
                        Subsignal("ref_clk", Pins(f"{pmod}:6")),
                    ),
                    ("eth_rmii", 0,
                        Subsignal("rx_data", Pins(f"{pmod}:5 {pmod}:1")),
                        Subsignal("crs_dv",  Pins(f"{pmod}:2")),
                        Subsignal("tx_en",   Pins(f"{pmod}:4")),
                        Subsignal("tx_data", Pins(f"{pmod}:0 {pmod}:7")),
                    ),
                ]
            platform.add_extension(eth_lan8720_rmii_pmod_io("PMOD"))

            from liteeth.phy.rmii import LiteEthPHYRMII
            self.ethphy = LiteEthPHYRMII(
                clock_pads = platform.request("eth_rmii_clocks"),
                pads       = platform.request("eth_rmii"),
                refclk_cd  = None
            )

        if with_ethernet:
            self.add_ethernet(phy=self.ethphy, local_ip=eth_ip, remote_ip=remote_ip, software_debug=False)
        if with_etherbone:
            self.add_etherbone(phy=self.ethphy, ip_address=eth_ip)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=machdyne_kolsch.Platform, description="LiteX SoC on Kolsch")
    parser.add_target_argument("--sys-clk-freq",        default=24e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-video-terminal", action="store_true",      help="Enable Video Terminal (VGA).")
    parser.add_target_argument("--flash",               action="store_true",      help="Flash bitstream.")
    parser.add_target_argument("--with-spi-sdcard",     action="store_true",      help="Enable SPI-mode SDCard support.")
    pmodopts = parser.target_group.add_mutually_exclusive_group()
    pmodopts.add_argument("--with-ethernet",            action="store_true",      help="Enable Ethernet support.")
    pmodopts.add_argument("--with-etherbone",           action="store_true",      help="Enable Etherbone support.")
    parser.add_target_argument("--eth-ip",              default="192.168.1.50",   help="Ethernet/Etherbone IP address.")
    parser.add_target_argument("--remote-ip",           default="192.168.1.100",  help="Remote IP address of TFTP server.")

    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq        = args.sys_clk_freq,
        toolchain           = args.toolchain,
        with_video_terminal = args.with_video_terminal,
        with_ethernet       = args.with_ethernet,
        with_etherbone      = args.with_etherbone,
        eth_ip              = args.eth_ip,
        remote_ip           = args.remote_ip,
        **parser.soc_argdict)

    if args.with_spi_sdcard:
        soc.add_spi_sdcard()

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
