#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019 Antti Lukats <antti.lukats@gmail.com>
# Copyright (c) 2014-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import *

from litex_boards.platforms import trenz_cr00010

from litex.soc.cores.clock import CycloneVPLL
from litex.soc.cores.hyperbus import HyperRAM
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.soc import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litedram.modules import MT48LC4M16
from litedram.phy import GENSDRPHY

from litespi.modules import W74M64FV
from litespi.opcodes import SpiNorFlashOpCodes as Codes

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst       = Signal()
        self.cd_sys    = ClockDomain()
        self.cd_sys_ps = ClockDomain()

        # # #

        self.pll = pll = CycloneVPLL(speedgrade="-C8")
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(platform.request("clk12"), 12e6)
        pll.create_clkout(self.cd_sys,    sys_clk_freq)
        pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=90)

        self.comb += platform.request("sdram_clock").eq(self.cd_sys_ps.clk)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    mem_map = {**SoCCore.mem_map, **{
        "spiflash": 0x20000000,
    }}

    def __init__(self, sys_clk_freq=50e6,
        device          = "10M08SAU169C8G",
        with_hyperram   = True,
        with_led_chaser = True,
        with_sdram      = True,
        with_spi_flash  = False,
        **kwargs):
        platform = trenz_cr00010.Platform(device=device)

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on CR00010", **kwargs)

        # HyperRAM ---------------------------------------------------------------------------------
        if with_hyperram:
            self.hyperram = HyperRAM(platform.request("hyperram"), sys_clk_freq=sys_clk_freq)
            self.bus.add_slave("hyperram", slave=self.hyperram.bus, region=SoCRegion(
                origin = 0x30000000,
                size   = 8*MEGABYTE,
                mode   = "rwx",
            ))

        # SPI Flash --------------------------------------------------------------------------------
        if with_spi_flash:
            self.add_spi_flash(
                name        = "spiflash",
                mode        = "1x",
                module      = W74M64FV(Codes.READ_1_1_1),
                number      = 1,
                with_master = False,
            )

        # SDR SDRAM --------------------------------------------------------------------------------
        if with_sdram and not self.integrated_main_ram_size:
            self.sdrphy = GENSDRPHY(platform.request("sdram"), sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.sdrphy,
                module        = MT48LC4M16(sys_clk_freq, "1:1"),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Power Control ----------------------------------------------------------------------------
        pwr = platform.request("power_control")
        self.comb += [
            pwr.enable.eq(1),
            pwr.vid0.eq(0),
            pwr.vid1.eq(0),
            pwr.vid2.eq(0),
        ]

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=trenz_cr00010.Platform, description="LiteX SoC on CR00010.")
    parser.add_target_argument("--sys-clk-freq",    default=50e6, type=float,       help="System clock frequency.")
    parser.add_target_argument("--device",          default="10m08", choices=["10m08", "10m16"], help="FPGA device.")
    parser.add_target_argument("--no-hyperram",     action="store_true",            help="Disable HyperRAM support.")
    parser.add_target_argument("--no-sdram",        action="store_true",            help="Disable SDRAM support.")
    parser.add_target_argument("--with-spi-flash",  action="store_true",            help="Enable SPI flash support.")
    args = parser.parse_args()

    device = {
        "10m08": "10M08SAU169C8G",
        "10m16": "10M16SAU169C8G",
    }[args.device]

    soc = BaseSoC(
        sys_clk_freq   = args.sys_clk_freq,
        device         = device,
        with_hyperram  = not args.no_hyperram,
        with_sdram     = not args.no_sdram,
        with_spi_flash = args.with_spi_flash,
        **parser.soc_argdict
    )
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
