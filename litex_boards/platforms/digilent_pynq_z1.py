#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Rakesh Peter <rakesh@stanproc.in>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform, VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk
    ("sysclk", 0, Pins("H16"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led", 0, Pins("R14"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("P14"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("N16"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("M14"), IOStandard("LVCMOS33")),
    ("user_led", 4, Pins("L15"), IOStandard("LVCMOS33")),
    ("user_led", 5, Pins("G17"), IOStandard("LVCMOS33")),
    ("user_led", 6, Pins("N15"), IOStandard("LVCMOS33")),
    ("user_led", 7, Pins("G14"), IOStandard("LVCMOS33")),
    ("user_led", 8, Pins("L14"), IOStandard("LVCMOS33")),
    ("user_led", 9, Pins("M15"), IOStandard("LVCMOS33")),
  
    # Switches
    ("user_sw", 0, Pins("M20"), IOStandard("LVCMOS33")),
    ("user_sw", 1, Pins("M19"), IOStandard("LVCMOS33")),
    
    # Buttons
    ("user_btn", 0, Pins("D19"), IOStandard("LVCMOS33")),
    ("user_btn", 1, Pins("D20"), IOStandard("LVCMOS33")),
    ("user_btn", 2, Pins("L20"), IOStandard("LVCMOS33")),
    ("user_btn", 3, Pins("L19"), IOStandard("LVCMOS33")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("pmoda:0")),
        Subsignal("rx", Pins("pmoda:1")),
        IOStandard("LVCMOS33")
    ),

    # Audio
    ("aud_pwm", 0, Pins("R18"), IOStandard("LVCMOS33")),
    ("aud_sd",  0, Pins("T17"), IOStandard("LVCMOS33")),
    ("m_clk",   0, Pins("F17"), IOStandard("LVCMOS33")),
    ("m_data",  0, Pins("G18"), IOStandard("LVCMOS33")),

    # Chipkit Single Ended Analog Input
    ("ck_an_n", 0, Pins("D18"), IOStandard("LVCMOS33")),
    ("ck_an_p", 0, Pins("E17"), IOStandard("LVCMOS33")),
    ("ck_an_n", 1, Pins("E19"), IOStandard("LVCMOS33")),
    ("ck_an_p", 1, Pins("E18"), IOStandard("LVCMOS33")),
    ("ck_an_n", 2, Pins("J14"), IOStandard("LVCMOS33")),
    ("ck_an_p", 2, Pins("K14"), IOStandard("LVCMOS33")),
    ("ck_an_n", 3, Pins("J16"), IOStandard("LVCMOS33")),
    ("ck_an_p", 3, Pins("K16"), IOStandard("LVCMOS33")),
    ("ck_an_n", 4, Pins("H20"), IOStandard("LVCMOS33")),
    ("ck_an_p", 4, Pins("J20"), IOStandard("LVCMOS33")),
    ("ck_an_n", 5, Pins("G20"), IOStandard("LVCMOS33")),
    ("ck_an_p", 5, Pins("G19"), IOStandard("LVCMOS33")),

    # Chipkit SPI
    ("ck_miso", 0, Pins("W15"), IOStandard("LVCMOS33")),
    ("ck_mosi", 0, Pins("T12"), IOStandard("LVCMOS33")),
    ("ck_sck",  0, Pins("H15"), IOStandard("LVCMOS33")),
    ("ck_ss",   0, Pins("F16"), IOStandard("LVCMOS33")),
    
    # Chipkit I2C
    ("ck_scl", 0, Pins("P16"), IOStandard("LVCMOS33")),
    ("ck_sda", 0, Pins("P15"), IOStandard("LVCMOS33")),

    # Crypto SDA
    ("crypto_sda", 0, Pins("J15"), IOStandard("LVCMOS33")),
]

