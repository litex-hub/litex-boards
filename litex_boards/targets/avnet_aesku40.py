#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Andrew Elbert Wilson <andrew.e.wilson@ieee.org>
# SPDX-License-Identifier: BSD-2-Clause

import os

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from litex_boards.platforms import avnet_aesku40

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

from litedram.modules import EDY4016A
from litedram.phy import usddrphy

from liteeth.phy.usrgmii import LiteEthPHYRGMII

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst       = Signal()
        self.cd_sys    = ClockDomain()
        self.cd_sys4x  = ClockDomain(reset_less=True)
        self.cd_pll4x  = ClockDomain(reset_less=True)
        self.cd_idelay = ClockDomain()
        self.cd_eth    = ClockDomain()

        # # #

        self.pll = pll = USMMCM(speedgrade=-2)
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

        self.idelayctrl = USIDELAYCTRL(cd_ref=self.cd_idelay, cd_sys=self.cd_sys)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=125e6,
        with_ethernet   = False,
        with_etherbone  = False,
        eth_ip          = "192.168.1.50",
        with_led_chaser = True,
        with_pcie       = False,
        with_sata       = False,
        **kwargs):
        platform = avnet_aesku40.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on AESKU40", **kwargs)

        # Ethernet ---------------------------------------------------------------------------------
        if with_ethernet:
            self.ethphy = LiteEthPHYRGMII(
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
            self.ddrphy = usddrphy.USDDRPHY(platform.request("ddram"),
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
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=avnet_aesku40.Platform, description="LiteX SoC on AESKU40.")
    parser.add_argument("--sys-clk-freq", default=125e6, type=float, help="System clock frequency.")
    ethopts = parser.target_group.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",  action="store_true",    help="Add Ethernet.")
    ethopts.add_argument("--with-etherbone", action="store_true",    help="Add EtherBone.")
    parser.add_target_argument("--eth-ip",   default="192.168.1.50", help="Ethernet/Etherbone IP address.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq   = args.sys_clk_freq,
        with_ethernet  = args.with_ethernet,
        with_etherbone = args.with_etherbone,
        eth_ip         = args.eth_ip,
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
