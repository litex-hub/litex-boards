#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
# Copyright (c) 2021 Omkar Bhilare <ombhilare999@gmail.com>
# Copyright (c) 2021 Michael Welling <mwelling@ieee.org>
# SPDX-License-Identifier: BSD-2-Clause

import os
import sys
import argparse

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex_boards.platforms import beaglewire

from litex.build.io import DDROutput

from litex.soc.cores.clock import iCE40PLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.spi_flash import SpiFlash
from litex.soc.cores.led import LedChaser
from litex.soc.cores.uart import UARTWishboneBridge

from litedram.phy import GENSDRPHY
from litedram.modules import MT48LC32M8

kB = 1024
mB = 1024*kB

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_sys = ClockDomain()
        self.clock_domains.cd_por = ClockDomain(reset_less=True)

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
        self.submodules.pll = pll = iCE40PLL()
        self.comb += pll.reset.eq(rst_n) # FIXME: Add proper iCE40PLL reset support and add back | self.rst.
        pll.register_clkin(clk100, 100e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq, with_reset=False)
        self.specials += AsyncResetSynchronizer(self.cd_sys, ~por_done | ~pll.locked)
        platform.add_period_constraint(self.cd_sys.clk, 1e9/sys_clk_freq)

        # SDRAM clock
        self.specials += DDROutput(0, 1, platform.request("sdram_clock"),  ClockSignal("sys"))

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    mem_map = {**SoCCore.mem_map, **{"spiflash": 0x80000000}}
    def __init__(self, bios_flash_offset, sys_clk_freq=int(50e6), **kwargs):
        platform = beaglewire.Platform()

        # Disable Integrated ROM since too large for iCE40.
        kwargs["integrated_rom_size"]  = 0
        kwargs["integrated_sram_size"] = 2*kB

        # Set CPU reset address
        kwargs["cpu_reset_address"] = self.mem_map["spiflash"] + bios_flash_offset

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, 
            ident          = "LiteX SoC on Beaglewire",
            ident_version  = True,
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # SDR SDRAM --------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.submodules.sdrphy = GENSDRPHY(platform.request("sdram"), sys_clk_freq)
            self.add_sdram("sdram",
                phy                     = self.sdrphy,
                module                  = MT48LC32M8(sys_clk_freq, "1:1"),
                l2_cache_size           = kwargs.get("l2_size", 1024)
            )

        # SPI Flash --------------------------------------------------------------------------------
        self.add_spi_flash(mode="1x", dummy_cycles=8)

        # Add ROM linker region --------------------------------------------------------------------
        self.bus.add_region("rom", SoCRegion(
            origin = self.mem_map["spiflash"] + bios_flash_offset,
            size   = 32*kB,
            linker = True)
        )

        # Leds -------------------------------------------------------------------------------------
        self.submodules.leds = LedChaser(
            pads         = platform.request_all("user_led"),
            sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on Beaglewire")
    parser.add_argument("--build",             action="store_true", help="Build bitstream")
    parser.add_argument("--bios-flash-offset", default=0x60000,     help="BIOS offset in SPI Flash (default: 0x60000)")
    parser.add_argument("--sys-clk-freq",      default=50e6,        help="System clock frequency (default: 50MHz)")
    parser.add_argument("--output_dir",        default="build",         help="Output directory of csr")
    parser.add_argument("--csr_csv",           default="build/csr.csv", help="csr.csv")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
         bios_flash_offset = args.bios_flash_offset,
         sys_clk_freq      = int(float(args.sys_clk_freq)),
         **soc_core_argdict(args)
    )
    builder = Builder(soc,  **builder_argdict(args))
    builder.build(run=args.build)

if __name__ == "__main__":
    main()
