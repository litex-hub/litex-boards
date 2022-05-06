#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019 Sean Cross <sean@xobs.io>
# Copyright (c) 2018 David Shah <dave@ds0.me>
# Copyright (c) 2020 Piotr Esden-Tempski <piotr@esden.net>
# Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# The iCEBreaker is the first open source iCE40 FPGA development board designed for teachers and
# students: https://www.crowdsupply.com/1bitsquared/icebreaker-fpga

# This target file provides a minimal LiteX SoC for the iCEBreaker with a CPU, its ROM (in SPI Flash),
# its SRAM, close to the others LiteX targets. A more complete example of LiteX SoC for the iCEBreaker
# with more features, examples to run C/Rust code on the RISC-V CPU and documentation can be found
# at: https://github.com/icebreaker-fpga/icebreaker-litex-examples

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex_boards.platforms import icebreaker

from litex.soc.cores.ram import Up5kSPRAM
from litex.soc.cores.clock import iCE40PLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.video import VideoDVIPHY
from litex.soc.cores.led import LedChaser

kB = 1024
mB = 1024*kB

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_sys = ClockDomain()
        self.clock_domains.cd_por = ClockDomain()

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
    def __init__(self, bios_flash_offset, sys_clk_freq=int(24e6), with_led_chaser=True,
                 with_video_terminal=False, **kwargs):
        platform = icebreaker.Platform()
        platform.add_extension(icebreaker.break_off_pmod)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        # Disable Integrated ROM/SRAM since too large for iCE40 and UP5K has specific SPRAM.
        kwargs["integrated_sram_size"] = 0
        kwargs["integrated_rom_size"]  = 0
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on iCEBreaker", **kwargs)

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
        from litespi.modules import W25Q128JV
        from litespi.opcodes import SpiNorFlashOpCodes as Codes
        self.add_spi_flash(mode="4x", module=W25Q128JV(Codes.READ_1_1_4), with_master=False)

        # Add ROM linker region --------------------------------------------------------------------
        self.bus.add_region("rom", SoCRegion(
            origin = self.bus.regions["spiflash"].origin + bios_flash_offset,
            size   = 32*kB,
            linker = True)
        )
        self.cpu.set_reset_address(self.bus.regions["rom"].origin)

        # Video ------------------------------------------------------------------------------------
        if with_video_terminal:
            platform.add_extension(icebreaker.dvi_pmod)
            self.submodules.videophy = VideoDVIPHY(platform.request("dvi"), clock_domain="sys")
            self.add_video_terminal(phy=self.videophy, timings="640x480@75Hz", clock_domain="sys")

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Flash --------------------------------------------------------------------------------------------

def flash(build_dir, build_name, bios_flash_offset):
    from litex.build.lattice.programmer import IceStormProgrammer
    prog = IceStormProgrammer()
    prog.flash(bios_flash_offset, f"{build_dir}/software/bios/bios.bin")
    prog.flash(0x00000000,        f"{build_dir}/gateware/{build_name}.bin")

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on iCEBreaker")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",               action="store_true", help="Build design.")
    target_group.add_argument("--load",                action="store_true", help="Load bitstream.")
    target_group.add_argument("--flash",               action="store_true", help="Flash Bitstream and BIOS.")
    target_group.add_argument("--sys-clk-freq",        default=24e6,        help="System clock frequency.")
    target_group.add_argument("--bios-flash-offset",   default="0x40000",   help="BIOS offset in SPI Flash.")
    target_group.add_argument("--with-video-terminal", action="store_true", help="Enable Video Terminal (with DVI PMOD).")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        bios_flash_offset   = int(args.bios_flash_offset, 0),
        sys_clk_freq        = int(float(args.sys_clk_freq)),
        with_video_terminal = args.with_video_terminal,
        **soc_core_argdict(args)
    )
    builder = Builder(soc, **builder_argdict(args))
    if args.build:
        builder.build()

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram", ext=".bin")) # FIXME

    if args.flash:
        flash(builder.output_dir, soc.build_name, args.bios_flash_offset)

if __name__ == "__main__":
    main()
