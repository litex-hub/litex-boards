#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Mark Standke <mstandke@cern.ch>
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
        69:   "J8",     70  :   "K15",
        71:   "J14",    72  :   "M16",

        75:   "A9",     76  :   "G15",
        77:   "A8",     78  :   "F15",
        79:   "C9",     80  :   "J15",
        81:   "B9",     82  :   "J16",

        85:   "D9",     86  :   "F17",
        87:   "D8",     88  :   "E17",
        89:   "E10",    90  :   "E15",
        91:   "D10",    92  :   "E16",

        95:   "F9",     96  :   "H16",
        97:   "F8",     98  :   "G16",
        99:   "H9",     100 :   "D15",
        101:   "H8",    102 :   "D16",

        105:   "N18",   106 :   "P16",
        107:   "M19",   108 :   "N17",
        109:   "R16",   110 :   "U17",
        111:   "R17",   112 :   "T17",

        115:   "P23",   116 :   "R18",
        117:   "N23",   118 :   "P18",
        119:   "T24",   120 :   "R22",
        121:   "T25",   122 :   "R23",

        125:   "N19",   126 :   "P24",
        127:   "M20",   128 :   "N24",
        129:   "T18",   130 :   "P19",
        131:   "T19",   132 :   "P20",

        135:   "U19",   136 :   "T22",
        137:   "U20",   138 :   "T23",
        139:   "T20",   140 :   "K25",
        141:   "R20",   142 :   "K26",

        145:   "R25",   146 :   "N21",
        147:   "P25",   148 :   "N22",

        151:   "R21",   152 :   "M24",
        153:   "P21",   154 :   "L24",

        157:   "M21",   158 :   "M25",
        159:   "M22",   160 :   "L25",
        161:   "R26",   162 :   "N26",
        163:   "P26",   164 :   "M26",
    })
]

_st1_io = [
    ("clk_ref", 0,
        Subsignal("p", Pins("C:7"), IOStandard("LVDS")),
        Subsignal("n", Pins("C:9"), IOStandard("LVDS"))
    ),
    ("clk_ref0", 0,
        Subsignal("p", Pins("B:3"), IOStandard("LVDS")),
        Subsignal("n", Pins("B:5"), IOStandard("LVDS"))
    ),
    ("clk_ref1", 0,
        Subsignal("p", Pins("C:10"), IOStandard("LVDS")),
        Subsignal("n", Pins("C:12"), IOStandard("LVDS"))
    ),
    ("clk_ref2", 0,
        Subsignal("p", Pins("C:3"), IOStandard("LVDS")),
        Subsignal("n", Pins("C:5"), IOStandard("LVDS"))
    ),
    # daughterboard LEDs
    ("user_led", 4, Pins("C:142"), IOStandard("LVCMOS33"), Misc("SLEW=SLOW")),
    ("user_led", 5, Pins("C:144"), IOStandard("LVCMOS33"), Misc("SLEW=SLOW")),
    ("i2c_fpga", 0,
        Subsignal("scl",     Pins("A:111")),
        Subsignal("sda",     Pins("A:113")),
        Subsignal("int_n",   Pins("A:115")),
        IOStandard("LVCMOS33")
    ),
    ("i2c_fpga", 0,
        Subsignal("scl",     Pins("A:55")),
        Subsignal("sda",     Pins("A:57")),
        IOStandard("LVCMOS33")
    ),

    # HDMI Bus
    ("hdmi", 0,
        Subsignal("clk_p",   Pins("C:139")),
        Subsignal("clk_n",   Pins("C:141")),
        Subsignal("data0_p", Pins("C:45")),
        Subsignal("data0_n", Pins("C:47")),
        Subsignal("data1_p", Pins("C:51")),
        Subsignal("data1_n", Pins("C:53")),
        Subsignal("data2_p", Pins("C:57")),
        Subsignal("data2_n", Pins("C:59")),
        Subsignal("hpd",     Pins("A:61")),
        IOStandard("TMDS_33")
    ),
    ("sfp_tx", 0,  # SFP A
        Subsignal("p", Pins("C:63")),
        Subsignal("n", Pins("C:65"))
    ),
    ("sfp_rx", 0,  # SFP A
        Subsignal("p", Pins("C:66")),
        Subsignal("n", Pins("C:68"))
    ),
    ("usb3", 0,
        Subsignal("tx_p", Pins("B:29")),
        Subsignal("tx_n", Pins("B:33")),
        Subsignal("rx_p", Pins("B:32")),
        Subsignal("rx_n", Pins("B:36")),
    )
    ("usb3", 1,
        Subsignal("tx_p", Pins("B:37")),
        Subsignal("tx_n", Pins("B:41")),
        Subsignal("rx_p", Pins("B:40")),
        Subsignal("rx_n", Pins("B:44")),
    )
    ("displayport", 0,
        Subsignal("aux_in",  Pins("A:88")),
        Subsignal("aux_out", Pins("A:90")),
        Subsignal("aux_oe",  Pins("A:92")),
        Subsignal("hpd",     Pins("A:94")),
        Subsignal("lanes_p", Pins("B:21 B:13 B:16 B:24")),
        Subsignal("lanes_n", Pins("B:25 B:17 B:20 B:28")),
    )
    ("mipi", 0,
        Subsignal("clkp", Pins("C:151")),
        Subsignal("clkn", Pins("C:153")),
        Subsignal("clk_d0lp_p", Pins("C:160")),
        Subsignal("clk_d0lp_n", Pins("C:162")),
        Subsignal("dp",   Pins("C:145 C:154")),
        Subsignal("dn",   Pins("C:147 C:156")),
        IOStandard("MIPI_DPHY")
    ),
    ("mipi", 1,
        Subsignal("clkp", Pins("C:148")),
        Subsignal("clkn", Pins("C:150")),
        Subsignal("clk_d0lp_p", Pins("C:161")),
        Subsignal("clk_d0lp_n", Pins("C:163")),
        Subsignal("dp",   Pins("C:164 C:157")),
        Subsignal("dn",   Pins("C:166 C:159")),
        IOStandard("MIPI_DPHY")
    ),
]

