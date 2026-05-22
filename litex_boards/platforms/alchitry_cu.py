#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2023 Nimalan M <nimalan.m@protonmail.com>
# SPDX-License-Identifier: BSD-2-Clause

# The Alchitry Cu is FPGA Development board
# by SparkFun - https://www.sparkfun.com/products/16526.
#
# It has a Lattice ICE40HX8K-CB132IC and can be programmed
# with the Icestorm toolchain
# Schematic - https://cdn.sparkfun.com/assets/2/6/e/5/e/alchitry_cu_sch_update.pdf

from litex.build.generic_platform import *
from litex.build.lattice import LatticeiCE40Platform
from litex.build.lattice.programmer import IceStormProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk100", 0, Pins("P7"), IOStandard("LVCMOS33")),
    ("cpu_reset_n", 0, Pins("P8"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led", 0, Pins("J11"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("K11"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("K12"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("K14"), IOStandard("LVCMOS33")),
    ("user_led", 4, Pins("L12"), IOStandard("LVCMOS33")),
    ("user_led", 5, Pins("L14"), IOStandard("LVCMOS33")),
    ("user_led", 6, Pins("M12"), IOStandard("LVCMOS33")),
    ("user_led", 7, Pins("N14"), IOStandard("LVCMOS33")),

    # Serial
    ("serial", 0,
        Subsignal("rx", Pins("P14")),
        Subsignal("tx", Pins("M9")),
        IOStandard("LVCMOS33")
    ),

    # Onboard QWIIC
    ("i2c", 0,
        Subsignal("scl", Pins("A4")),
        Subsignal("sda", Pins("A3")),
        IOStandard("LVCMOS33"),
    ),

    # SPIFlash X25XXSMD1
    ("spiflash", 0,
        Subsignal("mosi", Pins("M11")),
        Subsignal("miso", Pins("P11")),
        Subsignal("clk",  Pins("P12")),
        Subsignal("cs_n", Pins("P13")),
        IOStandard("LVCMOS33")
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("A", { # X3.
         2: "M1",  3: "L1",
         5: "J1",  6: "J3",
         8: "G1",  9: "G3",
        11: "E1", 12: "D1",
        14: "C1", 15: "B1",
        17: "D3", 18: "C3",
        20: "A1", 21: "A2",
        23: "A3", 24: "A4",
        27: "A5", 28: "C5",
        30: "D5", 31: "C4",
        33: "D4", 34: "E4",
        36: "F4", 37: "F3",
        39: "H4", 40: "G4",
        42: "H1", 43: "H3",
        45: "K3", 46: "K4",
        48: "N1", 49: "P1",
    }),
    ("B", { # X4.
         2: "A6",  3: "A7",
         5: "A10", 6: "A11",
         8: "C9",  9: "C10",
        11: "A12", 12: "B14",
        14: "C14", 15: "D14",
        17: "E14", 18: "E12",
        20: "F14", 21: "G14",
        23: "H12", 24: "J12",
        27: "H11", 28: "G11",
        30: "G12", 31: "F12",
        33: "F11", 34: "E11",
        36: "D12", 37: "D11",
        39: "C12", 40: "C11",
        42: "D10", 43: "D9",
        45: "D7",  46: "D6",
        48: "C7",  49: "C6",
    }),
    ("C", { # X5.
         2: "M3",  3: "M4",
         5: "L4",  6: "L5",
         8: "M6",  9: "M7",
        12: "L9",
        27: "M11", 28: "P11",
        36: "M9", 37: "P14",
        38: "P10", 39: "P9",
        42: "L8", 43: "L6",
        45: "P5", 46: "P4",
        48: "P3", 49: "P2",
    }),
    ("D", { # X6.
         2: "K12", 3: "K14",
         5: "M12", 6: "N14",
        27: "P12", 28: "P13",
        38: "P8",  39: "P7",
        45: "L14", 46: "L12",
        48: "K11", 49: "J11",
    }),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticeiCE40Platform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self, toolchain="icestorm", **kwargs):
        LatticeiCE40Platform.__init__(self, "ice40-hx8k-cb132", _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        return IceStormProgrammer()

    def do_finalize(self, fragment):
        LatticeiCE40Platform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100", loose=True), 1e9/100e6)
