#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 Chengyin Yao <cyao@duck.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.lattice import LatticeECP5Platform
from litex.build.openfpgaloader import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io_common = [
    # Clock
    ("clk50", 0, Pins("M1"), IOStandard("LVCMOS33")),
    ("rst",   0, Pins("C4"), IOStandard("LVCMOS33"), Misc("PULLMODE=UP")), # Pull down?

    # Buttons
    ("user_btn", 0, Pins("C4"), IOStandard("LVCMOS33"), Misc("PULLMODE=UP")), # Pull down?
    ("user_btn", 1, Pins("C5"), IOStandard("LVCMOS33"), Misc("PULLMODE=UP")), # Pull down?

    # Leds
    ("user_led", 0, Pins("E13"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("D14"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("E12"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("C13"), IOStandard("LVCMOS33")),
    ("user_led", 4, Pins("D13"), IOStandard("LVCMOS33")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("K15"), IOStandard("LVCMOS33")),
        Subsignal("rx", Pins("K16"), IOStandard("LVCMOS33"))
    ),

    # SDR SDRAM
    ("sdram_clock", 0, Pins("A3"), IOStandard("LVCMOS33")),
    ("sdram", 0,
        Subsignal("a",     Pins(
            "B10 A9  B9  A8  B8  A7  B7  A6 ",
            "B6  A5  A10 B5  A4 ")),
        Subsignal("dq",    Pins(
            "B16 C14 C16 C15 D16 A15 B15 A14",
            "A2  B2  E2  D1  C2  C1  C3  B1 ")),
        Subsignal("we_n",  Pins("A13")),
        Subsignal("ras_n", Pins("A12")),
        Subsignal("cas_n", Pins("B13")),
        Subsignal("cs_n",  Pins("B12")),
        Subsignal("cke",   Pins("B4")),
        Subsignal("ba",    Pins("A11 B11")),
        Subsignal("dm",    Pins("B14 B3 ")),
        IOStandard("LVCMOS33"),
        Misc("SLEWRATE=FAST"),
    ),

    # GPIOs
    ("gpio", 0, 
        Pins("G3 K3 T2 R2 R1 E1 F3 G1 H2 J1 L2 G2 J3 E3 P1 N1 H3 R3 N4 E4 F1 F2 P2 M2 L1 J2 D4 P3"), 
        IOStandard("LVCMOS33")
    ),

    # USB
    ("usb", 0,
        Subsignal("d_p", Pins("F15")),
        Subsignal("d_n", Pins("E16")),
        Subsignal("pullup", Pins("G15 H14")),
        IOStandard("LVCMOS33")
    ),
    ("usb", 1,
        Subsignal("d_p", Pins("J16")),
        Subsignal("d_n", Pins("J15")),
        Subsignal("pullup", Pins("E14 E11")),
        IOStandard("LVCMOS33")
    ),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("N8")),
        Subsignal("miso", Pins("T7")),
        Subsignal("mosi", Pins("T8")),
        Subsignal("wp", Pins("M7")),
        Subsignal("hold", Pins("N7")),
        IOStandard("LVCMOS33")
    ),
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("N8")),
        Subsignal("dq", Pins("T8", "T7", "M7", "N7")),
        IOStandard("LVCMOS33")
    ),
    # CLK = N9

    # SDCard
    ("spisdcard", 0,
        Subsignal("clk",  Pins("P15")),
        Subsignal("mosi", Pins("N16"), Misc("PULLMODE=UP")),
        Subsignal("cs_n", Pins("M14"), Misc("PULLMODE=UP")),
        Subsignal("miso", Pins("P14"), Misc("PULLMODE=UP")),
        Misc("SLEWRATE=FAST"),
        IOStandard("LVCMOS33"),
    ),
    ("sdcard", 0,
        Subsignal("clk",  Pins("P15")),
        Subsignal("cmd",  Pins("N16"), Misc("PULLMODE=UP")),
        Subsignal("data", Pins("P14 R14 M15 M14"), Misc("PULLMODE=UP")),
        Misc("SLEWRATE=FAST"),
        IOStandard("LVCMOS33"),
    ),

    # GPDI
    ("gpdi", 0,
        Subsignal("clk_p",    Pins("R12"), IOStandard("LVCMOS33D"), Misc("DRIVE=4")),
        #Subsignal("clk_n",   Pins("T13"), IOStandard("LVCMOS33D"), Misc("DRIVE=4")),
        Subsignal("data0_p",  Pins("R13"), IOStandard("LVCMOS33D"), Misc("DRIVE=4")),
        #Subsignal("data0_n", Pins("T14"), IOStandard("LVCMOS33D"), Misc("DRIVE=4")),
        Subsignal("data1_p",  Pins("R15"), IOStandard("LVCMOS33D"), Misc("DRIVE=4")),
        #Subsignal("data1_n", Pins("T15"), IOStandard("LVCMOS33D"), Misc("DRIVE=4")),
        Subsignal("data2_p",  Pins("P16"), IOStandard("LVCMOS33D"), Misc("DRIVE=4")),
        #Subsignal("data2_n", Pins("R16"), IOStandard("LVCMOS33D"), Misc("DRIVE=4")),
        Subsignal("cec",     Pins("R5"), IOStandard("LVCMOS33"), Misc("PULLMODE=UP")),
        Subsignal("scl",     Pins("T3"), IOStandard("LVCMOS33"), Misc("PULLMODE=UP")),
        Subsignal("sda",     Pins("T4"), IOStandard("LVCMOS33"), Misc("PULLMODE=UP")),
        Subsignal("hpd",     Pins("L14"), IOStandard("LVCMOS33"), Misc("PULLMODE=UP")),
        Subsignal("util",     Pins("P5"), IOStandard("LVCMOS33"), Misc("PULLMODE=UP"))
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticeECP5Platform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self, device="LFE5U-25F", toolchain="trellis", **kwargs):
        assert device in ["LFE5U-25F", "LFE5U-45F"]
        _io = _io_common
        LatticeECP5Platform.__init__(self, device + "-6BG256C", _io, toolchain=toolchain, **kwargs)

    def create_programmer(self):
        return OpenFPGALoader(board="icepi-zero")

    def do_finalize(self, fragment):
        LatticeECP5Platform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)

