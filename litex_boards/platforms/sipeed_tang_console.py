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
    ("clk50",  0, Pins("V22"), IOStandard("LVCMOS33")),
    ("rst",    0, Pins("AA13"),  IOStandard("LVCMOS15")), #EX_KEY.0

    # Serial.
    ("serial", 0,
        Subsignal("rx", Pins("V14")),
        Subsignal("tx", Pins("U15")),
        IOStandard("LVCMOS33")
    ),

    # Leds
    ("led", 0,  Pins("G11"), IOStandard("LVCMOS33")), # Done.
    ("led", 1,  Pins("U12"), IOStandard("LVCMOS33")), # Ready.

    # SPIFlash.
    ("spiflash", 0,
        Subsignal("cs_n", Pins("T19")),
        Subsignal("clk",  Pins("L12")),
        Subsignal("miso", Pins("R22")),
        Subsignal("mosi", Pins("P22")),
        Subsignal("wp",   Pins("P21")),
        Subsignal("hold", Pins("R21")),
        IOStandard("LVCMOS33"),
    ),
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("T19")),
        Subsignal("clk",  Pins("L12")),
        Subsignal("dq",   Pins("P22 R22 P21 R21")),
        IOStandard("LVCMOS33"),
    ),

    # PCI Express
    ("pcie_clkreq_n", 0, Pins("AA14"), IOStandard("LVCMOS33")),
    ("pcie", 0,
        Subsignal("rst_n",  Pins("W11"),  IOStandard("LVCMOS15")),
        Subsignal("wake_n", Pins("T14"),  IOStandard("LVCMOS33")),
    ),

    # DDR3 SDRAM MY41J128M16JT-125
    # FIXME: Tang Mega 60k: One chip, 138k: Two chips.
    ("ddram", 0,
        Subsignal("a", Pins(
            "M1 K2 G2 J4 J2 H2 G3 J1",
            "J5 H5 L1 H3 K4 K1"),      # D1(A14) R1(A15): Unused
            IOStandard("SSTL15"),
            Misc("DRIVE=12"),
        ),
        Subsignal("ba",      Pins("P5 P2 M6"), IOStandard("SSTL15"), Misc("DRIVE=12")),
        Subsignal("ras_n",   Pins("L5"),       IOStandard("SSTL15"), Misc("DRIVE=12")),
        Subsignal("cas_n",   Pins("L4"),       IOStandard("SSTL15"), Misc("DRIVE=12")),
        Subsignal("we_n",    Pins("M5"),       IOStandard("SSTL15"), Misc("DRIVE=12")),
        Subsignal("cs_n",    Pins("P4"),       IOStandard("SSTL15"), Misc("DRIVE=12")),
        Subsignal("dm",      Pins("AA4 V7"),   IOStandard("SSTL15"), Misc("DRIVE=12")),
        Subsignal("dq",      Pins(
            " Y4 AB3 AA5 V4 AA1 AB2 AB5 AB1",
            "AA8  Y8 AB7 Y7 AB8  W9 AB6  Y9"),
            IOStandard("SSTL15"),
            Misc("DRIVE=12"),
        ),
        Subsignal("dqs_p",   Pins("Y3 V9"),    IOStandard("SSTL15D"), Misc("DRIVE=8")),
        Subsignal("dqs_n",   Pins("AA3 V8"),   IOStandard("SSTL15D"), Misc("DRIVE=8")),
        Subsignal("clk_p",   Pins("L3"),       IOStandard("SSTL15D"), Misc("DRIVE=8")),
        Subsignal("clk_n",   Pins("K3"),       IOStandard("SSTL15D"), Misc("DRIVE=8")),
        Subsignal("cke",     Pins("K6"),       IOStandard("SSTL15"),  Misc("DRIVE=4")),
        Subsignal("odt",     Pins("M2"),       IOStandard("SSTL15"),  Misc("DRIVE=12")),
        Subsignal("reset_n", Pins("L6"),       IOStandard("SSTL15"),  Misc("DRIVE=12")),
        Misc("PULL_MODE=NONE BANK_VCCIO=1.5"),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ["J0",
        # -------------------------------------------------------------
        "---", # 0
        #  GND  GND  TMS       TDO       TCK  GND  TDI        (   1-10).
        " ---- ---- ----  V19 AB26  V18 AB25 ---- AA24  U22",
        #  GND                      GND  GND                  (  11-20).
        " ----  T18  U21  R18  T21 ---- ----  R17  T20  P16",
        #  GND  GND                      GND      VCCO        (  21-30).
        " ---- ----  R19  L14  P19  L15 ----  N20 ----  M29",
        #                                                     (  31-40).
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
    ["J1",
        # -------------------------------------------------------------
        "---", # 0
        # VCCO  GND  GND                      GND             (   1-10).
        " ---- ---- ----  C20  A21  D20  B21  ---  V21  D19",
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
        "  E10  C11  F10  D11 ---- ----   C7   A6   D7   D6",
        #  GND  GND PCIe PCIe PCIe PCIe  GND  GND PCIe PCIe   (  81-90).
        " ---- ----   A6   C9   B6   D9 ---- ----   C5   A8",
        # PCIe PCIe  GND  GND PCIe PCIe PCIe PCIe  GND  GND   ( 91-100).
        "   D5   B8 ---- ----   B4   E6   A4   F6 ---- ----",
    ],
    ["J2",
        # -------------------------------------------------------------
        "---", # 0
        #  VCC                                                (   1-10).
        " ----  V22  Y22  W21  Y21  V20 Ab22  U20 AB21  M17",
        #                                                     (  11-20).
        " AA21  P17 AA20  N17 AB20  M16 AA19  M1(  W20  N15",
        #                                                     (  21-30).
        "  W11  N13 AB18  N14 AA18  Y17  Y19 AB17  Y18 AA16",
        #                                                     (  31-40).
        "  W17  M13  V17  L13  U18 AB16  U17 AA15  W16 AB15",
        #                                GND                  (  41-50).
        "  U16  Y16  T16  W15  T15  V15 ----  W14  R16  U15",
        #            GND                     PCIe  GND        (  51-60).
        "  P15  Y14 ----  V14  R14  Y13  P14 AA14 ---- AA13",
        #                      GND        NC      MODE PCIe   (  61-70).
        "  K14 AB13  K13  Y12 ---- AB12 ----  V10   U9  W11",
        # MODE      MODE  GND            GND       GND        (  71-80).
        "  U10  Y11  U11  W10   U8 AB11 ---- AA11 ---- AB10",
        #  GND       GND       GND       GND      VBUS PCIe   (  81-90).
        " ---- AA10 ----  AA9 ----  W12 ----  V13 ----  T14",
        # VBUS  ADC VBUS  ADC VBUS  ADC VBUS  ADC VBUS  GND   ( 91-100).
        " ----   N9 ----  N10 ----   M9 ----  L10 ---- ----",
    ],
]

# Dock IOs -----------------------------------------------------------------------------------------

_dock_io = [
    ("btn_n", 0,  Pins( "J3:60"), IOStandard("LVCMOS33")),
    ("btn_n", 1,  Pins( "J3:62"), IOStandard("LVCMOS33")),
    ("btn_n", 2,  Pins( "J3:64"), IOStandard("LVCMOS33")),

    # FAN
    ("fan_en", 0, Pins("J2:66"), IOStandard("LVCMOS15")), # 3.3 with 138K

    # LCD
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

    # SDCard.
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

_dock_connectors = [
    # Pmod
    ["pmod0", "J0:6  J0:4  J0:65 J0:67 J0:69 J0:71 J0:73 J0:75"],
    ["pmod1", "j2:21 j2:19 J0:68 J0:70 J0:74 J0:76 J0:78 J0:80"],

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

# SDRAMs -------------------------------------------------------------------------------------------

def misterSDRAM(conn="sdram0_connector"):
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

def sipeedSDRAM(conn="sdram0_connector"):
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
        GowinPlatform.__init__(self, "GW5AT-LV60PG484AC1/I0", _io, _connectors, toolchain=toolchain, devicename="GW5AT-60B")
        self.add_extension(_dock_io)
        self.add_connector(_dock_connectors)

        self.toolchain.options["use_ready_as_gpio"] = 1
        self.toolchain.options["use_done_as_gpio"]  = 1
        self.toolchain.options["use_mspi_as_gpio"]  = 1
        #self.toolchain.options["use_sspi_as_gpio"]  = 1
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
