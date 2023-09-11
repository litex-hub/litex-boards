#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Franck Jullien <franck.jullien@collshade.fr>
# Copyright (c) 2022 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.efinix.platform import EfinixPlatform
from litex.build.efinix import EfinixProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk
    ("clk25",    0, Pins("B2"),  IOStandard("1.8_V_LVCMOS")),
    ("clk33",    0, Pins("P2"),  IOStandard("1.8_V_LVCMOS")),
    ("clk74_25", 0, Pins("A11"), IOStandard("1.8_V_LVCMOS")),

    # SD-Card
    ("spisdcard", 0,
        Subsignal("clk",  Pins("B12")),
        Subsignal("mosi", Pins("C12"), Misc("WEAK_PULLUP")),
        Subsignal("cs_n", Pins("A12"), Misc("WEAK_PULLUP")),
        Subsignal("miso", Pins("B14"), Misc("WEAK_PULLUP")),
        IOStandard("1.8_V_LVCMOS"),
    ),
    ("sdcard", 0,
        Subsignal("data", Pins("B14 A14 D12 A12"), Misc("WEAK_PULLUP")),
        Subsignal("cmd",  Pins("C12"), Misc("WEAK_PULLUP")),
        Subsignal("clk",  Pins("B12")),
        IOStandard("3.3_V_LVCMOS"),
    ),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("R4")),
        Subsignal("rx", Pins("R3")),
        IOStandard("3.3_V_LVCMOS"), Misc("WEAK_PULLUP")
    ),

    # Leds
    ("user_led", 0,
        Subsignal("r", Pins("J15")),
        Subsignal("g", Pins("H10")),
        Subsignal("b", Pins("K14")),
        IOStandard("1.8_V_LVCMOS"),
    ),
    ("user_led", 1,
        Subsignal("r", Pins("H15")),
        Subsignal("g", Pins("H11")),
        Subsignal("b", Pins("J14")),
        IOStandard("1.8_V_LVCMOS"),
    ),

    # Buttons
    ("user_btn", 0, Pins("K13"), IOStandard("1.8_V_LVCMOS")),
    ("user_btn", 1, Pins("J13"), IOStandard("1.8_V_LVCMOS")),
    ("user_btn", 2, Pins("C5"),  IOStandard("1.8_V_LVCMOS")),
    ("user_btn", 3, Pins("R13"), IOStandard("1.8_V_LVCMOS")),

    # Switches
    ("user_sw", 0, Pins("F3"), IOStandard("1.8_V_LVCMOS")),
    ("user_sw", 1, Pins("E3"), IOStandard("1.8_V_LVCMOS")),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("P1")),
        Subsignal("clk",  Pins("N1")),
        Subsignal("mosi", Pins("M1")),
        Subsignal("miso", Pins("L1")),
        IOStandard("1.8_V_LVCMOS")
    ),

    # HyperRAM (X16)
    ("hyperram", 0,
        Subsignal("dq",  Pins(
            "B6 C6 A5 A6  F7  F8  E7  D7",
            "B9 A9 F9 E9 C10 D10 A10 B10"
        ), IOStandard("1.8_V_LVCMOS")),
        Subsignal("rwds",  Pins("B8 C8"), IOStandard("1.8_V_LVCMOS")),
        Subsignal("cs_n",  Pins("A8"),    IOStandard("1.8_V_LVCMOS")),
        Subsignal("rst_n", Pins("D5"),    IOStandard("1.8_V_LVCMOS")),
        Subsignal("clk",   Pins("B7"),    IOStandard("1.8_V_LVCMOS")),
        Misc("SLEWRATE=FAST")
    ),

    # MIPI
    ("mipi_tx", 0,
        Subsignal("clk",   Pins("D13"), IOStandard("1.8_V_LVCMOS")),
        Subsignal("data0", Pins("C15"), IOStandard("1.8_V_LVCMOS")),
        Subsignal("data1", Pins("D14"), IOStandard("1.8_V_LVCMOS")),
        Subsignal("data2", Pins("E14"), IOStandard("1.8_V_LVCMOS")),
        Subsignal("data3", Pins("E12"), IOStandard("1.8_V_LVCMOS")),
        Misc("SLEWRATE=FAST")
    ),

    # MIPI
    ("mipi_rx", 0,
        Subsignal("clk",   Pins("M15"), IOStandard("1.8_V_LVCMOS")),
        Subsignal("data0", Pins("K11"), IOStandard("1.8_V_LVCMOS")),
        Subsignal("data1", Pins("L13"), IOStandard("1.8_V_LVCMOS")),
        Misc("SLEWRATE=FAST")
    ),

    ("cam_i2c", 0,
        Subsignal("sda",   Pins("H4"), Misc("WEAK_PULLUP")),
        Subsignal("scl",   Pins("H5"), Misc("WEAK_PULLUP")),
        Subsignal("reset", Pins("R14")),
        IOStandard("1.8_V_LVCMOS")
    ),
]

