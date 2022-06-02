#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Primesh Pinto <primeshp@gmailcom>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk100", 0, Pins("H4"),  IOStandard("LVCMOS33")),
    ("rst_n",  0, Pins("D14"), IOStandard("LVCMOS33")),


    # Leds
    ("user_led", 0, Pins("J1"),  IOStandard("LVCMOS33")), # Green.
    ("user_led", 1, Pins("A13"), IOStandard("LVCMOS33")), # Red.

    # RGB Leds (2 X SK6805 Leds)
    ("rgb", 0, Pins("N11"),IOStandard("LVCMOS33")),

    # Buttons
    ("user_btn", 0, Pins("C3"), IOStandard("LVCMOS33")),
    ("user_btn", 1, Pins("M4"), IOStandard("LVCMOS33")),

    # Mini HDMI
    ("hdmi", 0,
        Subsignal("clk_p",   Pins("G4"),IOStandard("LVCMOS33")),
        Subsignal("clk_n",   Pins("F4"),IOStandard("LVCMOS33")),
        Subsignal("data0_p", Pins("G1"),IOStandard("LVCMOS33")),
        Subsignal("data0_n", Pins("F1"),IOStandard("LVCMOS33")),
        Subsignal("data1_p", Pins("E2"),IOStandard("LVCMOS33")),
        Subsignal("data1_n", Pins("D2"),IOStandard("LVCMOS33")),
        Subsignal("data2_p", Pins("D1"),IOStandard("LVCMOS33")),
        Subsignal("data2_n", Pins("C1"),IOStandard("LVCMOS33")),
        Subsignal("scl",     Pins("F3"),IOStandard("LVCMOS33")),   
        Subsignal("sda",     Pins("F2"),IOStandard("LVCMOS33")),  
        Subsignal("hpd",     Pins("D4"),IOStandard("LVCMOS33")),
        Subsignal("cec",     Pins("E4"),IOStandard("LVCMOS33"))  
    ),

    # MIPI (Untested)
    ("mipi", 0,
        Subsignal("clkp", Pins("G11"),     IOStandard("MIPI_DPHY")),
        Subsignal("clkn", Pins("F11"),     IOStandard("LVCMOS12H")),
        Subsignal("dp",   Pins("J11 P10"), IOStandard("MIPI_DPHY")),
        Subsignal("dn",   Pins("J12 P11"), IOStandard("LVCMOS12H")),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("j10", {
        "j10_0"   : "N14",
        "j10_1"   : "M14",
        "j10_2"   : "C4",
        "j10_3"   : "B13",
        "j10_4"   : "N10",
        "j10_5"   : "M10",
        "j10_6"   : "B14",
        "j10_7"   : "D3",
        "j10_8"   : "P5",
        "j10_9"   : "E11",
        }
    ),
    
    ("digital_d2",{
        "d2_0"    : "A10",
        "d2_1"    : "B6",
    }),

    ("i2c", "P12 P13"), # SCL, SDA

    ("ar_io", {
        # Outer Digital Header
        "d0"  : "A12",
        "d1"  : "C12",
        "d2"  : "A10",
        "d3"  : "B6",
        "d4"  : "A5",
        "d5"  : "B5",
        "d6"  : "A4",
        "d7"  : "A3",
        "d8"  : "B3",
        "d9"  : "A2",
        "d10" : "B2",
        "d11" : "B1",
        "d12" : "H1",
        "d13" : "H2",


        # Outer Analog Header as Digital IO
        "a0" : "F5",
        "a1" : "D8",
        "a2" : "C7",
        "a3" : "E7",
        "a4" : "D7",
        "a5" : "D5",
        } )
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self, toolchain="vivado"):
        XilinxPlatform.__init__(self, "xc7s15-ftgb196", _io, _connectors, toolchain=toolchain)

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100", loose=True), 1e9/100e6)
