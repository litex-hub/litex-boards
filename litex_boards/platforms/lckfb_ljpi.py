#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2024 Andelf <andelf@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause
#
# LCKFB LJPI FPGA board: https://wiki.lckfb.com/zh-hans/fpga-ljpi/

from migen import *

from litex.build.generic_platform import *
from litex.build.gowin.platform import GowinPlatform
from litex.build.gowin.programmer import GowinProgrammer, GOWIN_CABLE_FT2CH
from litex.build.openfpgaloader import OpenFPGALoader


# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst.
    ("clk50",  0, Pins("T7"), IOStandard("LVCMOS33")),

    # Serial.
    ("serial", 0,
        Subsignal("tx", Pins("F12")),
        Subsignal("rx", Pins("F13")),
        IOStandard("LVCMOS33")
    ),

    # Leds. LED2 and LED3 are RGB LEDs.
    ("led", 0,  Pins( "R9"), IOStandard("LVCMOS33")),
    ("led", 1,  Pins("C10"), IOStandard("LVCMOS33")),
    ("led", 3,  Pins( "R7"), IOStandard("LVCMOS33")),
    ("led", 2,  Pins( "N6"), IOStandard("LVCMOS33")),
    ("led", 4,  Pins("T10"), IOStandard("LVCMOS33")),
    ("led", 5,  Pins( "P7"), IOStandard("LVCMOS33")),

    # Buttons. SW2
    ("btn_n", 0,  Pins("D11"), IOStandard("LVCMOS33")),
    # ("btn_n", 1,  Pins("F10"), IOStandard("LVCMOS33")),

    # Reset. Use SW3 as reset button.
    ("rst_n", 0,  Pins("F10"), IOStandard("LVCMOS33")),

    # SPIFlash.
    # W25Q64JVSSIQ
    ("spiflash", 0,
        Subsignal("cs_n", Pins("M9"),  IOStandard("LVCMOS33")),
        Subsignal("clk",  Pins("L10"), IOStandard("LVCMOS33")),
        Subsignal("miso", Pins("P10"), IOStandard("LVCMOS33")),
        Subsignal("mosi", Pins("R10"), IOStandard("LVCMOS33")),
    ),

    # HDMI(LVDS).
    ("hdmi", 0,
        Subsignal("clk_p",   Pins("M10")),
        Subsignal("clk_n",   Pins("N11")),
        Subsignal("data0_p", Pins("R13")),
        Subsignal("data0_n", Pins("T14")),
        Subsignal("data1_p", Pins("R11")),
        Subsignal("data1_n", Pins("T12")),
        Subsignal("data2_p", Pins("R12")),
        Subsignal("data2_n", Pins("P13")),
        IOStandard("LVCMOS33D DRIVE=8"),
        Misc("PULL_MODE=NONE"),
    ),

    # 8-segment LED display, Common Anode.
    ("seg8", 0, Pins("G13"), IOStandard("LVCMOS33")),
    ("seg8", 1, Pins("H16"), IOStandard("LVCMOS33")),
    ("seg8", 2, Pins("H12"), IOStandard("LVCMOS33")),
    ("seg8", 3, Pins("H13"), IOStandard("LVCMOS33")),
    ("seg8", 4, Pins("H14"), IOStandard("LVCMOS33")),
    ("seg8", 5, Pins("G12"), IOStandard("LVCMOS33")),
    ("seg8", 6, Pins("G11"), IOStandard("LVCMOS33")),
    # ("seg8", 7, Pins("L14"), IOStandard("LVCMOS33")),

    # DDR3 SDRAM
    # MT41J128M16JT-125K.
    ("ddram", 0,
        Subsignal("a", Pins("F7 A4 D6 F8 C4 E6 B1 D8 A5 F9 K3 B7 A3 C8"),
            IOStandard("SSTL15")),
        Subsignal("ba", Pins("H4 D3 H5"), IOStandard("SSTL15")),
        Subsignal("ras_n", Pins("R4"), IOStandard("SSTL15")),
        Subsignal("cas_n", Pins("R6"), IOStandard("SSTL15")),
        Subsignal("we_n",  Pins("L2"), IOStandard("SSTL15")),
        Subsignal("cs_n",  Pins("P5"), IOStandard("SSTL15")),
        Subsignal("dm", Pins("G1 K5"), IOStandard("SSTL15")),
        Subsignal("dq", Pins(
            "G5 F5 F4 F3 E2 C1 E1 B3",
            "M3 K4 N2 L1 P4 H3 R1 M2"),
            IOStandard("SSTL15"),
            Misc("VREF=INTERNAL")),
        Subsignal("dqs_p", Pins("G2 J5"), IOStandard("SSTL15D")),
        Subsignal("dqs_n", Pins("G3 K6"), IOStandard("SSTL15D")),
        Subsignal("clk_p", Pins("J1"), IOStandard("SSTL15D")),
        Subsignal("clk_n", Pins("J3"), IOStandard("SSTL15D")),
        Subsignal("cke",   Pins("J2"), IOStandard("SSTL15")),
        Subsignal("odt",   Pins("R3"), IOStandard("SSTL15")),
        Subsignal("reset_n", Pins("B9"), IOStandard("SSTL15")),
    ),

    # USB Type-C.
    ("usb", 0,
        Subsignal("d_p", Pins("M14")),
        Subsignal("d_n", Pins("M15")),
        Subsignal("pullup", Pins("L15")),
        IOStandard("LVCMOS33")
    ),

    # Wired to onboard GD32 MCU.
    ("mcu_bus", 0,
        Subsignal("data", Pins("PA0 PA1 PA2 PA3 PA4 PA5 PA6 PA7"), IOStandard("LVCMOS33"))),
]

