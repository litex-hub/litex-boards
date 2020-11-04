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
import argparse

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex_boards.platforms import fomu_pvt

from litex.soc.cores.up5kspram import Up5kSPRAM
from litex.soc.cores.spi_flash import SpiFlash
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
        self.clock_domains.cd_por    = ClockDomain(reset_less=True)
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
        self.comb += pll.reset.eq(self.rst)
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
    mem_map = {**SoCCore.mem_map, **{"spiflash": 0x80000000}}
    def __init__(self, bios_flash_offset, **kwargs):
        kwargs["uart_name"] = "usb_acm" # Enforce UART to USB-ACM
        sys_clk_freq = int(12e6)
        platform = fomu_pvt.Platform()

        # Disable Integrated ROM/SRAM since too large for iCE40 and UP5K has specific SPRAM.
        kwargs["integrated_sram_size"] = 0
        kwargs["integrated_rom_size"]  = 0

        # Set CPU variant / reset address
        kwargs["cpu_reset_address"] = self.mem_map["spiflash"] + bios_flash_offset

        # Serial -----------------------------------------------------------------------------------
        # FIXME: do proper install of ValentyUSB.
        # FIXME: replace IoBuf with https://github.com/im-tomu/valentyusb/blob/master/valentyusb/usbcore/io.py#L13-L61.
        os.system("git clone https://github.com/gregdavill/valentyusb -b hw_cdc_eptri")
        sys.path.append("valentyusb")

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident          = "LiteX SoC on Fomu",
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

        # Leds -------------------------------------------------------------------------------------
        self.submodules.leds = LedChaser(
            pads         = platform.request_all("user_led_n"),
            sys_clk_freq = sys_clk_freq)
        self.add_csr("leds")

# Flash --------------------------------------------------------------------------------------------

def flash(bios_flash_offset):
    from litex.build.dfu import DFUProg
    prog = DFUProg(vid="1209", pid="5bf0")
    bitstream  = open("build/fomu_pvt/gateware/fomu_pvt.bin",  "rb")
    bios       = open("build/fomu_pvt/software/bios/bios.bin", "rb")
    image      = open("build/fomu_pvt/image.bin", "wb")
    # Copy bitstream at 0x00000000
    for i in range(0x00000000, 0x0020000):
        b = bitstream.read(1)
        if not b:
            image.write(0xff.to_bytes(1, "big"))
        else:
            image.write(b)
    # Copy bios at 0x00020000
    for i in range(0x00000000, 0x00010000):
        b = bios.read(1)
        if not b:
            image.write(0xff.to_bytes(1, "big"))
        else:
            image.write(b)
    bitstream.close()
    bios.close()
    image.close()
    prog.load_bitstream("build/fomu_pvt/image.bin")

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on Fomu")
    parser.add_argument("--build", action="store_true", help="Build bitstream")
    parser.add_argument("--bios-flash-offset", default=0x60000, help="BIOS offset in SPI Flash")
    parser.add_argument("--flash",             action="store_true", help="Flash Bitstream")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(args.bios_flash_offset, **soc_core_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.flash:
        flash(args.bios_flash_offset)

if __name__ == "__main__":
    main()
