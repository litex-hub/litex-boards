#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 Aria Wegrzyn <git@ariac.at>
# Copyright (c) 2026 Frank Zosso <f.zosso@resorix.ch>
# SPDX-License-Identifier: BSD-2-Clause

# Documentation for the board can be found here:
# https://github.com/tommythorn/rk-xcku5p-f-v1.2/

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxUSPPlatform
from litex.build.openfpgaloader import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk.
    ("clk200", 0,
        Subsignal("p", Pins("T24"), IOStandard("DIFF_SSTL12")),
        Subsignal("n", Pins("U24"), IOStandard("DIFF_SSTL12"))
    ),

    # LEDs.
    ("user_led", 0, Pins("H9"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("J9"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("G11"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("H11"), IOStandard("LVCMOS33")),

    # Buttons.
    ("user_btn", 0, Pins("K9"),  IOStandard("LVCMOS33")),
    ("user_btn", 1, Pins("K10"), IOStandard("LVCMOS33")),
    ("user_btn", 2, Pins("J10"), IOStandard("LVCMOS33")),
    ("user_btn", 3, Pins("J11"), IOStandard("LVCMOS33")),

    # UART.
    ("serial", 0,
        Subsignal("tx", Pins("AC14")),
        Subsignal("rx", Pins("AD13")),
        IOStandard("LVCMOS33")
    ),

    # DDR4
    ("ddram", 0,
        Subsignal("a",       Pins(
                "Y22  Y25  W23  V26  R26  U26 R21 W25",
                "R20  Y26  R25  V23  AA24 W26"),
            IOStandard("SSTL12_DCI")),
        Subsignal("ba",      Pins("P21 P26"), IOStandard("SSTL12_DCI")),
        Subsignal("bg",      Pins("R22"), IOStandard("SSTL12_DCI")),
        Subsignal("ras_n",   Pins("T25"), IOStandard("SSTL12_DCI")),  # A16
        Subsignal("cas_n",   Pins("AA25"), IOStandard("SSTL12_DCI")), # A15
        Subsignal("we_n",    Pins("P23"), IOStandard("SSTL12_DCI")),  # A14
        Subsignal("cs_n",    Pins("P25"), IOStandard("SSTL12_DCI")),
        Subsignal("act_n",   Pins("P24"), IOStandard("SSTL12_DCI")),
        Subsignal("alert_n", Pins("U25"), IOStandard("SSTL12_DCI")),
        Subsignal("par",     Pins("Y23"), IOStandard("SSTL12_DCI")),
        Subsignal("dq",      Pins(
                "AF24 AF25 AD24 AB26 AC24 AB25 AD25 AB24",
                "AC21 AD23 AD21 AC22 AB21 AE23 AE21 AC23",
                "AE16 AD19 AD16 AF17 AC19 AF19 AF18 AE17",
                "AA20 AA18 AA19 Y18  AB20 Y17  AB19 AA17"),
            IOStandard("POD12_DCI")),
        Subsignal("dqs_p",   Pins(
                "AC26 AA22 AC18 AB17"),
            IOStandard("DIFF_POD12")),
        Subsignal("dqs_n",   Pins(
                "AD26 AB22 AD18 AC17"),
            IOStandard("DIFF_POD12")),
        Subsignal("dm",     Pins(
                "AE25 AE22 AD20 Y20"), # also selects chip
            IOStandard("POD12_DCI")),
        Subsignal("clk_p",   Pins("V24"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("clk_n",   Pins("W24"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("cke",     Pins("P20"), IOStandard("SSTL12_DCI")),
        Subsignal("odt",     Pins("R23"), IOStandard("SSTL12_DCI")),
        Subsignal("reset_n", Pins("P19"), IOStandard("SSTL12")),
        Misc("SLEW=FAST"),
    ),

    # SDCard (3.3V only).
    ("spisdcard", 0,
        Subsignal("clk",  Pins("Y15")),
        Subsignal("mosi", Pins("AA15"), Misc("PULLUP True")),
        Subsignal("cs_n", Pins("AB15"), Misc("PULLUP True")),
        Subsignal("miso", Pins("AB14"), Misc("PULLUP True")),
        Misc("SLEW=FAST"),
        IOStandard("LVCMOS33"),
    ),
    ("sdcard", 0,
        Subsignal("data", Pins("AB14 AA14 AB16 AB15"), Misc("PULLUP True")),
        Subsignal("cmd",  Pins("AA15"), Misc("PULLUP True")),
        Subsignal("clk",  Pins("Y15")),
        Subsignal("cd",   Pins("Y16")),
        Misc("SLEW=FAST"),
        IOStandard("LVCMOS33"),
    ),

    # RGMII Ethernet (RTL8211F, TX/RX delays added by the PHY, PHY reset not connected).
    ("eth_clocks", 0,
        Subsignal("tx", Pins("M25")),
        Subsignal("rx", Pins("K22")),
        IOStandard("LVCMOS18")
    ),
    ("eth", 0,
        Subsignal("mdio",    Pins("M19")),
        Subsignal("mdc",     Pins("L19")),
        Subsignal("rx_ctl",  Pins("K23")),
        Subsignal("rx_data", Pins("L24 L25 K25 K26")),
        Subsignal("tx_ctl",  Pins("M26")),
        Subsignal("tx_data", Pins("L23 L22 L20 K20")),
        IOStandard("LVCMOS18")
    ),

    # PCIe (Gen3 X4 on X8 edge connector).
    ("pcie_x4", 0,
        Subsignal("rst_n", Pins("T19"), IOStandard("LVCMOS12")),
        Subsignal("clk_p", Pins("AB7")),
        Subsignal("clk_n", Pins("AB6")),
        Subsignal("rx_p",  Pins("AB2 AD2 AE4 AF2")),
        Subsignal("rx_n",  Pins("AB1 AD1 AE3 AF1")),
        Subsignal("tx_p",  Pins("AC5 AD7 AE9 AF7")),
        Subsignal("tx_n",  Pins("AC4 AD6 AE8 AF6"))
    ),

    # QSFP28 (156.25MHz RefClk).
    ("qsfp", 0,
        Subsignal("clk_p",   Pins("V7")),
        Subsignal("clk_n",   Pins("V6")),
        Subsignal("txp",     Pins("AA5 W5 U5 R5")),
        Subsignal("txn",     Pins("AA4 W4 U4 R4")),
        Subsignal("rxp",     Pins("Y2 V2 T2 P2")),
        Subsignal("rxn",     Pins("Y1 V1 T1 P1")),
        Subsignal("modsell", Pins("W13"),  IOStandard("LVCMOS33")),
        Subsignal("resetl",  Pins("W12"),  IOStandard("LVCMOS33")),
        Subsignal("modprsl", Pins("AA13"), IOStandard("LVCMOS33")),
        Subsignal("intl",    Pins("Y13"),  IOStandard("LVCMOS33")),
        Subsignal("lpmode",  Pins("W14"),  IOStandard("LVCMOS33")),
    ),
    ("qsfp_i2c", 0,
        Subsignal("scl", Pins("AE15")),
        Subsignal("sda", Pins("AE13")),
        IOStandard("LVCMOS33")
    ),

    # Fan (on when high or floating).
    ("fan", 0, Pins("G9"), IOStandard("LVCMOS33")),

    # MIPI CSI-2 Camera (J3).
    ("mipi_csi", 0,
        Subsignal("clk_p",  Pins("U19")),
        Subsignal("clk_n",  Pins("V19")),
        Subsignal("data_p", Pins("T22 U21 T20 V21")),
        Subsignal("data_n", Pins("T23 U22 U20 V22")),
        IOStandard("MIPI_DPHY_DCI")
    ),
    ("mipi_cam", 0,
        Subsignal("scl",  Pins("J25")),
        Subsignal("sda",  Pins("J26")),
        Subsignal("pwdn", Pins("M21")),
        Subsignal("rst",  Pins("J21")),
        Subsignal("clk",  Pins("K21")),
        IOStandard("LVCMOS18")
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    # FMC HPC (LA00-LA33 and CLK0/CLK1 at VADJ 1.8V, DP0-DP7 on GTY226/GTY227, no HA/HB).
    ("HPC", {
        "DP0_C2M_P"     : "N5",
        "DP0_C2M_N"     : "N4",
        "DP0_M2C_P"     : "M2",
        "DP0_M2C_N"     : "M1",
        "DP1_C2M_P"     : "L5",
        "DP1_C2M_N"     : "L4",
        "DP1_M2C_P"     : "K2",
        "DP1_M2C_N"     : "K1",
        "DP2_C2M_P"     : "J5",
        "DP2_C2M_N"     : "J4",
        "DP2_M2C_P"     : "H2",
        "DP2_M2C_N"     : "H1",
        "DP3_C2M_P"     : "G5",
        "DP3_C2M_N"     : "G4",
        "DP3_M2C_P"     : "F2",
        "DP3_M2C_N"     : "F1",
        "DP4_C2M_P"     : "F7",
        "DP4_C2M_N"     : "F6",
        "DP4_M2C_P"     : "D2",
        "DP4_M2C_N"     : "D1",
        "DP5_C2M_P"     : "E5",
        "DP5_C2M_N"     : "E4",
        "DP5_M2C_P"     : "C4",
        "DP5_M2C_N"     : "C3",
        "DP6_C2M_P"     : "D7",
        "DP6_C2M_N"     : "D6",
        "DP6_M2C_P"     : "B2",
        "DP6_M2C_N"     : "B1",
        "DP7_C2M_P"     : "B7",
        "DP7_C2M_N"     : "B6",
        "DP7_M2C_P"     : "A4",
        "DP7_M2C_N"     : "A3",
        "GBTCLK0_M2C_P" : "P7",
        "GBTCLK0_M2C_N" : "P6",
        "GBTCLK1_M2C_P" : "K7",
        "GBTCLK1_M2C_N" : "K6",
        "CLK0_M2C_P"    : "H23",
        "CLK0_M2C_N"    : "H24",
        "CLK1_M2C_P"    : "B19",
        "CLK1_M2C_N"    : "B20",
        "LA00_CC_P"     : "G24",
        "LA00_CC_N"     : "G25",
        "LA01_CC_P"     : "J23",
        "LA01_CC_N"     : "J24",
        "LA02_P"        : "H21",
        "LA02_N"        : "H22",
        "LA03_P"        : "J19",
        "LA03_N"        : "J20",
        "LA04_P"        : "H26",
        "LA04_N"        : "G26",
        "LA05_P"        : "F24",
        "LA05_N"        : "F25",
        "LA06_P"        : "G20",
        "LA06_N"        : "G21",
        "LA07_P"        : "D24",
        "LA07_N"        : "D25",
        "LA08_P"        : "D26",
        "LA08_N"        : "C26",
        "LA09_P"        : "E25",
        "LA09_N"        : "E26",
        "LA10_P"        : "B25",
        "LA10_N"        : "B26",
        "LA11_P"        : "A24",
        "LA11_N"        : "A25",
        "LA12_P"        : "D23",
        "LA12_N"        : "C24",
        "LA13_P"        : "F23",
        "LA13_N"        : "E23",
        "LA14_P"        : "C23",
        "LA14_N"        : "B24",
        "LA15_P"        : "H18",
        "LA15_N"        : "H19",
        "LA16_P"        : "E21",
        "LA16_N"        : "D21",
        "LA17_CC_P"     : "C18",
        "LA17_CC_N"     : "C19",
        "LA18_CC_P"     : "D19",
        "LA18_CC_N"     : "D20",
        "LA19_P"        : "A22",
        "LA19_N"        : "A23",
        "LA20_P"        : "F20",
        "LA20_N"        : "E20",
        "LA21_P"        : "C21",
        "LA21_N"        : "B21",
        "LA22_P"        : "H16",
        "LA22_N"        : "G16",
        "LA23_P"        : "C22",
        "LA23_N"        : "B22",
        "LA24_P"        : "A17",
        "LA24_N"        : "A18",
        "LA25_P"        : "E18",
        "LA25_N"        : "D18",
        "LA26_P"        : "A19",
        "LA26_N"        : "A20",
        "LA27_P"        : "F18",
        "LA27_N"        : "F19",
        "LA28_P"        : "C17",
        "LA28_N"        : "B17",
        "LA29_P"        : "E16",
        "LA29_N"        : "E17",
        "LA30_P"        : "D16",
        "LA30_N"        : "C16",
        "LA31_P"        : "G15",
        "LA31_N"        : "F15",
        "LA32_P"        : "B15",
        "LA32_N"        : "A15",
        "LA33_P"        : "E15",
        "LA33_N"        : "D15",
        "SCL"           : "F10",
        "SDA"           : "F9",
        "PG_C2M"        : "G10",
    }),

    # 40-pin header J1 (3.3V, IOn_N on pin 2n+1, IOn_P on pin 2n+2): index = header pin number.
    ("j1",
        "None None None D10 D11 E10 E11 B11 C11 C9",
        "D9 A9 B9 A10 B10 A12 A13 A14 B14 C13",
        "C14 B12 C12 D13 D14 E12 E13 F13 F14 F12",
        "G12 G14 H14 J14 J15 H13 J13 None None None",
        "None",
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxUSPPlatform):
    default_clk_name   = "clk200"
    default_clk_period = 1e9/200e6

    def __init__(self, toolchain="vivado"):
        XilinxUSPPlatform.__init__(self, "xcku5p-ffvb676-2-i", _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        return OpenFPGALoader(cable="ft2232", fpga_part="xcku5p-2ffvb676")

    def do_finalize(self, fragment):
        XilinxUSPPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk200", loose=True), 1e9/200e6)

        # IDELAYCTRL SIM_DEVICE: Vivado versions disagree on ULTRASCALE/ULTRASCALE_PLUS for this
        # simulation-only property (2026.1 errors on ULTRASCALE).
        self.add_platform_command("set_property SEVERITY {{Warning}} [get_drc_checks ADEF-911]")

        # Shutdown on overheating
        self.add_platform_command("set_property BITSTREAM.CONFIG.OVERTEMPSHUTDOWN ENABLE [current_design]")

        # Reduce programming time
        self.add_platform_command("set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]")

        # Configuration: Bank 0 at 1.8V, SPIx4 MX25U51245G (512Mbit, 32-bit addressing).
        self.add_platform_command("set_property CONFIG_VOLTAGE 1.8 [current_design]")
        self.add_platform_command("set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]")
        self.add_platform_command("set_property BITSTREAM.CONFIG.SPI_32BIT_ADDR YES [current_design]")
        self.add_platform_command("set_property BITSTREAM.CONFIG.CONFIGRATE 51.0 [current_design]")
