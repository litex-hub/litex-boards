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

    # Leds
    ("user_led", 0, Pins("A2"), IOStandard("LVCMOS33")),

    # SDRAM
    ("sdram_clock", 0, Pins("F16"), IOStandard("LVTTL33")),
    ("sdram", 0,
        Subsignal("a", Pins(
            "M13 M14 L14 L13 G12 G13 G14 G15",
            "F12 F13 T15 F14 E14")),
        Subsignal("ba",    Pins("P14 N13")),
        Subsignal("cs_n",  Pins("G16")),
        Subsignal("cke",   Pins("F15")),
        Subsignal("ras_n", Pins("J16")),
        Subsignal("cas_n", Pins("K16")),
        Subsignal("we_n",  Pins("L15")),
        Subsignal("dq", Pins(
            "R15 R16 P15 P16 N16 N14 M16 M15",
            "E16 D14 D16 C15 C16 C14 B16 B15")),
        Subsignal("dm", Pins("L16 E15")),
        IOStandard("LVTTL33")
    ),

    # VGA
    ("vga", 0,
        Subsignal("r",     Pins("T2")),
        Subsignal("g",     Pins("N1")),
        Subsignal("b",     Pins("R4")),
        #Subsignal("r",     Pins("T2 R1 R2")),
        #Subsignal("g",     Pins("N1 P2 P1")),
        #Subsignal("b",     Pins("R4 T3 T4")),
        Subsignal("hsync", Pins("P3")),
        Subsignal("vsync", Pins("R3")),
        IOStandard("LVCMOS33")
    ),

    # USB-C
    ("usb", 0,
        Subsignal("d_p", Pins("T6")),
        Subsignal("d_n", Pins("R6")),
        Subsignal("pullup", Pins("R7")),
        IOStandard("LVCMOS33")
    ),

    # USB HOST
    ("usb_host", 0,
        Subsignal("dp", Pins("B1")),
        Subsignal("dm", Pins("B2")),
        IOStandard("LVCMOS33")
    ),

    # DEBUG UART ON PMODA
    ("serial", 0,
        Subsignal("tx", Pins("PMODA:1")),
        Subsignal("rx", Pins("PMODA:2")),
        IOStandard("LVCMOS33")
    ),

]

_io_v0 = [

    # SD card w/ SPI interface
    ("spisdcard", 0,
        Subsignal("clk",  Pins("F2")),
        Subsignal("mosi", Pins("K1")),
        Subsignal("cs_n", Pins("K2")),
        Subsignal("miso", Pins("F3")),
        Misc("SLEWRATE=FAST"),
        IOStandard("LVCMOS33"),
    ),

    ("spiflash", 0,
        Subsignal("cs_n",   Pins("N8"), Misc("PULLMODE=UP")),
        #Subsignal("clk",    Pins("N9")),
        Subsignal("miso",   Pins("T7"), Misc("PULLMODE=UP")),
        Subsignal("mosi",   Pins("T8"), Misc("PULLMODE=UP")),
        Misc("SLEWRATE=SLOW"),
        IOStandard("LVCMOS33"),
    ),

]

# Connectors ---------------------------------------------------------------------------------------

_connectors_vx = [
    ("PMODA", "B11 B12 B13 B14 A11 A12 A13 A14"),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticeECP5Platform):
    default_clk_name   = "clk48"
    default_clk_period = 1e9/48e6

    def __init__(self, revision="v0", device="12F", toolchain="trellis", **kwargs):
        assert revision in ["v0", "v1"]
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
