#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Hans Baier <hansfbaier@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.altera import AlteraPlatform
from litex.build.altera.programmer import USBBlaster

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk
    ("clk50", 0, Pins("M9"), IOStandard("3.3-V LVTTL")),

    # Button
    ("key", 0, Pins("AB13"),  IOStandard("3.3-V LVTTL")),
    ("key", 1, Pins("V18"),  IOStandard("3.3-V LVTTL")),

    # SPIFlash (MT25QL128ABA)
    ("spiflash", 0,
        # clk
        Subsignal("cs_n", Pins("R4")),
        Subsignal("clk",  Pins("V3")),
        Subsignal("mosi", Pins("AB4")),
        Subsignal("miso", Pins("AB3")),
        IOStandard("3.3-V LVTTL"),
    ),

    # SDR SDRAM
    ("sdram_clock", 0, Pins("AB11"), IOStandard("3.3-V LVTTL")),
    ("sdram", 0,
        Subsignal("a",     Pins(
            "P8 P7 N8 N6 U6 U7 V6 U8",
            "T8 W8 R6 T9 Y9")),
        Subsignal("ba",    Pins("T7 P9")),
        Subsignal("cs_n",  Pins("AB5")),
        Subsignal("cke",   Pins("V9")),
        Subsignal("ras_n", Pins("AB6")),
        Subsignal("cas_n", Pins("AA7")),
        Subsignal("we_n",  Pins("W9")),
        Subsignal("dq", Pins(
            "AA12 Y11 AA10 AB10 Y10 AA9 AB8 AA8",
            " U10 T10 U11  R12  U12 P12 R10 R11")),
        Subsignal("dm", Pins("AB7 V10")),
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
         # odd row   even row
          7: "AA2",   8: "AA1",
          9: "Y3",   10: "W2",
         11: "U1",   12: "U2",
         13: "N1",   14: "N2",
         15: "L1",   16: "L2",
         17: "G1",   18: "G2",
         19: "E2",   20: "D3",
         21: "C1",   22: "C2",
         23: "G6",   24: "H6",
         25: "G8",   26: "H8",
         27: "F7",   28: "E7",
         29: "D6",   30: "C6",
         31: "E9",   32: "D9",
         33: "B5",   34: "A5",
         35: "B6",   36: "B7",
         37: "A7",   38: "A8",
         39: "A9",   40: "A10",
         41: "B10",  42: "C9",
         43: "G10",  44: "F10",
         45: "C11",  46: "B11",
         47: "B12",  48: "A12",
         49: "E12",  50: "D12",
         51: "D13",  52: "C13",
         53: "B13",  54: "A13",
         55: "A15",  56: "A14",
         57: "B15",  58: "C15",
         59: "C16",  60: "B16",
    }),
    ("J3", {
        # odd row     even row
         7: "AA14",   8: "AA13",
         9: "AA15",  10: "AB15",
        11: "Y15",   12: "Y14",
        13: "AB18",  14: "AB17",
        15: "Y17",   16: "Y16",
        17: "AA18",  18: "AA17",
        19: "AA20",  20: "AA19",
        21: "Y20",   22: "Y19",
        23: "AB21",  24: "AB20",
        25: "AA22",  26: "AB22",
        27: "W22",   28: "Y22",
        29: "Y21",   30: "W21",
        31: "U22",   32: "V21",
        33: "V20",   34: "W19",
        35: "U21",   36: "U20",
        37: "R22",   38: "T22",
        39: "P22",   40: "R21",
        41: "T20",   42: "T19",
        43: "P16",   44: "P17",
        45: "N20",   46: "N21",
        47: "M21",   48: "M20",
        49: "M18",   50: "N19",
        51: "L18",   52: "L19",
        53: "M22",   54: "L22",
        55: "L17",   56: "K17",
        57: "K22",   58: "K21",
        59: "M16",   60: "N16",
    })
]

# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6
    core_resources = [
        ("user_led", 0, Pins("D17"), IOStandard("3.3-V LVTTL")),
        ("serial", 0,
            Subsignal("tx", Pins("J3:7"), IOStandard("3.3-V LVTTL")),
            Subsignal("rx", Pins("J3:8"), IOStandard("3.3-V LVTTL"))
        ),
 ]

    def __init__(self, toolchain="quartus", with_daughterboard=False):
        device = "5CEFA2F23C8"
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
