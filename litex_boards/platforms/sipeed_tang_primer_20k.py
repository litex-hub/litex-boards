#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Icenowy Zheng <icenowy@aosc.io>
# Copyright (c) 2022 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.build.generic_platform import *
from litex.build.gowin.platform import GowinPlatform
from litex.build.gowin.programmer import GowinProgrammer
from litex.build.openfpgaloader import OpenFPGALoader


# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst.
    ("clk27",  0, Pins("H11"), IOStandard("LVCMOS33")),

    # Serial.
    ("serial", 0,
        Subsignal("rx", Pins("T13")), # CARD1:1
        Subsignal("tx", Pins("M11")), # CARD1:11
        IOStandard("LVCMOS33")
    ),

    # SPIFlash.
    ("spiflash", 0,
        Subsignal("cs_n", Pins("M9"),  IOStandard("LVCMOS33")),
        Subsignal("clk",  Pins("L10"), IOStandard("LVCMOS33")),
        Subsignal("miso", Pins("P10"), IOStandard("LVCMOS33")),
        Subsignal("mosi", Pins("R10"), IOStandard("LVCMOS33")),
    ),

    # SDCard.
    ("spisdcard", 0,
        Subsignal("clk",  Pins("N10")),
        Subsignal("mosi", Pins("R14")),
        Subsignal("cs_n", Pins("N11")),
        Subsignal("miso", Pins("M8")),
        IOStandard("LVCMOS33"),
    ),
    ("sdcard", 0,
        Subsignal("data", Pins("M8 M7 M10 N11")),
        Subsignal("cmd",  Pins("R14")),
        Subsignal("clk",  Pins("N10")),
        Subsignal("cd",   Pins("D15")),
        IOStandard("LVCMOS33"),
    ),

    # DDR3 SDRAM IMD128M16R39CG8GNF-125.
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
]

# Dock 204 Pins SODIMM Connector -------------------------------------------------------------------

_connectors = [
    ["CARD1",
        # A.
        # -------------------------------------------------
        "---", # 0
        #     GND GND  5V  5V  5V  5V GND GND  NC   ( 1-10).
        " T13 --- --- --- --- --- --- --- --- ---",
        #      NC GND GND      NC  NC  NC GND GND   (11-20).
        " M11 --- --- --- T10 --- --- --- --- ---",
        #  NC 3V3  NC 3V3 GND GND                   (21-30).
        " --- --- --- --- --- ---  T6 R16  P6 P15",
        # GND GND                 GND GND           (31-40).
        " --- ---  T7 P16  R8 N15 --- ---  T8  N16",
        #         GND                 GND GND       (41-50).
        "  M6 N14 --- L16  T9 L14  P9 --- --- K15",
        #             GND GND                 GND   (51-60).
        " P11 K14 T11 --- --- K16 R11 J15 T12 ---",
        # GND                 GND                   (61-70).
        " --- H16 R12 H14 P13 --- R13 G16 T14 H15",
        # GND GND                                   (71-72).
        " --- ---",
        # B.
        # -------------------------------------------------
        #                                      NC   (73-82).
        " M15 L13 M14 K11 F13 K12 G12 K13 T15 ---",
        #                  NC  NC                   (83-92).
        " J16 H13 J14 J12 --- --- G14 H12 G15 G11",
        #  NC  NC                  NC  NC      NC  (93-102).
        " --- --- F14 B10 F16 A13 --- --- E15 ---",
        #      NC  NC  NC      NC      NC  NC  NC  (103-112).
        " D15 --- --- --- A15 --- B14 --- --- ---",
        #      NC      NC  NC  NC      NC      NC  (113-122).
        " A14 --- B13 --- --- --- C12 --- B12 ---",
        #      NC      NC GND GND                  (123-132).
        " A12 --- C11 --- --- --- B11 E16 A11 F15",
        # GND GND          NC GND GND      NC      (133-142).
        " --- --- C10 C13 --- --- --- D16 --- E14",
        #     GND GND                 GND GND      (143-152).
        "  B8 --- ---  C9  C6  A9  A7 --- --- L12",
        #         GND GBD                 GND GND  (153-162).
        "  A6 J11 --- ---  C7  E9  D7  E8 --- ---",
        #     VCC     VCC GND GND     VCC     GND  (163-172).
        "  T2 ---  T3 --- --- ---  T4 ---  T5 ---",
        # GND VCC             GND GND              (173-182).
        " --- ---  N6 F10  N7 --- --- D11  N9 D10",
        #     GND GND      NC  NC GND GND          (183-192).
        "  R9 --- --- E10 --- --- --- ---  N8 R7",
        #         GND GND  NC      NC      NC  NC  (193-202).
        "  L9  P7 --- --- ---  M6 ---  L8 --- ---",
        #  NC  NC                                  (203-204).
        " --- ---",
    ],
]

