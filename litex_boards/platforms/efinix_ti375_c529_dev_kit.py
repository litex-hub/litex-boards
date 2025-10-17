#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2024 Dolu1990 <charles.papon.90@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.efinix.platform import EfinixPlatform
from litex.build.efinix import EfinixProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk
    ("clk25",  0, Pins("L17"), IOStandard("1.8_V_LVCMOS")),
    ("clk100", 0, Pins("U4"), IOStandard("3.3_V_LVCMOS")),
    ("clketh", 0, Pins("A14"), IOStandard("1.8_V_LVCMOS")),

    # Serial.
    ("serial", 0,
        Subsignal("tx", Pins(" E9")),
        Subsignal("rx", Pins("E10")),
        IOStandard("3.3_V_LVTTL"),
        Misc("WEAK_PULLUP"),
    ),

    # Buttons.
    ("user_btn", 0, Pins("U19"), IOStandard("3.3_V_LVCMOS")),

    # DRAM.
    ("dram_pll_refclk", 0, Pins("XXX"), IOStandard("3.3_V_LVTTL_/_LVCMOS")),

    # SDCard.
    ("spisdcard", 0,
        Subsignal("clk",  Pins(" C9")),
        Subsignal("mosi", Pins("C10")),
        Subsignal("cs_n", Pins(" A9")),
        Subsignal("miso", Pins(" B9")),
        IOStandard("3.3_V_LVCMOS"),
    ),
    ("sdcard", 0,
        Subsignal("data", Pins("B9 B10 A8 A9")),
        Subsignal("cmd",  Pins("C10")),
        Subsignal("clk",  Pins("C9")) , #, Misc("SLEWRATE=1"), Misc("DRIVE_STRENGTH=16")
        IOStandard("3.3_V_LVTTL"),
    ),

    ("emmc", 0,
        Subsignal("data", Pins("J18 C15 D18 C18 F18 E18 B15 B16")),
        Subsignal("cmd",  Pins("G19")),
        Subsignal("clk",  Pins("F19")), #, Misc("SLEWRATE=1"), Misc("DRIVE_STRENGTH=16")
        IOStandard("1.8_V_LVCMOS"),
    ),

    # ETH.
    ("eth_clocks", 0,
        Subsignal("tx", Pins("C17")),
        Subsignal("rx", Pins("D15")),
        IOStandard("1.8_V_LVCMOS"),
        Misc("SLEWRATE=1"),
        Misc("DRIVE_STRENGTH=16")
     ),
    ("eth", 0,
        Subsignal("rst_n", Pins("D10"), IOStandard("3.3_V_LVCMOS")),
        Subsignal("int_n", Pins("B11"), IOStandard("3.3_V_LVCMOS")),
        Subsignal("mdio", Pins("B14")),
        Subsignal("mdc", Pins("B19")),
        Subsignal("rx_ctl", Pins("H18")),
        Subsignal("rx_data", Pins("A18 A19 D16 D17")),
        Subsignal("tx_ctl", Pins("B20")),
        Subsignal("tx_data", Pins("B17 A16 A17 C19")),
        IOStandard("1.8_V_LVCMOS"),
        Misc("SLEWRATE=1"),
        Misc("DRIVE_STRENGTH=16")
     ),

    # SPIFlash
    # both flashes are connected to the same clk pin, so only one can be used at a time.
    ("spiflash", 0,
        Subsignal("cs_n", Pins("A7")),
        Subsignal("clk", Pins("G6")),
        Subsignal("mosi", Pins("H4")),
        Subsignal("miso", Pins("H5")),
        IOStandard("1.8_V_LVCMOS")
    ),
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("A7")),
        Subsignal("clk", Pins("G6")),
        Subsignal("dq", Pins("H4 H5 G5 B7")),
        IOStandard("1.8_V_LVCMOS")
    ),

    # SPIFlash
    ("spiflash", 1,
        Subsignal("cs_n", Pins("A2")),
        Subsignal("clk", Pins("G6")),
        Subsignal("mosi", Pins("D5")),
        Subsignal("miso", Pins("D6")),
        IOStandard("1.8_V_LVCMOS")
    ),
    ("spiflash4x", 1,
        Subsignal("cs_n", Pins("L4")),
        Subsignal("clk", Pins("G6")),
        Subsignal("dq", Pins("D5 D6 E4 E5")),
        IOStandard("1.8_V_LVCMOS")
    ),

    # FAN.
    ("fan_speed_control", 0, Pins("T19"), IOStandard("3.3_V_LVCMOS")),

    # Leds
    ("user_led", 0, Pins("R20")),
    ("user_led", 1, Pins("V4"), IOStandard("3.3_V_LVCMOS")),
    ("user_led", 2, Pins("U6"), IOStandard("3.3_V_LVCMOS")),
    ("user_led", 3, Pins("L18")),
    ("user_led", 4, Pins("E19")),
]

    

