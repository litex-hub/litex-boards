#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Andrew Gillham <gillham@roadsign.com>
# Copyright (c) 2014-2015 Sebastien Bourdeauducq <sb@m-labs.hk>
# Copyright (c) 2014-2020 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2014-2015 Yann Sionneau <ys@m-labs.hk>
# Copyright (c) 2020 Hans Baier <hansfbaier@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

# Board support for this chinese Kintex 420T board by "SITLINV FPGA Board Store"
# https://www.aliexpress.com/item/1005001631827738.html

import os

from migen import *

from litex.gen import *

from litex_boards.platforms import sitlinv_xc7k420t

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.bitbang import I2CMaster

from litedram.phy import s7ddrphy
from litedram.common import PHYPadsReducer
from litedram.modules import K4B1G0446F

from litepcie.phy.s7pciephy import S7PCIEPHY
from litepcie.software import generate_litepcie_software

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst          = Signal()
        self.cd_sys       = ClockDomain()
        self.cd_sys4x     = ClockDomain()
        self.cd_sys4x_dqs = ClockDomain()
        self.cd_idelay    = ClockDomain()

        # # #

        # Clk/Rst.
        clk100 = platform.request("clk100")
        rst_n  = platform.request("cpu_reset_n")

        # PLL.
        self.pll = pll = S7PLL(speedgrade=-2)
        self.comb += pll.reset.eq(~rst_n | self.rst)
        pll.register_clkin(clk100, 100e6)
        pll.create_clkout(self.cd_sys,       sys_clk_freq)
        pll.create_clkout(self.cd_sys4x,     4*sys_clk_freq)
        pll.create_clkout(self.cd_sys4x_dqs, 4*sys_clk_freq, phase=120)
        pll.create_clkout(self.cd_idelay,    200e6)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        self.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=100e6,
        io_voltage      = "3.3V",
        with_led_chaser = True,
        with_pcie       = False,
        with_sata       = False,
        **kwargs):
        platform = sitlinv_xc7k420t.Platform(io_voltage)

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on SITLINV XC7K420T", **kwargs)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            # we need to use A7DDRPHY instead of K7DDRPHY, because the 420T has no ODELAYE2
            self.ddrphy = s7ddrphy.A7DDRPHY(
                pads         = PHYPadsReducer(platform.request("ddram", 0), [0, 1, 2, 3]),
                #pads         = platform.request("ddram", 0),
                memtype      = "DDR3",
                nphases      = 4,
                sys_clk_freq = sys_clk_freq,
                iodelay_clk_freq = 200e6
            )
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = K4B1G0446F(sys_clk_freq, "1:4", "800"),
                l2_cache_size = kwargs.get("l2_size", 8192),
            )

        # PCIe -------------------------------------------------------------------------------------
        if with_pcie:
            self.pcie_phy = S7PCIEPHY(platform, platform.request("pcie_x4"),
                data_width = 128,
                bar0_size  = 0x20000)
            self.add_pcie(phy=self.pcie_phy, ndmas=1)

        # TODO verify / test
        # SATA -------------------------------------------------------------------------------------
        if with_sata:
            from litex.build.generic_platform import Subsignal, Pins
            from litesata.phy import LiteSATAPHY

            # RefClk, Generate 150MHz from PLL.
            self.cd_sata_refclk = ClockDomain()
            self.crg.pll.create_clkout(self.cd_sata_refclk, 150e6)
            sata_refclk = ClockSignal("sata_refclk")
            platform.add_platform_command("set_property SEVERITY {{Warning}} [get_drc_checks REQP-52]")

            # PHY
            self.sata_phy = LiteSATAPHY(platform.device,
                refclk     = sata_refclk,
                pads       = platform.request("sata", 0),
                gen        = "gen2",
                clk_freq   = sys_clk_freq,
                data_width = 16)

            # Core
            self.add_sata(phy=self.sata_phy, mode="read+write")

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led_n"),
                sys_clk_freq = sys_clk_freq)

        # I2C --------------------------------------------------------------------------------------
        self.i2c = I2CMaster(platform.request("i2c"))

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=sitlinv_xc7k420t.Platform, description="LiteX SoC on AliExpress SITLINV FPGA Store XC7K420T")
    parser.add_target_argument("--sys-clk-freq",    default=100e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--io-voltage",      default="3.3V",            help="IO voltage chosen by Jumper J3. Can be: '3.3V' or '2.5V'.")
    parser.add_target_argument("--with-pcie",       action="store_true",       help="Enable PCIe support.")
    parser.add_target_argument("--driver",          action="store_true",       help="Generate PCIe driver.")
    parser.add_target_argument("--with-sata",       action="store_true",       help="Enable SATA support.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq   = args.sys_clk_freq,
        io_voltage     = args.io_voltage,
        with_pcie      = args.with_pcie,
        with_sata      = args.with_sata,
        **parser.soc_argdict
    )
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.driver:
        generate_litepcie_software(soc, os.path.join(builder.output_dir, "driver"))

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
