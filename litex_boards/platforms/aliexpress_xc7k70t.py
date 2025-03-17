#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2023 Hans Baier <hansfbaier@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform
from litex.build.openocd import OpenOCD

# This board is available here:
# https://www.aliexpress.com/item/1005005572549665.html

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk50",            0, Pins("E11"), IOStandard("LVCMOS33")),
    ("sma_global_clock", 0, Pins("C12"), IOStandard("LVCMOS33")),
    ("sma_global_clock", 1, Pins("C11"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led", 0, Pins("AD9"),  IOStandard("LVCMOS18")),
    ("user_led", 1, Pins("AD8"),  IOStandard("LVCMOS18")),
    ("user_led", 2, Pins("AC9"),  IOStandard("LVCMOS18")),
    ("user_led", 3, Pins("AC8"),  IOStandard("LVCMOS18")),

    # Buttons
    ("user_btn_n", 0, Pins("AF7"),  IOStandard("LVCMOS18")),
    ("user_btn_n", 1, Pins("AF8"),  IOStandard("LVCMOS18")),
    ("user_btn_n", 2, Pins("AE8"),  IOStandard("LVCMOS18")),
    ("user_btn_n", 3, Pins("AF9"),  IOStandard("LVCMOS18")),


    # Serial
    ("serial", 0,
        Subsignal("tx",  Pins("HR_IO:0")),
        Subsignal("rx",  Pins("HR_IO:1")),
        IOStandard("LVCMOS33")
    ),

    # SDRAM
    ("sdram_clock", 0, Pins("P23"), IOStandard("LVCMOS33"), Misc("SLEW=FAST")),
    ("sdram", 0,
        Subsignal("a",     Pins("L25 L24 K23 M26 G25 F24 H26 F23 E23 J26 M25 G24")),
        Subsignal("dq",    Pins("T23 T25 T24 R25 R23 R26 P24 P25 F25 H24 E26 H23 E25 J24 D26 J23")),
        Subsignal("ba",    Pins("K25 M24")),
        Subsignal("dm",    Pins("N23 G26")),
        Subsignal("ras_n", Pins("N24")),
        Subsignal("cas_n", Pins("K26")),
        Subsignal("we_n",  Pins("P26")),
        Subsignal("cs_n",  Pins("N26")),
        Subsignal("cke",   Pins("J25")),
        IOStandard("LVCMOS33"),
        Misc("SLEW = FAST")
    ),

    ("spiflash4x", 0,  # clock needs to be accessed through STARTUPE2
        Subsignal("cs_n", Pins("C23")),
        Subsignal("dq",   Pins("B24 A25 B22 A22")),
        IOStandard("LVCMOS33")
    ),
    ("spiflash8x", 0,
        Subsignal("clk",  Pins("A14")),
        Subsignal("cs_n", Pins("B11")),
        Subsignal("dq",   Pins("A13 A10 B10 B14 A15 B12 A12 B15")),
        IOStandard("LVCMOS33")
    ),

    # RGMII Ethernet
    ("eth_clocks", 0,
        Subsignal("tx",  Pins("AF13"), IOStandard("LVCMOS18")),
        Subsignal("rx",  Pins("AB11"), IOStandard("LVCMOS18"))
    ),
    ("eth", 0,
        # Subsignal("rst_n",   Pins("")),
        Subsignal("mdio",    Pins("AD13")),
        Subsignal("mdc",     Pins("AC13")),
        Subsignal("rx_ctl",  Pins("AF10")),
        Subsignal("rx_data", Pins("AE10 AE11 AF12 AE12")),
        Subsignal("tx_ctl",  Pins("AE13")),
        Subsignal("tx_data", Pins("AD10 AD11 AC11 AC12")),
        IOStandard("LVCMOS18")
    ),

    # camera connector I2C, has pull up resistors
    ("i2c", 0,
        Subsignal("scl", Pins("C13")),
        Subsignal("sda", Pins("C16")),
        IOStandard("LVCMOS33"),
    ),

    ("camera", 0,
        Subsignal("d",     Pins("C17 B16 A17 B17 A18 D16 C18 D13")),
        Subsignal("vsync", Pins("C14")),
        Subsignal("xclk",  Pins("C19")),
        Subsignal("pclk",  Pins("E18")),
        Subsignal("pwdn",  Pins("D11")),
        Subsignal("reset", Pins("D15")),
        Subsignal("href",  Pins("D14")),
        IOStandard("LVCMOS33"),
    ),

    # HDMI out
    ("hdmi_out", 0,
        Subsignal("clk_p",   Pins("E10")),
        Subsignal("clk_n",   Pins("D10")),
        Subsignal("data0_p", Pins("D9")),
        Subsignal("data0_n", Pins("D8")),
        Subsignal("data1_p", Pins("C9")),
        Subsignal("data1_n", Pins("B9")),
        Subsignal("data2_p", Pins("A9")),
        Subsignal("data2_n", Pins("A8")),
        IOStandard("TMDS_33"),
    ),

    # PCIe
    ("pcie_x1", 0,
        Subsignal("rst_n", Pins("F8"), IOStandard("LVCMOS33")),
        Subsignal("clk_p", Pins("F5")),
        Subsignal("clk_n", Pins("F6")),
        Subsignal("rx_p",  Pins("B6")),
        Subsignal("rx_n",  Pins("B5")),
        Subsignal("tx_p",  Pins("A4")),
        Subsignal("tx_n",  Pins("A3"))
    ),
    ("pcie_x2", 0,
        Subsignal("rst_n", Pins("F8"), IOStandard("LVCMOS33")),
        Subsignal("clk_p", Pins("F5")),
        Subsignal("clk_n", Pins("F6")),
        Subsignal("rx_p",  Pins("B6 C4")),
        Subsignal("rx_n",  Pins("B5 C3")),
        Subsignal("tx_p",  Pins("A4 B2")),
        Subsignal("tx_n",  Pins("A3 B1"))
    ),
    ("pcie_x4", 0,
        Subsignal("rst_n", Pins("F8"), IOStandard("LVCMOS33")),
        Subsignal("clk_p", Pins("F5")),
        Subsignal("clk_n", Pins("F6")),
        Subsignal("rx_p",  Pins("B6 C4 E4 G4")),
        Subsignal("rx_n",  Pins("B5 C3 E3 G3")),
        Subsignal("tx_p",  Pins("A4 B2 D2 F2")),
        Subsignal("tx_n",  Pins("A3 B1 D1 F1"))
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    # 1.8V
    ("HP_IO", {
        "0_P"  :  "AE6",
        "0_N"  :  "AE5",
        "1_P"  :  "AD6",
        "1_N"  :  "AD5",
        "2_P"  :  "AF5",
        "2_N"  :  "AF4",
        "3_P"  :  "AD4",
        "3_N"  :  "AD3",
        "4_P"  :  "AF3",
        "4_N"  :  "AF2",
        "5_P"  :  "AE3",
        "5_N"  :  "AE2",
        "6_P"  :  "AB2",
        "6_N"  :  "AC2",
        "7_P"  :  "V2",
        "7_N"  :  "V1",
        "8_P"  :  "AA3",
        "8_N"  :  "AA2",
        "9_P"  :  "AB1",
        "9_N"  :  "AC1",
        "10_P" :  "W1",
        "10_N" :  "Y1",
        "11_P" :  "AD1",
        "11_N" :  "AE1",
    }),

    # 3.3V
    ("HR_IO", {
        0  : "D19",
        1  : "D18",
        2  : "C21",
        3  : "D20",
        4  : "C22",
        5  : "D21",
        6  : "C24",
        7  : "D23",
        8  : "D24",
        9  : "A19",
        10 : "B19",
        11 : "A20",
        12 : "B20",
        13 : "B21",
        14 : "A23",
        15 : "A24",
        16 : "B25",
        17 : "B26",
        18 : "C26",
        19 : "D25",
    }),

    # 3.3V
    ("CAM", {
        3  : "C14",
        4  : "C13", # has pull up resistor
        5  : "D14",
        6  : "C16", # has pull up resistor
        7  : "D15",
        8  : "C17",
        9  : "B16",
        10 : "A17",
        11 : "B17",
        12 : "A18",
        13 : "D16",
        14 : "C18",
        15 : "D13",
        16 : "E18",
        17 : "C19",
        18 : "D11",
    })
]
# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self, toolchain="vivado"):
        Xilinx7SeriesPlatform.__init__(self, "xc7k70t-fbg676-1", _io, _connectors, toolchain=toolchain)
        self.add_platform_command("""
set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]
""")
        self.toolchain.bitstream_commands  = ["set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]"]
        self.toolchain.additional_commands = ["write_cfgmem -force -format bin -interface spix4 -size 16 -loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"]

    def create_programmer(self):
        return OpenOCD("openocd_xc7_ft4232.cfg", "bscan_spi_xc7k70t.bit")

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50",         0, loose=True), 1e9/50e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:rx", 0, loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:tx", 0, loose=True), 1e9/125e6)
