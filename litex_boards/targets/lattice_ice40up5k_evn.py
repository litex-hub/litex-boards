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

target="lattice_ice40up5k_evn"

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex_boards.platforms import lattice_ice40up5k_evn
from litex.build.lattice.programmer import IceStormProgrammer

from litex.soc.cores.ram import Up5kSPRAM
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

        # # #

        # Clk/Rst
        sys = platform.request("clk12")
        platform.add_period_constraint(sys, 1e9/12e6)

        # Power On Reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += self.cd_por.clk.eq(ClockSignal("sys"))
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # Sys Clk
        self.comb += self.cd_sys.clk.eq(sys)
        self.specials += AsyncResetSynchronizer(self.cd_sys, ~por_done)


# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    mem_map = {**SoCCore.mem_map, **{"spiflash": 0x80000000}}
    def __init__(self, bios_flash_offset, sys_clk_freq=int(12e6), with_led_chaser=True, **kwargs):
        platform = lattice_ice40up5k_evn.Platform()

        # Disable Integrated ROM/SRAM since too large for iCE40 and UP5K has specific SPRAM.
        kwargs["integrated_sram_size"] = 0
        kwargs["integrated_rom_size"]  = 0

        # Set CPU variant / reset address
        kwargs["cpu_reset_address"] = self.mem_map["spiflash"] + bios_flash_offset

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident          = "LiteX SoC on Lattice iCE40UP5k EVN breakout board",
            ident_version  = True,
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # 128KB SPRAM (used as SRAM) ---------------------------------------------------------------
        self.submodules.spram = Up5kSPRAM(size=128*kB)
        self.bus.add_slave("sram", self.spram.bus, SoCRegion(size=128*kB))

        # SPI Flash --------------------------------------------------------------------------------
        self.add_spi_flash(mode="1x", dummy_cycles=8) 
        # 4x mode is not possible on this board since WP and HOLD pins are not connected to the FPGA

        # Add ROM linker region --------------------------------------------------------------------
        self.bus.add_region("rom", SoCRegion(
            origin = self.mem_map["spiflash"] + bios_flash_offset,
            size   = 32*kB,
            linker = True)
        )

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led_n"),
                sys_clk_freq = sys_clk_freq)

        # Add a UART-Wishbone bridge -----------------------------------------
        debug_uart=False
        if debug_uart:
            # This will add a bridge on the second serial port defined in platform
            from litex.soc.cores.uart import UARTWishboneBridge
            self.submodules.uart_bridge = UARTWishboneBridge(
                platform.request("serial"),
                sys_clk_freq,
                baudrate=115200)
            self.add_wb_master(self.uart_bridge.wishbone)

# Flash --------------------------------------------------------------------------------------------

def flash(bios_flash_offset):
    from litex.build.dfu import DFUProg
    prog = IceStormProgrammer()
    bitstream  = open("build/"+target+"/gateware/"+target+".bin",  "rb")
    bios       = open("build/"+target+"/software/bios/bios.bin", "rb")
    image      = open("build/"+target+"/image.bin", "wb")
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
    print("Flashing bitstream (+bios)")
    prog.flash(0x0, "build/"+target+"/image.bin")

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on Lattice iCE40UP5k EVN breakout board")
    parser.add_argument("--build",             action="store_true", help="Build bitstream")
    parser.add_argument("--sys-clk-freq",      default=12e6,        help="System clock frequency (default: 12MHz)")
    parser.add_argument("--bios-flash-offset", default=0x20000,     help="BIOS offset in SPI Flash (default: 0x20000)")
    parser.add_argument("--flash",             action="store_true", help="Flash Bitstream")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        bios_flash_offset = args.bios_flash_offset,
        sys_clk_freq      = int(float(args.sys_clk_freq)),
        **soc_core_argdict(args)
    )
    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.flash:
        flash(args.bios_flash_offset)

if __name__ == "__main__":
    main()
