#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019 Sean Cross <sean@xobs.io>
# Copyright (c) 2018 David Shah <dave@ds0.me>
# Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause


from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from litex_boards.platforms import kosagi_fomu_pvt

from litex.soc.cores.ram import Up5kSPRAM
from litex.soc.cores.clock import iCE40PLL
from litex.soc.integration.soc import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        assert sys_clk_freq == 12e6
        self.rst       = Signal()
        self.cd_sys    = ClockDomain()
        self.cd_por    = ClockDomain()
        self.cd_usb_12 = ClockDomain()
        self.cd_usb_48 = ClockDomain()

        # # #

        # Clk/Rst
        clk48 = platform.request("clk48")
        platform.add_period_constraint(clk48, 1e9/48e6)

        # Power On Reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += self.cd_por.clk.eq(ClockSignal())
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # USB PLL
        self.pll = pll = iCE40PLL()
        #self.comb += pll.reset.eq(self.rst) # FIXME: Add proper iCE40PLL reset support and add back | self.rst.
        pll.clko_freq_range = ( 12e6,  275e9) # FIXME: improve iCE40PLL to avoid lowering clko_freq_min.
        pll.register_clkin(clk48, 48e6)
        pll.create_clkout(self.cd_usb_12, 12e6, with_reset=False)
        self.comb += self.cd_usb_48.clk.eq(clk48)
        self.specials += AsyncResetSynchronizer(self.cd_usb_12, ~por_done | ~pll.locked)
        self.specials += AsyncResetSynchronizer(self.cd_usb_48, ~por_done | ~pll.locked)

        # Sys Clk
        self.comb += self.cd_sys.clk.eq(self.cd_usb_12.clk)
        self.specials += AsyncResetSynchronizer(self.cd_sys, ~por_done | ~pll.locked)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, bios_flash_offset, sys_clk_freq=12e6,
        spi_flash_module = "AT25SF161",
        with_led_chaser  = True,
        **kwargs):
        platform = kosagi_fomu_pvt.Platform()

        # Default to USB ACM through LUNA, but allow explicit override.
        uart_name = kwargs.get("uart_name", "serial")
        if uart_name == "serial":
            uart_name = "usb_acm"
        kwargs["uart_name"] = uart_name

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        # Disable Integrated ROM/SRAM since too large for iCE40 and UP5K has specific SPRAM.
        kwargs["integrated_sram_size"] = 0
        kwargs["integrated_rom_size"]  = 0
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Fomu", **kwargs)

        # 128KB SPRAM (used as 64kB SRAM / 64kB RAM) -----------------------------------------------
        self.spram = Up5kSPRAM(size=128 * KILOBYTE)
        self.bus.add_slave("psram", self.spram.bus, SoCRegion(origin=self.mem_map["sram"], size=128 * KILOBYTE))
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
        from litespi.modules import AT25SF161, GD25Q16C, MX25R1635F, W25Q128JV
        from litespi.opcodes import SpiNorFlashOpCodes as Codes

        # lambdas for lazy module instantiation.
        spi_flash_modules = {
            "AT25SF161":  lambda: AT25SF161( Codes.READ_1_1_4),
            "GD25Q16C":   lambda: GD25Q16C(  Codes.READ_1_1_1),
            "MX25R1635F": lambda: MX25R1635F(Codes.READ_1_1_4),
            "W25Q128JV":  lambda: W25Q128JV( Codes.READ_1_1_4),
        }
        self.add_spi_flash(mode="4x", module=spi_flash_modules[spi_flash_module](), with_master=False)

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
                pads         = platform.request_all("user_led_n"),
                sys_clk_freq = sys_clk_freq)

# Flash --------------------------------------------------------------------------------------------

DFU_FLASH_OFFSET = 0x40000

def flash(builder, bios_flash_offset):
    from litex.build.dfu import DFUProg
    with open(builder.get_bitstream_filename(mode="flash"), "rb") as f:
        bitstream = f.read()
    with open(builder.get_bios_filename(), "rb") as f:
        bios = f.read()
    bios_size = builder.soc.bus.regions["rom"].size
    if bios_flash_offset < 128 * KILOBYTE:
        raise ValueError("BIOS offset must leave at least 128 KiB for the bitstream.")
    if len(bitstream) > bios_flash_offset:
        raise ValueError("Bitstream overlaps the BIOS flash offset.")
    if len(bios) > bios_size:
        raise ValueError("BIOS exceeds the ROM region size.")
    if DFU_FLASH_OFFSET + bios_flash_offset + bios_size > builder.soc.bus.regions["spiflash"].size:
        raise ValueError("DFU image exceeds the SPI flash size.")
    os.makedirs(builder.output_dir, exist_ok=True)
    image_file = os.path.join(builder.output_dir, "image.bin")
    with open(image_file, "wb") as f:
        f.write(bitstream.ljust(bios_flash_offset, b"\xff"))
        f.write(bios.ljust(bios_size, b"\xff"))
    prog = DFUProg(vid="1209", pid="5bf0")
    prog.load_bitstream(image_file)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=kosagi_fomu_pvt.Platform, description="LiteX SoC on Fomu.")
    parser.add_target_argument("--sys-clk-freq",      default=12e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--bios-flash-offset", default="0x20000",        help="BIOS offset in SPI Flash.")
    parser.add_target_argument("--flash",             action="store_true",      help="Flash bitstream.")
    args = parser.parse_args()

    soc = BaseSoC(
        bios_flash_offset = DFU_FLASH_OFFSET + int(args.bios_flash_offset, 0),
        sys_clk_freq      = args.sys_clk_freq,
        **parser.soc_argdict
    )
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.flash:
        flash(builder, int(args.bios_flash_offset, 0))

if __name__ == "__main__":
    main()
