#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2018-2019 Rohit Singh <rohit@rohitksingh.in>
# Copyright (c) 2019 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk100", 0, Pins("F22"), IOStandard("LVCMOS33")),
    ("clk150", 0,
        Subsignal("p", Pins("G24"), IOStandard("TMDS_33")),
        Subsignal("n", Pins("F24"), IOStandard("TMDS_33"))
    ),
    ("cpu_reset", 0, Pins("C26"), IOStandard("LVCMOS33"), Misc("PULLDOWN=True")), # Active high, pulldown needed.

    # Leds (activive-low)
    ("rgb_led", 0,
        Subsignal("r", Pins("J26")),
        Subsignal("g", Pins("H26")),
        Subsignal("b", Pins("G26")),
        IOStandard("LVCMOS33"),
    ),

    # FAN
    ("fan", 0, Pins("J25"), IOStandard("LVCMOS33")),

    # Serial
    ("serial", 0,
        Subsignal("tx",    Pins("H22")),
        Subsignal("rx",    Pins("K22")),
        Subsignal("rts",   Pins("L22")),
        Subsignal("cts",   Pins("L23")),
        Subsignal("cbus0", Pins("K23")),
        IOStandard("LVCMOS33")
    ),

    # XADC
    ("xadc", 0,
        Subsignal("adc_p", Pins("C16 A18 B17")),
        Subsignal("adc_n", Pins("B16 A19 A17")),
        Subsignal("v_p",   Pins("N12")),
        Subsignal("v_n",   Pins("P11")),
    ),

    # DDR3 SDRAM
    ("ddram", 0,
        Subsignal("a", Pins(
            "AF7 AE7 AC7 AB7 AA7 AC8 AC9 AA9",
            "AD8  V9 Y11  Y7 W10  Y8 Y10  W9"),
            IOStandard("SSTL135")),
        Subsignal("ba",    Pins("AA8 AD9 AB9"), IOStandard("SSTL135")),
        Subsignal("ras_n", Pins("AC13"), IOStandard("SSTL135")),
        Subsignal("cas_n", Pins("AC12"), IOStandard("SSTL135")),
        Subsignal("we_n",  Pins("AA13"), IOStandard("SSTL135")),
        Subsignal("cs_n",  Pins("AB12"), IOStandard("SSTL135")),
        Subsignal("dm", Pins(
            "W16 AD18 AE15 AB15 AD1 AC3 Y3 V6"),
            IOStandard("SSTL135")),
        Subsignal("dq", Pins(
            "V19   V16  Y17  V14  V17  V18  W14  W15",
            "AB17 AB19 AC18 AC19 AA19 AA20 AC17 AD19",
            "AD16 AD15 AF20 AE17 AF17 AF19 AF14 AF15",
            "AB16 AA15 AA14 AC14 AA18 AA17 AD14 AB14",
            "AE3   AE6  AE2  AF3  AD4  AE5  AE1  AF2",
            "AB6    Y6  AB4  AC4  AC6  AD6   Y5  AA4",
            "AB2   AC2   V1   W1   V2  AA3   Y1   Y2",
            "V4     V3   U2   U1   U7   W3   U6   U5"),
            IOStandard("SSTL135_T_DCI")),
        Subsignal("dqs_p", Pins("W18 AD20 AE18 Y15 AF5 AA5 AB1 W6"),
            IOStandard("DIFF_SSTL135")),
        Subsignal("dqs_n", Pins("W19 AE20 AF18 Y16 AF4 AB5 AC1 W5"),
            IOStandard("DIFF_SSTL135")),
        Subsignal("clk_p", Pins("V11"), IOStandard("DIFF_SSTL135")),
        Subsignal("clk_n", Pins("W11"), IOStandard("DIFF_SSTL135")),
        Subsignal("cke", Pins("AA10"),  IOStandard("SSTL135")),
        Subsignal("odt", Pins("AD13"),  IOStandard("SSTL135")),
        Subsignal("reset_n", Pins("AA2"), IOStandard("SSTL135")),
        Misc("SLEW=FAST"),
    ),

    # SPIFlash
    ("spiflash", 0,  # clock needs to be accessed through STARTUPE2
        Subsignal("cs_n", Pins("C23")),
        Subsignal("mosi", Pins("B24")),
        Subsignal("miso", Pins("A25")),
        Subsignal("wp",   Pins("B22")),
        Subsignal("hold", Pins("A22")),
        IOStandard("LVCMOS33"),
    ),
    ("spiflash4x", 0,  # clock needs to be accessed through STARTUPE2
        Subsignal("cs_n", Pins("C23")),
        Subsignal("dq",   Pins("B24", "A25", "B22", "A22")),
        IOStandard("LVCMOS33")
    ),

    # SDCard
    ("sdcard", 0,
        Subsignal("cmd", Pins("H24")),
        Subsignal("clk", Pins("G22")),
        Subsignal("dat", Pins("F25 E25 J23 H23")),
        IOStandard("LVCMOS33")
     ),

    # PCIe
    ("pcie_x1", 0,
        Subsignal("rst_n", Pins("E21"), IOStandard("LVCMOS33"), Misc("PULLUP=TRUE")),
        Subsignal("clk_p", Pins("K6")),
        Subsignal("clk_n", Pins("K5")),
        Subsignal("rx_p",  Pins("J4")),
        Subsignal("rx_n",  Pins("J3")),
        Subsignal("tx_p",  Pins("H2")),
        Subsignal("tx_n",  Pins("H1"))
    ),
    ("pcie_x2", 0,
        Subsignal("rst_n", Pins("E21"), IOStandard("LVCMOS33"), Misc("PULLUP=TRUE")),
        Subsignal("clk_p", Pins("K6")),
        Subsignal("clk_n", Pins("K5")),
        Subsignal("rx_p",  Pins("J4 L4")),
        Subsignal("rx_n",  Pins("J3 L3")),
        Subsignal("tx_p",  Pins("H2 K2")),
        Subsignal("tx_n",  Pins("H1 K1"))
    ),
    ("pcie_x4", 0,
        Subsignal("rst_n", Pins("E21"), IOStandard("LVCMOS33"), Misc("PULLUP=TRUE")),
        Subsignal("clk_p", Pins("K6")),
        Subsignal("clk_n", Pins("K5")),
        Subsignal("rx_p",  Pins("J4 L4 N4 R4")),
        Subsignal("rx_n",  Pins("J3 L3 N3 R3")),
        Subsignal("tx_p",  Pins("H2 K2 M2 P2")),
        Subsignal("tx_n",  Pins("H1 K1 M1 P1"))
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("HPC", {

        # FMC GTP Section
        "DP0_M2C_P" : "G4",
        "DP0_M2C_N" : "G3",
        "DP1_M2C_P" : "E4",
        "DP1_M2C_N" : "E3",
        "DP2_M2C_P" : "C4",
        "DP2_M2C_N" : "C3",
        "DP3_M2C_P" : "B6",
        "DP3_M2C_N" : "B5",

        "GBTCLK0_M2C_P" : "F6",
        "GBTCLK0_M2C_N" : "F5",
        "GBTCLK1_M2C_P" : "D6",
        "GBTCLK1_M2C_N" : "D5",

        "DP0_C2M_P" : "F2",
        "DP0_C2M_N" : "F1",
        "DP1_C2M_P" : "D2",
        "DP1_C2M_N" : "D1",
        "DP2_C2M_P" : "B2",
        "DP2_C2M_N" : "B1",
        "DP3_C2M_P" : "A4",
        "DP3_C2M_N" : "A3",

        # FMC LA Bank GPIOs
        "LA00_P" : "AA23",
        "LA00_N" : "AB24",
        "LA01_P" : "Y23",
        "LA01_N" : "AA24",
        "LA02_P" : "AD26",
        "LA02_N" : "AE26",
        "LA03_P" : "AA25",
        "LA03_N" : "AB25",
        "LA04_P" : "AD25",
        "LA04_N" : "AE25",
        "LA05_P" : "W25",
        "LA05_N" : "W26",
        "LA06_P" : "Y25",
        "LA06_N" : "Y26",
        "LA07_P" : "V23",
        "LA07_N" : "V24",
        "LA08_P" : "U26",
        "LA08_N" : "V26",
        "LA09_P" : "W20",
        "LA09_N" : "Y21",
        "LA10_P" : "V21",
        "LA10_N" : "W21",
        "LA11_P" : "L19",
        "LA11_N" : "L20",
        "LA12_P" : "M17",
        "LA12_N" : "L18",
        "LA13_P" : "K20",
        "LA13_N" : "J20",
        "LA14_P" : "J18",
        "LA14_N" : "J19",
        "LA15_P" : "U17",
        "LA15_N" : "T17",
        "LA16_P" : "T18",
        "LA16_N" : "T19",
        "LA17_P" : "E18",
        "LA17_N" : "D18",
        "LA18_P" : "F17",
        "LA18_N" : "E17",
        "LA19_P" : "H16",
        "LA19_N" : "G16",
        "LA20_P" : "K16",
        "LA20_N" : "K17",
        "LA21_P" : "D19",
        "LA21_N" : "D20",
        "LA22_P" : "C19",
        "LA22_N" : "B19",
        "LA23_P" : "C17",
        "LA23_N" : "C18",
        "LA24_P" : "D15",
        "LA24_N" : "D16",
        "LA25_P" : "F19",
        "LA25_N" : "E20",
        "LA26_P" : "J15",
        "LA26_N" : "J16",
        "LA27_P" : "G15",
        "LA27_N" : "F15",
        "LA28_P" : "G17",
        "LA28_N" : "F18",
        "LA29_P" : "E15",
        "LA29_N" : "E16",
        "LA30_P" : "H17",
        "LA30_N" : "H18",
        "LA31_P" : "G19",
        "LA31_N" : "F20",
        "LA32_P" : "H19",
        "LA32_N" : "G20",
        "LA33_P" : "L17",
        "LA33_N" : "K18",

        # FMC HA Bank GPIOs
        "HA00_P" : "P23",
        "HA00_N" : "N23",
        "HA01_P" : "N21",
        "HA01_N" : "N22",
        "HA02_P" : "AB22",
        "HA02_N" : "AC22",
        "HA03_P" : "AD23",
        "HA03_N" : "AD24",
        "HA04_P" : "N19",
        "HA04_N" : "M20",
        "HA05_P" : "R18",
        "HA05_N" : "P18",
        "HA06_P" : "P16",
        "HA06_N" : "N17",
        "HA07_P" : "R16",
        "HA07_N" : "R17",
        "HA08_P" : "U19",
        "HA08_N" : "U20",
        "HA09_P" : "N18",
        "HA09_N" : "M19",
        "HA10_P" : "T20",
        "HA10_N" : "R20",
        "HA11_P" : "P19",
        "HA11_N" : "P20",
        "HA12_P" : "T24",
        "HA12_N" : "T25",
        "HA13_P" : "U24",
        "HA13_N" : "U25",
        "HA14_P" : "R26",
        "HA14_N" : "P26",
        "HA15_P" : "P24",
        "HA15_N" : "N24",
        "HA16_P" : "R25",
        "HA16_N" : "P25",
        "HA17_P" : "M21",
        "HA17_N" : "M22",
        "HA18_P" : "N26",
        "HA18_N" : "M26",
        "HA19_P" : "K25",
        "HA19_N" : "K26",
        "HA20_P" : "M25",
        "HA20_N" : "L25",
        "HA21_P" : "M24",
        "HA21_N" : "L24",
        "HA22_P" : "T22",
        "HA22_N" : "T23",
        "HA23_P" : "U22",
        "HA23_N" : "V22",

        # FMC HB Bank GPIOs
        "HB00_P" : "E10",
        "HB00_N" : "D10",
        "HB01_P" : "F14",
        "HB01_N" : "F13",
        "HB02_P" : "H14",
        "HB02_N" : "G14",
        "HB03_P" : "J13",
        "HB03_N" : "H13",
        "HB04_P" : "B14",
        "HB04_N" : "A14",
        "HB05_P" : "B15",
        "HB05_N" : "A15",
        "HB06_P" : "C12",
        "HB06_N" : "C11",
        "HB07_P" : "G10",
        "HB07_N" : "G9",
        "HB08_P" : "E13",
        "HB08_N" : "E12",
        "HB09_P" : "D14",
        "HB09_N" : "D13",
        "HB10_P" : "C9",
        "HB10_N" : "B9",
        "HB11_P" : "A13",
        "HB11_N" : "A12",
        "HB12_P" : "B10",
        "HB12_N" : "A10",
        "HB13_P" : "B12",
        "HB13_N" : "B11",
        "HB14_P" : "F9",
        "HB14_N" : "F8",
        "HB15_P" : "E11",
        "HB15_N" : "D11",
        "HB16_P" : "D9",
        "HB16_N" : "D8",
        "HB17_P" : "G11",
        "HB17_N" : "F10",
        "HB18_P" : "G12",
        "HB18_N" : "F12",
        "HB19_P" : "A9",
        "HB19_N" : "A8",
        "HB20_P" : "J11",
        "HB20_N" : "J10",
        "HB21_P" : "H9",
        "HB21_N" : "H8",

        # FMC Clock and Misc signals
        "CLK0_M2C_P"   : "Y22",
        "CLK0_M2C_N"   : "AA22",
        "CLK1_M2C_P"   : "AC23",
        "CLK1_M2C_N"   : "AC24",
        "CLK2_BIDIR_P" : "R22",
        "CLK2_BIDIR_N" : "R23",
        "CLK3_BIDIR_P" : "R21",
        "CLK3_BIDIR_N" : "P21",
        "CLK_DIR"      : "D23",

        "PG_C2M"       : "D26",
        "PG_M2C"       : "E26",
        "FMC_SCL"      : "C21",
        "FMC_SDA"      : "B21",
        "FMC_PRSNT"    : "B26",
        }
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self, toolchain="vivado"):
        Xilinx7SeriesPlatform.__init__(self, "xc7k160t-fbg676-1", _io, _connectors, toolchain=toolchain)

        self.add_platform_command("""
set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
""")
        self.toolchain.bitstream_commands = [
            "set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]",
            "set_property BITSTREAM.CONFIG.CONFIGRATE 16 [current_design]",
            "set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]"
        ]
        self.toolchain.additional_commands = \
            ["write_cfgmem -force -format bin -interface spix4 -size 16 "
             "-loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"]

    def create_programmer(self):
        return OpenOCD("openocd_xc7_ft232.cfg", "bscan_spi_xc7k160t.bit")

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100", loose=True), 1e9/100e6)
        self.add_period_constraint(self.lookup_request("clk150", loose=True), 1e9/150e6)
