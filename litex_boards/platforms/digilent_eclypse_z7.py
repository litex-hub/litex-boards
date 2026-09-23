#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 Gwenhael Goavec-Merou <gwenhael.goavec-merou@trabucayre.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform
from litex.build.openfpgaloader import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk125", 0, Pins("D18"), IOStandard("LVCMOS33")),

    # Buttons
    ("user_btn", 0, Pins("C17"), IOStandard("LVCMOS33")),
    ("user_btn", 1, Pins("C18"), IOStandard("LVCMOS33")),

    # Leds
    ("rgb_led", 0,
        Subsignal("r", Pins("B17")),
        Subsignal("g", Pins("B16")),
        Subsignal("b", Pins("A17")),
        IOStandard("LVCMOS33"),
    ),
    ("rgb_led", 1,
        Subsignal("r", Pins("A19")),
        Subsignal("g", Pins("A18")),
        Subsignal("b", Pins("A16")),
        IOStandard("LVCMOS33"),
    ),

    # Crypto
    ("crypto_sda", 0, Pins("D22"), IOStandard("LVCMOS33")),

    # Misc
    ("mcu_rsvd", 0, Pins("B22"), IOStandard("LVCMOS33")),
    ("mcu_rsvd", 1, Pins("B21"), IOStandard("LVCMOS33")),

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
    ("pmod_ja", "B15 C15 D15 E16 E15 F17 F16 G16"),
    ("pmod_jb", "G15 D16 D17 E18 F18 G17 H18 H17"),

    ("syzygy_a", {
        "c2p_clk_p" : "N19",
        "c2p_clk_n" : "N20",
        "p2c_clk_p" : "M19",
        "p2c_clk_n" : "M20",
        "s0_d0_p"   : "T16",
        "s1_d1_p"   : "R19",
        "s2_d0_n"   : "T17",
        "s3_d1_n"   : "T19",
        "s4_d2_p"   : "R18",
        "s5_d3_p"   : "P17",
        "s6_d2_n"   : "T18",
        "s7_d3_n"   : "P18",
        "s8_d4_p"   : "P16",
        "s9_d5_p"   : "N15",
        "s10_d4_n"  : "R16",
        "s11_d5_n"  : "P15",
        "s12_d6_p"  : "J18",
        "s13_d7_p"  : "J20",
        "s14_d6_n"  : "K18",
        "s15_d7_n"  : "K21",
        "s16"       : "L19",
        "s17"       : "K20",
        "s18"       : "L18",
        "s19"       : "K19",
        "s20"       : "L22",
        "s21"       : "J22",
        "s22"       : "L21",
        "s23"       : "J21",
        "s24"       : "N22",
        "s25"       : "P22",
        "s26"       : "M21",
        "s27"       : "M22",
    }),

    ("syzygy_b", {
        "c2p_clk_p" : "W16",
        "c2p_clk_n" : "Y16",
        "p2c_clk_p" : "W17",
        "p2c_clk_n" : "W18",
        "s0_d0_p"   : "W15",
        "s1_d1_p"   : "V13",
        "s2_d0_n"   : "Y15",
        "s3_d1_n"   : "W13",
        "s4_d2_p"   : "Y13",
        "s5_d3_p"   : "AB14",
        "s6_d2_n"   : "AA13",
        "s7_d3_n"   : "AB15",
        "s8_d4_p"   : "Y14",
        "s9_d5_p"   : "V14",
        "s10_d4_n"  : "AA14",
        "s11_d5_n"  : "V15",
        "s12_d6_p"  : "AA22",
        "s13_d7_p"  : "Y20",
        "s14_d6_n"  : "AB22",
        "s15_d7_n"  : "Y21",
        "s16"       : "AA18",
        "s17"       : "AA19",
        "s18"       : "Y18",
        "s19"       : "Y19",
        "s20"       : "AB20",
        "s21"       : "AB21",
        "s22"       : "AB19",
        "s23"       : "AA21",
        "s24"       : "U16",
        "s25"       : "U15",
        "s26"       : "V17",
        "s27"       : "U17",
    }),
]

# PS7 config ---------------------------------------------------------------------------------------