# Dock IOs -----------------------------------------------------------------------------------------

_dock_io = [
    # Leds
    ("led", 0,  Pins( "CARD1:44"), IOStandard("LVCMOS18")), # CHECKME: Should be LVCMOS33.
    ("led", 1,  Pins( "CARD1:46"), IOStandard("LVCMOS18")), # CHECKME: Should be LVCMOS33.
    ("led", 3,  Pins( "CARD1:40"), IOStandard("LVCMOS18")), # CHECKME: Should be LVCMOS33.
    ("led", 2,  Pins( "CARD1:42"), IOStandard("LVCMOS18")), # CHECKME: Should be LVCMOS33.
    ("led", 4,  Pins( "CARD1:98"), IOStandard("LVCMOS33")),
    ("led", 5,  Pins("CARD1:136"), IOStandard("LVCMOS33")),

    # RGB Led.
    ("rgb_led", 0, Pins("CARD1:45"), IOStandard("LVCMOS18")),

    # Buttons.
    ("btn_n", 0,  Pins( "CARD1:15"), IOStandard("LVCMOS33")),
    ("btn_n", 1,  Pins("CARD1:165"), IOStandard("LVCMOS15")),
    ("btn_n", 2,  Pins("CARD1:163"), IOStandard("LVCMOS15")),
    ("btn_n", 3,  Pins("CARD1:159"), IOStandard("LVCMOS15")),
    ("btn_n", 4,  Pins("CARD1:157"), IOStandard("LVCMOS15")),

    # HDMI.
    ("hdmi", 0,
        Subsignal("clk_p",   Pins("CARD1:68")),
        Subsignal("clk_n",   Pins("CARD1:70")),
        Subsignal("data0_p", Pins("CARD1:64")),
        Subsignal("data0_n", Pins("CARD1:62")),
        Subsignal("data1_p", Pins("CARD1:58")),
        Subsignal("data1_n", Pins("CARD1:56")),
        Subsignal("data2_p", Pins("CARD1:52")),
        Subsignal("data2_n", Pins("CARD1:50")),
        Subsignal("hdp", Pins("CARD1:154"), IOStandard("LVCMOS18")),
        Subsignal("cec", Pins("CARD1:152"), IOStandard("LVCMOS18")),
        Subsignal("sda", Pins("CARD1:95"),  IOStandard("LVCMOS18")),
        Subsignal("scl", Pins("CARD1:97"),  IOStandard("LVCMOS18")),
        Misc("PULL_MODE=NONE"),
    ),

    # LCD.
    ("lcd", 0,
        # Control.
        Subsignal("rst",   Pins("CARD1:123")),
        Subsignal("bl",    Pins("CARD1:186")),
        Subsignal("sda",   Pins("CARD1: 95")),
        Subsignal("scl",   Pins("CARD1: 97")),
        Subsignal("int",   Pins("CARD1:125")),

        # Video.
        Subsignal("clk",   Pins("CARD1:183")),
        Subsignal("de",    Pins("CARD1:101")),
        Subsignal("hsync", Pins("CARD1:107")),
        Subsignal("vsync", Pins("CARD1:103")),
        Subsignal("r",     Pins("CARD1:193 CARD1:191 CARD1:181 CARD1:177 CARD1:175")),
        Subsignal("g",     Pins("CARD1:180 CARD1:131 CARD1:129 CARD1:194 CARD1:192 CARD1:182")),
        Subsignal("b",     Pins("CARD1:121 CARD1:119 CARD1:115 CARD1:113 CARD1:109")),
        IOStandard("LVCMOS18")
    ),

    # RMII Ethernet
    ("eth_clocks", 0,
        Subsignal("ref_clk", Pins("CARD1:148")),
        IOStandard("LVCMOS33"),
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("CARD1:176")),
        Subsignal("rx_data", Pins("CARD1:132 CARD1:146")),
        Subsignal("crs_dv",  Pins("CARD1:198")),
        Subsignal("tx_en",   Pins("CARD1:130")),
        Subsignal("tx_data", Pins("CARD1:140 CARD1:142")),
        Subsignal("mdc",     Pins("CARD1:95")),
        Subsignal("mdio",    Pins("CARD1:97")),
        Subsignal("rx_er",   Pins("CARD1:200")),
        #Subsignal("int_n",   Pins("CARD1:")),
        IOStandard("LVCMOS33")
     ),
]

