#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Andrew Dennison <andrew@motec.com.au>
# Copyright (c) 2022 Charles-Henri Mousset <ch.mousset@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

import os
from litex.build.generic_platform import *
from litex.build.efinix.platform import EfinixPlatform
from litex.build.efinix.programmer import EfinixAtmelProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk
    ("clk33", 0, Pins("C3"), IOStandard("3.3_V_LVTTL_/_LVCMOS")),  # net PLL_IN

    # Buttons
    ("user_btn", 0, Pins("G1"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("WEAK_PULLUP")),
    ("user_btn", 1, Pins("F1"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("WEAK_PULLUP")),

    # Leds
    ("user_led", 0, Pins("G4"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=3")),
    ("user_led", 1, Pins("J2"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=3")),
    ("user_led", 2, Pins("C2"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=3")),
    ("user_led", 3, Pins("E3"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=3")),
    ("user_led", 4, Pins("B3"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=3")),

    # SPIFlash (W25Q80DV)
    ("spiflash", 0,
        Subsignal("cs_n", Pins("J4")),  # net SPI_SS
        Subsignal("clk",  Pins("H4")),  # net SPI_SCLK
        Subsignal("mosi", Pins("F4")),  # net SPI_MOSI
        Subsignal("miso", Pins("H3")),  # net SPI_MISO
        #Subsignal("wp",   Pins("")),
        #Subsignal("hold", Pins("")),
        IOStandard("3.3_V_LVTTL_/_LVCMOS")
     ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    # use "j3:1" reference for pin 1 of J3. This makes it a 1:1 translation with connector numbering
    ("j3", "ZERO #N/A #N/A G5 F1 G4 E1 J3 C2 G3 D2 J2 E3 H2 D3 F3 C3 G1 B3 #N/A #N/A A2 A2"),
    ("j4", "ZERO #N/A #N/A A5 B8 B5 C8 C5 D6 A6 B9 B6 C9 C6 D7 C7 D8 A8 D9 A9 E8 A2 A2"),
    ("j5", "ZERO #N/A #N/A F8 J9 E7 J8 F7 G8 E6 H8 F6 J7 F5 G6 G9 H6 H9 J6 #N/A #N/A A2 A2"),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(EfinixPlatform):
    default_clk_name = "clk33"
    default_clk_period = 1e9/33.333e6

    def __init__(self, toolchain="efinity"):
        EfinixPlatform.__init__(self, "T8F81C2", _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        return EfinixAtmelProgrammer()

    def do_finalize(self, fragment):
        EfinixPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk33", loose=True), 1e9/33.333e6)
