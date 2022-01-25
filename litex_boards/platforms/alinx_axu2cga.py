#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Gwenhael Goavec-Merou <gwenhael.goavec-merou@trabucayre.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform
from litex.build.openfpgaloader import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk25", 0, Pins("AB11"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led", 0, Pins("W13"),  IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("Y12"),  IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("AA12"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("AB13"), IOStandard("LVCMOS33")),

    # Buttons
    ("user_btn", 0, Pins("AA13"), IOStandard("LVCMOS33")),
    ("user_btn", 1, Pins("AE14"), IOStandard("LVCMOS33")),
    ("user_btn", 2, Pins("AE15"), IOStandard("LVCMOS33")),
    ("user_btn", 3, Pins("AG14"), IOStandard("LVCMOS33")),

    # Serial (no UART by default -> use J15 3 & 5)
    ("serial", 0,
        Subsignal("tx", Pins("A11")),
        Subsignal("rx", Pins("A13")),
        IOStandard("LVCMOS33")
    ),

    # MIPI 0
    ("camera", 0,
        Subsignal("mclk",    Pins("AG13"),IOStandard("LVCMOS33")),
        Subsignal("clkp",    Pins("AC9")),
        Subsignal("clkn",    Pins("AD9")),
        Subsignal("dp",      Pins("AE9 AB8")),
        Subsignal("dn",      Pins("AE8 AC8")),
        IOStandard("MIPI_DPHY")
    ),
    ("mipi_gpio", 0,
        Subsignal("gpio",    Pins("AH14")),
        IOStandard("LVCMOS33")
    ),
    ("mipi_i2c", 0,
        Subsignal("scl",     Pins("AH13")),
        Subsignal("sda",     Pins("AE13")),
        IOStandard("LVCMOS33")
    ),
 
    # MIPI 1
    ("camera", 1,
        Subsignal("mclk",    Pins("AC14"), IOStandard("LVCMOS33")),
        Subsignal("clkp",    Pins("U9")),
        Subsignal("clkn",    Pins("V9")),
        Subsignal("dp",      Pins("U8 W8")),
        Subsignal("dn",      Pins("V8 Y8")),
        IOStandard("MIPI_DPHY")
    ),
    ("mipi_gpio", 1,
        Subsignal("gpio",    Pins("AD15")),
        IOStandard("LVCMOS33")
    ),
    ("mipi_i2c", 1,
        Subsignal("scl",     Pins("AD14")),
        Subsignal("sda",     Pins("AC13")),
        IOStandard("LVCMOS33")
    )

]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("J12", {
         3: "F7",  4: "G8",
         5: "F6",  6: "G6",
         7: "D9",  8: "E9",
         9: "F5", 10: "G5",
        11: "E8", 12: "F8",
        13: "D5", 14: "E5",
        15: "C4", 16: "D4",
        17: "E3", 18: "E4",
        19: "F1", 20: "G1",
        21: "E2", 22: "F2",
        23: "D6", 24: "D7",
        25: "B9", 26: "C9",
        27: "A4", 28: "B4",
        29: "B6", 30: "C6",
        31: "A6", 32: "A7",
        33: "B8", 34: "C8",
        35: "A8", 36: "A9",
    }),
    ("j15", {
         3: "A11",  4: "A12",
         5: "A13",  6: "B13",
         7: "A14",  8: "B14",
         9: "E13", 10: "E14",
        11: "A15", 12: "B15",
        13: "C13", 14: "C14",
        15: "B10", 16: "C11",
        17: "D14", 18: "D15",
        19: "F11", 20: "F12",
        21: "H13", 22: "H14",
        23: "G14", 24: "G15",
        25: "F10", 26: "G11",
        27: "H12", 28: "J12",
        29: "J14", 30: "K14",
        31: "K12", 32: "K13",
        33: "L13", 34: "L14",
        35: "G10", 36: "H11",
    })
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "clk25"
    default_clk_period = 1e9/25e6

    def __init__(self):
        XilinxPlatform.__init__(self, "xczu2cg-sfvc784-1-e", _io, _connectors, toolchain="vivado")

    def create_programmer(self, cable):
        return OpenFPGALoader("axu2cga", cable)

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk25", loose=True), 1e9/25e6)
