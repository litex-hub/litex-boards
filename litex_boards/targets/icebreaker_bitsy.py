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

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from litex_boards.platforms import icebreaker_bitsy

from litex.soc.cores.ram import Up5kSPRAM
from litex.soc.cores.clock import iCE40PLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser


kB = 1024
mB = 1024*kB

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq=48e6, with_usb_pll=False):
        assert not with_usb_pll or sys_clk_freq == 48e6

        self.rst    = Signal()
        self.cd_sys = ClockDomain()
        self.cd_por = ClockDomain()

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
        if with_usb_pll:
            self.cd_usb_12 = ClockDomain()
            self.cd_usb_48 = ClockDomain()
            locked = Signal()
            self.specials.pll = pll = Instance("SB_PLL40_2F_PAD",
                i_PACKAGEPIN    = clk12,
                i_RESETB        = rst_n,
                i_BYPASS        = C(0),

                # o_PLLOUTGLOBALA   = self.cd_sys.clk,
                o_PLLOUTGLOBALA   = self.cd_usb_48.clk,
                o_PLLOUTGLOBALB   = self.cd_usb_12.clk,
                o_LOCK            = locked,

                # Create a 48 MHz PLL clock...
                p_FEEDBACK_PATH = "SIMPLE",
                p_PLLOUT_SELECT_PORTA = "GENCLK",
                p_PLLOUT_SELECT_PORTB = "SHIFTREG_0deg",
                p_DIVR          = 0,
                p_DIVF          = 63,
                p_DIVQ          = 4,
                p_FILTER_RANGE  = 1,
            )
            self.specials += AsyncResetSynchronizer(self.cd_sys, ~por_done | ~locked)
            platform.add_period_constraint(self.cd_sys.clk, 48e6)
            platform.add_period_constraint(self.cd_usb_48.clk, 48e6)
            platform.add_period_constraint(self.cd_usb_12.clk, 12e6)
            self.comb += [
                self.cd_sys.clk.eq(self.cd_usb_48.clk),
            ]
        else:
            self.pll = pll = iCE40PLL(primitive="SB_PLL40_PAD")
            self.comb += pll.reset.eq(~rst_n) # FIXME: Add proper iCE40PLL reset support and add back | self.rst.
            pll.register_clkin(clk12, 12e6)
            pll.create_clkout(self.cd_sys, sys_clk_freq, with_reset=False)
            self.specials += AsyncResetSynchronizer(self.cd_sys, ~por_done | ~pll.locked)
            platform.add_period_constraint(self.cd_sys.clk, 1e9/sys_clk_freq)


# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, bios_flash_offset, sys_clk_freq=24e6, revision="v1", with_led_chaser=True, **kwargs):
        platform = icebreaker_bitsy.Platform(revision=revision)

        # CRG --------------------------------------------------------------------------------------
        with_usb_acm = kwargs["uart_name"] == "usb_acm"
        if with_usb_acm:
            sys_clk_freq = 48e6
        self.crg = _CRG(platform, sys_clk_freq, with_usb_pll=with_usb_acm)

        # SoCCore ----------------------------------------------------------------------------------
        # Disable Integrated ROM/SRAM since too large for iCE40 and UP5K has specific SPRAM.
        kwargs["integrated_sram_size"] = 0
        kwargs["integrated_rom_size"]  = 0
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on iCEBreaker-bitsy", **kwargs)

        # 128KB SPRAM (used as 64kB SRAM / 64kB RAM) -----------------------------------------------
        self.spram = Up5kSPRAM(size=128*kB)
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

        # LED Chaser --------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led_n"),
                sys_clk_freq = sys_clk_freq,
                polarity     = 1)

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

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=icebreaker_bitsy.Platform, description="LiteX SoC on iCEBreaker.")
    parser.add_target_argument("--flash",             action="store_true",      help="Flash bitstream and BIOS.")
    parser.add_target_argument("--sys-clk-freq",      default=24e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--bios-flash-offset", default="0xa0000",        help="BIOS offset in SPI Flash.")
    parser.add_target_argument("--revision",          default="v1",             help="Board revision (v0 or v1).")
    args = parser.parse_args()

    soc = BaseSoC(
        bios_flash_offset   = int(args.bios_flash_offset, 0),
        sys_clk_freq        = args.sys_clk_freq,
		revision            = args.revision,
        **parser.soc_argdict
    )
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.flash:
        from litex.build.dfu import DFUProg
        prog_gw = DFUProg(vid="1d50", pid="0x6146", alt=0)
        prog_sw = DFUProg(vid="1d50", pid="0x6146", alt=1)

        prog_gw.load_bitstream(builder.get_bitstream_filename(mode="sram", ext=".bin"), reset=False) # FIXME
        prog_sw.load_bitstream(builder.get_bios_filename())

if __name__ == "__main__":
    main()
