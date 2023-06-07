#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2023 Gabriel Somlo <gsomlo@gmail.com>
# Copyright (c) 2022 Andrew Gillham <gillham@roadsign.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform
from litex.build.openocd import OpenOCD

# This board is available here:
# https://www.aliexpress.com/item/1005001275162791.html

# IOs ----------------------------------------------------------------------------------------------

def _get_io(voltage="2.5V"):
    assert voltage in ["2.5V", "3.3V"]
    VCCIO = {"2.5V": "25", "3.3V": "33"}[voltage]
    _io = [
        # Clk / Rst
        ("cpu_reset_n", 0, Pins("AC16"), IOStandard("LVCMOS15")),

        ("clk50",      0, Pins("F17"), IOStandard("LVCMOS" + VCCIO)),
        ("clk200", 0,
            Subsignal("p", Pins("AB11"), IOStandard("DIFF_SSTL15")),
            Subsignal("n", Pins("AC11"), IOStandard("DIFF_SSTL15"))
        ),
        ("clk156", 0, # TODO verify / test (in docs)
            Subsignal("p", Pins("D6"), IOStandard("LVDS")),
            Subsignal("n", Pins("D5"), IOStandard("LVDS")),
        ),
        ("clk150", 0, # TODO verify / test (in docs)
            Subsignal("p", Pins("F6"), IOStandard("LVDS")),
            Subsignal("n", Pins("F5"), IOStandard("LVDS")),
        ),

        # Leds
        ("user_led_n", 0, Pins("AA2"),  IOStandard("LVCMOS15")),
        ("user_led_n", 1, Pins("AD5"),  IOStandard("LVCMOS15")),
        ("user_led_n", 2, Pins("W10"),  IOStandard("LVCMOS15")),
        ("user_led_n", 3, Pins("Y10"),  IOStandard("LVCMOS15")),
        ("user_led_n", 4, Pins("AE10"), IOStandard("LVCMOS15")),
        ("user_led_n", 5, Pins("W11"),  IOStandard("LVCMOS15")),
        ("user_led_n", 6, Pins("V11"),  IOStandard("LVCMOS15")),
        ("user_led_n", 7, Pins("Y12"),  IOStandard("LVCMOS15")),

        # Buttons
        ("user_btn_n", 0, Pins("AC16"), IOStandard("LVCMOS15")),
        ("user_btn_n", 0, Pins("C24"),  IOStandard("LVCMOS33")), # J4 jumper 2.5V or 3.3V

        # I2C / AT24C04
        ("i2c", 0,
            Subsignal("scl", Pins("U26")),
            Subsignal("sda", Pins("V26")),
            IOStandard("LVCMOS" + VCCIO)
        ),

        # Serial
        ("serial", 0,
            Subsignal("tx",  Pins("L23")),  # CP2102_TX
            Subsignal("rx",  Pins("K21")),  # CP2102_RX
            IOStandard("LVCMOS" + VCCIO)
        ),

        # DDR3 SDRAM
        ("ddram", 0,
            Subsignal("a",     Pins(
                "AB7  AD11 AA8 AF10  AC7 AE11  AC8 AD8",
                "AC13 AF12 AF9 AD10 AE13  AF7 AB12 AC12"),
                IOStandard("SSTL15")),
            Subsignal("ba",    Pins("AE8 AA7 AF13"), IOStandard("SSTL15")),
            Subsignal("ras_n", Pins("Y7"),  IOStandard("SSTL15")),
            Subsignal("cas_n", Pins("AE7"), IOStandard("SSTL15")),
            Subsignal("we_n",  Pins("AF8"),  IOStandard("SSTL15")),
            Subsignal("cs_n",  Pins("AA13"), IOStandard("SSTL15")),
            Subsignal("dm",      Pins(
                "AD16 AB16 AB19 V17 U1 AA3 AD6 AE1"),
                IOStandard("SSTL15")),
            Subsignal("dq",      Pins(
                "AF17 AE17 AF15 AF14 AE15 AD15 AF20 AF19",
                "AA15 AA14 AC14 AD14 AB14 AB15 AA18 AA17",
                "AC18 AD18 AC17 AB17 AA20 AA19 AD19 AC19",
                " W14  V14  V19  V18  V16  W15  W16  Y17",
                "  V4   U6   U5   U2   V3   W3   U7   V6",
                "  Y3   Y2   V2   V1   W1   Y1  AB2  AC2",
                " AA4  AB4  AC4  AC3  AC6  AB6   Y6   Y5",
                " AD4  AD1  AF2  AE2  AE6  AE5  AF3  AE3"),
                IOStandard("SSTL15_T_DCI")),
            Subsignal("dqs_p",   Pins("AE18 Y15 AD20 W18 W6 AB1 AA5 AF5"),
                IOStandard("DIFF_SSTL15_T_DCI")),
            Subsignal("dqs_n",   Pins("AF18 Y16 AE20 W19 W5 AC1 AB5 AF4"),
                IOStandard("DIFF_SSTL15_T_DCI")),
            Subsignal("clk_p",   Pins("AC9"),
                IOStandard("DIFF_SSTL15"), Misc("IO_BUFFER_TYPE=NONE")),
            Subsignal("clk_n",   Pins("AD9"),
                IOStandard("DIFF_SSTL15"), Misc("IO_BUFFER_TYPE=NONE")),
            Subsignal("cke",     Pins("AB10"), IOStandard("SSTL15")),
            Subsignal("odt",     Pins("AA12"), IOStandard("SSTL15")),
            Subsignal("reset_n", Pins("AB20"), IOStandard("LVCMOS15")),
            Misc("SLEW=FAST"),
            Misc("VCCAUX_IO=NORMAL")
        ),
        # 2 Rank Signals:
        # Subsignal("cs_n",  Pins("AD13"), IOStandard("SSTL15")),
        # Subsignal("clk_p", Pins("AA9"), IOStandard("DIFF_SSTL15")),
        # Subsignal("clk_n", Pins("AB9"), IOStandard("DIFF_SSTL15")),
        # Subsignal("cke",   Pins("AA10"), IOStandard("SSTL15")),
        # Subsignal("odt",   Pins("Y13"),  IOStandard("SSTL15")),

        ## TODO verify / test
        # # SPIFlash
        # ("spiflash", 0,
        #     Subsignal("cs_n", Pins("C23")),
        #     Subsignal("clk", Pins("C8")),
        #     Subsignal("dq",   Pins("B24 A25 B22 A22")),
        #     IOStandard("LVCMOS25")
        # ),

        # Sata
        ("sata", 0,
            Subsignal("rx_p", Pins("R4")),
            Subsignal("rx_n", Pins("R3")),
            Subsignal("tx_p", Pins("P2")),
            Subsignal("tx_n", Pins("P1")),
        ),
        ("sata", 1,
            Subsignal("rx_p", Pins("N4")),
            Subsignal("rx_n", Pins("N3")),
            Subsignal("tx_p", Pins("M2")),
            Subsignal("tx_n", Pins("M1")),
        ),

        # SDCard
        ("spisdcard", 0,
            Subsignal("clk",  Pins("V22")),
            Subsignal("cs_n", Pins("W23")),
            Subsignal("mosi", Pins("W24"), Misc("PULLUP True")),
            Subsignal("miso", Pins("U22"), Misc("PULLUP True")),
            Misc("SLEW=FAST"),
            IOStandard("LVCMOS" + VCCIO)
        ),
        ("sdcard", 0,
            Subsignal("clk", Pins("V22")),
            Subsignal("cmd", Pins("W24"), Misc("PULLUP True")),
            Subsignal("data", Pins("U22 V21 W21 W23"), Misc("PULLUP True")),
            Misc("SLEW=FAST"),
            IOStandard("LVCMOS" + VCCIO)
        ),

        # RGMII Ethernet
        ("eth_clocks", 0,
            Subsignal("tx",  Pins("D11"), IOStandard("LVCMOS25")),
            Subsignal("rx",  Pins("C12"), IOStandard("LVCMOS25"))
        ),
        ("eth_clocks", 1,
            Subsignal("tx",  Pins("B11"),  IOStandard("LVCMOS25")),
            Subsignal("rx",  Pins("E10"), IOStandard("LVCMOS25"))
        ),
        ("eth", 0,
            Subsignal("rst_n",   Pins("J8")),
            Subsignal("mdio",    Pins("H11")),
            Subsignal("mdc",     Pins("F9")),
            Subsignal("rx_ctl",  Pins("F8")),
            Subsignal("rx_data", Pins("D8 D9 C9 D10")),
            Subsignal("tx_ctl",  Pins("C14")),
            Subsignal("tx_data", Pins("E12 D13 C13 D14")),
            IOStandard("LVCMOS25")
        ),
        ("eth", 1,
            Subsignal("rst_n",   Pins("B14")),
            Subsignal("mdio",    Pins("B15")),
            Subsignal("mdc",     Pins("A15")),
            Subsignal("rx_ctl",  Pins("A8")),
            Subsignal("rx_data", Pins("B9 A9 B10 A10")),
            Subsignal("tx_ctl",  Pins("A14")),
            Subsignal("tx_data", Pins("B12 A12 A13 C11")),
            IOStandard("LVCMOS25")
        ),

        # HDMI out
        ("hdmi_out", 0,
            Subsignal("clk_p",   Pins("F14"), IOStandard("TMDS_33" if VCCIO == "33" else "LVDS_25")),
            Subsignal("clk_n",   Pins("F13"), IOStandard("TMDS_33" if VCCIO == "33" else "LVDS_25")),
            Subsignal("data0_p", Pins("G12"), IOStandard("TMDS_33" if VCCIO == "33" else "LVDS_25")),
            Subsignal("data0_n", Pins("F12"), IOStandard("TMDS_33" if VCCIO == "33" else "LVDS_25")),
            Subsignal("data1_p", Pins("G10"), IOStandard("TMDS_33" if VCCIO == "33" else "LVDS_25")),
            Subsignal("data1_n", Pins("G9"), IOStandard("TMDS_33" if VCCIO == "33" else "LVDS_25")),
            Subsignal("data2_p", Pins("H9"), IOStandard("TMDS_33" if VCCIO == "33" else "LVDS_25")),
            Subsignal("data2_n", Pins("H8"), IOStandard("TMDS_33" if VCCIO == "33" else "LVDS_25")),
        ),

        # HDMI in
        ("hdmi_in", 0,
            Subsignal("clk_p",   Pins("G11"), IOStandard("TMDS_33" if VCCIO == "33" else "LVDS_25")),
            Subsignal("clk_n",   Pins("F10"), IOStandard("TMDS_33" if VCCIO == "33" else "LVDS_25")),
            Subsignal("data0_p", Pins("J13"), IOStandard("TMDS_33" if VCCIO == "33" else "LVDS_25")),
            Subsignal("data0_n", Pins("H13"), IOStandard("TMDS_33" if VCCIO == "33" else "LVDS_25")),
            Subsignal("data1_p", Pins("J11"), IOStandard("TMDS_33" if VCCIO == "33" else "LVDS_25")),
            Subsignal("data1_n", Pins("J10"), IOStandard("TMDS_33" if VCCIO == "33" else "LVDS_25")),
            Subsignal("data2_p", Pins("H14"), IOStandard("TMDS_33" if VCCIO == "33" else "LVDS_25")),
            Subsignal("data2_n", Pins("G14"), IOStandard("TMDS_33" if VCCIO == "33" else "LVDS_25")),
            Subsignal("scl",     Pins("U21"), IOStandard("LVCMOS" + VCCIO)),
            Subsignal("sda",     Pins("Y20"), IOStandard("LVCMOS" + VCCIO)),
        ),

        # PCIe
        ("pcie_x1", 0,
            Subsignal("rst_n", Pins("E17"), IOStandard("LVCMOS" + VCCIO)),
            Subsignal("clk_p", Pins("H6")),
            Subsignal("clk_n", Pins("H5")),
            Subsignal("rx_p",  Pins("B6")),
            Subsignal("rx_n",  Pins("B5")),
            Subsignal("tx_p",  Pins("A4")),
            Subsignal("tx_n",  Pins("A3"))
        ),
        ("pcie_x2", 0,
            Subsignal("rst_n", Pins("E17"), IOStandard("LVCMOS" + VCCIO)),
            Subsignal("clk_p", Pins("H6")),
            Subsignal("clk_n", Pins("H5")),
            Subsignal("rx_p",  Pins("B6 C4")),
            Subsignal("rx_n",  Pins("B5 C3")),
            Subsignal("tx_p",  Pins("A4 B2")),
            Subsignal("tx_n",  Pins("A3 B1"))
        ),
        ("pcie_x4", 0,
            Subsignal("rst_n", Pins("E17"), IOStandard("LVCMOS" + VCCIO)),
            Subsignal("clk_p", Pins("H6")),
            Subsignal("clk_n", Pins("H5")),
            Subsignal("rx_p",  Pins("B6 C4 E4 G4")),
            Subsignal("rx_n",  Pins("B5 C3 E3 G3")),
            Subsignal("tx_p",  Pins("A4 B2 D2 F2")),
            Subsignal("tx_n",  Pins("A3 B1 D1 F1"))
        ),

        # TODO find / test
        # # SGMII Clk
        # ("sgmii_clock", 0,
        #     Subsignal("p", Pins("")),
        #     Subsignal("n", Pins(""))
        # ),

        # SFP
        ("sfp_a", 0,  # SFP A
            Subsignal("txp", Pins("H2")),
            Subsignal("txn", Pins("H1")),
            Subsignal("rxp", Pins("J4")),
            Subsignal("rxn", Pins("J3")),
            Subsignal("sda", Pins("B21")),
            Subsignal("scl", Pins("C21")),
        ),
        ("sfp_a_tx", 0,  # SFP A
            Subsignal("p", Pins("H2")),
            Subsignal("n", Pins("H1"))
        ),
        ("sfp_a_rx", 0,  # SFP A
            Subsignal("p", Pins("J4")),
            Subsignal("n", Pins("J3"))
        ),
        ("sfp_b", 0,  # SFP B
            Subsignal("txp", Pins("K2")),
            Subsignal("txn", Pins("K1")),
            Subsignal("rxp", Pins("L4")),
            Subsignal("rxn", Pins("L3")),
            Subsignal("sda", Pins("D21")),
            Subsignal("scl", Pins("C22")),
        ),
        ("sfp_b_tx", 0,  # SFP B
            Subsignal("p", Pins("K2")),
            Subsignal("n", Pins("K1"))
        ),
        ("sfp_b_rx", 0,  # SFP B
            Subsignal("p", Pins("L4")),
            Subsignal("n", Pins("L3"))
        ),

        # SI5338 (optional part per seller?)
        ("si5338_i2c", 0,
            Subsignal("sck", Pins("U26"), IOStandard("LVCMOS" + VCCIO)),
            Subsignal("sda", Pins("V26"), IOStandard("LVCMOS" + VCCIO))
        ),
        ("si5338_clkin", 0,  # CLK2A/B
            Subsignal("p", Pins("K6"), IOStandard("LVDS_25")),
            Subsignal("n", Pins("K5"), IOStandard("LVDS_25"))
        ),
    ]

    return _io

