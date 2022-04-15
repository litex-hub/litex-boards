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
    ("clk50", 0, Pins("B14"), IOStandard("3.3-V LVTTL")),

    # Button
    ("key", 0, Pins("AD23"),  IOStandard("3.3-V LVTTL")),
    ("key", 1, Pins("AD24"),  IOStandard("3.3-V LVTTL")),

    # SPIFlash (W25Q64)
    ("spiflash", 0,
        # clk
        Subsignal("cs_n", Pins("D5")),
        Subsignal("clk",  Pins("F6")),
        Subsignal("mosi", Pins("E6")),
        Subsignal("miso", Pins("D6")),
        IOStandard("3.3-V LVTTL"),
    ),

    # SDR SDRAM
    ("sdram_clock", 0, Pins("J23"), IOStandard("3.3-V LVTTL")),
    ("sdram", 0,
        Subsignal("a",     Pins(
            "L25 L26 M25 M26 N22 N23 N24 M22",
            "M24 L23 K26 L24 K23")),
        Subsignal("ba",    Pins("J25 J26")),
        Subsignal("cs_n",  Pins("H26")),
        Subsignal("cke",   Pins("K24")),
        Subsignal("ras_n", Pins("H25")),
        Subsignal("cas_n", Pins("G26")),
        Subsignal("we_n",  Pins("G25")),
        Subsignal("dq", Pins(
            "B25 B26 C25 C26 D25 D26 E25 E26",
            "H23 G24 G22 F24 F23 E24 D24 C24")),
        Subsignal("dm", Pins("F26 H24")),
        IOStandard("3.3-V LVTTL")
    ),
]

# The connectors are named after the daughterboard, not the core board
# because on the different core boards the names vary, but on the
# daughterboard they stay the same, which we need to connect the
# daughterboard peripherals to the core board.
# On this board J2 is U5 and J3 is U4
_connectors = [
    ("J2", {
        # odd row      even row
         7: "AF24",   8: "AF25",
         9: "AC21",  10: "AD21",
        11: "AE23",  12: "AF23",
        13: "AE22",  14: "AF22",
        15: "AD20",  16: "AE21",
        17: "AF20",  18: "AF21",
        19: "AE19",  20: "AF19",
        21: "AC19",  22: "AD19",
        23: "AE18",  24: "AF18",
        25: "AC18",  26: "AD18",
        27: "AE17",  28: "AF17",
        29: "AC17",  30: "AD17",
        31: "AF15",  32: "AF16",
        33: "AC16",  34: "AD16",
        35: "AE14",  36: "AE15",
        37: "AC15",  38: "AD15",
        39: "AC14",  40: "AD14",
        41: "AF11",  42: "AF12",
        43: "AC10",  44: "AD10",
        45: "AE9",   46: "AF9",
        47: "AF7",   48: "AF8",
        49: "AE7",   50: "AF6",
        51: "AE5",   52: "AE6",
        53: "AD5",   54: "AD6",
        55: "AF4",   56: "AF5",
        57: "AD3",   58: "AE3",
        59: "AC4",   60: "AD4",
    }),
    ("J3", {
        # odd row      even row
         7: "C21",    8: "B22",
         9: "B23",   10: "A23",
        11: "B21",   12: "A22",
        13: "C19",   14: "B19",
        15: "A21",   16: "A20",
        17: "A19",   18: "A18",
        19: "C17",   20: "B18",
        21: "C16",   22: "B17",
        23: "A17",   24: "A16",
        25: "B15",   26: "A15",
        27: "C15",   28: "C14",
        29: "C13",   30: "B13",
        31: "C12",   32: "C11",
        33: "A13",   34: "A12",
        35: "B11",   36: "A11",
        37: "B10",   38: "A10",
        39: "C10",   40: "B9",
        41: "A9",    42: "A8",
        43: "A7",    44: "A6",
        45: "B7",    46: "B6",
        47: "B5",    48: "A5",
        49: "B4",    50: "A4",
        51: "C5",    52: "C4",
        53: "A3",    54: "A2",
        55: "B2",    56: "B1",
        57: "D1",    58: "C1",
        59: "E2",    60: "E1",
    })
]

# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6
    core_resources = [
        ("user_led", 0, Pins("A25"), IOStandard("3.3-V LVTTL")),
        ("user_led", 1, Pins("A24"), IOStandard("3.3-V LVTTL")),
        ("serial", 0,
            Subsignal("tx", Pins("J3:7"), IOStandard("3.3-V LVTTL")),
            Subsignal("rx", Pins("J3:8"), IOStandard("3.3-V LVTTL"))
        ),
    ]

    def __init__(self, toolchain="quartus", with_daughterboard=False):
        device = "EP4CGX150DF27I7"
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
