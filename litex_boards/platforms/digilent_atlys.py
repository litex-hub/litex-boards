#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2015-2021 HDMI2USB/LiteX developers
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk/Rst
    ("clk100",    0, Pins("L15"), IOStandard("LVCMOS33")),
    ("cpu_reset", 0, Pins("T15"), IOStandard("LVCMOS33")),

    # Serial
    ("serial", 0,
        Subsignal("rx", Pins("A16"), IOStandard("LVCMOS33")),
        Subsignal("tx", Pins("B16"), IOStandard("LVCMOS33")),
    ),

    # FX2
    ("fx2", 0,
        Subsignal("ifclk",    Pins("C10")),
        Subsignal("data",     Pins("A2 D6 C6 B3 A3 B4 A4 C5")),
        Subsignal("addr",     Pins("A14 B14"), Misc("DRIVE=12")),
        Subsignal("flaga",    Pins("B9"),  Misc("DRIVE=12")),
        Subsignal("flagb",    Pins("A9"),  Misc("DRIVE=12")),
        Subsignal("flagc",    Pins("C15"), Misc("DRIVE=12")),
        Subsignal("rd_n",     Pins("F13"), Misc("DRIVE=12")),
        Subsignal("wr_n",     Pins("E13")),
        Subsignal("oe_n",     Pins("A15"), Misc("DRIVE=12")),
        Subsignal("cs_n",     Pins("B2")),
        Subsignal("pktend_n", Pins("C4"), Misc("DRIVE=12")),
        IOStandard("LVCMOS33")
    ),

    # SPI Flash
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("V3")),
        Subsignal("clk",  Pins("R15")),
        Subsignal("dq",   Pins("T13", "R13", "T14", "V14")),
        IOStandard("LVCMOS33"),
        Misc("SLEW=FAST"),
    ),

    # Leds
    ("user_led", 0, Pins("U18"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("M14"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("N14"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("L14"), IOStandard("LVCMOS33")),
    ("user_led", 4, Pins("M13"), IOStandard("LVCMOS33")),
    ("user_led", 5, Pins("D4"),  IOStandard("LVCMOS33")),
    ("user_led", 6, Pins("P16"), IOStandard("LVCMOS33")),
    ("user_led", 7, Pins("N12"), IOStandard("LVCMOS33")),

    # Buttons
    ("user_btn", 0, Pins("N4"), IOStandard("LVCMOS18")), # North button
    ("user_btn", 1, Pins("P4"), IOStandard("LVCMOS18")), # East button
    ("user_btn", 2, Pins("P3"), IOStandard("LVCMOS18")), # South button
    ("user_btn", 3, Pins("F6"), IOStandard("LVCMOS18")), # West button
    ("user_btn", 4, Pins("F5"), IOStandard("LVCMOS18")), # Center button

    # Switches.
    ("user_sw", 0, Pins("A10"), IOStandard("LVCMOS33")),
    ("user_sw", 1, Pins("D14"), IOStandard("LVCMOS33")),
    ("user_sw", 2, Pins("C14"), IOStandard("LVCMOS33")),
    ("user_sw", 3, Pins("P15"), IOStandard("LVCMOS33")),
    ("user_sw", 4, Pins("P12"), IOStandard("LVCMOS33")),
    ("user_sw", 5, Pins("R5"),  IOStandard("LVCMOS33")),
    ("user_sw", 6, Pins("T5"),  IOStandard("LVCMOS33")),
    ("user_sw", 7, Pins("E4"),  IOStandard("LVCMOS18")),

    # GMII/MII Ethernet
    ("eth_clocks", 0,
        Subsignal("tx",  Pins("K16")),
        Subsignal("gtx", Pins("L12")),
        Subsignal("rx",  Pins("K15")),
        IOStandard("LVCMOS33")
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("G13")),
        Subsignal("int_n",   Pins("L16")),
        Subsignal("mdio",    Pins("N17")),
        Subsignal("mdc",     Pins("F16")),
        Subsignal("rx_dv",   Pins("F17")),
        Subsignal("rx_er",   Pins("F18")),
        Subsignal("rx_data", Pins("G16 H14 E16 F15 F14 E18 D18 D17")),
        Subsignal("tx_en",   Pins("H15")),
        Subsignal("tx_er",   Pins("G18")),
        Subsignal("tx_data", Pins("H16 H13 K14 K13 J13 G14 H12 K12")),
        Subsignal("col",     Pins("C17")),
        Subsignal("crs",     Pins("C18")),
        IOStandard("LVCMOS33")
    ),

    # DDR2 SDRAM.
    ("ddram_clock", 0,
        Subsignal("p", Pins("G3")),
        Subsignal("n", Pins("G1")),
        IOStandard("DIFF_SSTL18_II"), Misc("IN_TERM=NONE")
    ),
    ("ddram", 0,
        Subsignal("cke",   Pins("H7"), IOStandard("SSTL18_II")),
        Subsignal("ras_n", Pins("L5"), IOStandard("SSTL18_II")),
        Subsignal("cas_n", Pins("K5"), IOStandard("SSTL18_II")),
        Subsignal("we_n",  Pins("E3"), IOStandard("SSTL18_II")),
        Subsignal("ba",    Pins("F2 F1 E1"), IOStandard("SSTL18_II")),
        Subsignal("a", Pins(
            "J7 J6 H5 L7 F3 H4 H3 H6",
            "D2 D1 F4 D3 G6"),
            IOStandard("SSTL18_II")),
        Subsignal("dq", Pins(
            "L2 L1 K2 K1 H2 H1 J3 J1",
            "M3 M1 N2 N1 T2 T1 U2 U1"),
            IOStandard("SSTL18_II")),
        Subsignal("dqs",   Pins("P2 L4"), IOStandard("DIFF_SSTL18_II")),
        Subsignal("dqs_n", Pins("P1 L3"), IOStandard("DIFF_SSTL18_II")),
        Subsignal("dm",    Pins("K4 K3"), IOStandard("SSTL18_II")),
        Subsignal("odt",   Pins("K6"),    IOStandard("SSTL18_II"))
    ),

    # HDMI Out 0
    ("hdmi_out", 0,
        Subsignal("clk_p",   Pins("B6"), IOStandard("TMDS_33")),
        Subsignal("clk_n",   Pins("A6"), IOStandard("TMDS_33")),
        Subsignal("data0_p", Pins("D8"), IOStandard("TMDS_33")),
        Subsignal("data0_n", Pins("C8"), IOStandard("TMDS_33")),
        Subsignal("data1_p", Pins("C7"), IOStandard("TMDS_33")),
        Subsignal("data1_n", Pins("A7"), IOStandard("TMDS_33")),
        Subsignal("data2_p", Pins("B8"), IOStandard("TMDS_33")),
        Subsignal("data2_n", Pins("A8"), IOStandard("TMDS_33")),
        Subsignal("scl",     Pins("D9"), IOStandard("I2C")),
        Subsignal("sda",     Pins("C9"), IOStandard("I2C")),
    ),

    # HDMI In 0
    ("hdmi_in", 0,
        Subsignal("clk_p",   Pins("D11")),
        Subsignal("clk_n",   Pins("C11")),
        Subsignal("data0_p", Pins("G9")),
        Subsignal("data0_n", Pins("F9")),
        Subsignal("data1_p", Pins("B11")),
        Subsignal("data1_n", Pins("A11")),
        Subsignal("data2_p", Pins("B12")),
        Subsignal("data2_n", Pins("A12")),
        Subsignal("scl",     Pins("C13"), IOStandard("LVCMOS33")),
        Subsignal("sda",     Pins("A13"), IOStandard("LVCMOS33")),
    ),

    # HDMI In 1
    ("hdmi_in", 1,
        Subsignal("clk_p",   Pins("H17")),
        Subsignal("clk_n",   Pins("H18")),
        Subsignal("data0_p", Pins("K17")),
        Subsignal("data0_n", Pins("K18")),
        Subsignal("data1_p", Pins("L17")),
        Subsignal("data1_n", Pins("L18")),
        Subsignal("data2_p", Pins("J16")),
        Subsignal("data2_n", Pins("J18")),
        Subsignal("scl",     Pins("M16"), IOStandard("LVCMOS33")),
        Subsignal("sda",     Pins("M18"), IOStandard("LVCMOS33")),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("VHDCI",
        {
        "EXP-IO1_P"  : "U16",
        "EXP-IO2_P"  : "U15",
        "EXP-IO3_P"  : "U13",
        "EXP-IO4_P"  : "M11",
        "EXP-IO5_P"  : "R11",
        "EXP-IO6_P"  : "T12",
        "EXP-IO7_P"  : "N10",
        "EXP-IO8_P"  : "M10",
        "EXP-IO9_P"  : "U11",
        "EXP-IO10_P" : "R10",
        "EXP-IO11_P" : "U10",
        "EXP-IO12_P" :  "R8",
        "EXP-IO13_P" :  "M8",
        "EXP-IO14_P" :  "U8",
        "EXP-IO15_P" :  "U7",
        "EXP-IO16_P" :  "N7",
        "EXP-IO17_P" :  "T6",
        "EXP-IO18_P" :  "R7",
        "EXP-IO19_P" :  "N6",
        "EXP-IO20_P" :  "U5",
        "EXP-IO1_N"  : "V16",
        "EXP-IO2_N"  : "V15",
        "EXP-IO3_N"  : "V13",
        "EXP-IO4_N"  : "N11",
        "EXP-IO5_N"  : "T11",
        "EXP-IO6_N"  : "V12",
        "EXP-IO7_N"  : "P11",
        "EXP-IO8_N"  :  "N9",
        "EXP-IO9_N"  : "V11",
        "EXP-IO10_N" : "T10",
        "EXP-IO11_N" : "V10",
        "EXP-IO12_N" :  "T8",
        "EXP-IO13_N" :  "N8",
        "EXP-IO14_N" :  "V8",
        "EXP-IO15_N" :  "V7",
        "EXP-IO16_N" :  "P8",
        "EXP-IO17_N" :  "V6",
        "EXP-IO18_N" :  "T7",
        "EXP-IO19_N" :  "P7",
        "EXP-IO20_N" :  "V5",
        }
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self, toolchain="ise"):
        XilinxPlatform.__init__(self,  "xc6slx45-csg324-3", _io, _connectors, toolchain=toolchain)
        self.add_platform_command("""CONFIG VCCAUX="3.3";""")

    def create_programmer(self):
        return iMPACT()

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100",           loose=True), 1e9/100e6)
        self.add_period_constraint(self.lookup_request("hdmi_in:clk_p", 0, loose=True), 1e9/74.25e6)
        self.add_period_constraint(self.lookup_request("hdmi_in:clk_p", 1, loose=True), 1e9/74.25e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:rx",    loose=True), 1e9/25e6)
        self.add_period_constraint(self.lookup_request("fx2:ifclk",        loose=True), 1e9/100e6)
