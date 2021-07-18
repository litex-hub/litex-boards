#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2018 William D. Jones <thor0505@comcast.net>
# Copyright (c) 2020 Staf Verhaegen <staf@fibraservi.eu>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import Pins, Subsignal, IOStandard, Misc
from litex.build.xilinx import XilinxPlatform
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk50", 0, Pins("N14"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led", 0, Pins("M1"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("A14"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("A13"), IOStandard("LVCMOS33")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("N11")), # BDBUS1
        Subsignal("rx", Pins("E11")), # BDBUS0
        IOStandard("LVCMOS33")
    ),

    ("issiram", 0,
        Subsignal("addr", Pins("M4 N3 N4 P3 M5 E5 D5 D3  B7 B4 J4 H4 H3 G4 E6 A7  A5 A4 C4"), IOStandard("LVCMOS33")),
        Subsignal("data", Pins("L5 L3 L4 R2 F3 F4 E3 D6"), IOStandard("LVCMOS33")),
        Subsignal("wen", Pins("R1"), IOStandard("LVCMOS33")),
        Subsignal("cen", Pins("M6"), IOStandard("LVCMOS33")),
        Misc("SLEW=FAST"),
    ),
]

# Connectors ---------------------------------------------------------------------------------------
_connectors = [
]

# Platform -----------------------------------------------------------------------------------------

class Xc7A35t_Platform(XilinxPlatform):
    def __init__(self, io, conns ):
        XilinxPlatform.__init__(self, "xc7a35tftg256-1", io, conns, toolchain="vivado")
    def do_finalize(self,fragment):
        self.add_period_constraint(self.lookup_request("clk50", loose=True), self.default_clk_period)

def get_platform(base_platform):
  class the_platform(base_platform):

    def __init__(self):
        self.default_clk_name   = "clk50"
        self.default_clk_period = 1e9/50e6
        base_platform.__init__(self,_io, _connectors)

    def do_finalize(self, fragment):
        base_platform.do_finalize(self, fragment)

  return the_platform()