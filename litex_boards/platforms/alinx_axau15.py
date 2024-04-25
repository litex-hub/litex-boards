#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2023 John Simons <jammsimons@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxUSPPlatform
from litex.build.openfpgaloader import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst.
    ("clk200", 0,
        Subsignal("p", Pins("T24"), IOStandard("LVDS")),
        Subsignal("n", Pins("U24"), IOStandard("LVDS"))
    ),

    ("clk156p25", 0,
        Subsignal("p", Pins("T7"), IOStandard("LVDS")),
        Subsignal("n", Pins("T6"), IOStandard("LVDS"))
    ),

    # Buttons.
    ("user_btn", 0, Pins("N26"),  IOStandard("LVCMOS33")),
    ("user_btn", 1, Pins("AA23"), IOStandard("LVCMOS33")),

    # Leds.
    ("user_led", 0, Pins("W21"),  IOStandard("LVCMOS18")),
    ("user_led", 1, Pins("AC16"), IOStandard("LVCMOS18")),

    # Serial.
    ("serial", 0,
        Subsignal("tx", Pins("A13")),
        Subsignal("rx", Pins("A12")),
        IOStandard("LVCMOS33")
    ),

    # SDCard.
    ("sdcard", 0,
        Subsignal("data", Pins("Y22 Y23 W20 W19"), Misc("PULLUP True")),
        Subsignal("cmd",  Pins("AA24"),            Misc("PULLUP True")),
        Subsignal("clk",  Pins("AA25")),
        Subsignal("cd",   Pins("Y25")),
        Misc("SLEW=FAST"),
        IOStandard("LVCMOS18"),
    ),

    # DDR4 SDRAM MT40A512M16.
    ("ddram", 0,
        Subsignal("a", Pins(
            "G25 M26 L25 E26 M25 F22 H26 F24",
            "G26 J23 J25 J24 F25 H24"),
            IOStandard("SSTL12_DCI")),
        Subsignal("ba",      Pins("J26 G22"), IOStandard("SSTL12_DCI")),
        Subsignal("bg",      Pins("L22"), IOStandard("SSTL12_DCI")),
        Subsignal("ras_n",   Pins("H21"), IOStandard("SSTL12_DCI")), 
        Subsignal("cas_n",   Pins("H22"), IOStandard("SSTL12_DCI")), 
        Subsignal("we_n",    Pins("K26"), IOStandard("SSTL12_DCI")), 
        Subsignal("cs_n",    Pins("H23"), IOStandard("SSTL12_DCI")),
        Subsignal("act_n",   Pins("K25"), IOStandard("SSTL12_DCI")),
        #Subsignal("par",      Pins("L24"), IOStandard("SSTL12_DCI")),
        Subsignal("dm",      Pins("E25 L18"),
            IOStandard("POD12_DCI")),
        Subsignal("dq",      Pins(
            "F23 D25 E23 B26 D24 D26 B25 C26",
            "M20 J20 J19 M21 L20 J21 K20 K21"),
            IOStandard("POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_p",   Pins("D23 M19"),
            IOStandard("DIFF_POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_n",   Pins("C24 L19"),
            IOStandard("DIFF_POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("clk_p",   Pins("K22"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("clk_n",   Pins("K23"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("cke",     Pins("L23"), IOStandard("SSTL12_DCI")),
        Subsignal("odt",     Pins("M24"), IOStandard("SSTL12_DCI")),
        Subsignal("reset_n", Pins("G24"), IOStandard("LVCMOS12")),
        Misc("SLEW=FAST"),
    ),

    # SPIFlash.
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("AA12")),
        Subsignal("clk",  Pins("Y11")), 
        Subsignal("dq",   Pins("AD11 AC12 AC11 AE11")),
        IOStandard("LVCMOS18")
    ),

    # RGMII Ethernet.
    ("eth_clocks", 0,
        Subsignal("tx", Pins("AE16")),
        Subsignal("rx", Pins("AD21")),
        IOStandard("LVCMOS18")
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("AF23"), IOStandard("LVCMOS18")),
        #Subsignal("int_n",   Pins(""), IOStandard("LVCMOS18")),
        Subsignal("mdio",    Pins("AE18"), IOStandard("LVCMOS18")),
        Subsignal("mdc",     Pins("AF20"), IOStandard("LVCMOS18")),
        Subsignal("rx_ctl",  Pins("AE21"), IOStandard("LVCMOS18")),
        Subsignal("rx_data", Pins("AC22 AC23 AD23 AE23"), IOStandard("LVCMOS18")),
        Subsignal("tx_ctl",  Pins("AD16"), IOStandard("LVCMOS18")),
        Subsignal("tx_data", Pins("Y18 AA18 AB24 AC24"), IOStandard("LVCMOS18")),
    ),

    # PCIe.
    ("pcie_x1", 0,
        Subsignal("rst_n", Pins("T19"), IOStandard("LVCMOS18")),
        Subsignal("clk_p", Pins("AB7")),
        Subsignal("clk_n", Pins("AB6")),
        Subsignal("rx_p",  Pins("AB2")),
        Subsignal("rx_n",  Pins("AB1")),
        Subsignal("tx_p",  Pins("AC5")),
        Subsignal("tx_n",  Pins("AC4"))
    ),
    ("pcie_x2", 0,
        Subsignal("rst_n", Pins("T19"), IOStandard("LVCMOS18")),
        Subsignal("clk_p", Pins("AB7")),
        Subsignal("clk_n", Pins("AB6")),
        Subsignal("rx_p",  Pins("AB2 AD2")),
        Subsignal("rx_n",  Pins("AB1 AD1")),
        Subsignal("tx_p",  Pins("AC5 AD7")),
        Subsignal("tx_n",  Pins("AC4 AD6"))
    ),
    ("pcie_x4", 0,
        Subsignal("rst_n", Pins("T19"), IOStandard("LVCMOS18")),
        Subsignal("clk_p", Pins("AB7")),
        Subsignal("clk_n", Pins("AB6")),
        Subsignal("rx_p",  Pins("AB2 AD2 AE4 AF2")),
        Subsignal("rx_n",  Pins("AB1 AD1 AE3 AF1")),
        Subsignal("tx_p",  Pins("AC5 AD7 AE9 AF7")),
        Subsignal("tx_n",  Pins("AC4 AD6 AE8 AF6"))
    ),
]


# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("HPC", {
        "SCL"           : "V26",
        "SDA"           : "U26",
        "CLK0_N"        : "U25",
        "CLK0_P"        : "T25",
        "CLK1_N"        : "AC21",
        "CLK1_P"        : "AB21",
        "DP0_M2C_P"     : "Y2",
        "DP0_M2C_N"     : "Y1",
        "DP1_M2C_P"     : "V2",
        "DP1_M2C_N"     : "V1",
        "DP2_M2C_P"     : "T2",
        "DP2_M2C_N"     : "T1",
        "DP3_M2C_P"     : "P2",
        "DP3_M2C_N"     : "P1",
        "DP4_M2C_P"     : "M2",
        "DP4_M2C_N"     : "M1",
        "DP5_M2C_P"     : "K2",
        "DP5_M2C_N"     : "K1",
        "DP6_M2C_P"     : "H2",
        "DP6_M2C_N"     : "H1",
        "DP7_M2C_P"     : "F2",
        "DP7_M2C_N"     : "F1",

        "DP0_C2M_P"     : "AA5",
        "DP0_C2M_N"     : "AA4",
        "DP1_C2M_P"     : "W5",
        "DP1_C2M_N"     : "W4",
        "DP2_C2M_P"     : "U5",
        "DP2_C2M_N"     : "U4",
        "DP3_C2M_P"     : "R5",
        "DP3_C2M_N"     : "R4",
        "DP4_C2M_P"     : "N5",
        "DP4_C2M_N"     : "N4",
        "DP5_C2M_P"     : "L5",
        "DP5_C2M_N"     : "L4",
        "DP6_C2M_P"     : "J5",
        "DP6_C2M_N"     : "J4",
        "DP7_C2M_P"     : "G5",
        "DP7_C2M_N"     : "G4",
        
        "LA06_P"        : "N23",
        "LA06_N"        : "P23",
        "LA10_P"        : "W25",
        "LA10_N"        : "W26",
        "LA14_P"        : "U19",
        "LA14_N"        : "V19",
        "LA18_CC_P"     : "AD20",
        "LA18_CC_N"     : "AE20",
        "LA27_P"        : "AA19",
        "LA27_N"        : "AB19",
        "CLK1_M2C_P"    : "P7",
        "CLK1_M2C_N"    : "P6",
        "LA00_CC_P"     : "V23",
        "LA00_CC_N"     : "W23",
        "LA03_P"        : "N21",
        "LA03_N"        : "N22",
        "LA08_P"        : "R20",
        "LA08_N"        : "R21",
        "LA12_P"        : "R22",
        "LA12_N"        : "R23",
        "LA16_P"        : "U21",
        "LA16_N"        : "U22",
        "LA20_P"        : "AE17",
        "LA20_N"        : "AF17",
        "LA22_P"        : "AB17",
        "LA22_N"        : "AC17",
        "LA25_P"        : "AA22",
        "LA25_N"        : "AB22",
        "LA29_P"        : "AE25",
        "LA29_N"        : "AE26",
        "LA31_P"        : "AD24",
        "LA31_N"        : "AD26",
        "LA33_P"        : "AB25",
        "LA33_N"        : "AB26",
        "GBTCLK1_M2C_P" : "P7",
        "GBTCLK1_M2C_N" : "P6",
        "GBTCLK0_M2C_P" : "V7",
        "GBTCLK0_M2C_N" : "V6",
        "LA01_CC_P"     : "V24",
        "LA01_CC_N"     : "W24",
        "LA05_P"        : "P25",
        "LA05_N"        : "P26",
        "LA09_P"        : "N19",
        "LA09_N"        : "P19",
        "LA13_P"        : "T20",
        "LA13_N"        : "U20",
        "LA17_CC_P"     : "AC19",
        "LA17_CC_N"     : "AD19",
        "LA23_P"        : "AA20",
        "LA23_N"        : "AB20",
        "LA26_P"        : "Y20",
        "LA26_N"        : "Y21",
        "PRSNT_M2C_B"   : "Y26",
        "CLK0_M2C_P"    : "V7",
        "CLK0_M2C_N"    : "V6",
        "LA02_P"        : "N24",
        "LA02_N"        : "P24",
        "LA04_P"        : "R25",
        "LA04_N"        : "R26",
        "LA07_P"        : "P20",
        "LA07_N"        : "P21",
        "LA11_P"        : "T22",
        "LA11_N"        : "T23",
        "LA15_P"        : "V21",
        "LA15_N"        : "V22",
        "LA19_P"        : "AE22",
        "LA19_N"        : "AF22",
        "LA21_P"        : "Y17",
        "LA21_N"        : "AA17",
        "LA24_P"        : "AC18",
        "LA24_N"        : "AD18",
        "LA28_P"        : "AF18",
        "LA28_N"        : "AF19",
        "LA30_P"        : "AF24",
        "LA30_N"        : "AF25",
        "LA32_P"        : "AC26",
        "LA32_N"        : "AD26",
        }
    ),
    ("XADC", {
        "GPIO0"   : "AB25",
        "GPIO1"   : "AA25",
        "GPIO2"   : "AB28",
        "GPIO3"   : "AA27",
        "VAUX0_N" : "J24",
        "VAUX0_P" : "J23",
        "VAUX8_N" : "L23",
        "VAUX8_P" : "L22",
        }
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxUSPPlatform):
    default_clk_name   = "clk200"
    default_clk_period = 1e9/200e6

    def __init__(self, toolchain="vivado"):
        XilinxUSPPlatform.__init__(self, "xcau15p-ffvb676-2-i", _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        return OpenFPGALoader(fpga_part="xcau15p", cable="digilent_hs2")

    def do_finalize(self, fragment):
        XilinxUSPPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk200", loose=True), 1e9/200e6)
        self.add_period_constraint(self.lookup_request("clk156", loose=True), 1e9/156e6)
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 66]")