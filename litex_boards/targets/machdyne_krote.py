#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2021 Omkar Bhilare <ombhilare999@gmail.com>
# Copyright (c) 2021 Michael Welling <mwelling@ieee.org>
# Copyright (c) 2022 Lone Dynamics Corporation <info@lonedynamics.com>
#
# SPDX-License-Identifier: BSD-2-Clause
#
# Krote FPGA board: https://github.com/machdyne/krote
#
# TODO:
# - add support for QQSPI PSRAM (32MB) pmod
# - add support for SD card pmod 
#

import os
import sys

from migen import *

from litex.gen import *

from litex.build.io import CRG

from litex_boards.platforms import machdyne_krote

from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.clock import iCE40PLL
from litex.soc.cores.led import LedChaser

from migen.genlib.resetsync import AsyncResetSynchronizer

kB = 1024
mB = 1024*kB


# _CRG ---------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()
        self.cd_por = ClockDomain(reset_less=True)

        # Clk/Rst
        clk100 = platform.request("clk100")
        platform.add_period_constraint(clk100, 1e9/100e6)

        # Power On Reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += self.cd_por.clk.eq(clk100)
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # Sys Clk
        self.pll = pll = iCE40PLL()
        pll.register_clkin(clk100, 100e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq, with_reset=False)
        self.specials += AsyncResetSynchronizer(self.cd_sys, ~por_done | ~pll.locked)
        platform.add_period_constraint(self.cd_sys.clk, 1e9/sys_clk_freq)



# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    mem_map = {**SoCCore.mem_map, **{"spiflash": 0x20000000}}
    def __init__(self, bios_flash_offset, sys_clk_freq=100e6, with_led_chaser=True, **kwargs):
        platform = machdyne_krote.Platform()

        # Disable Integrated ROM since too large for iCE40.
        kwargs["integrated_rom_size"]  = 0
        kwargs["integrated_sram_size"]  = 4*kB

        # Set CPU variant / reset address
        kwargs["cpu_reset_address"] = self.mem_map["spiflash"] + bios_flash_offset

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident          = "LiteX SoC on Kr\xf6te",
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SPI Flash --------------------------------------------------------------------------------
        from litespi.modules import W25Q32
        from litespi.opcodes import SpiNorFlashOpCodes as Codes
        self.add_spi_flash(mode="1x", module=W25Q32(Codes.READ_1_1_1), with_master=False)

        # Add ROM linker region --------------------------------------------------------------------
        self.bus.add_region("rom", SoCRegion(
            origin = self.mem_map["spiflash"] + bios_flash_offset,
            size   = 32*kB,
            linker = True)
        )

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=machdyne_krote.Platform, description="LiteX SoC on Kr\xf6te.")
    parser.add_argument("--bios-flash-offset", default="0x021000",       help="BIOS offset in SPI Flash (default: 0x21000)")
    parser.add_argument("--sys-clk-freq",      default=50e6, type=float, help="System clock frequency (default: 50MHz)")
    parser.add_argument("--with-led-chaser", action="store_true",        help="Enable LED Chaser.")
    args = parser.parse_args()

    soc = BaseSoC(
         bios_flash_offset = int(args.bios_flash_offset, 0),
         sys_clk_freq      = args.sys_clk_freq,
         **parser.soc_argdict
    )
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

if __name__ == "__main__":
    main()
