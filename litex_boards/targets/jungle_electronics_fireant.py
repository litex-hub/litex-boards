#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Miodrag Milanovic <mmicko@gmail.com>
# Copyright (c) 2021 Andrew Dennison <andrew@motec.com.au>
# Copyright (c) 2021 Franck Jullien <franck.jullien@collshade.fr>
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex_boards.platforms import jungle_electronics_fireant

from litex.build.generic_platform import *

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion

from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

kB = 1024
mB = 1024*kB

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.clock_domains.cd_sys = ClockDomain()

        # # #

        clk33 = platform.request("clk33")
        rst_n = platform.request("user_btn", 0)

        # PLL.
        self.submodules.pll = pll = TRIONPLL(platform)
        self.comb += pll.reset.eq(~rst_n)
        pll.register_clkin(clk33, 33.333e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq, with_reset=True)

# Default peripherals
serial = [
    ("serial", 0,
        Subsignal("tx", Pins("J2:2")),
        Subsignal("rx", Pins("J2:3")),
        IOStandard("3.3_V_LVTTL_/_LVCMOS") , Misc("WEAK_PULLUP")
    )
]

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    mem_map = {**SoCCore.mem_map, **{"spiflash": 0x80000000}}
    def __init__(self, bios_flash_offset, sys_clk_freq, with_led_chaser=True, **kwargs):
        platform = jungle_electronics_fireant.Platform()
        platform.add_extension(serial)

        # Disable Integrated ROM since too large for this device.
        kwargs["integrated_rom_size"]  = 0

        # Set CPU variant / reset address
        if kwargs.get("cpu_type", "vexriscv") == "vexriscv":
            kwargs["cpu_variant"] = "minimal"
        kwargs["cpu_reset_address"] = self.mem_map["spiflash"] + bios_flash_offset

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident = "LiteX SoC on Jungle Electronics FireAnt",
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # SPI Flash --------------------------------------------------------------------------------
        from litespi.modules import W25Q80BV
        from litespi.opcodes import SpiNorFlashOpCodes as Codes
        # Board is using W25Q80DV, which is replacemenet for W25Q80BV
        self.add_spi_flash(mode="1x", module=W25Q80BV(Codes.READ_1_1_1), with_master=False)

        # Add ROM linker region --------------------------------------------------------------------
        self.bus.add_region("rom", SoCRegion(
            origin = self.mem_map["spiflash"] + bios_flash_offset,
            size   = 32*kB,
            linker = True)
        )

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------


def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on Jungle Electronics FireAnt")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build", action="store_true",           help="Build bitstream.")
    target_group.add_argument("--load",  action="store_true",           help="Load bitstream.")
    target_group.add_argument("--flash", action="store_true",           help="Flash Bitstream.")
    target_group.add_argument("--sys-clk-freq",      default=33.333e6,  help="System clock frequency.")
    target_group.add_argument("--bios-flash-offset", default="0x40000", help="BIOS offset in SPI Flash.")

    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        bios_flash_offset = int(args.bios_flash_offset, 0),
        sys_clk_freq      = int(float(args.sys_clk_freq)),
        **soc_core_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.flash(0, builder.get_bitstream_filename(mode="flash", ext=".hex")) # FIXME
        prog.flash(args.bios_flash_offset, builder.get_bios_filename())

if __name__ == "__main__":
    main()
