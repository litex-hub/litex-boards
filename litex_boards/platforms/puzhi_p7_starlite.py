#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 Gwenhael Goavec-Merou <gwenhael.goavec-merou@trabucayre.com>
# SPDX-License-Identifier: BSD-2-Clause
#
# PZ-Starlite :
# - PZ7010-Starlite (xc7z010): https://www.puzhitech.com/en/detail/373.html
# - PZ7010-Starlite (xc7z010): https://www.puzhitech.com/en/detail/374.html

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform
from litex.build.openfpgaloader import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk50", 0, Pins("U18"), IOStandard("LVCMOS33")),
    ("rst_n", 0, Pins("U19"), IOStandard("LVCMOS33")), # Also connected to PS_PORB

    # Leds
    ("user_led", 0, Pins("R19"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("V13"), IOStandard("LVCMOS33")),

    # Buttons
    ("user_btn", 0, Pins("G14"), IOStandard("LVCMOS33")),
    ("user_btn", 1, Pins("J15"), IOStandard("LVCMOS33")),

    # Serial (JM1 Pins 37 & 39)
    ("serial", 0,
        Subsignal("tx", Pins("M19")),
        Subsignal("rx", Pins("M20")),
        IOStandard("LVCMOS33")
    ),

    # EEPROM (AT24C64D)
    ("eeprom", 0,
        Subsignal("sda", Pins("W15")),
        Subsignal("scl", Pins("W15")),
        IOStandard("LVCMOS33"),
    ),

    # RGMII Ethernet (RTL8211F) on board
    ("eth_clocks", 0,
        Subsignal("tx", Pins("V20")),
        Subsignal("rx", Pins("N18")),
        IOStandard("LVCMOS33")
    ),
    ("eth", 0,
        Subsignal("mdio",    Pins("U15")),
        Subsignal("mdc",     Pins("U14")),
        Subsignal("rx_ctl",  Pins("P19")),
        Subsignal("rx_data", Pins("Y18 Y19 V16 W16")),
        Subsignal("tx_ctl",  Pins("W20")),
        Subsignal("tx_data", Pins("N20 P20 T20 U20")),
        IOStandard("LVCMOS33")
    ),

    # HDMI
    ("hdmi", 0,
        Subsignal("clk_p",       Pins("T17"), IOStandard("TMDS_33")),
        Subsignal("clk_n",       Pins("R18"), IOStandard("TMDS_33")),
        Subsignal("data0_p",     Pins("V17"), IOStandard("TMDS_33")),
        Subsignal("data0_n",     Pins("V18"), IOStandard("TMDS_33")),
        Subsignal("data1_p",     Pins("W18"), IOStandard("TMDS_33")),
        Subsignal("data1_n",     Pins("W19"), IOStandard("TMDS_33")),
        Subsignal("data2_p",     Pins("N17"), IOStandard("TMDS_33")),
        Subsignal("data2_n",     Pins("P18"), IOStandard("TMDS_33")),
        Subsignal("scl",         Pins("R17"), IOStandard("LVCMOS33")),
        Subsignal("sda",         Pins("R16"), IOStandard("LVCMOS33")),
        Subsignal("hdp",         Pins("P15"), IOStandard("LVCMOS33")),
        Subsignal("hdmi_out_en", Pins("P16"), IOStandard("LVCMOS33")),
        Subsignal("cec",         Pins("T19"), IOStandard("LVCMOS33")),
    ),

    # PS7
    ("ps7_clk", 0,   Pins(1)),
    ("ps7_porb", 0,  Pins(1)),
    ("ps7_srstb", 0, Pins(1)),
    ("ps7_mio", 0,   Pins(54)),
    ("ps7_ddram", 0,
        Subsignal("addr",    Pins(15)),
        Subsignal("ck_p",    Pins(1)),
        Subsignal("ck_n",    Pins(1)),
        Subsignal("cke",     Pins(1)),
        Subsignal("reset_n", Pins(1)),
        Subsignal("cs_n",    Pins(1)),
        Subsignal("we_n",    Pins(1)),
        Subsignal("ras_n",   Pins(1)),
        Subsignal("cas_n",   Pins(1)),
        Subsignal("ba",      Pins(3)),
        Subsignal("dm",      Pins(2)),
        Subsignal("odt",     Pins(1)),
        Subsignal("dq",      Pins(16)),
        Subsignal("dqs_p",   Pins(2)),
        Subsignal("dqs_n",   Pins(2)),
        Subsignal("vrp",     Pins(1)),
        Subsignal("vrn",     Pins(1)),
    ),
]

