#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022-2023 Icenowy Zheng <uwu@icenowy.me>
# Copyright (c) 2022 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2023 Gwenhael Goavec-Merou <gwenhael@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.build.generic_platform import *
from litex.build.gowin.platform import GowinPlatform
from litex.build.gowin.programmer import GowinProgrammer
from litex.build.openfpgaloader import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst.
    ("clk50",  0, Pins("P16"), IOStandard("LVCMOS33")),
    ("rst",    0, Pins("U4"),  IOStandard("LVCMOS15")),

    # Serial.
    ("serial", 0,
        Subsignal("rx", Pins("N16")),
        Subsignal("tx", Pins("P15")),
        IOStandard("LVCMOS33")
    ),

    # SPIFlash.
    ("spiflash", 0,
        Subsignal("cs_n",   Pins("P18"), IOStandard("LVCMOS33")),
        Subsignal("clk",    Pins("H13"), IOStandard("LVCMOS33")),
        Subsignal("miso",   Pins("R15"), IOStandard("LVCMOS33")),
        Subsignal("mosi",   Pins("R14"), IOStandard("LVCMOS33")),
        Subsignal("wp_n",   Pins("P14"), IOStandard("LVCMOS33")),
        Subsignal("hold_n", Pins("N14"), IOStandard("LVCMOS33")),
    ),

    # PCI Express
    ("pcie", 0,
        Subsignal("rst_n", Pins("L23")),
    ),

    # Leds
    ("led_n", 0,  Pins("J14"), IOStandard("LVCMOS33")),
    ("led_n", 1,  Pins("R26"), IOStandard("LVCMOS33")),
    ("led_n", 2,  Pins("L20"), IOStandard("LVCMOS33")),
    ("led_n", 3,  Pins("M25"), IOStandard("LVCMOS33")),
    ("led_n", 4,  Pins("N21"), IOStandard("LVCMOS33")),
    ("led_n", 5,  Pins("N23"), IOStandard("LVCMOS33")),

    ("led_done", 0, Pins("W10"), IOStandard("LVCMOS33")),
    ("led_ready", 0, Pins("V11"), IOStandard("LVCMOS33")),

    # DDR3 SDRAM H5TQ4G63EFR-RDC
    ("ddram", 0,
        Subsignal("a", Pins(
            "N1 R1 R2 N2 P1 T2 N4 U1",
            "T4 T3 M1 P4 N3 U2 U5   "), # (M6 unused in 256x16)
            IOStandard("SSTL15"),
            Misc("DRIVE=12"),
        ),
        Subsignal("ba",      Pins("M4 L5 K3"),    IOStandard("SSTL15"), Misc("DRIVE=12")),
        Subsignal("ras_n",   Pins("H2"),          IOStandard("SSTL15"), Misc("DRIVE=12")),
        Subsignal("cas_n",   Pins("H1"),          IOStandard("SSTL15"), Misc("DRIVE=12")),
        Subsignal("we_n",    Pins("J3"),          IOStandard("SSTL15"), Misc("DRIVE=12")),
        Subsignal("cs_n",    Pins("L4"),          IOStandard("SSTL15"), Misc("DRIVE=12")),
        Subsignal("dm",      Pins("F4 H9 E3 A3"), IOStandard("SSTL15"), Misc("DRIVE=12")),
        Subsignal("dq",      Pins(
            "G4 J6 L8 G5 K7 J5 K8 K6",
            "E6 H8 H6 G8 D6 F8 G6 F7",
            "C4 F3 B4 E5 D3 D5 A4 D4",
            "E1 A2 G2 C2 F2 E2 G1 D1"),
            IOStandard("SSTL15"),
            Misc("DRIVE=12"),
            ),
        Subsignal("dqs_p",   Pins("J4 H7 B5 C1"), IOStandard("SSTL15D"), Misc("DRIVE=8")),
        Subsignal("dqs_n",   Pins("H4 G7 A5 B1"), IOStandard("SSTL15D"), Misc("DRIVE=8")),
        Subsignal("clk_p",   Pins("M2"),          IOStandard("SSTL15D"), Misc("DRIVE=8")),
        Subsignal("clk_n",   Pins("L2"),          IOStandard("SSTL15D"), Misc("DRIVE=8")),
        Subsignal("cke",     Pins("L3"),          IOStandard("SSTL15"),  Misc("DRIVE=4")),
        Subsignal("odt",     Pins("J1"),          IOStandard("SSTL15"),  Misc("DRIVE=12")),
        Subsignal("reset_n", Pins("N8"),          IOStandard("SSTL15"),  Misc("DRIVE=12")),
        Misc("PULL_MODE=NONE BANK_VCCIO=1.5"),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ["J1",
        # -------------------------------------------------------------
        "---", # 0
        #  GND  GND                                           (   1-10).
        " ---- ---- AC26 AC24 AB26 AB24 AB25 AA23 AA24 AA22",
        #                                          GND  GND   (  11-20).
        " AA25  Y23  Y25  Y22  Y26  W24  W25  V24 ---- ----",
        #                                                     (  21-30).
        "  W26  W23  V26  V23  U26  U24  U25  L24  R26  Y20",
        #                                                     (  31-40).
        "  P26  W20  P19  W19  N19  V19  M20  V22  L20  U22",
        #   5V   5V   5V   5V   5V   5V   5V   5V   5V   5V   (  41-50).
        " ---- ---- ---- ---- ---- ---- ---- ---- ---- ----",
        #   5V   5V   5V   5V   5V   5V  3V3   5V  3V3   5V   (  51-60).
        " ---- ---- ---- ---- ---- ---- ---- ---- ---- ----",
        #  GND  GND                      GND                  (  61-70).
        " ---- ----  R15  N16  L20  E17 ----  E18  M21  N17",
        #            GND                           GND  GND   (  71-80).
        "  M22  M24 ----  M25  N23  N22  N24  N21 ---- ----",
        #                                                     (  81-90).
        "  N26  L22  M26  L23  C19  K22  D19  K23  K25  K21",
        #                                                     ( 91-100).
        "  K26  J21  J25  N18  J26  M19  H26  L19  G26  K18",
        #  GND  GND                                           (101-110).
        " ---- ----  M15  J24  L15  H24  K20  J23  J20  H23",
        #                                          GND  GND   (111-120).
        "  E26  D23  D26  D24  C26  C22  B26  C23 ---- ----",
    ],
    ["J2",
        # -------------------------------------------------------------
        "---", # 0
        #  GND  GND VCCO VCCO VCCO VCCO  GND  GND             (   1-10).
        " ---- ---- ---- ---- ---- ---- ---- ----  V21  P25",
        #            GND                                      (  11-20).
        "  U21  R25 ----  T25  U20  T24  T20  T23  U19  R23",
        #                                     GND             (  21-30).
        "  T19  P24  W18  P23  V18  P21  R18 ----  T18  Y21",
        #                 GND                                 (  31-40).
        "  T17  W21  U17 ----  U14  V17  V14  V16  T15  U16",
        #                                GND  GND             (  41-50).
        "  T14  U15   Y9 AB15  AB7   W9 ---- ----  R17  J15",
        #            GND  GND                      GND  GND   (  51-60).
        "  R16  J14 ---- ----  R11 AE16  R12   U4 ---- ----",
        #                      GND  GND                       (  61-70).
        " AD14 AA11 AC14 AB11 ---- ---- AB13 AC10 AA13 AD10",
        #  GND  GND                      GND  GND             (  71-80).
        " ---- ---- AF13  Ac8 AE13  AD8 ---- ---- AF11  AE9",
        #            GND  GND                      GND  GND   (  81-90).
        " AE11  AF9 ---- ---- AD12  AE7 AC12  AF7 ---- ----",
        #                      GND  GND                       ( 91-100).
        "   W4  AB1   V4  AC1 ---- ----  AA3  AE5   Y3  AF5",
        #  GND  GND                      GND  GND             (101-110).
        " ---- ----   W3  AE3   V3  AF3 ---- ----  AA2  AE2",
        #            GND  GND                      GND  GND   (111-120).
        "   Y2  AF2 ---- ----   W1  AD1   V1  AE1 ---- ----",
    ],
    ["J3",
        # -------------------------------------------------------------
        "---", # 0
        #  GND  GND                           GND             (   1-10).
        " ---- ----  B25  A24  A25  A23  C24 ---- B24   H22",
        #                                     GND  GND        (  11-20).
        "  E25  H21  D25  F20  G24  G19  F24 ---- ----  F19",
        #                                                     (  21-30).
        "  E22  F18  H17  M17  F23  M16  E23  J16  B22  K15",
        #       GND                                           (  31-40).
        "  A22 ----  E21  F22  D21  G22  E20  G21  D20  G20",
        #  GND  GND                                           (  41-50).
        " ---- ----  D18  H19  C18  J19  C17  F25  B17  G25",
        #       GND                                           (  51-60).
        "  E16 ----  D16  H18  G17  J18  F17  K17  L17  K16",
        #            GND                                      (  61-70).
        "  L18  F15 ----  G15  H14  G16  H15  H16  C21  L14",
        #                 GND            GND            GND   (  71-80).
        "  B21  M14  B20 ----  A20  P11 ----  N12  B19 ----",
        #       TCK  GND  TDI       TDO       TMS  GND  GND   (  81-90).
        "  A19  H12 ----  H10  A17  J10  A18  H11 ---- ----",
        #                      GND  GND                       ( 91-100).
        "  F11  F13  E11  E13 ---- ----  D10  C12  C10  D12",
        #  GND  GND                      GND  GND             (101-110).
        " ---- ----   D8  C14   C8  D14 ---- ----   B9  A13",
        #            GND  GND                      GND  GND   (111-120).
        "   A9  B13 ---- ----   B7  P11   A7  N12 ---- ----",
    ],
]

