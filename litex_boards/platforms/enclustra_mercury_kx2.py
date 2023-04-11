#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Mark Standke <mstandke@cern.ch>
# Copyright (c) 2023 Hans Baier <hansfbaier@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk200", 0,
        Subsignal("p", Pins("AB11"), IOStandard("LVDS")),
        Subsignal("n", Pins("AC11"), IOStandard("LVDS"))
    ),
    ("cpu_reset_n", 0, Pins("G9"), IOStandard("LVCMOS25")),

    # Leds
    ("user_led", 0, Pins("U9"),  IOStandard("LVCMOS15"), Misc("SLEW=SLOW")),
    ("user_led", 1, Pins("V12"), IOStandard("LVCMOS15"), Misc("SLEW=SLOW")),
    ("user_led", 2, Pins("V13"), IOStandard("LVCMOS15"), Misc("SLEW=SLOW")),
    ("user_led", 3, Pins("W13"), IOStandard("LVCMOS15"), Misc("SLEW=SLOW")),

    # The Serial which connects to the second UART
    # of the FTDI on the base board (first FTDI port is JTAG)
    ("serial", 0,
        Subsignal("tx", Pins("A20")),
        Subsignal("rx", Pins("B20")),
        IOStandard("LVCMOS15")
     ),

    # Serial This one is multiplexed with the I2C bus
    ("serial", 1,
        Subsignal("tx", Pins("W11")),
        Subsignal("rx", Pins("AB16")),
        IOStandard("LVCMOS15")
     ),

    # DDR3 SDRAM
    ("ddram", 0,
        Subsignal("a", Pins(
            "AE11 AF9 AD10 AB10  AA9 AB9 AA8 AC8",
            "AA7  AE8 AF10 AD8  AE10 AF8 AC7"),
            IOStandard("SSTL15")),
        Subsignal("ba",    Pins("AD11 AA10 AF12"), IOStandard("SSTL15")),
        Subsignal("ras_n", Pins("AE13"), IOStandard("SSTL15")),
        Subsignal("cas_n", Pins("AE12"), IOStandard("SSTL15")),
        Subsignal("we_n",  Pins("AA12"), IOStandard("SSTL15")),
        Subsignal("cs_n",  Pins("Y12"), IOStandard("SSTL15")),
        Subsignal("dm", Pins(
            "Y3 U5 AD4 AC4 AF19 AC16 AB19 V14"),
            IOStandard("SSTL15")),
        Subsignal("dq", Pins(
            "AA2    Y2  AB2   V1   Y1   W1  AC2   V2",
            "W3     V3   U1   U7   U6   V4   V6   U2",
            "AE3   AE6  AF3  AD1  AE1  AE2  AF2  AE5",
            "AD5    Y5  AC6   Y6  AB4  AD6  AB6  AC3",
            "AD16 AE17 AF15 AF20 AD15 AF14 AE15 AF17",
            "AA14 AA15 AC14 AD14 AB14 AB15 AA17 AA18",
            "AB20 AD19 AC19 AA20 AA19 AC17 AD18 AB17",
            "W15   W16  W14   V16 V19  V17  V18  Y17"),
            IOStandard("SSTL15_T_DCI")),
        Subsignal("dqs_p", Pins("AB1 W6 AF5 AA5 AE18 Y15 AD20 W18"),
            IOStandard("DIFF_SSTL15_T_DCI")),
        Subsignal("dqs_n", Pins("AC1 W5 AF4 AB5 AF18 Y16 AE20 W19"),
            IOStandard("DIFF_SSTL15_T_DCI")),
        Subsignal("clk_p", Pins("AB12"), IOStandard("DIFF_SSTL15")),
        Subsignal("clk_n", Pins("AC12"), IOStandard("DIFF_SSTL15")),
        Subsignal("cke",   Pins("AA13"), IOStandard("SSTL15")),
        Subsignal("odt",   Pins("AD13"), IOStandard("SSTL15")),
        Subsignal("reset_n", Pins("AB7"), IOStandard("SSTL15"), Misc("SLEW=SLOW")),
        Misc("SLEW=FAST"),
        Misc("VCCAUX_IO=HIGH"),
    ),

    # Don't use, this is for documentation only.
    # This pin sets DDR3 voltage. LOW = 1.3V, HI-Z = 1.5V, HIGH = illegal
    ("ddram_vsel", 0, Pins('AA3'), IOStandard("SSTL15"), Misc("SLEW=SLOW")),
]

