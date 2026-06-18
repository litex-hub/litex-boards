#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from litex_boards.platforms import trenz_tel0025

from litex.soc.cores.clock import *
from litex.soc.cores.led import LedChaser
from litex.soc.integration.soc import *
from litex.soc.integration.builder import *

# Constants ----------------------------------------------------------------------------------------

_HYPERRAM_SIZE  = 32*MEGABYTE
_OPENSBI_OFFSET = 0x00f00000
_OPENSBI_SIZE   = 0x00080000

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()
        self.cd_por = ClockDomain()

        # # #

        # Clk / Rst
        clk25      = platform.request("clk25")
        user_btn_n = platform.request("user_btn_n")

        # Built-in oscillator for power-on reset.
        self.hf_clk = NXOSCA(platform)
        self.hf_clk.create_hf_clk(self.cd_por, 25e6)

        # Power-on reset.
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))
        self.specials += AsyncResetSynchronizer(self.cd_por, ~user_btn_n)

        # PLL.
        self.sys_pll = sys_pll = NXPLL(platform=platform, create_output_port_clocks=True)
        self.comb += sys_pll.reset.eq(self.rst | ~por_done)
        sys_pll.register_clkin(clk25, 25e6)
        sys_pll.create_clkout(self.cd_sys, sys_clk_freq)
        self.specials += AsyncResetSynchronizer(self.cd_sys, ~sys_pll.locked)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=75e6, toolchain="radiant",
        with_hyperram       = True,
        with_led_chaser     = True,
        with_sdcard         = False,
        with_spi_sdcard     = False,
        with_spi_flash      = False,
        **kwargs):
        platform = trenz_tel0025.Platform(toolchain=toolchain)

        # Linux -----------------------------------------------------------------------------------
        # The SMP/Vexii Linux variants place OpenSBI at main_ram + 0x00f00000.
        main_ram_size = kwargs.get("integrated_main_ram_size", 0) or 0
        if with_hyperram and not main_ram_size:
            main_ram_size = _HYPERRAM_SIZE
        cpu_type    = kwargs.get("cpu_type", "vexriscv")
        cpu_variant = kwargs.get("cpu_variant", None) or "standard"
        with_opensbi = (
            (cpu_type == "vexriscv_smp" and cpu_variant == "linux") or
            (cpu_type == "vexiiriscv"   and cpu_variant in ["linux", "debian"])
        )
        if with_opensbi and main_ram_size < (_OPENSBI_OFFSET + _OPENSBI_SIZE):
            raise ValueError(
                "vexriscv_smp/vexiiriscv Linux variants place OpenSBI at "
                "main_ram + 0x00f00000; provide at least 16MiB of main RAM "
                "or use vexriscv linux instead."
            )

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Trenz TEL0025", **kwargs)

        # HyperRAM ---------------------------------------------------------------------------------
        if with_hyperram and not self.integrated_main_ram_size:
            self.add_hyperram(
                region_name  = "main_ram",
                latency      = 7,
                latency_mode = "variable",
                clk_ratio    = "4:1",
                size         = _HYPERRAM_SIZE,
            )

        # SPI Flash --------------------------------------------------------------------------------
        if with_spi_flash:
            from litespi.modules import MT25QL256A
            from litespi.opcodes import SpiNorFlashOpCodes as Codes
            self.add_spi_flash(
                mode        = "4x",
                module      = MT25QL256A(Codes.READ_1_1_4),
                with_master = False,
            )

        # SDCard -----------------------------------------------------------------------------------
        if with_sdcard:
            self.add_sdcard()
        if with_spi_sdcard:
            self.add_spi_sdcard()

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq,
                polarity     = 1,
            )

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=trenz_tel0025.Platform, description="LiteX SoC on Trenz TEL0025.")
    parser.add_target_argument("--sys-clk-freq",   default=75e6,       type=float, help="System clock frequency.")
    parser.add_target_argument("--no-hyperram",    action="store_true",            help="Disable HyperRAM support.")
    parser.add_target_argument("--with-spi-flash", action="store_true",            help="Enable SPI Flash support.")
    parser.add_target_argument("--flash",          action="store_true",            help="Flash bitstream to SPI Flash.")
    sdopts = parser.target_group.add_mutually_exclusive_group()
    sdopts.add_argument("--with-sdcard",     action="store_true", help="Enable SDCard support.")
    sdopts.add_argument("--with-spi-sdcard", action="store_true", help="Enable SPI-mode SDCard support.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq    = args.sys_clk_freq,
        toolchain       = args.toolchain,
        with_hyperram   = not args.no_hyperram,
        with_sdcard     = args.with_sdcard,
        with_spi_sdcard = args.with_spi_sdcard,
        with_spi_flash  = args.with_spi_flash,
        **parser.soc_argdict
    )

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.flash(0, builder.get_bitstream_filename(mode="flash"), external=True)

if __name__ == "__main__":
    main()