# Bank voltage ---------------------------------------------------------------------------------------

_bank_info = [
            ("2A"      , "1.8 V LVCMOS"), # is_dyn_voltage="false" mode_sel_name="2A_MODE_SEL"/>
            ("2B"      , "1.8 V LVCMOS"), # is_dyn_voltage="false" mode_sel_name="2B_MODE_SEL"/>
            ("2C"      , "1.8 V LVCMOS"), # is_dyn_voltage="false" mode_sel_name="2C_MODE_SEL"/>
            ("2D"      , "1.8 V LVCMOS"), # is_dyn_voltage="false" mode_sel_name="2D_MODE_SEL"/>
            ("2E"      , "1.8 V LVCMOS"), # is_dyn_voltage="false" mode_sel_name="2E_MODE_SEL"/>
            ("4A_4B"   , "1.8 V LVCMOS"), # is_dyn_voltage="false" mode_sel_name="4A_4B_MODE_SEL"/>
            ("4C"      , "1.8 V LVCMOS"), # is_dyn_voltage="false" mode_sel_name="4C_MODE_SEL"/>
            ("4D"      , "1.8 V LVCMOS"), # is_dyn_voltage="false" mode_sel_name="4D_MODE_SEL"/>
            ("BL2_BL3" , "3.3 V LVCMOS"), # is_dyn_voltage="false">
            ("BR0"     , "3.3 V LVCMOS"), # is_dyn_voltage="false" mode_sel_name="BR0_MODE_SEL"/>
            ("BR3_BR4" , "3.3 V LVCMOS"), # is_dyn_voltage="false">
            ("TL1_TL5" , "3.3 V LVCMOS"), # is_dyn_voltage="false">
            ("TR0"     , "3.3 V LVCMOS"), # is_dyn_voltage="false" mode_sel_name="TR0_MODE_SEL"/>
            ("TR1"     , "3.3 V LVCMOS"), # is_dyn_voltage="false" mode_sel_name="TR1_MODE_SEL"/>
            ("TR2"     , "3.3 V LVCMOS"), # is_dyn_voltage="false" mode_sel_name="TR2_MODE_SEL"/>
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("pmod0", "G15 G16 F16 F17 G17 A11 A13 A12"),
    ("pmod1", "B12 C14 C13 C12 D12 F12 D13 E13"),
    ("pmod2", "E14 E16 F13 E15 F14 E11 F11 D11"),
    ["p1",
        "---", # 0
        # 3V3      5V     GND GND                 GND GND                 GND GND         ↓
        "--- B21 --- A21 --- --- C22 E21 B22 D21 --- --- B23 F21 A22 F22 --- --- D22 G21",
        #  1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17  18  19  20  ↑
        # 21  22  23  24  25  26  27  28  28  30  31  32  33  34  35  36  37  38  39  40  ↓
        "D23 G22 --- --- F23 H20 E23 G20 --- --- H22 K23 H23 L23 --- --- L19 M21 M19 M22",
        #        GND GND                 GND GND                 GND GND                  ↑
    ],
    ("LPC", {
        "PRSNT_M2C_L"   :  "K5", # FMC_PRESENT_n / GPIOB_P_26_EXTSPICLK

        "CLK0_M2C_P"    : "N17", # FMC_M2C_CLK2_P / GPIOT_P_40_CLK23_P
        "CLK0_M2C_N"    : "N18", # FMC_M2C_CLK2_N / GPIOT_N_40_CLK23_N
        "CLK1_M2C_P"    :  "F2", # FMC_M2C_CLK1_P / GPIOB_P_17_CLK4_P
        "CLK1_M2C_N"    :  "G2", # FMC_M2C_CLK1_N / GPIOB_N_17_CLK4_N

        "DP0_M2C_P"     :  "A4", # GPIOB32_TO_FMC_P_P0CTL4 / GPIOB_P_32
        "DP0_M2C_N"     :  "A3", # GPIOB32_TO_FMC_N_P1CTL4 / GPIOB_N_32

        "LA00_CC_P"     :  "D1", # FMC_GLOBAL_CLK_4_P / GPIOB_P_20_CLK7_P
        "LA00_CC_N"     :  "D2", # FMC_GLOBAL_CLK_4_N / GPIOB_N_20_CLK7_N
        "LA01_CC_P"     :  "E8", # FMC_GLOBAL_CLK_2_P / GPIOB_P_44_CLK11_P
        "LA01_CC_N"     :  "D8", # FMC_GLOBAL_CLK_2_N / GPIOB_N_44_CLK11_N
        "LA02_P"        :  "B6", # GPIOB35_TO_FMC_P / GPIOB_P_35
        "LA02_N"        :  "A6", # GPIOB35_TO_FMC_N / GPIOB_N_35
        "LA03_P"        :  "C3", # GPIOB27_TO_FMC_P / GPIOB_P_27
        "LA03_N"        :  "D3", # GPIOB27_TO_FMC_N / GPIOB_N_27
        "LA04_P"        :  "B1", # GPIOB21_TO_FMC_P / GPIOB_P_21
        "LA04_N"        :  "C2", # GPIOB21_TO_FMC_N / GPIOB_N_21
        "LA05_P"        :  "D7", # GPIOB41_TO_FMC_P / GPIOB_P_41
        "LA05_N"        :  "C7", # GPIOB41_TO_FMC_N / GPIOB_N_41
        "LA06_P"        :  "C5", # GPIOB34_TO_FMC_P / GPIOB_P_34
        "LA06_N"        :  "B5", # GPIOB34_TO_FMC_N / GPIOB_N_34
        "LA07_P"        :  "E1", # GPIOB18_TO_FMC_P / GPIOB_P_18_CLK5_P
        "LA07_N"        :  "F1", # GPIOB18_TO_FMC_N / GPIOB_N_18_CLK5_N
        "LA08_P"        :  "C4", # GPIOB31_TO_FMC_P / GPIOB_P_31
        "LA08_N"        :  "B4", # GPIOB31_TO_FMC_N / GPIOB_N_31
        "LA09_P"        :  "F6", # GPIOB42_TO_FMC_P / GPIOB_P_42
        "LA09_N"        :  "E6", # GPIOB42_TO_FMC_N / GPIOB_N_42
        "LA10_P"        :  "A2", # GPIOB30_TO_FMC_P / GPIOB_P_30_CDI9_PLLIN0
        "LA10_N"        :  "B2", # GPIOB30_TO_FMC_N / GPIOB_N_30_CDI8
        "LA11_P"        :  "J1", # GPIOB19_TO_FMC_P / GPIOB_P_19_NSTATUS_CLK6_P
        "LA11_N"        :  "J2", # GPIOB19_TO_FMC_N / GPIOB_N_19_TEST_N_CLK6_N
        "LA12_P"        :  "G1", # GPIOB23_TO_FMC_P / GPIOB_P_23_CBSEL1
        "LA12_N"        :  "H2", # GPIOB23_TO_FMC_N / GPIOB_N_23_CBSEL0
        "LA13_P"        :  "E3", # GPIOB24_TO_FMC_P / GPIOB_P_24_CDI15
        "LA13_N"        :  "F3", # GPIOB24_TO_FMC_N / GPIOB_N_24_CDI14
        "LA14_P"        :  "K3", # GPIOB29_TO_FMC_P / GPIOB_P_29_CDI11_EXTFB
        "LA14_N"        :  "K4", # GPIOB29_TO_FMC_N / GPIOB_N_29_CDI10
        "LA15_P"        :  "P5", # GPIOB06_TO_FMC_P / GPIOB_P_06_CDI26_EXTFB
        "LA15_N"        :  "R5", # GPIOB06_TO_FMC_N / GPIOB_N_06_CDI25
        "LA16_P"        :  "L3", # GPIOB11_TO_FMC_P / GPIOB_P_11
        "LA16_N"        :  "M4", # GPIOB11_TO_FMC_N / GPIOB_N_11
        "LA17_CC_P"     :  "N3", # FMC_GLOBAL_CLK_3_P_FMC_P0SDA / GPIOB_P_13_CDI21_CLK0_P
        "LA17_CC_N"     :  "P3", # FMC_GLOBAL_CLK_3_N_FMC_P0SCL / GPIOB_N_13_CDI20_CLK0_N
        "LA18_CC_P"     :  "L2", # FMC_GLOBAL_CLK_1_P_FMC_SPI_SCK / GPIOB_P_15_CDI17_CLK2_P
        "LA18_CC_N"     :  "M2", # FMC_GLOBAL_CLK_1_N_FMC_FPGA_SSN / GPIOB_N_15_CDI16_CLK2_N
        "LA19_P"        :  "K6", # GPIOB25_TO_FMC_P_FMCSPI_nCS0 / GPIOB_P_25_CDI13
        "LA19_N"        :  "L6", # GPIOB25_TO_FMC_N_FMCSPI_nCS1 / GPIOB_N_25_CDI12
        "LA20_P"        :  "G4", # GPIOB33_TO_FMC_P_FMC_P1SDA / GPIOB_P_33
        "LA20_N"        :  "F4", # GPIOB33_TO_FMC_N_FMC_P1SCL / GPIOB_N_33
        "LA21_P"        :  "H3", # GPIOB28_TO_FMC_P_P1CTL1_CDONE / GPIOB_P_28
        "LA21_N"        :  "J3", # GPIOB28_TO_FMC_N_P1CTL0_INIT_RST_N / GPIOB_N_28
        "LA22_P"        :  "M5", # GPIOB22_TO_FMC_P_P0CTL0 / GPIOB_P_22
        "LA22_N"        :  "M6", # GPIOB22_TO_FMC_N_P0CTL1 / GPIOB_N_22
        "LA23_P"        :  "K1", # GPIOB14_TO_FMC_P / GPIOB_P_14_CDI19_CLK1_P
        "LA23_N"        :  "L1", # GPIOB14_TO_FMC_N / GPIOB_N_14_CDI18_CLK1_N
        "LA24_P"        :  "J6", # GPIOB43_TO_FMC_P_P1CTL3 / GPIOB_P_43_CSO_CLK10_P
        "LA24_N"        :  "J5", # GPIOB43_TO_FMC_N_P1CTL2_PROG_N / GPIOB_N_43_CSI_CLK10_N
        "LA25_P"        :  "N7", # GPIOB08_TO_FMC_P_P0CTL2 / GPIOB_P_08_CDI22_EXTFB
        "LA25_N"        :  "P7", # GPIOB08_TO_FMC_N_P0CTL3 / GPIOB_N_08
        "LA26_P"        :  "N5", # GPIOB12_TO_FMC_P / GPIOB_P_12
        "LA26_N"        :  "N4", # GPIOB12_TO_FMC_N / GPIOB_N_12
        "LA27_P"        :  "M1", # GPIOB09_TO_FMC_P / GPIOB_P_09
        "LA27_N"        :  "N2", # GPIOB09_TO_FMC_N / GPIOB_N_09
        "LA28_P"        :  "P6", # GPIOB05_TO_FMC_P_P1CTL5 / GPIOB_P_05_CDI28_PLLIN0
        "LA28_N"        :  "R6", # GPIOB05_TO_FMC_N_P1CTL6 / GPIOB_N_05_CDI27
        "LA29_P"        :  "T3", # GPIOB10_TO_FMC_P_P0CTL5 / GPIOB_P_10
        "LA29_N"        :  "T2", # GPIOB10_TO_FMC_N_P0CTL6 / GPIOB_N_10
        "LA30_P"        :  "R1", # GPIOB04_TO_FMC_P_FMCSPIDATA3 / GPIOB_P_04_CDI30_EXTFB
        "LA30_N"        :  "T1", # GPIOB04_TO_FMC_N_FMCSPIDATA2 / GPIOB_N_04_CDI29
        "LA31_P"        :  "P2", # GPIOB16_TO_FMC_P_FMCSPIDAT1 / GPIOB_P_16_CLK3_P
        "LA31_N"        :  "P1", # GPIOB16_TO_FMC_N_FMCSPIDAT0 / GPIOB_N_16_CLK3_N
        "LA32_P"        :  "U2", # GPIOB03_TO_FMC_P_FMCSPIDATA7 / GPIOB_P_03_PLLIN0
        "LA32_N"        :  "U1", # GPIOB03_TO_FMC_N_FMCSPIDATA6 / GPIOB_N_03_CDI31
        "LA33_P"        :  "R4", # GPIOB07_TO_FMC_P_FMCSPIDAT5 / GPIOB_P_07_CDI24_PLLIN0
        "LA33_N"        :  "R3", # GPIOB07_TO_FMC_N_FMCSPIDAT4 / GPIOB_N_07_CDI23
        }
    ),
]

