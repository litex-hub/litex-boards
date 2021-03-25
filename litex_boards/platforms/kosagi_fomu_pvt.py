#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019 Tom Keddie <git@bronwenandtom.com>
# SPDX-License-Identifier: BSD-2-Clause

# Fomu PVT board:
# - Crowd Supply campaign: https://www.crowdsupply.com/sutajio-kosagi/fomu
# - Design files: https://github.com/im-tomu/fomu-hardware/tree/pvt/hardware/pcb

from litex.build.generic_platform import *
from litex.build.lattice import LatticePlatform
from litex.build.lattice.programmer import IceStormProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk48", 0, Pins("F4"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led_n", 0, Pins("A5"), IOStandard("LVCMOS33")),
    ("rgb_led", 0,
        Subsignal("r", Pins("C5")),
        Subsignal("g", Pins("B5")),
        Subsignal("b", Pins("A5")),
        IOStandard("LVCMOS33")
    ),

    # Buttons
    ("user_touch_n", 0, Pins("E4"), IOStandard("LVCMOS33")),
    ("user_touch_n", 1, Pins("D5"), IOStandard("LVCMOS33")),
    ("user_touch_n", 2, Pins("E5"), IOStandard("LVCMOS33")),
    ("user_touch_n", 3, Pins("F5"), IOStandard("LVCMOS33")),

    # USB
    ("usb", 0,
        Subsignal("d_p", Pins("A1")),
        Subsignal("d_n", Pins("A2")),
        Subsignal("pullup", Pins("A4")),
        IOStandard("LVCMOS33")
    ),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("C1"), IOStandard("LVCMOS33")),
        Subsignal("clk",  Pins("D1"), IOStandard("LVCMOS33")),
        Subsignal("mosi", Pins("F1"), IOStandard("LVCMOS33")),
        Subsignal("miso", Pins("E1"), IOStandard("LVCMOS33")),
        Subsignal("wp",   Pins("F2"), IOStandard("LVCMOS33")),
        Subsignal("hold", Pins("B1"), IOStandard("LVCMOS33")),
    ),
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("C1"), IOStandard("LVCMOS33")),
        Subsignal("clk",  Pins("D1"), IOStandard("LVCMOS33")),
        Subsignal("dq",   Pins("F1 E1 F2 B1"), IOStandard("LVCMOS33")),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("touch_pins", "E4 D5 E5 F5"),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticePlatform):
    default_clk_name   = "clk48"
    default_clk_period = 1e9/48e6

    def __init__(self, toolchain="icestorm"):
        LatticePlatform.__init__(self, "ice40-up5k-uwg30", _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        return IceStormProgrammer()

    def do_finalize(self, fragment):
        LatticePlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk48", loose=True), 1e9/48e6)