_st1_connectors = [
    ("FMC", {
        "DP0_C2M_P":   "B:45",
        "DP0_C2M_N":   "B:47",
        "DP1_C2M_P":   "B:51",
        "DP1_C2M_N":   "B:53",
        "CLK1_M2C_P":  "B:57",
        "CLK1_M2C_N":  "B:59",
        "DP2_C2M_P":   "B:63",
        "DP2_C2M_N":   "B:65",
        "DP3_C2M_P":   "B:69",
        "DP3_C2M_N":   "B:71",
        "LA33_P":      "B:75",
        "LA33_N":      "B:77",
        "LA32_P":      "B:81",
        "LA32_N":      "B:83",
        "LA31_P":      "B:87",
        "LA31_N":      "B:89",
        "LA30_P":      "B:91",
        "LA30_N":      "B:93",
        "LA29_P":      "B:97",
        "LA29_N":      "B:99",
        "LA28_P":      "B:101",
        "LA28_N":      "B:103",
        "LA27_P":      "B:107",
        "LA27_N":      "B:109",
        "LA26_P":      "B:111",
        "LA26_N":      "B:113",
        "LA25_P":      "B:117",
        "LA25_N":      "B:119",
        "LA18_CC_P":   "B:123",
        "LA18_CC_N":   "B:125",
        "LA24_P":      "B:129",
        "LA24_N":      "B:131",
        "LA23_P":      "B:133",
        "LA23_N":      "B:135",
        "LA22_P":      "B:139",
        "LA22_N":      "B:141",
        "LA21_P":      "B:145",
        "LA21_N":      "B:147",
        "LA17_CC_P":   "B:151",
        "LA17_CC_N":   "B:153",
        "LA20_P":      "B:157",
        "LA20_N":      "B:159",
        "LA19_P":      "B:163",
        "LA19_N":      "B:165",
        "DP0_M2C_P":   "B:48",
        "DP0_M2C_N":   "B:50",
        "DP1_M2C_P":   "B:54",
        "DP1_M2C_N":   "B:56",
        "DP2_M2C_P":   "B:60",
        "DP2_M2C_N":   "B:62",
        "DP3_M2C_P":   "B:66",
        "DP3_M2C_N":   "B:68",
        "LA16_P":      "B:72",
        "LA16_N":      "B:74",
        "CLK0_M2C_P":  "B:78",
        "CLK0_M2C_N":  "B:80",
        "LA15_P":      "B:84",
        "LA15_N":      "B:86",
        "LA14_P":      "B:90",
        "LA14_N":      "B:92",
        "LA13_P":      "B:94",
        "LA13_N":      "B:96",
        "LA12_P":      "B:100",
        "LA12_N":      "B:102",
        "LA11_P":      "B:104",
        "LA11_N":      "B:106",
        "LA10_P":      "B:110",
        "LA10_N":      "B:112",
        "LA09_P":      "B:114",
        "LA09_N":      "B:116",
        "LA08_P":      "B:120",
        "LA08_N":      "B:122",
        "LA07_P":      "B:124",
        "LA07_N":      "B:126",
        "LA01_CC_P":   "B:130",
        "LA01_CC_N":   "B:132",
        "LA06_P":      "B:136",
        "LA06_N":      "B:138",
        "LA05_P":      "B:142",
        "LA05_N":      "B:144",
        "LA04_P":      "B:148",
        "LA04_N":      "B:150",
        "LA00_CC_P":   "B:154",
        "LA00_CC_N":   "B:156",
        "LA03_P":      "B:160",
        "LA03_N":      "B:162",
        "LA02_P":      "B:164",
        "LA02_N":      "B:166",

        "DP4_C2M_P":   "C:13",
        "DP4_C2M_N":   "C:17",
        "DP5_C2M_P":   "C:21",
        "DP5_C2M_N":   "C:25",
        "DP6_C2M_P":   "C:29",
        "DP6_C2M_N":   "C:33",
        "DP7_C2M_P":   "C:37",
        "DP7_C2M_N":   "C:41",
        "HA13_P":      "C:69",
        "HA13_N":      "C:71",
        "HA11_P":      "C:75",
        "HA11_N":      "C:77",
        "HA09_P":      "C:79",
        "HA09_N":      "C:81",
        "HA07_P":      "C:85",
        "HA07_N":      "C:87",
        "HA01_CC_P":   "C:89",
        "HA01_CC_N":   "C:91",
        "HA04_P":      "C:95",
        "HA04_N":      "C:97",
        "HA02_P":      "C:99",
        "HA02_N":      "C:101",
        "HA17_P":      "C:135",
        "HA17_N":      "C:137",

        "GCLK1_M2C_P": "C:4",
        "GCLK1_M2C_N": "C:6",
        "DP4_M2C_P":   "C:16",
        "DP4_M2C_N":   "C:20",
        "DP5_M2C_P":   "C:24",
        "DP5_M2C_N":   "C:28",
        "DP6_M2C_P":   "C:32",
        "DP6_M2C_N":   "C:36",
        "DP7_M2C_P":   "C:40",
        "DP7_M2C_N":   "C:44",
        "HA16_P":      "C:48",
        "HA16_N":      "C:50",
        "HA15_P":      "C:54",
        "HA15_N":      "C:56",
        "HA14_P":      "C:60",
        "HA14_N":      "C:62",
        "HA12_P":      "C:72",
        "HA12_N":      "C:74",
        "HA10_P":      "C:78",
        "HA10_N":      "C:80",
        "HA08_P":      "C:82",
        "HA08_N":      "C:84",
        "HA00_CC_P":   "C:88",
        "HA00_CC_N":   "C:90",
        "HA06_P":      "C:92",
        "HA06_N":      "C:94",
        "HA05_P":      "C:98",
        "HA05_N":      "C:100",
        "HA03_P":      "C:102",
        "HA03_N":      "C:104",
    }),
    ("IO1", {
        "CLK_P": "C:122",
        "CLK_N": "C:124",
         "D0_P": "C:115",
         "D1_N": "C:117",
         "D2_P": "C:129",
         "D3_N": "C:131",
         "D4_P": "C:125",
         "D5_N": "C:127",
         "D6_P": "C:119",
         "D7_N": "C:121",
         "D8_P": "C:109",
         "D9_N": "C:111",
        "D10_P": "C:105",
        "D11_N": "C:107",
        "D12_P": "C:138",
        "D13_N": "C:140",
        "D14_P": "C:132",
        "D15_N": "C:134",
        "D16_P": "C:128",
        "D17_N": "C:130",
        "D18_P": "C:118",
        "D19_N": "C:120",
        "D20_P": "C:112",
        "D21_N": "C:114",
        "D22_P": "C:108",
        "D23_N": "C:110",
    }),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk200"
    default_clk_period = 1e9/200e6

    def __init__(self, toolchain="vivado"):
        Xilinx7SeriesPlatform.__init__(self, "xc7k160tffg676-2", _io, toolchain=toolchain)
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

    def add_st1_baseboard(self):
        self.add_extension(_st1_io)
        self.add_connector(_st1_connectors)

    def create_programmer(self):
        return OpenOCD("openocd_xc7_ft232.cfg", "bscan_spi_xc7k160t.bit")

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk200", loose=True), 1e9/200e6)