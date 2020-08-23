#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019 Tom Keddie <git@bronwenandtom.com>
# Copyright (c) 2019 Sean Cross <sean@xobs.io>
# SPDX-License-Identifier: BSD-2-Clause

# Fomu EVT board:
# - Crowd Supply campaign: https://www.crowdsupply.com/sutajio-kosagi/fomu
# - Design files: https://github.com/im-tomu/fomu-hardware/tree/evt/hardware/pcb

from litex.build.generic_platform import *
from litex.build.lattice import LatticePlatform
from litex.build.lattice.programmer import IceStormProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    ("clk48", 0, Pins("44"), IOStandard("LVCMOS33")),

    ("user_led_n", 0, Pins("41"), IOStandard("LVCMOS33")),
    ("rgb_led", 0,
        Subsignal("r", Pins("40")),
        Subsignal("g", Pins("39")),
        Subsignal("b", Pins("41")),
        IOStandard("LVCMOS33"),
    ),

    ("user_btn_n", 0, Pins("42"), IOStandard("LVCMOS33")),
    ("user_btn_n", 1, Pins("38"), IOStandard("LVCMOS33")),

    ("serial", 0,
        Subsignal("rx", Pins("21")),
        Subsignal("tx", Pins("13"), Misc("PULLUP")),
        IOStandard("LVCMOS33")
    ),

    ("usb", 0,
        Subsignal("d_p", Pins("34")),
        Subsignal("d_n", Pins("37")),
        Subsignal("pullup",   Pins("35")),
        Subsignal("pulldown", Pins("36")),
        IOStandard("LVCMOS33")
    ),

    ("spiflash", 0,
        Subsignal("cs_n", Pins("16"), IOStandard("LVCMOS33")),
        Subsignal("clk",  Pins("15"), IOStandard("LVCMOS33")),
        Subsignal("miso", Pins("17"), IOStandard("LVCMOS33")),
        Subsignal("mosi", Pins("14"), IOStandard("LVCMOS33")),
        Subsignal("wp",   Pins("18"), IOStandard("LVCMOS33")),
        Subsignal("hold", Pins("19"), IOStandard("LVCMOS33")),
    ),

    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("16"), IOStandard("LVCMOS33")),
        Subsignal("clk",  Pins("15"), IOStandard("LVCMOS33")),
        Subsignal("dq",   Pins("14 17 18 19"), IOStandard("LVCMOS33")),
    ),
    ("i2c", 0,
        Subsignal("scl", Pins("12"), IOStandard("LVCMOS18")),
        Subsignal("sda", Pins("20"), IOStandard("LVCMOS18")),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("touch_pins", "48 47 46 45"),
    ("pmoda_n",    "28 27 26 23"),
    ("pmodb_n",    "48 47 46 45"),
    ("dbg",        "20 12 11 25 10 9"),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticePlatform):
    default_clk_name   = "clk48"
    default_clk_period = 1e9/48e6

    def __init__(self):
        LatticePlatform.__init__(self, "ice40-up5k-sg48", _io, _connectors, toolchain="icestorm")

    def create_programmer(self):
        return IceStormProgrammer()

    def do_finalize(self, fragment):
        LatticePlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk48", loose=True), 1e9/48e6)
