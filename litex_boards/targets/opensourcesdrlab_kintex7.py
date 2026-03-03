#!/usr/bin/env python3
#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2023 Kazumoto Kojima
# Copyright (c) 2023 Hans Baier <hansfbaier@gmail.com>
#
# SPDX-License-Identifier: BSD-2-Clause

import os
from migen import *

from litex_boards.platforms import opensourcesdrlab_kintex7

from litex.soc.cores.clock import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.video import VideoVGAPHY
from litex.soc.cores.led import LedChaser

from litedram.modules import MT41K256M16
from litedram.phy import s7ddrphy
from litepcie.phy.s7pciephy import S7PCIEPHY

from liteeth.phy.mii import LiteEthPHYMII

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_sys       = ClockDomain()
        self.clock_domains.cd_sys4x     = ClockDomain(reset_less=True)
        self.clock_domains.cd_sys4x_dqs = ClockDomain(reset_less=True)
        self.clock_domains.cd_idelay    = ClockDomain()

        # # #

        self.submodules.pll = pll = S7PLL(speedgrade=-2)
        reset_button = platform.request("user_btn", 0)
        self.comb += pll.reset.eq(~reset_button | self.rst)

        pll.register_clkin(platform.request("clk50"), 50e6)
        pll.create_clkout(self.cd_sys,       sys_clk_freq)
        pll.create_clkout(self.cd_sys4x,     4*sys_clk_freq)
        pll.create_clkout(self.cd_sys4x_dqs, 4*sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_idelay,    200e6)

        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        self.submodules.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, toolchain="vivado", sys_clk_freq=int(100e6), with_led_chaser=True, with_spi_flash=False, with_pcie=False, **kwargs):
        platform = opensourcesdrlab_kintex7.Platform(toolchain=toolchain)

        # SoCCore ----------------------------------------------------------------------------------
        if kwargs.get("uart_name", "serial") == "serial": kwargs["uart_name"] = "serial"
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident = "Open Source SDR LAB XC7K325T",
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.ddrphy = s7ddrphy.K7DDRPHY(platform.request("ddram"),
                memtype      = "DDR3",
                nphases      = 4,
                sys_clk_freq = sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT41K256M16(sys_clk_freq, "1:4"),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

                # SPI Flash --------------------------------------------------------------------------------
        if with_spi_flash:
            from litespi.modules import MT25QL256
            from litespi.opcodes import SpiNorFlashOpCodes as Codes
            self.add_spi_flash(mode="4x", module=MT25QL256(Codes.READ_1_1_1), with_master=True)

                # PCIe -------------------------------------------------------------------------------------
        if with_pcie:
            self.pcie_phy = S7PCIEPHY(platform, platform.request("pcie_x4"),
                data_width = 128,
                bar0_size  = 0x20000)
            self.add_pcie(phy=self.pcie_phy, ndmas=1)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led")[:8],
                sys_clk_freq = sys_clk_freq,
            )

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=opensourcesdrlab_kintex7.Platform, description="LiteX SoC on Open Source SDR Lab Kintex-7.")
    parser.add_target_argument("--sys-clk-freq", default=100e6, type=float, help="System clock frequency.")

    parser.add_target_argument("--with-pcie",       action="store_true", help="Enable PCIe support.")
    parser.add_target_argument("--with-spi-sdcard", action="store_true", help="Enable SPI-mode SDCard support.")
    parser.add_target_argument("--with-spi-flash",  action="store_true", help="Enable memory-mapped SPI flash.")
    args = parser.parse_args()

    soc = BaseSoC(
        toolchain       = args.toolchain,
        sys_clk_freq    = int(float(args.sys_clk_freq)),
        with_spi_flash  = args.with_spi_flash,
        with_pcie       = args.with_pcie,
        with_spi_sdcard = args.with_spi_sdcard,
        **parser.soc_argdict
    )

    if args.with_spi_sdcard:
        soc.add_spi_sdcard()

    builder = Builder(soc, **parser.builder_argdict)

    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
