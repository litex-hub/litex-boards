#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Miodrag Milanovic <mmicko@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.efinix.platform import EfinixPlatform
from litex.build.efinix import EfinixProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk
    ("clk50", 0, Pins("L13"), IOStandard("3.3_V_LVTTL_/_LVCMOS")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("H4:18")), # 27 on H4
        Subsignal("rx", Pins("H4:19")), # 28 on H4
        IOStandard("3.3_V_LVTTL_/_LVCMOS") , Misc("WEAK_PULLUP")
    ),

    # Leds
    ("user_led", 0, Pins("D14"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=3")),
    ("user_led", 1, Pins("E13"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=3")),
    ("user_led", 2, Pins("G13"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=3")),
    ("user_led", 3, Pins("F14"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=3")),
    ("user_led", 4, Pins("N14"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=3")),
    ("user_led", 5, Pins("N16"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=3")),
    ("user_led", 6, Pins("P15"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=3")),
    ("user_led", 7, Pins("M14"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=3")),

    # Buttons
    ("user_btn", 0, Pins("P2"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("WEAK_PULLUP")),
    ("user_btn", 1, Pins("N3"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("WEAK_PULLUP")),
    ("user_btn", 2, Pins("L4"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("WEAK_PULLUP")),

    # Switches
    ("user_sw", 0, Pins("H14"),  IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("WEAK_PULLUP")),
    ("user_sw", 1, Pins("H15"),  IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("WEAK_PULLUP")),
    ("user_sw", 2, Pins("H16"),  IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("WEAK_PULLUP")),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("P3")),
        Subsignal("clk",  Pins("M3")),
        Subsignal("mosi", Pins("L3")),
        Subsignal("miso", Pins("N1")),
        IOStandard("3.3_V_LVTTL_/_LVCMOS")
    ),
]

# Bank voltage ---------------------------------------------------------------------------------------

_bank_info = [
            ("1A",       "3.3 V LVTTL / LVCMOS"),
            ("1B_1C",    "3.3 V LVTTL / LVCMOS"),
            ("1D_1E",    "3.3 V LVTTL / LVCMOS"),
            ("3A_3B_3C", "3.3 V LVTTL / LVCMOS"),
            ("3D_3E",    "3.3 V LVTTL / LVCMOS"),
            ("4A",       "3.3 V LVTTL / LVCMOS"),
            ("4B",       "3.3 V LVTTL / LVCMOS"),
            ("BR",       "1.2 V"),
            ("TL",       "1.2 V"),
            ("TR",       "1.2 V"),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ["H4", # -  - 26 25 24 23 22 21 20 19 18 16 15 14 13 12 11
           " -  - H4 H2 H3 L1 H1 H5 J2 K2 K1 J3 K3 J4 L2 K4 J5",
           # - 27 28 29 30 31 32 33 34 35 36 37 39 40 41 42 43
           " - G3 G5 G2 F1 G1 F2 C1 E2 F3 D1 E1 E3 F5 C2 G4 F4"],
    ["H2", # - 45 47 49 51 53 55 57 59 61  - 63 65 67 69 71 73
           " - B2 D4 D5 C4 B4 E4 A3 A4 B5  - B7 A6 C5 D7 B8 D8",
           # - 44 46 48 50 52 54 56 58 60 62 64 66 68 70 72 74
           " - B1 D3 C3 A2 B3 D6 E6 C6 E5 A7 B6 A8 E7 C7 C8 D9"],
    ["H3", #158 155 153 150 127 124 122 120 117 111 105  81  79  77
           "L12 P15 N14 L14 G14 G15 F15 E15 G13 F12 E13 C10 A10 D10",
           #156 154 151 149 126 123 121 118 113 110 104   -  78  76
           "M14 N16 K13 R16 G16 F16 G12 F14 F13 E14 D14   -  A9  C9"],
]

# Platform -----------------------------------------------------------------------------------------

class Platform(EfinixPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self, toolchain="efinity"):
        EfinixPlatform.__init__(self, "T20F256C4", _io, _connectors, iobank_info=_bank_info, toolchain=toolchain)

    def create_programmer(self):
        return EfinixProgrammer()

    def do_finalize(self, fragment):
        EfinixPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