_io_xc7z020 = [
    # MIPI.
    ("camera", 0,
        Subsignal("mclk",    Pins("W8")),
        Subsignal("clkp",    Pins("Y6")),
        Subsignal("clkn",    Pins("Y7")),
        Subsignal("lp_clkp", Pins("Y9")),
        Subsignal("lp_clkn", Pins("Y8")),
        Subsignal("dp",      Pins("U7  T9")),
        Subsignal("dn",      Pins("V7 U10")),
        Subsignal("lp_dp",   Pins("W10 U9")),
        Subsignal("lp_dn",   Pins(" W9 U8")),
        Subsignal("reset_n", Pins("W11")),
        IOStandard("LVCMOS33"),
    ),

    ("mipi_i2c", 0,
        Subsignal("scl",     Pins("Y11")),
        Subsignal("sda",     Pins("T5")),
        IOStandard("LVCMOS33")
    ),
]

_connectors = [
    ("JM1", {
          1: "5V",   2: "3V3",
          3: "GND",  4: "GND",
          5: "H16",  6: "E17",
          7: "H17",  8: "D18",
          9: "E18", 10: "F16",
         11: "E19", 12: "F17",
         13: "G17", 14: "B19",
         15: "G18", 16: "A20",
         17: "D19", 18: "C20",
         19: "D20", 20: "B20",
         21: "J18", 22: "K19",
         23: "H18", 24: "J19",
         25: "K17", 26: "M17",
         27: "K18", 28: "M18",
         29: "L16", 30: "F19",
         31: "L17", 32: "F20",
         33: "GND", 34: "GND",
         35: "GND", 36: "GND",
         37: "M19", 38: "L19",
         39: "M20", 40: "L20",
    }),
    ("JM2", {
          1: "5V",   2: "3V3",
          3: "GND",  4: "GND",
          5: "G19",  6: "J20",
          7: "G20",  8: "H20",
          9: "H15", 10: "K14",
         11: "G15", 12: "J14",
         13: "K16", 14: "L14",
         15: "J16", 16: "L15",
         17: "N15", 18: "M14",
         19: "N16", 20: "M15",
         21: "T16", 22: "T14",
         23: "U17", 24: "T15",
         25: "P14", 26: "T12",
         27: "R14", 28: "U12",
         29: "T11", 30: "Y16",
         31: "T10", 32: "Y17",
         33: "GND", 34: "GND",
         35: "GND", 36: "GND",
         37: "V12", 38: "W14",
         39: "W13", 40: "Y14",
    })
]

# PS7 config ---------------------------------------------------------------------------------------

ps7_config = {
    # Global
    "PCW_PRESET_BANK1_VOLTAGE"       : "LVCMOS 1.8V",

    # Ref Clk
    "PCW_CRYSTAL_PERIPHERAL_FREQMHZ" : "33.333333",

    # Core Frequency
    "PCW_APU_PERIPHERAL_FREQMHZ"     : "666.666687",

    # DDR3
    "PCW_UIPARAM_DDR_BUS_WIDTH"      : "16 Bit",
    "PCW_UIPARAM_DDR_MEMORY_TYPE"    : "DDR 3 (Low Voltage)",
    "PCW_UIPARAM_DDR_PARTNO"         : "MT41K256M16 RE-125",

    # QSPI
    "PCW_QSPI_PERIPHERAL_FREQMHZ"    : "200",
    "PCW_QSPI_PERIPHERAL_ENABLE"     : "1",
    "PCW_QSPI_QSPI_IO"               : "MIO 1 .. 6",
    "PCW_QSPI_GRP_SINGLE_SS_ENABLE"  : "1",
    "PCW_QSPI_GRP_SS1_ENABLE"        : "0",
    "PCW_SINGLE_QSPI_DATA_MODE"      : "x4",
    "PCW_QSPI_GRP_IO1_ENABLE"        : "0",
    "PCW_QSPI_GRP_FBCLK_ENABLE"      : "0",

    # USB0
    "PCW_USB0_PERIPHERAL_FREQMHZ"    : "60",
    "PCW_USB0_PERIPHERAL_ENABLE"     : "1",
    "PCW_USB0_USB0_IO"               : "MIO 28 .. 39",
    "PCW_USB0_RESET_ENABLE"          : "1",
    "PCW_USB0_RESET_IO"              : "MIO 46",

    "PCW_GPIO_MIO_GPIO_ENABLE"       : "1",
    "PCW_GPIO_MIO_GPIO_IO"           : "MIO",
}

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self, variant="xc7z020", toolchain="vivado"):
        assert variant in ["xc7z020", "xc7z010"]

        device     = f"{variant}clg400-2"
        io         = _io
        connectors = _connectors

        Xilinx7SeriesPlatform.__init__(self, device, io, connectors, toolchain=toolchain)
        self.ps7_config = ps7_config

        if variant in ["xc7z020"]:
            self.add_extension(_io_xc7z020)

    def create_programmer(self):
        return OpenFPGALoader(cable="ft232", index_chain=1)

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
