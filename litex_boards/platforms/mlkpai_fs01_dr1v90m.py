#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 Junhui Liu <junhui.liu@pigmoral.tech>
# SPDX-License-Identifier: BSD-2-Clause

#
# Board Info:
# https://www.milianke.com/product-item-104.html

from migen import *

from litex.build.generic_platform import *
from litex.build.anlogic.platform import AnlogicPlatform
from litex.build.anlogic.programmer import TangDynastyProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk25",  0, Pins("L18"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led", 0, Pins("L21"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("L22"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("M21"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("M22"), IOStandard("LVCMOS33")),
    ("user_led", 4, Pins("N22"), IOStandard("LVCMOS33")),
    ("user_led", 5, Pins("P20"), IOStandard("LVCMOS33")),
    ("user_led", 6, Pins("P22"), IOStandard("LVCMOS33")),
    ("user_led", 7, Pins("P21"), IOStandard("LVCMOS33")),

    # Buttons.
    ("user_btn", 0, Pins("U22"),  IOStandard("LVCMOS18")),
    ("user_btn", 1, Pins("T22"),  IOStandard("LVCMOS18")),
    ("user_btn", 2, Pins("T21"),  IOStandard("LVCMOS18")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("V18")),
        Subsignal("rx", Pins("V19")),
        IOStandard("LVCMOS18")
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = []

# Platform -----------------------------------------------------------------------------------------

class Platform(AnlogicPlatform):
    default_clk_name   = "clk25"
    default_clk_period = 1e9/25e6

    def __init__(self, toolchain="td"):
        AnlogicPlatform.__init__(self, "DR1V90MEG484", _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        return TangDynastyProgrammer()

    def do_finalize(self, fragment):
        AnlogicPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk25", loose=True), 1e9/25e6)
