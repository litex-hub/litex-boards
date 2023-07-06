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
    ("cpu_reset", 0, Pins("P8"), IOStandard("LVCMOS33")),

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

_connectors = []

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

