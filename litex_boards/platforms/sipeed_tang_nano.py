#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# Board diagram/pinout:
# https://user-images.githubusercontent.com/1450143/133655492-532d5e9a-0635-4889-85c9-68683d06cae0.png
# http://dl.sipeed.com/TANG/Nano/HDK/Tang-NANO-2704(Schematic).pdf

from migen import *

from litex.build.generic_platform import *
from litex.build.gowin.platform import GowinPlatform
from litex.build.openfpgaloader import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk24",  0, Pins("35"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led", 0, Pins("16"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("17"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("18"), IOStandard("LVCMOS33")),

    # Buttons.
    ("user_btn", 0, Pins("15"),  IOStandard("LVCMOS33")),
    ("user_btn", 1, Pins("14"),  IOStandard("LVCMOS33")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("8")),
        Subsignal("rx", Pins("9")),
        IOStandard("LVCMOS33")
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = []

# Platform -----------------------------------------------------------------------------------------

class Platform(GowinPlatform):
    default_clk_name   = "clk24"
    default_clk_period = 1e9/24e6

    def __init__(self, toolchain="gowin"):
        GowinPlatform.__init__(self, "GW1N-LV1QN48C6/I5", _io, _connectors, toolchain=toolchain, devicename="GW1N-1")
        self.toolchain.options["use_done_as_gpio"]      = 1
        self.toolchain.options["use_reconfign_as_gpio"] = 1

    def create_programmer(self):
        return OpenFPGALoader("tangnano")

    def do_finalize(self, fragment):
        GowinPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk24", loose=True), 1e9/24e6)
