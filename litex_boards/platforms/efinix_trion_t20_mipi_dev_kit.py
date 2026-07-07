#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.efinix.platform import EfinixPlatform
from litex.build.efinix import EfinixProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk
    ("clk26",    0, Pins("F11"), IOStandard("3.3_V_LVTTL_/_LVCMOS")),
    ("clk50",    0, Pins("D13"), IOStandard("3.3_V_LVTTL_/_LVCMOS")),
    ("clk74_25", 0, Pins("B1"),  IOStandard("1.8_V_LVCMOS")),

    # Leds
    ("user_led", 0, Pins("E1"), IOStandard("3.3_V_LVTTL_/_LVCMOS")),
    ("user_led", 1, Pins("F2"), IOStandard("3.3_V_LVTTL_/_LVCMOS")),

    # Buttons
    ("user_btn_n", 0, Pins("F1"), IOStandard("3.3_V_LVTTL_/_LVCMOS")),
    ("user_btn_n", 1, Pins("G2"), IOStandard("3.3_V_LVTTL_/_LVCMOS")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("K5")), # J11:1
        Subsignal("rx", Pins("K6")), # J11:2
        IOStandard("3.3_V_LVTTL_/_LVCMOS"),
        Misc("WEAK_PULLUP"),
    ),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("L1")),
        Subsignal("clk",  Pins("K1")),
        Subsignal("mosi", Pins("J1")),
        Subsignal("miso", Pins("J2")),
        IOStandard("3.3_V_LVTTL_/_LVCMOS")
    ),
]

# Bank voltage ---------------------------------------------------------------------------------------

_bank_info = [
            ("1A",       "3.3 V LVTTL / LVCMOS"),
            ("1B_1C_1D", "3.3 V LVTTL / LVCMOS"),
            ("1E",       "1.8 V"),
            ("3A_3B",    "3.3 V LVTTL / LVCMOS"),
            ("3C_3D_3E", "3.3 V LVTTL / LVCMOS"),
            ("4A",       "3.3 V LVTTL / LVCMOS"),
            ("4B",       "3.3 V LVTTL / LVCMOS"),
            ("BR",       "1.2 V"),
            ("TL",       "1.2 V"),
            ("TR",       "1.2 V"),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("J8", {
         1: "F1",  2: "G2",
         3: "E1",  4: "F2",
         5: "D1",  6: "D2",
         7: "C2",  8: "F3",
         9: "C1", 10: "E3",
    }),
    ("J11", {
         1: "K5",  2: "K6",
         3: "L6",  4: "L5",
         5: "N6",  6: "M6",
         7: "L9",  8: "J12",
        10: "E11",
        11: "E13", 12: "F12",
        13: "K9",  14: "G11",
        15: "M9",  16: "L10",
        17: "M10", 18: "N9",
        19: "K10", 20: "N10",
    }),
    ("J12", {
         1: "G3",
         3: "F13",  4: "H3",
         5: "J11",  6: "G12",
         7: "G13",  8: "H11",
        10: "H13",
        11: "H12", 12: "J13",
        13: "K11",
        15: "L11", 16: "K13",
        17: "M12", 18: "N12",
        19: "M11", 20: "N11",
    }),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(EfinixPlatform):
    default_clk_name   = "clk50"
    default_clk_freq   = 50e6
    default_clk_period = 1e9/50e6

    def __init__(self, toolchain="efinity"):
        EfinixPlatform.__init__(self, "T20F169C4", _io, _connectors, iobank_info=_bank_info, toolchain=toolchain)

    def create_programmer(self):
        return EfinixProgrammer()

    def do_finalize(self, fragment):
        EfinixPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
