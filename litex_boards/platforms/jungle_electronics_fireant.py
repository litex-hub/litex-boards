#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Miodrag Milanovic <mmicko@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

# Board schematics at:
# https://github.com/jungle-elec/FireAnt


from litex.build.generic_platform import *
from litex.build.efinix.platform import EfinixPlatform
from litex.build.openfpgaloader import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk
    ("clk33", 0, Pins("C3"), IOStandard("3.3_V_LVTTL_/_LVCMOS")),

    # Leds
    ("user_led", 0, Pins("C5"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=1")),
    ("user_led", 1, Pins("B6"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=1")),
    ("user_led", 2, Pins("C7"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=1")),
    ("user_led", 3, Pins("A9"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=1")),

    # Buttons
    ("user_btn", 0, Pins("J9"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("WEAK_PULLUP")),
    ("user_btn", 1, Pins("J8"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("WEAK_PULLUP")),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("J4")),
        Subsignal("clk",  Pins("H4")),
        Subsignal("mosi", Pins("F4")),
        Subsignal("miso", Pins("H3")),
        IOStandard("3.3_V_LVTTL_/_LVCMOS")
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ["J1", " - G5 G4 J3 G3 J2 H2 F3 G1 F1 E2 E1 C2 D2 E3 D3 B3 A5 B5 -"],
    ["J2", " -  - H8 G8 H9 G9 F5 F6 F7 E7 F8 E8 D9 B9 C8 B8 A8 C6 A6 -"],
]

# Platform -----------------------------------------------------------------------------------------

class Platform(EfinixPlatform):
    default_clk_name   = "clk33"
    default_clk_period = 1e9/33.33e6

    def __init__(self, toolchain="efinity"):
        EfinixPlatform.__init__(self, "T8F81C2", _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        return OpenFPGALoader("fireant")

    def do_finalize(self, fragment):
        EfinixPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk33", loose=True), 1e9/33.33e6)
