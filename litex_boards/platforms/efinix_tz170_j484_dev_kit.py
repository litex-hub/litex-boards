#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 Fin Maaß <f.maass@vogl-electronic.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.efinix.platform import EfinixPlatform
from litex.build.efinix import EfinixProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk
    ("clk33", 0, Pins("K17"), IOStandard("3.3_V_LVCMOS")), # PLL_TL2
    ("clk50", 0, Pins("C1"),  IOStandard("1.8_V_LVCMOS")), # PLL_BL1
    ("clk74", 0, Pins("L16"), IOStandard("3.3_V_LVCMOS")), # PLL_TL0

    # Serial.
    ("serial", 0,
        Subsignal("tx", Pins("G10")),
        Subsignal("rx", Pins("F8")),
        IOStandard("3.3_V_LVTTL"),
        Misc("WEAK_PULLUP"),
    ),

    # SPIFlash
    # both flashes are connected to the same clk pin, so only one can be used at a time.
    ("spiflash", 0,
        Subsignal("cs_n", Pins("E2")),
        Subsignal("clk", Pins("J2")),
        Subsignal("mosi", Pins("G2")),
        Subsignal("miso", Pins("H2")),
        IOStandard("1.8_V_LVCMOS")
    ),
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("E2")),
        Subsignal("clk", Pins("J2")),
        Subsignal("dq", Pins("G2 H2 F3 G3")),
        IOStandard("1.8_V_LVCMOS")
    ),

    # SPIFlash
    ("spiflash", 1,
        Subsignal("cs_n", Pins("A2")),
        Subsignal("clk", Pins("J2")),
        Subsignal("mosi", Pins("F5")),
        Subsignal("miso", Pins("E5")),
        IOStandard("1.8_V_LVCMOS")
    ),
    ("spiflash4x", 1,
        Subsignal("cs_n", Pins("A2")),
        Subsignal("clk", Pins("J2")),
        Subsignal("dq", Pins("F5 E5 B5 C5")),
        IOStandard("1.8_V_LVCMOS")
    ),

    # Buttons.
    ("user_btn", 0, Pins("D2"), Misc("WEAK_PULLUP")), # SW3
    ("user_btn", 1, Pins("E4"), Misc("WEAK_PULLUP")), # SW4

    # SDCard.
    ("spisdcard", 0,
        Subsignal("clk",  Pins("F16")),
        Subsignal("mosi", Pins("F17")),
        Subsignal("cs_n", Pins("G17")),
        Subsignal("miso", Pins("G15")),
        IOStandard("3.3_V_LVCMOS"),
    ),
    ("sdcard", 0,
        Subsignal("data", Pins("G15 F15 H15 G17")),
        Subsignal("cmd",  Pins("F17")),
        Subsignal("clk",  Pins("F16")),
        IOStandard("3.3_V_LVTTL"),
    ),

    # Leds
    ("user_led", 0, Pins("E1")), # LED2
    ("user_led", 1, Pins("F1")), # LED3
    ("user_led", 2, Pins("C2")), # LED4
    ("user_led", 3, Pins("E3")), # LED5
    ("user_led", 4, Pins("B1")), # LED6
    ("user_led", 5, Pins("B2")), # LED7
]

    

# Bank voltage ---------------------------------------------------------------------------------------

