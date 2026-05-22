# This file is Copyright (c) 2019 Antti Lukats <antti.lukats@gmail.com>
# This file is Copyright (c) 2018-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# License: BSD

from litex.build.generic_platform import *
from litex.build.microsemi import MicrosemiPlatform

# IOs ----------------------------------------------------------------------------------------------

_io = [
    ("clk12", 0, Pins("N16"), IOStandard("LVCMOS33")),

#    ("rst_n", 0, Pins("F5"), IOStandard("LVCMOS33")),

    ("user_led", 0, Pins("G17"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("E18"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("R17"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("R18"), IOStandard("LVCMOS33")),
    ("user_led", 4, Pins("T18"), IOStandard("LVCMOS33")),
    ("user_led", 5, Pins("U18"), IOStandard("LVCMOS33")),
    ("user_led", 6, Pins("R16"), IOStandard("LVCMOS33")),
    ("user_led", 7, Pins("E1"),  IOStandard("LVCMOS33")),
    ("user_led", 8, Pins("D2"),  IOStandard("LVCMOS33")),

    ("user_btn", 0, Pins("B19"), IOStandard("LVCMOS33")),

    ("serial", 0,
        Subsignal("tx", Pins("D18")),
        Subsignal("rx", Pins("C19")),
        IOStandard("LVCMOS33")
    ),

    ("spiflash", 0,
        Subsignal("cs_n", Pins("K15")),
        Subsignal("clk",  Pins("P18")),
        Subsignal("mosi", Pins("P19")),
        Subsignal("miso", Pins("K16")),
        Subsignal("wp",   Pins("J18")),
        Subsignal("hold", Pins("N19")),
        IOStandard("LVCMOS33"),
    ),
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("K15")),
        Subsignal("clk",  Pins("P18")),
        Subsignal("dq",   Pins("P19 K16 J18 N19")),
        IOStandard("LVCMOS33")
    ),

    ("sdram_clock", 0, Pins("T14"), IOStandard("LVCMOS33")),
    ("sdram", 0,
        Subsignal("a",     Pins("U11 U12 V11 Y10 W15 U14 Y15 W14 T15 W13 T13 V14 V15 Y16")),
        Subsignal("ba",    Pins("W10 V12")),
        Subsignal("cs_n",  Pins("R13")),
        Subsignal("cke",   Pins("Y13")),
        Subsignal("ras_n", Pins("U13")),
        Subsignal("cas_n", Pins("Y12")),
        Subsignal("we_n",  Pins("R12")),
        Subsignal("dq",    Pins("F1 G1 E2 G2 E3 G3 F3 F4 J7 G6 F6 H5 H6 H4 F5 G4")),
        Subsignal("dm",    Pins("E5 F7")),
        IOStandard("LVCMOS33"),
    ),

]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("pmod", "J20 K20 L16 L15 - - J17 F20 G19 H16"),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(MicrosemiPlatform):
    default_clk_name = "clk12"
    default_clk_period = 83.0

    def __init__(self, toolchain="libero_soc"):
        # LiteX's Microsemi backend models the SmartFusion2 fabric through the IGLOO2 family.
        MicrosemiPlatform.__init__(self, "M2GL010-1VF400", _io, _connectors, toolchain=toolchain)
