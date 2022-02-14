#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019 Antti Lukats <antti.lukats@gmail.com>
# Copyright (c) 2019 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.altera import AlteraPlatform
from litex.build.altera.programmer import USBBlaster

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk12", 0, Pins("G21"),  IOStandard("3.3-V LVTTL")),
    ("clk25", 0, Pins("AA12"), IOStandard("3.3-V LVTTL")),
    ("cpu_reset", 0, Pins("V15"), IOStandard("3.3-V LVTTL")),

    # Leds
    ("user_led", 0, Pins("C18"), IOStandard("3.3-V LVTTL")),
    ("user_led", 1, Pins("D19"), IOStandard("3.3-V LVTTL")),
    ("user_led", 2, Pins("C19"), IOStandard("3.3-V LVTTL")),
    ("user_led", 3, Pins("C17"), IOStandard("3.3-V LVTTL")),
    ("user_led", 4, Pins("D18"), IOStandard("3.3-V LVTTL")),

    # Switches
    ("sw", 0, Pins("U10"), IOStandard("3.3-V LVTTL")),
    ("sw", 1, Pins("U11"), IOStandard("3.3-V LVTTL")),
    ("sw", 2, Pins("V11"), IOStandard("3.3-V LVTTL")),
    ("sw", 3, Pins("T10"), IOStandard("3.3-V LVTTL")),
    ("sw", 4, Pins("T11"), IOStandard("3.3-V LVTTL")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("B21"), IOStandard("3.3-V LVTTL")),
        Subsignal("rx", Pins("C20"), IOStandard("3.3-V LVTTL")),
    ),

    # SDR SDRAM
    ("sdram_clock", 0, Pins("AA3"), IOStandard("3.3-V LVTTL")),
    ("sdram", 0,
        Subsignal("a", Pins(
            "V5   Y3 W6  Y4 AB5 AB6 AA6 AA7",
            "AB7 AA5 V6 AA8 AB8")),
        Subsignal("ba",    Pins("Y6 V7")),
        Subsignal("cs_n",  Pins("W7")),
        Subsignal("cke",   Pins("AA4")),
        Subsignal("ras_n", Pins("V8")),
        Subsignal("cas_n", Pins("Y7")),
        Subsignal("we_n",  Pins("W8")),
        Subsignal("dq", Pins(
            "AB16 Y17 AA16 AA19 AB18 AA20 AB19 AB20",
            "Y13  Y15 AA13 AB15 AB13 AA15 AA14 AB14")),
        Subsignal("dm", Pins("Y14 W13")),
        IOStandard("3.3-V LVTTL")
    ),

    # ECPS
    ("epcs", 0,
        Subsignal("data0", Pins("K1")),
        Subsignal("dclk",  Pins("K2")),
        Subsignal("ncs0",  Pins("E2")),
        Subsignal("asd0",  Pins("D1")),
        IOStandard("3.3-V LVTTL")
    ),

    # HyperRAM
    ("hyperram", 0,
        Subsignal("clk",   Pins("T16")),
        Subsignal("rst_n", Pins("U12")),
        Subsignal("dq",    Pins("T15 W17 U14 R15 R14 V16 U16 U17")),
        Subsignal("cs_n",  Pins("V13")),
        Subsignal("rwds",  Pins("U13")),
        IOStandard("3.3-V LVTTL")
    ),

    # GPIO Leds
    ("gpio_leds", 0,
        Pins("AB10 AA10 AA9 Y10 W10 U9 U8 U7"),
        IOStandard("3.3-V LVTTL")
    ),

    # MII Ethernet
    ("eth_clocks", 0,
        Subsignal("tx", Pins("U21")),
        Subsignal("rx", Pins("V22")),
        IOStandard("3.3-V LVTTL"),
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("R19")),
        Subsignal("mdio",    Pins("AA21")),
        Subsignal("mdc",     Pins("AA22")),
        Subsignal("rx_dv",   Pins("W21")),
        Subsignal("rx_er",   Pins("V21")),
        Subsignal("rx_data", Pins("W22 W20 Y21 Y22")),
        Subsignal("tx_en",   Pins("T18")),
        Subsignal("tx_data", Pins("T17 U20 U19 T20")),
        Subsignal("col",     Pins("T19")),
        Subsignal("crs",     Pins("R20")),
        IOStandard("3.3-V LVTTL"),
    ),
    ("eth_clocks", 1,
        Subsignal("tx", Pins("N16")),
        Subsignal("rx", Pins("V22")),
        IOStandard("3.3-V LVTTL"),
    ),
    ("eth", 1,
        Subsignal("rst_n",   Pins("M21")),
        Subsignal("mdio",    Pins("N20")),
        Subsignal("mdc",     Pins("N18")),
        Subsignal("rx_dv",   Pins("R18")),
        Subsignal("rx_er",   Pins("P17")),
        Subsignal("rx_data", Pins("M20 M19 M16 N19")),
        Subsignal("tx_en",   Pins("R22")),
        Subsignal("tx_data", Pins("R21 N21 M22 N22")),
        Subsignal("col",     Pins("P21")),
        Subsignal("crs",     Pins("P22")),
        IOStandard("3.3-V LVTTL"),
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name   = "clk12"
    default_clk_period = 1e9/12e6

    def __init__(self, toolchain="quartus"):
        AlteraPlatform.__init__(self, "10CL055YU484A7G", _io, toolchain=toolchain)

    def create_programmer(self):
        return USBBlaster(cable_name="Arrow-USB-Blaster")

    def do_finalize(self, fragment):
        AlteraPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk12", loose=True), 1e9/12e6)
        self.add_period_constraint(self.lookup_request("clk25", loose=True), 1e9/25e6)
