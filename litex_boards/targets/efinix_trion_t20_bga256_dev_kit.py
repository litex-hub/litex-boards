#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Miodrag Milanovic <mmicko@gmail.com>
# Copyright (c) 2021 Franck Jullien <franck.jullien@collshade.fr>
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from litex_boards.platforms import efinix_trion_t20_bga256_dev_kit

from litex.build.io import ClkOutput
from litex.build.generic_platform import *

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litex.gen.genlib.misc import WaitTimer

from litedram.modules import NDS36PT5
from litedram.phy import GENSDRPHY

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst       = Signal()
        self.cd_sys    = ClockDomain()
        self.cd_sys_ps = ClockDomain()
        self.cd_rst    = ClockDomain(reset_less=True)

        # # #

        # Clk/Rst.
        clk50 = platform.request("clk50")
        rst_n = platform.request("user_btn", 0)

        self.comb += self.cd_rst.clk.eq(clk50)

        # A pulse is necessary to do a reset.
        self.rst_pulse = Signal()
        self.reset_timer = reset_timer = ClockDomainsRenamer("rst")(WaitTimer(25e-6*platform.default_clk_freq))
        self.comb += self.rst_pulse.eq(self.rst ^ reset_timer.done)
        self.comb += reset_timer.wait.eq(self.rst)

        # PLL.
        self.pll = pll = TRIONPLL(platform)
        self.comb += pll.reset.eq(~rst_n | self.rst_pulse)
        pll.register_clkin(clk50, platform.default_clk_freq)
        pll.create_clkout(self.cd_sys, sys_clk_freq, with_reset=True)
        pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=180)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=100e6, with_spi_flash=False, with_led_chaser=True, **kwargs):
        platform = efinix_trion_t20_bga256_dev_kit.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Efinix Trion T20 BGA256 Dev Kit", **kwargs)

        # SDR SDRAM --------------------------------------------------------------------------------
        if not self.integrated_main_ram_size and sys_clk_freq <= 50e6 :
            self.specials += ClkOutput(ClockSignal("sys_ps"), platform.request("sdram_clock"))

            self.sdrphy = GENSDRPHY(platform.request("sdram"), sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.sdrphy,
                module        = NDS36PT5(sys_clk_freq, "1:1"),
                l2_cache_size = kwargs.get("l2_size", 8192),
                with_bist     = kwargs.get("with_bist", False)
            )

        # SPI Flash --------------------------------------------------------------------------------
        if with_spi_flash:
            from litespi.modules import W25Q32JV
            from litespi.opcodes import SpiNorFlashOpCodes as Codes
            self.add_spi_flash(mode="1x", module=W25Q32JV(Codes.READ_1_1_1), with_master=True)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=efinix_trion_t20_bga256_dev_kit.Platform, description="LiteX SoC on Efinix Trion T20 BGA256 Dev Kit.")
    parser.add_target_argument("--flash",          action="store_true",             help="Flash bitstream.")
    parser.add_target_argument("--sys-clk-freq",   default=45e6,        type=float, help="System clock frequency.")
    parser.add_target_argument("--with-spi-flash", action="store_true",             help="Enable SPI Flash (MMAPed).")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq   = args.sys_clk_freq,
        with_spi_flash = args.with_spi_flash,
         **parser.soc_argdict)
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        from litex.build.openfpgaloader import OpenFPGALoader
        prog = OpenFPGALoader("trion_t120_bga576")
        prog.flash(0, builder.get_bitstream_filename(mode="flash", ext=".hex")) # FIXME

if __name__ == "__main__":
    main()
