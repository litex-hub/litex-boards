#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 Neil Liu <wetone.liu@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform, VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk50",    0, Pins("U18"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led", 0, Pins("M14"),  IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("M15"),  IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("K16"),  IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("J16"),  IOStandard("LVCMOS33")),

    # Buttons
    ("user_btn", 0, Pins("N15"), IOStandard("LVCMOS33")),
    ("user_btn", 1, Pins("N16"), IOStandard("LVCMOS33")),
    ("user_btn", 2, Pins("T17"), IOStandard("LVCMOS33")),
    ("user_btn", 3, Pins("R17"), IOStandard("LVCMOS33")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("W19"), IOStandard("LVCMOS33")),
        Subsignal("rx", Pins("W18"), IOStandard("LVCMOS33")),
    ),

    # HDMI
    ("hdmi", 0,
        Subsignal("clk_p",   Pins("N18"), IOStandard("TMDS_33")),
        Subsignal("clk_n",   Pins("P19"), IOStandard("TMDS_33")),
        Subsignal("data0_p", Pins("V20"), IOStandard("TMDS_33")),
        Subsignal("data0_n", Pins("W20"), IOStandard("TMDS_33")),
        Subsignal("data1_p", Pins("T20"), IOStandard("TMDS_33")),
        Subsignal("data1_n", Pins("U20"), IOStandard("TMDS_33")),
        Subsignal("data2_p", Pins("N20"), IOStandard("TMDS_33")),
        Subsignal("data2_n", Pins("P20"), IOStandard("TMDS_33")),
        Subsignal("scl",     Pins("R18"), IOStandard("LVCMOS33")),
        Subsignal("sda",     Pins("R16"), IOStandard("LVCMOS33")),
        Subsignal("hpd_en",  Pins("Y19"), IOStandard("LVCMOS33")),
        Subsignal("cec",     Pins("Y18"), IOStandard("LVCMOS33")),
    ),

    # PS7
    ("ps7_clk",   0, Pins("E7")),
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
    ("j10",
        "W19 W18 R14 P14 Y17 Y16 W15 V15",
        "Y14 W14 P18 N17 U15 U14 P16 P15",
        "U17 T16 V18 V17 T15 T14 V13 U13",
        "W13 V12 U12 T12 T10 T11 A20 B19",
        "B20 C20"
    ),
    ("j11",
        "F17 F16 F20 F19 G20 G19 H18 J18",
        "L20 L19 M20 M19 K18 K17 J19 K19",
        "H20 J20 L17 L16 M18 M17 D20 D19",
        "E19 E18 G18 G17 H17 H16 G15 H15",
        "J14 K14"
    ),
]

# PS7 config ---------------------------------------------------------------------------------------

ps7_config_variants = {
    "common" : {
        "PCW_FPGA_FCLK0_ENABLE"         : "1",
        "PCW_FPGA0_PERIPHERAL_FREQMHZ"  : "100",
        "PCW_S_AXI_HP0_FREQMHZ"         : "100",
        "PCW_S_AXI_HP0_DATA_WIDTH"      : "32",
        "PCW_EN_UART1"                  : "1",
        "PCW_UART1_PERIPHERAL_ENABLE"   : "1",
        "PCW_UART1_UART1_IO"            : "MIO 48 .. 49",
        "PCW_PRESET_BANK1_VOLTAGE"      : "LVCMOS 1.8V",
        "PCW_USE_S_AXI_HP0"             : "1",
        "PCW_USB0_PERIPHERAL_ENABLE"    : "1",
        "PCW_UIPARAM_DDR_PARTNO"        : "MT41K256M16 RE-125",
    },
}

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk50"
    default_clk_freq   = 50e6
    default_clk_period = 1e9/default_clk_freq

    def __init__(self):
        self.ps7_config = ps7_config_variants["common"]
        Xilinx7SeriesPlatform.__init__(self, "xc7z020clg400-2", _io, _connectors, toolchain="vivado")

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), self.default_clk_period)

