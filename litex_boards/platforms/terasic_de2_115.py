#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019 Antony Pavlov <antonynpavlov@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.altera import AlteraPlatform
from litex.build.altera.programmer import USBBlaster

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk
    ("clk50", 0, Pins("Y2"), IOStandard("3.3-V LVTTL")),
    ("clk25", 0, Pins("A14"), IOStandard("3.3-V LVTTL")),

    # Red LEDs
    ("user_led", 0,  Pins("G19"), IOStandard("2.5 V")),
    ("user_led", 1,  Pins("F19"), IOStandard("2.5 V")),
    ("user_led", 2,  Pins("E19"), IOStandard("2.5 V")),
    ("user_led", 3,  Pins("F21"), IOStandard("2.5 V")),
    ("user_led", 4,  Pins("F18"), IOStandard("2.5 V")),
    ("user_led", 5,  Pins("E18"), IOStandard("2.5 V")),
    ("user_led", 6,  Pins("J19"), IOStandard("2.5 V")),
    ("user_led", 7,  Pins("H19"), IOStandard("2.5 V")),
    ("user_led", 8,  Pins("J17"), IOStandard("2.5 V")),
    ("user_led", 9,  Pins("G17"), IOStandard("2.5 V")),
    ("user_led", 10, Pins("J15"), IOStandard("2.5 V")),
    ("user_led", 11, Pins("H16"), IOStandard("2.5 V")),
    ("user_led", 12, Pins("J16"), IOStandard("2.5 V")),
    ("user_led", 13, Pins("H17"), IOStandard("2.5 V")),
    ("user_led", 14, Pins("F15"), IOStandard("2.5 V")),
    ("user_led", 15, Pins("G15"), IOStandard("2.5 V")),
    ("user_led", 16, Pins("G16"), IOStandard("2.5 V")),
    ("user_led", 17, Pins("H15"), IOStandard("2.5 V")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("G9"), IOStandard("3.3-V LVTTL")), # Use built-in Tx RS32 port
        Subsignal("rx", Pins("G12"), IOStandard("3.3-V LVTTL"))  #  Use built-in Rx RS32 port
    ),

    # SDR SDRAM
    ("sdram_clock", 0, Pins("AE5"), IOStandard("3.3-V LVTTL")),
    ("sdram", 0,
        Subsignal("a",     Pins(
            "R6 V8 U8 P1 V5 W8 W7 AA7",
            "Y5 Y6 R5 AA5 Y7")),
        Subsignal("ba",    Pins("U7 R4")),
        Subsignal("cs_n",  Pins("T4")),
        Subsignal("cke",   Pins("AA6")),
        Subsignal("ras_n", Pins("U6")),
        Subsignal("cas_n", Pins("V7")),
        Subsignal("we_n",  Pins("V6")),
        Subsignal("dq", Pins(
            "W3 W2  V4  W1  V3  V2  V1  U3",
            "Y3 Y4 AB1 AA3 AB2 AC1 AB3 AC2")),
        Subsignal("dm", Pins("U2 W4")),
        IOStandard("3.3-V LVTTL")
    ),

    # SD Card
    ("sdcard", 0,
        Subsignal("data", Pins("AE14 AF13 AB14 AC14")),
        Subsignal("cmd",  Pins("AD14")),
        Subsignal("clk",  Pins("AE13")),
        Misc("FAST_OUTPUT_REGISTER ON"),
        IOStandard("3.3-V LVTTL"),
    ),

    # MII Ethernet (88E1111)
    ("eth_clocks", 0,
        Subsignal("tx", Pins("B17")),
        Subsignal("rx", Pins("A15")),
        IOStandard("2.5 V")
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("C19")),
        Subsignal("int_n",   Pins("A21")),
        Subsignal("mdio",    Pins("B21")),
        Subsignal("mdc",     Pins("C20")),
        Subsignal("rx_dv",   Pins("C17")),
        Subsignal("rx_er",   Pins("D18")),
        Subsignal("rx_data", Pins("C16 D16 D17 C15")),
        Subsignal("tx_en",   Pins("A18")),
        Subsignal("tx_er",   Pins("B18")),
        Subsignal("tx_data", Pins("C18 D19 A19 B19")),
        Subsignal("col",     Pins("E15")),
        Subsignal("crs",     Pins("D15")),
        IOStandard("2.5 V")
    ),

    # MII Ethernet (88E1111)
    ("eth_clocks", 1,
        Subsignal("tx", Pins("C22")),
        Subsignal("rx", Pins("B15")),
        IOStandard("2.5 V")
    ),
    ("eth", 1,
        Subsignal("rst_n",   Pins("D22")),
        Subsignal("int_n",   Pins("D24")),
        Subsignal("mdio",    Pins("D25")),
        Subsignal("mdc",     Pins("D23")),
        Subsignal("rx_dv",   Pins("A22")),
        Subsignal("rx_er",   Pins("C24")),
        Subsignal("rx_data", Pins("B23 C21 A23 D21")),
        Subsignal("tx_en",   Pins("B25")),
        Subsignal("tx_er",   Pins("A25")),
        Subsignal("tx_data", Pins("C25 A26 B26 C26")),
        Subsignal("col",     Pins("B22")),
        Subsignal("crs",     Pins("D20")),
        IOStandard("2.5 V")
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self, toolchain="quartus"):
        AlteraPlatform.__init__(self, "EP4CE115F29C7", _io, toolchain=toolchain)

    def create_programmer(self):
        return USBBlaster()

    def do_finalize(self, fragment):
        AlteraPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
        self.add_period_constraint(self.lookup_request("clk25", loose=True), 1e9/25e6)
