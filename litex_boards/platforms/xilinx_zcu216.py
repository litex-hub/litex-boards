#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Ilia Sergachev <ilia@sergachev.ch>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxUSPPlatform, VivadoProgrammer


# IOs ----------------------------------------------------------------------------------------------

_io = [
    ("clk100", 0,
        Subsignal("p", Pins("G12"), IOStandard("LVDS_25")),
        Subsignal("n", Pins("G11"), IOStandard("LVDS_25"))
    ),

    ("user_led", 0, Pins("C13"), IOStandard("LVCMOS18")),
    ("user_led", 1, Pins("D14"), IOStandard("LVCMOS18")),
    ("user_led", 2, Pins("D12"), IOStandard("LVCMOS18")),
    ("user_led", 3, Pins("D13"), IOStandard("LVCMOS18")),
    ("user_led", 4, Pins("AW18"), IOStandard("LVCMOS12")),
    ("user_led", 5, Pins("AV18"), IOStandard("LVCMOS12")),
    ("user_led", 6, Pins("BA19"), IOStandard("LVCMOS12")),
    ("user_led", 7, Pins("AP21"), IOStandard("LVCMOS12")),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxUSPPlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9 / 100e6

    def __init__(self, toolchain="vivado"):
        XilinxUSPPlatform.__init__(self, "xczu49dr-ffvf1760-2-e", _io, toolchain=toolchain)
        self.toolchain.bitstream_commands = \
            ["set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]", ]
        self.default_clk_freq = 1e9 / self.default_clk_period

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment, *args, **kwargs):
        XilinxUSPPlatform.do_finalize(self, fragment, *args, **kwargs)
        self.add_period_constraint(self.lookup_request(self.default_clk_name, loose=True), self.default_clk_period)
