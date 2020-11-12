#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Basel Sayeh <Basel.Sayeh@hotmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.altera import AlteraPlatform
from litex.build.altera.programmer import USBBlaster

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk
    ("clk50", 0, Pins("T2"), IOStandard("3.3-V LVTTL")),

    # Leds
    ("user_led", 0, Pins("E4"), IOStandard("3.3-V LVTTL")),

    # Button
    ("key", 0, Pins("Y13"), IOStandard("3.3-V LVTTL")),
    ("key", 1, Pins("W13"),  IOStandard("3.3-V LVTTL")),

    # Serial
    ("serial", 0,
        # Compatible with cheap FT232 based cables (ex: Gaoominy 6Pin Ftdi Ft232Rl Ft232)
        Subsignal("tx", Pins("AA13"), IOStandard("3.3-V LVTTL")), # GPIO_07 (JP1 Pin 10)
        Subsignal("rx", Pins("AA14"), IOStandard("3.3-V LVTTL"))  # GPIO_05 (JP1 Pin 8)
    ),

    # SDR SDRAM
    ("sdram_clock", 0, Pins("Y6"), IOStandard("3.3-V LVTTL")),
    ("sdram", 0,
        Subsignal("a",     Pins(
            "V2 V1 U2 U1 V3 V4 Y2 AA1",
            "Y3 V5 W1 Y4 V6")),
        Subsignal("ba",    Pins("Y1 W2")),
        Subsignal("cs_n",  Pins("AA3")),
        Subsignal("cke",   Pins("W6")),
        Subsignal("ras_n", Pins("AB3")),
        Subsignal("cas_n", Pins("AA4")),
        Subsignal("we_n",  Pins("AB4")),
        Subsignal("dq", Pins(
            "AA10 AB9 AA9 AB8 AA8 AB7 AA7 AB5",
            "Y7 W8 Y8 V9 V10 Y10 W10 V11")),
        Subsignal("dm", Pins("AA5 W7")),
        IOStandard("3.3-V LVTTL")
    ),

    # GPIOs
    #ignore for now
    #("gpio_0", 0, Pins(
    #    "D3 C3  A2  A3  B3  B4  A4  B5",
    #    "A5 D5  B6  A6  B7  D6  A7  C6",
    #    "C8 E6  E7  D8  E8  F8  F9  E9",
    #    "C9 D9 E11 E10 C11 B11 A12 D11",
    #    "D12 B12"),
    #    IOStandard("3.3-V LVTTL")
    #),
    #("gpio_1", 0, Pins(
    #    "F13 T15 T14 T13 R13 T12 R12 T11",
    #    "T10 R11 P11 R10 N12  P9  N9 N11",
    #    "L16 K16 R16 L15 P15 P16 R14 N16",
    #    "N15 P14 L14 N14 M10 L13 J16 K15",
    #    "J13 J14"),
    #    IOStandard("3.3-V LVTTL")
    #),
    #("gpio_2", 0, Pins(
    #    "A14 B16 C14 C16 C15 D16 D15 D14",
    #    "F15 F16 F14 G16 G15"),
    #    IOStandard("3.3-V LVTTL")
    #),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self):
        AlteraPlatform.__init__(self, "EP4CE15F23C8", _io)

    def create_programmer(self):
        return USBBlaster()

    def do_finalize(self, fragment):
        AlteraPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
