#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 Fin Maaß <f.maass@vogl-electronic.com>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import *

from litex_boards.platforms import efinix_tz170_j484_dev_kit

from litex.soc.integration.soc import *
from litex.soc.integration.builder import *

from litex.soc.cores.clock.efinix import *
from litex.soc.cores.ram.efinix_ddr import EfinixDDR, add_efinix_ddr

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, cpu_clk_freq):
        self.rst      = Signal()
        self.cd_sys   = ClockDomain()
        self.cd_cpu   = ClockDomain()
        self.cd_rst   = ClockDomain(reset_less=True)

        # # #

        # Clk/Rst.
        default_clk = platform.request(platform.default_clk_name)
        rst_n  = platform.request("user_btn_n", 0)

        self.comb += self.cd_rst.clk.eq(default_clk)

        # A pulse is necessary to do a reset.
        self.rst_pulse = Signal()
        last_rst = Signal()

        self.sync.rst += last_rst.eq(self.rst)
        self.sync.rst += self.rst_pulse.eq(~last_rst & self.rst)

        # PLL.
        self.pll = pll = TITANIUMPLL(platform)
        self.comb += pll.reset.eq(~rst_n | self.rst_pulse)
        pll.register_clkin(default_clk, platform.default_clk_freq)
        # You can use CLKOUT0 only for clocks with a maximum frequency of 4x
        # (integer) of the reference clock. If all your system clocks do not fall within
        # this range, you should dedicate one unused clock for CLKOUT0.
        pll.create_clkout(self.cd_sys, sys_clk_freq, with_reset=True)
        pll.create_clkout(self.cd_cpu, cpu_clk_freq)

        platform.add_false_path_constraints(self.cd_cpu.clk, self.cd_sys.clk)


class _CRG_DDR(LiteXModule):
    def __init__(self, platform):
        clk33 = platform.request("clk33")
        freq = 33.33e6

        # PLL.
        self.pll = pll = TITANIUMPLL(platform)
        self.comb += pll.reset.eq(ResetSignal())
        pll.register_clkin(clk33, freq)
        # You can use CLKOUT0 only for clocks with a maximum frequency of 4x
        # (integer) of the reference clock. If all your system clocks do not fall within
        # this range, you should dedicate one unused clock for CLKOUT0.
        pll.create_clkout(None,         freq)
        pll.create_clkout(None,         600e6, nclkout=4, margin=1e-02) # LPDDR4 ctrl


# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=100e6, cpu_clk_freq=175e6, with_spi_flash=False, spi_flash_number=0, spi_flash_rate="1:1", with_led_chaser=True, **kwargs):
        platform = efinix_tz170_j484_dev_kit.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, cpu_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Efinix Tz170 J484 Dev Kit", **kwargs)
        if hasattr(self.cpu, "cpu_clk"):
            self.comb += self.cpu.cpu_clk.eq(self.crg.cd_cpu.clk)

        # LPDDR4 SDRAM -----------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.ddr_crg = _CRG_DDR(platform)
            clock_domain = "cpu" if (
                hasattr(self.cpu, "add_memory_buses") and
                hasattr(self.cpu, "cpu_clk")
            ) else "sys"
            self.ddr = EfinixDDR(
                platform     = platform,
                clock_domain = clock_domain,
                **platform.ddr_config,
            )
            add_efinix_ddr(self, self.ddr, size=platform.ddr_size)

        # SPI Flash --------------------------------------------------------------------------------
        if with_spi_flash:
            from litespi.modules import MX25U25645G
            from litespi.opcodes import SpiNorFlashOpCodes as Codes

            self.add_spi_flash(mode="4x",
                            clk_freq=133e6,
                            number=spi_flash_number,
                            module=MX25U25645G(Codes.READ_1_1_4_4B),
                            with_master=True,
                            extra_latency=0.5,
                            rate=spi_flash_rate,
            )

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            from litex.soc.cores.led import LedChaser
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=efinix_tz170_j484_dev_kit.Platform, description="LiteX SoC on Efinix Tz170 J484 Dev Kit.")
    parser.add_target_argument("--flash",        action="store_true",       help="Flash bitstream.")
    parser.add_target_argument("--sys-clk-freq", default=100e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--cpu-clk-freq", default=175e6, type=float, help="CPU clock frequency.")
    sdopts = parser.target_group.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-sdcard",      action="store_true", help="Enable SPI-mode SDCard support.")
    sdopts.add_argument("--with-sdcard",          action="store_true", help="Enable SDCard support.")
    sdopts.add_argument("--with-sdcard-emulator", action="store_true", help="Enable SDCard (emulator) support.")
    parser.add_target_argument("--with-spi-flash",   action="store_true",                             help="Enable SPI Flash.")
    parser.add_target_argument("--spi-flash-number", default=0, type=int, choices=[0, 1],             help="SPI Flash number.")
    parser.add_target_argument("--spi-flash-rate",   default="1:2", type=str, choices=["1:1", "1:2"], help="SPI Flash rate.")
    parser.add_target_argument("--with-led-chaser",  action="store_true",                             help="Enable LED Chaser.")
    args = parser.parse_args()

    soc = BaseSoC(args.sys_clk_freq, args.cpu_clk_freq, args.with_spi_flash,
                  args.spi_flash_number, args.spi_flash_rate, args.with_led_chaser, **parser.soc_argdict)

    if args.with_spi_sdcard:
        soc.add_spi_sdcard()
    if args.with_sdcard:
        soc.add_sdcard()
    if args.with_sdcard_emulator:
        soc.add_sdcard(use_emulator=True)

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.flash(0, builder.get_bitstream_filename(mode="flash", ext=".hex"), device_id=0x00699A79)

if __name__ == "__main__":
    main()