# PMODS --------------------------------------------------------------------------------------------

def raw_pmod_io(pmod):
    return [(pmod, 0, Pins(" ".join([f"{pmod}:{i:d}" for i in range(8)])), IOStandard("3.3_V_LVTTL_/_LVCMOS"))]

def jtag_pmod_io(pmod):
    return [
        ("usb_uart", 0,
            Subsignal("tck", Pins(f"{pmod}:0")),
            Subsignal("tdi", Pins(f"{pmod}:1")),
            Subsignal("tdo", Pins(f"{pmod}:2")),
            Subsignal("tms", Pins(f"{pmod}:3")),
            IOStandard("3.3_V_LVCMOS")
        ),
    ]

def hdmi_px(px):
    return [
        ("hdmi_i2c", 0,
            Subsignal("sda", Pins(f"{px}:26")),
            Subsignal("scl", Pins(f"{px}:28")),
            IOStandard("1.8_V_LVCMOS"),
            Misc("WEAK_PULLUP"),
            Misc("SCHMITT_TRIGGER"),
        ),
        ("hdmi_data", 0,
            Subsignal("clk", Pins(f"{px}:4")),
            Subsignal("de", Pins(f"{px}:33")),
            Subsignal("d", Pins(f"{px}:31 {px}:27 {px}:25 {px}:21 {px}:19 {px}:15 {px}:13 {px}:9 {px}:7 {px}:2 {px}:8 {px}:10 {px}:14 {px}:16 {px}:20 {px}:22")),
            IOStandard("1.8_V_LVCMOS")
        ),
        ("hdmi_sync", 0,
            Subsignal("hsync", Pins(f"{px}:37")),
            Subsignal("vsync", Pins(f"{px}:39")),
            IOStandard("1.8_V_LVCMOS")
        ),
    ]

# Platform -----------------------------------------------------------------------------------------

class Platform(EfinixPlatform):
    default_clk_name   = "clk100"
    default_clk_freq   = 100e6
    default_clk_period = 1e9/100e6

    def __init__(self, toolchain="efinity"):
        EfinixPlatform.__init__(self, "Ti375C529C4", _io, _connectors, iobank_info=_bank_info, toolchain=toolchain)

    def create_programmer(self):
        return EfinixProgrammer(family=self.family)

    def do_finalize(self, fragment):
        EfinixPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100", loose=True), 1e9/100e6)
