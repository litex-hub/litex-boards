#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Andrew Elbert Wilson <andrew.e.wilson@ieee.org>
# SPDX-License-Identifier: BSD-2-Clause

import os
import argparse

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex_boards.platforms import avnet_aesku40

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

from litedram.modules import EDY4016A
from litedram.phy import usddrphy

from liteeth.phy.usrgmii import LiteEthPHYRGMII

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_sys    = ClockDomain()
        self.clock_domains.cd_sys4x  = ClockDomain(reset_less=True)
        self.clock_domains.cd_pll4x  = ClockDomain(reset_less=True)
        self.clock_domains.cd_idelay = ClockDomain()
        self.clock_domains.cd_eth    = ClockDomain()

        # # #

        self.submodules.pll = pll = USMMCM(speedgrade=-2)
        self.comb += pll.reset.eq(platform.request("cpu_reset") | self.rst)
        pll.register_clkin(platform.request("clk250"), 250e6)
        pll.create_clkout(self.cd_pll4x, sys_clk_freq*4, buf=None, with_reset=False)
        pll.create_clkout(self.cd_idelay, 200e6)
        pll.create_clkout(self.cd_eth,    200e6)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        self.specials += [
            Instance("BUFGCE_DIV",
                p_BUFGCE_DIVIDE=4,
                i_CE=1, i_I=self.cd_pll4x.clk, o_O=self.cd_sys.clk),
            Instance("BUFGCE",
                i_CE=1, i_I=self.cd_pll4x.clk, o_O=self.cd_sys4x.clk),
        ]

        self.submodules.idelayctrl = USIDELAYCTRL(cd_ref=self.cd_idelay, cd_sys=self.cd_sys)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(125e6), with_ethernet=False, with_etherbone=False,
                 eth_ip="192.168.1.50", with_led_chaser=True, with_pcie=False, with_sata=False,
                 **kwargs):
        platform = avnet_aesku40.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on AESKU40", **kwargs)

        # Ethernet ---------------------------------------------------------------------------------
        if with_ethernet:
            self.submodules.ethphy = LiteEthPHYRGMII(
                clock_pads = self.platform.request("eth_clocks"),
                pads       = self.platform.request("eth"),
                tx_delay=1e-9, #Supported Delay with 200 MHz ref clk
                rx_delay=1e-9)

            # Change ref clk for IDELAYE3: FIXME: Allow it direclty in LiteEth?
            for special in self.ethphy.rx._fragment.specials:
                if special.name_override == "IDELAYE3":
                    for item in special.items:
                        if item.name == "REFCLK_FREQUENCY":
                            item.value=200.00
                            
            self.add_ethernet(phy=self.ethphy)

        # DDR4 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.submodules.ddrphy = usddrphy.USDDRPHY(platform.request("ddram"),
                memtype          = "DDR4",
                sys_clk_freq     = sys_clk_freq,
                iodelay_clk_freq = 200e6)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = EDY4016A(sys_clk_freq, "1:4"),
                size          = 0x40000000,
                l2_cache_size = kwargs.get("l2_size", 8192)
            )


# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on AESKU40")
    parser.add_argument("--build",         action="store_true", help="Build bitstream")
    parser.add_argument("--load",          action="store_true", help="Load bitstream")
    parser.add_argument("--sys-clk-freq",  default=125e6,       help="System clock frequency (default: 125MHz)")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq = int(float(args.sys_clk_freq)),
        **soc_core_argdict(args)
	)
    builder = Builder(soc, **builder_argdict(args))
    if args.build:
        builder.build()

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
