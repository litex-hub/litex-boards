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
    ("clk50", 0, Pins("E1"), IOStandard("3.3-V LVTTL")),

    # Button
    ("key", 0, Pins("F3"),  IOStandard("3.3-V LVTTL")),
    ("key", 1, Pins("J6"),  IOStandard("3.3-V LVTTL")),

    # SPIFlash (W25Q64)
    ("spiflash", 0,
        # clk
        Subsignal("cs_n", Pins("D2")),
        Subsignal("clk",  Pins("H1")),
        Subsignal("mosi", Pins("C1")),
        Subsignal("miso", Pins("H2")),
        IOStandard("3.3-V LVTTL"),
    ),

    # SDR SDRAM
    ("sdram_clock", 0, Pins("P2"), IOStandard("3.3-V LVTTL")),
    ("sdram", 0,
        Subsignal("a",     Pins(
            "R7 T7 R8 T8 R6 T5 R5 T4",
            "R4 T3 T6 R3 T2")),
        Subsignal("ba",    Pins("N8 L8")),
        Subsignal("cs_n",  Pins("P8")),
        Subsignal("cke",   Pins("R1")),
        Subsignal("ras_n", Pins("M8")),
        Subsignal("cas_n", Pins("M7")),
        Subsignal("we_n",  Pins("P6")),
        Subsignal("dq", Pins(
            "K5 L3 L4 K6 N3 M6 P3 N5",
            "N2 N1 L1 L2 K1 K2 J1 J2")),
        Subsignal("dm", Pins("N6 P1")),
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
          7: "G1",    8: "G2",
          9: "D1",   10: "C2",
         11: "B1",   12: "F5",
         13: "D3",   14: "C3",
         15: "B3",   16: "A3",
         17: "B4",   18: "A4",
         19: "E5",   20: "A2",
         21: "D4",   22: "E6",
         23: "C6",   24: "D6",
         25: "B5",   26: "A5",
         27: "B6",   28: "A6",
         29: "B7",   30: "A7",
         31: "D8",   32: "C8",
         33: "D9",   34: "C9",
         35: "B8",   36: "A8",
         37: "B9",   38: "A9",
         39: "E9",   40: "E8",
         41: "E11",  42: "E10",
         43: "A10",  44: "B10",
         45: "D12",  46: "D11",
         47: "B11",  48: "A11",
         49: "B12",  50: "A12",
         51: "B13",  52: "A13",
         53: "B14",  54: "A14",
         55: "D14",  56: "C14",
         57: "B16",  58: "A15",
         59: "C16",  60: "C15",
    }),
    ("J3", {
        # odd row     even row
         7: "R9",     8: "T9",
         9: "R10",   10: "T10",
        11: "R11",   12: "T11",
        13: "R12",   14: "T12",
        15: "N9",    16: "M9",
        17: "M10",   18: "P9",
        19: "P11",   20: "N11",
        21: "R13",   22: "T13",
        23: "T15",   24: "T14",
        25: "N12",   26: "M11",
        27: "R14",   28: "N13",
        29: "N14",   30: "P14",
        31: "P16",   32: "R16",
        33: "N16",   34: "N15",
        35: "M16",   36: "M15",
        37: "L16",   38: "L15",
        39: "P15",   40: "M12",
        41: "L14",   42: "L13",
        43: "K16",   44: "K15",
        45: "K12",   46: "J12",
        47: "J14",   48: "J13",
        49: "K11",   50: "J11",
        51: "G11",   52: "F11",
        53: "F13",   54: "F14",
        55: "F10",   56: "F9",
        57: "E16",   58: "E15",
        59: "D16",   60: "D15",
    })
]

# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6
    core_resources = [
        ("user_led", 0, Pins("L9"), IOStandard("3.3-V LVTTL")),
        ("serial", 0,
            # Compatible with cheap FT232 based cables (ex: Gaoominy 6Pin Ftdi Ft232Rl Ft232)
            Subsignal("tx", Pins("J3:7"), IOStandard("3.3-V LVTTL")), # GPIO_07 (JP1 Pin 10)
            Subsignal("rx", Pins("J3:8"), IOStandard("3.3-V LVTTL"))  # GPIO_05 (JP1 Pin 8)
        ),
    ]

    def __init__(self, toolchain="quartus", with_daughterboard=False):
        device = "10CL006YU256C8G"
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

        # Generate PLL clock in STA
        self.toolchain.additional_sdc_commands.append("derive_pll_clocks")
        # Calculates clock uncertainties
        self.toolchain.additional_sdc_commands.append("derive_clock_uncertainty")

    def create_programmer(self):
        return USBBlaster()

    def do_finalize(self, fragment):
        AlteraPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
