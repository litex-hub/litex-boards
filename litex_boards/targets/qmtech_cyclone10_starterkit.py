#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 Denis Bodor <lefinnois@lefinnois.net>
# Copyright (c) 2021 Hans Baier <hansfbaier@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from litex.build.io import DDROutput

from litex_boards.platforms import qmtech_cyclone10_starterkit

from litex.soc.cores.clock import Cyclone10LPPLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litedram.modules import W9825G6KH6
from litedram.phy import GENSDRPHY, HalfRateGENSDRPHY

# RTL8211EG is RGMII/GMII - This is not compatible with Cyclone10 for now
#from liteeth.phy.mii import LiteEthPHYRGMII

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, sdram_rate="1:1"):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()

        if sdram_rate == "1:2":
            self.cd_sys2x    = ClockDomain()
            self.cd_sys2x_ps = ClockDomain()
        else:
            self.cd_sys_ps   = ClockDomain()

        # # #

        # Clk / Rst
        clk50 = platform.request("clk50")

        # PLL
        self.pll = pll = Cyclone10LPPLL(speedgrade="-C8")
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk50, 50e6)
        pll.create_clkout(self.cd_sys,    sys_clk_freq)
        if sdram_rate == "1:2":
            pll.create_clkout(self.cd_sys2x,    2*sys_clk_freq)
            # theoretically 90 degrees, but increase to relax timing
            pll.create_clkout(self.cd_sys2x_ps, 2*sys_clk_freq, phase=180)
        else:
            pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=90)

        # SDRAM clock
        sdram_clk = ClockSignal("sys2x_ps" if sdram_rate == "1:2" else "sys_ps")
        self.specials += DDROutput(1, 0, platform.request("sdram_clock"), sdram_clk)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=50e6,
        with_led_chaser = True,
        sdram_rate      = "1:1",
        **kwargs):
        platform = qmtech_cyclone10_starterkit.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, sdram_rate=sdram_rate)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on QMTECH Cyclone10 Starter Kit", **kwargs)

        # SDR SDRAM --------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            sdrphy_cls = HalfRateGENSDRPHY if sdram_rate == "1:2" else GENSDRPHY
            self.sdrphy = sdrphy_cls(platform.request("sdram"), sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.sdrphy,
                module        = W9825G6KH6(sys_clk_freq, sdram_rate),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

            seven_seg_display = platform.request("seven_seg_ctl")
            self.comb += seven_seg_display.dig.eq(0b111)
            self.leds7 = LedChaser(
                pads         = seven_seg_display.segments,
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=qmtech_cyclone10_starterkit.Platform, description="LiteX SoC on QMTECH Cyclone10 Starter Kit.")
    parser.add_target_argument("--sys-clk-freq",    default=50e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--sdram-rate",      default="1:2",            help="SDRAM Rate (1:1 Full Rate or 1:2 Half Rate).")
    sdopts = parser.target_group.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-sdcard",        action="store_true",      help="Enable SPI-mode SDCard support.")
    sdopts.add_argument("--with-sdcard",            action="store_true",      help="Enable SDCard support.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq = args.sys_clk_freq,
        sdram_rate   = args.sdram_rate,
        **parser.soc_argdict
    )

    if args.with_sdcard:
        soc.add_sdcard()
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