# Dock IOs -----------------------------------------------------------------------------------------

# Note: SOM.J1 -> dock.J6 odd/even revert
#       SOM.J2 -> dock.J7 odd/even revert
#       SOM.J3 -> dock.J8 odd/even revert

_dock_io = [
    ("btn_n", 0,  Pins( "J3:60"), IOStandard("LVCMOS33")),
    ("btn_n", 1,  Pins( "J3:62"), IOStandard("LVCMOS33")),
    ("btn_n", 2,  Pins( "J3:64"), IOStandard("LVCMOS33")),
    ("btn_n", 3,  Pins( "J3:66"), IOStandard("LVCMOS33")),

    # FAN
    ("fan", 0,
        Subsignal("pwm", Pins("T18")),
        Subsignal("tac", Pins("T17")),
        IOStandard("LVCMOS33")
    ),

    ("led_ws2812", 0, Pins("H16"), IOStandard("LVCMOS33")),

    # LCD
    ("lcd", 0,
        Subsignal("r", Pins("H19 J19 G25 H18 J18 K17")),
        Subsignal("g", Pins("J16 K15 F22 G22 G21 G20")),
        Subsignal("b", Pins("F20 G19 F19 F18 M17 M16")),
        Subsignal("en", Pins("A24")),
        Subsignal("clk", Pins("H21")),
        IOStandard("LVCMOS33"),
        Misc("PULL_MODE=NONE DRIVE=24 BANK_VCCIO=3.3")
    ),

    # HDMI In
    ("hdmi_in", 0,
        Subsignal("clk_p",   Pins("J1:107")),
        Subsignal("clk_n",   Pins("J1:109")),
        Subsignal("data0_p", Pins("J1:87")),
        Subsignal("data0_n", Pins("J1:85")),
        Subsignal("data1_p", Pins("J1:103")),
        Subsignal("data1_n", Pins("J1:105")),
        Subsignal("data2_p", Pins("J1:93")),
        Subsignal("data2_n", Pins("J1:95")),
        Subsignal("hdp",     Pins("J1:99")),
        #Subsignal("scl",     Pins("J1:89")),
        #Subsignal("sda",     Pins("J1:91")),
        #Subsignal("cec",     Pins("J1:97")),
        IOStandard("LVCMOS33D"),
        Misc("PULL_MODE=NONE DRIVE=8")
    ),

    # HDMI Out
    ("hdmi_out", 0,
        Subsignal("clk_p",   Pins("J1:14")),
        Subsignal("clk_n",   Pins("J1:12")),
        Subsignal("data0_p", Pins("J1:6")),
        Subsignal("data0_n", Pins("J1:4")),
        Subsignal("data1_p", Pins("J1:18")),
        Subsignal("data1_n", Pins("J1:16")),
        Subsignal("data2_p", Pins("J1:10")),
        Subsignal("data2_n", Pins("J1:8")),
        Subsignal("hdp",     Pins("J2:39")),
        #Subsignal("scl",     Pins("J1:89")),
        #Subsignal("sda",     Pins("J1:91")),
        #Subsignal("cec",     Pins("J2:41")),
        IOStandard("LVCMOS33D"),
        Misc("PULL_MODE=NONE DRIVE=8")
    ),

    # RGMII Ethernet
    ("eth_clocks", 0,
        Subsignal("tx", Pins("H24")),
        Subsignal("rx", Pins("C23")),
        IOStandard("LVCMOS33")
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("E17")),
        Subsignal("mdio",    Pins("K22")),
        Subsignal("mdc",     Pins("K23")),
        Subsignal("rx_ctl",  Pins("C22")),
        Subsignal("rx_data", Pins("B26 C26 D26 E26")),
        Subsignal("tx_ctl",  Pins("J24")),
        Subsignal("tx_data", Pins("K21 J21 L19 K18")),
        IOStandard("LVCMOS33"),
    ),
    ("ephy_clk", 0, Pins("E18"), IOStandard("LVCMOS33")),
]

