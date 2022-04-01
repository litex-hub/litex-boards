#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Hans Baier <hansfbaier@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

# iCESugar FPGA: https://www.aliexpress.com/item/4001201771358.html

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex_boards.platforms import muselab_icesugar

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
        self.rst = Signal()
        self.clock_domains.cd_sys = ClockDomain()
        self.clock_domains.cd_por = ClockDomain()

        # # #

        # Clk/Rst
        clk12 = platform.request("clk12")

        # Power On Reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += self.cd_por.clk.eq(ClockSignal())
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # PLL
        self.submodules.pll = pll = iCE40PLL(primitive="SB_PLL40_PAD")
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk12, 12e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq, with_reset=False)
        self.specials += AsyncResetSynchronizer(self.cd_sys, ~por_done | ~pll.locked)
        platform.add_period_constraint(self.cd_sys.clk, 1e9/sys_clk_freq)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, bios_flash_offset, sys_clk_freq=int(24e6), with_led_chaser=True,
                 with_video_terminal=False, **kwargs):
        platform = muselab_icesugar.Platform()

        # Disable Integrated ROM/SRAM since too large for iCE40 and UP5K has specific SPRAM.
        kwargs["integrated_sram_size"] = 0
        kwargs["integrated_rom_size"]  = 0

        # Set CPU variant
        if kwargs.get("cpu_type", "vexriscv") == "vexriscv":
            kwargs["cpu_variant"] = "lite"

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident = "LiteX SoC on Muselab iCESugar",
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # 128KB SPRAM (used as SRAM) ---------------------------------------------------------------
        self.submodules.spram = Up5kSPRAM(size=64*kB)
        self.bus.add_slave("sram", self.spram.bus, SoCRegion(size=64*kB))

        # SPI Flash --------------------------------------------------------------------------------
        from litespi.modules import W25Q64FV
        from litespi.opcodes import SpiNorFlashOpCodes as Codes
        self.add_spi_flash(mode="1x", module=W25Q64FV(Codes.READ_1_1_1), with_master=False)

        # Add ROM linker region --------------------------------------------------------------------
        self.bus.add_region("rom", SoCRegion(
            origin = self.bus.regions["spiflash"].origin + bios_flash_offset,
            size   = 32*kB,
            linker = True)
        )
        self.cpu.set_reset_address(self.bus.regions["rom"].origin)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            led_pads = platform.request_all("user_led_n")
            self.submodules.leds = LedChaser(
                pads         = led_pads,
                sys_clk_freq = sys_clk_freq)

# Flash --------------------------------------------------------------------------------------------

def flash(bios_flash_offset):
    from litex.build.lattice.programmer import IceSugarProgrammer
    prog = IceSugarProgrammer()
    prog.flash(bios_flash_offset, "build/muselab_icesugar/software/bios/bios.bin")
    prog.flash(0x00000000,        "build/muselab_icesugar/gateware/muselab_icesugar.bin")

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on iCEBreaker")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",               action="store_true", help="Build bitstream.")
    target_group.add_argument("--load",                action="store_true", help="Load bitstream.")
    target_group.add_argument("--flash",               action="store_true", help="Flash Bitstream.")
    target_group.add_argument("--sys-clk-freq",        default=24e6,        help="System clock frequency.")
    target_group.add_argument("--bios-flash-offset",   default="0x40000",   help="BIOS offset in SPI Flash.")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        bios_flash_offset   = int(args.bios_flash_offset, 0),
        sys_clk_freq        = int(float(args.sys_clk_freq)),
        **soc_core_argdict(args)
    )
    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram", ext=".bin")) # FIXME

    if args.flash:
        flash(int(args.bios_flash_offset, 0))

if __name__ == "__main__":
    main()
