#!/usr/bin/env python3

#
# This file is part of LiteX.
#
# Copyright (c) 2014-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2013-2014 Sebastien Bourdeauducq <sb@m-labs.hk>
# SPDX-License-Identifier: BSD-2-Clause

import os
import argparse
import importlib

from migen import *

from litex.build.io import CRG

from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litex_boards.platforms import tec0117

kB = 1024
mB = 1024*kB

class BaseSoC(SoCCore):
    mem_map = {**SoCCore.mem_map, **{"spiflash": 0x80000000}}
    def __init__(self, bios_flash_offset, **kwargs):
        platform     = tec0117.Platform()
        sys_clk_freq = int(1e9/platform.default_clk_period)

        # SoC can have littel a bram, as a treat
        kwargs["integrated_sram_size"] = 2048*2
        kwargs["integrated_rom_size"]  = 0

        # Set CPU variant / reset address
        kwargs["cpu_reset_address"] = self.mem_map["spiflash"] + bios_flash_offset

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident          = "LiteX SoC on TEC0117",
            ident_version  = True,
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = CRG(
                platform.request(platform.default_clk_name),
                ~platform.request('rst'),
        )

        # SPI Flash --------------------------------------------------------------------------------
        self.add_spi_flash(mode="1x", dummy_cycles=8)

        # Add ROM linker region --------------------------------------------------------------------
        self.bus.add_region("rom", SoCRegion(
            origin = self.mem_map["spiflash"] + bios_flash_offset,
            size   = 8*mB,
            linker = True)
        )

        # Leds -------------------------------------------------------------------------------------
        self.submodules.leds = LedChaser(
            pads         = platform.request_all("user_led"),
            sys_clk_freq = sys_clk_freq)
        self.add_csr("leds")

# Flash --------------------------------------------------------------------------------------------

def flash(offset, path):
    from spiflash.serialflash import SerialFlashManager
    platform = tec0117.Platform()
    flash = platform.request("spiflash", 0)
    bus = platform.request("spiflash", 1)

    module = Module()
    module.comb += [
        flash.clk.eq(bus.clk),
        flash.cs_n.eq(bus.cs_n),
        flash.mosi.eq(bus.mosi),
        bus.miso.eq(flash.miso),
    ]

    platform.build(module)
    prog = platform.create_programmer()
    prog.load_bitstream('build/impl/pnr/project.fs')

    dev = SerialFlashManager.get_flash_device("ftdi://ftdi:2232/2")
    dev.TIMINGS['chip'] = (4, 60) # chip is too slow
    print("Erasing flash...")
    dev.erase(0, -1)

    with open(path, 'rb') as f:
        bios = f.read()

    print("Programming flash...")
    dev.write(offset, bios)



# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on iCEBreaker")
    parser.add_argument("--build",             action="store_true", help="Build bitstream")
    parser.add_argument("--load",              action="store_true", help="Load bitstream")
    parser.add_argument("--bios-flash-offset", default=0,     help="BIOS offset in SPI Flash")
    parser.add_argument("--flash",             action="store_true", help="Flash bios")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc     = BaseSoC(args.bios_flash_offset, **soc_core_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.flash:
        flash(
            args.bios_flash_offset,
            os.path.join(builder.software_dir, "bios", "bios.bin"))

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(
            os.path.join(builder.gateware_dir, "impl", "pnr", "project.fs"),
            args.flash)


if __name__ == "__main__":
    main()