# Connector IOs ------------------------------------------------------------------------------------

_connectors = [
    ("h5", {
        1:  "K16",   2: "J15",
        3:  "J14",   4: "J16",
        5:  "F14",   6: "F16",
        7:  "J13",   8: "H11",
        9:  "E16",  10: "F15",
        11: "C16",  12: "D15",
        13: "D16",  14: "E14",
        15: "B13",  16: "A14",
        17: "B14",  18: "A15",
        19: "A12",  20: "B11",
        21: "B12",  22: "C12",
        23: "C11",  24: "A11",
        25: "C9",   26: "A9",
        27: "E10",  28: "D10",
        29: "N10",  30: "M11",
        31: "P12",  32: "P11",
        33: "T13",  34: "T11",
        35: "R14",  36: "T15",
    }),
    ("h6", {
        7:  "G15",  8:  "G14",
        9:  "G16",  10: "H15",
        11: "L9",
        13: "L8",   14: "N9",
        15: "M6",   16: "M8",
        17: "M7",   18: "T6",
        19: "N7",   20: "N8",
        21: "P6",   22: "R8",
        23: "T9",   24: "P9",
        25: "T8",   26: "P8",
        27: "K14",  28: "K15",
        29: "K13",  30: "K12",
        31: "N15",  32: "P16",
        33: "P15",  34: "R16",
        35: "N16",  36: "N14",
    }),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(GowinPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self, toolchain="gowin"):

        GowinPlatform.__init__(self, "GW2A-LV18PG256C8/I7", _io, _connectors, toolchain=toolchain, devicename="GW2A-18C")

        self.toolchain.options["use_mspi_as_gpio"]  = 1
        self.toolchain.options["use_sspi_as_gpio"]  = 1

    def create_programmer(self, kit="openfpgaloader"):
        if kit == "gowin":
            # The board provides an external programmer with an emulated FT2232
            return GowinProgrammer(self.devicename, cable=GOWIN_CABLE_FT2CH)
        else:
            return OpenFPGALoader(cable="ft2232")

    def do_finalize(self, fragment):
        GowinPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
