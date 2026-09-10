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

from litex_boards.platforms import lattice_ice40up5k_evn
from litex.build.lattice.programmer import IceStormProgrammer

from litex.soc.cores.ram import Up5kSPRAM
from litex.soc.integration.soc import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        assert sys_clk_freq == 12e6
        self.rst    = Signal()
        self.cd_sys = ClockDomain()
        self.cd_por = ClockDomain()

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
    def __init__(self, bios_flash_offset, sys_clk_freq=12e6,
        with_led_chaser = True,
        **kwargs):
        platform = lattice_ice40up5k_evn.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        # Disable Integrated ROM/SRAM since too large for iCE40 and UP5K has specific SPRAM.
        kwargs["integrated_sram_size"] = 0
        kwargs["integrated_rom_size"]  = 0
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Lattice iCE40UP5k EVN breakout board", **kwargs)

        # 128KB SPRAM (used as SRAM) ---------------------------------------------------------------
        self.spram = Up5kSPRAM(size=128 * KILOBYTE)
        self.bus.add_slave("sram", self.spram.bus, SoCRegion(origin=self.mem_map["sram"], size=128 * KILOBYTE))

        # SPI Flash --------------------------------------------------------------------------------
        # 4x mode is not possible on this board since WP and HOLD pins are not connected to the FPGA
        from litespi.modules import N25Q032A
        from litespi.opcodes import SpiNorFlashOpCodes as Codes
        self.add_spi_flash(mode="1x", module=N25Q032A(Codes.READ_1_1_1))

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

def flash(builder, bios_flash_offset):
    with open(builder.get_bitstream_filename(mode="flash"), "rb") as f:
        bitstream = f.read()
    with open(builder.get_bios_filename(), "rb") as f:
        bios = f.read()
    bios_size = 0x10000
    if len(bitstream) > bios_flash_offset:
        raise ValueError("Bitstream overlaps the BIOS flash offset.")
    if len(bios) > builder.soc.bus.regions["rom"].size:
        raise ValueError("BIOS exceeds the ROM region size.")
    if bios_flash_offset + bios_size > builder.soc.bus.regions["spiflash"].size:
        raise ValueError("BIOS image exceeds the SPI flash size.")
    os.makedirs(builder.output_dir, exist_ok=True)
    image_file = os.path.join(builder.output_dir, "image.bin")
    with open(image_file, "wb") as f:
        f.write(bitstream.ljust(bios_flash_offset, b"\xff"))
        f.write(bios.ljust(bios_size, b"\xff"))
    print("Flashing bitstream (+bios)")
    prog = IceStormProgrammer()
    prog.flash(0x0, image_file)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=lattice_ice40up5k_evn.Platform, description="LiteX SoC on Lattice iCE40UP5k EVN breakout board.")
    parser.add_target_argument("--sys-clk-freq",      default=12e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--bios-flash-offset", default="0x20000",        help="BIOS offset in SPI Flash.")
    parser.add_target_argument("--flash",             action="store_true",      help="Flash bitstream.")
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
        flash(builder, int(args.bios_flash_offset, 0))

if __name__ == "__main__":
    main()
