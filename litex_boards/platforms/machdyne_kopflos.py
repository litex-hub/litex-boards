#
# This file is part of LiteX-Boards.
#
# Copright (c) 2023 Lone Dynamics Corporation <info@lonedynamics.com>
#
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.lattice import LatticePlatform
from litex.build.openfpgaloader import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io_vx = [

    # Clock
    ("clk48", 0,  Pins("A7"),  IOStandard("LVCMOS33")),

    # Leds
    ("user_led", 0, Pins("C1"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("E1"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("G1"),  IOStandard("LVCMOS33")),
    ("rgb_led", 0,
        Subsignal("r", Pins("C1"), IOStandard("LVCMOS33")),
        Subsignal("g", Pins("E1"), IOStandard("LVCMOS33")),
        Subsignal("b", Pins("G1"),  IOStandard("LVCMOS33")),
    ),

    # Buttons
    ("user_btn", 0, Pins("C2"), IOStandard("LVCMOS33")),

    # DDR3L
    ("ddram", 0,
        Subsignal("a", Pins(
            "R15 L13 P14 R14 L12 T14 N11 T13",
            "P12 T15 C14 M13 E14 R13 M14 D14"),
            IOStandard("SSTL135_I")),
        Subsignal("ba",    Pins("N16 K13 P16"), IOStandard("SSTL135_I")),
        Subsignal("ras_n", Pins("L16"),  IOStandard("SSTL135_I")),
        Subsignal("cas_n", Pins("M16"),  IOStandard("SSTL135_I")),
        Subsignal("we_n",  Pins("P15"),  IOStandard("SSTL135_I")),
        Subsignal("cs_n",  Pins("M15"),  IOStandard("SSTL135_I")),
        Subsignal("dm", Pins("F13 J13"), IOStandard("SSTL135_I")),
        Subsignal("dq", Pins(
            "F14 E16 F12 F15 G13 B16 G12 B15",
            "J14 J16 K15 K14 H14 K16 H13 J15"),
            IOStandard("SSTL135_I"),
            Misc("TERMINATION=75")),
        Subsignal("dqs_p", Pins("D16 G16"), IOStandard("SSTL135D_I"),
            Misc("TERMINATION=OFF DIFFRESISTOR=100")),
        Subsignal("clk_p", Pins("C16"), IOStandard("SSTL135D_I")),
        Subsignal("cke",   Pins("K12"),  IOStandard("SSTL135_I")),
        Subsignal("odt",   Pins("L15"), IOStandard("SSTL135_I")),
        Subsignal("reset_n", Pins("R12"), IOStandard("SSTL135_I")),
        Misc("SLEWRATE=FAST")
    ),

    # USB-C
    ("usb", 0,
        Subsignal("d_p", Pins("T6")),
        Subsignal("d_n", Pins("R6")),
        Subsignal("pullup", Pins("R7")),
        IOStandard("LVCMOS33")
    ),

    # DUAL USB HOST
    ("usb_host", 0,
        Subsignal("dp", Pins("R4 P1")),
        Subsignal("dm", Pins("T3 R1")),
        IOStandard("LVCMOS33")
    ),

    # ETHERNET
    ("eth_clocks", 0,
        Subsignal("ref_clk", Pins("M1")),
        IOStandard("LVCMOS33")
    ),
    ("eth", 0,
        Subsignal("rx_data", Pins("N1 P2"), Misc("PULLMODE=UP")),
        Subsignal("tx_data", Pins("T2 R2")),
        Subsignal("tx_en", Pins("P3")),
        Subsignal("crs_dv", Pins("M3"), Misc("PULLMODE=UP")),
        Subsignal("rst_n", Pins("N4")),
        IOStandard("LVCMOS33")
    ),

    # DEBUG UART
    ("serial", 0,
        Subsignal("tx", Pins("B1")),
        Subsignal("rx", Pins("B2")),
        IOStandard("LVCMOS33")
    ),

    # SPI
    ("spiflash", 0,
        Subsignal("cs_n",   Pins("N8")),
        Subsignal("miso",   Pins("T7")),
        Subsignal("mosi",   Pins("T8")),
        Misc("SLEWRATE=FAST"),
        IOStandard("LVCMOS33"),
    ),

]

_io_v0 = [

    # SD card w/ SD-mode interface
    ("sdcard", 0,
        Subsignal("cd", Pins("A5")),
        Subsignal("clk", Pins("B4")),
        Subsignal("cmd", Pins("A3"), Misc("PULLMODE=UP")),
        Subsignal("data", Pins("A4 B5 A2 B3"), Misc("PULLMODE=UP")),
        Misc("SLEWRATE=FAST"),
        IOStandard("LVCMOS33")
    ),

    # SD card w/ SPI interface
    ("spisdcard", 0,
        Subsignal("clk",  Pins("B4")),
        Subsignal("mosi", Pins("A3")),
        Subsignal("cs_n", Pins("B3")),
        Subsignal("miso", Pins("A4")),
        Misc("SLEWRATE=FAST"),
        IOStandard("LVCMOS33"),
    ),

]

# Connectors ---------------------------------------------------------------------------------------

_connectors_vx = [
    ("PMODA", "K3 J2 J3 F1 K2 K1 J1 G2"),
    ("PMODB", "N5 M5 T4 P4 N6 M6 R5 P5"),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticePlatform):
    default_clk_name   = "clk48"
    default_clk_period = 1e9/48e6

    def __init__(self, revision="v0", device="12F", toolchain="trellis", **kwargs):
        assert revision in ["v0"]
        assert device in ["12F", "25F", "45F", "85F"]
        self.revision = revision

        io = _io_vx
        connectors = _connectors_vx

        if revision == "v0": io += _io_v0

        LatticePlatform.__init__(self, f"LFE5U-{device}-6BG256", io, connectors, toolchain=toolchain, **kwargs)

    def create_programmer(self, cable):
        return OpenFPGALoader(cable=cable)

    def do_finalize(self, fragment):
        LatticePlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk48", loose=True), 1e9/48e6)