# Connectors ---------------------------------------------------------------------------------------

        #GLS FIXME
_connectors = [
    ("LPC", {
        # Row C
        "DP0_C2M_P"     : "", # not connected
        "DP0_C2M_N"     : "", # not connected
        "DP0_M2C_P"     : "", # not connected
        "DP0_M2C_N"     : "", # not connected
        "LA06_P"        : "AE23",
        "LA06_N"        : "AF23",
        "LA10_P"        : "AD26",
        "LA10_N"        : "AE26",
        "LA14_P"        : "Y25",
        "LA14_N"        : "Y26",
        "LA18_CC_P"     : "P23",
        "LA18_CC_N"     : "N23",
        "LA27_P"        : "R26",
        "LA27_N"        : "P26",

        # Row D
        "GBTCLK0_M2C_P" : "", # not connected
        "GBTCLK0_M2C_N" : "", # not connected
        "LA01_CC_P"     : "AA23",
        "LA01_CC_N"     : "AB24",
        "LA05_P"        : "AF24",
        "LA05_N"        : "AF25",
        "LA09_P"        : "AB22",
        "LA09_N"        : "AC22",
        "LA13_P"        : "AB26",
        "LA13_N"        : "AC26",
        "LA17_CC_P"     : "R22",
        "LA17_CC_N"     : "R23",
        "LA23_P"        : "T24",
        "LA23_N"        : "T25",
        "LA26_P"        : "U17",
        "LA26_N"        : "T17",

        # Row G
        "CLK1_M2C_P"    : "Y23",
        "CLK1_M2C_N"    : "AA24",
        "LA00_CC_P"     : "Y22",
        "LA00_CC_N"     : "AA22",
        "LA03_P"        : "U24",
        "LA03_N"        : "U25",
        "LA08_P"        : "AE22",
        "LA08_N"        : "AF22",
        "LA12_P"        : "W25",
        "LA12_N"        : "W26",
        "LA16_P"        : "AA25",
        "LA16_N"        : "AB25",
        "LA20_P"        : "P24",
        "LA20_N"        : "N24",
        "LA22_P"        : "M21",
        "LA22_N"        : "M22",
        "LA25_P"        : "M25",
        "LA25_N"        : "L25",
        "LA29_P"        : "R16",
        "LA29_N"        : "R17",
        "LA31_P"        : "P16",
        "LA31_N"        : "N17",
        "LA33_P"        : "T22",
        "LA33_N"        : "T23",

        # Row H
        "CLK0_M2C_P"    : "AC23",
        "CLK0_M2C_N"    : "AC24",
        "LA02_P"        : "V23",
        "LA02_N"        : "V24",
        "LA04_P"        : "AD21",
        "LA04_N"        : "AE21",
        "LA07_P"        : "AB21",
        "LA07_N"        : "AC21",
        "LA11_P"        : "AD23",
        "LA11_N"        : "AD24",
        "LA15_P"        : "AD25",
        "LA15_N"        : "AE25",
        "LA19_P"        : "R25",
        "LA19_N"        : "P25",
        "LA21_P"        : "U19",
        "LA21_N"        : "U20",
        "LA24_P"        : "T18",
        "LA24_N"        : "T19",
        "LA28_P"        : "R18",
        "LA28_N"        : "P18",
        "LA30_P"        : "M19",
        "LA30_N"        : "V22",
        "LA32_P"        : "T20",
        "LA32_N"        : "R20",
        }
    ),
    ("BTB-A", {
        10: "P19", # P
        11: "P20", # N

        13: "N21", # P
        14: "N22", # N
        15: "K23", # P
        16: "J23", # N

        18: "M24", # P
        19: "L24", # N
        20: "J24", # P
        21: "J25", # N

        23: "H21", # P
        24: "G21", # N
        25: "E21", # P
        26: "E22", # N

        28: "G22", # P
        29: "F23", # N
        30: "E25", # P
        31: "D25", # N

        33: "D23", # P
        34: "D24", # N
        35: "F22", # P
        36: "E23", # N
    }),
    ("BTB-B", {
         5: "W20", # P
         6: "Y21", # N

         8: "N19", # P
         9: "M20", # N
        10: "N26", # P
        11: "M26", # N

        13: "L22", # P
        14: "K22", # N
        15: "K25", # P
        16: "K26", # N

        18: "J21", # P
        19: "H22", # N
        20: "J26", # P
        21: "H26", # N

        23: "G25", # P
        24: "G26", # N
        25: "F25", # P
        26: "E26", # N

        28: "D26", # P
        29: "C26", # N
        30: "A23", # P
        31: "A24", # N

        33: "B20", # P
        34: "A20", # N
        35: "B26",

        38: "K15",
        39: "M16",
    }),
    ("AB", {
         #    N          P
         1: "J20",  2: "K20",
         3: "G20",  4: "H19",
         5: "L20",  6: "L19",
         9: "E20", 10: "F19",
        11: "H18", 12: "H17",
        13: "F18", 14: "G17",
        15: "G16", 16: "H16",
        19: "F24", 20: "G24",
        21: "F20", 22: "G19",
        23: "L18", 24: "M17",
        25: "H24", 26: "H23",
    }),
    ("C", {
         2: "D19", # P
         3: "D20", # N
         7: "D18", # N
         8: "E18", # P
        10: "E16", # N
        11: "E15", # P
    }),
    ("DE", {
         1: "J18",  2: "J19", #  P   N
         3: "L17",  4: "K18", #  P   N
         5: "K16",  6: "K17", #  P   N
         9: "C19", 10: "B19", #  P   N
        11: "C18", 12: "C17", #  N   P
        13: "C16", 14: "B16", #  P   N
        15: "D15", 16: "D16", #  P   N
        19: "G15", 20: "F15", #  P   N
        21: "J15", 22: "J16", #  P   N
        23: "A18", 24: "A19", #  P   N
        25: "B17", 26: "A17", #  P   N
    }),
]
# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk200"
    default_clk_period = 1e9/200e6

    def __init__(self, vccio="3.3V"):
        assert vccio in ["2.5V", "3.3V"]
        Xilinx7SeriesPlatform.__init__(self, "xc7k325t-ffg676-2", _get_io(vccio), _connectors, toolchain="vivado")
        self.add_platform_command("""
set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE %s [current_design]
set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]
""" % vccio.replace("V", ""))
        self.toolchain.bitstream_commands = ["set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]"]
        self.toolchain.additional_commands = ["write_cfgmem -force -format bin -interface spix4 -size 16 -loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"]

    def create_programmer(self):
        return OpenOCD("openocd_xc7_ft4232.cfg", "bscan_spi_xc7a325t.bit")

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100",        loose=True), 1e9/100e6)
        self.add_period_constraint(self.lookup_request("clk200",        loose=True), 1e9/200e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:rx", 0, loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:tx", 0, loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:rx", 1, loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:tx", 1, loose=True), 1e9/125e6)
        self.add_platform_command("set_property DCI_CASCADE {{32 34}} [get_iobanks 33]")
