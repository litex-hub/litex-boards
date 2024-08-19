#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2023 Gwenhael Goavec-Merou <gwenhael.goavec-merou@trabucayre.com>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.build.generic_platform import *
from litex.build.gowin.platform import GowinPlatform
from litex.build.openfpgaloader import OpenFPGALoader


# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst.
    ("clk50",  0, Pins("E2"), IOStandard("LVCMOS33")),

    # SPIFlash.
    ("spiflash", 0,
        Subsignal("cs_n", Pins("E6"), IOStandard("LVCMOS33")),
        Subsignal("clk",  Pins("E7"), IOStandard("LVCMOS33")),
        Subsignal("mosi", Pins("D6"), IOStandard("LVCMOS33")),
        Subsignal("miso", Pins("E5"), IOStandard("LVCMOS33")),
        Subsignal("wp",   Pins("D5"), IOStandard("LVCMOS33")),
        Subsignal("hold", Pins("E4"), IOStandard("LVCMOS33")),
    ),
    ("spiflashx4", 0,
        Subsignal("cs_n", Pins("E6"),          IOStandard("LVCMOS33")),
        Subsignal("clk",  Pins("E7"),          IOStandard("LVCMOS33")),
        Subsignal("dq",   Pins("D6 E5 D5 E4"), IOStandard("LVCMOS33")),
    ),
]

# Dock 204 Pins SODIMM Connector -------------------------------------------------------------------

_connectors = [
    ["J1",
        # -------------------------------------------------
        "---", # 0
        # GND GND                                   ( 1-10).
        " --- --- L9  H5  K9  J5  J8  L5  K8  K5",
        #                 GND                       (11-20).
        "  F7  H8  F6  H7 ---  G7  E8  G8  B3  F5",
        #             3V3     3V3 GND GND 3V3       (21-30).
        "  C3  G5  E3 ---  D7 --- --- --- ---  L6",
        # 3V3                                       (31-40).
        " ---  K6 J11  K7 J10  J7 H11  L7 H10  L8",
        #                 GND                 GND   (41-50).
        " G11 L10 G10 K10 --- K11 D11 L11 D10 ---",
        #                                 GND GND   (51-60).
        " C11 E11 C10 E10 B11 A11 B10 A10 --- ---",
    ],
    ["J2",
        # ----------------------------------------------------------------------
        "---", # 0
        # GND     3V3         3V3                                       ( 1-10).
        " ---     ---      B2 ---      C2  L2      F2  L1      F1  K1",
        #                                                     GND       (11-20).
        "  A1      K2      D8  J4      E1  K4      D1  G2     ---  G1",
        # TCK             TMS         TDO         TDI         GND       (21-30).
        "  C1      L4      B1  L3      A2  J1      A3  J2     ---  G4",
        #                             GND             1V8         1V8   (31-40).
        " M0_D3_P  H4 M0_D3_N  H1     ---  H2 M0_D2_P --- M0_D2_N ---",
        # GND     2V5         2V5         3V3     GND 3V3         3V3   (41-50).
        " ---     --- M0_CK_P --- M0_CK_N ---     --- --- M0_D1_P ---",
        #          5V     GND GND          5V          5V     GND  5V   (51-60).
        " M0_D1_N ---     --- --- M0_D0_P --- M0_D0_N ---     --- ---",
    ],
]

# Dock IOs -----------------------------------------------------------------------------------------

_dock_io = [
    # Serial.
    ("serial", 0,
        Subsignal("rx", Pins("J1:19")),
        Subsignal("tx", Pins("J1:21")),
        IOStandard("LVCMOS33")
    ),

    # Leds.
    ("led", 0, Pins("J1:17"), IOStandard("LVCMOS33")), # Pin READY.
    ("led", 1, Pins("J1:25"), IOStandard("LVCMOS33")), # Pin DONE.

    # Buttons.
    ("btn_n", 0, Pins("J1:37"), IOStandard("LVCMOS33")),
    ("btn_n", 1, Pins("J1:39"), IOStandard("LVCMOS33")),

    # USB.
    ("usb", 0,
        Subsignal("d_p", Pins("J1:30")),
        Subsignal("d_n", Pins("J1:32")),
        IOStandard("LVCMOS33"),
    ),
]

