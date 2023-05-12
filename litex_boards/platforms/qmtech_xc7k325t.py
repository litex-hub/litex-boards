#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2023 Kazumoto Kojima
# Copyright (c) 2023 Hans Baier <hansfbaier@gmail.com>
#
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import Pins, Subsignal, IOStandard, Misc
from litex.build.xilinx import XilinxPlatform
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk50", 0, Pins("F22"), IOStandard("LVCMOS33")),

    # The core board does not have a USB serial on it,
    # so you will have to attach an USB to serial adapter
    # on these pins
    ("gpio_serial", 0,
        Subsignal("tx", Pins("J2:7")),
        Subsignal("rx", Pins("J2:8")),
        IOStandard("LVCMOS33")
    ),

    # SPIFlash
    # S25FL256L
    ("spiflash4x", 0,  # clock needs to be accessed through STARTUPE2
        Subsignal("cs_n", Pins("C23")),
        Subsignal("clk",  Pins("C8")),
        Subsignal("dq",   Pins("B24", "A25", "B22", "A22")),
        IOStandard("LVCMOS33")
    ),

    # DDR3 SDRAM
    # MT41J128M16JT-125K
    ("ddram", 0,
        Subsignal("a", Pins("AF5 AF2 AD6 AC6 AD4 AB6 AE2 Y5 AA4 AE6 AE3 AD5 AB4 Y6"),
            IOStandard("SSTL15")),
        Subsignal("ba", Pins("AD3 AE1 AE5"), IOStandard("SSTL15")),
        Subsignal("ras_n", Pins("AC3"),      IOStandard("SSTL15")),
        Subsignal("cas_n", Pins("AC4"),      IOStandard("SSTL15")),
        Subsignal("we_n",  Pins("AF4"),      IOStandard("SSTL15")),
        #Subsignal("cs_n", Pins("--"),       IOStandard("SSTL15")),
        Subsignal("dm", Pins("V1 V3"),       IOStandard("SSTL15")),
        Subsignal("dq", Pins(
            "W1 V2 Y1 Y3 AC2 Y2 AB2 AA3",
            "U1 V4 U6 W3 V6 U2 U7 U5"),
            IOStandard("SSTL15")), # _T_DCI")),

        Subsignal("dqs_p", Pins("AB1 W6"), IOStandard("DIFF_SSTL15")), # _T_DCI")),
        Subsignal("dqs_n", Pins("AC1 W5"), IOStandard("DIFF_SSTL15")), # _T_DCI")),

        Subsignal("clk_p", Pins("AA5"),    IOStandard("DIFF_SSTL15")),
        Subsignal("clk_n", Pins("AB5"),    IOStandard("DIFF_SSTL15")),

        Subsignal("cke",   Pins("AD1"),    IOStandard("SSTL15")),
        Subsignal("odt",   Pins("AF3"),    IOStandard("SSTL15")),
        Subsignal("reset_n", Pins("W4"),   IOStandard("LVCMOS15")),
        Misc("SLEW=FAST"),
    ),
]

# The connectors are named after the daughterboard, not the core board
# because on the different core boards the names vary, but on the
# daughterboard they stay the same, which we need to connect the
# daughterboard peripherals to the core board.
# On this board J2 is U5 and J3 is U4
_connectors = [
    ("J2", {
         # odd row     even row
          7: "A8",    8: "A9",
          9: "B9",   10: "C9",
         11: "A10",  12: "B10",
         13: "D10",  14: "E10",
         15: "B11",  16: "B12",
         17: "C11",  18: "C12",
         19: "A12",  20: "A13",
         21: "D13",  22: "D14",
         23: "A14",  24: "B14",
         25: "C13",  26: "C14",
         27: "A15",  28: "B15",
         29: "D16",  30: "D15",
         31: "B16",  32: "C16",
         33: "A17",  34: "B17",
         35: "D18",  36: "E18",
         37: "C18",  38: "C17",
         39: "A19",  40: "A18",
         41: "B19",  42: "C19",
         43: "A20",  44: "B20",
         45: "D20",  46: "D19",
         47: "A24",  48: "A23",
         49: "E22",  50: "E21",
         51: "D24",  52: "D23",
         53: "D25",  54: "E25",
         55: "E26",  56: "F25",
         57: "B26",  58: "B25",
         59: "C26",  60: "D26",
    }),
    ("J3", {
        # odd row     even row
         7: "AD21",   8: "AE21",
         9: "AE22",  10: "AF22",
        11: "AE23",  12: "AF23",
        13: "V21",   14: "W21",
        15: "Y22",   16: "AA22",
        17: "AF24",  18: "AF25",
        19: "AB21",  20: "AC21",
        21: "AB22",  22: "AC22",
        23: "AD23",  24: "AD24",
        25: "AC23",  26: "AC24",
        27: "AD25",  28: "AE25",
        29: "AA23",  30: "AB24",
        31: "AA25",  32: "AB25",
        33: "Y23",   34: "AA24",
        35: "AD26",  36: "AE26",
        37: "AB26",  38: "AC26",
        39: "W23",   40: "W24",
        41: "Y25",   42: "Y26",
        43: "W25",   44: "W26",
        45: "U26",   46: "V26",
        47: "V23",   48: "V24",
        49: "U24",   50: "U25",
        51: "T22",   52: "T23",
        53: "R22",   54: "R23",
        55: "R25",   56: "P25",
        57: "P23",   58: "N23",
        59: "N26",   60: "M26",
    })
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6

    core_resources_daughterboard = [
        ("onboard_led_1", 0, Pins("J26"), IOStandard("LVCMOS33")),
        ("onboard_led_2", 0, Pins("H26"), IOStandard("LVCMOS33")),
        ("cpu_reset", 0, Pins("AD21"), IOStandard("LVCMOS33")),
    ]

    core_resources_standalone = [
        ("user_led", 0, Pins("J26"), IOStandard("LVCMOS33")),
        ("user_led", 1, Pins("H26"), IOStandard("LVCMOS33")),
        ("cpu_reset", 0, Pins("AD21"), IOStandard("LVCMOS33")),
    ]

    def __init__(self, toolchain="vivado", with_daughterboard=False):
        device = "xc7k325tffg676-1"
        io = _io
        connectors = _connectors

        if with_daughterboard:
            io += self.core_resources_daughterboard
            from litex_boards.platforms.qmtech_daughterboard import QMTechDaughterboard
            daughterboard = QMTechDaughterboard(IOStandard("LVCMOS33"))
            io += daughterboard.io
            connectors += daughterboard.connectors
        else:
            io += self.core_resources_standalone

        XilinxPlatform.__init__(self, device, io, connectors, toolchain=toolchain)

        self.add_platform_command("set_property INTERNAL_VREF 0.750 [get_iobanks 34]")
        self.add_platform_command("set_property INTERNAL_VREF 0.90  [get_iobanks 33]")

    def create_programmer(self):
        bscan_spi = "bscan_spi_xc7k325t.bit"
        return OpenOCD("openocd_xc7_ft2232.cfg", bscan_spi)


    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
