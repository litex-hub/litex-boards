#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

import os
import argparse

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex_boards.platforms import pano_logic_g2

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from liteeth.phy import LiteEthPHY

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, clk_freq, with_ethernet=False):
        self.clock_domains.cd_sys    = ClockDomain()

        # # #

        if not with_ethernet:
            # Take Ethernet PHY out of reset to enable 125MHz on clk125 (25MHz otherwise).
            # See https://github.com/tomverbeure/panologic-g2#fpga-external-clocking-architecture
            self.comb += platform.request("eth_rst_n").eq(1)

        self.submodules.pll = pll = S6PLL(speedgrade=-2)
        self.comb += pll.reset.eq(~platform.request("user_btn_n"))
        pll.register_clkin(platform.request("clk125"), 125e6)
        pll.create_clkout(self.cd_sys, clk_freq)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, revision, sys_clk_freq=int(50e6), with_ethernet=False, with_etherbone=False, **kwargs):
        platform = pano_logic_g2.Platform(revision=revision)
        if with_etherbone:
            sys_clk_freq = int(125e6)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident          = "LiteX SoC on Pano Logic G2",
            ident_version  = True,
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq, with_ethernet=with_ethernet or with_etherbone)

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            self.submodules.ethphy = LiteEthPHY(
                clock_pads         = self.platform.request("eth_clocks"),
                pads               = self.platform.request("eth"),
                clk_freq           = sys_clk_freq,
                with_hw_init_reset = False)
            self.add_csr("ethphy")
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy)
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy)

        # Leds -------------------------------------------------------------------------------------
        self.submodules.leds = LedChaser(
            pads         = platform.request_all("user_led"),
            sys_clk_freq = sys_clk_freq)
        self.add_csr("leds")

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on Pano Logic G2")
    parser.add_argument("--build",    action="store_true", help="Build bitstream")
    parser.add_argument("--load",     action="store_true", help="Load bitstream")
    parser.add_argument("--revision", default="c",         help="Board revision c (default) or b")
    builder_args(parser)
    soc_core_args(parser)
    parser.add_argument("--with-ethernet",  action="store_true", help="Enable Ethernet support")
    parser.add_argument("--with-etherbone", action="store_true", help="Enable Etherbone support")
    args = parser.parse_args()

    assert not (args.with_ethernet and args.with_etherbone)
    soc = BaseSoC(
        revision       = args.revision,
        with_ethernet  = args.with_ethernet,
        with_etherbone = args.with_etherbone,
        **soc_core_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".bit"))

if __name__ == "__main__":
    main()
