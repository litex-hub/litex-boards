#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2023 Hans Baier <hansfbaier@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.altera import AlteraPlatform
from litex.build.altera.programmer import USBBlaster

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk
    ("clk50", 0, Pins("M9"), IOStandard("3.3-V LVCMOS")),

    # Button
    ("key", 0, Pins("J17"),  IOStandard("3.3-V LVCMOS")),
    ("key", 1, Pins("E16"),  IOStandard("3.3-V LVCMOS")),

    # SPIFlash (MT25QL128ABA)
    ("spiflash", 0,
        # clk
        Subsignal("cs_n", Pins("R4")),
        Subsignal("clk",  Pins("V3")),
        Subsignal("mosi", Pins("AB4")),
        Subsignal("miso", Pins("AB3")),
        IOStandard("3.3-V LVCMOS"),
    ),

    # SDR SDRAM
    ("sdram_clock", 0, Pins("G18"), IOStandard("3.3-V LVCMOS")),
    ("sdram", 0,
        Subsignal("a",     Pins(
            # A0  A1  A2  A3  A4  A5  A6  A7
            "M18 M20 M16 L17 L19 L18 K16 K17",
            # A8  A9 A10 A11 A12
            "J18 J19 N19 H18 H20")),
        Subsignal("ba",    Pins("P19 P18")),
        Subsignal("cs_n",  Pins("P17")),
        Subsignal("cke",   Pins("G17")),
        Subsignal("ras_n", Pins("P16")),
        Subsignal("cas_n", Pins("T19")),
        Subsignal("we_n",  Pins("U20")),
        Subsignal("dq", Pins(
            "AA22 AB22 Y22 Y21 W22 W21 V21 U22 M21 M22 T22 R21 R22 P22 N20 N21 ",
            "K22   K21 J22 J21 H21 G22 G21 F22 E22 E20 D22 D21 C21 B22 A22 B21")),
        Subsignal("dm", Pins("U21 L22 K20 E21")),
        IOStandard("3.3-V LVCMOS")
    ),
]

# The connectors are named after the daughterboard, not the core board
# because on the different core boards the names vary, but on the
# daughterboard they stay the same, which we need to connect the
# daughterboard peripherals to the core board.
# On this board J2 is U6 and J3 is U5
_connectors = [
    ("J2", {
         # odd row   even row
          7: "AB21",   8: "AB20",
          9: "Y19",   10: "Y20",
         11: "AA20",  12: "AA19",
         13: "W19",   14: "V20",
         15: "AB18",  16: "AB17",
         17: "U17",   18: "U16",
         19: "R16",   20: "R17",
         21: "T15",   22: "R15",
         23: "R14",   24: "P14",
         25: "AA15",  26: "AB15",
         27: "T13",   28: "T12",
         29: "R11",   30: "R10",
         31: "AA13",  32: "AA14",
         33: "Y15",   34: "Y14",
         35: "AB12",  36: "AB13",
         37: "AB11",  38: "AB10",
         39: "V10",   40: "V9",
         41: "U12",   42: "U11",
         43: "R9",    44: "T10",
         45: "T8",    46: "T7",
         47: "N8",    48: "P8",
         49: "M7",    50: "M6",
         51: "N6",    52: "P6",
         53: "R5",    54: "R6",
         55: "AB8",   56: "AA8 ",
         57: "AB7",   58: "AA7",
         59: "AB5",   60: "AB6",
    }),
    ("J3", {
        # odd row     even row
         7: "F19",    8: "F18",
         9: "E19",   10: "D19",
        11: "C20",   12: "B20",
        13: "A20",   14: "A19",
        15: "C19",   16: "C18",
        17: "A18",   18: "A17",
        19: "B18",   20: "B17",
        21: "B16",   22: "C16",
        23: "C15",   24: "B15",
        25: "E15",   26: "F15",
        27: "A15",   28: "A14",
        29: "B13",   30: "A13",
        31: "B12",   32: "A12",
        33: "G15",   34: "F14",
        35: "H13",   36: "G13",
        37: "D12",   38: "E12",
        39: "H11",   40: "G12",
        41: "A10",   42: "A9",
        43: "J9",    44: "H9",
        45: "E9",    46: "D9",
        47: "H8",    48: "G8",
        49: "L7",    50: "K7",
        51: "J7",    52: "J8",
        53: "A8",    54: "A7",
        55: "B6",    56: "B7",
        57: "C6",    58: "D6",
        59: "A5",    60: "B5",
    })
]

# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6
    core_resources = [
        ("user_led", 0, Pins("V19"), IOStandard("3.3-V LVCMOS")),
        ("user_led", 1, Pins("T20"), IOStandard("3.3-V LVCMOS")),
        ("serial", 0,
            Subsignal("tx", Pins("J3:7"), IOStandard("3.3-V LVCMOS")),
            Subsignal("rx", Pins("J3:8"), IOStandard("3.3-V LVCMOS"))
        ),
 ]

    def __init__(self, toolchain="quartus", with_daughterboard=False):
        device = "5CEFA5F23I7"
        io = _io
        connectors = _connectors

        if with_daughterboard:
            from litex_boards.platforms.qmtech_daughterboard import QMTechDaughterboard
            daughterboard = QMTechDaughterboard(IOStandard("3.3-V LVCMOS"))
            io += daughterboard.io
            connectors += daughterboard.connectors
        else:
            io += self.core_resources

        AlteraPlatform.__init__(self, device, io, connectors, toolchain=toolchain)

        if with_daughterboard:
            # ethernet takes the config pin, so make it available
            self.add_platform_command("set_global_assignment -name CYCLONEII_RESERVE_NCEO_AFTER_CONFIGURATION \"USE AS REGULAR IO\"")

        # Generate PLL clock in STA
        self.toolchain.additional_sdc_commands.append("derive_pll_clocks")
        # Calculates clock uncertainties
        self.toolchain.additional_sdc_commands.append("derive_clock_uncertainty")

    def create_programmer(self):
        return USBBlaster()

    def do_finalize(self, fragment):
        AlteraPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
