#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Basel Sayeh <Basel.Sayeh@hotmail.com>
# Copyright (c) 2021 Hans Baier <hansfbaier@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.altera import AlteraPlatform
from litex.build.altera.programmer import USBBlaster

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk
    ("clk50", 0, Pins("T2"), IOStandard("3.3-V LVTTL")),

    # Button
    ("key", 0, Pins("Y13"),  IOStandard("3.3-V LVTTL")),
    ("key", 1, Pins("W13"),  IOStandard("3.3-V LVTTL")),

    # SPIFlash (W25Q64)
    ("spiflash", 0,
        # clk
        Subsignal("cs_n", Pins("E2")),
        Subsignal("clk",  Pins("K2")),
        Subsignal("mosi", Pins("D1")),
        Subsignal("miso", Pins("E2")),
        IOStandard("3.3-V LVTTL"),
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
]

# The connectors are named after the daughterboard, not the core board
# because on the different core boards the names vary, but on the
# daughterboard they stay the same, which we need to connect the
# daughterboard peripherals to the core board.
# On this board J2 is U7 and J3 is U8
_connectors = [
    ("J2", {
         # odd row     even row
          7: "R1",   8: "R2",
          9: "P1",  10: "P2",
         11: "N1",  12: "N2",
         13: "M1",  14: "M2",
         15: "J1",  16: "J2",
         17: "H1",  18: "H2",
         19: "F1",  20: "F2",
         21: "E1",  22: "D2",
         23: "C1",  24: "C2",
         25: "B1",  26: "B2",
         27: "B3",  28: "A3",
         29: "B4",  30: "A4",
         31: "C4",  32: "C3",
         33: "B5",  34: "A5",
         35: "B6",  36: "A6",
         37: "B7",  38: "A7",
         39: "B8",  40: "A8",
         41: "B9",  42: "A9",
         43: "B10", 44: "A10",
         45: "B13", 46: "A13",
         47: "B14", 48: "A14",
         49: "B15", 50: "A15",
         51: "B16", 52: "A16",
         53: "B17", 54: "A17",
         55: "B18", 56: "A18",
         57: "B19", 58: "A19",
         59: "B20", 60: "A20",
    }),
    ("J3", {
        # odd row     even row
         7: "AA13",   8: "AB13",
         9: "AA14",  10: "AB14",
        11: "AA15",  12: "AB15",
        13: "AA16",  14: "AB16",
        15: "AA17",  16: "AB17",
        17: "AA18",  18: "AB18",
        19: "AA19",  20: "AB19",
        21: "AA20",  22: "AB20",
        23: "Y22",   24: "Y21",
        25: "W22",   26: "W21",
        27: "V22",   28: "V21",
        29: "U22",   30: "U21",
        31: "R22",   32: "R21",
        33: "P22",   34: "P21",
        35: "N22",   36: "N21",
        37: "M22",   38: "M21",
        39: "L22",   40: "L21",
        41: "K22",   42: "K21",
        43: "J22",   44: "J21",
        45: "H22",   46: "H21",
        47: "F22",   48: "F21",
        49: "E22",   50: "E21",
        51: "D22",   52: "D21",
        53: "C22",   54: "C21",
        55: "B22",   56: "B21",
        57: "N20",   58: "N19",
        59: "M20",   60: "M19",
    })
]

# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6
    core_resources = [
        ("user_led", 0, Pins("E4"), IOStandard("3.3-V LVTTL")),
        ("serial", 0,
            Subsignal("tx", Pins("J3:7"), IOStandard("3.3-V LVTTL")),
            Subsignal("rx", Pins("J3:8"), IOStandard("3.3-V LVTTL"))
        ),
    ]

    def __init__(self, variant="ep4ce15", toolchain="quartus", with_daughterboard=False):
        device = {
            "ep4ce15": "EP4CE15F23C8",
            "ep4ce55": "EP4CE55F23C8"
        }[variant]
        io = _io
        connectors = _connectors

        if with_daughterboard:
            from litex_boards.platforms.qmtech_daughterboard import QMTechDaughterboard
            daughterboard = QMTechDaughterboard(IOStandard("3.3-V LVTTL"))
            io += daughterboard.io
            connectors += daughterboard.connectors
        else:
            io += self.core_resources

        AlteraPlatform.__init__(self, device, io, connectors, toolchain=toolchain)

        if with_daughterboard:
            # an ethernet pin takes K22, so make it available
            self.add_platform_command("set_global_assignment -name CYCLONEII_RESERVE_NCEO_AFTER_CONFIGURATION \"USE AS REGULAR IO\"")

    def create_programmer(self):
        return USBBlaster()

    def do_finalize(self, fragment):
        AlteraPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