_bank_info = [
            ("2A_2B_2C", "1.8 V"),
            ("3A"      , "1.8 V"),
            ("3B_3C"   , "1.8 V"),
            ("4A"      , "1.8 V"),
            ("4B"      , "1.8 V"),
            ("4C"      , "1.8 V"),
            ("BL"      , "3.3 V"),
            ("BR"      , "3.3 V"),
            ("TL"      , "3.3 V"),
            ("TR"      , "3.3 V"),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("HPC", {
        "CLK0_M2C_N": "J19",  # GPIOT_N_13_CLK16_N
        "CLK0_M2C_P": "H19",  # GPIOT_P_13_CLK16_P
        "CLK1_M2C_N": "C21",  # GPIOT_N_20_CLK23_N
        "CLK1_M2C_P": "C22",  # GPIOT_P_20_CLK23_P
        "HA01_N_CC" : "F21",  # GPIOT_N_14_CLK17_N
        "HA01_P_CC" : "G21",  # GPIOT_P_14_CLK17_P
        "HA05_N"    : "H20",  # GPIOT_N_15_CLK18_N
        "HA05_P"    : "G20",  # GPIOT_P_15_CLK18_P
        "HA09_N"    : "G19",  # GPIOT_N_16_CLK19_N
        "HA09_P"    : "F19",  # GPIOT_P_16_CLK19_P
        "HA13_N"    : "G18",  # GPIOT_N_17_CLK20_N
        "HA13_P"    : "H18",  # GPIOT_P_17_CLK20_P
        "HA16_N"    : "E22",  # GPIOT_N_18_CLK21_N
        "HA16_P"    : "D22",  # GPIOT_P_18_CLK21_P
        "HA20_N"    : "E21",  # GPIOT_N_19_CLK22_N
        "HA20_P"    : "E20",  # GPIOT_P_19_CLK22_P
        "HB03_N"    : "C4",   # GPIOB_N_17_CLK4_N
        "HB03_P"    : "D4",   # GPIOB_P_17_CLK4_P
        "HB05_N"    : "C6",   # GPIOB_N_22_CDI10
        "HB05_P"    : "D6",   # GPIOB_P_22_CDI11
        "HB09_N"    : "A5",   # GPIOB_N_21_CDI8
        "HB09_P"    : "A6",   # GPIOB_P_21_CDI9
        "HB13_N"    : "C5",   # GPIOB_N_20_CDI7_CLK7_N, not connected
        "HB13_P"    : "B5",   # GPIOB_P_20_CDI6_CLK7_P, not connected
        "HB19_N"    : "F5",   # GPIOB_N_19_CDI4_CLK6_N, not connected
        "HB19_P"    : "E5",   # GPIOB_P_19_CDI5_CLK6_P, not connected 
        "HB21_N"    : "G5",   # GPIOB_N_18_CLK5_N
        "HB21_P"    : "G6",   # GPIOB_P_18_CLK5_P
        "LA00_N_CC" : "A13",  # GPIOR_N_16
        "LA00_P_CC" : "A14",  # GPIOR_P_16_PLLIN1
        "LA01_N_CC" : "A19",  # GPIOR_N_31
        "LA01_P_CC" : "A18",  # GPIOR_P_31_PLLIN1
        "LA02_N"    : "C16",  # GPIOR_N_24_CLK11_N
        "LA02_P"    : "D16",  # GPIOR_P_24_CLK11_P
        "LA03_N"    : "E15",  # GPIOR_N_28
        "LA03_P"    : "E16",  # GPIOR_P_28
        "LA04_N"    : "A16",  # GPIOR_N_23_CLK12_N
        "LA04_P"    : "A15",  # GPIOR_P_23_CLK12_P
        "LA05_N"    : "C18",  # GPIOR_N_27_CLK8_N
        "LA05_P"    : "C17",  # GPIOR_P_27_CLK8_P
        "LA06_N"    : "G12",  # GPIOR_N_22_CLK13_N
        "LA06_P"    : "G11",  # GPIOR_P_22_CLK13_P
        "LA07_N"    : "B17",  # GPIOR_N_26_CLK9_N
        "LA07_P"    : "A17",  # GPIOR_P_26_CLK9_P
        "LA08_N"    : "E14",  # GPIOR_N_21_CLK14_N
        "LA08_P"    : "E13",  # GPIOR_P_21_CLK14_P
        "LA09_N"    : "G13",  # GPIOR_N_25_CLK10_N
        "LA09_P"    : "F13",  # GPIOR_P_25_CLK10_P
        "LA10_N"    : "B15",  # GPIOR_N_20_CLK15_N
        "LA10_P"    : "C15",  # GPIOR_P_20_CLK15_P
        "LA11_N"    : "H22",  # GPIOT_N_12
        "LA11_P"    : "G22",  # GPIOT_P_12_EXTFB
        "LA12_N"    : "D14",  # GPIOR_N_19
        "LA12_P"    : "C14",  # GPIOR_P_19
        "LA13_N"    : "A3",   # GPIOB_N_16_CLK3_N
        "LA13_P"    : "A4",   # GPIOB_P_16_EXTSPICLK_CLK3_P
        "LA14_N"    : "C13",  # GPIOR_N_18
        "LA14_P"    : "B13",  # GPIOR_P_18
        "LA15_N"    : "B3",   # GPIOB_N_15_CLK2_N
        "LA15_P"    : "C3",   # GPIOB_P_15_CLK2_P
        "LA16_N"    : "E12",  # GPIOR_N_17
        "LA16_P"    : "E11",  # GPIOR_P_17
        "LA17_N_CC" : "D20",  # GPIOR_N_45
        "LA17_P_CC" : "C20",  # GPIOR_P_45_PLLIN0
        "LA18_N_CC" : "C7",  # GPIOB_N_23_CDI12
        "LA18_P_CC" : "B7",  # GPIOB_P_23_PLLIN0
        "LA19_N"    : "B22",  # GPIOR_N_44
        "LA19_P"    : "B21",  # GPIOR_P_44_EXTFB
        "LA20_N"    : "A9",   # GPIOB_N_28_CDI20
        "LA20_P"    : "A10",  # GPIOB_P_28_CDI21
        "LA21_N"    : "E18",  # GPIOR_N_43
        "LA21_P"    : "D18",  # GPIOR_P_43
        "LA22_N"    : "C8",   # GPIOB_N_27_CDI18
        "LA22_P"    : "D8",   # GPIOB_P_27_CDI19
        "LA23_N"    : "A20",  # GPIOR_N_42
        "LA23_P"    : "A21",  # GPIOR_P_42
        "LA24_N"    : "C9",   # GPIOB_N_26_CDI17
        "LA24_P"    : "B9",   # GPIOB_P_26_CDI16
        "LA25_N"    : "C19",  # GPIOR_N_41
        "LA25_P"    : "B19",  # GPIOR_P_41
        "LA26_N"    : "A7",   # GPIOB_N_25_CDI14
        "LA26_P"    : "A8",   # GPIOB_P_25_CDI15
        "LA27_N"    : "E6",   # GPIOB_N_24_CDI13
        "LA27_P"    : "E7",   # GPIOB_P_24_EXTFB
        "LA28_N"    : "E10",  # GPIOB_N_33_CDI30
        "LA28_P"    : "F10",  # GPIOB_P_33_CDI31
        "LA29_N"    : "C12",  # GPIOB_N_34
        "LA29_P"    : "D12",  # GPIOB_P_34
        "LA30_N"    : "C10",  # GPIOB_N_31_CDI26
        "LA30_P"    : "D10",  # GPIOB_P_31_CDI27
        "LA31_N"    : "A12",  # GPIOB_N_32_CDI29
        "LA31_P"    : "A11",  # GPIOB_P_32_CDI28
        "LA32_N"    : "C11",  # GPIOB_N_29_CDI23
        "LA32_P"    : "B11",  # GPIOB_P_29_CDI22
        "LA33_N"    : "E8",   # GPIOB_N_30_CDI24
        "LA33_P"    : "E9",   # GPIOB_P_30_CDI25
        "SCL"       : "J7",   # GPIOL_00_PLLIN1
        "SDA"       : "K18",  # GPIOL_36_PLLIN1
        }
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(EfinixPlatform):
    default_clk_name   = "clk50"
    default_clk_freq   = 50e6
    default_clk_period = 1e9/50e6

    def __init__(self, toolchain="efinity"):
        EfinixPlatform.__init__(self, "Tz170J484I3", _io, _connectors, iobank_info=_bank_info, toolchain=toolchain, spi_width="4")

    def create_programmer(self):
        return EfinixProgrammer(family=self.family)

    def do_finalize(self, fragment):
        EfinixPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request(self.default_clk_name, loose=True), self.default_clk_period)
