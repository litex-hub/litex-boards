#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform, VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("rst",    0, Pins("G13"), IOStandard("LVCMOS18")),
    ("clk125", 0,
        Subsignal("p", Pins("H9"), IOStandard("DIFF_SSTL15")),
        Subsignal("n", Pins("G9"), IOStandard("DIFF_SSTL15")),
    ),

    # Leds
    ("user_led", 0, Pins("AL11"), IOStandard("LVCMOS12")),
    ("user_led", 1, Pins("AL13"), IOStandard("LVCMOS12")),
    ("user_led", 2, Pins("AK13"), IOStandard("LVCMOS12")),
    ("user_led", 3, Pins("AE15"), IOStandard("LVCMOS12")),
    ("user_led", 4, Pins("AM8"),  IOStandard("LVCMOS12")),
    ("user_led", 5, Pins("AM9"),  IOStandard("LVCMOS12")),
    ("user_led", 6, Pins("AM10"), IOStandard("LVCMOS12")),
    ("user_led", 7, Pins("AM11"), IOStandard("LVCMOS12")),

    # Serial
    ("serial", 0,
        Subsignal("cts", Pins("AP17")),
        Subsignal("rts", Pins("AM15")),
        Subsignal("tx",  Pins("AL17")),
        Subsignal("rx",  Pins("AH17")),
        IOStandard("LVCMOS12")
    ),
]


# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "clk125"
    default_clk_period = 1e9/125e6

    def __init__(self):
        XilinxPlatform.__init__(self, "xczu7ev-ffvc1156-2-e", _io, toolchain="vivado")

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk125", loose=True), 1e9/125e6)
