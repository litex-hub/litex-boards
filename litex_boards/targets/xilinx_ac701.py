#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019 Vamsi K Vytla <vamsi.vytla@gmail.com>
# Copyright (c) 2019-2020 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

import os

from migen import *

from litex.gen import *

from litex_boards.platforms import xilinx_ac701

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litedram.common import PHYPadsReducer
from litedram.modules import MT8JTF12864
from litedram.phy import s7ddrphy

from liteeth.phy.a7_gtp import QPLLSettings, QPLL
from liteeth.phy.a7_1000basex import A7_1000BASEX
from liteeth.phy.s7rgmii import LiteEthPHYRGMII

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

        self.pll = pll = S7PLL(speedgrade=-1)
        self.comb += pll.reset.eq(platform.request("cpu_reset") | self.rst)
        pll.register_clkin(platform.request("clk200"), 200e6)
        pll.create_clkout(self.cd_sys,       sys_clk_freq)
        pll.create_clkout(self.cd_sys4x,     4*sys_clk_freq)
        pll.create_clkout(self.cd_sys4x_dqs, 4*sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_idelay,    200e6)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        self.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=100e6,
        with_ethernet   = False,
        eth_phy         = "rgmii",
        with_spi_flash  = False,
        with_led_chaser = True,
        with_pcie       = False,
        **kwargs):
        platform = xilinx_ac701.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on AC701", **kwargs)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.ddrphy = s7ddrphy.A7DDRPHY(
                pads         = PHYPadsReducer(platform.request("ddram"), [0, 1, 2, 3]),
                memtype      = "DDR3",
                nphases      = 4,
                sys_clk_freq = sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT8JTF12864(sys_clk_freq, "1:4"),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Ethernet ---------------------------------------------------------------------------------
        if with_ethernet:
            # RGMII Ethernet PHY -------------------------------------------------------------------
            if eth_phy == "rgmii":
                # phy
                self.ethphy = LiteEthPHYRGMII(
                    clock_pads = self.platform.request("eth_clocks"),
                    pads       = self.platform.request("eth"))

            # 1000BaseX Ethernet PHY ---------------------------------------------------------------
            if eth_phy == "1000basex":
                # phy
                self.comb += self.platform.request("sfp_mgt_clk_sel0", 0).eq(0)
                self.comb += self.platform.request("sfp_mgt_clk_sel1", 0).eq(0)
                self.comb += self.platform.request("sfp_tx_disable_n", 0).eq(0)
                qpll_settings = QPLLSettings(
                    refclksel  = 0b001,
                    fbdiv      = 4,
                    fbdiv_45   = 5,
                    refclk_div = 1)
                refclk125 = self.platform.request("gtp_refclk")
                refclk125_se = Signal()
                self.specials += \
                    Instance("IBUFDS_GTE2",
                        i_CEB = 0,
                        i_I   = refclk125.p,
                        i_IB  = refclk125.n,
                        o_O   = refclk125_se)
                qpll = QPLL(refclk125_se, qpll_settings)
                self.submodules += qpll
                self.ethphy = A7_1000BASEX(
                    qpll_channel = qpll.channels[0],
                    data_pads    = self.platform.request("sfp", 0),
                    sys_clk_freq = self.clk_freq)

            self.add_ethernet(phy=self.ethphy)

        # SPI Flash --------------------------------------------------------------------------------
        if with_spi_flash:
            from litespi.modules import N25Q256A
            from litespi.opcodes import SpiNorFlashOpCodes as Codes
            self.add_spi_flash(mode="4x", module=N25Q256A(Codes.READ_1_1_4), rate="1:1", with_master=True)

        # PCIe -------------------------------------------------------------------------------------
        if with_pcie:
            self.pcie_phy = S7PCIEPHY(platform, platform.request("pcie_x4"),
                data_width = 128,
                bar0_size  = 0x20000)
            self.add_pcie(phy=self.pcie_phy, ndmas=1)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------
def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=xilinx_ac701.Platform, description="LiteX SoC on AC701.")
    parser.add_target_argument("--sys-clk-freq",   default=100e6, type=float,  help="System clock frequency.")
    parser.add_target_argument("--with-ethernet",  action="store_true",        help="Enable Ethernet support.")
    parser.add_target_argument("--eth-phy",        default="rgmii",            help="Select Ethernet PHY (rgmii or 1000basex).")
    parser.add_target_argument("--with-spi-flash", action="store_true",        help="Enable SPI Flash (MMAPed).")
    parser.add_target_argument("--with-pcie",      action="store_true",        help="Enable PCIe support.")
    parser.add_target_argument("--driver",         action="store_true",        help="Generate PCIe driver.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq   = args.sys_clk_freq,
        with_ethernet  = args.with_ethernet,
        eth_phy        = args.eth_phy,
        with_spi_flash = args.with_spi_flash,
        with_pcie      = args.with_pcie,
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