_connectors = [
    ("A", {
         15 : "W20",    16 : "AA23",
         17 : "Y21",    18 : "AB24",
         19 : "AD21",
         21 : "AE21",   22 : "AB21",
                        24 : "AC21",
         25 : "AE22",
         27 : "AF22",   28 : "AB22",
                        30 : "AC22",
         31 : "V21",
         33 : "W21",    34 : "AE23",
                        36 : "AF23",
         37 : "V23",
         39 : "V24",    40 : "AF24",
                        42 : "AF25",
         43 : "U24",
         45 : "U25",    46 : "Y22",
                        48 : "AA22",
         49 : "AC23",
         51 : "AC24",   52 : "AD25",
                        54 : "AE25",
         55 : "W25",
         57 : "W26",    58 : "AD23",
                        60 : "AD24",
         61 : "U26",
         63 : "V26",    64 : "U22",
                        66 : "V22",
         67 : "AB26",
         69 : "AC26",   70 : "W23",
                        72 : "W24",
         73 : "AA25",
         75 : "AB25",   76 : "AD26",
                        78 : "AE26",
         79 : "U21",
         81 : "Y20",    82 : "Y25",
                        84 : "Y26",
         85 : "Y23",
         87 : "AA24",   88 : "D23",
                        90 : "D24",
         91 : "C21",    92 : "E21",
         93 : "B21",    94 : "E22",
         95 : "D26",
         97 : "C26",    98 : "D21",
                        100 : "C22",
        101 : "A23",
        103 : "A24",    104 : "F22",
        105 : "B20",    106 : "E23",
        107 : "A20",
    }),
    ("B", {
        1   : "D6" ,
        3   : "D5" ,     4: "H6",
        5   : "F6" ,     6: "H5",
        7   : "F5" ,
                        10: "K6",
                        12: "K5",
        13  : "P2" ,
                        16: "R4",
        17  : "P1" ,
                        20: "R3",
        21  : "M2" ,
                        24: "N4",
        25  : "M1" ,
                        28: "N3",
        29  : "K2" ,
                        32: "L4",
        33  : "K1" ,
                        36: "L3",
        37  : "H2" ,
                        40: "J4",
        41  : "H1" ,
                        44: "J3",
        45  : "F2" ,
        47  : "F1" ,    48: "G4",
                        50: "G3",
        51  : "D2" ,
        53  : "D1" ,    54: "E4",
                        56: "E3",
        57  : "G11",
        59  : "F10",    60: "C4",
                        62: "C3",
        63  : "B2" ,
        65  : "B1" ,    66: "B6",
                        68: "B5",
        69  : "A4" ,
        71  : "A3" ,    72: "F19",
                        74: "E20",
        75  : "C14",
        77  : "C13",    78: "H17",
                        80: "H18",
        81  : "D14",
        83  : "D13",    84: "G19",
                        86: "F20",
        87  : "J13",
        89  : "H13",    90: "L19",
        91  : "F14",    92: "L20",
        93  : "F13",    94: "K20",
                        96: "J20",
        97  : "E13",
        99  : "E12",   100: "M17",
        101 : "G12",   102: "L18",
        103 : "F12",   104: "L17",
                       106: "K18",
        107 : "J11",
        109 : "J10",   110: "K16",
        111 : "H12",   112: "K17",
        113 : "H11",   114: "J18",
                       116: "J19",
        117 : "G10",
        119 : "G9" ,   120: "H19",
                       122: "G20",
        123 : "E11",   124: "D19",
        125 : "D11",   126: "D20",

        129 : "A13",   130: "G17",
        131 : "A12",   132: "F18",
        133 : "B10",
        135 : "A10",   136: "C17",
                       138: "C18",
        139 : "B12",
        141 : "B11",   142: "C16",
                       144: "B16",
        145 : "H14",
        147 : "G14",   148: "B17",
                       150: "A17",
        151 : "C12",
        153 : "C11",   154: "E18",
                       156: "D18",
        157 : "B14",
        159 : "A14",   160: "C19",
                       162: "B19",
        163 : "B15",   164: "A18",
        165 : "A15",   166: "A19",
    }),
    ("C", {
        69:   "J8",     
        71:   "J14",     72 :   "K15",
                         74 :   "M16",
        75:   "A9",     
        77:   "A8",      78 :   "G15",
        79:   "C9",      80 :   "F15",
        81:   "B9",      82 :   "J15",
                         84 :   "J16",
        85:   "D9",     
        87:   "D8",      88 :   "F17",
        89:   "E10",     90 :   "E17",
        91:   "D10",     92 :   "E15",
                         94 :   "E16",
        95:   "F9",     
        97:   "F8",      98 :   "H16",
        99:   "H9",     100 :   "G16",
        101:   "H8",    102 :   "D15",
                        104 :   "D16",
        105:   "N18",   
        107:   "M19",   108 :   "P16",
        109:   "R16",   110 :   "N17",
        111:   "R17",   113 :   "U17",
                        114 :   "T17",
        115:   "P23",   
        117:   "N23",   118 :   "R18",
        119:   "T24",   120 :   "P18",
        121:   "T25",   122 :   "R22",
                        124 :   "R23",
        125:   "N19",   
        127:   "M20",   128 :   "P24",
        129:   "T18",   130 :   "N24",
        131:   "T19",   132 :   "P19",
                        134 :   "P20",
        135:   "U19",   
        137:   "U20",   138 :   "T22",
        139:   "T20",   140 :   "T23",
        141:   "R20",   142 :   "K25",
                        144 :   "K26",
        145:   "R25",   
        147:   "P25",   148 :   "N21",
                        150 :   "N22",
        151:   "R21", 
        153:   "P21",   154 :   "M24",
                        156 :   "L24",     
        157:   "M21",   160 :   "M25",
        159:   "M22",   162 :   "L25",
        161:   "R26",   164 :   "N26",
        163:   "P26",   166 :   "M26",
    })
]

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk200"
    default_clk_period = 1e9/200e6

    def __init__(self, toolchain="vivado"):
        Xilinx7SeriesPlatform.__init__(self, "xc7k160tffg676-2", _io, _connectors, toolchain=toolchain)
        self.add_platform_command("set_property CONFIG_VOLTAGE 1.8 [current_design]")
        self.add_platform_command("set_property CFGBVS GND [current_design]")
        # DDR3 is connected to banks 32, 33 and 34
        self.add_platform_command("set_property INTERNAL_VREF 0.750 [get_iobanks 32]")
        self.add_platform_command("set_property INTERNAL_VREF 0.750 [get_iobanks 33]")
        self.add_platform_command("set_property INTERNAL_VREF 0.750 [get_iobanks 34]")
        # The VRP/VRN resistors are connected to bank 34.
        # Banks 32 and 33 have LEDs in the places, so we have to use the reference from bank 34
        # Bank 33 has no _T_DCI signals connected
        self.add_platform_command("set_property DCI_CASCADE {{32}} [get_iobanks 34]")
        self.add_platform_command("set_property BITSTREAM.CONFIG.CONFIGRATE 22 [current_design]")
        self.add_platform_command("set_property BITSTREAM.CONFIG.OVERTEMPPOWERDOWN ENABLE [current_design]")

        # Important! Do not remove this constraint!
        # This property ensures that all unused pins are set to high impedance.
        # If the constraint is removed, all unused pins have to be set to HiZ in the top level file
        # This causes DDR3 to use 1.5V by default
        self.add_platform_command("set_property BITSTREAM.CONFIG.UNUSEDPIN PULLNONE [current_design]")

    def add_baseboard(self, bb):
        self.add_connector(bb.connectors)
        self.add_extension(bb.io)

    def create_programmer(self):
        return OpenOCD("openocd_xc7_ft232.cfg", "bscan_spi_xc7k160t.bit")

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk200", loose=True), 1e9/200e6)