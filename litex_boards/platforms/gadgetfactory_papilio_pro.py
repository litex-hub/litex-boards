#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2023 Fabien Caura <fabien@acathla.tk>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxSpartan6Platform
from litex.build.xilinx.programmer import XC3SProg

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst.
    ("clk32", 0, Pins("P94"), IOStandard("LVCMOS33")),

    # Leds.
    ("user_led", 0, Pins("P112"), IOStandard("LVCMOS33"), Drive(24), Misc("SLEW=QUIETIO")),

    # Serial.
    ("serial", 1,
        Subsignal("tx", Pins("P105"), IOStandard("LVCMOS33"), Misc("SLEW=SLOW")),
        Subsignal("rx", Pins("P101"), IOStandard("LVCMOS33"), Misc("PULLUP"))
    ),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("P38")),
        Subsignal("clk",  Pins("P70")),
        Subsignal("mosi", Pins("P64")),
        Subsignal("miso", Pins("P65"), Misc("PULLUP")),
        IOStandard("LVCMOS33"), Misc("SLEW=FAST")
    ),
    ("spiflash2x", 0,
        Subsignal("cs_n", Pins("P38")),
        Subsignal("clk",  Pins("P70")),
        Subsignal("dq",   Pins("P64", "P65")),
        IOStandard("LVCMOS33"), Misc("SLEW=FAST")
    ),

    # SDR SDRAM.
    ("sdram_clock", 0, Pins("P32"), IOStandard("LVCMOS33"), Misc("SLEW=FAST")),
    ("sdram", 0,
        Subsignal("a", Pins(
            "P140 P139 P138 P137 P46 P45 P44",
            "P43 P41 P40 P141 P35 P34"
        )),
        Subsignal("ba",    Pins("P143 P142")),
        Subsignal("cs_n",  Pins("P1")),
        Subsignal("cke",   Pins("P33")),
        Subsignal("ras_n", Pins("P2")),
        Subsignal("cas_n", Pins("P5")),
        Subsignal("we_n",  Pins("P6")),
        Subsignal("dq",    Pins(
            "P9 P10 P11 P12 P14 P15 P16 P8",
            "P21 P22 P23 P24 P26 P27 P29 P30"
        )),
        Subsignal("dm",    Pins("P7 P17")),
        IOStandard("LVCMOS33"), Misc("SLEW=FAST")
    )
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
        #   0   1   2   3   4   5   6   7   8   9  10  11  12  13  14  15
    ("A", "P48 P51 P56 P58 P61 P66 P67 P75 P79 P81 P83 P85 P88 P93 P98 P100"),
    ("B", "P99 P97 P92 P87 P84 P82 P80 P78 P74 P95 P62 P59 P57 P55 P50 P47"),
    ("C", "P114 P115 P116 P117 P118 P119 P120 P121 P123 P124 P126 P127 P131 P132 P133 P134")
        #   0    1    2    3    4    5    6    7    8    9   10   11   12   13   14   15
]

# Extensions --------------------------------------------------------------------------------------

# Arcade MegaWing V1.3 pinout
_arcade_megawing = [
    # VGA.
    ("vga", 0,
        Subsignal("r", Pins("C:4 C:5 C:6 C:7")),
        Subsignal("g", Pins("B:4 B:5 B:6 B:7")),
        Subsignal("b", Pins("B:0 B:1 B:2 B:3")),
        Subsignal("vsync_n", Pins("C:2")),
        Subsignal("hsync_n", Pins("C:3")),
        IOStandard("LVCMOS33")
    ),

    # Buttons.
    ("buttons", 0,
        Subsignal("up",    Pins("C:8")),
        Subsignal("down",  Pins("C:10")),
        Subsignal("left",  Pins("C:11")),
        Subsignal("right", Pins("C:13")),
        IOStandard("LVCMOS33")
    ),

    # Joysticks ports.
    ("joy", 0,
        Subsignal("up",    Pins("C:8")),
        Subsignal("down",  Pins("C:10")),
        Subsignal("left",  Pins("C:11")),
        Subsignal("right", Pins("C:13")),
        Subsignal("fire1", Pins("C:9")),
        Subsignal("fire2", Pins("C:15")),
        IOStandard("LVCMOS33")
    ),
    ("joy", 1,
        Subsignal("up", Pins("B:12")),
        Subsignal("down", Pins("B:14")),
        Subsignal("left", Pins("B:15")),
        Subsignal("right", Pins("A:1")),
        Subsignal("fire1", Pins("B:13")),
        Subsignal("fire2", Pins("A:3")),
        IOStandard("LVCMOS33")
    ),

    # PS2 ports.
    ("ps2", 0,
        Subsignal("clk", Pins("C:1")),
        Subsignal("data", Pins("C:0")),
        IOStandard("LVCMOS33")
    ),
    ("ps2", 1,
        Subsignal("clk", Pins("A:13")),
        Subsignal("data", Pins("A:12")),
        IOStandard("LVCMOS33")
    ),

    # Leds.
    ("amw_user_led", 0, Pins("A:7"), IOStandard("LVCMOS33")),
    ("amw_user_led", 1, Pins("A:6"), IOStandard("LVCMOS33")),
    ("amw_user_led", 2, Pins("A:5"), IOStandard("LVCMOS33")),
    ("amw_user_led", 3, Pins("A:4"), IOStandard("LVCMOS33")),

    # Reset button.
    ("reset_button", 0, Pins("P85"), IOStandard("LVCMOS33") )
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxSpartan6Platform):
    default_clk_name = "clk32"
    default_clk_period = 1e9/32e6

    def __init__(self, toolchain="ise"):
        XilinxSpartan6Platform.__init__(self, "xc6slx9-tqg144-2", _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        return XC3SProg("papilio", "bscan_spi_lx9_papilio.bit")

    def do_finalize(self, fragment):
        XilinxSpartan6Platform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk32", loose=True), 1e9/32e6)
