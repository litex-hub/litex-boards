#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Hans Baier <hansfbaier@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.build.io import DDROutput

from litex_boards.platforms import qmtech_10cl006

from litex.soc.cores.clock import Cyclone10LPPLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litedram.modules import W9825G6KH6
from litedram.phy import GENSDRPHY, HalfRateGENSDRPHY

from litex.soc.cores.video import VideoVGAPHY
from liteeth.phy.mii import LiteEthPHYMII

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq, sdram_rate="1:1"):
        self.rst = Signal()
        self.clock_domains.cd_sys          = ClockDomain()

        if sdram_rate == "1:2":
            self.clock_domains.cd_sys2x    = ClockDomain()
            self.clock_domains.cd_sys2x_ps = ClockDomain()
        else:
            self.clock_domains.cd_sys_ps   = ClockDomain()

        # # #

        # Clk / Rst
        clk50 = platform.request("clk50")

        # PLL
        self.submodules.pll = pll = Cyclone10LPPLL(speedgrade="-C8")
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
    def __init__(self, sys_clk_freq=int(50e6), with_daughterboard=False,
                 with_ethernet=False, with_etherbone=False, eth_ip="192.168.1.50", eth_dynamic_ip=False,
                 with_led_chaser=True, with_video_terminal=False, with_video_framebuffer=False,
                 sdram_rate="1:1", **kwargs):
        platform = qmtech_10cl006.Platform(with_daughterboard=with_daughterboard)

        # unfornunately not even SERV would fit the devices
        kwargs["cpu_type"]  = None
        kwargs["integrated_sram_size"]  = 0

        # interact with the sdram with uartbone by default
        kwargs["uart_name"] = "uartbone"

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident = "LiteX SoC on QMTECH 10CL006" + (" + Daughterboard" if with_daughterboard else ""),
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq, sdram_rate=sdram_rate)

        # SDR SDRAM --------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            sdrphy_cls = HalfRateGENSDRPHY if sdram_rate == "1:2" else GENSDRPHY
            self.submodules.sdrphy = sdrphy_cls(platform.request("sdram"), sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.sdrphy,
                module        = W9825G6KH6(sys_clk_freq, sdram_rate),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on QMTECH 10CL006")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",               action="store_true", help="Build bitstream.")
    target_group.add_argument("--load",                action="store_true", help="Load bitstream.")
    target_group.add_argument("--sys-clk-freq",        default=50e6,        help="System clock frequency.")
    target_group.add_argument("--sdram-rate",          default="1:2",       help="SDRAM Rate (1:1 Full Rate or 1:2 Half Rate).")
    target_group.add_argument("--with-daughterboard",  action="store_true", help="Board plugged into the QMTech daughterboard.")
    sdopts = target_group.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-sdcard",     action="store_true", help="Enable SPI-mode SDCard support.")
    sdopts.add_argument("--with-sdcard",         action="store_true", help="Enable SDCard support.")
    target_group.add_argument("--with-spi-flash",      action="store_true", help="Enable SPI Flash (MMAPed).")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq = int(float(args.sys_clk_freq)),
        with_daughterboard     = args.with_daughterboard,
        with_spi_flash         = args.with_spi_flash,
        sdram_rate             = args.sdram_rate,
        **soc_core_argdict(args)
    )

    if args.with_spi_sdcard:
        soc.add_spi_sdcard()
    if args.with_sdcard:
        soc.add_sdcard()

    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