# Dock Lite IOs ------------------------------------------------------------------------------------

_dock_lite_io = [
    # Buttons.
    ("btn_n",   0, Pins("CARD1:15"),  IOStandard("LVCMOS33")),
    ("btn_n",   1, Pins("CARD1:163"), IOStandard("LVCMOS15")),

    # Switches
    ("user_sw", 0, Pins("CARD1:159"), IOStandard("LVCMOS15")),
    ("user_sw", 1, Pins("CARD1:157"), IOStandard("LVCMOS15")),
]

_dock_lite_connectors = [
    # Pmod
    ("j2", "F15 D16 C9  L12 E15 E14 A9  J11"),
    ("j6", "L8  P7  E10 D11 M6  R7  D10 F10"),
    ("j7", "T6  T7  T8  T9  P6  R8  M6  P9"),
    ("j8", "R16 P16 N16 L16 P15 N15 N14 L14"),

    ("j1", {
         7: "T5",
         9: "T3",  10: "T5",
        13: "E9",  14: "E8",
        15: "T15", 16: "C13",
        17: "T13", 18: "M11",
        19: "B10", 20: "A13",
        21: "H12", 22: "G11",
        23: "H13", 24: "J12",
        25: "K12", 26: "K13",
        27: "L13", 28: "K11",
        29: "R11", 30: "T12",
        31: "P11", 32: "T11",
        33: "G16", 34: "H15",
        35: "H16", 36: "H14",
        37: "K16", 38: "J15",
        39: "K15", 40: "K14",
    }),
    ("j3", {
         3: "N6",   4: "N7",
         5: "B11",  6: "A12",
         7: "L9",   8: "N8",
         9: "R9",  10: "N9",
        11: "A6",  12: "A7",
        13: "C6",  14: "B8",
        15: "C10",
        17: "A11", 18: "C11",
        19: "B12", 20: "C12",
        21: "B13", 22: "A14",
        23: "B14", 24: "A15",
        25: "D15", 26: "E15",
        27: "F16", 28: "F14",
        29: "G15", 30: "G14",
        31: "J14", 32: "J16",
        33: "G12", 34: "F13",
        35: "M14", 36: "M15",
        37: "T14", 38: "R13",
        39: "P13", 40: "R12",
    })
]

# Platform -----------------------------------------------------------------------------------------

class Platform(GowinPlatform):
    default_clk_name   = "clk27"
    default_clk_period = 1e9/27e6

    def __init__(self, dock="standard", toolchain="gowin"):

        GowinPlatform.__init__(self, "GW2A-LV18PG256C8/I7", _io, _connectors, toolchain=toolchain, devicename="GW2A-18C")
        self.add_extension(_dock_io if dock == "standard" else _dock_lite_io)
        if dock == "lite":
            self.add_connector(_dock_lite_connectors)

        self.toolchain.options["use_mspi_as_gpio"]  = 1
        self.toolchain.options["use_sspi_as_gpio"]  = 1
        self.toolchain.options["use_ready_as_gpio"] = 1
        self.toolchain.options["use_done_as_gpio"]  = 1
        self.toolchain.options["rw_check_on_ram"]   = 1

    def create_programmer(self, kit="openfpgaloader"):
        return OpenFPGALoader(cable="ft2232")

    def do_finalize(self, fragment):
        GowinPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk27", loose=True), 1e9/27e6)
