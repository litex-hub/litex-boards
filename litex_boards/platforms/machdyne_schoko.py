#
# This file is part of LiteX-Boards.
#
# Copright (c) 2022 Lone Dynamics Corporation <info@lonedynamics.com>
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
    ("user_led", 0, Pins("B1"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("C1"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("D1"),  IOStandard("LVCMOS33")),
    ("rgb_led", 0,
        Subsignal("r", Pins("B1"), IOStandard("LVCMOS33")),
        Subsignal("g", Pins("C1"), IOStandard("LVCMOS33")),
        Subsignal("b", Pins("D1"),  IOStandard("LVCMOS33")),
    ),

    # SDRAM
    ("sdram_clock", 0, Pins("F16"), IOStandard("LVTTL33")),
    ("sdram", 0,
        Subsignal("a", Pins(
            "R14 M14 L14 L13 G12 G13 G14 G15",
            "F12 F13 T15 F14 E14")),
        Subsignal("ba",    Pins("T14 T13")),
        Subsignal("cs_n",  Pins("G16")),
        Subsignal("cke",   Pins("F15")),
        Subsignal("ras_n", Pins("J16")),
        Subsignal("cas_n", Pins("K16")),
        Subsignal("we_n",  Pins("L15")),
        Subsignal("dq", Pins(
            "R15 R16 P16 P15 N16 N14 M16 M15",
            "E15 D16 D14 C16 B16 C14 C15 B15")),
        Subsignal("dm", Pins("L16 E16")),
        IOStandard("LVTTL33")
    ),

    # VGA
    ("vga", 0,
        Subsignal("r",     Pins("J3")),
        Subsignal("g",     Pins("K3")),
        Subsignal("b",     Pins("H2")),
        Subsignal("hsync", Pins("J1")),
        Subsignal("vsync", Pins("J2")),
        IOStandard("LVCMOS33")
    ),

    # Differential Data Multiple Interface
    ("ddmi", 0,
        Subsignal("clk_p",    Pins("R5"),
            IOStandard("LVCMOS33D"), Misc("DRIVE=4")),
        Subsignal("data0_p",  Pins("P4"),
            IOStandard("LVCMOS33D"), Misc("DRIVE=4")),
        Subsignal("data1_p",  Pins("P1"),
            IOStandard("LVCMOS33D"), Misc("DRIVE=4")),
        Subsignal("data2_p",  Pins("N1"),
            IOStandard("LVCMOS33D"), Misc("DRIVE=4")),
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
        Subsignal("dp", Pins("F2")),
        Subsignal("dm", Pins("E1")),
        IOStandard("LVCMOS33")
    ),

    # UART PMOD
    ("serial", 0,
        Subsignal("tx", Pins("PMODA:1")),
        Subsignal("rx", Pins("PMODA:2")),
        IOStandard("LVCMOS33")
    ),

    # SPI
    ("spiflash", 0,
        Subsignal("cs_n",   Pins("N8"), Misc("PULLMODE=UP")),
        Subsignal("clk",    Pins("N9")),
        Subsignal("miso",   Pins("T7"), Misc("PULLMODE=UP")),
        Subsignal("mosi",   Pins("T8"), Misc("PULLMODE=UP")),
        Misc("SLEWRATE=SLOW"),
        IOStandard("LVCMOS33"),
    ),

]

_io_v1 = [

    # SD card w/ SPI interface
    ("spisdcard", 0,
        Subsignal("clk",  Pins("D6")),
        Subsignal("mosi", Pins("C6")),
        Subsignal("cs_n", Pins("B6")),
        Subsignal("miso", Pins("E6")),
        Misc("SLEWRATE=FAST"),
        IOStandard("LVCMOS33"),
    ),

]

_io_v2 = [

    # SD card w/ SD-mode interface
    ("sdcard", 0,
        Subsignal("cd", Pins("A13")),
        Subsignal("clk", Pins("D6")),
        Subsignal("cmd", Pins("C6")),
        Subsignal("data", Pins("E6 B13 B12 B6")),
        Misc("SLEW=FAST"),
        IOStandard("LVCMOS33")
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors_vx = [
    ("PMODA", "A2 A3 A4 A5 B3 B4 B5 A6"),
    ("PMODB", "A12 A11 B11 B10 A9 A10 B8 B9"),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticeECP5Platform):
    default_clk_name   = "clk48"
    default_clk_period = 1e9/48e6

    def __init__(self, revision="v1", device="45F", toolchain="trellis", **kwargs):
        assert revision in ["v1", "v2"]
        assert device in ["25F", "45F", "85F"]
        self.revision = revision

        io = _io_vx
        connectors = _connectors_vx

        if revision == "v1": io += _io_v1
        if revision == "v2": io += _io_v2

        LatticeECP5Platform.__init__(self, f"LFE5U-{device}-6BG256", io, connectors, toolchain=toolchain, **kwargs)

    def create_programmer(self, cable):
        return OpenFPGALoader(cable=cable)

    def do_finalize(self, fragment):
        LatticeECP5Platform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk48", loose=True), 1e9/48e6)
