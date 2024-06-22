#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Lone Dynamics Corporation <info@lonedynamics.com>
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

    # Differential Data Multiple Interface
    ("ddmi", 0,
        Subsignal("clk_p",    Pins("L1"),
            IOStandard("LVCMOS33D"), Misc("DRIVE=4")),
        Subsignal("data0_p",  Pins("M1"),
            IOStandard("LVCMOS33D"), Misc("DRIVE=4")),
        Subsignal("data1_p",  Pins("R2"),
            IOStandard("LVCMOS33D"), Misc("DRIVE=4")),
        Subsignal("data2_p",  Pins("R4"),
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
        #Subsignal("dp", Pins("A3")),
        #Subsignal("dm", Pins("A4")),
        Subsignal("dp", Pins("A3 B1")),
        Subsignal("dm", Pins("A4 B2")),
        IOStandard("LVCMOS33")
    ),

    # 3.5MM AUDIO
    ("audio_pwm", 0,
        Subsignal("left", Pins("M3")),
        Subsignal("right", Pins("N1")),
        IOStandard("LVCMOS33")
    ),

    # 3.5MM VIDEO
    ("video_dac", 0,
        Subsignal("data", Pins("P1 R1 P2 N3")),
        IOStandard("LVCMOS33")
    ),

]

_io_v0 = [

    # SD card w/ SD-mode interface
    ("sdcard", 0,
        Subsignal("clk", Pins("F2"), Misc("PULLMODE=NONE")),
        Subsignal("cmd", Pins("K1"), Misc("PULLMODE=NONE")),
        Subsignal("data", Pins("F3 F1 K3 K2"), Misc("PULLMODE=NONE")),
        Misc("SLEWRATE=FAST"),
        IOStandard("LVCMOS33")
    ),

    # SD card w/ SPI interface
    ("spisdcard", 0,
        Subsignal("clk",  Pins("F2")),
        Subsignal("mosi", Pins("K1")),
        Subsignal("cs_n", Pins("K2")),
        Subsignal("miso", Pins("F3")),
        Misc("SLEWRATE=FAST"),
        IOStandard("LVCMOS33"),
    ),

    # UART PMOD
    ("serial", 0,
        Subsignal("tx", Pins("PMODA:1")),
        Subsignal("rx", Pins("PMODA:2")),
        IOStandard("LVCMOS33")
    ),

]

# Connectors ---------------------------------------------------------------------------------------

_connectors_vx = [
    ("PMODA", "B11 B12 B13 B14 A11 A12 A13 A14")
]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticeECP5Platform):
    default_clk_name   = "clk48"
    default_clk_period = 1e9/48e6

    def __init__(self, revision="v0", device="25F", toolchain="trellis", **kwargs):
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
