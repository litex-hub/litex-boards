#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019 Antony Pavlov <antonynpavlov@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.altera import AlteraPlatform
from litex.build.altera.programmer import USBBlaster

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk
    ("clk50", 0, Pins("AF14"), IOStandard("3.3-V LVTTL")),
    ("clk50", 1, Pins("AA16"), IOStandard("3.3-V LVTTL")),
    ("clk50", 2, Pins("Y26"),  IOStandard("3.3-V LVTTL")),
    ("clk50", 3, Pins("K14"),  IOStandard("3.3-V LVTTL")),

    # Leds
    ("user_led", 0, Pins("V16"), IOStandard("3.3-V LVTTL")),
    ("user_led", 1, Pins("W16"), IOStandard("3.3-V LVTTL")),
    ("user_led", 2, Pins("V17"), IOStandard("3.3-V LVTTL")),
    ("user_led", 3, Pins("V18"), IOStandard("3.3-V LVTTL")),
    ("user_led", 4, Pins("W17"), IOStandard("3.3-V LVTTL")),
    ("user_led", 5, Pins("W19"), IOStandard("3.3-V LVTTL")),
    ("user_led", 6, Pins("Y19"), IOStandard("3.3-V LVTTL")),
    ("user_led", 7, Pins("W20"), IOStandard("3.3-V LVTTL")),
    ("user_led", 8, Pins("W21"), IOStandard("3.3-V LVTTL")),
    ("user_led", 9, Pins("Y21"), IOStandard("3.3-V LVTTL")),

    # Seven Segment
    ("seven_seg", 0, Pins("AE26 AE27 AE28 AG27 AF28 AG28 AH28"), IOStandard("3.3-V LVTTL")),
    ("seven_seg", 1, Pins("AJ29 AH29 AH30 AG30 AF29 AF30 AD27"), IOStandard("3.3-V LVTTL")),
    ("seven_seg", 2, Pins("AB23 AE29 AD29 AC28 AD30 AC29 AC30"), IOStandard("3.3-V LVTTL")),
    ("seven_seg", 3, Pins("AD26 AC27 AD25 AC25 AB28 AB25 AB22"), IOStandard("3.3-V LVTTL")),
    ("seven_seg", 4, Pins("AA24 Y23  Y24  W22  W24  V23  W25"),  IOStandard("3.3-V LVTTL")),
    ("seven_seg", 5, Pins("V25  AA28 Y27  AB27 AB26 AA26 AA25"), IOStandard("3.3-V LVTTL")),

    # Button
    ("key", 0, Pins("AA14"), IOStandard("3.3-V LVTTL")),
    ("key", 1, Pins("AA15"), IOStandard("3.3-V LVTTL")),
    ("key", 2, Pins("W15"),  IOStandard("3.3-V LVTTL")),
    ("key", 3, Pins("Y16"),  IOStandard("3.3-V LVTTL")),

    # Switches
    ("user_sw", 0, Pins("AB12"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 1, Pins("AC12"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 2, Pins("AF9"),  IOStandard("3.3-V LVTTL")),
    ("user_sw", 3, Pins("AF10"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 4, Pins("AD11"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 5, Pins("AD12"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 6, Pins("AE11"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 7, Pins("AC9"),  IOStandard("3.3-V LVTTL")),
    ("user_sw", 8, Pins("AD10"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 9, Pins("AE12"), IOStandard("3.3-V LVTTL")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("JP1:1"), IOStandard("3.3-V LVTTL")),
        Subsignal("rx", Pins("JP1:2"),  IOStandard("3.3-V LVTTL"))
    ),

    # I2C
    ("i2c", 0,
        Subsignal("sclk", Pins("J12")),
        Subsignal("sdat", Pins("K12")),
        IOStandard("3.3-V LVTTL")
    ),

    # VGA
    ("vga", 0,
        Subsignal("hsync_n", Pins("B11")),
        Subsignal("vsync_n", Pins("D11")),
        Subsignal("r", Pins("A13 C13 E13 B12 C12 D12 E12 F1")),
        Subsignal("g", Pins("J9 J10 H12 G10 G11 G12 F11 E11")),
        Subsignal("b", Pins("B13 G13 H13 F14 H14 F15 G15 J14 F10")),
        IOStandard("3.3-V LVTTL")
    ),

    # GPIOs
    ("gpio_0", 0, Pins(
        "D3 C3  A2  A3  B3  B4  A4  B5",
        "A5 D5  B6  A6  B7  D6  A7  C6",
        "C8 E6  E7  D8  E8  F8  F9  E9",
        "C9 D9 E11 E10 C11 B11 A12 D11",
        "D12 B12"),
        IOStandard("3.3-V LVTTL")
    ),
    ("gpio_1", 0, Pins(
        "F13 T15 T14 T13 R13 T12 R12 T11",
        "T10 R11 P11 R10 N12  P9  N9 N11",
        "L16 K16 R16 L15 P15 P16 R14 N16",
        "N15 P14 L14 N14 M10 L13 J16 K15",
        "J13 J14"),
        IOStandard("3.3-V LVTTL")
    ),

    # SDR SDRAM
    ("sdram_clock", 0, Pins("AH12"), IOStandard("3.3-V LVTTL")),
    ("sdram", 0,
        Subsignal("a",     Pins(
            "AK14 AH14 AG15 AE14 AB15 AC14 AD14 AF15",
            "AH15 AG13 AG12 AH13 AJ14")),
        Subsignal("ba",    Pins("AF13 AJ12")),
        Subsignal("cs_n",  Pins("AG11")),
        Subsignal("cke",   Pins("AK13")),
        Subsignal("ras_n", Pins("AE13")),
        Subsignal("cas_n", Pins("AF11")),
        Subsignal("we_n",  Pins("AA13")),
        Subsignal("dq", Pins(
            "AK6   AJ7 AK7 AK8 AK9 AG10 AK11 AJ11",
            "AH10 AJ10 AJ9 AH9 AH8  AH7  AJ6 AJ5")),
        Subsignal("dm", Pins("AB13 AK12")),
        IOStandard("3.3-V LVTTL")
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    # PIN    0 1    2    3    4    5    6    7    8    9    10   11 12 13   14   15   16   17   18   19   20   21   22   23   24   25   26   27   28   29 30 31   32   33   34   35   36   37   38   39   40
    ("JP1", "- AC18 Y17  AD17 Y18  AK16 AK18 AK19 AJ19 AJ17 AJ16 -  -  AH18 AH17 AG16 AE16 AF16 AG17 AA18 AA19 AE17 AC20 AH19 AJ20 AH20 AK21 AD19 AD20 -  -  AE18 AE19 AF20 AF21 AF19 AG21 AF18 AG20 AG18 AJ21"),
    ("JP2", "- AB17 AA21 AB21 AC23 AD24 AE23 AE24 AF25 AF26 AG25 -  -  AG26 AH24 AH27 AJ27 AK29 AK28 AK27 AJ26 AK26 AH25 AJ25 AJ24 AK24 AG23 AK23 AH23 -  -  AK22 AJ22 AH22 AG22 AF24 AF23 AE22 AD21 AA20 AC22")
]

# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self, toolchain="quartus"):
        AlteraPlatform.__init__(self, "5CSEMA5F31C6", _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        return USBBlaster(cable_name="DE-SoC", device_id=2)

    def do_finalize(self, fragment):
        AlteraPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
