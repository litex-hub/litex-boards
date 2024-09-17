#
# This file is part of LiteX-Boards.
# Copyright (c) 2024, Signaloid <developer-support@signaloid.com>
# SPDX-License-Identifier: BSD-2-Clause

# Signaloid C0-microSD FPGA SoM:
# - Documentation: https://c0-microsd-docs.signaloid.io/
# - GitHub HomePage: https://github.com/signaloid/C0-microSD-Hardware

from litex.build.generic_platform import IOStandard, Misc, Pins, Subsignal
from litex.build.lattice import LatticeiCE40Platform

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk12", 0, Pins("B3"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led", 0, Pins("B5"), IOStandard("LVCMOS33")), # Red
    ("user_led", 1, Pins("A5"), IOStandard("LVCMOS33")), # Green

    # Serial
    ("serial", 0,
        Subsignal("rx", Pins("B3")),
        Subsignal("tx", Pins("A4"), Misc("PULLUP")),
        IOStandard("LVCMOS33")
    ),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("C1")),
        Subsignal("clk",  Pins("D1")),
        Subsignal("mosi", Pins("F1")),
        Subsignal("miso", Pins("E1")),
        IOStandard("LVCMOS18"),
    ),

    # SD Breakout pins
    ("SD_DAT0", 0, Pins("A1"), IOStandard("LVCMOS33")),
    ("SD_DAT1", 0, Pins("A2"), IOStandard("LVCMOS33")),
    ("SD_DAT2", 0, Pins("E5"), IOStandard("LVCMOS33")),
    ("SD_DAT3", 0, Pins("F5"), IOStandard("LVCMOS33")),
    ("SD_CMD",  0, Pins("A4"), IOStandard("LVCMOS33")),
    ("SD_CLK",  0, Pins("B3"), IOStandard("LVCMOS33")),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = []

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticeiCE40Platform):
    default_clk_name   = "clk12"
    default_clk_period = 1e9/12e6

    def __init__(self, toolchain="icestorm"):
        LatticeiCE40Platform.__init__(self, "ice40-up5k-uwg30", _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        print("\033[93m")
        print("-------------------------------------------------------------------------------")
        print("Programming is not supported for this platform.")
        print("Please use the official Signaloid C0-microSD utilities for flashing the device.")
        print("https://github.com/signaloid/C0-microSD-utilities")
        print("-------------------------------------------------------------------------------")
        print("\033[0m")
        return None

    def do_finalize(self, fragment):
        LatticeiCE40Platform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk12", loose=True), 1e9/12e6)
