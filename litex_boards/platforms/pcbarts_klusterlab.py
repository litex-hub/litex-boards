#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2023 Hans Baier <hansfbaier@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk66", 0, Pins("B26"), IOStandard("LVCMOS18")),

    ("clk200", 0,
        Subsignal("p", Pins("AC9"), IOStandard("DIFF_SSTL15")),
        Subsignal("n", Pins("AD9"), IOStandard("DIFF_SSTL15"))
    ),
    ("clk_si", 0,
        Subsignal("p", Pins("K6"), IOStandard("DIFF_HSTL_I_10")),
        Subsignal("n", Pins("K5"), IOStandard("DIFF_HSTL_I_10"))
    ),
    ("clk_sata_150", 0,
        Subsignal("p", Pins("F6"), IOStandard("DIFF_HSTL_I_10")),
        Subsignal("n", Pins("F5"), IOStandard("DIFF_HSTL_I_10"))
    ),
    ("clk_net_156", 0,
        Subsignal("p", Pins("H6"), IOStandard("DIFF_HSTL_I_10")),
        Subsignal("n", Pins("H5"), IOStandard("DIFF_HSTL_I_10"))
    ),

    ("cpu_reset", 0, Pins("A20"), IOStandard("LVCMOS18")),
    ("pi_reset_n",  0, Pins("A18"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led", 0, Pins("F23"),  IOStandard("LVCMOS18"), Misc("SLEW=SLOW")),
    ("user_led", 1, Pins("J26"),  IOStandard("LVCMOS18"), Misc("SLEW=SLOW")),
    ("user_led", 2, Pins("G26"),  IOStandard("LVCMOS18"), Misc("SLEW=SLOW")),
    ("user_led", 3, Pins("H26"),  IOStandard("LVCMOS18"), Misc("SLEW=SLOW")),
    ("user_led", 4, Pins("G25"),  IOStandard("LVCMOS18"), Misc("SLEW=SLOW")),
    ("user_led", 5, Pins("F24"),  IOStandard("LVCMOS18"), Misc("SLEW=SLOW")),
    ("user_led", 6, Pins("F25"),  IOStandard("LVCMOS18"), Misc("SLEW=SLOW")),
    ("user_led", 7, Pins("G24"),  IOStandard("LVCMOS18"), Misc("SLEW=SLOW")),

    # Buttons
    ("user_btn", 0, Pins("J24"), IOStandard("LVCMOS18")),
    ("user_btn", 1, Pins("H22"), IOStandard("LVCMOS18")),
    ("user_btn", 2, Pins("H23"), IOStandard("LVCMOS18")),
    ("user_btn", 3, Pins("H24"), IOStandard("LVCMOS18")),
    ("user_btn", 4, Pins("G22"), IOStandard("LVCMOS18")),

    # Switches
    ("user_sw", 0, Pins("E25"), IOStandard("LVCMOS18")),
    ("user_sw", 1, Pins("E26"), IOStandard("LVCMOS18")),
    ("user_sw", 2, Pins("D25"), IOStandard("LVCMOS18")),
    ("user_sw", 3, Pins("F22"), IOStandard("LVCMOS18")),
    ("user_sw", 4, Pins("D24"), IOStandard("LVCMOS18")),
    ("user_sw", 5, Pins("D23"), IOStandard("LVCMOS18")),
    ("user_sw", 6, Pins("E23"), IOStandard("LVCMOS18")),
    ("user_sw", 7, Pins("E22"), IOStandard("LVCMOS18")),
    ("user_sw", 8, Pins("J25"), IOStandard("LVCMOS18")),

    # Testpoints
    ("tp", 0, Pins("M17"), IOStandard("LVCMOS33")),
    ("tp", 1, Pins("L18"), IOStandard("LVCMOS33")),
    ("tp", 2, Pins("L17"), IOStandard("LVCMOS33")),
    ("tp", 3, Pins("K18"), IOStandard("LVCMOS33")),

    # Fan control
    ("fan", 0,
        Subsignal("tach", Pins("B19")),
        Subsignal("pwm",  Pins("C17")),
        Subsignal("sys",  Pins("C19")),
        IOStandard("LVCMOS33")),

    # USB Serial
    ("serial", 0,
        Subsignal("tx",  Pins("A17")),
        Subsignal("rx",  Pins("K15")),
        Subsignal("rts", Pins("B17")),
        Subsignal("cts", Pins("F18")),
        IOStandard("LVCMOS33")
     ),

    # I2C
    ("i2c_mxrst_n", Pins("W21"), IOStandard("LVCMOS18")),

    # IO
    ("i2c", 0,
        Subsignal("scl", Pins("V21")),
        Subsignal("sda", Pins("AE22")),
        IOStandard("LVCMOS18"),
    ),
    # temperature
    ("i2c", 1,
        Subsignal("scl", Pins("AE26")),
        Subsignal("sda", Pins("AD26")),
        IOStandard("LVCMOS18"),
    ),

    ("si5324", 0,
        Subsignal("int", Pins("V22")),
        Subsignal("rst", Pins("V24")),
        IOStandard("LVCMOS18"),
    ),

    ("smi", 0,
        Subsignal("sa", Pins("AB26 V26 U24 U26 AB25 V23"), IOStandard("LVCMOS33")),
        Subsignal("sd", Pins("W24 Y26 Y25 AA25 U22 AC26 U25 AB24"
                             "Y22 W25 Y23 AC23 Y21 W20  W26 AA23" 
                             "AA24 AA22"), IOStandard("LVCMOS33")),
        Subsignal("soe_n", Pins("AC24"),   IOStandard("LVCMOS33")),
        Subsignal("swe_n", Pins("W23"),    IOStandard("LVCMOS33")),
    ),

    # SD Card
    ("sdcard", 0,
        Subsignal("data", Pins("AD24 AC21 AD23 AB21"), Misc("PULLUP True")),
        Subsignal("cmd",  Pins("AB22"), Misc("PULLUP True")),
        Subsignal("clk",  Pins("AD21")),
        Subsignal("cd",   Pins("AC22")),
        Misc("SLEW=FAST"),
        IOStandard("LVCMOS18"),
    ),

    # PCIe
    ("pcie_x1", 0,
        Subsignal("rst_n", Pins("B16"), IOStandard("LVCMOS33"), Misc("PULLUP=TRUE")),
        Subsignal("clk_p", Pins("D6")),
        Subsignal("clk_n", Pins("D5")),
        Subsignal("rx_p",  Pins("B6")),
        Subsignal("rx_n",  Pins("B5")),
        Subsignal("tx_p",  Pins("A4")),
        Subsignal("tx_n",  Pins("A3"))
    ),

    ("sata", 0,
        Subsignal("rx_p", Pins("C4")),
        Subsignal("rx_n", Pins("C3")),
        Subsignal("tx_p", Pins("B2")),
        Subsignal("tx_n", Pins("B1")),
    ),

    # DDR3 SDRAM
    ("ddram", 0,
        Subsignal("a", Pins(
            "AF7  AD8  AB10 AC8 W11  AA12 AC12 AD13",
            "AB12 AD11 AE7  Y11 AA13 AB7  Y13  Y12"),
            IOStandard("SSTL15")),
        Subsignal("ba",    Pins("AC7 V8 AC13"), IOStandard("SSTL15")),
        Subsignal("ras_n", Pins("AA10"),        IOStandard("SSTL15")),
        Subsignal("cas_n", Pins("AA7"),         IOStandard("SSTL15")),
        Subsignal("we_n",  Pins("Y7"),          IOStandard("SSTL15")),
        Subsignal("cs_n",  Pins("Y8 V7"),       IOStandard("SSTL15")),
        Subsignal("dm", Pins(
            "AC19 V17 AF17 AA14 AC4 AF2 U7 Y1"),
            IOStandard("SSTL15")),
        Subsignal("dq", Pins(
            "AB17 AC18 AC17 AD19 AA19 AA20 AD18 AC16",
            "V16  V18  AB20 AB19 W15  V19  W16  Y17",
            "AF19 AE17 AE15 AF15 AF20 AD16 AD15 AF14",
            "AA15 AB16 AD14 AB14 AA18 AA17 AB15 AC14",
            "AD6  AC6  AC3  AB4  AB6  Y6   Y5   AA4",
            "AF3  AE3  AE2  AE1  AE6  AE5  AD4  AD1",
            "W3   V4   U2   U5   V6   V3   U1   U6",
            "AB2  AA3  W1   V2   AC2  Y3   Y2   V1 "),
            IOStandard("SSTL15_T_DCI")),
        Subsignal("dqs_p", Pins("AD20 W18 AE18 Y15 AA5 AF5 W6 AB1"),
            IOStandard("DIFF_SSTL15_T_DCI")),
        Subsignal("dqs_n", Pins("AE20 W19 AF18 Y16 AB5 AF4 W5 AC1"),
            IOStandard("DIFF_SSTL15_T_DCI")),
        Subsignal("clk_p", Pins("AB11 AA9"), IOStandard("DIFF_SSTL15")),
        Subsignal("clk_n", Pins("AC11 AB9"), IOStandard("DIFF_SSTL15")),
        Subsignal("cke",   Pins("Y10 W9"),   IOStandard("SSTL15")),
        Subsignal("odt",   Pins("AA8 V9"),   IOStandard("SSTL15")),
        Subsignal("reset_n", Pins("V11"),    IOStandard("SSTL15"), Misc("SLEW=SLOW")),
        Misc("SLEW=FAST"),
        Misc("VCCAUX_IO=HIGH"),
    ),

    # HDMI In
    ("hdmi_in", 0,
        Subsignal("clk_p",   Pins("M24"),   IOStandard("TMDS_33")),
        Subsignal("clk_n",   Pins("L24"),   IOStandard("TMDS_33")),
        Subsignal("data0_p", Pins("P24"),   IOStandard("TMDS_33")),
        Subsignal("data0_n", Pins("N24"),   IOStandard("TMDS_33")),
        Subsignal("data1_p", Pins("R26"),   IOStandard("TMDS_33")),
        Subsignal("data1_n", Pins("P26"),   IOStandard("TMDS_33")),
        Subsignal("data2_p", Pins("R25"),   IOStandard("TMDS_33")),
        Subsignal("data2_n", Pins("P25"),   IOStandard("TMDS_33")),
        Subsignal("scl",     Pins("P23"),   IOStandard("LVCMOS33")),
        Subsignal("sda",     Pins("M21"),   IOStandard("LVCMOS33")),
        Subsignal("hpd_en",  Pins("M22"),   IOStandard("LVCMOS25")),
        Subsignal("cec",     Pins("N23"),   IOStandard("LVCMOS33")),
        # Subsignal("txen",    Pins(""),   IOStandard("LVCMOS33")),
    ),

    # HDMI Out
    ("hdmi_out", 0,
        Subsignal("clk_p",   Pins("N19"),   IOStandard("TMDS_33")),
        Subsignal("clk_n",   Pins("M20"),   IOStandard("TMDS_33")),
        Subsignal("data0_p", Pins("P19"),   IOStandard("TMDS_33")),
        Subsignal("data0_n", Pins("P20"),   IOStandard("TMDS_33")),
        Subsignal("data1_p", Pins("K25"),  IOStandard("TMDS_33")),
        Subsignal("data1_n", Pins("K26"),  IOStandard("TMDS_33")),
        Subsignal("data2_p", Pins("M25"),  IOStandard("TMDS_33")),
        Subsignal("data2_n", Pins("L25"),  IOStandard("TMDS_33")),
        # Subsignal("scl",     Pins(""),   IOStandard("LVCMOS33")),
        # Subsignal("sda",     Pins(""),   IOStandard("LVCMOS33")),
        Subsignal("cec",     Pins("N26"),  IOStandard("LVCMOS33")),
        Subsignal("hdp",     Pins("M26"),  IOStandard("LVCMOS33")),
    ),

    # SFP0
    ("sfp", 0,
        Subsignal("txp", Pins("P2")),
        Subsignal("txn", Pins("P1")),
        Subsignal("rxp", Pins("R4")),
        Subsignal("rxn", Pins("R3"))
    ),
    ("sfp_tx_disable_n", 0, Pins("R18"),  IOStandard("LVCMOS33")),
    ("sfp_rx_los",       0, Pins("T19"), IOStandard("LVCMOS33")),
    ("sfp_link",         0, Pins("T24"), IOStandard("LVCMOS33")),
    ("sfp_act",          0, Pins("T25"), IOStandard("LVCMOS33")),

    # SFP1
    ("sfp", 1,
        Subsignal("txp", Pins("M2")),
        Subsignal("txn", Pins("M1")),
        Subsignal("rxp", Pins("N4")),
        Subsignal("rxn", Pins("N3")),
    ),
    ("sfp_tx_disable_n", 1, Pins("N18"), IOStandard("LVCMOS33")),
    ("sfp_rx_los",       1, Pins("M19"), IOStandard("LVCMOS33")),
    ("sfp_link",         1, Pins("T22"), IOStandard("LVCMOS33")),
    ("sfp_act",          1, Pins("R23"), IOStandard("LVCMOS33")),

    # SFP2
    ("sfp", 2,
        Subsignal("txp", Pins("K2")),
        Subsignal("txn", Pins("K1")),
        Subsignal("rxp", Pins("L4")),
        Subsignal("rxn", Pins("L3")),
    ),
    ("sfp_tx_disable_n", 2, Pins("N17"), IOStandard("LVCMOS33")),
    ("sfp_rx_los",       2, Pins("R17"), IOStandard("LVCMOS33")),
    ("sfp_link",         2, Pins("N22"), IOStandard("LVCMOS33")),
    ("sfp_act",          2, Pins("N21"), IOStandard("LVCMOS33")),

    # SFP3
    ("sfp", 3,
        Subsignal("txp", Pins("H2")),
        Subsignal("txn", Pins("H1")),
        Subsignal("rxp", Pins("J4")),
        Subsignal("rxn", Pins("J3")),
    ),
    ("sfp_tx_disable_n", 3, Pins("P16"), IOStandard("LVCMOS33")),
    ("sfp_rx_los",       3, Pins("R16"), IOStandard("LVCMOS33")),
    ("sfp_link",         3, Pins("R20"), IOStandard("LVCMOS33")),
    ("sfp_act",          3, Pins("R22"), IOStandard("LVCMOS33")),
]

_connectors = [
    ("cruvi_a", {
        "0_p"       : "F14",
        "0_n"       : "F13",
        "1_p"       : "A13",
        "1_n"       : "A12",
        "2_p"       : "D9",
        "2_n"       : "D8",
        "3_p"       : "C9",
        "3_n"       : "B9",
        "4_p"       : "B10",
        "4_n"       : "A10",
        "5_p"       : "B12",
        "5_n"       : "B11",
        "6_p"       : "C12",
        "6_n"       : "C11",
        "7_p"       : "B14",
        "7_n"       : "A14",
        "8_p"       : "B15",
        "8_n"       : "A15",
        "9_p"       : "C14",
        "9_n"       : "C13",
        "10_p"      : "H14",
        "10_n"      : "G14",
        "11_p"      : "D14",
        "11_n"      : "D13",
        "di"        : "G19",
        "do"        : "D20",
        "hsi"       : "F17",
        "hso"       : "H17",
        "hsio"      : "H18",
        "mode"      : "F20",
        "refclk"    : "E17",
        "reset"     : "H16",
        "sck"       : "G20",
        "sel"       : "E20",
        "smb_alert" : "H19",
        "smb_scl"   : "G17",
        "smb_sda"   : "F19",
    }),

    ("cruvi_b", {
        "0_p"       : "J10",
        "0_n"       : "J11",
        "1_p"       : "H8",
        "1_n"       : "H9",
        "2_p"       : "G9",
        "2_n"       : "G10",
        "3_p"       : "F8",
        "3_n"       : "F9",
        "4_p"       : "F10",
        "4_n"       : "G11",
        "5_p"       : "D10",
        "5_n"       : "E10",
        "6_p"       : "A8",
        "6_n"       : "A9",
        "7_p"       : "D11",
        "7_n"       : "E11",
        "8_p"       : "F12",
        "8_n"       : "G12",
        "9_p"       : "E12",
        "9_n"       : "E13",
        "10_p"      : "H11",
        "10_n"      : "H12",
        "11_p"      : "H13",
        "11_n"      : "J13",
        "di"        : "J15",
        "do"        : "C18",
        "hsi"       : "G16",
        "hso"       : "D16",
        "hsio"      : "F15",
        "mode"      : "E18",
        "refclk"    : "E16",
        "reset"     : "D15",
        "sck"       : "D19",
        "sel"       : "D18",
        "smb_alert" : "G15",
        "smb_scl"   : "E15",
        "smb_sda"   : "J16",
    }),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk200"
    default_clk_period = 1e9/200e6

    def __init__(self, toolchain="vivado"):
        Xilinx7SeriesPlatform.__init__(self, "xc7k160tffg676-2", _io, _connectors, toolchain=toolchain)
        self.add_platform_command("set_property CONFIG_VOLTAGE 1.8 [current_design]")
        self.add_platform_command("set_property CFGBVS GND [current_design]")
        # DDR3 is connected to banks 32, 33 and 34
        self.add_platform_command("set_property INTERNAL_VREF 0.750 [get_iobanks 32]")
        self.add_platform_command("set_property INTERNAL_VREF 0.750 [get_iobanks 33]")
        self.add_platform_command("set_property INTERNAL_VREF 0.750 [get_iobanks 34]")
        # The VRP/VRN resistors are connected to bank 34.
        # Banks 32 and 33 have LEDs in the places, so we have to use the reference from bank 34
        # Bank 33 has no _T_DCI signals connected
        self.add_platform_command("set_property DCI_CASCADE {{32}} [get_iobanks 34]")
        self.add_platform_command("set_property BITSTREAM.CONFIG.CONFIGRATE 22 [current_design]")
        self.add_platform_command("set_property BITSTREAM.CONFIG.OVERTEMPPOWERDOWN ENABLE [current_design]")

        # Important! Do not remove this constraint!
        # This property ensures that all unused pins are set to high impedance.
        # If the constraint is removed, all unused pins have to be set to HiZ in the top level file
        # This causes DDR3 to use 1.5V by default
        self.add_platform_command("set_property BITSTREAM.CONFIG.UNUSEDPIN PULLNONE [current_design]")

    def add_baseboard(self, bb):
        self.add_connector(bb.connectors)
        self.add_extension(bb.io)

    def create_programmer(self):
        return OpenOCD("openocd_xc7_ft232.cfg", "bscan_spi_xc7k160t.bit")

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk200", loose=True), 1e9/200e6)