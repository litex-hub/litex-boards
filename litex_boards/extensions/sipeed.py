#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022-2023 Icenowy Zheng <uwu@icenowy.me>
# Copyright (c) 2022-2026 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2023-2025 Gwenhael Goavec-Merou <gwenhael.goavec-merou@trabucayre.com>
# SPDX-License-Identifier: BSD-2-Clause

"""Sipeed SoMs board-to-board connectors and docks.

Docks are Extensions written with the SoM connector names (CARD1, J0/J1/J2...), plugged by the
platforms (Platform(dock=...)) or manually on a SoM-only platform:

    platform = sipeed_tang_mega_138k.Platform(dock=None)
    platform.add_extension(TangMegaNeoDock(som="138k"))
"""

from litex.build.generic_platform import *
from litex.build.extension import Extension

# Sipeed Dock --------------------------------------------------------------------------------------

class SipeedDock(Extension):
    """Dock described by static IO/connector lists, written with the SoM connector names."""
    io         = []
    connectors = []

    def define_io(self, platform):
        return self.io

    def define_connectors(self, platform):
        return self.connectors

# Tang Primer 20K Docks ----------------------------------------------------------------------------

_tang_primer_20k_dock_io = [
    # Leds
    ("led", 0,  Pins( "CARD1:44"), IOStandard("LVCMOS33")),
    ("led", 1,  Pins( "CARD1:46"), IOStandard("LVCMOS33")),
    ("led", 3,  Pins( "CARD1:40"), IOStandard("LVCMOS33")),
    ("led", 2,  Pins( "CARD1:42"), IOStandard("LVCMOS33")),
    ("led", 4,  Pins( "CARD1:98"), IOStandard("LVCMOS33")),
    ("led", 5,  Pins("CARD1:136"), IOStandard("LVCMOS33")),

    # RGB Led.
    ("rgb_led", 0, Pins("CARD1:45"), IOStandard("LVCMOS33")),

    # Buttons.
    ("btn_n", 0,  Pins( "CARD1:15"), IOStandard("LVCMOS33")),
    ("btn_n", 1,  Pins("CARD1:165"), IOStandard("LVCMOS15")),
    ("btn_n", 2,  Pins("CARD1:163"), IOStandard("LVCMOS15")),
    ("btn_n", 3,  Pins("CARD1:159"), IOStandard("LVCMOS15")),
    ("btn_n", 4,  Pins("CARD1:157"), IOStandard("LVCMOS15")),

    # HDMI.
    ("hdmi", 0,
        Subsignal("clk_p",   Pins("CARD1:68"), IOStandard("LVCMOS33")),
        Subsignal("clk_n",   Pins("CARD1:70"), IOStandard("LVCMOS33")),
        Subsignal("data0_p", Pins("CARD1:64"), IOStandard("LVCMOS33")),
        Subsignal("data0_n", Pins("CARD1:62"), IOStandard("LVCMOS33")),
        Subsignal("data1_p", Pins("CARD1:58"), IOStandard("LVCMOS33")),
        Subsignal("data1_n", Pins("CARD1:56"), IOStandard("LVCMOS33")),
        Subsignal("data2_p", Pins("CARD1:52"), IOStandard("LVCMOS33")),
        Subsignal("data2_n", Pins("CARD1:50"), IOStandard("LVCMOS33")),
        Subsignal("hdp", Pins("CARD1:154"), IOStandard("LVCMOS33")),
        Subsignal("cec", Pins("CARD1:152"), IOStandard("LVCMOS33")),
        #Subsignal("sda", Pins("CARD1:95")), # Conflict with eth mdc
        #Subsignal("scl", Pins("CARD1:97")), # Conflict with eth mdio
        Misc("PULL_MODE=NONE"),
    ),

    # LCD.
    ("lcd", 0,
        # Control.
        Subsignal("rst",   Pins("CARD1:123")),
        Subsignal("bl",    Pins("CARD1:186")),
        #Subsignal("sda",   Pins("CARD1: 95")), # Conflict with eth mdc
        #Subsignal("scl",   Pins("CARD1: 97")), # Conflict with eth mdio
        Subsignal("int",   Pins("CARD1:125")),

        # Video.
        Subsignal("clk",   Pins("CARD1:183")),
        Subsignal("de",    Pins("CARD1:101")),
        Subsignal("hsync", Pins("CARD1:107")),
        Subsignal("vsync", Pins("CARD1:103")),
        Subsignal("r",     Pins("CARD1:193 CARD1:191 CARD1:181 CARD1:177 CARD1:175")),
        Subsignal("g",     Pins("CARD1:180 CARD1:131 CARD1:129 CARD1:194 CARD1:192 CARD1:182")),
        Subsignal("b",     Pins("CARD1:121 CARD1:119 CARD1:115 CARD1:113 CARD1:109")),
        IOStandard("LVCMOS33")
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

_tang_primer_20k_dock_lite_io = [
    # Buttons.
    ("btn_n",   0, Pins("CARD1:15"),  IOStandard("LVCMOS33")),
    ("btn_n",   1, Pins("CARD1:163"), IOStandard("LVCMOS15")),

    # Switches
    ("user_sw", 0, Pins("CARD1:159"), IOStandard("LVCMOS15")),
    ("user_sw", 1, Pins("CARD1:157"), IOStandard("LVCMOS15")),
]

_tang_primer_20k_dock_lite_connectors = [
    # Pmod
    ("j2", "F15 D16 C9  L12 E15 E14 A9  J11"),
    ("j6", "L8  P7  E10 D11 M6  R7  D10 F10"),
    ("j7", "T6  T7  T8  T9  P6  R8  P8  P9"),
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

class TangPrimer20KDock(SipeedDock):
    """Tang Primer 20K Dock (on the SoM's 204-pin SODIMM connector)."""
    slots = {"CARD1": "CARD1"}
    io    = _tang_primer_20k_dock_io

class TangPrimer20KDockLite(SipeedDock):
    """Tang Primer 20K Lite Dock (on the SoM's 204-pin SODIMM connector)."""
    slots      = {"CARD1": "CARD1"}
    io         = _tang_primer_20k_dock_lite_io
    connectors = _tang_primer_20k_dock_lite_connectors

# Tang Primer 25K Dock -----------------------------------------------------------------------------

_tang_primer_25k_dock_io = [
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

_tang_primer_25k_dock_connectors = [
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

class TangPrimer25KDock(SipeedDock):
    """Tang Primer 25K Dock (on the SoM's J1/J2 connectors)."""
    slots      = {"J1": "J1", "J2": "J2"}
    io         = _tang_primer_25k_dock_io
    connectors = _tang_primer_25k_dock_connectors

# Tang Mega 138K/60K SoMs --------------------------------------------------------------------------

tang_mega_som_connectors = [
    ["J0", # BTB9900
        # -------------------------------------------------------------
        "---", # 0
        #  GND  GND  TMS       TDO       TCK  GND  TDI  PUDC  (   1-10).
        " ---- ---- ----  V19 ----  V18 ---- ---- ----  U22",
        #  GND                      GND  GND                  (  11-20).
        " ----  T18  U21  R18  T21 ---- ----  R17  T20  P16",
        #  GND  GND                      GND      VCCO        (  21-30).
        " ---- ----  R19  L14  P19  L15 ----  N20 ----  M20",
        #                      GND            GND             (  31-40).
        "  N22  L16  M22  K16 ----  P20  M21 ----  L21  N18",
        #                                                     (  41-50).
        "  L19  N19  L20  M18  K21  L18  K22  K18  J22  K19",
        #                                               GND   (  51-60).
        "  H22  H17  J20  H18  J21  J19  G17  H19  G18 ----",
        # RCFG       GND            GND                       (  61-70).
        "  N12  H20 ----  G20  G21 ----  G22  F19  F18  F20",
        #                               DONE       RDY        (  71-80).
        "  E18  F21  C22  E22  B22  D22  G11  E21  U12  D21",
    ],
    ["J1", # C2399
        # -------------------------------------------------------------
        "---", # 0
        # VCCO  GND  GND                      GND  GND        (   1-10).
        " ---- ---- ----  C20  A21  D20  B21  ---  ---  D19",
        #                 GND  GND                      GND   (  11-20).
        "  A20  E19  B20 ---- ----  C19  A19  C18  A18 ----",
        #  GND                      GND  GND                  (  21-30).
        " ----  E17  B18  F16  B17 ---- ----  D16  C17  E16",
        #       GND  GND                      GND  GND        (  31-40).
        "  D17 ---- ----  D15  A16  D14  A15 ---- ----  F15",
        #                      GND  GND                       (  41-50).
        "  B16  F14  B15  F13 ---- ----  A14  J16  A13  J17",
        #  GND                           GND       GND  GND   (  51-60).
        " ----  K17  B13  H15  C13  J15 ----  H14  C15  J14",
        #            GND                           GND  GND   (  61-70).
        "  C14 G16  ----  G15  E14  G13  E13  H13 ---- ----",
        # PCIe PCIe PCIe PCIe  GND  GND PCIe PCIe PCIe PCIe   (  71-80).
        "  E10  C11  F10  D11 ---- ----   C7  A10   D7  B10",
        #  GND  GND PCIe PCIe PCIe PCIe  GND  GND PCIe PCIe   (  81-90).
        " ---- ----   A6   C9   B6   D9 ---- ----   C5   A8",
        # PCIe PCIe  GND  GND PCIe PCIe PCIe PCIe  GND  GND   ( 91-100).
        "   D5   B8 ---- ----   A4   E6   B4   F6 ---- ----",
    ],
    ["J2", # C2400
        # -------------------------------------------------------------
        "---", # 0
        #  VCC                                                (   1-10).
        " ----  W22  Y22  W21  Y21  V20 AB22  U20 AB21  M17",
        #                                                     (  11-20).
        " AA21  P17 AA20  N17 AB20  M16 AA19  M15  W20  N15",
        #                                                     (  21-30).
        "  W19  N13 AB18  N14 AA18  Y17  Y19 AB17  Y18 AA16",
        #                                                     (  31-40).
        "  W17  M13  V17  L13  U18 AB16  U17 AA15  W16 AB15",
        #                                GND                  (  41-50).
        "  U16  Y16  T16  W15  T15  V15 ----  W14  R16  U15",
        #            GND                           GND        (  51-60).
        "  P15  Y14 ----  V14  R14  Y13  P14 AA14 ---- AA13",
        #                      GND       VIO      MODE        (  61-70).
        "  K14 AB13  K13  Y12 ---- AB12 ----  V10   U9  W11",
        # MODE      MODE      CFG        GND       GND        (  71-80).
        "  U10  Y11  U11  W10   U8 AB11 ---- AA11 ---- AB10",
        #  GND       GND       GND       GND      VBUS        (  81-90).
        " ---- AA10 ----  AA9 ----  W12 ----  V13 ----  T14",
        # VBUS  ADC VBUS  ADC VBUS  ADC VBUS  ADC VBUS  GND   ( 91-100).
        " ----   N9 ----  N10 ----   M9 ----  L10 ---- ----",
    ],
]

# The 60K and 138K SoMs share the same connectors pinout (on the 60K, SerDes lanes 1/3 are swapped
# inside the FPGA but the connectors' nets/balls are the same).
tang_mega_60k_som_connectors  = tang_mega_som_connectors
tang_mega_138k_som_connectors = tang_mega_som_connectors

# Tang Mega Docks (common) -------------------------------------------------------------------------

# Peripherals wired identically on the Tang Mega Neo Dock and on the Tang Console (and described
# identically for the 60K and 138K SoMs).

_tang_mega_dock_fan_io = [
    ("fan_en", 0, Pins("J2:66"), IOStandard("LVCMOS15")), # 3.3 with 138K
]

_tang_mega_dock_lcd_io = [
    ("lcd", 0,
        Subsignal("r",     Pins("J0:55 J0:53 J0:59 J0:57 J0:51 J0:49 J0:47 J0:45")),
        Subsignal("g",     Pins("J0:43 J0:24 J0:48 J0:39 J0:37 J0:33 J0:31 J0:50")),
        Subsignal("b",     Pins("J2:75 J0:46 J0:44 J0:42 J0:40 J0:34 J0:32 J0:30")),
        Subsignal("hsync", Pins("J0:28")),
        Subsignal("vsync", Pins("J0:26")),
        Subsignal("bl",    Pins("J0:36")),
        Subsignal("en",    Pins("J0:10")),
        Subsignal("clk",   Pins("J0:41")),
        IOStandard("LVCMOS33"),
        Misc("PULL_MODE=NONE DRIVE=24 BANK_VCCIO=3.3")
    ),
]

_tang_mega_dock_sdcard_io = [
    ("spisdcard", 0,
        Subsignal("clk",  Pins("J2:46")),
        Subsignal("mosi", Pins("J2:42")),
        Subsignal("cs_n", Pins("J2:44")),
        Subsignal("miso", Pins("J2:38")),
        IOStandard("LVCMOS33"),
        Misc("BANK_VCCIO=3.3"),
    ),
    ("sdcard", 0,
        Subsignal("data", Pins("J2:38 J2:40 J2:48 J2:44"), IOStandard("LVCMOS33"), Misc("BANK_VCCIO=3.3")),
        Subsignal("cmd",  Pins("J2:42"),                   IOStandard("LVCMOS33"), Misc("BANK_VCCIO=3.3")),
        Subsignal("clk",  Pins("J2:46"),                   IOStandard("LVCMOS33"), Misc("BANK_VCCIO=3.3")),
        Subsignal("cd",   Pins("J2:56"),                   IOStandard("LVCMOS15"), Misc("BANK_VCCIO=1.5")),
    ),
]

_tang_mega_dock_sdram1_connector = [
    ["sdram1_connector",
        # -------------------------------------------------------------
        "---", # 0
        #                                                                ( 1-10).
        "  J0:23 J0:25 J0:13 J0:15 J0:18 J0:20 J0:12 J0:14 J2:31 J2:33",
        #   5V    GND                                                    (11-20).
        "  ----- -----  J2:2  J2:4 J2:12 J2:14 J2:24 J2:22  J2:6  J2:8",
        #                                                                (21-30).
        "   J2:3  J2:5  J2:7  J2:9 J2:11 J2:13 J2:15 J2:17 J2:25 J2:23",
        #                                                                (31-40).
        "  J2:27 J2:29 J0:19 J2:20 J2:35 J2:37 J2:49 J2:51 J2:55 J2:57",
    ],
]

# Tang Mega Neo Dock -------------------------------------------------------------------------------

_tang_mega_neo_dock_hdmi_io = [
    ("hdmi", 0,
        Subsignal("clk_p",   Pins("J1:64"), IOStandard("LVCMOS33D")),
        Subsignal("clk_n",   Pins("J1:62"), IOStandard("LVCMOS33D")),
        Subsignal("data0_p", Pins("J1:60"), IOStandard("LVCMOS33D")),
        Subsignal("data0_n", Pins("J1:58"), IOStandard("LVCMOS33D")),
        Subsignal("data1_p", Pins("J1:56"), IOStandard("LVCMOS33D")),
        Subsignal("data1_n", Pins("J1:54"), IOStandard("LVCMOS33D")),
        Subsignal("data2_p", Pins("J1:52"), IOStandard("LVCMOS33D")),
        Subsignal("data2_n", Pins("J1:50"), IOStandard("LVCMOS33D")),
        Subsignal("hdp",     Pins("J2:63"), IOStandard("LVCMOS33")),
        #Subsignal("dir",     Pins("J2:61"), IOStandard("LVCMOS33")),
        #Subsignal("scl",     Pins("J2:32")),
        #Subsignal("sda",     Pins("J2:34")),
        Misc("PULL_MODE=NONE DRIVE=8")
    ),
]

# Same HDMI connector, description used by the 60K target.
_tang_mega_neo_dock_hdmi_out_io = [
    ("hdmi_out", 0,
        Subsignal("clk_p", Pins("J1:64")),
        Subsignal("clk_n", Pins("J1:62")),
        Subsignal("data0_p", Pins("J1:60")),
        Subsignal("data0_n", Pins("J1:58")),
        Subsignal("data1_p", Pins("J1:56")),
        Subsignal("data1_n", Pins("J1:54")),
        Subsignal("data2_p", Pins("J1:52")),
        Subsignal("data2_n", Pins("J1:50")),
        IOStandard("LVCMOS33D"),
        Misc("PULL_MODE=NONE DRIVE=3.5")
    ),
]

_tang_mega_neo_dock_ws2812_io = [
    ("ws2812", 0, Pins("J1:48"), IOStandard("LVCMOS33"), Misc("DRIVE=8")),
]

_tang_mega_neo_dock_ch569_io = [
    ("ch569", 0,
        Subsignal("htclk", Pins("J0:53")),
        Subsignal("htreq", Pins("J0:55")),
        Subsignal("htrdy", Pins("J0:41"), Misc("PULL_MODE=DOWN DRIVE=OFF BANK_VCCIO=3.3")),
        Subsignal("htvld", Pins("J0:59")),
        Subsignal("hd",    Pins(
            "J0:57 J0:51 J0:24 J0:47 J0:45 J0:48 J0:39 J0:37 "
            "J0:33 J0:31 J0:46 J0:44 J0:42 J0:40 J0:34 J0:32"
        )),
        IOStandard("LVCMOS33"), Misc("PULL_MODE=NONE DRIVE=8 BANK_VCCIO=3.3")
    ),
]

# 138K SoM specific IOs.
_tang_mega_neo_dock_138k_io = [
    ("usr_clk_in", 0, Pins("J2:88"), IOStandard("LVCMOS33")),

    ("btn_n", 0,  Pins("J2:60"), IOStandard("LVCMOS33"), Misc("PULL_MODE=UP DRIVE=OFF BANK_VCCIO=3.3")),
    ("btn_n", 1,  Pins("J2:62"), IOStandard("LVCMOS33"), Misc("PULL_MODE=UP DRIVE=OFF BANK_VCCIO=3.3")),
    ("btn_n", 2,  Pins("J2:64"), IOStandard("LVCMOS33"), Misc("PULL_MODE=UP DRIVE=OFF BANK_VCCIO=3.3")),

    *_tang_mega_dock_sdcard_io,

    # RGMII Ethernet (RTL8211F).
    ("eth_ref_clk", 0, Pins("J0:4"), IOStandard("LVCMOS33")),
    ("eth_clocks", 0,
        Subsignal("tx", Pins("J0:70")),
        Subsignal("rx", Pins("J0:65")),
        IOStandard("LVCMOS33"),
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("J2:19"), Misc("PULL_MODE=NONE BANK_VCCIO=3.3")),
        Subsignal("mdio",    Pins("J0:6"),  Misc("PULL_MODE=UP")),
        Subsignal("mdc",     Pins("J0:10"), Misc("PULL_MODE=NONE")),
        Subsignal("rx_ctl",  Pins("J0:67")),
        Subsignal("rx_data", Pins("J0:69 J0:71 J0:73 J0:75"), Misc("PULL_MODE=NONE BANK_VCCIO=3.3")),
        Subsignal("tx_ctl",  Pins("J0:72"), Misc("PULL_MODE=NONE BANK_VCCIO=3.3")),
        Subsignal("tx_data", Pins("J0:80 J0:78 J0:76 J0:74"), Misc("PULL_MODE=NONE BANK_VCCIO=3.3")),
        IOStandard("LVCMOS33"),
    ),
]

# 60K SoM specific IOs.
_tang_mega_neo_dock_60k_io = [
    ("sys_rst_n", 0, Pins("J2:60"), IOStandard("LVCMOS15"), Misc("PULL_MODE=UP")),

    # OV5640 Camera
    ("cmos", 0,
        Subsignal("pwdn", Pins("J2:7"), Misc("DRIVE=8")),
        Subsignal("rst_n", Pins("J2:3"), Misc("DRIVE=8")),
        Subsignal("xclk", Pins("J2:11"), Misc("DRIVE=4")),
        Subsignal("sda", Pins("J2:56"), IOStandard("LVCMOS15"), Misc("PULL_MODE=UP DRIVE=8")),
        Subsignal("scl", Pins("J2:58"), IOStandard("LVCMOS33"), Misc("PULL_MODE=UP DRIVE=8")),
        Subsignal("data", Pins("J2:57 J2:51 J2:49 J2:55 J2:20 J0:19 J2:17 J2:13")),
        Subsignal("pclk", Pins("J2:15")),
        Subsignal("href", Pins("J2:9")),
        Subsignal("vsync", Pins("J2:5")),
        IOStandard("LVCMOS33"),
        Misc("PULL_MODE=NONE")
    ),

    # Ethernet RGMII (TX only).
    ("eth", 0,
        Subsignal("tx_data", Pins("J0:80 J0:78 J0:76 J0:74")),
        Subsignal("tx_en", Pins("J0:72")),
        Subsignal("gtxclk", Pins("J0:70")),
        Subsignal("phy_clk", Pins("J0:4")),
        Subsignal("rst_n", Pins("J2:19")),
        IOStandard("LVCMOS33"),
        Misc("PULL_MODE=NONE")
    ),

    # SD Card (SPI mode).
    ("sdcard", 0,
        Subsignal("clk", Pins("J2:46"), Misc("DRIVE=8")),
        Subsignal("cs", Pins("J2:44"), Misc("DRIVE=8")),
        Subsignal("mosi", Pins("J2:42"), Misc("DRIVE=8")),
        Subsignal("miso", Pins("J2:38"), Misc("DRIVE=OFF")),
        IOStandard("LVCMOS33"),
        Misc("PULL_MODE=NONE")
    ),

    # Audio
    ("audio", 0,
        Subsignal("bck", Pins("J2:26")),
        Subsignal("ws", Pins("J2:28")),
        Subsignal("din", Pins("J2:30")),
        Subsignal("pa_en", Pins("J2:36")),
        IOStandard("LVCMOS33"),
        Misc("PULL_MODE=NONE")
    ),

    # Buttons
    ("btn", 0, Pins("J2:64"), IOStandard("LVCMOS15"), Misc("PULL_MODE=UP")),
    ("btn", 1, Pins("J2:62"), IOStandard("LVCMOS15"), Misc("PULL_MODE=UP")),

    # LEDs
    ("led", 0, Pins("J0:12"), IOStandard("LVCMOS33")),
    ("led", 1, Pins("J0:14"), IOStandard("LVCMOS33")),
    ("led", 2, Pins("J0:18"), IOStandard("LVCMOS33")),
    ("led", 3, Pins("J0:20"), IOStandard("LVCMOS33")),
    ("led", 4, Pins("J0:13"), IOStandard("LVCMOS33")),
    ("led", 5, Pins("J0:15"), IOStandard("LVCMOS33")),
    ("led", 6, Pins("J0:23"), IOStandard("LVCMOS33")),
    ("led", 7, Pins("J0:25"), IOStandard("LVCMOS33")),

    # SDRAM: plug the module on sdram0_connector (extensions/sdram_modules.py: SipeedSDRAM, MiSTerSDRAM).
]

_tang_mega_neo_dock_connectors = [
    # Pmod
    # Note PMOD0 is shared with SDRAM1_Dx
    ["pmod0", "J0:25 J0:15 J0:20 J0:14 J0:23 J0:13 J0:18 J0:12"],
    # Note PMOD1 is shared with SDRAM1_Ax and CAM0
    ["pmod1", " J2:5  J2:9 J2:13 J2:17  J2:3  J2:7 J2:11 J2:15"],

    # J13
    ["sdram0_connector",
        # -------------------------------------------------------------
        "---", # 0
        #                                                                ( 1-10).
        "  J1:65 J1:67 J1:59 J1:61 J1:53 J1:55 J1:47 J1:49 J1:41 J1:43",
        #   5V    GND                                                    (11-20).
        "  ----- ----- J1:35 J1:37 J1:11 J1:13  J1:5  J1:7 J1:23 J1:25",
        #                                                                (21-30).
        "  J1:29 J1:31 J1:17 J1:19 J1:34 J1:36 J1:28 J1:30 J1:42 J1:44",
        #                                                                (31-40).
        "  J1:22 J1:24 J0:68 J1:40  J1:4  J1:6 J1:10 J1:12 J1:16 J1:18",
    ],

    # J14
    *_tang_mega_dock_sdram1_connector,
]

class TangMegaNeoDock(SipeedDock):
    """Tang Mega Neo Dock (on the Tang Mega 138K/60K SoMs' J0/J1/J2 connectors).

    The SoMs' IO banks voltages differ, so some peripherals are described per SoM (som="138k" or
    "60k"); the others (LCD, HDMI, fan, CH569, WS2812, Pmods/SDRAM connectors) are common.
    """
    slots      = {"J0": "J0", "J1": "J1", "J2": "J2"}
    connectors = _tang_mega_neo_dock_connectors

    def __init__(self, *args, som="138k", **kwargs):
        if som not in ["138k", "60k"]:
            raise ValueError(f"Unsupported SoM {som}, supported: 138k, 60k.")
        self.som = som
        SipeedDock.__init__(self, *args, **kwargs)

    def define_io(self, platform):
        return [
            *{"138k": _tang_mega_neo_dock_138k_io, "60k": _tang_mega_neo_dock_60k_io}[self.som],
            *_tang_mega_dock_fan_io,
            *_tang_mega_dock_lcd_io,
            *_tang_mega_neo_dock_hdmi_io,
            *_tang_mega_neo_dock_hdmi_out_io,
            *_tang_mega_neo_dock_ws2812_io,
            *_tang_mega_neo_dock_ch569_io,
        ]

# Tang Console Dock --------------------------------------------------------------------------------

_tang_console_dock_io = [
    # J2:60 (EX_KEY.0) is used as rst.
    ("btn_n", 0,  Pins( "J2:62"), IOStandard("LVCMOS33")),
    ("btn_n", 1,  Pins( "J2:64"), IOStandard("LVCMOS33")),

    *_tang_mega_dock_fan_io,
    *_tang_mega_dock_lcd_io,

    # HDMI.
    ("hdmi", 0,
        Subsignal("clk_p",   Pins("J1:64"), IOStandard("LVCMOS33D")),
        Subsignal("clk_n",   Pins("J1:62"), IOStandard("LVCMOS33D")),
        Subsignal("data0_p", Pins("J1:60"), IOStandard("LVCMOS33D")),
        Subsignal("data0_n", Pins("J1:58"), IOStandard("LVCMOS33D")),
        Subsignal("data1_p", Pins("J1:56"), IOStandard("LVCMOS33D")),
        Subsignal("data1_n", Pins("J1:54"), IOStandard("LVCMOS33D")),
        Subsignal("data2_p", Pins("J1:52"), IOStandard("LVCMOS33D")),
        Subsignal("data2_n", Pins("J1:50"), IOStandard("LVCMOS33D")),
        Subsignal("hdp",     Pins("J2:63"), IOStandard("LVCMOS33")),
        Subsignal("pwr_sav", Pins("J2:61"), IOStandard("LVCMOS33")),
        #Subsignal("scl",     Pins("J2:32")),
        #Subsignal("sda",     Pins("J2:34")),
        #Subsignal("cec",     Pins("J2:41")),
        Misc("PULL_MODE=NONE DRIVE=8")
    ),

    *_tang_mega_dock_sdcard_io,
]

_tang_console_dock_connectors = [
    # Pmod
    ["pmod0", "J0:6  J0:4  J0:65 J0:67 J0:69 J0:71 J0:73 J0:75"],
    ["pmod1", "J2:21 J2:19 J0:68 J0:70 J0:74 J0:76 J0:78 J0:80"],

    # J9
    ["sdram0_connector",
        # -------------------------------------------------------------
        "---", # 0
        #                                                                ( 1-10).
        "  J1:65 J1:67 J1:59 J1:61 J1:53 J1:55 J1:47 J1:49 J1:41 J1:43",
        #   5V    GND                                                    (11-20).
        "  ----- ----- J1:35 J1:37 J1:11 J1:13  J1:5  J1:7 J1:23 J1:25",
        #                                                                (21-30).
        "  J1:29 J1:31 J1:17 J1:19 J1:34 J1:36 J1:28 J1:30 J1:42 J1:44",
        #                                                                (31-40).
        "  J1:22 J1:24 J0:72 J1:40  J1:4  J1:6 J1:10 J1:12 J1:16 J1:18",
    ],

    # J10
    *_tang_mega_dock_sdram1_connector,
]

class TangConsoleDock(SipeedDock):
    """Tang Console dock (on the Tang Mega 60K/138K SoMs' J0/J1/J2 connectors)."""
    slots      = {"J0": "J0", "J1": "J1", "J2": "J2"}
    io         = _tang_console_dock_io
    connectors = _tang_console_dock_connectors

# Tang Mega 138K Pro Dock --------------------------------------------------------------------------

# Note: SOM.J1 -> dock.J6 odd/even revert
#       SOM.J2 -> dock.J7 odd/even revert
#       SOM.J3 -> dock.J8 odd/even revert

_tang_mega_138k_pro_dock_io = [
    # SFP-0/1 (SerDes Q1, lanes 0/1; reference clock: Q1 REFCLK1).
    ("sfp", 0,
        Subsignal("tx_disable", Pins("R18")),
        Subsignal("los",        Pins("V18")),
        IOStandard("LVCMOS33")
    ),
    ("sfp", 1,
        Subsignal("tx_disable", Pins("M20")),
        Subsignal("los",        Pins("W18")),
        IOStandard("LVCMOS33")
    ),

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

_tang_mega_138k_pro_dock_connectors = [
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

class TangMega138KProDock(SipeedDock):
    """Tang Mega 138K Pro Dock (on the SoM's J1/J2/J3 connectors)."""
    slots      = {"J1": "J1", "J2": "J2", "J3": "J3"}
    io         = _tang_mega_138k_pro_dock_io
    connectors = _tang_mega_138k_pro_dock_connectors
