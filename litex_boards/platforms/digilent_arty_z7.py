# This file is Copyright (c) 2019 Michael Betz <michibetz@gmail.com>
# License: BSD

from litex.build.generic_platform import Pins, IOStandard, Subsignal
from litex.build.xilinx import XilinxPlatform, VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk125", 0, Pins("H16"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led", 0, Pins("R14"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("P14"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("N16"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("M14"), IOStandard("LVCMOS33")),

    ("rgb_led", 0,
        Subsignal("r", Pins("N15")),
        Subsignal("g", Pins("G17")),
        Subsignal("b", Pins("L15")),
        IOStandard("LVCMOS33"),
    ),
    ("rgb_led", 1,
        Subsignal("r", Pins("M15")),
        Subsignal("g", Pins("L14")),
        Subsignal("b", Pins("G14")),
        IOStandard("LVCMOS33"),
    ),
    # Switches
    ("user_sw", 0, Pins("M20"), IOStandard("LVCMOS33")),
    ("user_sw", 1, Pins("M19"), IOStandard("LVCMOS33")),

    # Buttons
    ("user_btn", 0, Pins("D19"), IOStandard("LVCMOS33")),
    ("user_btn", 1, Pins("D20"), IOStandard("LVCMOS33")),
    ("user_btn", 2, Pins("L20"), IOStandard("LVCMOS33")),
    ("user_btn", 3, Pins("L19"), IOStandard("LVCMOS33")),

	# SPI
    ("spi", 0,
        Subsignal("clk",  Pins("H15")),
        Subsignal("cs_n", Pins("F16")),
        Subsignal("mosi", Pins("T12")),
        Subsignal("miso", Pins("W15")),
        IOStandard("LVCMOS33"),
    ),

	# I2C
    ("i2c", 0,
        Subsignal("scl",  Pins("P16")),
        Subsignal("sda",  Pins("P15")),
        IOStandard("LVCMOS33"),
    ),

	# Audio
    ("audio", 0,
        Subsignal("pwm", Pins("R18")), # FIXME
        Subsignal("sd", Pins("T17")), # FIXME
        IOStandard("LVCMOS33"),
    ),

    # HDMI In
    ("hdmi_in", 0,
        Subsignal("clk_p",   Pins("H17"), IOStandard("TMDS_33")),
        Subsignal("clk_n",   Pins("P19"), IOStandard("TMDS_33")),
        Subsignal("data0_p", Pins("V20"), IOStandard("TMDS_33")),
        Subsignal("data0_n", Pins("W20"), IOStandard("TMDS_33")),
        Subsignal("data1_p", Pins("T20"), IOStandard("TMDS_33")),
        Subsignal("data1_n", Pins("U20"), IOStandard("TMDS_33")),
        Subsignal("data2_p", Pins("N20"), IOStandard("TMDS_33")),
        Subsignal("data2_n", Pins("P20"), IOStandard("TMDS_33")),
        Subsignal("scl",     Pins("U14"), IOStandard("LVCMOS33")),
        Subsignal("sda",     Pins("U15"), IOStandard("LVCMOS33")),
        Subsignal("hpd_en",  Pins("T19"), IOStandard("LVCMOS33")),
        Subsignal("cec",     Pins("H17"), IOStandard("LVCMOS33")),
    ),

    # HDMI Out
    ("hdmi_out", 0,
        Subsignal("clk_p",   Pins("L16"), IOStandard("TMDS_33")),
        Subsignal("clk_n",   Pins("L17"), IOStandard("TMDS_33")),
        Subsignal("data0_p", Pins("K17"), IOStandard("TMDS_33")),
        Subsignal("data0_n", Pins("K18"), IOStandard("TMDS_33")),
        Subsignal("data1_p", Pins("K19"), IOStandard("TMDS_33")),
        Subsignal("data1_n", Pins("J19"), IOStandard("TMDS_33")),
        Subsignal("data2_p", Pins("J18"), IOStandard("TMDS_33")),
        Subsignal("data2_n", Pins("H18"), IOStandard("TMDS_33")),
        Subsignal("scl",     Pins("M17"), IOStandard("LVCMOS33")),
        Subsignal("sda",     Pins("M18"), IOStandard("LVCMOS33")),
        Subsignal("cec",     Pins("G15"), IOStandard("LVCMOS33")),
        Subsignal("hdp",     Pins("R19"), IOStandard("LVCMOS33")),
    ),

    # PS7
    ("ps7_clk",   0, Pins(1)),
    ("ps7_porb",  0, Pins(1)),
    ("ps7_srstb", 0, Pins(1)),
    ("ps7_mio",   0, Pins(54)),
    ("ps7_ddram", 0,
        Subsignal("addr",    Pins(15)),
        Subsignal("ba",      Pins(3)),
        Subsignal("cas_n",   Pins(1)),
        Subsignal("ck_n",    Pins(1)),
        Subsignal("ck_p",    Pins(1)),
        Subsignal("cke",     Pins(1)),
        Subsignal("cs_n",    Pins(1)),
        Subsignal("dm",      Pins(4)),
        Subsignal("dq",      Pins(32)),
        Subsignal("dqs_n",   Pins(4)),
        Subsignal("dqs_p",   Pins(4)),
        Subsignal("odt",     Pins(1)),
        Subsignal("ras_n",   Pins(1)),
        Subsignal("reset_n", Pins(1)),
        Subsignal("we_n",    Pins(1)),
        Subsignal("vrn",     Pins(1)),
        Subsignal("vrp",     Pins(1)),

    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    # access a pin with `pmoda:N`, where N is:
    #   N: 0  1  2  3  4  5  6  7
    # Pin: 1  2  3  4  7  8  9 10
    # Bank 13
    ("pmoda", "Y18 Y19 Y16 Y17 U18 U19 W18 W19"),
    ("pmodb", "W14 Y14 T11 T10 V16 W16 V12 W13"),
    ("ck_io", {
		"ck_ioa"  : "Y13",

        # Outer Digital Header
		"ck_io0"  : "T14",
        "ck_io1"  : "U12",
        "ck_io2"  : "U13",
        "ck_io3"  : "V13",
        "ck_io4"  : "V15",
        "ck_io5"  : "T15",
        "ck_io6"  : "R16",
        "ck_io7"  : "U17",
        "ck_io8"  : "V17",
        "ck_io9"  : "V18",
        "ck_io10" : "T16",
        "ck_io11" : "R17",
        "ck_io12" : "P18",
        "ck_io13" : "N17",

		# Inner Digital Header
        # Only for Arty Z7 20
        "ck_io26" : "U5",
        "ck_io27" : "V5",
        "ck_io28" : "V6",
        "ck_io29" : "U7",
        "ck_io30" : "V7",
        "ck_io31" : "U8",
        "ck_io32" : "V8",
        "ck_io33" : "V10",
        "ck_io34" : "W10",
        "ck_io35" : "W6",
        "ck_io36" : "Y6",
        "ck_io37" : "Y7",
        "ck_io38" : "W8",
        "ck_io39" : "Y8",
        "ck_io40" : "W9",
        "ck_io41" : "Y9",

        # Outer Analog Header as Digital IO
        # Only for Arty Z7 20
        "ck_a0" : "Y11",
        "ck_a1" : "Y12",
        "ck_a2" : "W11",
        "ck_a3" : "V11",
        "ck_a4" : "T5",
        "ck_a5" : "U10",

        # Inner Analog Header as Digital IO
        "ck_a6"  : "F19",
        "ck_a7"  : "F20",
        "ck_a8"  : "C20",
        "ck_a9"  : "B20",
        "ck_a10" : "B19",
        "ck_a11" : "A20",
	}),
    ("XADC", {
        # Outer Analog Header
        "vaux1_p"  : "E17",
        "vaux1_n"  : "B18",
        "vaux9_p"  : "E18",
        "vaux9_n"  : "E19",
        "vaux6_p"  : "K14",
        "vaux6_n"  : "J14",
        "vaux15_p" : "K16",
        "vaux15_n" : "J16",
        "vaux5_p"  : "J20",
        "vaux5_n"  : "H20",
        "vaux13_p" : "G19",
        "vaux13_n" : "G20",

        # Inner Analog Header
        "vaux12_p" : "F19",
        "vaux12_n" : "F20",
        "vaux0_p"  : "C20",
        "vaux0_n"  : "B20",
        "vaux8_p"  : "B19",
        "vaux8_n"  : "A19",
    })
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "clk125"
    default_clk_period = 1e9/125e6

    def __init__(self, variant="z7-20", toolchain="vivado"):
        device = {
            "z7-10": "xc7z010clg400-1",
            "z7-20": "xc7z020clg400-1"
        }[variant]
        self.board = {
            "z7-10": "arty_z7_10",
            "z7-20": "arty_z7_20"
        }[variant]

        XilinxPlatform.__init__(self, device, _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk125", loose=True), 1e9/125e6)