_dock_connectors = [
    ["sdram_connector",
        # -------------------------------------------------------------
        "---", # 0
        #                                                     ( 1-10).
        "  U16 V16  U15  V17  W21  Y21  P21  U17  P23  P24",
        #  5V  GND                                            (11-20).
        "  --- ---  T23  R23  R25  T25  W23  P25  U24  V23",
        #                                                     (21-30).
        " AC26 U25 AB25 AB26 AA25 AA24  Y26  Y25  L22  M24",
        #                                                     (31-40).
        "  W26 W25  U26  V26  W20  Y20  V19  W19  U22  V22",
    ],
]

# SDRAMs -------------------------------------------------------------------------------------------

def misterSDRAM(conn="sdram_connector"):
    return [
        ("sdram_clock", 0, Pins(f"{conn}:20"),
            IOStandard("LVCMOS33"),
            Misc("PULL_MODE=NONE DRIVE=16"),
        ),
        ("sdram", 0,
            Subsignal("a",   Pins(
                f"{conn}:37 {conn}:38 {conn}:39 {conn}:40 {conn}:28 {conn}:25 {conn}:26 {conn}:23",
                f"{conn}:24 {conn}:21 {conn}:36 {conn}:22 {conn}:19"),
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
            IOStandard("LVCMOS33"),
        ),
    ]

def sipeedSDRAM(conn="sdram_connector"):
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

    def __init__(self, dock="standard", toolchain="gowin"):
        GowinPlatform.__init__(self, "GW5AST-LV138FPG676AES", _io, _connectors, toolchain=toolchain, devicename="GW5AST-138B")
        self.add_extension(_dock_io)
        self.add_connector(_dock_connectors)

        self.toolchain.options["use_ready_as_gpio"] = 1
        self.toolchain.options["use_done_as_gpio"]  = 1
        self.toolchain.options["use_mspi_as_gpio"]  = 1
        self.toolchain.options["use_sspi_as_gpio"]  = 1
        self.toolchain.options["use_cpu_as_gpio"]   = 1
        self.toolchain.options["rw_check_on_ram"]   = 1
        self.toolchain.options["bit_security"]      = 0
        self.toolchain.options["bit_encrypt"]       = 0
        self.toolchain.options["bit_compress"]      = 0

    def create_programmer(self, kit="openfpgaloader"):
        return OpenFPGALoader(cable="ft2232")

    def do_finalize(self, fragment):
        GowinPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
