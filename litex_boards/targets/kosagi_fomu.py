#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019 Sean Cross <sean@xobs.io>
# Copyright (c) 2018 David Shah <dave@ds0.me>
# Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

import os
import sys

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex_boards.platforms import kosagi_fomu_pvt

from litex.soc.cores.ram import Up5kSPRAM
from litex.soc.cores.clock import iCE40PLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

kB = 1024
mB = 1024*kB

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        assert sys_clk_freq == 12e6
        self.rst = Signal()
        self.clock_domains.cd_sys    = ClockDomain()
        self.clock_domains.cd_por    = ClockDomain()
        self.clock_domains.cd_usb_12 = ClockDomain()
        self.clock_domains.cd_usb_48 = ClockDomain()

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
        self.submodules.pll = pll = iCE40PLL()
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
    def __init__(self, bios_flash_offset, spi_flash_module="AT25SF161", sys_clk_freq=int(12e6),
                 with_led_chaser=True, **kwargs):
        platform = kosagi_fomu_pvt.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        # Defaults to USB ACM through ValentyUSB.
        kwargs["uart_name"] = "usb_acm"
        # Disable Integrated ROM/SRAM since too large for iCE40 and UP5K has specific SPRAM.
        kwargs["integrated_sram_size"] = 0
        kwargs["integrated_rom_size"]  = 0
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Fomu", **kwargs)

        # 128KB SPRAM (used as 64kB SRAM / 64kB RAM) -----------------------------------------------
        self.submodules.spram = Up5kSPRAM(size=128*kB)
        self.bus.add_slave("psram", self.spram.bus, SoCRegion(size=128*kB))
        self.bus.add_region("sram", SoCRegion(
                origin = self.bus.regions["psram"].origin + 0*kB,
                size   = 64*kB,
                linker = True)
        )
        if not self.integrated_main_ram_size:
            self.bus.add_region("main_ram", SoCRegion(
                origin = self.bus.regions["psram"].origin + 64*kB,
                size   = 64*kB,
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
            size   = 32*kB,
            linker = True)
        )
        self.cpu.set_reset_address(self.bus.regions["rom"].origin)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led_n"),
                sys_clk_freq = sys_clk_freq)

# Flash --------------------------------------------------------------------------------------------

def flash(build_dir, build_name, bios_flash_offset):
    from litex.build.dfu import DFUProg
    prog = DFUProg(vid="1209", pid="5bf0")
    bitstream = open(f"{build_dir}/gateware/{build_name}.bin",  "rb")
    bios      = open(f"{build_dir}/software/bios/bios.bin", "rb")
    image     = open(f"{build_dir}/image.bin", "wb")
    # Copy bitstream at 0.
    assert bios_flash_offset >= 128*kB
    for i in range(0, bios_flash_offset):
        b = bitstream.read(1)
        if not b:
            image.write(0xff.to_bytes(1, "big"))
        else:
            image.write(b)
    # Copy bios at bios_flash_offset.
    for i in range(0, 32*kB):
        b = bios.read(1)
        if not b:
            image.write(0xff.to_bytes(1, "big"))
        else:
            image.write(b)
    bitstream.close()
    bios.close()
    image.close()
    prog.load_bitstream(f"{build_dir}/image.bin")

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on Fomu")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",             action="store_true", help="Build design.")
    target_group.add_argument("--sys-clk-freq",      default=12e6,        help="System clock frequency.")
    target_group.add_argument("--bios-flash-offset", default="0x20000",   help="BIOS offset in SPI Flash.")
    target_group.add_argument("--flash",             action="store_true", help="Flash Bitstream.")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    dfu_flash_offset = 0x40000

    soc = BaseSoC(
        bios_flash_offset = dfu_flash_offset + int(args.bios_flash_offset, 0),
        sys_clk_freq      = int(float(args.sys_clk_freq)),
        **soc_core_argdict(args)
    )
    builder = Builder(soc, **builder_argdict(args))
    if args.build:
        builder.build()

    if args.flash:
        flash(builder.output_dir, soc.build_name, int(args.bios_flash_offset, 0))

if __name__ == "__main__":
    main()
