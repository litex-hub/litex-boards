# This file is Copyright (c) 2019 Greg Davill <greg.davill@gmail.com>
# License: BSD

from litex.build.generic_platform import *
from litex.build.lattice import LatticePlatform

# IOs ----------------------------------------------------------------------------------------------

_io = [
    ("clk100", 0, Pins("A9"), IOStandard("LVCMOS33")),
    ("rst_n", 0, Pins("R16"), IOStandard("LVCMOS25")),

    ("rgb_led", 0,
        Subsignal("r", Pins("V17"), IOStandard("LVCMOS25")),
        Subsignal("g", Pins("T17"), IOStandard("LVCMOS25")),
        Subsignal("b", Pins("J3"),  IOStandard("LVCMOS33")),
    )

    ("serial", 0,
        Subsignal("tx", Pins("N17"), IOStandard("LVCMOS25")),
        Subsignal("rx", Pins("M18"), IOStandard("LVCMOS25")),
    ),

    ("ddram", 0,
        Subsignal("a", Pins(
            "A4 D2 C3 C7 D3 D4 D1 B2",
            "C1 A2 A7 C2 C4"),
            IOStandard("SSTL135_I"),Misc("SLEWRATE=FAST")),
        Subsignal("ba", Pins("B6 B7 A6"), IOStandard("SSTL135_I"),Misc("SLEWRATE=FAST")),
        Subsignal("ras_n", Pins("C12"), IOStandard("SSTL135_I"),Misc("SLEWRATE=FAST")),
        Subsignal("cas_n", Pins("D13"), IOStandard("SSTL135_I"),Misc("SLEWRATE=FAST")),
        Subsignal("we_n", Pins("B12"), IOStandard("SSTL135_I"),Misc("SLEWRATE=FAST")),
        Subsignal("cs_n", Pins("A12"), IOStandard("SSTL135_I"),Misc("SLEWRATE=FAST")),
        Subsignal("dm", Pins("D16 G16"), IOStandard("SSTL135_I"),Misc("SLEWRATE=FAST")),
        Subsignal("dq", Pins(
            "C17 D15 B17 C16 A15 B13 A17 A13",
            "F17 F16 G15 F15 J16 C18 H16 F18"),
            IOStandard("SSTL135_I"),
            Misc("TERMINATION=75 SLEWRATE=FAST")),
        Subsignal("dqs_p", Pins("B15 G18"), IOStandard("SSTL135D_I"), Misc("TERMINATION=OFF DIFFRESISTOR=100 SLEWRATE=FAST")),
        Subsignal("clk_p", Pins("J18"), IOStandard("SSTL135D_I"),Misc("SLEWRATE=FAST")),
        Subsignal("cke", Pins("D6"), IOStandard("SSTL135_I"),Misc("SLEWRATE=FAST")),
        Subsignal("odt", Pins("C13"), IOStandard("SSTL135_I"),Misc("SLEWRATE=FAST")),
        Subsignal("reset_n", Pins("B1"), IOStandard("SSTL135_I"),Misc("SLEWRATE=FAST")),
        Subsignal("vccio", Pins("D18 K16 B18 D17 K15 K17 C6 A3"), IOStandard("SSTL135_II"), Misc("DRIVE=10")),
        Subsignal("gnd", Pins("L18 L15 L16"), IOStandard("SSTL135_II"), Misc("DRIVE=10")),
        Misc("SLEWRATE=FAST")
    ),


    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("U17")),
        Subsignal("clk", Pins("U16")),
        Subsignal("dq", Pins("U18", "T18", "R18", "N18")),
        IOStandard("LVCMOS25")
    ),
    #("spiflash", 0,
    #    Subsignal("cs_n", Pins("U17")),
    #    Subsignal("clk", Pins("U16")),
    #    Subsignal("mosi", Pins("U18")),
    #    Subsignal("miso", Pins("T18")),
    #    Subsignal("wp", Pins("R18")),
    #    Subsignal("hold", Pins("N18")),
    #    IOStandard("LVCMOS25"),
    #),

]



# Connectors ---------------------------------------------------------------------------------------

_connectors = [
]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticePlatform):
    default_clk_name = "clk48"
    default_clk_period = int(1e9/48e6)

    def __init__(self, **kwargs):
        LatticePlatform.__init__(self, "LFE5U-25F-8MG285C", _io, _connectors, **kwargs)

