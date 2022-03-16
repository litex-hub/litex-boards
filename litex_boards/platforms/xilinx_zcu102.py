#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 FAYE Joseph <joseph-wagane.faye@insa-rennes.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform, VivadoProgrammer


# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk125", 0,
        Subsignal("p", Pins("G21"), IOStandard("LVDS")),
        Subsignal("n", Pins("F21"), IOStandard("LVDS")),
    ),
    ("clk300", 0,
        Subsignal("p", Pins("AL8"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("n", Pins("AL7"), IOStandard("DIFF_SSTL12_DCI")),
    ),
    ("cpu_reset", 0, Pins("AM13"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led", 0, Pins("AG14"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("AF13"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("AE13"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("AJ14"), IOStandard("LVCMOS33")),
    ("user_led", 4, Pins("AJ15"), IOStandard("LVCMOS33")),
    ("user_led", 5, Pins("AH13"), IOStandard("LVCMOS33")),
    ("user_led", 6, Pins("AH14"), IOStandard("LVCMOS33")),
    ("user_led", 7, Pins("AL12"), IOStandard("LVCMOS33")),

    # Buttons
    ("user_btn", 0, Pins("AG15"), IOStandard("LVCMOS33")),
    ("user_btn", 1, Pins("AE14"), IOStandard("LVCMOS33")),
    ("user_btn", 2, Pins("AF15"), IOStandard("LVCMOS33")),
    ("user_btn", 3, Pins("AE15"), IOStandard("LVCMOS33")),
    ("user_btn", 3, Pins("AG13"), IOStandard("LVCMOS33")),

    # Switches
    ("user_dip", 0, Pins("AN14"), IOStandard("LVCMOS33")),
    ("user_dip", 1, Pins("AP14"), IOStandard("LVCMOS33")),
    ("user_dip", 2, Pins("AM14"), IOStandard("LVCMOS33")),
    ("user_dip", 3, Pins("AN13"), IOStandard("LVCMOS33")),
    ("user_dip", 4, Pins("AN12"), IOStandard("LVCMOS33")),
    ("user_dip", 5, Pins("AP12"), IOStandard("LVCMOS33")),
    ("user_dip", 6, Pins("AL13"), IOStandard("LVCMOS33")),
    ("user_dip", 7, Pins("AK13"), IOStandard("LVCMOS33")),


    # Serial
    ("serial", 0,
        Subsignal("cts", Pins("E12")),
        Subsignal("rts", Pins("D12")),
        Subsignal("tx",  Pins("E13")),
        Subsignal("rx",  Pins("F13")),
        IOStandard("LVCMOS18")
    ),

    # I2C
    ("i2c", 0,
        Subsignal("sda", Pins("J11")),
        Subsignal("scl", Pins("J10")),
        IOStandard("LVCMOS33")
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "clk125"
    default_clk_period = 1e9/125e6

    def __init__(self, toolchain="vivado"):
        XilinxPlatform.__init__(self, "xczu9eg-ffvb1156-2-i", _io, toolchain=toolchain)

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk125", loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("clk300", loose=True), 1e9/300e6)
