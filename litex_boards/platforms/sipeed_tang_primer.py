#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Miodrag Milanovic <mmicko@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

#
# Tech data:
# https://tang.sipeed.com/en/hardware-overview/lichee-tang/
#
# Board diagram/pinout:
# https://tang.sipeed.com/hardware-overview/lichee-tang/images/newtang_pinout.png
# https://tang.sipeed.com/hardware-overview/lichee-tang/images/E203_pin.png

from migen import *

from litex.build.generic_platform import *
from litex.build.anlogic.platform import AnlogicPlatform
from litex.build.openfpgaloader import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk24",  0, Pins("K14"), IOStandard("LVCMOS33")),

    # RGB LED
    ("user_led", 0, Pins("R3"), IOStandard("LVCMOS33")),  # R
    ("user_led", 1, Pins("J14"), IOStandard("LVCMOS33")), # G
    ("user_led", 2, Pins("P13"), IOStandard("LVCMOS33")), # B

    # Buttons.
    ("user_btn", 0, Pins("K16"),  IOStandard("LVCMOS33")), # USER_KEY

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("J13")),
        Subsignal("rx", Pins("H13")),
        IOStandard("LVCMOS33")
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = []

# Platform -----------------------------------------------------------------------------------------

class Platform(AnlogicPlatform):
    default_clk_name   = "clk24"
    default_clk_period = 1e9/24e6

    def __init__(self, toolchain="td"):
        AnlogicPlatform.__init__(self, "EG4S20BG256", _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        return OpenFPGALoader("licheeTang")

    def do_finalize(self, fragment):
        AnlogicPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk24", loose=True), 1e9/24e6)
