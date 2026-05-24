#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2024 Yu-Ti Kuo <bobgash2@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause
# embedfire rise pro FPGA: https://detail.tmall.com/item.htm?id=645153441975
# Hardware manual:
# https://www.scribd.com/document/941685325/%E9%87%8E%E7%81%AB-%E5%8D%87%E8%85%BE-Pro%E5%BC%80%E5%8F%91%E6%9D%BF%E7%A1%AC%E4%BB%B6%E8%A7%84%E6%A0%BC%E4%B9%A6V1-0-1-copy

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform
from litex.build.xilinx.programmer import VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk50"    , 0, Pins("W19"), IOStandard("LVCMOS33")),
    ("cpu_reset_n", 0, Pins("N15"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led", 0, Pins("M21"),  IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("L21"),  IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("K21"),  IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("K22"),  IOStandard("LVCMOS33")),
    ("user_led", 4, Pins("P20"),  IOStandard("LVCMOS33")),

    # Buttons
    ("user_sw", 0, Pins("V17"),  IOStandard("LVCMOS33")),
    ("user_sw", 1, Pins("W17"),  IOStandard("LVCMOS33")),
    ("user_sw", 2, Pins("AA18"), IOStandard("LVCMOS33")),
    ("user_sw", 3, Pins("AB18"), IOStandard("LVCMOS33")),

    # Beeper (Buzzer)
    ("beeper", 0, Pins("M17"), IOStandard("LVCMOS33")),

    # Fan
    ("fan", 0, Pins("W22"), IOStandard("LVCMOS33")),

    # Serial CH340G
    ("serial", 0,
        Subsignal("tx", Pins("N17")),
        Subsignal("rx", Pins("P17")),
        IOStandard("LVCMOS33")
    ),

    # I2C EEPROM 24C64
    ("i2c", 0,
        Subsignal("scl", Pins("E22")),
        Subsignal("sda", Pins("D22")),
        IOStandard("LVCMOS33"),
    ),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("T10")),
        Subsignal("clk",  Pins("L12")),
        Subsignal("mosi", Pins("P22")),
        Subsignal("miso", Pins("R22")),
        Subsignal("wp",   Pins("P21")),
        Subsignal("hold", Pins("R21")),
        IOStandard("LVCMOS33"),
    ),
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("T10")),
        Subsignal("clk",  Pins("L12")),
        Subsignal("dq",   Pins("P22 R22 P21 R21")),
        IOStandard("LVCMOS33"),
    ),

    # DDR3 SDRAM MT41K256M16
    ("ddram", 0,
        Subsignal("a", Pins(
            "AA4 AB2 AA5 AB3 AB1 U2 W1 R2",
            "V2 U3 Y1 W2 Y2 U1 V3"),
            IOStandard("SSTL135")),
        Subsignal("ba",    Pins("AA1 Y3 AA3"), IOStandard("SSTL135")),
        Subsignal("ras_n", Pins("W6"), IOStandard("SSTL135")),
        Subsignal("cas_n", Pins("U5"), IOStandard("SSTL135")),
        Subsignal("we_n",  Pins("Y4"), IOStandard("SSTL135")),
        Subsignal("cs_n",  Pins("T1"), IOStandard("SSTL135")),
        Subsignal("dm", Pins("D2 G2 M2 M5"), IOStandard("SSTL135")),
        Subsignal("dq", Pins(
            "C2 G1 A1 F3 B2 F1 B1 E2",
            "H3 G3 H2 H5 J1 J5 K1 H4",
            "L4 M3 L3 J6 K3 K6 J4 L5",
            "P1 N4 R1 N2 M6 N5 P6 P2"),
            IOStandard("SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("dqs_p", Pins("E1 K2 M1 P5"),
            IOStandard("DIFF_SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("dqs_n", Pins("D1 J2 L1 P4"),
            IOStandard("DIFF_SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("clk_p", Pins("V4"), IOStandard("DIFF_SSTL135")),
        Subsignal("clk_n", Pins("W4"), IOStandard("DIFF_SSTL135")),
        Subsignal("cke",   Pins("AB5"), IOStandard("SSTL135")),
        Subsignal("odt",   Pins("T5"), IOStandard("SSTL135")),
        Subsignal("reset_n", Pins("R3"), IOStandard("SSTL135")),
        Misc("SLEW=FAST"),
    ),

    # RGMII Ethernet (RTL8211F)
    ("eth_clocks", 0,
        Subsignal("tx", Pins("C18")),
        Subsignal("rx", Pins("C19")),
        IOStandard("LVCMOS33")
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("E21")),
        Subsignal("inib",    Pins("D21")),
        Subsignal("mdio",    Pins("G22")),
        Subsignal("mdc",     Pins("G21")),
        Subsignal("rx_ctl",  Pins("C22")),
        Subsignal("rx_data", Pins("D20 C20 A18 A19")),
        Subsignal("tx_ctl",  Pins("B22")),
        Subsignal("tx_data", Pins("B20 A20 B21 A21")),
        IOStandard("LVCMOS33")
    ),

    # SDCard
    ("spisdcard", 0,
        Subsignal("cd",   Pins("AA19")),
        Subsignal("clk",  Pins("Y22")),
        Subsignal("mosi", Pins("Y21")),
        Subsignal("cs_n", Pins("A14")),
        Subsignal("miso", Pins("AB21")),
        Misc("SLEW=FAST"),
        IOStandard("LVCMOS33"),
    ),

    ("sdcard", 0,
        Subsignal("data", Pins("AB21 AB22 AB20 W21"),),
        Subsignal("cmd",  Pins("Y21"),),
        Subsignal("clk",  Pins("Y22")),
        Subsignal("cd",   Pins("AA19")),
        Misc("SLEW=FAST"),
        IOStandard("LVCMOS33"),
    ),

    # PCIe / SFP GTP bank.
    ("pcie_x1", 0,
        Subsignal("rst_n", Pins("F21"), IOStandard("LVCMOS33"), Misc("PULLUP=TRUE")),
        Subsignal("clk_p", Pins("F10")),
        Subsignal("clk_n", Pins("E10")),
        Subsignal("rx_p",  Pins("D9")),
        Subsignal("rx_n",  Pins("C9")),
        Subsignal("tx_p",  Pins("D7")),
        Subsignal("tx_n",  Pins("C7")),
    ),
    ("pcie_x2", 0,
        Subsignal("rst_n", Pins("F21"), IOStandard("LVCMOS33"), Misc("PULLUP=TRUE")),
        Subsignal("clk_p", Pins("F10")),
        Subsignal("clk_n", Pins("E10")),
        Subsignal("rx_p",  Pins("D9 B10")),
        Subsignal("rx_n",  Pins("C9 A10")),
        Subsignal("tx_p",  Pins("D7 B6")),
        Subsignal("tx_n",  Pins("C7 A6")),
    ),
    ("gtp_refclk", 0,
        Subsignal("p", Pins("F10")),
        Subsignal("n", Pins("E10")),
    ),

    ("sfp", 0,
        Subsignal("txp", Pins("B4")),
        Subsignal("txn", Pins("A4")),
        Subsignal("rxp", Pins("B8")),
        Subsignal("rxn", Pins("A8")),
    ),
    ("sfp_tx_disable", 0, Pins("V18"), IOStandard("LVCMOS33")),
    ("sfp_rx_los",       0, Pins("V19"), IOStandard("LVCMOS33")),
    ("sfp_i2c", 0,
        Subsignal("scl", Pins("Y18"), Misc("PULLUP True")),
        Subsignal("sda", Pins("Y19"), Misc("PULLUP True")),
        IOStandard("LVCMOS33"),
    ),
    ("sfp", 1,
        Subsignal("txp", Pins("D5")),
        Subsignal("txn", Pins("C5")),
        Subsignal("rxp", Pins("D11")),
        Subsignal("rxn", Pins("C11")),
    ),
    ("sfp_tx_disable", 1, Pins("U20"), IOStandard("LVCMOS33")),
    ("sfp_rx_los",       1, Pins("V20"), IOStandard("LVCMOS33")),
    ("sfp_i2c", 1,
        Subsignal("scl", Pins("U17"), Misc("PULLUP True")),
        Subsignal("sda", Pins("U18"), Misc("PULLUP True")),
        IOStandard("LVCMOS33"),
    ),

    # HDMI decoder (SiI9013-compatible parallel output).
    ("hdmi_in", 0,
        Subsignal("clk",     Pins("B17")),
        Subsignal("de",      Pins("B18")),
        Subsignal("hsync",   Pins("F19")),
        Subsignal("vsync",   Pins("F20")),
        Subsignal("scl",     Pins("E19"), Misc("PULLUP True")),
        Subsignal("sda",     Pins("D19"), Misc("PULLUP True")),
        Subsignal("rst_n",   Pins("F15")),
        Subsignal("data",    Pins(
            "C17 D17 E18 F18 A16 A15 B16 B15",
            "C15 C14 D16 E16 E17 F16 A14 A13",
            "B13 C13 D15 D14 F14 F13 E14 E13")),
        IOStandard("LVCMOS33"),
    ),

    # LCD / HDMI encoder (SiI9134-compatible parallel input).
    ("lcd", 0,
        Subsignal("clk",     Pins("K18")),
        Subsignal("de",      Pins("K19")),
        Subsignal("hsync",   Pins("K17")),
        Subsignal("vsync",   Pins("J17")),
        Subsignal("scl",     Pins("E22"), Misc("PULLUP True")),
        Subsignal("sda",     Pins("D22"), Misc("PULLUP True")),
        Subsignal("r",       Pins("K16 L16 K14 K13 H22 J22 J21 J20")),
        Subsignal("g",       Pins("G20 H20 H19 J19 H18 H17 H15 J15")),
        Subsignal("b",       Pins("H14 J14 G18 G17 G16 G15 G13 H13")),
        Subsignal("backlight", Pins("P15")),
        Subsignal("ctp_rst", Pins("T20")),
        Subsignal("ctp_int", Pins("R16")),
        IOStandard("LVCMOS33"),
    ),
    ("hdmi_out", 0,
        Subsignal("clk",     Pins("K18")),
        Subsignal("de",      Pins("K19")),
        Subsignal("hsync",   Pins("K17")),
        Subsignal("vsync",   Pins("J17")),
        Subsignal("scl",     Pins("E19"), Misc("PULLUP True")),
        Subsignal("sda",     Pins("D19"), Misc("PULLUP True")),
        Subsignal("rst_n",   Pins("J16")),
        Subsignal("r",       Pins("K16 L16 K14 K13 H22 J22 J21 J20")),
        Subsignal("g",       Pins("G20 H20 H19 J19 H18 H17 H15 J15")),
        Subsignal("b",       Pins("H14 J14 G18 G17 G16 G15 G13 H13")),
        IOStandard("LVCMOS33"),
    ),

    # OV7725/OV5640 camera header.
    ("camera", 0,
        Subsignal("d",     Pins("N14 N13 R19 P19 U22 AA20 R18 U21")),
        Subsignal("vsync", Pins("T18")),
        Subsignal("href",  Pins("T21")),
        Subsignal("xclk",  Pins("V22")),
        Subsignal("pclk",  Pins("AA21")),
        Subsignal("pwdn",  Pins("R17")),
        Subsignal("reset", Pins("P16")),
        Subsignal("scl",   Pins("R14"), Misc("PULLUP True")),
        Subsignal("sda",   Pins("P14"), Misc("PULLUP True")),
        IOStandard("LVCMOS33"),
    ),
]
# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    # 40-pin expansion headers.
    ("CN3", {
         5: "Y16",
         6: "AA16",
         7: "AA15",
         8: "AB15",
         9: "U15",
        10: "V15",
        11: "T14",
        12: "T15",
        13: "Y13",
        14: "AB14",
        17: "AB11",
        18: "AB12",
        19: "V10",
        20: "W10",
        21: "W11",
        22: "W12",
        23: "AA10",
        24: "AA11",
        25: "Y11",
        26: "Y12",
        29: "V13",
        30: "V14",
        31: "AA13",
        32: "AB13",
        33: "W14",
        34: "Y14",
        35: "W15",
        36: "W16",
        37: "T16",
        38: "U16",
    }),
    ("CN4", {
         5: "L13",
         6: "M13",
         7: "M16",
         8: "M15",
         9: "M20",
        10: "N20",
        11: "M22",
        12: "N22",
        13: "L15",
        14: "L14",
        17: "N19",
        18: "N18",
        19: "L18",
        20: "M18",
        21: "N14",
        22: "N13",
        23: "R19",
        24: "P19",
        25: "V22",
        26: "U22",
        29: "AA21",
        30: "AA20",
        31: "T18",
        32: "R18",
        33: "U21",
        34: "T21",
        35: "R17",
        36: "P16",
        37: "R14",
        38: "P14",
    }),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self, variant="a7-35", toolchain="vivado"):
        device = {
            "a7-35":  "xc7a35tfgg484-2",
            "a7-100": "xc7a100tfgg484-2",
            "a7-200": "xc7a200tfbg484-2"
        }[variant]
        Xilinx7SeriesPlatform.__init__(self, device, _io, _connectors, toolchain=toolchain)
        self.toolchain.bitstream_commands = \
            ["set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]"]
        self.toolchain.additional_commands = \
            ["write_cfgmem -force -format bin -interface spix4 -size 16 "
            "-loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"]
        self.add_platform_command("set_property INTERNAL_VREF 0.675 [get_iobanks 34]")

    def create_programmer(self):
        return VivadoProgrammer(flash_part="mt25ql128-spi-x1_x2_x4")

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
