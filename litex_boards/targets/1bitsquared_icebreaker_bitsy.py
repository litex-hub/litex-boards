#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019 Sean Cross <sean@xobs.io>
# Copyright (c) 2018 David Shah <dave@ds0.me>
# Copyright (c) 2020 Piotr Esden-Tempski <piotr@esden.net>
# Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2021 Sylvain Munaut <tnt@246tNt.com>
# SPDX-License-Identifier: BSD-2-Clause

# This target file provides a minimal LiteX SoC for the iCEBreaker-bitsy with a CPU,
# its ROM (in SPI Flash), its SRAM, close to the others LiteX targets.
# For more complete example of LiteX SoC for the iCEBreaker-bitsy with more features and
# documentation can be found, refer to :
# https://github.com/icebreaker-fpga/icebreaker-litex-examples

import os
import argparse

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex_boards.platforms import icebreaker_bitsy

from litex.soc.cores.ram import Up5kSPRAM
from litex.soc.cores.spi_flash import SpiFlash
from litex.soc.cores.clock import iCE40PLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *

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
        clk12 = platform.request("clk12")
        rst_n = platform.request("user_btn_n")

        # Power On Reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += self.cd_por.clk.eq(ClockSignal())
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # PLL
        self.submodules.pll = pll = iCE40PLL(primitive="SB_PLL40_PAD")
        self.comb += pll.reset.eq(~rst_n) # FIXME: Add proper iCE40PLL reset support and add back | self.rst.
        pll.register_clkin(clk12, 12e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq, with_reset=False)
        self.specials += AsyncResetSynchronizer(self.cd_sys, ~por_done | ~pll.locked)
        platform.add_period_constraint(self.cd_sys.clk, 1e9/sys_clk_freq)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    mem_map = {**SoCCore.mem_map, **{"spiflash": 0x80000000}}
    def __init__(self, bios_flash_offset, sys_clk_freq=int(24e6), revision="v1", **kwargs):
        platform = icebreaker_bitsy.Platform(revision=revision)

        # Disable Integrated ROM/SRAM since too large for iCE40 and UP5K has specific SPRAM.
        kwargs["integrated_sram_size"] = 0
        kwargs["integrated_rom_size"]  = 0

        # Set CPU variant / reset address
        kwargs["cpu_reset_address"] = self.mem_map["spiflash"] + bios_flash_offset

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident          = "LiteX SoC on iCEBreaker-bitsy",
            ident_version  = True,
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # 128KB SPRAM (used as SRAM) ---------------------------------------------------------------
        self.submodules.spram = Up5kSPRAM(size=128*kB)
        self.bus.add_slave("sram", self.spram.bus, SoCRegion(size=128*kB))

        # SPI Flash --------------------------------------------------------------------------------
        self.add_spi_flash(mode="1x", dummy_cycles=8)

        # Add ROM linker region --------------------------------------------------------------------
        self.bus.add_region("rom", SoCRegion(
            origin = self.mem_map["spiflash"] + bios_flash_offset,
            size   = 32*kB,
            linker = True)
        )

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on iCEBreaker")
    parser.add_argument("--build",               action="store_true", help="Build bitstream")
    parser.add_argument("--flash",               action="store_true", help="Flash bitstream and bios")
    parser.add_argument("--sys-clk-freq",        default=24e6,        help="System clock frequency (default: 24MHz)")
    parser.add_argument("--bios-flash-offset",   default=0xa0000,     help="BIOS offset in SPI Flash (default: 0xa0000)")
    parser.add_argument("--revision",            default="v1",        help="Board revision 'v0' or 'v1'")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        bios_flash_offset   = args.bios_flash_offset,
        sys_clk_freq        = int(float(args.sys_clk_freq)),
		revision            = args.revision,
        **soc_core_argdict(args)
    )
    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.flash:
        from litex.build.dfu import DFUProg
        prog_gw = DFUProg(vid="1d50", pid="0x6146", alt=0)
        prog_sw = DFUProg(vid="1d50", pid="0x6146", alt=1)

        prog_gw.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".bin"), reset=False)
        prog_sw.load_bitstream(os.path.join(builder.software_dir, 'bios/bios.bin'))

if __name__ == "__main__":
    main()
