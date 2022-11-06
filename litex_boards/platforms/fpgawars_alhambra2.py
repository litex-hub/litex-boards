#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 JM Robles <roblesjm@gmail.com>
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.lattice import LatticeiCE40Platform
from litex.build.lattice.programmer import IceStormProgrammer

_io = [

    # Clock
    ("clk12", 0, Pins("49"), IOStandard("LVCMOS33")),
    # Leds
    ("user_leds", 0, Pins("45"), IOStandard("LVCMOS33")),
    ("user_leds", 1, Pins("44"), IOStandard("LVCMOS33")),
    ("user_leds", 2, Pins("43"), IOStandard("LVCMOS33")),
    ("user_leds", 3, Pins("42"), IOStandard("LVCMOS33")),
    ("user_leds", 4, Pins("41"), IOStandard("LVCMOS33")),
    ("user_leds", 5, Pins("39"), IOStandard("LVCMOS33")),
    ("user_leds", 6, Pins("38"), IOStandard("LVCMOS33")),
    ("user_leds", 7, Pins("37"), IOStandard("LVCMOS33")),
    # Switches
    ("sw1", 0, Pins("34"), IOStandard("LVCMOS33")),
    ("sw2", 0, Pins("33"), IOStandard("LVCMOS33")),

    # Serial
    ("serial", 0, 
        Subsignal("rx", Pins("62"), IOStandard("LVCMOS33")),
        Subsignal("tx", Pins("61"), IOStandard("LVCMOS33")),
    ),
    # SPI
    (
        "spiflash", 0, 
        Subsignal("cs_n", Pins("71")),
        Subsignal("clk", Pins("70")),
        Subsignal("mosi", Pins("67")),
        Subsignal("miso", Pins("68")),
        IOStandard("LVCMOS33")

    ),
    # ADC
    (
        "adc", 0,
        Subsignal("int", Pins(90)),
        Subsignal("sda", Pins(83)),
        Subsignal("scl", Pins(84)),
        IOStandard("LVCMOS33")
    )

]

_connectors = [
    ("d0", "2"),
    ("d1", "1"),
    ("d2", "4"),
    ("d3", "3"),
    ("d4", "8"),
    ("d5", "7"),
    ("d6", "10"),
    ("d7", "9"),
    ("d8", "20"),
    ("d9", "19"),
    ("d10", "22"),
    ("d11", "21"),
    ("d12", "63"),
    ("d13", "64"),

    ("a0", "114"),
    ("a1", "115"),
    ("a2", "116"),
    ("a3", "117"),
]

# Platform -------------------------------------------------------------------------------

class Platform(LatticeiCE40Platform):

    default_clk_name = "clk12"
    default_clk_period = 1e9/12e6

    def __init__(self, toolchain="icestorm", **kwargs):

        LatticeiCE40Platform.__init__(self, "ice40-hx8k-tq144:4k", _io, _connectors, toolchain=toolchain, **kwargs)

    def create_programmer(self, mode="direct"):

        return IceStormProgrammer()

    def do_finalize(self, fragment):
        LatticeiCE40Platform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk12", loose=True), 1e9/12e6)

