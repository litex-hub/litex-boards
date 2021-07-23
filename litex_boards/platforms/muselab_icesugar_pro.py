#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Lucas Teske <lucas@teske.com.br>
# SPDX-License-Identifier: BSD-2-Clause

# The Muselab IceSugar Pro PCB and IOs have been documented by @wuxx
# https://github.com/wuxx/icesugar-pro

from litex.build.generic_platform import *
from litex.build.lattice import LatticePlatform
from litex.build.lattice.programmer import EcpDapProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk
    ("clk25", 0, Pins("P6"), IOStandard("LVCMOS33")),

    # Led
    ("user_led_n", 0, Pins("B11"), IOStandard("LVCMOS33")), # Red
    ("user_led_n", 1, Pins("A11"), IOStandard("LVCMOS33")), # Green
    ("user_led_n", 2, Pins("A12"), IOStandard("LVCMOS33")), # Blue

    ("rgb_led", 0,
        Subsignal("r", Pins("B11")),
        Subsignal("g", Pins("A11")),
        Subsignal("b", Pins("A12")),
        IOStandard("LVCMOS33"),
    ),

    # Reset button
    ("cpu_reset_n", 0, Pins("L14"), IOStandard("LVCMOS33"), Misc("PULLMODE=UP")),

    # Serial
    ("serial", 0, # iCELink
        Subsignal("tx", Pins("B9")),
        Subsignal("rx", Pins("A9")),
        IOStandard("LVCMOS33")
    ),

    # SPIFlash (W25Q256JV (32MB))
    ("spiflash", 0,
        Subsignal("cs_n", Pins("N8")),
        # https://github.com/m-labs/nmigen-boards/pull/38
        #Subsignal("clk",  Pins("")), driven through USRMCLK
        Subsignal("mosi", Pins("T8")),
        Subsignal("miso", Pins("T7")),
        IOStandard("LVCMOS33"),
    ),

    # SDRAM (IS42S16160B (32MB))
    ("sdram_clock", 0, Pins("R15"), IOStandard("LVCMOS33")),
    ("sdram", 0,
        Subsignal("a", Pins(
            "H15 B13 B12 J16 J15 R12 K16 R13",
            "T13 K15 A13 R14 T14")),
        Subsignal("dq", Pins(
            "F16 E15 F15 D14 E16 C15 D16 B15",
            "R16 P16 P15 N16 N14 M16 M15 L15")),
        Subsignal("we_n",  Pins("A15")),
        Subsignal("ras_n", Pins("B16")),
        Subsignal("cas_n", Pins("G16")),
        Subsignal("cs_n", Pins("A14")),
        Subsignal("cke",  Pins("L16")),
        Subsignal("ba",    Pins("G15 B14")),
        Subsignal("dm",   Pins("C16 T15")),
        IOStandard("LVCMOS33"),
        Misc("SLEWRATE=FAST")
    ),

    # SDCard
    ("spisdcard", 0,
        Subsignal("clk",  Pins("J12")),
        Subsignal("mosi", Pins("H12"), Misc("PULLMODE=UP")),
        Subsignal("cs_n", Pins("G12"), Misc("PULLMODE=UP")),
        Subsignal("miso", Pins("K12"), Misc("PULLMODE=UP")),
        Misc("SLEWRATE=FAST"),
        IOStandard("LVCMOS33"),
    ),
    ("sdcard", 0,
        Subsignal("clk", Pins("J12")),
        Subsignal("cmd", Pins("H12"), Misc("PULLMODE=UP")),
        Subsignal("data", Pins("K12 L12 F12 G12"), Misc("PULLMODE=UP")),
        Misc("SLEWRATE=FAST"),
        IOStandard("LVCMOS33")
     ),

    # GPDI
    ("gpdi", 0,
        Subsignal("clk_p",   Pins("E2"), IOStandard("LVCMOS33"), Misc("DRIVE=4")),
        # Subsignal("clk_n",   Pins("D3"), IOStandard("LVCMOS33"), Misc("DRIVE=4")),
        Subsignal("data0_p", Pins("G1"), IOStandard("LVCMOS33"), Misc("DRIVE=4")),
        # Subsignal("data0_n", Pins("F1"), IOStandard("LVCMOS33"), Misc("DRIVE=4")),
        Subsignal("data1_p", Pins("J1"), IOStandard("LVCMOS33"), Misc("DRIVE=4")),
        # Subsignal("data1_n", Pins("H2"), IOStandard("LVCMOS33"), Misc("DRIVE=4")),
        Subsignal("data2_p", Pins("L1"), IOStandard("LVCMOS33"), Misc("DRIVE=4")),
        # Subsignal("data2_n", Pins("K2"), IOStandard("LVCMOS33"), Misc("DRIVE=4")),
    ),
]

# from colorlight_i5.py adapted to icesugar pro
# https://github.com/wuxx/icesugar-pro/blob/master/doc/iCESugar-pro-pinmap.png
_connectors = [
    ("pmode", "N3  M2  L2  G2  P1  N1  M1  K1"),
    ("pmodf", "T6  R5  R4  R3  P7  R6  T4  T3"),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticePlatform):
    default_clk_name   = "clk25"
    default_clk_period = 1e9/25e6

    def __init__(self, toolchain="trellis"):
        device     = "LFE5U-25F-6BG256C"
        io         = _io
        connectors = _connectors
        LatticePlatform.__init__(self, device, io, connectors=connectors, toolchain=toolchain)

    def create_programmer(self):
        return EcpDapProgrammer()

    def do_finalize(self, fragment):
        LatticePlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk25", loose=True), 1e9/25e6)
