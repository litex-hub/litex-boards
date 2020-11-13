#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform, VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [ # Documented by https://github.com/360nosc0pe project.
    # Leds
    ("user_led", 0, Pins("G16"), IOStandard("LVCMOS33")),

    # Beeper
    ("beeper", 0, Pins("W17"), IOStandard("LVCMOS33")),

    # Led Frontpanel
    ("led_frontpanel", 0,
        Subsignal("rclk", Pins("N22")),
        Subsignal("clk",  Pins("R20")),
        Subsignal("mosi", Pins("P22")),
        Subsignal("oe",   Pins("R21")),
        IOStandard("LVCMOS33"),
    ),

    # Button Frontpanel
    ("btn_frontpanel", 0,
        Subsignal("clk",  Pins("H18")),
        Subsignal("clr",  Pins("G19")),
        Subsignal("miso", Pins("G17")),
        IOStandard("LVCMOS33")
    ),

    # LCD
    ("lcd", 0,
        Subsignal("clk",   Pins("D20")),
        Subsignal("vsync", Pins("A21")),
        Subsignal("hsync", Pins("A22")),
        Subsignal("r", Pins("G22 F22 F21 F19 F18 F17")),
        Subsignal("g", Pins("F16 E21 E20 E19 E18 E16")),
        Subsignal("b",  Pins("D22 D21 C22 C20 B22 B21")),
        IOStandard("LVCMOS33"),
    ),

    # MII Ethernet
    ("eth_clocks", 0,
        Subsignal("tx", Pins("B19")),
        Subsignal("rx", Pins("C17")),
        IOStandard("LVCMOS33"),
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("R6")),
        Subsignal("mdio",    Pins("E15")),
        Subsignal("mdc",     Pins("D15")),
        Subsignal("rx_dv",   Pins("A16")),
        Subsignal("rx_er",   Pins("C15")),
        Subsignal("rx_data", Pins("D16 A17 B17 D17")),
        Subsignal("tx_en",   Pins("A18")),
        Subsignal("tx_data", Pins("C18 A19 C19 B20")),
        Subsignal("col",     Pins("B16")),
        Subsignal("crs",     Pins("B15")),
        IOStandard("LVCMOS33"),
    ),

    # DDR3 SDRAM
    ("ddram", 0,
        Subsignal("a", Pins(
            "J21 K18 J18 R16 P16 T18 R18 T19",
            "R19 P18 P17 P15 N15"),
            IOStandard("SSTL135")),
        Subsignal("ba",    Pins("K21 J20 J22"), IOStandard("SSTL135")),
        Subsignal("ras_n", Pins("L21"), IOStandard("SSTL135")),
        Subsignal("cas_n", Pins("L22"), IOStandard("SSTL135")),
        Subsignal("we_n",  Pins("K19"), IOStandard("SSTL135")),
        #Subsignal("cs_n", Pins(""), IOStandard("SSTL135")), # Pulled low.
        #Subsignal("dm",   Pins(""), IOStandard("SSTL135")), # Pulled low.
        Subsignal("dq", Pins(
            " T21  U21  T22  U22  W20  W21 U20   V20",
            "AA22 AB22 AA21 AB21 AB19 AB20 Y19  AA19",
	        " W16  Y16  U17  V17 AA17 AB17 AA16 AB16",
	        " V14  V13  W13  Y14 AA14  Y13 AA13 AB14"),
            IOStandard("SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("dqs_p", Pins("V22 Y20 U15 W15"),
            IOStandard("DIFF_SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("dqs_n", Pins("W22 Y21 U16 Y15"),
            IOStandard("DIFF_SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("clk_p",   Pins("T16"), IOStandard("DIFF_SSTL135")),
        Subsignal("clk_n",   Pins("T17"), IOStandard("DIFF_SSTL135")),
        Subsignal("cke",     Pins("M21"), IOStandard("SSTL135")),
        Subsignal("odt",     Pins("M22"), IOStandard("SSTL135")),
        Subsignal("reset_n", Pins("V18"), IOStandard("SSTL135")),
        Misc("SLEW=FAST"),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = []

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    def __init__(self):
        XilinxPlatform.__init__(self, "xc7z020-clg484-1", _io,  _connectors, toolchain="vivado")

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("eth_clocks:rx", loose=True), 1e9/25e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:tx", loose=True), 1e9/25e6)
