#!/usr/bin/env python3

# This file is Copyright (c) 2018-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# This file is Copyright (c) 2018-2019 David Shah <dave@ds0.me>
# License: BSD

import os
import argparse

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex_boards.platforms import crosslink_nx_eval

from litex.soc.cores.lifclspram import LIFCLSPRAM
from litex.soc.cores.spi_flash import SpiFlash
from litex.build.io import CRG
from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc_sdram import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

kB = 1024
mB = 1024*kB

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    SoCCore.mem_map = {
        "sram":             0x10000000,
        "spiflash":         0x20000000,
        "csr":              0xf0000000,
    }
    def __init__(self, bios_flash_offset, sys_clk_freq=int(125e6), **kwargs):
        platform = crosslink_nx_eval.Platform()

        # TODO
        # Disable Integrated ROM/SRAM since too large for iCE40 and UP5K has specific SPRAM.
        kwargs["integrated_sram_size"] = 0
        kwargs["integrated_rom_size"]  = 0

        # Set CPU variant / reset address
        kwargs["cpu_reset_address"] = self.mem_map["spiflash"] + bios_flash_offset

        # SoCCore -----------------------------------------_----------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident          = "LiteX SoC on Crosslink-NX",
            ident_version  = True,
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = CRG(platform.request(platform.default_clk_name))

        # 128KB SPRAM (used as SRAM) ---------------------------------------------------------------
        self.submodules.spram = LIFCLSPRAM(size=128*kB)
        self.register_mem("sram", self.mem_map["sram"], self.spram.bus, 128*kB)

        # SPI Flash --------------------------------------------------------------------------------
        self.submodules.spiflash = SpiFlash(platform.request("spiflash4x"), dummy=6, endianness="little")
        self.register_mem("spiflash", self.mem_map["spiflash"], self.spiflash.bus, size=16*mB)
        self.add_csr("spiflash")

        # Add ROM linker region --------------------------------------------------------------------
        self.add_memory_region("rom", self.mem_map["spiflash"] + bios_flash_offset, 32*kB, type="cached+linker")

        # Leds -------------------------------------------------------------------------------------
        self.submodules.leds = LedChaser(
            pads         = Cat(*[platform.request("user_led", i) for i in range(11)]),
            sys_clk_freq = sys_clk_freq)
        self.add_csr("leds")

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on Crosslink-NX Eval Board")
    parser.add_argument("--build", action="store_true", help="Build bitstream")
    parser.add_argument("--load",  action="store_true", help="Load bitstream")
    parser.add_argument("--bios-flash-offset", default=0x40000,     help="BIOS offset in SPI Flash")
    builder_args(parser)
    soc_sdram_args(parser)
    parser.add_argument("--sys-clk-freq",  default=125e6, help="System clock frequency (default=125MHz)")
    args = parser.parse_args()

    soc = BaseSoC(args.bios_flash_offset, sys_clk_freq=int(float(args.sys_clk_freq)),
        **soc_sdram_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder_kargs = {}
    builder.build(**builder_kargs, run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".svf"))

if __name__ == "__main__":
    main()