_ps7_io = [    
    # PS7
    ("ps7_clk",   0, Pins("E7")),
    ("ps7_porb",  0, Pins("C7")),
    ("ps7_srstb", 0, Pins("B10")),
    ("ps7_mio",   0, Pins(
        " E6  A7  B8  D6  B7  A6  A5  D8",
        " D5  B5  E9  C6  D9  E8  C5  C8",
        "A19 E14 B18 D10 A17 F14 B17 D11",
        "A16 F15 A15 D13 C16 C13 C15 E16",
        "A14 D15 A12 F12 A11 A10 E13 C18"
        "D14 C17 E12  A9 F13 B15 D16 B14"
        "B12 C12 B13  B9 C10 C11")),
    ("ps7_ddram", 0,
        Subsignal("addr", Pins(
            "N2 K2 M3 K3 M4 L1 L4 K4",
            "K1 J4 F5 G4 E4 D4 F4")),
        Subsignal("ba",    Pins("L5 R4 J5")),
        Subsignal("cas_n", Pins("P5")),
        Subsignal("cke",   Pins("N3")),
        Subsignal("ck_n",  Pins("M2")),
        Subsignal("ck_p",  Pins("L2")),
        Subsignal("cs_n",  Pins("N1")),
        Subsignal("dm",    Pins("A1 F1 T1 Y1")),
        Subsignal("dq", Pins(
            "C3 B3 A2 A4 D3 D1 C1 E1",
            "E2 E3 G3 H3 J3 H2 H1 J1",
            "P1 P3 R3 R1 T4 U4 U2 U3",
            "V1 Y3 W1 Y4 Y2 W3 V2 V3"),
        ),
        Subsignal("dqs_n",   Pins("B2 F2 T2 W4")),
        Subsignal("dqs_p",   Pins("C2 G2 R2 W5")),
        Subsignal("reset_n", Pins("B4")),
        Subsignal("odt",     Pins("N5")),
        Subsignal("ras_n",   Pins("P4")),
        Subsignal("vrn",     Pins("G5")),
        Subsignal("vrp",     Pins("H5")),
        Subsignal("we_n",    Pins("M5"))
    ),
]

_hdmi_rx_io = [
    # HDMI Rx
    ("hdmi_rx", 0,
        Subsignal("cec",     Pins("H17"), IOStandard("LVCMOS33")),
        Subsignal("clk_p",   Pins("N18"), IOStandard("TMDS_33")),
        Subsignal("clk_n",   Pins("P19"), IOStandard("TMDS_33")),
        Subsignal("data0_p", Pins("V20"), IOStandard("TMDS_33")),
        Subsignal("data0_n", Pins("W20"), IOStandard("TMDS_33")),
        Subsignal("data1_p", Pins("T20"), IOStandard("TMDS_33")),
        Subsignal("data1_n", Pins("U20"), IOStandard("TMDS_33")),
        Subsignal("data2_p", Pins("N20"), IOStandard("TMDS_33")),
        Subsignal("data2_n", Pins("P20"), IOStandard("TMDS_33")),
        Subsignal("hpd",     Pins("T19"), IOStandard("LVCMOS33")),
        Subsignal("scl",     Pins("U14"), IOStandard("LVCMOS33")),
        Subsignal("sda",     Pins("U15"), IOStandard("LVCMOS33")),
 ),
]

_hdmi_tx_io = [
    # HDMI Tx
    ("hdmi_tx", 0,
        Subsignal("cec",     Pins("G15"), IOStandard("LVCMOS33")),
        Subsignal("clk_p",   Pins("L16"), IOStandard("TMDS_33")),
        Subsignal("clk_n",   Pins("L17"), IOStandard("TMDS_33")),
        Subsignal("data0_p", Pins("K17"), IOStandard("TMDS_33")),
        Subsignal("data0_n", Pins("K18"), IOStandard("TMDS_33")),
        Subsignal("data1_p", Pins("K19"), IOStandard("TMDS_33")),
        Subsignal("data1_n", Pins("J19"), IOStandard("TMDS_33")),
        Subsignal("data2_p", Pins("J18"), IOStandard("TMDS_33")),
        Subsignal("data2_n", Pins("H18"), IOStandard("TMDS_33")),
        Subsignal("hpdn",    Pins("R19"), IOStandard("LVCMOS33")),
        Subsignal("scl",     Pins("M17"), IOStandard("LVCMOS33")),
        Subsignal("sda",     Pins("M18"), IOStandard("LVCMOS33")),
 ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("pmoda", "Y18 Y19 Y16 Y17 U18 U19 W18 W19"), # XADC
    ("pmodb", "W14 Y14 T11 T10 V16 W16 V12 W13"),
    ("ck_io", "T14 U12 U13 V13 V15 T15 R16 U17 V17 V18 T16 R17 P18 N17 Y11 Y12 W11 V11 T5 U10 B20 C20 F20 F19 A20 B19 U5 V5 V6 U7 V7 U8 V8 V10 W10 W6 Y6 Y7 W8 Y8 W9 Y9 Y13")
]
# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "sysclk"
    default_clk_period = 1e9/125e6

    def __init__(self, toolchain="vivado"):
        XilinxPlatform.__init__(self, "xc7z020-clg400-1", _io,  _connectors, toolchain=toolchain)
        self.add_extension(_ps7_io)
        self.add_extension(_hdmi_rx_io)
        self.add_extension(_hdmi_tx_io)

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("sysclk", loose=True), 1e9/125e6)
