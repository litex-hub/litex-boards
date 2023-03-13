#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Icenowy Zheng <icenowy@aosc.io>
# Copyright (c) 2022 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from litex.build.io import DDROutput

from litex.soc.cores.clock.gowin_gw2a import GW2APLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.gpio import GPIOIn
from litex.soc.cores.led import LedChaser, WS2812

from litex_boards.platforms import sipeed_tang_nano_20k

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst      = Signal()
        self.cd_sys   = ClockDomain()
        self.cd_por   = ClockDomain()

        # Clk
        clk27 = platform.request("clk27")

        # Power on reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += self.cd_por.clk.eq(clk27)
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # PLL
        self.pll = pll = GW2APLL(devicename=platform.devicename, device=platform.device)
        self.comb += pll.reset.eq(~por_done)
        pll.register_clkin(clk27, 27e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=48e6,
        with_led_chaser     = True,
        with_rgb_led        = False,
        with_buttons        = True,
        **kwargs):

        platform = sipeed_tang_nano_20k.Platform(toolchain="gowin")

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Tang Nano 20K", **kwargs)

        # TODO: XTX SPI Flash

        # TODO: copackaged SDRAM

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("led_n"),
                sys_clk_freq = sys_clk_freq
            )

        # RGB Led ----------------------------------------------------------------------------------
        if with_rgb_led:
            self.rgb_led = WS2812(
                pad          = platform.request("rgb_led"),
                nleds        = 1,
                sys_clk_freq = sys_clk_freq
            )
            self.bus.add_slave(name="rgb_led", slave=self.rgb_led.bus, region=SoCRegion(
                origin = 0x2000_0000,
                size   = 4,
            ))

        # Buttons ----------------------------------------------------------------------------------
        if with_buttons:
            self.buttons = GPIOIn(pads=~platform.request_all("btn"))


# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=sipeed_tang_nano_20k.Platform, description="LiteX SoC on Tang Primer 20K.")
    parser.add_target_argument("--flash",        action="store_true",      help="Flash Bitstream.")
    parser.add_target_argument("--sys-clk-freq", default=48e6, type=float, help="System clock frequency.")
    sdopts = parser.target_group.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-sdcard",            action="store_true", help="Enable SPI-mode SDCard support.")
    sdopts.add_argument("--with-sdcard",                action="store_true", help="Enable SDCard support.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq        = args.sys_clk_freq,
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

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.flash(0, builder.get_bitstream_filename(mode="flash", ext=".fs"), external=True)

if __name__ == "__main__":
    main()