iobank_info = [
            ("1A", "1.8 V LVCMOS"),
            ("1B", "1.8 V LVCMOS"),
            ("2A", "1.8 V LVCMOS"),
            ("2B", "1.8 V LVCMOS"),
            ("3A", "1.8 V LVCMOS"),
            ("3B", "1.8 V LVCMOS"),
            ("4A", "1.8 V LVCMOS"),
            ("4B", "1.8 V LVCMOS"),
            ("BL", "3.3 V LVCMOS"),
            ("BR", "1.8 V LVCMOS"),
            ("TL", "1.8 V LVCMOS"),
            ("TR", "3.3 V LVCMOS"),
]

# QSE Connectors -----------------------------------------------------------------------------------

_connectors = [
    ["P1",
        "---", # 0
        #3V3      5V     GND GND                 GND GND                 GND GND         ↓
        "--- H14 --- G14 --- --- F12 G13 E12 F13 --- --- E15 H13 E14 H12 --- --- C13 G15",
        #  1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17  18  19  20 ↑
        # 21  22  23  24  25  26  27  28  28  30  31  32  33  34  35  36  37  38  39  40 ↓
        "D13 F15 --- --- D15 G11 D14 F11 --- --- C14 N14 C15 P14 --- ---  K4  A4  J3  B5",
        #        GND GND                 GND GND                 GND GND                 ↑
    ],
    ["P2",
        "---", # 0
        #3V3      5V     GND GND                 GND GND                 GND GND         ↓
        "---  R9 ---  P9 --- --- L11 N10 K11 M10 --- --- L12 R10 L13 P10 --- --- M14 R12",
        #  1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17  18  19  20 ↑
        # 21  22  23  24  25  26  27  28  28  30  31  32  33  34  35  36  37  38  39  40 ↓
        "M15 R11 --- --- K10 P11 J10 P12 --- --- K12 N13 J12 P15 --- ---  H5  H4 P13 R14",
        #        GND GND                 GND GND                 GND GND                 ↑
    ],
    ["P3",
        "---", # 0
        #3V3      5V     GND GND                 GND GND                 GND GND         ↓
        "---  R5 ---  P5 --- ---  M7  R6  L7  P6 --- ---  R8  N6  P8  M6 --- ---  K7  R7",
        #  1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17  18  19  20 ↑
        # 21  22  23  24  25  26  27  28  28  30  31  32  33  34  35  36  37  38  39  40 ↓
        " L8  P7 --- ---  N8  L6  M8  K6 --- ---  M9  A3  L9  B3 --- --- E10  C3 F10  C4",
        #        GND GND                 GND GND                 GND GND                 ↑
    ],
]

# QSE Extensions -----------------------------------------------------------------------------------

def rgmii_ethernet_qse_ios(con, n=""):
    return [
        (f"eth{n}_clocks", 0,
            Subsignal("tx", Pins(f"{con}:26")),
            Subsignal("rx", Pins(f"{con}:2")),
            IOStandard("1.8_V_LVCMOS"),
        ),
        (f"eth{n}", 0,
            Subsignal("rx_ctl",  Pins(f"{con}:27")),
            Subsignal("rx_data", Pins(f"{con}:21 {con}:19 {con}:15 {con}:13")),
            Subsignal("tx_ctl",  Pins(f"{con}:20")),
            Subsignal("tx_data", Pins(f"{con}:16 {con}:14 {con}:10 {con}:8")),
            Subsignal("rst_n",   Pins(f"{con}:40")),
            Subsignal("mdc",     Pins(f"{con}:39")),
            Subsignal("mdio",    Pins(f"{con}:37")),
            IOStandard("1.8_V_LVCMOS"),
        ),
    ]

# Platform -----------------------------------------------------------------------------------------

class Platform(EfinixPlatform):
    default_clk_name   = "clk25"
    default_clk_period = 1e9/50e6

    def __init__(self, toolchain="efinity"):
        EfinixPlatform.__init__(self, "Ti60F225C3", _io, _connectors, iobank_info=iobank_info, toolchain=toolchain)

    def create_programmer(self):
        return EfinixProgrammer()

    def do_finalize(self, fragment):
        EfinixPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk25", loose=True), 1e9/50e6)
