#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 Myrtle Shah <gatecat@ds0.me>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.lattice import LatticeNexusPlatform
from litex.build.lattice.programmer import LatticeProgrammer
from litex.build.lattice.programmer import EcpprogProgrammer
from litex.build.lattice.programmer import OpenOCDJTAGProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Section 5.1 Clock sources
    ("clk12", 0, Pins("G13"), IOStandard("LVCMOS33")), # Ensure JP4 is installed
    ("clk25", 0, Pins("F16"), IOStandard("LVCMOS33")),
    ("clk27", 0, Pins("G15"), IOStandard("LVCMOS33")),

    # Clock signal is differential, but we only name the "p" side.
    ("clk100", 0, Pins("P1"), IOStandard("LVDS")),
    ("clk125", 0, Pins("L6"), IOStandard("LVDS")),

    ("clk100_clk_dis", 0, Pins("F15"), IOStandard("LVCMOS33")),
    ("clk125_clk_dis", 0, Pins("H10"), IOStandard("LVCMOS33")),

    # 7.2. General Purpose Push Buttons - all logic zero when pressed
    ("gsrn",     0, Pins("G3"),  IOStandard("LVCMOS18")),   # SW6
    ("programn", 0, Pins("C12"), IOStandard("LVCMOS18")),   # SW4
    ("user_btn", 0, Pins("G4"),  IOStandard("LVCMOS18")),   # SW3
    ("user_btn", 1, Pins("G2"),  IOStandard("LVCMOS18")),   # SW5
    ("user_btn", 2, Pins("J16"), IOStandard("LVCMOS33")),   # SW2

    # 6.2. UART Topology - close JP25 and JP26
    ("serial", 0,
        Subsignal("rx", Pins("F10"), IOStandard("LVCMOS33")),
        Subsignal("tx", Pins("E13"), IOStandard("LVCMOS33")),
    ),

    # Section 7.3 General Purpose LEDs
    ("user_led", 0, Pins("B3"),  IOStandard("LVCMOS33")),  # Bank 2 Green
    ("user_led", 1, Pins("A2"),  IOStandard("LVCMOS33")),  # Bank 2 Green
    ("user_led", 2, Pins("H16"), IOStandard("LVCMOS33")),  # Bank 2 Green
    ("user_led", 3, Pins("B2"),  IOStandard("LVCMOS33")),  # Bank 2 Green
    ("user_led", 4, Pins("H15"), IOStandard("LVCMOS33")),  # Bank 2 Green
    ("user_led", 5, Pins("H14"), IOStandard("LVCMOS33")),  # Bank 2 Green
    ("user_led", 6, Pins("H12"), IOStandard("LVCMOS33")),  # Bank 2 Green
    ("user_led", 7, Pins("J15"), IOStandard("LVCMOS33")),  # Bank 2 Green

    ("seven_seg", 0, Pins("G16 G14 G12 G11 E12 E10 E9 F9"), IOStandard("LVCMOS33")),

    # Section 7.1 DIP Switch
    ("user_dip_btn", 0, Pins("L10"), IOStandard("LVCMOS15H")),
    ("user_dip_btn", 1, Pins("E16"), IOStandard("LVCMOS18")),
    ("user_dip_btn", 2, Pins("L11"), IOStandard("LVCMOS15H")),
    ("user_dip_btn", 3, Pins("R3"),  IOStandard("LVCMOS15H")),

    # Section 6.3.1. SPI Configuration
    ("spiflash", 0,
        Subsignal("cs_n", Pins("C15")),
        Subsignal("clk",  Pins("C16")),
        Subsignal("mosi", Pins("C14")),
        Subsignal("miso", Pins("D16")),
        Subsignal("wp",   Pins("D15")),
        Subsignal("hold", Pins("D12")),
        IOStandard("LVCMOS18")
    ),

    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("C15")),
        Subsignal("clk",  Pins("C16")),
        Subsignal("dq",   Pins("C14 D16 D15 D12")),
        IOStandard("LVCMOS18")
    ),

    # DDR3 SDRAM
    ("ddram", 0,
        Subsignal("a", Pins(
            "R4 P7 R2 L8 R6 T2 R5 P4 P6 T6 P8 T5 R7"),
            IOStandard("SSTL15_I")),
        Subsignal("ba",    Pins("N8 R8 M8"), IOStandard("SSTL15_I")),
        Subsignal("ras_n", Pins("R9"), IOStandard("SSTL15_I")),
        Subsignal("cas_n", Pins("M10"), IOStandard("SSTL15_I")),
        Subsignal("we_n",  Pins("L9"), IOStandard("SSTL15_I")),
        Subsignal("cs_n",  Pins("M9"), IOStandard("SSTL15_I")),
        Subsignal("dm", Pins("N12 P14"), IOStandard("SSTL15_I")),
        Subsignal("dq", Pins(
            "R13 N11 T12 R14 T11 P10 P11 R10 "
            "M12 L12 M11 N13 M16 M13 M14 N14"),
            IOStandard("SSTL15_I"),
            Misc("TERMINATION=75"),
            Misc("VREF=VREF1_LOAD")),
        Subsignal("dqs_p", Pins("R12 N16"), IOStandard("SSTL15D_I"),
            Misc("TERMINATION=OFF")),
        Subsignal("clk_p", Pins("T9"), IOStandard("SSTL15D_I")),
        Subsignal("cke",   Pins("P9"), IOStandard("SSTL15_I")),
        Subsignal("odt",   Pins("N9"), IOStandard("SSTL15_I")),
        Subsignal("reset_n", Pins("P5"), IOStandard("SSTL15_I")),
        Misc("SLEWRATE=FAST"),
    ),


]


# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    # Section 8.7 PMOD Header
    # PMOD signal number:
    #          1   2   3   4   7  8  9  10
    ("PMOD0", "J11 J12 K11 K12 C8 C7 B7 A7"),
    ("PMOD1", "A6  B6  B5  A5  A4 B4 C4 C5"),
    ("PMOD2", "H1  H2  N1  K5  N2 L3 M3 L5"),
]


# Platform -----------------------------------------------------------------------------------------

class Platform(LatticeNexusPlatform):
    default_clk_name   = "clk12"
    default_clk_period = 1e9/12e6

    def __init__(self, toolchain="radiant", **kwargs):
        LatticeNexusPlatform.__init__(self, "LFD2NX-40-8BG256C", _io, _connectors, toolchain=toolchain, **kwargs)

    def request(self, *args, **kwargs):
        return LatticeNexusPlatform.request(self, *args, **kwargs)

    def create_programmer(self, mode = "direct", prog="ecpprog"):
        assert mode in ["direct","flash"]
        assert prog in ["ecpprog", ]

        if prog == "ecpprog":
            return EcpprogProgrammer()

