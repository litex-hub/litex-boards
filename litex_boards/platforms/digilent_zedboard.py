# This file is Copyright (c) 2019 Michael Betz <michibetz@gmail.com>
# License: BSD

from litex.build.generic_platform import Pins, IOStandard, Subsignal
from litex.build.xilinx import Xilinx7SeriesPlatform
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk100", 0, Pins("Y9"), IOStandard("LVCMOS33")),

    # Leds (above DIP switches)
    ("user_led", 0, Pins("T22"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("T21"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("U22"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("U21"), IOStandard("LVCMOS33")),
    ("user_led", 4, Pins("V22"), IOStandard("LVCMOS33")),
    ("user_led", 5, Pins("W22"), IOStandard("LVCMOS33")),
    ("user_led", 6, Pins("U19"), IOStandard("LVCMOS33")),
    ("user_led", 7, Pins("U14"), IOStandard("LVCMOS33")),

    # Switches
    ("user_sw", 0, Pins("F22"), IOStandard("LVCMOS18")),
    ("user_sw", 1, Pins("G22"), IOStandard("LVCMOS18")),
    ("user_sw", 2, Pins("H22"), IOStandard("LVCMOS18")),
    ("user_sw", 3, Pins("F21"), IOStandard("LVCMOS18")),
    ("user_sw", 4, Pins("H19"), IOStandard("LVCMOS18")),
    ("user_sw", 5, Pins("H18"), IOStandard("LVCMOS18")),
    ("user_sw", 6, Pins("H17"), IOStandard("LVCMOS18")),
    ("user_sw", 7, Pins("M15"), IOStandard("LVCMOS18")),

    # Buttons
    ("user_btn_c", 0, Pins("P16"), IOStandard("LVCMOS25")),
    ("user_btn_d", 0, Pins("R16"), IOStandard("LVCMOS25")),
    ("user_btn_l", 0, Pins("N15"), IOStandard("LVCMOS25")),
    ("user_btn_r", 0, Pins("R18"), IOStandard("LVCMOS25")),
    ("user_btn_u", 0, Pins("T18"), IOStandard("LVCMOS25")),

    # OLED (UG-2832HSWEG04/ssd1306)
    ("zed_oled", 0,
        Subsignal("clk",     Pins("AB12")),
        Subsignal("mosi",    Pins("AA12")),
        # OLED does not have a MISO pin :(
        Subsignal("reset_n", Pins("U9")),
        Subsignal("dc",      Pins("U10")),
        Subsignal("vbat_n",  Pins("U11")),
        Subsignal("vdd_n",   Pins("U12")),
        IOStandard("LVCMOS33")
    ),

    # PS7
    ("ps7_clk",   0, Pins("F7")),
    ("ps7_porb",  0, Pins("B5")),
    ("ps7_srstb", 0, Pins("C9")),
    ("ps7_mio",   0, Pins(
        " G6  A1  A2  F6  E4  A3  A4  D5",
        " E5  C4  G7  B4  C5  A6  B6  E6",
        " D6  E9  A7 E10  A8 F11 A14 E11",
        " B7 F12 A13  D7 A12  E8 A11  F9",
        " C7 G13 B12 F14 A9  B14 F13 C13",
        "E14  C8  D8 B11 E13  B9 D12 B10",
        "D11 C14 D13 C10 D10 C12")),
    ("ps7_ddram", 0,
        Subsignal("addr", Pins(
            "M4 M5 K4 L4 K6 K5 J7 J6",
            "J5 H5 J3 G5 H4 F4 G4")),
        Subsignal("ba",    Pins("L7 L6 M6")),
        Subsignal("cas_n", Pins("P3")),
        Subsignal("cke",   Pins("V3")),
        Subsignal("ck_n",  Pins("N5")),
        Subsignal("ck_p",  Pins("N4")),
        Subsignal("cs_n",  Pins("P6")),
        Subsignal("dm",    Pins("B1 H3 P1 AA2")),
        Subsignal("dq", Pins(
            " D1  C3  B2  D3  E3  E1  F2  F1",
            " G2  G1  L1  L2  L3  K1  J1  K3",
            " M1  T3  N3  T1  R3  T2  M2  R1",
            "AA3  U1 AA1  U2  W1  Y3  W3  Y1"),
        ),
        Subsignal("dqs_n",   Pins("D2 J2 P2 W2")),
        Subsignal("dqs_p",   Pins("C2 H2 N2 V2")),
        Subsignal("reset_n", Pins("F3")),
        Subsignal("odt",     Pins("P5")),
        Subsignal("ras_n",   Pins("R5")),
        Subsignal("vrn",     Pins("M7")),
        Subsignal("vrp",     Pins("N7")),
        Subsignal("we_n",    Pins("R4"))
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    # access a pin with `pmoda:N`, where N is:
    #   N: 0  1  2  3  4  5  6  7
    # Pin: 1  2  3  4  7  8  9 10
    # Bank 13
    ("pmoda", "Y11 AA11 Y10 AA9 AB11 AB10 AB9 AA8"),
    ("pmodb", "W12 W11 V10 W8 V12 W10 V9 V8"),
    ("pmodc", "AB6 AB7 AA4 Y4 T6 R6 U4 T4"),
    ("pmodd", "W7 V7 V4 V5 W5 W6 U5 U6"),
    ("XADC", {
        # Bank 34
        "gio_0": "H15",
        "gio_1": "R15",
        "gio_2": "K15",
        "gio_3": "J15",
        # Bank 35
        "AD0N_R": "E16",
        "AD0P_R": "F16",
        "AD8N_N": "D17",
        "AD8P_R": "D16"
    }),
    ("LPC", {
        # "DP0_C2M_N": "",  # NC
        # "DP0_C2M_P": "",  # NC
        # "DP0_M2C_N": "",  # NC
        # "DP0_M2C_P": "",  # NC
        # "GBTCLK0_M2C_N": "",  # NC
        # "GBTCLK0_M2C_P": "",  # NC
        "CLK0_M2C_N": "L19",
        "CLK0_M2C_P": "L18",
        "CLK1_M2C_N": "C19",
        "CLK1_M2C_P": "D18",
        "IIC_SCL_MAIN": "R7",
        "IIC_SDA_MAIN": "U7",
        "LA00_CC_N": "M20",
        "LA00_CC_P": "M19",
        "LA01_CC_N": "N20",
        "LA01_CC_P": "N19",
        "LA02_N": "P18",
        "LA02_P": "P17",
        "LA03_N": "P22",
        "LA03_P": "N22",
        "LA04_N": "M22",
        "LA04_P": "M21",
        "LA05_N": "K18",
        "LA05_P": "J18",
        "LA06_N": "L22",
        "LA06_P": "L21",
        "LA07_N": "T17",
        "LA07_P": "T16",
        "LA08_N": "J22",
        "LA08_P": "J21",
        "LA09_N": "R21",
        "LA09_P": "R20",
        "LA10_N": "T19",
        "LA10_P": "R19",
        "LA11_N": "N18",
        "LA11_P": "N17",
        "LA12_N": "P21",
        "LA12_P": "P20",
        "LA13_N": "M17",
        "LA13_P": "L17",
        "LA14_N": "K20",
        "LA14_P": "K19",
        "LA15_N": "J17",
        "LA15_P": "J16",
        "LA16_N": "K21",
        "LA16_P": "J20",
        "LA17_CC_N": "B20",
        "LA17_CC_P": "B19",
        "LA18_CC_N": "C20",
        "LA18_CC_P": "D20",
        "LA19_N": "G16",
        "LA19_P": "G15",
        "LA20_N": "G21",
        "LA20_P": "G20",
        "LA21_N": "E20",
        "LA21_P": "E19",
        "LA22_N": "F19",
        "LA22_P": "G19",
        "LA23_N": "D15",
        "LA23_P": "E15",
        "LA24_N": "A19",
        "LA24_P": "A18",
        "LA25_N": "C22",
        "LA25_P": "D22",
        "LA26_N": "E18",
        "LA26_P": "F18",
        "LA27_N": "D21",
        "LA27_P": "E21",
        "LA28_N": "A17",
        "LA28_P": "A16",
        "LA29_N": "C18",
        "LA29_P": "C17",
        "LA30_N": "B15",
        "LA30_P": "C15",
        "LA31_N": "B17",
        "LA31_P": "B16",
        "LA32_N": "A22",
        "LA32_P": "A21",
        "LA33_N": "B22",
        "LA33_P": "B21",
        "PRSNT_M2C_L": "AB14"
    })
]

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self, toolchain="vivado"):
        Xilinx7SeriesPlatform.__init__(self, "xc7z020clg484-1", _io, _connectors, toolchain=toolchain)
        self.toolchain.bitstream_commands = \
            ["set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]", ]

    def create_programmer(self):
        return OpenOCD(config="board/digilent_zedboard.cfg")

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100", loose=True), 1e9/100e6)