_dock_connectors = [
    # Pmod
    ("j4", "G11 D11 B11 C11 G10 D10 B10 C10"),
    ("j5", "A11 E11 K11  L5 A10 E10 L11  K5"),
    ("j6", " F5  G7  H8  H5  G5  G8  H7  J5"),

    ("j3", {
         1:  "K2",  2:  "K1",
         3:  "L1",  4:  "L2",
         5:  "K4",  6:  "J4",
         7:  "G1",  8:  "G2",
         9:  "L3", 10:  "L4",
        11: "---", 12: "---",
        13:  "C2", 14:  "B2",
        15:  "F1", 16:  "F2",
        17:  "A1", 18:  "E1",
        19:  "D1", 20:  "E3",
        21:  "J2", 22:  "J1",
        23:  "H4", 24:  "G4",
        25:  "H2", 26:  "H1",
        27:  "J7", 28:  "K7",
        29:  "L8", 30:  "L7",
        31: "K10", 32: "L10",
        33:  "K9", 34:  "L9",
        35:  "K8", 36:  "J8",
        37:  "F6", 38:  "F7",
        39: "J10", 40: "J11",
    }),
]

# SDRAMs -------------------------------------------------------------------------------------------

def misterSDRAM(conn="j3"):
    return [
        ("sdram_clock", 0, Pins(f"{conn}:20"),
            IOStandard("LVCMOS33"),
            Misc("PULL_MODE=NONE DRIVE=16"),
        ),
        ("sdram", 0,
            Subsignal("a",   Pins(
                f"{conn}:37 {conn}:38 {conn}:39 {conn}:40 {conn}:28 {conn}:25 {conn}:26 {conn}:23",
                f"{conn}:24 {conn}:21 {conn}:36 {conn}:22 {conn}:19")
            ),
            Subsignal("dq",  Pins(
                f"{conn}:1  {conn}:2  {conn}:3  {conn}:4  {conn}:5  {conn}:6  {conn}:7  {conn}:8",
                f"{conn}:18 {conn}:17 {conn}:16 {conn}:15 {conn}:14 {conn}:13 {conn}:10 {conn}:9")
            ),
            Subsignal("ba",    Pins(f"{conn}:34 {conn}:35")),
            Subsignal("cas_n", Pins(f"{conn}:31")),
            Subsignal("cs_n",  Pins(f"{conn}:33")),
            Subsignal("ras_n", Pins(f"{conn}:32")),
            Subsignal("we_n",  Pins(f"{conn}:27")),
            IOStandard("LVCMOS33"),
        ),
    ]

def sipeedSDRAM(conn="j3"):
    return [
        ("sdram_clock", 0, Pins(f"{conn}:20"),
            IOStandard("LVCMOS33"),
            Misc("PULL_MODE=NONE DRIVE=16"),
        ),
        ("sdram", 0,
            Subsignal("a",   Pins(
                f"{conn}:37 {conn}:38 {conn}:39 {conn}:40 {conn}:28 {conn}:25 {conn}:26 {conn}:23",
                f"{conn}:24 {conn}:21 {conn}:36 {conn}:22 {conn}:19")
            ),
            Subsignal("dq",  Pins(
                f"{conn}:1  {conn}:2  {conn}:3  {conn}:4  {conn}:5  {conn}:6  {conn}:7  {conn}:8",
                f"{conn}:18 {conn}:17 {conn}:16 {conn}:15 {conn}:14 {conn}:13 {conn}:10 {conn}:9"),
            ),
            Subsignal("ba",    Pins(f"{conn}:34 {conn}:35")),
            Subsignal("cas_n", Pins(f"{conn}:31")),
            Subsignal("cs_n",  Pins(f"{conn}:33")),
            Subsignal("ras_n", Pins(f"{conn}:32")),
            Subsignal("we_n",  Pins(f"{conn}:27")),
            Subsignal("dm",    Pins(f"{conn}:29 {conn}:30")),
            IOStandard("LVCMOS33"),
        ),
    ]

# Platform -----------------------------------------------------------------------------------------

class Platform(GowinPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self, toolchain="gowin"):

        GowinPlatform.__init__(self, "GW5A-LV25MG121NC1/I0", _io, _connectors, toolchain=toolchain, devicename="GW5A-25A")
        self.add_extension(_dock_io)
        self.add_connector(_dock_connectors)

        self.toolchain.options["use_mspi_as_gpio"]  = 1 # spi flash
        self.toolchain.options["use_i2c_as_gpio"]   = 1 # SDRAM / J3
        self.toolchain.options["use_ready_as_gpio"] = 1 # led
        self.toolchain.options["use_done_as_gpio"]  = 1 # led
        self.toolchain.options["use_cpu_as_gpio"]   = 1 # clk
        self.toolchain.options["rw_check_on_ram"]   = 1

    def create_programmer(self, kit="openfpgaloader"):
        return OpenFPGALoader(cable="ft2232")

    def do_finalize(self, fragment):
        GowinPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
