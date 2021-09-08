#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.build.generic_platform import *
from litex.build.gowin.platform import GowinPlatform
from litex.build.openfpgaloader import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk27",  0, Pins("45"), IOStandard("LVCMOS33")),
    ("rst_n",  0, Pins("15"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led", 0, Pins("10"), IOStandard("LVCMOS33")),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = []

# Platform -----------------------------------------------------------------------------------------

class Platform(GowinPlatform):
    default_clk_name   = "clk27"
    default_clk_period = 1e9/27e6

    def __init__(self):
        GowinPlatform.__init__(self, "GW1NSR-LV4CQN48PC7/I6", _io, _connectors, toolchain="gowin", devicename="GW1NSR-4C")
        self.toolchain.options["use_mode_as_gpio"] = 1

    def create_programmer(self):
        return OpenFPGALoader("tangnano")

    def do_finalize(self, fragment):
        GowinPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk27", loose=True), 1e9/100e6)
