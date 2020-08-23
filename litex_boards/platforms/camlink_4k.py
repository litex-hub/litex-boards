#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# The Cam Link 4K PCB and IOs have been documented by @GregDavill and @ApertusOSCinema:
# https://wiki.apertus.org/index.php/Elgato_CAM_LINK_4K

# The FX3 exploration tool (and FPGA loader) has been developed by @ktemkin:
# https://github.com/ktemkin/camlink-re

from litex.build.generic_platform import *
from litex.build.lattice import LatticePlatform

# IOs ----------------------------------------------------------------------------------------------

_io = [
    ("clk27", 0, Pins("B11"), IOStandard("LVCMOS25")),

    ("user_led", 0, Pins("A6"), IOStandard("LVCMOS25")),
    ("user_led", 1, Pins("A9"), IOStandard("LVCMOS25")),

    ("serial", 0,
        Subsignal("tx", Pins("A6")), # led0
        Subsignal("rx", Pins("A9")), # led1
        IOStandard("LVCMOS25")
    ),

    ("ddram", 0,
        Subsignal("a", Pins(
            "P2 L2 N1 P1 N5 M1 M3 N4",
            "L3 L1 P5 N2 N3"),
            IOStandard("SSTL135_I")),
        Subsignal("ba",    Pins("C4 A3 B4"), IOStandard("SSTL135_I")),
        Subsignal("ras_n", Pins("D3"), IOStandard("SSTL135_I")),
        Subsignal("cas_n", Pins("C3"), IOStandard("SSTL135_I")),
        Subsignal("we_n",  Pins("D5"), IOStandard("SSTL135_I")),
        Subsignal("cs_n",  Pins("B5"), IOStandard("SSTL135_I")),
        Subsignal("dm", Pins("J4 H5"), IOStandard("SSTL135_I")),
        Subsignal("dq", Pins(
            "L5 F1 K4 G1 L4 H1 G2 J3",
            "D1 C1 E2 C2 F3 A2 E1 B1"),
            IOStandard("SSTL135_I"),
            Misc("TERMINATION=75")),
        Subsignal("dqs_p", Pins("K2 H4"),
            Misc("TERMINATION=OFF"),
            Misc("DIFFRESISTOR=100"),
            IOStandard("SSTL135D_I")),
        Subsignal("clk_p",  Pins("A4"), IOStandard("SSTL135D_I")),
        Subsignal("cke",    Pins("E4"), IOStandard("SSTL135_I")),
        Subsignal("odt",    Pins("B3"), IOStandard("SSTL135_I")),
        Subsignal("reset_n", Pins("C5"), IOStandard("SSTL135_I")),
        Misc("SLEWRATE=FAST"),
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticePlatform):
    default_clk_name   = "clk27"
    default_clk_period = 1e9/27e6

    def __init__(self, **kwargs):
        LatticePlatform.__init__(self, "LFE5U-25F-8BG381C", _io, **kwargs)

    def do_finalize(self, fragment):
        LatticePlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk27", loose=True), 1e9/27e6)
