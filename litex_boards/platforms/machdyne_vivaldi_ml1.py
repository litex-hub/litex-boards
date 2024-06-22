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
    ("clk48", 0,  Pins("A7"),  IOStandard("LVCMOS33")),
    ("clk50", 0,  Pins("C7"),  IOStandard("LVCMOS33")),

    # SDRAM
    ("sdram_clock", 0, Pins("F16"), IOStandard("LVTTL33")),
    ("sdram", 0,
        Subsignal("a", Pins(
            "M13 M14 L14 L13 G12 G13 G14 G15",
            "F12 F13 T15 F14 E14")),
        Subsignal("ba",    Pins("P14 N13")),
        Subsignal("cs_n",  Pins("J16")),
        Subsignal("cke",   Pins("F15")),
        Subsignal("ras_n", Pins("K15")),
        Subsignal("cas_n", Pins("K16")),
        Subsignal("we_n",  Pins("L15")),
        Subsignal("dq", Pins(
            "R15 R16 P16 P15 N16 N14 M16 M15",
            "E15 D16 D14 C16 C15 C14 B15 B16")),
        Subsignal("dm", Pins("L16 E16")),
        IOStandard("LVTTL33")
    ),

    # I2C
    ("i2c", 0,
        Subsignal("sda", Pins("A13")),
        Subsignal("scl", Pins("A11")),
        IOStandard("LVCMOS33")
    ),

    # DUAL USB HOST
    ("usb_host", 0,
        Subsignal("dp", Pins("A9 C8")),
        Subsignal("dm", Pins("A10 B8")),
        IOStandard("LVCMOS33")
    ),

    # ETHERNET
    ("eth", 0,
        Subsignal("rx_data", Pins("E4 D4"), Misc("PULLMODE=UP")),
        Subsignal("tx_data", Pins("E6 D6")),
        Subsignal("tx_en", Pins("C5")),
        Subsignal("crs_dv", Pins("A5"), Misc("PULLMODE=UP")),
        Subsignal("rst_n", Pins("B5")),
        IOStandard("LVCMOS33")
    ),
    ("eth", 1,
        Subsignal("rx_data", Pins("B3 A2"), Misc("PULLMODE=UP")),
        Subsignal("tx_data", Pins("A4 A3")),
        Subsignal("tx_en", Pins("R12")),
        Subsignal("crs_dv", Pins("T13"), Misc("PULLMODE=UP")),
        Subsignal("rst_n", Pins("T14")),
        IOStandard("LVCMOS33")
    ),

    # SD card w/ SD-mode interface
    ("sdcard", 0,
        Subsignal("cd", Pins("A6")),
        Subsignal("clk", Pins("L3")),
        Subsignal("cmd", Pins("M1")),
        Subsignal("data", Pins("L1 M2 M3 L2")),
        Misc("SLEWRATE=FAST"),
        IOStandard("LVCMOS33")
    ),

    # SD card w/ SPI interface
    ("spisdcard", 0,
        Subsignal("clk",  Pins("L3")),
        Subsignal("mosi", Pins("M1")),
        Subsignal("cs_n", Pins("L2")),
        Subsignal("miso", Pins("L1")),
        Misc("SLEWRATE=FAST"),
        IOStandard("LVCMOS33"),
    ),
]

_io_v0 = [

    # DEBUG UART
    ("serial", 0,
        Subsignal("tx", Pins("B3")),
        Subsignal("rx", Pins("A2")),
        IOStandard("LVCMOS33")
    ),

]

_io_v2 = [

    # DEBUG UART
    ("serial", 0,
        Subsignal("tx", Pins("B4")),
        Subsignal("rx", Pins("C4")),
        IOStandard("LVCMOS33")
    ),

]

# Connectors ---------------------------------------------------------------------------------------

_connectors_vx = [
]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticeECP5Platform):
    default_clk_name   = "clk48"
    default_clk_period = 1e9/48e6

    def __init__(self, revision="v2", device="45F", toolchain="trellis", **kwargs):
        assert revision in ["v0", "v1", "v2"]
        assert device in ["12F", "25F", "45F", "85F"]
        self.revision = revision

        io = _io_vx
        connectors = _connectors_vx

        if revision == "v0": io += _io_v0
        if revision == "v1": io += _io_v0
        if revision == "v2": io += _io_v2

        LatticeECP5Platform.__init__(self, f"LFE5U-{device}-6BG256", io, connectors, toolchain=toolchain, **kwargs)

    def create_programmer(self, cable):
        return OpenFPGALoader(cable=cable)

    def do_finalize(self, fragment):
        LatticeECP5Platform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk48", loose=True), 1e9/48e6)
