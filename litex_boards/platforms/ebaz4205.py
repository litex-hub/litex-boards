#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019-2020 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2021 Dhiru Kholia <dhiru.kholia@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform, VivadoProgrammer
from litex.build.xilinx.programmer import XC3SProg

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk33_333", 0, Pins("N18"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led", 0, Pins("W14"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("W13"), IOStandard("LVCMOS33")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("B20")),
        Subsignal("rx", Pins("B19")),
        IOStandard("LVCMOS33")
    ),
]

# This is currently untested on this EBAZ4205 board
_ps7_io = [
    # PS7
    ("ps7_clk",   0, Pins(1)),
    ("ps7_porb",  0, Pins(1)),
    ("ps7_srstb", 0, Pins(1)),
    ("ps7_mio",   0, Pins(54)),
    ("ps7_ddram", 0,
        Subsignal("addr",    Pins(15)),
        Subsignal("ba",      Pins(3)),
        Subsignal("cas_n",   Pins(1)),
        Subsignal("ck_n",    Pins(1)),
        Subsignal("ck_p",    Pins(1)),
        Subsignal("cke",     Pins(1)),
        Subsignal("cs_n",    Pins(1)),
        Subsignal("dm",      Pins(4)),
        Subsignal("dq",      Pins(32)),
        Subsignal("dqs_n",   Pins(4)),
        Subsignal("dqs_p",   Pins(4)),
        Subsignal("odt",     Pins(1)),
        Subsignal("ras_n",   Pins(1)),
        Subsignal("reset_n", Pins(1)),
        Subsignal("we_n",    Pins(1)),
        Subsignal("vrn",     Pins(1)),
        Subsignal("vrp",     Pins(1)),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
]

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk33_333"
    default_clk_period = 1e9/33.333e6

    def __init__(self, toolchain="vivado"):
        Xilinx7SeriesPlatform.__init__(self, "xc7z010-clg400-1", _io,  _connectors, toolchain=toolchain)
        self.add_extension(_ps7_io)

    def create_programmer(self):
        return VivadoProgrammer()

    """
    # We will like to use this later - Vivado is slow!
    def create_programmer(self):
        return XC3SProg(cable="ftdi")
    """

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk33_333", loose=True), 1e9/33.333e6)
