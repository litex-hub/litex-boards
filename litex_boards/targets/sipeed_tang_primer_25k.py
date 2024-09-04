#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2023 Gwenhael Goavec-Merou <gwenhael.goavec-merou@trabucayre.com>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import *

from litex.build.io import DDROutput

from litex.soc.cores.clock.gowin_gw5a import GW5APLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.gpio import GPIOIn

from litedram.modules import AS4C32M16, W9825G6KH6
from litedram.phy import GENSDRPHY, HalfRateGENSDRPHY

from litex_boards.platforms import sipeed_tang_primer_25k

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_sdram=False, sdram_rate="1:2"):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()
        self.cd_por = ClockDomain()
        if with_sdram:
            if sdram_rate == "1:2":
                self.cd_sys2x    = ClockDomain()
                self.cd_sys2x_ps = ClockDomain()
            else:
                self.cd_sys_ps = ClockDomain()

        # # #

        # Clk
        clk50 = platform.request("clk50")

        # Power on reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += [
            self.cd_por.clk.eq(clk50),
            por_done.eq(por_count == 0),
        ]
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # PLL
        self.pll = pll = GW5APLL(devicename=platform.devicename, device=platform.device)
        self.comb += pll.reset.eq(~por_done | self.rst)
        pll.register_clkin(clk50, 50e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)

        # SDRAM clock
        if with_sdram:
            if sdram_rate == "1:2":
                pll.create_clkout(self.cd_sys2x,    2*sys_clk_freq)
                pll.create_clkout(self.cd_sys2x_ps, 2*sys_clk_freq, phase=180)
                sdram_clk = ClockSignal("sys2x_ps")
            else:
                pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=90)
                sdram_clk = ClockSignal("sys_ps")
            self.specials += DDROutput(1, 0, platform.request("sdram_clock"), sdram_clk)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, toolchain="gowin", sys_clk_freq=50e6,
        with_spi_flash      = False,
        with_led_chaser     = True,
        with_buttons        = True,
        with_sdram          = False,
        sdram_model         = "sipeed",
        sdram_rate          = "1:2",
        **kwargs):

        platform = sipeed_tang_primer_25k.Platform(toolchain=toolchain)

        assert not with_sdram or (sdram_model in ["sipeed", "mister"])

        if with_sdram:
            platform.add_extension({
                "sipeed": sipeed_tang_primer_25k.sipeedSDRAM(),
                "mister": sipeed_tang_primer_25k.misterSDRAM}[sdram_model]
            )

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, with_sdram, sdram_rate)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Tang Primer 25K", **kwargs)

        # SDR SDRAM --------------------------------------------------------------------------------
        if with_sdram and not self.integrated_main_ram_size:
            module_cls = {
                "sipeed": W9825G6KH6,
                "mister": AS4C32M16}[sdram_model]
            if sdram_rate == "1:2":
                sdrphy_cls = HalfRateGENSDRPHY
            else:
                sdrphy_cls = GENSDRPHY
            self.sdrphy = sdrphy_cls(platform.request("sdram"), sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.sdrphy,
                module        = module_cls(sys_clk_freq, sdram_rate),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # SPI Flash --------------------------------------------------------------------------------
        if with_spi_flash:
            from litespi.modules import W25Q64FV as SpiFlashModule
            from litespi.opcodes import SpiNorFlashOpCodes as Codes
            self.add_spi_flash(mode="1x", module=SpiFlashModule(Codes.READ_1_1_1))

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("led"),
                sys_clk_freq = sys_clk_freq
            )

        # Buttons ----------------------------------------------------------------------------------
        if with_buttons:
            self.buttons = GPIOIn(pads=~platform.request_all("btn_n"))


# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=sipeed_tang_primer_25k.Platform, description="LiteX SoC on Tang Primer 25K.")
    parser.add_target_argument("--flash",           action="store_true",      help="Flash Bitstream.")
    parser.add_target_argument("--sys-clk-freq",    default=50e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-spi-flash",  action="store_true",      help="Enable SPI Flash (MMAPed).")
    parser.add_target_argument("--with-sdram",      action="store_true",      help="Enable optional SDRAM module.")
    parser.add_target_argument("--sdram-model",     default="sipeed",         help="SDRAM module model.",
        choices=[
            "sipeed",
            "mister"
    ])
    args = parser.parse_args()

    soc = BaseSoC(
        toolchain      = args.toolchain,
        sys_clk_freq   = args.sys_clk_freq,
        with_spi_flash = args.with_spi_flash,
        with_sdram     = args.with_sdram,
        sdram_model    = args.sdram_model,
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
