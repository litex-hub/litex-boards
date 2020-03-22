# This file is Copyright (c) Greg Davill <greg.davill@gmail.com>
# License: BSD

from litex.build.generic_platform import *
from litex.build.lattice import LatticePlatform

# IOs ----------------------------------------------------------------------------------------------

_io = [
    ("clk48", 0, Pins("A9"), IOStandard("LVCMOS33")),
    ("rst_n", 0, Pins("V17"), IOStandard("LVCMOS33")),

    ("usr_btn", 0, Pins("J17"),IOStandard("SSTL135_I")),

    ("rgb_led", 0,
        Subsignal("r", Pins("K4"), IOStandard("LVCMOS33")),
        Subsignal("g", Pins("M3"), IOStandard("LVCMOS33")),
        Subsignal("b", Pins("J3"), IOStandard("LVCMOS33")),    
    ),

    ("ddram", 0,
        Subsignal("a", Pins(
            "C4 D2 D3 A3 A4 D4 C3 B2",
            "B1 D1 A7 C2 B6 C1 A2 C7"),
            IOStandard("SSTL135_I"),Misc("SLEWRATE=FAST")),
        Subsignal("ba", Pins("D6 B7 A6"), IOStandard("SSTL135_I"),Misc("SLEWRATE=FAST")),
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
        Subsignal("cke", Pins("D18"), IOStandard("SSTL135_I"),Misc("SLEWRATE=FAST")),
        Subsignal("odt", Pins("C13"), IOStandard("SSTL135_I"),Misc("SLEWRATE=FAST")),
        Subsignal("reset_n", Pins("L18"), IOStandard("SSTL135_I"),Misc("SLEWRATE=FAST")),
        Subsignal("vccio", Pins("K16 D17 K15 K17 B18 C6"), IOStandard("SSTL135_II")),
        Subsignal("gnd", Pins("L15 L16"), IOStandard("SSTL135_II")),
    ),

    ("usb", 0,
        Subsignal("d_p", Pins("N1")),
        Subsignal("d_n", Pins("M2")),
        Subsignal("pullup", Pins("N2")),
        IOStandard("LVCMOS33")
    ),

    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("U17"), IOStandard("LVCMOS33")),
        #Subsignal("clk",  Pins("U16"), IOStandard("LVCMOS33")),
        Subsignal("dq",   Pins("U18 T18 R18 N18"), IOStandard("LVCMOS33")),
    ),
    ("spiflash", 0,
        Subsignal("cs_n", Pins("U17"), IOStandard("LVCMOS33")),
        #Subsignal("clk",  Pins("U16"), IOStandard("LVCMOS33")), # Note: CLK is bound using USRMCLK block
        Subsignal("miso", Pins("T18"), IOStandard("LVCMOS33")),
        Subsignal("mosi", Pins("U18"), IOStandard("LVCMOS33")),
        Subsignal("wp",   Pins("R18"), IOStandard("LVCMOS33")),
        Subsignal("hold", Pins("N18"), IOStandard("LVCMOS33")),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    # Feather 0.1" Header Pin Numbers, 
    # Note: Pin nubering is not continuous.
    ("GPIO", "N17 M18 C10 C9 - B10 B9 - - C8 B8 A8 H2 J2 N15 R17 N16 - L4 N3 N4 H4 G4 T17"),
]

# Standard Feather Pins
feather_serial = [
    ("serial", 0,
        Subsignal("tx", Pins("GPIO:1"), IOStandard("LVCMOS33")),
        Subsignal("rx", Pins("GPIO:0"), IOStandard("LVCMOS33"))
    )
]

feather_i2c = [
    ("i2c", 0,
        ("sda", Pins("GPIO:2"), IOStandard("LVCMOS33")),
        ("scl", Pins("GPIO:3"), IOStandard("LVCMOS33"))
    )
]

feather_spi = [
    ("spi",0,
        ("miso", Pins("GPIO:14"), IOStandard("LVCMOS33")),
        ("mosi", Pins("GPIO:16"), IOStandard("LVCMOS33")),
        ("sck", Pins("GPIO:15"), IOStandard("LVCMOS33"))
    )
]


# Platform -----------------------------------------------------------------------------------------

class Platform(LatticePlatform):
    default_clk_name = "clk48"
    default_clk_period = 1e9/48e6

    def __init__(self, device='25F', **kwargs):
        LatticePlatform.__init__(self, f"LFE5U-{device}-8MG285C", _io, _connectors, **kwargs)
