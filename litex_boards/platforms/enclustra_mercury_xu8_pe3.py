#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2023-2024 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxUSPPlatform, VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst.
    ("clk33",  0, Pins("P19"), IOStandard("SSTL12")),
    ("clk100", 0,
        Subsignal("n", Pins("AJ6"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("p", Pins("AH6"), IOStandard("DIFF_SSTL12_DCI")),
    ),

    # Leds.
    ("user_led", 0, Pins("AF13"), IOStandard("LVCMOS12")),

    # Serial.
    ("serial", 0,
        Subsignal("tx", Pins("C14")), # ANIO IO_D22_P.
        Subsignal("rx", Pins("B14")), # ANIO IO_D23_N.
        IOStandard("LVCMOS18")
    ),
    ("debug", 0, Pins("G13"), IOStandard("LVCMOS18")), # ANIO IO_D20_P.
    ("debug", 1, Pins("F13"), IOStandard("LVCMOS18")), # ANIO IO_D21_N.

    # I2C.
    ("i2c_user", 0,
        Subsignal("scl", Pins("K15"), Misc("PULLUP=True")),
        Subsignal("sda", Pins("K14"), Misc("PULLUP=True")),
        IOStandard("LVCMOS18")
    ),
    ("i2c_mgmt", 0,
        Subsignal("scl", Pins("AB13"), Misc("PULLUP=True")),
        Subsignal("sda", Pins("AH13"), Misc("PULLUP=True")),
        IOStandard("LVCMOS12")
    ),

    # PCIe.
    ("pcie_x4", 0, # GTH Bank 227.
        Subsignal("rst_n", Pins("AF2"), IOStandard("LVCMOS12"), Misc("PULLUP=TRUE")),
        Subsignal("clk_p", Pins("B10")),
        Subsignal("clk_n", Pins("B9")),
        Subsignal("rx_p",  Pins("D2 C4 B2 A4")),
        Subsignal("rx_n",  Pins("D1 C3 B1 A3")),
        Subsignal("tx_p",  Pins("D6 C8 B6 A8")),
        Subsignal("tx_n",  Pins("D5 C7 B5 A7")),
    ),

    ("pcie_x8", 0, # GTH Bank 227 and 226.
        Subsignal("rst_n", Pins("AF2"), IOStandard("LVCMOS12"), Misc("PULLUP=TRUE")),
        Subsignal("clk_p", Pins("B10")),
        Subsignal("clk_n", Pins("B9")),
        Subsignal("rx_p",  Pins("D2 C4 B2 A4 H2 G4 F2 E4")),
        Subsignal("rx_n",  Pins("D1 C3 B1 A3 H1 G3 F1 E3")),
        Subsignal("tx_p",  Pins("D6 C8 B6 A8 H6 G8 F6 E8")),
        Subsignal("tx_n",  Pins("D5 C7 B5 A7 H5 G7 F5 E7")),
    ),

    # DDR4 SDRAM.
    ("ddram", 0,
        Subsignal("a",       Pins(
            "AG6 AG5 AK7 AK6 AJ4 AK4 AF6 AF5",
            "AH4 AK3 AK2 AJ2 AJ1 AH3"),
            IOStandard("SSTL12_DCI")),
        Subsignal("we_n",    Pins("AH2"),     IOStandard("SSTL12_DCI")),  # A14
        Subsignal("cas_n",   Pins("AG4"),     IOStandard("SSTL12_DCI")),  # A15
        Subsignal("ras_n",   Pins("AG3"),     IOStandard("SSTL12_DCI")),  # A16
        Subsignal("ba",      Pins("AH1 AF3"), IOStandard("SSTL12_DCI")),
        Subsignal("bg",      Pins("AF8 AF7"), IOStandard("SSTL12_DCI")),
        Subsignal("cs_n",    Pins("AE9"),     IOStandard("SSTL12_DCI")),
        Subsignal("act_n",   Pins("AG1"),     IOStandard("SSTL12_DCI")),
        Subsignal("dm",      Pins("AA13 AG13 AF16 AG16"), IOStandard("POD12_DCI")),
        Subsignal("dq",      Pins(
            "AB15 AE15 AD15 AE14 AC14 AD14 AA15 AE13",
            "AH14 AK13 AG15 AK12 AG14 AK14 AF15 AJ14",
            "AC16 AE19 AD17 AD19 AC17 AE17 AC18 AD16",
            "AE18 AK16 AG18 AJ17 AH17 AH18 AJ16 AF18"),
            IOStandard("POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_p",   Pins("AA14 AJ15 AA16 AK17"),
            IOStandard("DIFF_POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_n",   Pins("AB14 AK15 AB16 AK18"),
            IOStandard("DIFF_POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("clk_p",   Pins("AJ5"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("clk_n",   Pins("AK5"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("cke",     Pins("AE8"), IOStandard("SSTL12_DCI")),
        Subsignal("odt",     Pins("AF1"), IOStandard("SSTL12_DCI")),
        Subsignal("reset_n", Pins("AG9"), IOStandard("LVCMOS12")),
        Misc("SLEW=FAST"),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_j800_pins = {
    15 :  "C14", 16 :  "G13", 17 :  "B14", 18 :  "F13",  19 :  "K13",  21 :  "J12", 22 :  "H13", 24 :  "H12",
    25 :  "H14", 27 :  "G14", 28 :  "D12", 30 :  "C12",  31 :  "C17",  33 :  "B16", 34 :  "A14", 36 :  "A13",
    37 :  "F12", 39 :  "E12", 40 :  "B12", 42 :  "A12",  43 :  "E14",  45 :  "E13", 46 :  "D14", 48 :  "C13",
    49 :  "G16", 51 :  "G15", 52 :  "F16", 54 :  "F15",  55 :  "K15",  57 :  "K14", 58 :  "K12", 60 :  "K11",
    61 :  "J16", 63 :  "H16", 64 :  "J15", 66 :  "J14",  67 :  "D16",  69 :  "C16", 70 :  "L15", 72 :  "L14",
    73 :  "B15", 75 :  "A15", 76 :  "E15", 78 :  "D15",  79 :  "A17",  81 :  "A16", 85 :  "E17", 87 :  "D17",
    88 : "AF17", 90 : "AC19", 92 : "AH16", 94 : "AG19", 111 : "AB13", 113 : "AH13",
}

_j801_pins = {
      3 : "B10" ,   4 : "M23",   5 : "B9"  ,   6 : "M24" ,   7 : "L25",   9 : "L26",  10 : "D10" ,  12 : "D9"  ,
     13 : "M27" ,  16 : "L29",  17 : "M28" ,  20 : "L30" ,  21 : "K27",  24 : "J29",  25 : "K28" ,  28 : "J30" ,
     29 : "J25" ,  32 : "H27",  33 : "J26" ,  36 : "H28" ,  37 : "G25",  40 : "G29",  41 : "G26" ,  44 : "G30" ,
     45 : "D6"  ,  47 : "D5" ,  48 : "D2"  ,  50 : "D1"  ,  51 : "C8" ,  53 : "C7" ,  54 : "C4"  ,  56 : "C3"  ,
     60 : "B2"  ,  62 : "B1" ,  63 : "B6"  ,  65 : "B5"  ,  66 : "A4" ,  68 : "A3" ,  69 : "A8"  ,  71 : "A7"  ,
     72 : "AB1" ,  74 : "AC1",  78 : "AC8" ,  80 : "AC7" ,  84 : "AD1",  86 : "AE1",  90 : "AA2" ,  92 : "AA1" ,
     94 : "AD2" ,  96 : "AE2", 100 : "AA3" , 102 : "AB3" , 104 : "AC3", 106 : "AC2", 110 : "AD4" , 112 : "AE4" ,
    114 : "AB4" , 116 : "AC4", 120 : "AD5" , 122 : "AE5" , 124 : "AA6", 126 : "AA5", 129 : "AE3" , 130 : "AB6" ,
    131 : "Y1"  , 132 : "AB5", 133 : "AD11", 135 : "AD10", 136 : "AC6", 138 : "AD6", 139 : "Y10" , 141 : "AA10",
    142 : "Y7"  , 144 : "AA7", 145 : "AA12", 147 : "AA11", 148 : "W8" , 150 : "Y8" , 151 : "AD7" , 153 : "AE7" ,
    154 : "AA8" , 156 : "AB8", 157 : "AB11", 159 : "AC11", 160 : "AC9", 162 : "AD9", 163 : "AC12", 164 : "AB10",
    165 : "AD12", 166 : "AB9",
}

_j900_pins = {
      3 : "L8"  ,   4 : "H10" ,   5 : "L7"  ,   6 : "H9"  ,   7 :   "J8",   9 :   "J7",  10 :  "F10",  12 : "F9",
     13 : "H6"  ,  16 : "H2"  ,  17 : "H5"  ,  20 : "H1"  ,  21 :   "G8",  24 :   "G4",  25 :   "G7",  28 : "G3",
     29 : "F6"  ,  32 : "F2"  ,  33 : "F5"  ,  36 : "F1"  ,  37 :   "E8",  40 :   "E4",  41 :   "E7",  44 : "E3",
     45 : "P6"  ,  47 : "P5"  ,  48 : "N4"  ,  50 : "N3"  ,  51 :   "M6",  53 :   "M5",  54 :   "M2",  56 : "M1",
     57 : "L4"  ,  59 : "L3"  ,  60 : "K2"  ,  62 : "K1"  ,  63 :   "K6",  65 :   "K5",  66 :   "J4",  68 : "J3",
     69 : "N8"  ,  71 : "N7"  ,  72 : "R8"  ,  74 : "R7"  ,  75 :   "W4",  77 :   "W3",  78 :   "V2",  79 : "V6",
     80 : "V1"  ,  81 : "V5"  ,  82 : "U4"  ,  84 : "U3"  ,  85 :   "T6",  87 :   "T5",  88 :   "T2",  89 : "R4",
     90 : "T1"  ,  91 : "R3"  ,  92 : "P2"  ,  94 : "P1"  , 139 :  "AH9", 141 :  "AJ9", 142 :  "AK9", 144 : "AK8",
    145 : "AF12", 147 : "AF11", 148 : "AH7" , 150 : "AJ7" , 151 :  "AG8", 153 :  "AH8", 154 : "AG11", 156 : "AH11",
    157 : "AF10", 159 : "AG10", 160 : "AH12", 161 : "AJ11", 162 : "AJ12", 163 : "AK11", 164 : "AJ10", 166 : "AK10",
}

_connectors = [
    # Mercury+ module connectors: A (J800), B (J801), C (J900).
    ("A", _j800_pins),
    ("B", _j801_pins),
    ("C", _j900_pins),

    ("HPC", {
        "DP1_M2C_P"     : "M2",
        "DP1_M2C_N"     : "M1",
        "DP2_M2C_P"     : "K2",
        "DP2_M2C_N"     : "K1",
        "DP3_M2C_P"     : "J4",
        "DP3_M2C_N"     : "J3",
        "DP1_C2M_P"     : "M6",
        "DP1_C2M_N"     : "M5",
        "DP2_C2M_P"     : "L4",
        "DP2_C2M_N"     : "L3",
        "DP3_C2M_P"     : "K6",
        "DP3_C2M_N"     : "K5",
        "DP0_C2M_P"     : "P6",
        "DP0_C2M_N"     : "P5",
        "DP0_M2C_P"     : "N4",
        "DP0_M2C_N"     : "N3",
        "LA06_P"        : "B:136",
        "LA06_N"        : "B:138",
        "LA10_P"        : "B:110",
        "LA10_N"        : "B:112",
        "LA14_P"        : "B:90",
        "LA14_N"        : "B:92",
        #"LA18_CC_P"     : "B:123",
        #"LA18_CC_N"     : "B:125",
        #"LA27_P"        : "B:107",
        #"LA27_N"        : "B:109",
        "HA01_CC_P"     : "C:151",
        "HA01_CC_N"     : "C:153",
        "HA05_P"        : "C:157",
        "HA05_N"        : "C:159",
        "HA09_P"        : "C:139",
        "HA09_N"        : "C:141",
        #"HA13_P"        : "C:129",
        #"HA13_N"        : "C:131",
        #"HA16_P"        : "C:118",
        #"HA16_N"        : "C:120",
        #"HA20_P"        : "C:112",
        #"HA20_N"        : "C:114",
        #"CLK1_M2C_P"    : "B:57",
        #"CLK1_M2C_N"    : "B:59",
        "LA00_CC_P"     : "B:154",
        "LA00_CC_N"     : "B:156",
        "LA03_P"        : "B:160",
        "LA03_N"        : "B:162",
        "LA08_P"        : "B:120",
        "LA08_N"        : "B:122",
        "LA12_P"        : "B:100",
        "LA12_N"        : "B:102",
        "LA16_P"        : "B:72",
        "LA16_N"        : "B:74",
        "LA20_P"        : "B:157",
        "LA20_N"        : "B:159",
        "LA22_P"        : "B:139",
        "LA22_N"        : "B:141",
        #"LA25_P"        : "B:117",
        #"LA25_N"        : "B:119",
        #"LA29_P"        : "B:97",
        #"LA29_N"        : "B:99",
        #"LA31_P"        : "B:87",
        #"LA31_N"        : "B:89",
        #"LA33_P"        : "B:75",
        #"LA33_N"        : "B:77",
        "HA03_P"        : "C:161",
        "HA03_N"        : "C:163",
        "HA07_P"        : "C:145",
        "HA07_N"        : "C:147",
        #"HA11_P"        : "C:135",
        #"HA11_N"        : "C:137",
        #"HA14_P"        : "C:128",
        #"HA14_N"        : "C:130",
        #"HA18_P"        : "C:115",
        #"HA18_N"        : "C:117",
        #"HA22_P"        : "C:108",
        #"HA22_N"        : "C:110",
        #"GBTCLK1_M2C_P" : "X",
        #"GBTCLK1_M2C_N" : "X",
        "GBTCLK0_M2C_P" : "L8", # refclk7
        "GBTCLK0_M2C_N" : "L7", # refclk7
        "LA01_CC_P"     : "B:130",
        "LA01_CC_N"     : "B:132",
        "LA05_P"        : "B:142",
        "LA05_N"        : "B:144",
        "LA09_P"        : "B:114",
        "LA09_N"        : "B:116",
        "LA13_P"        : "B:94",
        "LA13_N"        : "B:96",
        "LA17_CC_P"     : "B:151",
        "LA17_CC_N"     : "B:153",
        "LA23_P"        : "B:133",
        "LA23_N"        : "B:135",
        #"LA26_P"        : "B:111",
        #"LA26_N"        : "B:113",
        #"PG_M2C"        : "",
        "HA00_CC_P"     : "C:148",
        "HA00_CC_N"     : "C:150",
        "HA04_P"        : "C:160",
        "HA04_N"        : "C:162",
        "HA08_P"        : "C:142",
        "HA08_N"        : "C:144",
        #"HA12_P"        : "C:132",
        #"HA12_N"        : "C:134",
        #"HA15_P"        : "C:125",
        #"HA15_N"        : "C:127",
        #"HA19_P"        : "C:119",
        #"HA19_N"        : "C:121",
        "PRSNT_M2C_B"   : "",
        "CLK0_M2C_P"    : "B:78",
        "CLK0_M2C_N"    : "B:80",
        "LA02_P"        : "B:164",
        "LA02_N"        : "B:166",
        "LA04_P"        : "B:148",
        "LA04_N"        : "B:150",
        "LA07_P"        : "B:124",
        "LA07_N"        : "B:126",
        "LA11_P"        : "B:104",
        "LA11_N"        : "B:106",
        "LA15_P"        : "B:84",
        "LA15_N"        : "B:86",
        "LA19_P"        : "B:163",
        "LA19_N"        : "B:165",
        "LA21_P"        : "B:145",
        "LA21_N"        : "B:147",
        "LA24_P"        : "B:129",
        "LA24_N"        : "B:131",
        #"LA28_P"        : "B:101",
        #"LA28_N"        : "B:103",
        #"LA30_P"        : "B:91",
        #"LA30_N"        : "B:93",
        #"LA32_P"        : "B:81",
        #"LA32_N"        : "B:83",
        "HA02_P"        : "C:164",
        "HA02_N"        : "C:166",
        "HA06_P"        : "C:154",
        "HA06_N"        : "C:156",
        #"HA10_P"        : "C:138",
        #"HA10_N"        : "C:140",
        #"HA17_CC_P"     : "C:122",
        #"HA17_CC_N"     : "C:124",
        #"HA21_P"        : "C:109",
        #"HA21_N"        : "C:111",
        #"HA23_P"        : "C:105",
        #"HA23_N"        : "C:107",
    })
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxUSPPlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self, toolchain="vivado"):
        XilinxUSPPlatform.__init__(self, "xczu7ev-fbvb900-2-i", _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment):
        XilinxUSPPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100",     loose=True), 1e9/100e6)
        self.add_period_constraint(self.lookup_request("clk33",      loose=True), 1e9/33e6)
        self.add_platform_command("set_property BITSTREAM.CONFIG.OVERTEMPSHUTDOWN ENABLE [current_design]")
        self.add_platform_command("set_property BITSTREAM.CONFIG.UNUSEDPIN PULLNONE [current_design]")
        self.add_platform_command("set_property INTERNAL_VREF 0.600 [get_iobanks 64]")