ps7_config = {
    "PCW_FPGA_FCLK0_ENABLE"              : "1",
    "PCW_FPGA0_PERIPHERAL_FREQMHZ"       : "100",
    "PCW_PRESET_BANK1_VOLTAGE"           : "LVCMOS 1.8V",
    "PCW_USE_S_AXI_GP0"                  : "1",
    "PCW_CRYSTAL_PERIPHERAL_FREQMHZ"     : "33.333333",
    "PCW_APU_PERIPHERAL_FREQMHZ"         : "666.666687",

    "PCW_GPIO_MIO_GPIO_ENABLE"           : "1",
    "PCW_GPIO_MIO_GPIO_IO"               : "MIO",

    "PCW_QSPI_PERIPHERAL_ENABLE"         : "1",
    "PCW_QSPI_PERIPHERAL_FREQMHZ"        : "200",
    "PCW_QSPI_QSPI_IO"                   : "MIO 1 .. 6",
    "PCW_QSPI_GRP_SINGLE_SS_ENABLE"      : "1",
    "PCW_QSPI_GRP_SINGLE_SS_IO"          : "MIO 1 .. 6",
    "PCW_QSPI_GRP_FBCLK_ENABLE"          : "1",
    "PCW_QSPI_GRP_FBCLK_IO"              : "MIO 8",

    "PCW_SDIO_PERIPHERAL_FREQMHZ"        : "50",
    "PCW_UART_PERIPHERAL_FREQMHZ"        : "100",

    # USB.
    "PCW_USB_RESET_ENABLE"               : "1",
    "PCW_USB_RESET_SELECT"               : "Share reset pin",
    "PCW_USB0_PERIPHERAL_ENABLE"         : "1",
    "PCW_USB0_USB0_IO"                   : "MIO 28 .. 39",
    "PCW_USB0_RESET_ENABLE"              : "1",
    "PCW_USB0_RESET_IO"                  : "MIO 46",
    "PCW_USB0_PERIPHERAL_FREQMHZ"        : "60",

    "PCW_DDR_RAM_HIGHADDR"               : "0x3FFFFFFF",
    "PCW_UIPARAM_DDR_PARTNO"             : "MT41K256M16 RE-125",
    "PCW_UIPARAM_DDR_MEMORY_TYPE"        : "DDR 3 (Low Voltage)",
    "PCW_UIPARAM_DDR_SPEED_BIN"          : "DDR3_1066F",
    "PCW_UIPARAM_DDR_DRAM_WIDTH"         : "16 Bits",
    "PCW_UIPARAM_DDR_BUS_WIDTH"          : "32 Bit",
    "PCW_UIPARAM_DDR_FREQ_MHZ"           : "533.333313",
    "PCW_UIPARAM_DDR_BOARD_DELAY0"       : "0.311",
    "PCW_UIPARAM_DDR_BOARD_DELAY1"       : "0.311",
    "PCW_UIPARAM_DDR_BOARD_DELAY2"       : "0.304",
    "PCW_UIPARAM_DDR_BOARD_DELAY3"       : "0.304",
    "PCW_UIPARAM_DDR_DQS_TO_CLK_DELAY_0" : "0.202",
    "PCW_UIPARAM_DDR_DQS_TO_CLK_DELAY_1" : "0.202",
    "PCW_UIPARAM_DDR_DQS_TO_CLK_DELAY_2" : "0.029",
    "PCW_UIPARAM_DDR_DQS_TO_CLK_DELAY_3" : "0.031",

    # Ethernet Phy Reset
    "PCW_ENET_RESET_ENABLE"              : "1",
    "PCW_ENET_RESET_SELECT"              : "Share reset pin",
    "PCW_ENET0_RESET_ENABLE"             : "1",
    "PCW_ENET0_RESET_IO"                 : "MIO 9",

    # I2C Phy Reset
    "PCW_I2C_RESET_ENABLE"               : "1",
    "PCW_I2C_RESET_SELECT"               : "Share reset pin",

    # MIO
    "PCW_MIO_0_PULLUP"                   : "enabled",
    "PCW_MIO_0_IOTYPE"                   : "LVCMOS 3.3V",
    "PCW_MIO_0_DIRECTION"                : "inout",
    "PCW_MIO_0_SLEW"                     : "slow",
    "PCW_MIO_7_PULLUP"                   : "disabled",
    "PCW_MIO_7_IOTYPE"                   : "LVCMOS 3.3V",
    "PCW_MIO_7_DIRECTION"                : "out",
    "PCW_MIO_7_SLEW"                     : "slow",
    "PCW_MIO_10_PULLUP"                  : "disabled",
    "PCW_MIO_10_IOTYPE"                  : "LVCMOS 3.3V",
    "PCW_MIO_10_DIRECTION"               : "inout",
    "PCW_MIO_10_SLEW"                    : "slow",
    "PCW_MIO_11_PULLUP"                  : "disabled",
    "PCW_MIO_11_IOTYPE"                  : "LVCMOS 3.3V",
    "PCW_MIO_11_DIRECTION"               : "inout",
    "PCW_MIO_11_SLEW"                    : "slow",

    "PCW_MIO_48_PULLUP"                  : "enabled",
    "PCW_MIO_48_IOTYPE"                  : "LVCMOS 1.8V",
    "PCW_MIO_48_DIRECTION"               : "inout",
    "PCW_MIO_48_SLEW"                    : "slow",
    "PCW_MIO_49_PULLUP"                  : "enabled",
    "PCW_MIO_49_IOTYPE"                  : "LVCMOS 1.8V",
    "PCW_MIO_49_DIRECTION"               : "inout",
    "PCW_MIO_49_SLEW"                    : "slow",
    "PCW_MIO_50_PULLUP"                  : "enabled",
    "PCW_MIO_50_IOTYPE"                  : "LVCMOS 1.8V",
    "PCW_MIO_50_DIRECTION"               : "inout",
    "PCW_MIO_50_SLEW"                    : "slow",
    "PCW_MIO_51_PULLUP"                  : "enabled",
    "PCW_MIO_51_IOTYPE"                  : "LVCMOS 1.8V",
    "PCW_MIO_51_DIRECTION"               : "inout",
    "PCW_MIO_51_SLEW"                    : "slow",
}

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk125"
    default_clk_freq   = 125e6
    default_clk_period = 1e9/default_clk_freq

    def __init__(self, toolchain="vivado"):
        self.ps7_config = ps7_config
        Xilinx7SeriesPlatform.__init__(self, "xc7z020-clg484-1", _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        return OpenFPGALoader(cable="digilent", fpga_part="xc7z020clg484")

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk125", loose=True), self.default_clk_period)
