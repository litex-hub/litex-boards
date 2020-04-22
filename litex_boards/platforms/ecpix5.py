# This file is Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# License: BSD

from litex.build.generic_platform import *
from litex.build.lattice import LatticePlatform

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # clock / reset
    ("clk100", 0, Pins("K23"), IOStandard("LVCMOS33")),
    ("rst_n",  0, Pins("N5"),  IOStandard("LVCMOS33")),

    # led
    ("rgb_led", 0,
        Subsignal("r", Pins("U21")),
        Subsignal("g", Pins("W21")),
        Subsignal("b", Pins("T24")),
        IOStandard("LVCMOS33"),
    ),
    ("rgb_led", 1,
        Subsignal("r", Pins("T23")),
        Subsignal("g", Pins("R21")),
        Subsignal("b", Pins("T22")),
        IOStandard("LVCMOS33"),
    ),
    ("rgb_led", 2,
        Subsignal("r", Pins("P21")),
        Subsignal("g", Pins("R23")),
        Subsignal("b", Pins("P22")),
        IOStandard("LVCMOS33"),
    ),
    ("rgb_led", 3,
        Subsignal("r", Pins("K21")),
        Subsignal("g", Pins("K24")),
        Subsignal("b", Pins("M21")),
        IOStandard("LVCMOS33"),
    ),

    # serial
    ("serial", 0,
        Subsignal("rx", Pins("R26"), IOStandard("LVCMOS33")),
        Subsignal("tx", Pins("R24"), IOStandard("LVCMOS33")),
    ),
]

_connectors = []

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticePlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self, **kwargs):
        LatticePlatform.__init__(self, "LFE5UM5G-85F-8BG554I", _io, _connectors, **kwargs)
