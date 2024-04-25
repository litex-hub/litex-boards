#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2024 Gwenhael Goavec-Merou <gwenhael@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform, VivadoProgrammer
from litex.build.openfpgaloader import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst.
    ("clk200", 0,
        Subsignal("p", Pins("H9"), IOStandard("LVDS")),
        Subsignal("n", Pins("G9"), IOStandard("LVDS")),
    ),
    ("usrclk", 0,
        Subsignal("p", Pins("AF14"), IOStandard("LVDS_25")),
        Subsignal("n", Pins("AG14"), IOStandard("LVDS_25")),
    ),
    ("cpu_reset", 0, Pins("A8"), IOStandard("LVCMOS15")),

    # Leds.
    ("user_led", 0, Pins("Y21"), IOStandard("LVCMOS25")),
    ("user_led", 1, Pins("G2"),  IOStandard("LVCMOS15")),
    ("user_led", 2, Pins("W21"), IOStandard("LVCMOS25")),
    ("user_led", 3, Pins("A17"), IOStandard("LVCMOS15")),

    # Buttons.
    ("user_btn_l", 0, Pins("AK25"), IOStandard("LVCMOS25")),
    ("user_btn_c", 0, Pins("K15"),  IOStandard("LVCMOS15")),
    ("user_btn_r", 0, Pins("R27"),  IOStandard("LVCMOS25")),

    # Switches.
    ("user_dip_btn", 0, Pins("AB17"), IOStandard("LVCMOS25")),
    ("user_dip_btn", 1, Pins("AC16"), IOStandard("LVCMOS25")),
    ("user_dip_btn", 2, Pins("AC17"), IOStandard("LVCMOS25")),
    ("user_dip_btn", 3, Pins("AJ13"), IOStandard("LVCMOS25")),

    # SMA.
    ("user_sma_clock", 0,
        Subsignal("p", Pins("AD18")),
        Subsignal("n", Pins("AD19")),
        IOStandard("LVDS_25"),
        Misc("DIFF_TERM=TRUE")
    ),
    ("user_sma_clock_p", Pins("AD18"), IOStandard("LVCMOS25")),
    ("user_sma_clock_n", Pins("AD19"), IOStandard("LVCMOS25")),

    # FAN.
    ("fan", 0,
        Subsignal("tach",  Pins("AA19")),
        Subsignal("pwm_n", Pins("AB19")),
        IOStandard("LVCMOS18")
    ),

    # I2C (SI570, SFP, HDMI, EEPROM, ...)
    ("i2c", 0,
        Subsignal("scl", Pins("AJ14"), Misc("PULLUP=True")),
        Subsignal("sda", Pins("AJ18"), Misc("PULLUP=True")),
        IOStandard("LVCMOS25")
    ),

    # DDR3 SDRAM.
    ("ddram", 0,
        Subsignal("a", Pins(
            "E10 B9 E11 A9 D11  B6  F9 E8",
            "B10 J8 D6  B7 H12 A10 G11 C6"),
            IOStandard("SSTL15")),
        Subsignal("ba",      Pins("F8 H7 A7"), IOStandard("SSTL15")),
        Subsignal("ras_n",   Pins("H11"), IOStandard("SSTL15")),
        Subsignal("cas_n",   Pins("E7"),  IOStandard("SSTL15")),
        Subsignal("we_n",    Pins("F7"),  IOStandard("SSTL15")),
        Subsignal("cs_n",    Pins("J11"), IOStandard("SSTL15")), # J11 H8
        Subsignal("dm",      Pins(
            "J3 F2 E1 C2 L12 G14 C16 C11"),
            IOStandard("SSTL15")),
        Subsignal("dq",      Pins(
            " L1  L2  K5  J4  K1  L3  J5  K6",
            " G6  H4  H6  H3  G1  H2  G5  G4",
            " E2  E3  D4  E5  F4  F3  D1  D3",
            " A2  B2  B4  B5  A3  B1  C1  C4",
            "K10  L9 K12  J9 K11 L10 J10  L7",
            "F14 F15 F13 G16 G15 E12 D13 E13",
            "D15 E15 D16 E16 C17 B16 D14 B17",
            "B12 C12 A12 A14 A13 B11 C14 B14"),
            IOStandard("SSTL15_T_DCI")),
        Subsignal("dqs_p",   Pins("K3 J1 E6 A5 L8 G12 F17 B15"),
            IOStandard("DIFF_SSTL15")),
        Subsignal("dqs_n",   Pins("K2 H1 D5 A4 K8 F12 E17 A15"),
            IOStandard("DIFF_SSTL15")),
        Subsignal("clk_p",   Pins("G10"), IOStandard("DIFF_SSTL15")), # G10 D9
        Subsignal("clk_n",   Pins("F10"), IOStandard("DIFF_SSTL15")), # F10 D8
        Subsignal("cke",     Pins("D10"), IOStandard("SSTL15")),      # D10 C7
        Subsignal("odt",     Pins("G7"),  IOStandard("SSTL15")),      # G7 C9
        Subsignal("reset_n", Pins("G17"), IOStandard("LVCMOS15")),
        Misc("SLEW=FAST"),
        Misc("VCCAUX_IO=HIGH")
    ),

    # PCIe.
    ("pcie_x1", 0,
        Subsignal("rst_n",  Pins("AK23"), IOStandard("LVCMOS25")),
        Subsignal("wake_n", Pins("AK22"), IOStandard("LVCMOS25")),
        Subsignal("clk_p",  Pins("N8")),
        Subsignal("clk_n",  Pins("N7")),
        Subsignal("tx_p",   Pins("N4")),
        Subsignal("tx_n",   Pins("N3")),
        Subsignal("rx_p",   Pins("P6")),
        Subsignal("rx_n",   Pins("P5")),
    ),
    ("pcie_x2", 0,
        Subsignal("rst_n",  Pins("AK23"), IOStandard("LVCMOS25")),
        Subsignal("wake_n", Pins("AK22"), IOStandard("LVCMOS25")),
        Subsignal("clk_p",  Pins("N8")),
        Subsignal("clk_n",  Pins("N7")),
        Subsignal("tx_p",   Pins("N4 P2")),
        Subsignal("tx_n",   Pins("N3 P1")),
        Subsignal("rx_p",   Pins("P6 T6")),
        Subsignal("rx_n",   Pins("P5 T5")),
    ),
    ("pcie_x4", 0,
        Subsignal("rst_n",  Pins("AK23"), IOStandard("LVCMOS25")),
        Subsignal("wake_n", Pins("AK22"), IOStandard("LVCMOS25")),
        Subsignal("clk_p",  Pins("N8")),
        Subsignal("clk_n",  Pins("N7")),
        Subsignal("tx_p",   Pins("N4 P2 R4 T2")),
        Subsignal("tx_n",   Pins("N3 P1 R3 T1")),
        Subsignal("rx_p",   Pins("P6 T6 U4 V6")),
        Subsignal("rx_n",   Pins("P5 T5 U3 V5")),
    ),

    # SMA.
    ("user_sma_mgt_refclk", 0,
        Subsignal("p", Pins("W7")),
        Subsignal("n", Pins("W8"))
    ),
    ("user_sma_mgt_tx", 0,
        Subsignal("p", Pins("Y2")),
        Subsignal("n", Pins("Y1"))
    ),
    ("user_sma_mgt_rx", 0,
        Subsignal("p", Pins("AB6")),
        Subsignal("n", Pins("AB5"))
    ),

    # SFP.
    ("sfp_tx_disable_n", 0, Pins("AA18"), IOStandard("LVCMOS25")),
    ("sfp", 0,
        Subsignal("txp", Pins("W4")),
        Subsignal("txn", Pins("W3")),
        Subsignal("rxp", Pins("Y6")),
        Subsignal("rxn", Pins("Y5")),
    ),
    ("sfp_tx", 0,
        Subsignal("p", Pins("W4")),
        Subsignal("n", Pins("W3")),
    ),
    ("sfp_rx", 0,
        Subsignal("p", Pins("Y6")),
        Subsignal("n", Pins("Y5")),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("pmod1", "AJ21 AK21 AB21 AB16 Y20 AA20 AC18 AC19"),
    ("HPC", {
        # A
        "DP1_M2C_P"       : "AJ8",
        "DP1_M2C_N"       : "AJ7",
        "DP2_M2C_P"       : "AG8",
        "DP2_M2C_N"       : "AG7",
        "DP3_M2C_P"       : "AE8",
        "DP3_M2C_N"       : "AE7",
        "DP4_M2C_P"       : "AH6",
        "DP4_M2C_N"       : "AH5",
        "DP5_M2C_P"       : "AG4",
        "DP5_M2C_N"       : "AG3",
        "DP1_C2M_P"       : "AK6",
        "DP1_C2M_N"       : "AK5",
        "DP2_C2M_P"       : "AJ4",
        "DP2_C2M_N"       : "AJ3",
        "DP3_C2M_P"       : "AK2",
        "DP3_C2M_N"       : "AK1",
        "DP4_C2M_P"       : "AH2",
        "DP4_C2M_N"       : "AH1",
        "DP5_C2M_P"       : "AF2",
        "DP5_C2M_N"       : "AF1",
        # B
        "DP7_M2C_P"       : "AD6",
        "DP7_M2C_N"       : "AD5",
        "DP6_M2C_P"       : "AF6",
        "DP6_M2C_N"       : "AF5",
        "GBTCLK1_M2C_C_P" : "AA8",
        "GBTCLK1_M2C_C_N" : "AA7",
        "DP7_C2M_P"       : "AD2",
        "DP7_C2M_N"       : "AD1",
        "DP6_C2M_P"       : "AE4",
        "DP6_C2M_N"       : "AE3",
        # C
        "DP0_C2M_P"       : "AK10",
        "DP0_C2M_N"       : "AK9",
        "DP0_M2C_P"       : "AH10",
        "DP0_M2C_N"       : "AH9",
        "LA06_P"          : "AG22",
        "LA06_N"          : "AH22",
        "LA10_P"          : "AG24",
        "LA10_N"          : "AG25",
        "LA14_P"          : "AC24",
        "LA14_N"          : "AD24",
        "LA18_CC_P"       : "W25",
        "LA18_CC_N"       : "W26",
        "LA27_P"          : "V28",
        "LA27_N"          : "V29",
        # C
        "GBTCLK0_M2C_C_P" : "AD10",
        "GBTCLK0_M2C_C_N" : "AD9",
        "LA01_CC_P"       : "AG21",
        "LA01_CC_N"       : "AH21",
        "LA05_P"          : "AH23",
        "LA05_N"          : "AH24",
        "LA09_P"          : "AD21",
        "LA09_N"          : "AE21",
        "LA13_P"          : "AA22",
        "LA13_N"          : "AA23",
        "LA17_CC_P"       : "V23",
        "LA17_CC_N"       : "W24",
        "LA23_P"          : "P25",
        "LA23_N"          : "P26",
        "LA26_P"          : "R28",
        "LA26_N"          : "T28",
        # G
        "CLK1_M2C_P"      : "U26",
        "CLK1_M2C_N"      : "U27",
        "LA00_CC_P"       : "AF20",
        "LA00_CC_N"       : "AG20",
        "LA03_P"          : "AH19",
        "LA03_N"          : "AJ19",
        "LA08_P"          : "AF19",
        "LA08_N"          : "AG19",
        "LA12_P"          : "AF23",
        "LA12_N"          : "AF24",
        "LA16_P"          : "AA24",
        "LA16_N"          : "AB24",
        "LA20_P"          : "U25",
        "LA20_N"          : "V26",
        "LA22_P"          : "V27",
        "LA22_N"          : "W28",
        "LA25_P"          : "T29",
        "LA25_N"          : "U29",
        "LA29_P"          : "R25",
        "LA29_N"          : "R26",
        "LA31_P"          : "N29",
        "LA31_N"          : "P29",
        "LA33_P"          : "N26",
        "LA33_N"          : "N27",
        # H
        "CLK0_M2C_P"      : "AE22",
        "CLK0_M2C_N"      : "AF22",
        "LA02_P"          : "AK17",
        "LA02_N"          : "AK18",
        "LA04_P"          : "AJ20",
        "LA04_N"          : "AK20",
        "LA07_P"          : "AJ23",
        "LA07_N"          : "AJ24",
        "LA11_P"          : "AD23",
        "LA11_N"          : "AE23",
        "LA15_P"          : "Y22",
        "LA15_N"          : "Y23",
        "LA19_P"          : "T24",
        "LA19_N"          : "T25",
        "LA21_P"          : "W29",
        "LA21_N"          : "W30",
        "LA24_P"          : "T30",
        "LA24_N"          : "U30",
        "LA28_P"          : "P30",
        "LA28_N"          : "R30",
        "LA30_P"          : "P23",
        "LA30_N"          : "P24",
        "LA32_P"          : "P21",
        "LA32_N"          : "R21",
        }
    ),
    ("LPC", {
        # C
        "DP0_C2M_P"       : "AB2",
        "DP0_C2M_N"       : "AB1",
        "DP0_M2C_P"       : "AC4",
        "DP0_M2C_N"       : "AC3",
        "LA06_P"          : "AB12",
        "LA06_N"          : "AC12",
        "LA10_P"          : "AC14",
        "LA10_N"          : "AC13",
        "LA14_P"          : "AF18",
        "LA14_N"          : "AF17",
        "LA18_CC_P"       : "AE27",
        "LA18_CC_N"       : "AF27",
        "LA27_P"          : "AJ28",
        "LA27_N"          : "AJ29",
        # D
        "GBTCLK0_M2C_C_P" : "U8",
        "GBTCLK0_M2C_C_N" : "U7",
        "LA01_CC_P"       : "AF15",
        "LA01_CC_N"       : "AG15",
        "LA05_P"          : "AE16",
        "LA05_N"          : "AE15",
        "LA09_P"          : "AH14",
        "LA09_N"          : "AH13",
        "LA13_P"          : "AH17",
        "LA13_N"          : "AH16",
        "LA17_CC_P"       : "AB27",
        "LA17_CC_N"       : "AC27",
        "LA23_P"          : "AJ26",
        "LA23_N"          : "AK26",
        "LA26_P"          : "AJ30",
        "LA26_N"          : "AK30",
        # G
        "CLK1_M2C_P"      : "AC28",
        "CLK1_M2C_N"      : "AD28",
        "LA00_CC_P"       : "AE13",
        "LA00_CC_N"       : "AF13",
        "LA03_P"          : "AG12",
        "LA03_N"          : "AH12",
        "LA08_P"          : "AD14",
        "LA08_N"          : "AD13",
        "LA12_P"          : "AD16",
        "LA12_N"          : "AD15",
        "LA16_P"          : "AE18",
        "LA16_N"          : "AE17",
        "LA20_P"          : "AG26",
        "LA20_N"          : "AG27",
        "LA22_P"          : "AK27",
        "LA22_N"          : "AK28",
        "LA25_P"          : "AF29",
        "LA25_N"          : "AG29",
        "LA29_P"          : "AE25",
        "LA29_N"          : "AF25",
        "LA31_P"          : "AC29",
        "LA31_N"          : "AD29",
        "LA33_P"          : "Y30",
        "LA33_N"          : "AA30",
        # H
        "CLK0_M2C_P"      : "AG17",
        "CLK0_M2C_N"      : "AG16",
        "LA02_P"          : "AE12",
        "LA02_N"          : "AF12",
        "LA04_P"          : "AJ15",
        "LA04_N"          : "AK15",
        "LA07_P"          : "AA15",
        "LA07_N"          : "AA14",
        "LA11_P"          : "AJ16",
        "LA11_N"          : "AK16",
        "LA15_P"          : "AB15",
        "LA15_N"          : "AB14",
        "LA19_P"          : "AH26",
        "LA19_N"          : "AH27",
        "LA21_P"          : "AH28",
        "LA21_N"          : "AH29",
        "LA24_P"          : "AF30",
        "LA24_N"          : "AG30",
        "LA28_P"          : "AD25",
        "LA28_N"          : "AE26",
        "LA30_P"          : "AB29",
        "LA30_N"          : "AB30",
        "LA32_P"          : "Y26",
        "LA32_N"          : "Y27",
        }
    ),
    ("XADC", {
        "AD1_R_N"  : "K13",
        "AD1_R_P"  : "L13",
        "GPIO_0"   : "H14",
        "GPIO_1"   : "J15",
        "GPIO_2"   : "J16",
        "GPIO_3"   : "J14",
        "VAUX0N_R" : "L14",
        "VAUX0P_R" : "L15",
        "VAUX8N_R" : "H13",
        "VAUX8P_R" : "J13",
        }
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk200"
    default_clk_period = 1e9/200e6

    def __init__(self, toolchain="vivado"):
        Xilinx7SeriesPlatform.__init__(self, "xc7z045ffg900-2", _io,  _connectors, toolchain=toolchain)

    def create_programmer(self, name='vivado'):
        if name == 'vivado':
            return VivadoProgrammer()
        else:
            return OpenFPGALoader("zc706")

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk200", loose=True), 1e9/200e6)
        self.add_platform_command("set_property DCI_CASCADE {{34}} [get_iobanks 33]")
