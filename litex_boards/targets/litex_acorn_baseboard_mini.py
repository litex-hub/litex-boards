#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021-2024 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# Build/Use ----------------------------------------------------------------------------------------

import os

from migen import *

from litex.gen import LiteXModule

from litex_boards.platforms import sqrl_acorn

from litex.soc.interconnect.csr import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

from litex.soc.cores.clock import *
from litex.soc.cores.led import LedChaser

from litex.build.generic_platform import Subsignal, Pins
from liteeth.phy.a7_gtp import QPLLSettings, QPLL
from liteeth.phy.a7_1000basex import A7_1000BASEX

# CRG ----------------------------------------------------------------------------------------------

class CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_sys    = ClockDomain()
        self.clock_domains.cd_idelay = ClockDomain()

        # Clk/Rst
        clk200 = platform.request("clk200")

        # PLL
        self.submodules.pll = pll = S7PLL()
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk200, 200e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq, margin=0)
        # Ignore sys_clk to pll.clkin path created by SoC's rst.
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin)

# BaseSoC -----------------------------------------------------------------------------------------

class BaseSoC(SoCMini):
    def __init__(self, variant="cle-215+", sys_clk_freq=156.25e6, with_led_chaser=True, **kwargs):
        platform = sqrl_acorn.Platform(variant=variant)
        assert sys_clk_freq == 156.25e6

        # SoCCore ----------------------------------------------------------------------------------
        SoCMini.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Acorn CLE-101/215(+)")

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = CRG(platform, sys_clk_freq)

        # Etherbone --------------------------------------------------------------------------------

        _eth_io = [
            ("sfp", 0,
                Subsignal("txp", Pins("D5")),
                Subsignal("txn", Pins("C5")),
                Subsignal("rxp", Pins("D11")),
                Subsignal("rxn", Pins("C11")),
            ),
            ("sfp", 1,
                Subsignal("txp", Pins("B4")),
                Subsignal("txn", Pins("A4")),
                Subsignal("rxp", Pins("B8")),
                Subsignal("rxn", Pins("A8")),
            ),
        ]
        platform.add_extension(_eth_io)

        # phy
        qpll_settings = QPLLSettings(
            refclksel  = 0b001,
            fbdiv      = 4,
            fbdiv_45   = 4,
            refclk_div = 1
        )
        qpll = QPLL(ClockSignal("sys"), qpll_settings)
        print(qpll)
        self.submodules += qpll

        self.ethphy0 = A7_1000BASEX(
            qpll_channel = qpll.channels[0],
            data_pads    = self.platform.request("sfp", 0),
            sys_clk_freq = self.clk_freq,
            rx_polarity  = 1,  # Inverted on Acorn
            tx_polarity  = 0   # Inverted on Acorn and on baseboard.
        )
        platform.add_platform_command("set_property SEVERITY {{Warning}} [get_drc_checks REQP-49]")
        self.add_etherbone(name="etherbone0",
            phy         = self.ethphy0,
            phy_cd      = "ethphy0_eth",
            mac_address = 0x10e2d5000000,
            ip_address  = "192.168.1.50"
        )

        self.ethphy1 = A7_1000BASEX(
            qpll_channel = qpll.channels[0],
            data_pads    = self.platform.request("sfp", 1),
            sys_clk_freq = self.clk_freq,
            rx_polarity  = 1,  # Inverted on Acorn
            tx_polarity  = 0   # Inverted on Acorn and on baseboard.
        )
        platform.add_platform_command("set_property SEVERITY {{Warning}} [get_drc_checks REQP-49]")
        self.add_etherbone(name="etherbone1",
            phy         = self.ethphy1,
            phy_cd      = "ethphy1_eth",
            mac_address = 0x10e2d5000001,
            ip_address  = "192.168.1.51"
        )

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=sqrl_acorn.Platform, description="LiteX SoC on Acorn CLE-101/215(+).")
    parser.add_target_argument("--flash",           action="store_true",       help="Flash bitstream.")
    parser.add_target_argument("--variant",         default="cle-215+",        help="Board variant (cle-215+, cle-215 or cle-101).")
    args = parser.parse_args()

    soc = BaseSoC(
        variant = args.variant,
        **parser.soc_argdict
    )

    builder  = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.flash(0, builder.get_bitstream_filename(mode="flash"))

if __name__ == "__main__":
    main()
