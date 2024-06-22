#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2023 Lone Dynamics Corporation <info@lonedynamics.com>
#
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.lattice import LatticeECP5Platform
from litex.build.openfpgaloader import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io_vx = [

    # Clock
    ("clk48", 0,  Pins("C7"),  IOStandard("LVCMOS33")),

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

    # Differential Data Multiple Interface
    ("ddmi", 0,
        Subsignal("clk_p",    Pins("B10"),
            IOStandard("LVCMOS33D"), Misc("DRIVE=4")),
        Subsignal("data0_p",  Pins("A9"),
            IOStandard("LVCMOS33D"), Misc("DRIVE=4")),
        Subsignal("data1_p",  Pins("C8"),
            IOStandard("LVCMOS33D"), Misc("DRIVE=4")),
        Subsignal("data2_p",  Pins("A11"),
            IOStandard("LVCMOS33D"), Misc("DRIVE=4")),
    ),

    # USB-C
    ("usb", 0,
        Subsignal("d_p", Pins("A13")),
        Subsignal("d_n", Pins("A14")),
        Subsignal("pullup", Pins("B14")),
        IOStandard("LVCMOS33")
    ),

    # DUAL USB HOST
    ("usb_host", 0,
        Subsignal("dp", Pins("A5 A3")),
        Subsignal("dm", Pins("A6 A4")),
        IOStandard("LVCMOS33")
    ),

    # ETHERNET
    ("eth_clocks", 0,
        Subsignal("ref_clk", Pins("A7")),
        IOStandard("LVCMOS33")
    ),
    ("eth", 0,
        Subsignal("rx_data", Pins("B5 B4"), Misc("PULLMODE=UP")),
        Subsignal("tx_data", Pins("C6 B6")),
        Subsignal("tx_en", Pins("C5")),
        Subsignal("crs_dv", Pins("E7"), Misc("PULLMODE=UP")),
        Subsignal("rst_n", Pins("D7")),
        IOStandard("LVCMOS33")
    ),

    # DEBUG UART
    ("serial", 0,
        Subsignal("tx", Pins("B3")),
        Subsignal("rx", Pins("A2")),
        IOStandard("LVCMOS33")
    ),
]

_io_v0 = [

    # SD card w/ SPI interface
    ("spisdcard", 0,
        Subsignal("clk",  Pins("L1")),
        Subsignal("mosi", Pins("L4")),
        Subsignal("cs_n", Pins("L2")),
        Subsignal("miso", Pins("L3")),
        Misc("SLEWRATE=FAST"),
        IOStandard("LVCMOS33"),
    ),

]

# Connectors ---------------------------------------------------------------------------------------

_connectors_vx = [

]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticeECP5Platform):
    default_clk_name   = "clk48"
    default_clk_period = 1e9/48e6

    def __init__(self, revision="v0", device="45F", toolchain="trellis", **kwargs):
        assert revision in ["v0"]
        assert device in ["12F", "25F", "45F", "85F"]
        self.revision = revision

        io = _io_vx
        connectors = _connectors_vx

        if revision == "v0": io += _io_v0

        LatticeECP5Platform.__init__(self, f"LFE5U-{device}-6BG256", io, connectors, toolchain=toolchain, **kwargs)

    def create_programmer(self, cable):
        return OpenFPGALoader(cable=cable)

    def do_finalize(self, fragment):
        LatticeECP5Platform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk48", loose=True), 1e9/48e6)
