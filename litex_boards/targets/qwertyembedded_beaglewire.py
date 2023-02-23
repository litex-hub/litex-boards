#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
# Copyright (c) 2021 Omkar Bhilare <ombhilare999@gmail.com>
# Copyright (c) 2021 Michael Welling <mwelling@ieee.org>
# SPDX-License-Identifier: BSD-2-Clause

import os

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from litex_boards.platforms import qwertyembedded_beaglewire

from litex.build.io import DDROutput

from litex.soc.cores.clock import iCE40PLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.uart import UARTWishboneBridge

from litedram.phy import GENSDRPHY
from litedram.modules import MT48LC32M8

kB = 1024
mB = 1024*kB

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()
        self.cd_por = ClockDomain()

        # # #

        # Clk/Rst
        clk100 = platform.request("clk100")
        rst_n  = platform.request("user_btn_n")

        # Power On Reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += self.cd_por.clk.eq(ClockSignal())
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # PLL
        self.pll = pll = iCE40PLL()
        self.comb += pll.reset.eq(rst_n) # FIXME: Add proper iCE40PLL reset support and add back | self.rst.
        pll.register_clkin(clk100, 100e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq, with_reset=False)
        self.specials += AsyncResetSynchronizer(self.cd_sys, ~por_done | ~pll.locked)
        platform.add_period_constraint(self.cd_sys.clk, 1e9/sys_clk_freq)

        # SDRAM clock
        self.specials += DDROutput(0, 1, platform.request("sdram_clock"),  ClockSignal("sys"))

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, bios_flash_offset, sys_clk_freq=50e6, **kwargs):
        platform = qwertyembedded_beaglewire.Platform()

        # Disable Integrated ROM since too large for iCE40.
        kwargs["integrated_rom_size"]  = 0
        kwargs["integrated_sram_size"] = 2*kB

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Beaglewire", **kwargs)

        # SDR SDRAM --------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.sdrphy = GENSDRPHY(platform.request("sdram"), sys_clk_freq)
            self.add_sdram("sdram",
                phy                     = self.sdrphy,
                module                  = MT48LC32M8(sys_clk_freq, "1:1"),
                l2_cache_size           = kwargs.get("l2_size", 1024)
            )

        # SPI Flash --------------------------------------------------------------------------------
        from litespi.modules import M25PX32
        from litespi.opcodes import SpiNorFlashOpCodes as Codes
        self.add_spi_flash(mode="1x", module=M25PX32(Codes.READ_1_1_1), with_master=False)

        # Add ROM linker region --------------------------------------------------------------------
        self.bus.add_region("rom", SoCRegion(
            origin = self.bus.regions["spiflash"].origin + bios_flash_offset,
            size   = 32*kB,
            linker = True)
        )
        self.cpu.set_reset_address(self.bus.regions["rom"].origin)

        # Leds -------------------------------------------------------------------------------------
        self.leds = LedChaser(
            pads         = platform.request_all("user_led"),
            sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=qwertyembedded_beaglewire.Platform, description="LiteX SoC on Beaglewire.")
    parser.add_target_argument("--bios-flash-offset", default="0x60000",        help="BIOS offset in SPI Flash.")
    parser.add_target_argument("--sys-clk-freq",      default=50e6, type=float, help="System clock frequency.")
    args = parser.parse_args()

    soc = BaseSoC(
         bios_flash_offset = int(args.bios_flash_offset, 0),
         sys_clk_freq      = args.sys_clk_freq,
         **parser.soc_argdict
    )
    builder = Builder(soc,  **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

if __name__ == "__main__":
    main()
