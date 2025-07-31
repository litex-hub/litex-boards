#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 Marco Tassemeier <mtassemeier@uni-osnabrueck.de>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxUSPlatform, VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------
_io = [
    # Clk / Rst
    ("clk300", 0,
        Subsignal("p", Pins("K22"), IOStandard("DIFF_SSTL12")),
        Subsignal("n", Pins("K23"), IOStandard("DIFF_SSTL12"))
    ),

    ("clk125", 0,
        Subsignal("p", Pins("G12"), IOStandard("LVDS_25")),
        Subsignal("n", Pins("F12"), IOStandard("LVDS_25"))
    ),

    ("FPGA_EMCCLK", 0, Pins("N21"), IOStandard("LVCMOS18")),

    ("USER_MGT_CLK", 0,
        Subsignal("p", Pins("M7")),
        Subsignal("n", Pins("M6"))
    ),

    ("CLK_74_25", 0,
        Subsignal("p", Pins("D11"), IOStandard("LVDS_25")),
        Subsignal("n", Pins("D10"), IOStandard("LVDS_25"))
    ),

    ("cpu_reset", 0, Pins("B9"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led", 0, Pins("C9"),  IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("D9"),  IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("E10"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("E11"), IOStandard("LVCMOS33")),
    ("user_led", 4, Pins("F9"),  IOStandard("LVCMOS33")),
    ("user_led", 5, Pins("F10"), IOStandard("LVCMOS33")),
    ("user_led", 6, Pins("G9"),  IOStandard("LVCMOS33")),
    ("user_led", 7, Pins("G10"), IOStandard("LVCMOS33")),

    # Buttons
    ("user_btn_c", 0, Pins("A9"),  IOStandard("LVCMOS33")),
    ("user_btn_n", 0, Pins("A10"), IOStandard("LVCMOS33")),
    ("user_btn_s", 0, Pins("C11"), IOStandard("LVCMOS33")),
    ("user_btn_w", 0, Pins("B10"), IOStandard("LVCMOS33")),
    ("user_btn_e", 0, Pins("B11"), IOStandard("LVCMOS33")),

    # DIP-Switches
    ("user_dip_sw", 0, Pins("G11"), IOStandard("LVCMOS33")),
    ("user_dip_sw", 1, Pins("H11"), IOStandard("LVCMOS33")),
    ("user_dip_sw", 2, Pins("H9"),  IOStandard("LVCMOS33")),
    ("user_dip_sw", 3, Pins("J9"),  IOStandard("LVCMOS33")),

    # SMA
    ("user_sma_clock", 0,
        Subsignal("p", Pins("J23"), IOStandard("DIFF_SSTL12")),
        Subsignal("n", Pins("J24"), IOStandard("DIFF_SSTL12"))
    ),

    ("user_sma_gpio", 0,
        Subsignal("p", Pins("K25"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("n", Pins("K26"), IOStandard("DIFF_SSTL12_DCI"))
    ),

    # I2C
    ("i2c", 0,
        Subsignal("scl", Pins("AE13")),
        Subsignal("sda", Pins("AF13")),
        IOStandard("LVCMOS33")
    ),
    
    ("i2c_hdmi", 0,
        Subsignal("scl", Pins("AD15")),
        Subsignal("sda", Pins("AE15")),
        IOStandard("LVCMOS33")
     ),

    # Serial
    ("serial", 0,
        Subsignal("cts", Pins("Y13")),
        Subsignal("rts", Pins("AA13")),
        Subsignal("tx",  Pins("W13")),
        Subsignal("rx",  Pins("W12")),
        IOStandard("LVCMOS33")
    ),

    # SPIFlash
    ("spiflash", 0, # clock needs to be accessed through primitive
        Subsignal("cs_n"), Pins("AA12"),
        Subsignal("dq"),   Pins("AD11 AC12 AC11 AE11"),
        IOStandard("LVCMOS18")
    ),

    ("spiflash", 1, # clock needs to be accessed through primitive
        Subsignal("cs_n"), Pins("U22"),
        Subsignal("dq"),   Pins("N23 P23 R20 R21"),
        IOStandard("LVCMOS18")
    ),

    # HDMI
    ("hdmi", 0,
        Subsignal("d", Pins(
            "V21 V22 T22  T23  W19 W20 Y22 Y23",
            "Y25 Y26 AA24 AA25 W25 W26 V23 W23",
            "V24 W24")),
        Subsignal("de",        Pins("U20")),
        Subsignal("clk",       Pins("P20")),
        Subsignal("vsync",     Pins("U21")),
        Subsignal("hsync",     Pins("V19")),
        Subsignal("spdif",     Pins("T20")),
        Subsignal("spdif_out", Pins("U19")),
        IOStandard("LVCMOS18")
    ),

    # DDR4 SDRAM
    ("ddram", 0,
        Subsignal("a", Pins(
            "D25 D23 D26 D24 E26 C26 G22 B25",
            "F22 C24 E25 F23 E23 B26"),
            IOStandard("SSTL12")),
        Subsignal("ba",        Pins("H22 H21"),         IOStandard("SSTL12")),
        Subsignal("bg",        Pins("G26"),             IOStandard("SSTL12")),
        Subsignal("ras_n",     Pins("F24"),             IOStandard("SSTL12")), # A16
        Subsignal("cas_n",     Pins("F25"),             IOStandard("SSTL12")), # A15
        Subsignal("we_n",      Pins("H26"),             IOStandard("SSTL12")), # A14
        Subsignal("cs_n",      Pins("H23"),             IOStandard("SSTL12")),
        Subsignal("act_n",     Pins("J26"),             IOStandard("SSTL12")),
        #Subsignal("ten",       Pins(""),                IOStandard("SSTL12")),
        Subsignal("alert_n",   Pins("L24"),             IOStandard("SSTL12")),
        Subsignal("par",       Pins("J25"),             IOStandard("SSTL12")),
        Subsignal("dm",        Pins("A22 C18 H18 G15"), IOStandard("POD12_DCI")),
        Subsignal("dq",        Pins(
            "C22 B24 C23 A24 D21 B22 E21 A25",
            "A19 C17 A20 B17 B20 A15 B19 B15",
            "F18 G21 F19 D20 E18 D19 G20 D18",
            "H17 D16 G16 D15 E15 C16 H16 G17"),
            IOStandard("POD12_DCI")),
        Subsignal("dqs_p",     Pins("C21 A17 F20 E16"),
            IOStandard("DIFF_POD12_DCI")),
        Subsignal("dqs_n",     Pins("B21 A18 E20 E17"),
            IOStandard("DIFF_POD12_DCI")),
        Subsignal("clk_p",     Pins("G24"),             IOStandard("DIFF_POD12")),
        Subsignal("clk_n",     Pins("G25"),             IOStandard("DIFF_POD12")),     
        Subsignal("cke",       Pins("M24"),             IOStandard("SSTL12")),
        Subsignal("odt",       Pins("H24"),             IOStandard("SSTL12")),
        Subsignal("reset_n",   Pins("L25"),             IOStandard("LVCMOS12")), 
    ),

    # PCIe
    ("pcie_x1", 0,
        Subsignal("rst_n",    Pins("T19"), IOStandard("LVCMOS18")),
        Subsignal("wake_n",   Pins("P19"), IOStandard("LVCMOS18")),
        Subsignal("clk_p",    Pins("V7")),
        Subsignal("clk_n",    Pins("V6")),
        Subsignal("rx_p",     Pins("P2")),
        Subsignal("rx_n",     Pins("P1")),
        Subsignal("tx_p",     Pins("R5")),
        Subsignal("tx_n",     Pins("R4"))
    ),

    ("pcie_x4", 0,
        Subsignal("rst_n",    Pins("T19"), IOStandard("LVCMOS18")),
        Subsignal("wake_n",   Pins("P19"), IOStandard("LVCMOS18")),
        Subsignal("clk_p",    Pins("V7")),
        Subsignal("clk_n",    Pins("V6")),
        Subsignal("rx_p",     Pins("P2 T2 V2 Y2")),
        Subsignal("rx_n",     Pins("P1 T1 V1 Y1")),
        Subsignal("tx_p",     Pins("R5 U5 W5 AA5")),
        Subsignal("tx_n",     Pins("R4 U4 W4 AA4"))
    ),

    ("pcie_x8", 0,
        Subsignal("rst_n",    Pins("T19"), IOStandard("LVCMOS18")),
        Subsignal("wake_n",   Pins("P19"), IOStandard("LVCMOS18")),
        Subsignal("clk_p",    Pins("V7")),
        Subsignal("clk_n",    Pins("V6")),
        Subsignal("rx_p",     Pins("P2 T2 V2 Y2  AB2 AD2 AE4 AF2")),
        Subsignal("rx_n",     Pins("P1 T1 V1 Y1  AB1 AD1 AE3 AF1")),
        Subsignal("tx_p",     Pins("R5 U5 W5 AA5 AC5 AD7 AE9 AF7")),
        Subsignal("tx_n",     Pins("R4 U4 W4 AA4 AC4 AD6 AE8 AF6"))
    ),

    # SFP
    ("sfp", 0,
        Subsignal("txp", Pins("N5")),
        Subsignal("txn", Pins("N4")),
        Subsignal("rxp", Pins("M2")),
        Subsignal("rxn", Pins("M1"))
    ),
    ("sfp_tx", 0,
        Subsignal("p", Pins("N5")),
        Subsignal("n", Pins("N4")),
    ),
    ("sfp_rx", 0,
        Subsignal("p", Pins("M2")),
        Subsignal("n", Pins("M1")),
    ),
    ("sfp_tx_disable_n", 0, Pins("AB14"), IOStandard("LVCMOS33")),

    ("sfp", 1,
        Subsignal("txp", Pins("L5")),
        Subsignal("txn", Pins("L4")),
        Subsignal("rxp", Pins("K2")),
        Subsignal("rxn", Pins("K1"))
    ),
    ("sfp_tx", 1,
        Subsignal("p", Pins("L5")),
        Subsignal("n", Pins("L4")),
    ),
    ("sfp_rx", 1,
        Subsignal("p", Pins("K2")),
        Subsignal("n", Pins("K1")),
    ),
    ("sfp_tx_disable_n", 1, Pins("AA14"), IOStandard("LVCMOS33")),

    ("sfp", 2,
        Subsignal("txp", Pins("J5")),
        Subsignal("txn", Pins("J4")),
        Subsignal("rxp", Pins("H2")),
        Subsignal("rxn", Pins("H1"))
    ),
    ("sfp_tx", 2,
        Subsignal("p", Pins("J5")),
        Subsignal("n", Pins("J4")),
    ),
    ("sfp_rx", 2,
        Subsignal("p", Pins("H2")),
        Subsignal("n", Pins("H1")),
    ),
    ("sfp_tx_disable_n", 2, Pins("AA15"), IOStandard("LVCMOS33")),

    ("sfp", 3,
        Subsignal("txp", Pins("G5")),
        Subsignal("txn", Pins("G4")),
        Subsignal("rxp", Pins("F2")),
        Subsignal("rxn", Pins("F1"))
    ),
    ("sfp_tx", 3,
        Subsignal("p", Pins("G5")),
        Subsignal("n", Pins("G4")),
    ),
    ("sfp_rx", 3,
        Subsignal("p", Pins("F2")),
        Subsignal("n", Pins("F1")),
    ),
    ("sfp_tx_disable_n", 3, Pins("Y15"), IOStandard("LVCMOS33")),
    
]

# Connectors ---------------------------------------------------------------------------------------
_connectors = [
    ("HPC", {
        "DP0_C2M_P" : "F7",
        "DP0_C2M_N" : "F6",
        "DP0_M2C_P" : "D2",
        "DP0_M2C_N" : "D1",
        "DP1_C2M_P" : "E5",
        "DP1_C2M_N" : "E4",
        "DP1_M2C_P" : "C4",
        "DP1_M2C_N" : "C3",
        "DP2_C2M_P" : "D7",
        "DP2_C2M_N" : "D6",
        "DP2_M2C_P" : "B2",
        "DP2_M2C_N" : "B1",
        "DP3_C2M_P" : "B7",
        "DP3_C2M_N" : "B6",
        "DP3_M2C_P" : "A4",
        "DP3_M2C_N" : "A3",
        "LA00_P_CC" : "AD20", # LVDS
        "LA00_N_CC" : "AE20", # LVDS
        "LA01_P_CC" : "AC19", # LVDS
        "LA01_N_CC" : "AD19", # LVDS
        "LA02_P"    : "Y17",  # LVDS
        "LA02_N"    : "AA17", # LVDS
        "LA03_P"    : "AB17", # LVDS
        "LA03_N"    : "AC17", # LVDS
        "LA04_P"    : "AA20", # LVDS
        "LA04_N"    : "AB20", # LVDS
        "LA05_P"    : "AA19", # LVDS
        "LA05_N"    : "AB19", # LVDS
        "LA06_P"    : "Y20",  # LVDS
        "LA06_N"    : "Y21",  # LVDS
        "LA07_P"    : "AD16", # LVDS 
        "LA07_N"    : "AE16", # LVDS
        "LA08_P"    : "AE17", # LVDS
        "LA08_N"    : "AF17", # LVDS
        "LA09_P"    : "AC18", # LVDS
        "LA09_N"    : "AD18", # LVDS
        "LA10_P"    : "AF18", # LVDS
        "LA10_N"    : "AF19", # LVDS
        "LA11_P"    : "Y18",  # LVDS
        "LA11_N"    : "AA18", # LVDS
        "LA12_P"    : "AC22", # LVDS
        "LA12_N"    : "AC23", # LVDS
        "LA13_P"    : "AD23", # LVDS
        "LA13_N"    : "AE23", # LVDS
        "LA14_P"    : "AE22", # LVDS
        "LA14_N"    : "AF22", # LVDS
        "LA15_P"    : "AB24", # LVDS
        "LA15_N"    : "AC24", # LVDS
        "LA16_P"    : "AD24", # LVDS
        "LA16_N"    : "AD25", # LVDS
        "LA17_P_CC" : "AD21", # LVDS
        "LA17_N_CC" : "AE21", # LVDS
        "LA18_P_CC" : "AA22", # LVDS
        "LA18_N_CC" : "AB22", # LVDS
        "LA19_P"    : "AC26", # LVDS
        "LA19_N"    : "AD26", # LVDS
        "LA20_P"    : "AF24", # LVDS
        "LA20_N"    : "AF25", # LVDS
        "LA21_P"    : "AB25", # LVDS
        "LA21_N"    : "AB26", # LVDS
        "LA22_P"    : "AE25", # LVDS
        "LA22_N"    : "AE26", # LVDS
        "GBTCLK0_M2C_P" : "K7",
        "GBTCLK0_M2C_N" : "K6",
        "GBTCLK1_M2C_P" : "H7",
        "GBTCLK1_M2C_N" : "H6",
        "CLK0_M2C_P"    : "AB21", # LVDS
        "CLK0_M2C_N"    : "AC21", # LVDS
        "PG_M2C"        : "H13"   # LVCMOS33
    }),
    
    ("pmod0", "A14 B15 A12 A13 B12 C12 C13 C14"), # LVCMOS33
    ("pmod1", "D13 D14 E12 E13 F13 F14 J14 J15")  # LVCMOS33
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxUSPlatform):
    default_clk_name   = "clk125"
    default_clk_period = 1e9/125e6

    def __init__(self, toolchain="vivado"):
        XilinxUSPlatform.__init__(self, "xcku5p-ffvb676-2-e", _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment):
        XilinxUSPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk300",  loose=True), 1e9/300e6)
        self.add_period_constraint(self.lookup_request("clk125",     loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("FPGA_EMCCLK", loose=True), 1e9/90e6)
        self.add_period_constraint(self.lookup_request("CLK_74_25",   loose=True), 1e9/74.25e6)
        # DDR4 memory Internal Vref
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 66]")
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 67]")
