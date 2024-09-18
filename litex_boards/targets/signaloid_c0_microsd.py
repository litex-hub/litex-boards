#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
# Copyright (c) 2024, Signaloid <developer-support@signaloid.com>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from litex_boards.platforms import signaloid_c0_microsd

from litex.soc.cores.ram import Up5kSPRAM
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser


# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst         = Signal()
        self.cd_sys      = ClockDomain()
        self.cd_por      = ClockDomain()
        self.cd_clk10khz = ClockDomain()

        assert sys_clk_freq in [6e6, 12e6, 24e6, 48e6]

        # # #

        # Power On Reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += self.cd_por.clk.eq(self.cd_sys.clk)
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # High frequency oscillator (HFSOC) up to 48MHz
        clk_hf_div = {
            48e6: "0b00",
            24e6: "0b01",
            12e6: "0b10",
             6e6: "0b11"}[sys_clk_freq]

        self.specials += Instance(
            "SB_HFOSC",
            p_CLKHF_DIV = clk_hf_div,
            i_CLKHFEN   = 0b1,
            i_CLKHFPU   = 0b1,
            o_CLKHF     = self.cd_sys.clk,
        )
        self.specials += AsyncResetSynchronizer(self.cd_sys, ~por_done)
        platform.add_period_constraint(self.cd_sys.clk, 1e9 / sys_clk_freq)

        # Low frequency oscillator (LFOSC) at 10kHz
        self.specials += Instance(
            "SB_LFOSC",
            i_CLKLFEN=0b1,
            i_CLKLFPU=0b1,
            o_CLKLF=self.cd_clk10khz.clk,
        )

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, bios_flash_offset, sys_clk_freq=24e6,
        with_led_chaser = True,
        **kwargs):
        platform = signaloid_c0_microsd.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        # Disable Integrated ROM/SRAM since too large for iCE40 and UP5K has specific SPRAM.
        kwargs["integrated_sram_size"] = 0
        kwargs["integrated_rom_size"]  = 0
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Signaloid C0-microSD", **kwargs)

        # 128KB SPRAM (used as 64kB SRAM / 64kB RAM) -----------------------------------------------
        self.spram = Up5kSPRAM(size=128 * KILOBYTE)
        self.bus.add_slave("psram", self.spram.bus, SoCRegion(size=128 * KILOBYTE))
        self.bus.add_region("sram", SoCRegion(
            origin = self.bus.regions["psram"].origin + 0 * KILOBYTE,
            size   = 64 * KILOBYTE,
            linker = True)
        )
        if not self.integrated_main_ram_size:
            self.bus.add_region("main_ram", SoCRegion(
                origin = self.bus.regions["psram"].origin + 64 * KILOBYTE,
                size   = 64 * KILOBYTE,
                linker = True)
            )

        # SPI Flash --------------------------------------------------------------------------------
        # Signaloid C0-microSD uses the AT25QL128A SPI flash with the QPI mode
        # disabled. Hence, the AT25SL128A module is used instead, which is
        # compatible with Signaloid C0-microSD's AT25QL128A with the QPI mode
        # disabled.
        from litespi.modules import AT25SL128A
        from litespi.opcodes import SpiNorFlashOpCodes as Codes
        self.add_spi_flash(mode="1x", module=AT25SL128A(Codes.READ_1_1_1), with_master=False)

        # Add ROM linker region --------------------------------------------------------------------
        self.bus.add_region("rom", SoCRegion(
            origin = self.bus.regions["spiflash"].origin + bios_flash_offset,
            size   = 32 * KILOBYTE,
            linker = True)
        )
        self.cpu.set_reset_address(self.bus.regions["rom"].origin)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Flash --------------------------------------------------------------------------------------------

def flash(build_dir, build_name, bios_flash_offset):
    print("\033[93m")
    print("-------------------------------------------------------------------------------")
    print("Programming is not supported for this platform.")
    print("Please use the official Signaloid C0-microSD utilities for flashing the device.")
    print("https://github.com/signaloid/C0-microSD-utilities")
    print(f"Bitstream path: {build_dir}/gateware/{build_name}.bin")
    print(f"Binary path   : {build_dir}/software/bios/bios.bin")
    print("-------------------------------------------------------------------------------")
    print("\033[0m")

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=signaloid_c0_microsd.Platform, description="LiteX SoC on Signaloid C0-microSD.")
    parser.add_target_argument("--flash",             action="store_true",      help="Flash Bitstream and BIOS.")
    parser.add_target_argument("--sys-clk-freq",      default=24e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--bios-flash-offset", default="0x200000",       help="BIOS offset in SPI Flash.")
    parser.add_target_argument("--add_uart",          action="store_true",      help="Enable UART (shared pins with clk/SD interface.")
    args = parser.parse_args()

    if not args.add_uart:
        args.no_uart = True

    soc = BaseSoC(
        bios_flash_offset   = int(args.bios_flash_offset, 0),
        sys_clk_freq        = args.sys_clk_freq,
        **parser.soc_argdict
    )
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        print("\033[93m")
        print("-------------------------------------------------------------------------------")
        print("Loading is not supported for this platform.")
        print("Please use the official Signaloid C0-microSD utilities for flashing the device.")
        print("https://github.com/signaloid/C0-microSD-utilities")
        print("-------------------------------------------------------------------------------")
        print("\033[0m")

    if args.flash:
        flash(builder.output_dir, soc.build_name, args.bios_flash_offset)

if __name__ == "__main__":
    main()
