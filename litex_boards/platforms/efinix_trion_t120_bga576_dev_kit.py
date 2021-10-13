#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Franck Jullien <franck.jullien@collshade.fr>
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.efinix.platform import EfinixPlatform
from litex.build.efinix import EfinixProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk
    ("clk40", 0, Pins("P19"), IOStandard("3.3_V_LVTTL_/_LVCMOS")),

    # Leds
    ("user_led", 0, Pins("AB16"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=3")),
    ("user_led", 1, Pins("AA16"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=3")),
    ("user_led", 2, Pins("AA15"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=3")),
    ("user_led", 3, Pins("Y15"),  IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=3")),
    ("user_led", 4, Pins("Y16"),  IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=3")),
    ("user_led", 5, Pins("W16"),  IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=3")),
    ("user_led", 6, Pins("AD16"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=3")),
    ("user_led", 7, Pins("AC16"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=3")),

    # Buttons
    ("user_btn", 0, Pins("AD15"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("WEAK_PULLUP")),
    ("user_btn", 1, Pins("AC15"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("WEAK_PULLUP")),
    ("user_btn", 2, Pins("W15"),  IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("WEAK_PULLUP")),
    ("user_btn", 3, Pins("V15"),  IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("WEAK_PULLUP")),

    # Serial / PMOD USB-UART on PMOD E.
    ("serial", 0,
        Subsignal("tx", Pins("B23")),
        Subsignal("rx", Pins("A20")),
        IOStandard("3.3_V_LVTTL_/_LVCMOS")
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(EfinixPlatform):
    default_clk_name   = "clk40"
    default_clk_period = 1e9/40e6

    def __init__(self):
        EfinixPlatform.__init__(self, "T120F576", _io, toolchain="efinity")

    def create_programmer(self):
        return EfinixProgrammer()

    def do_finalize(self, fragment):
        EfinixPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk40", loose=True), 1e9/40e6)
