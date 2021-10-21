#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Franck Jullien <franck.jullien@collshade.fr>
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

import argparse

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex_boards.platforms import efinix_xyloni_dev_kit

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

# CRG ----------------------------------------------------------------------------------------------


class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.clock_domains.cd_sys = ClockDomain()

        # # #

        clk33 = platform.request("clk33")
        rst_n = platform.request("user_btn", 0)

        if sys_clk_freq == int(33.333e6):
            self.comb += self.cd_sys.clk.eq(clk33)
            self.specials += AsyncResetSynchronizer(self.cd_sys, ~rst_n)
        else:
            # PLL TODO: V1 simple pll not supported in infrastructure yet
            self.submodules.pll = pll = TRIONPLL(platform)
            self.comb += pll.reset.eq(~rst_n)
            pll.register_clkin(clk33, 33.333e6)
            pll.create_clkout(self.cd_sys, sys_clk_freq, with_reset=True)

# BaseSoC ------------------------------------------------------------------------------------------


class BaseSoC(SoCCore):
    mem_map = {**{"sram": 0x01000000}, **{"spiflash": 0x80000000}}

    def __init__(self, sys_clk_freq, bios_flash_offset, with_uartbone=False, with_spi_flash=False, with_led_chaser=True, **kwargs):
        platform = efinix_xyloni_dev_kit.Platform()

        # SoCCore ----------------------------------------------------------------------------------
        kwargs["integrated_sram_size"] = 0xC00
        # kwargs["integrated_rom_size"]  = 0x6000 # doesn't fit
        kwargs["integrated_rom_size"] = 0

        # Set CPU variant / reset address
        if with_spi_flash:
            kwargs["cpu_reset_address"] = self.mem_map["spiflash"] + \
                bios_flash_offset

        # Can probably only support minimal variant of vexriscv
        if kwargs.get("cpu_type", "vexriscv") == "vexriscv":
            kwargs["cpu_variant"] = "minimal"

        SoCCore.__init__(self, platform, sys_clk_freq,
                         ident="LiteX SoC on Efinix Xyloni Dev Kit",
                         ident_version=True,
                         integrated_rom_no_we=True,  # FIXME: Avoid this.
                         integrated_sram_no_we=True,  # FIXME: Avoid this.
                         integrated_main_ram_no_we=True,  # FIXME: Avoid this.
                         **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # SPI Flash --------------------------------------------------------------------------------
        if with_spi_flash:
            from litespi.modules import W25Q128JV
            from litespi.opcodes import SpiNorFlashOpCodes as Codes
            self.add_spi_flash(mode="1x", module=W25Q128JV(
                Codes.READ_1_1_1), with_master=True)

            # Add ROM linker region --------------------------------------------------------------------
            self.bus.add_region("rom", SoCRegion(
                origin=self.mem_map["spiflash"] + bios_flash_offset,
                size=32*1024,
                linker=True)
            )

        # UartBone ---------------------------------------------------------------------------------
        if with_uartbone:
            self.add_uartbone("serial", baudrate=1e6)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads=platform.request_all("user_led"),
                sys_clk_freq=sys_clk_freq)

# Build --------------------------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="LiteX SoC on Efinix Xyloni Dev Kit")
    parser.add_argument("--build", action="store_true", help="Build bitstream")
    parser.add_argument("--load",  action="store_true", help="Load bitstream")
    parser.add_argument("--flash", action="store_true", help="Flash Bitstream")
    # TODO: try a differnet frequency when PLL is supported
    parser.add_argument("--sys-clk-freq", default=33.333e6,
                        help="System clock frequency (default: 33.333MHz)")
    parser.add_argument("--with-uartbone",  action="store_true",
                        help="Enable Uartbone support")
    parser.add_argument("--with-spi-flash", action="store_true",
                        help="Enable SPI Flash (MMAPed)")
    parser.add_argument("--bios-flash-offset", default=0x40000,
                        help="BIOS offset in SPI Flash (default: 0x40000)")

    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        int(float(args.sys_clk_freq)),
        bios_flash_offset=args.bios_flash_offset,
        with_uartbone=args.with_uartbone,
        with_spi_flash=args.with_spi_flash,
        **soc_core_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(
            builder.gateware_dir, f"outflow/{soc.build_name}.bit"))

    if args.flash:
        from litex.build.openfpgaloader import OpenFPGALoader
        prog = OpenFPGALoader("xyloni_spi")
        prog.flash(0, os.path.join(builder.gateware_dir,
                   f"outflow/{soc.build_name}.hex"))


if __name__ == "__main__":
    main()
