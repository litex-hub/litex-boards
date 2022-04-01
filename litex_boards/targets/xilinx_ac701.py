#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019 Vamsi K Vytla <vamsi.vytla@gmail.com>
# Copyright (c) 2019-2020 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

import os

from migen import *

from litex_boards.platforms import ac701

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

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_sys       = ClockDomain()
        self.clock_domains.cd_sys4x     = ClockDomain()
        self.clock_domains.cd_sys4x_dqs = ClockDomain()
        self.clock_domains.cd_idelay    = ClockDomain()

        # # #

        self.submodules.pll = pll = S7PLL(speedgrade=-1)
        self.comb += pll.reset.eq(platform.request("cpu_reset") | self.rst)
        pll.register_clkin(platform.request("clk200"), 200e6)
        pll.create_clkout(self.cd_sys,       sys_clk_freq)
        pll.create_clkout(self.cd_sys4x,     4*sys_clk_freq)
        pll.create_clkout(self.cd_sys4x_dqs, 4*sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_idelay,    200e6)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        self.submodules.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(100e6), with_ethernet=False, eth_phy="rgmii",
                 with_led_chaser=True, with_pcie=False, **kwargs):
        platform = ac701.Platform()

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident = "LiteX SoC on AC701",
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.submodules.ddrphy = s7ddrphy.A7DDRPHY(
                pads         = PHYPadsReducer(platform.request("ddram"), [0, 1, 2, 3]),
                memtype      = "DDR3",
                nphases      = 4,
                sys_clk_freq = sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT8JTF12864(sys_clk_freq, "1:4"),
                size          = 0x40000000,
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Ethernet ---------------------------------------------------------------------------------
        if with_ethernet:
            # RGMII Ethernet PHY -------------------------------------------------------------------
            if eth_phy == "rgmii":
                # phy
                self.submodules.ethphy = LiteEthPHYRGMII(
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
                self.submodules.ethphy = A7_1000BASEX(
                    qpll_channel = qpll.channels[0],
                    data_pads    = self.platform.request("sfp", 0),
                    sys_clk_freq = self.clk_freq)

            self.add_ethernet(phy=self.ethphy)

        # PCIe -------------------------------------------------------------------------------------
        if with_pcie:
            self.submodules.pcie_phy = S7PCIEPHY(platform, platform.request("pcie_x4"),
                data_width = 128,
                bar0_size  = 0x20000)
            self.add_pcie(phy=self.pcie_phy, ndmas=1)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------
def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on AC701")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",         action="store_true", help="Build bitstream.")
    target_group.add_argument("--load",          action="store_true", help="Load bitstream.")
    target_group.add_argument("--sys-clk-freq",  default=100e6,       help="System clock frequency.")
    target_group.add_argument("--with-ethernet", action="store_true", help="Enable Ethernet support.")
    target_group.add_argument("--eth-phy",       default="rgmii",     help="Select Ethernet PHY (rgmii or 1000basex).")
    target_group.add_argument("--with-pcie",     action="store_true", help="Enable PCIe support.")
    target_group.add_argument("--driver",        action="store_true", help="Generate PCIe driver.")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq  = int(float(args.sys_clk_freq)),
        with_ethernet = args.with_ethernet,
        eth_phy       = args.eth_phy,
        with_pcie     = args.with_pcie,
        **soc_core_argdict(args)
    )
    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.driver:
        generate_litepcie_software(soc, os.path.join(builder.output_dir, "driver"))

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
