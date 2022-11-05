#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019 Vamsi K Vytla <vamsi.vytla@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk200", 0,
        Subsignal("p", Pins("R3"), IOStandard("DIFF_SSTL15")),
        Subsignal("n", Pins("P3"), IOStandard("DIFF_SSTL15"))
    ),
    ("clk156", 0,
        Subsignal("p", Pins("M21"), IOStandard("LVDS_25")),
        Subsignal("n", Pins("M22"), IOStandard("LVDS_25"))
    ),
    ("cpu_reset", 0, Pins("U4"), IOStandard("SSTL15")),

    # Leds
    ("user_led", 0, Pins("M26"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("T24"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("T25"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("R26"), IOStandard("LVCMOS33")),

    # Serial
    ("serial", 0,
        Subsignal("cts", Pins("V19")),
        Subsignal("rts", Pins("W19")),
        Subsignal("tx",  Pins("U19")),
        Subsignal("rx",  Pins("T19")),
        IOStandard("LVCMOS18")
    ),

    # RGMII Ethernet
    ("eth_clocks", 0,
        Subsignal("tx", Pins("U22")),
        Subsignal("rx", Pins("U21")),
        IOStandard("LVCMOS18")
    ),
    ("eth", 0,
        Subsignal("rx_ctl",  Pins("U14")),
        Subsignal("rx_data", Pins("U17 V17 V16 V14")),
        Subsignal("tx_ctl",  Pins("T15")),
        Subsignal("tx_data", Pins("U16 U15 T18 T17")),
        Subsignal("rst_n",   Pins("V18")),
        Subsignal("mdc",     Pins("W18")),
        Subsignal("mdio",    Pins("T14")),
        Misc("SLEW=FAST"),
        Drive(16),
        IOStandard("LVCMOS18"),
    ),

    # DDR3 SDRAM
    ("ddram", 0,
        Subsignal("a", Pins(
            "M4 J3 J1 L4 K5 M7 K1 M6",
            "H1 K3 N7 L5 L7 N6 L3 K2"),
            IOStandard("SSTL15")),
        Subsignal("ba",    Pins("N1 M1 H2"), IOStandard("SSTL15")),
        Subsignal("ras_n", Pins("P1"), IOStandard("SSTL15")),
        Subsignal("cas_n", Pins("T4"), IOStandard("SSTL15")),
        Subsignal("we_n",  Pins("R1"), IOStandard("SSTL15")),
        Subsignal("cs_n",  Pins("T3"), IOStandard("SSTL15")),
        Subsignal("dm", Pins("AC6 AC4 AA3 U7 G1 F3 G5 H9"),
            IOStandard("SSTL15")),
        Subsignal("dq", Pins(
            "AB6 AA8  Y8 AB5 AA5  Y5  Y6  Y7",
            "AF4 AF5 AF3 AE3 AD3 AC3 AB4 AA4",
            "AC2 AB2 AF2 AE2  Y1  Y2 AC1 AB1",
            "Y3   W3  W6  V6  W4  W5  W1  V1",
            "G2   D1  E1  E2  F2  A2  A3  C2",
            "C3   D3  A4  B4  C4  D4  D5  E5",
            "F4   G4  K6  K7  K8  L8  J5  J6",
            "G6   H6  F7  F8  G8  H8  D6  E6"),
            IOStandard("SSTL15"),
            Misc("IN_TERM=UNTUNED_SPLIT_50")),
        Subsignal("dqs_p", Pins("V8 AD5 AD1 V3 C1 B5 J4 H7"),
            IOStandard("DIFF_SSTL15")),
        Subsignal("dqs_n", Pins("W8 AE5 AE1 V2 B1 A5 H4 G7"),
            IOStandard("DIFF_SSTL15")),
        Subsignal("clk_p", Pins("M2"), IOStandard("DIFF_SSTL15")),
        Subsignal("clk_n", Pins("L2"), IOStandard("DIFF_SSTL15")),
        Subsignal("cke",   Pins("P4"), IOStandard("SSTL15")),
        Subsignal("odt",   Pins("R2"), IOStandard("SSTL15")),
        Subsignal("reset_n", Pins("N8"), IOStandard("LVCMOS15")),
        Misc("SLEW=FAST"),
    ),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("P18")),
        #Subsignal("clk",  Pins("")), # Accessed through STARTUPE2
        Subsignal("mosi", Pins("R14")),
        Subsignal("miso", Pins("R15")),
        Subsignal("wp",   Pins("P14")),
        Subsignal("hold", Pins("N14")),
        IOStandard("LVCMOS33"),
    ),
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("P18")),
        #Subsignal("clk",  Pins("")), # Accessed through STARTUPE2
        Subsignal("dq",   Pins("R14 R15 P14 N14")),
        IOStandard("LVCMOS33")
    ),

    # PCIe
    ("pcie_x1", 0,
        Subsignal("rst_n", Pins("M20"), IOStandard("LVCMOS25")),
        Subsignal("clk_p", Pins("F11")),
        Subsignal("clk_n", Pins("E11")),
        Subsignal("rx_p",  Pins("D12")),
        Subsignal("rx_n",  Pins("C12")),
        Subsignal("tx_p",  Pins("D10")),
        Subsignal("tx_n",  Pins("C10"))
    ),

    ("pcie_x4", 0,
        Subsignal("rst_n", Pins("M20"), IOStandard("LVCMOS25")),
        Subsignal("clk_p", Pins("F11")),
        Subsignal("clk_n", Pins("E11")),
        Subsignal("rx_p",  Pins("D12 B13 D14 B11")),
        Subsignal("rx_n",  Pins("C12 A13 C14 A11")),
        Subsignal("tx_p",  Pins("D10 B9 D8 B7")),
        Subsignal("tx_n",  Pins("C10 A9 C8 A7"))
    ),

    # GTP RefClk
    ("gtp_refclk", 0,
     Subsignal("p", Pins("AA13")),
     Subsignal("n", Pins("AB13"))
    ),

    # SFP
    ("sfp", 0,
        Subsignal("txp", Pins("AC10")),
        Subsignal("txn", Pins("AD10")),
        Subsignal("rxp", Pins("AC12")),
        Subsignal("rxn", Pins("AD12")),
    ),
    ("sfp_mgt_clk_sel0", 0, Pins("B26"), IOStandard("LVCMOS25")),
    ("sfp_mgt_clk_sel1", 0, Pins("C24"), IOStandard("LVCMOS25")),
    ("sfp_tx_disable_n", 0, Pins("R18"), IOStandard("LVCMOS33")),
    ("sfp_rx_los",       0, Pins("R23"), IOStandard("LVCMOS33")),

    # Others
    ("vadj_on_b", 0, Pins("R16"), IOStandard("LVCMOS25")),

]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("HPC", {
      "CLK0_M2C_N" : "C19",
      "CLK0_M2C_P" : "D19",
      "CLK1_M2C_N" : "H22",
      "CLK1_M2C_P" : "H21",
      "LA00_CC_N"  : "C18",
      "LA00_CC_P"  : "D18",
      "LA01_CC_N"  : "E18",
      "LA01_CC_P"  : "E17",
      "LA02_N"     : "H15",
      "LA02_P"     : "H14",
      "LA03_N"     : "F17",
      "LA03_P"     : "G17",
      "LA04_N"     : "F19",
      "LA04_P"     : "F18",
      "LA05_N"     : "F15",
      "LA05_P"     : "G15",
      "LA06_N"     : "F20",
      "LA06_P"     : "G19",
      "LA07_N"     : "G16",
      "LA07_P"     : "H16",
      "LA08_N"     : "B17",
      "LA08_P"     : "C17",
      "LA09_N"     : "D16",
      "LA09_P"     : "E16",
      "LA10_N"     : "A18",
      "LA10_P"     : "A17",
      "LA11_N"     : "A19",
      "LA11_P"     : "B19",
      "LA12_N"     : "D20",
      "LA12_P"     : "E20",
      "LA13_N"     : "A20",
      "LA13_P"     : "B20",
      "LA14_N"     : "B21",
      "LA14_P"     : "C21",
      "LA15_N"     : "A22",
      "LA15_P"     : "B22",
      "LA16_N"     : "D21",
      "LA16_P"     : "E21",
      "LA17_CC_N"  : "J21",
      "LA17_CC_P"  : "K21",
      "LA18_CC_N"  : "G21",
      "LA18_CC_P"  : "G20",
      "LA19_N"     : "L14",
      "LA19_P"     : "M14",
      "LA20_N"     : "M17",
      "LA20_P"     : "M16",
      "LA21_N"     : "H19",
      "LA21_P"     : "J19",
      "LA22_N"     : "L18",
      "LA22_P"     : "L17",
      "LA23_N"     : "J20",
      "LA23_P"     : "K20",
      "LA24_N"     : "H18",
      "LA24_P"     : "J18",
      "LA25_N"     : "F22",
      "LA25_P"     : "G22",
      "LA26_N"     : "H24",
      "LA26_P"     : "J24",
      "LA27_N"     : "E23",
      "LA27_P"     : "F23",
      "LA28_N"     : "K23",
      "LA28_P"     : "K22",
      "LA29_N"     : "F24",
      "LA29_P"     : "G24",
      "LA30_N"     : "D25",
      "LA30_P"     : "E25",
      "LA31_N"     : "D26",
      "LA31_P"     : "E26",
      "LA32_N"     : "G26",
      "LA32_P"     : "H26",
      "LA33_N"     : "F25",
      "LA33_P"     : "G25",
      "PRSNT_M2C_L"         : "N16",
      "PWR_GOOD_FLASH_RST_B": "P15"}
    ),
    ("XADC", {
        "GPIO0"   : "H17",
        "GPIO1"   : "E22",
        "GPIO2"   : "K18",
        "GPIO3"   : "L19",
        "VAUX0_N" : "J16",
        "VAUX0_P" : "K15",
        "VAUX8_N" : "J15",
        "VAUX8_P" : "J14",
        }
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk156"
    default_clk_period = 1e9/156.5e6

    def __init__(self, toolchain="vivado"):
        Xilinx7SeriesPlatform.__init__(self, "xc7a200t-fbg676-2", _io, _connectors, toolchain=toolchain)
        self.toolchain.bitstream_commands = ["set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]"]
        self.toolchain.additional_commands = ["write_cfgmem -force -format bin -interface spix4 -size 16 -loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"]
        self.add_platform_command("set_property INTERNAL_VREF 0.750 [get_iobanks 33]")
        self.add_platform_command("set_property INTERNAL_VREF 0.750 [get_iobanks 34]")
        self.add_platform_command("set_property INTERNAL_VREF 0.750 [get_iobanks 35]")

    def create_programmer(self):
        return OpenOCD("openocd_xc7_ft2232.cfg", "bscan_spi_xc7a200t.bit")

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk200",        loose=True), 1e9/200e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:rx", loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:tx", loose=True), 1e9/125e6)
