#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2023 Nimalan M <nimalan.m@protonmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import *

from litex_boards.platforms import alchitry_cu

from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.clock import iCE40PLL
from litex.soc.cores.led import LedChaser

from migen.genlib.resetsync import AsyncResetSynchronizer

kB = 1024
mB = 1024*kB


# CRG -------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()
        self.cd_por = ClockDomain()
    
        # Clk/Rst
        clk100  = platform.request("clk100")
        rst_n   = platform.request("cpu_reset")

        # Power On Reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += self.cd_por.clk.eq(ClockSignal())
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        self.pll = pll = iCE40PLL(primitive="SB_PLL40_CORE")
        self.comb += pll.reset.eq(~rst_n) # FIXME: Add proper iCE40PLL reset support and add back | self.rst.
        pll.register_clkin(clk100, 100e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq, with_reset=False)
        self.specials += AsyncResetSynchronizer(self.cd_sys, ~por_done | ~pll.locked)
        platform.add_period_constraint(self.cd_sys.clk, 1e9/sys_clk_freq)

# BaseSoC -----------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
  def __init__(self,
    bios_flash_offset,
    sys_clk_freq=50e6,
    with_led_chaser = True,
    **kwargs):
        # Create our platform (fpga interface)
        platform = alchitry_cu.Platform()

        # Disable Integrated ROM since too large for iCE40.
        kwargs["integrated_rom_size"]  = 0

        # SoC with CPU
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident                    = "LiteX SoC on Alchitry Cu",
            **kwargs)

        # CRG
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # SPI Flash --------------------------------------------------------------------------------
        from litespi.modules import W25Q32
        from litespi.opcodes import SpiNorFlashOpCodes as Codes
        self.add_spi_flash(mode="1x", module=W25Q32(Codes.READ_1_1_1), with_master=False)

        # Add ROM linker region --------------------------------------------------------------------
        self.bus.add_region("rom", SoCRegion(
            origin = self.bus.regions["spiflash"].origin + bios_flash_offset,
            size   = 256*kB,
            linker = True)
        )
        self.cpu.set_reset_address(self.bus.regions["rom"].origin)

        # Led
        if with_led_chaser:
            self.submodules.leds = LedChaser(pads=platform.request_all("user_led"), sys_clk_freq=sys_clk_freq)

# Flash --------------------------------------------------------------------------------------------

def flash(build_dir, build_name, bios_flash_offset):
    from litex.build.lattice.programmer import IceStormProgrammer
    prog = IceStormProgrammer()
    prog.flash(bios_flash_offset, f"{build_dir}/software/bios/bios.bin")
    prog.flash(0x00000000,        f"{build_dir}/gateware/{build_name}.bin")

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=alchitry_cu.Platform, description="LiteX SoC on Alchitry Cu")
    parser.add_target_argument("--flash",             action="store_true",      help="Flash Bitstream and BIOS.")
    parser.add_target_argument("--bios-flash-offset", default="0x040000",       help="BIOS offset in SPI Flash (default: 0x40000)")
    parser.add_target_argument("--sys-clk-freq",      default=50e6, type=float, help="System clock frequency (default: 50MHz)")
    parser.add_target_argument("--with-led-chaser",   action="store_true",      help="Enable LED Chaser.")
    args = parser.parse_args()

    soc = BaseSoC(
         bios_flash_offset = int(args.bios_flash_offset, 0),
         sys_clk_freq      = args.sys_clk_freq,
         **parser.soc_argdict
    )
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.flash:
        flash(builder.output_dir, soc.build_name, args.bios_flash_offset)


if __name__ == "__main__":
    main()
