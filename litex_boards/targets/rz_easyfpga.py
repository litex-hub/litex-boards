#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# SPDX-License-Identifier: BSD-2-Clause

import os
import argparse

from migen import *

from litex.build.io import DDROutput

from litex_boards.platforms import rz_easyfpga

from litex.soc.cores.clock import CycloneIVPLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.cores.led import LedChaser

from litedram.modules import HY57V641620FTP
from litedram.phy import GENSDRPHY

kB = 1024

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq, sdram_rate="1:1"):
        self.rst = Signal()
        self.clock_domains.cd_sys = ClockDomain()
        self.clock_domains.cd_sys_ps = ClockDomain(reset_less=True)

        # # #

        # Clk / Rst
        clk50 = platform.request("clk50")

        # PLL
        self.submodules.pll = pll = CycloneIVPLL(speedgrade="-8")
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk50, 50e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=90)

        # SDRAM clock
        self.comb += platform.request("sdram_clock").eq(self.cd_sys_ps.clk)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    mem_map = {**SoCCore.mem_map, **{"spiflash": 0x80000000}}
    def __init__(self, bios_flash_offset, spi_flash_module="W25Q16JV", sys_clk_freq=int(50e6),
                 with_led_chaser=True, **kwargs):
        print(kwargs)

        platform = rz_easyfpga.Platform()

        # Use external ROM since too large for Cyclone IV EP4CE6
        kwargs["integrated_rom_size"]  = 0
        kwargs["integrated_sram_size"] = 0x800

        # Set CPU variant / reset address
        kwargs["cpu_reset_address"] = self.mem_map["spiflash"] + bios_flash_offset

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident          = "LiteX SoC on RZ-EasyFPGA",
            ident_version  = True,
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # SDR SDRAM --------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.submodules.sdrphy = GENSDRPHY(platform.request("sdram"), sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.sdrphy,
                module        = HY57V641620FTP(sys_clk_freq, "1:1"), # Hynix
                l2_cache_size = kwargs.get("l2_size", 0)
            )

        # SPI Flash --------------------------------------------------------------------------------
        from litespi.modules import W25Q16JV
        from litespi.opcodes import SpiNorFlashOpCodes as Codes

        # lambdas for lazy module instantiation.
        spi_flash_modules = {
            "W25Q16JV":  lambda: W25Q16JV( Codes.READ_1_1_4),
        }
        self.add_spi_flash(mode="4x", module=spi_flash_modules[spi_flash_module](), with_master=False)

        # Add ROM linker region --------------------------------------------------------------------
        self.bus.add_region("rom", SoCRegion(
            origin = self.mem_map["spiflash"] + bios_flash_offset,
            size   = 32*kB,
            linker = True)
        )

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on RZ-EasyFPGA")
    parser.add_argument("--build",        action="store_true", help="Build bitstream")
    parser.add_argument("--load",         action="store_true", help="Load bitstream")
    parser.add_argument("--sys-clk-freq", default=50e6,        help="System clock frequency (default: 50MHz)")
    parser.add_argument("--bios-flash-offset", default=0x20000,     help="BIOS offset in SPI Flash (default: 0x20000)")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    dfu_flash_offset = 0x40000

    soc = BaseSoC(
        bios_flash_offset = dfu_flash_offset + args.bios_flash_offset,
        sys_clk_freq = int(float(args.sys_clk_freq)),
        **soc_core_argdict(args)
    )
    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".sof"))

if __name__ == "__main__":
    main()
