#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Gwenhael Goavec-Merou <gwenhael.goavec-merou@trabucayre.com>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.build.generic_platform import *
from litex.build.gowin.platform import GowinPlatform
from litex.build.openfpgaloader import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk12",  0, Pins("4"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led", 0, Pins("23"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("24"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("25"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("26"), IOStandard("LVCMOS33")),
    ("user_led", 4, Pins("27"), IOStandard("LVCMOS33")),
    ("user_led", 5, Pins("28"), IOStandard("LVCMOS33")),
    ("user_led", 6, Pins("29"), IOStandard("LVCMOS33")),
    ("user_led", 7, Pins("30"), IOStandard("LVCMOS33")),

    # RGB led, active-low
    ("rgb_led", 0,
        Subsignal("r", Pins("112")),
        Subsignal("g", Pins("114")),
        Subsignal("b", Pins("113")),
        IOStandard("LVCMOS33"),
    ),
    ("rgb_led", 1,
        Subsignal("r", Pins("106")),
        Subsignal("g", Pins("111")),
        Subsignal("b", Pins("110")),
        IOStandard("LVCMOS33"),
    ),
    ("rgb_led", 2,
        Subsignal("r", Pins("101")),
        Subsignal("g", Pins("104")),
        Subsignal("b", Pins("102")),
        IOStandard("LVCMOS33"),
    ),
    ("rgb_led", 3,
        Subsignal("r", Pins("98")),
        Subsignal("g", Pins("100")),
        Subsignal("b", Pins("99")),
        IOStandard("LVCMOS33"),
    ),

    # Switches
    ("user_sw", 0, Pins("75"), IOStandard("LVCMOS33")),
    ("user_sw", 1, Pins("76"), IOStandard("LVCMOS33")),
    ("user_sw", 2, Pins("78"), IOStandard("LVCMOS33")),
    ("user_sw", 3, Pins("79"), IOStandard("LVCMOS33")),
    ("user_sw", 4, Pins("80"), IOStandard("LVCMOS33")),
    ("user_sw", 5, Pins("81"), IOStandard("LVCMOS33")),
    ("user_sw", 6, Pins("82"), IOStandard("LVCMOS33")),
    ("user_sw", 7, Pins("83"), IOStandard("LVCMOS33")),

    # Buttons.
    ("user_btn", 0, Pins("58"),  IOStandard("LVCMOS33")),
    ("user_btn", 1, Pins("59"),  IOStandard("LVCMOS33")),
    ("user_btn", 2, Pins("60"),  IOStandard("LVCMOS33")),
    ("user_btn", 3, Pins("61"),  IOStandard("LVCMOS33")),
    ("user_btn", 4, Pins("62"),  IOStandard("LVCMOS33")),
    ("user_btn", 5, Pins("63"),  IOStandard("LVCMOS33")),
    ("user_btn", 6, Pins("64"),  IOStandard("LVCMOS33")),
    ("user_btn", 7, Pins("65"),  IOStandard("LVCMOS33")),

    # Serial.
    # FT232H has only one interface -> use (arbitrary) two pins from J2 to
    # connect an external USB<->serial adapter
    ("serial", 0,
        Subsignal("tx", Pins("116")), # J2.17
        Subsignal("rx", Pins("115")), # J2.18
        IOStandard("LVCMOS33")
    ),

    # Seven Segment
    ("seven_seg_dig", 0, Pins("137"), IOStandard("LVCMOS33")),
    ("seven_seg_dig", 1, Pins("140"), IOStandard("LVCMOS33")),
    ("seven_seg_dig", 2, Pins("141"), IOStandard("LVCMOS33")),
    ("seven_seg_dig", 3, Pins("7"), IOStandard("LVCMOS33")),
    ("seven_seg", 0, Pins("138 142 9 11 12 139 8 10"), IOStandard("LVCMOS33")),

]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ["J1", "-  38  39  40  41  42  43  44  66  67  68  69  70  71  72  96  95  94  93 -"],
    ["J2", "- 136 135 134 133 132 131 130 129 128 123 122 121 120 119 118 117 116 115 -"],
]

# Platform -----------------------------------------------------------------------------------------

class Platform(GowinPlatform):
    default_clk_name   = "clk12"
    default_clk_period = 1e9/12e6

    def __init__(self, toolchain="gowin"):
        GowinPlatform.__init__(self, "GW1N-UV4LQ144C6/I5", _io, _connectors, toolchain=toolchain, devicename="GW1N-4")
        self.toolchain.options["use_mspi_as_gpio"] = 1

    def create_programmer(self):
        return OpenFPGALoader("runber")

    def do_finalize(self, fragment):
        GowinPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk12", loose=True), 1e9/12e6)
