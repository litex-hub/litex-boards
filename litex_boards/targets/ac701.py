#!/usr/bin/env python3

# This file is Copyright (c) 2019 Vamsi K Vytla <vamsi.vytla@gmail.com>
# This file is Copyright (c) 2019 Florent Kermarrec <florent@enjoy-digital.fr>
# License: BSD

import argparse

from migen import *

from litex_boards.platforms import ac701

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc_sdram import *
from litex.soc.integration.builder import *

from litedram.modules import MT8JTF12864
from litedram.phy import s7ddrphy

from liteeth.phy.a7_gtp import QPLLSettings, QPLL
from liteeth.phy.a7_1000basex import A7_1000BASEX
from liteeth.phy.s7rgmii import LiteEthPHYRGMII
from liteeth.mac import LiteEthMAC

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.clock_domains.cd_sys       = ClockDomain()
        self.clock_domains.cd_sys4x     = ClockDomain(reset_less=True)
        self.clock_domains.cd_sys4x_dqs = ClockDomain(reset_less=True)
        self.clock_domains.cd_clk200    = ClockDomain()

        # # #

        self.submodules.pll = pll = S7PLL(speedgrade=-1)
        self.comb += pll.reset.eq(platform.request("cpu_reset"))
        pll.register_clkin(platform.request("clk200"), 200e6)
        pll.create_clkout(self.cd_sys,       sys_clk_freq)
        pll.create_clkout(self.cd_sys4x,     4*sys_clk_freq)
        pll.create_clkout(self.cd_sys4x_dqs, 4*sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_clk200,    200e6)

        self.submodules.idelayctrl = S7IDELAYCTRL(self.cd_clk200)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(100e6), **kwargs):
        platform = ac701.Platform()

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, clk_freq=sys_clk_freq, **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.submodules.ddrphy = s7ddrphy.A7DDRPHY(platform.request("ddram"),
                memtype      = "DDR3",
                nphases      = 4,
                sys_clk_freq = sys_clk_freq)
            self.add_csr("ddrphy")
            self.add_sdram("sdram",
                phy                     = self.ddrphy,
                module                  = MT8JTF12864(sys_clk_freq, "1:4"),
                origin                  = self.mem_map["main_ram"],
                size                    = kwargs.get("max_sdram_size", 0x40000000),
                l2_cache_size           = kwargs.get("l2_size", 8192),
                l2_cache_min_data_width = kwargs.get("min_l2_data_width", 128),
                l2_cache_reverse        = True
            )

# EthernetSoC --------------------------------------------------------------------------------------

class EthernetSoC(BaseSoC):
    mem_map = {
        "ethmac": 0xb0000000,
    }
    mem_map.update(BaseSoC.mem_map)

    def __init__(self, phy="rgmii", **kwargs):
        assert phy in ["rgmii", "1000basex"]
        BaseSoC.__init__(self, **kwargs)

        # RGMII Ethernet PHY -----------------------------------------------------------------------
        if phy == "rgmii":
            # phy
            self.submodules.ethphy = LiteEthPHYRGMII(
                clock_pads = self.platform.request("eth_clocks"),
                pads       = self.platform.request("eth"))
            self.add_csr("ethphy")
            # timing constraints
            self.platform.add_period_constraint(self.ethphy.crg.cd_eth_rx.clk, 1e9/125e6)
            self.platform.add_period_constraint(self.ethphy.crg.cd_eth_tx.clk, 1e9/125e6)
            self.platform.add_false_path_constraints(
                self.crg.cd_sys.clk,
                self.ethphy.crg.cd_eth_rx.clk,
                self.ethphy.crg.cd_eth_tx.clk)

        # 1000BaseX Ethernet PHY -------------------------------------------------------------------
        if phy == "1000basex":
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
            self.submodules.ethphy = A7_1000BASEX(qpll.channels[0], self.platform.request("sfp", 0), self.clk_freq)
            # timing constraints
            self.platform.add_period_constraint(self.ethphy.txoutclk, 1e9/62.5e6)
            self.platform.add_period_constraint(self.ethphy.rxoutclk, 1e9/62.5e6)
            self.platform.add_false_path_constraints(
                self.crg.cd_sys.clk,
                self.ethphy.txoutclk,
                self.ethphy.rxoutclk)

        # Ethernet MAC -----------------------------------------------------------------------------
        self.submodules.ethmac = LiteEthMAC(
            phy        = self.ethphy,
            dw         = 32,
            interface  = "wishbone",
            endianness = self.cpu.endianness)
        self.add_memory_region("ethmac", self.mem_map["ethmac"], 0x2000, type="io")
        self.add_wb_slave(self.mem_map["ethmac"], self.ethmac.bus, 0x2000)
        self.add_csr("ethmac")
        self.add_interrupt("ethmac")

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on AC701")
    builder_args(parser)
    soc_sdram_args(parser)
    parser.add_argument("--with-ethernet", action="store_true",
                        help="enable Ethernet support")
    parser.add_argument("--ethernet-phy", default="rgmii",
                        help="select Ethernet PHY (rgmii or 1000basex)")
    args = parser.parse_args()

    if args.with_ethernet:
        soc = EthernetSoC(args.ethernet_phy, **soc_sdram_argdict(args))
    else:
        soc = BaseSoC(**soc_sdram_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder.build()


if __name__ == "__main__":
    main()
