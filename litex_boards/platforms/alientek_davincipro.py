#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2023 Hans Baier <hansfbaier@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

# Board product page: https://www.alientek.com/productinfo/945752.html
# Taobao item: https://item.taobao.com/item.htm?id=641238123452
# The Taobao agent I used: https://www.basetao.com/?ejATJf+gGuEbpa8IBg

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform, VivadoProgrammer
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk50",     0, Pins("R4"), IOStandard("SSTL135")),
    ("cpu_reset", 0, Pins("U7"), IOStandard("SSTL135")),

    # Leds
    ("user_led", 0, Pins("V9"), IOStandard("SSTL135")),
    ("user_led", 1, Pins("Y8"), IOStandard("SSTL135")),
    ("user_led", 2, Pins("Y7"), IOStandard("SSTL135")),
    ("user_led", 3, Pins("W7"), IOStandard("SSTL135")),

    # Buttons
    ("user_btn", 0, Pins("T4"), IOStandard("SSTL135")),
    ("user_btn", 1, Pins("T3"), IOStandard("SSTL135")),
    ("user_btn", 2, Pins("R6"), IOStandard("SSTL135")),
    ("user_btn", 3, Pins("T6"), IOStandard("SSTL135")),

    # Beeper
    ("beeper", 3, Pins("V7"), IOStandard("SSTL135")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("D17")),
        Subsignal("rx", Pins("E14")),
        IOStandard("LVCMOS33"),
    ),

    # RS485
    ("rs485", 0,
        Subsignal("tx", Pins("T18")),
        Subsignal("rx", Pins("R18")),
        IOStandard("LVCMOS33"),
    ),

    # CAN bus
    ("can", 0,
        Subsignal("tx", Pins("TR18")),
        Subsignal("rx", Pins("AA19")),
        IOStandard("LVCMOS33"),
    ),

    # EEPROM + RTC
    ("i2c", 0,
        Subsignal("sda", Pins("A19")),
        Subsignal("scl", Pins("F13")),
        IOStandard("LVCMOS33")
    ),

    # USB FIFO
    ("usb_clk", 0, Pins("E19"), IOStandard("LVCMOS33")),
    ("usb_fifo", 0, # Can be used when FT232H's Channel is configured to ASYNC FIFO 245 mode
        Subsignal("data",  Pins("C17 F15 F18 E18 E21 D21 F21 E22")),
        Subsignal("rxf_n", Pins("F16")),
        Subsignal("txe_n", Pins("E17")),
        Subsignal("rd_n",  Pins("F19")),
        Subsignal("wr_n",  Pins("F20")),
        Subsignal("siwua", Pins("G21")),
        Subsignal("oe_n",  Pins("D19")),
        Misc("SLEW=FAST"),
        Drive(8),
        IOStandard("LVCMOS33"),
    ),

    # SDCard
    ("spisdcard", 0,
        Subsignal("cd",   Pins("A18")),
        Subsignal("clk",  Pins("A16")),
        Subsignal("mosi", Pins("A15")),
        Subsignal("cs_n", Pins("A14")),
        Subsignal("miso", Pins("B17")),
        Misc("SLEW=FAST"),
        IOStandard("LVCMOS33"),
    ),

    ("sdcard", 0,
        Subsignal("data", Pins("B17 B18 A13 A14"),),
        Subsignal("cmd",  Pins("A15"),),
        Subsignal("clk",  Pins("A16")),
        Subsignal("cd",   Pins("A18")),
        Misc("SLEW=FAST"),
        IOStandard("LVCMOS33"),
    ),

    # DDR3 SDRAM
    ("ddram", 0,
        Subsignal("a", Pins(
            "AA4 AB2 AA5 AB5 AB1 U3 W1 T1", # A0-A7
            "V2  U2  Y1  W2  Y2  U1 V3"),  # A8-A14
            IOStandard("SSTL135")),
        Subsignal("ba",    Pins("AA3 Y3 Y4"), IOStandard("SSTL135")),
        Subsignal("ras_n", Pins("V4"), IOStandard("SSTL135")),
        Subsignal("cas_n", Pins("W4"), IOStandard("SSTL135")),
        Subsignal("we_n",  Pins("AA1"), IOStandard("SSTL135")),
        Subsignal("cs_n",  Pins("AB3"), IOStandard("SSTL135")),
        Subsignal("dm", Pins("D2 G2 M2 M5"), IOStandard("SSTL135")),
        Subsignal("dq", Pins(
            "C2 G1 A1 F3 F1 B2 B1 E2 H3 G3 H2 H5 J1 J5 K1 H4",  # D0-D15
            "L4 M3 L3 J6 K3 K6 J4 L5 P1 N4 R1 N2 M6 N5 P6 P2"), # D16-D31
            IOStandard("SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_50")),
        Subsignal("dqs_p", Pins("E1 K2 M1 P5"), IOStandard("DIFF_SSTL135")),
        Subsignal("dqs_n", Pins("D1 J2 L1 P4"), IOStandard("DIFF_SSTL135")),
        Subsignal("clk_p", Pins("R3"),    IOStandard("DIFF_SSTL135")),
        Subsignal("clk_n", Pins("R2"),    IOStandard("DIFF_SSTL135")),
        Subsignal("cke",   Pins("T5"),    IOStandard("SSTL135")),
        Subsignal("odt",   Pins("U5"),    IOStandard("SSTL135")),
        Subsignal("reset_n", Pins("W6"), IOStandard("SSTL135")),
        Misc("SLEW=FAST"),
    ),

    # RGMII Ethernet
    ("eth_clocks", 0,
        Subsignal("tx", Pins("V18")),
        Subsignal("rx", Pins("U20")),
        IOStandard("LVCMOS33")
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("N20")),
        Subsignal("mdio",    Pins("N22")),
        Subsignal("mdc",     Pins("M22")),
        Subsignal("rx_ctl",  Pins("AA20")),
        Subsignal("rx_data", Pins("AA21 V20 U22 V22")),
        Subsignal("tx_ctl",  Pins("V19")),
        Subsignal("tx_data", Pins("T21 U21 P19 R19")),
        IOStandard("LVCMOS33")
    ),
    ("eth_clocks", 1,
        Subsignal("tx", Pins("W19")),
        Subsignal("rx", Pins("Y18")),
        IOStandard("LVCMOS33")
    ),
    ("eth", 1,
        Subsignal("rst_n",   Pins("N20")),
        Subsignal("mdio",    Pins("N22")),
        Subsignal("mdc",     Pins("M20")),
        Subsignal("rx_ctl",  Pins("AA20")),
        Subsignal("rx_data", Pins("AA21 V20 U22 V22")),
        Subsignal("tx_ctl",  Pins("V19")),
        Subsignal("tx_data", Pins("T21 U21 P19 R19")),
        IOStandard("LVCMOS33")
    ),

    # HDMI I2C
    ("i2c", 1,
        Subsignal("sda", Pins("N18")),
        Subsignal("scl", Pins("L21")),
        IOStandard("LVCMOS33")
    ),
    # HDMI In
    ("adv7611", 0,
        Subsignal("clk",     Pins("L19")),
        Subsignal("rst_n",   Pins("N19")),
        Subsignal("hsync_n", Pins("M22")),
        Subsignal("vsync_n", Pins("M15")),
        Subsignal("de_n",    Pins("M21")),
        Subsignal("r",       Pins("M16 L16 K16 K18 K19 M13 L13 L14")), # D16-D23
        Subsignal("g",       Pins("L15 K13 K14 J16 J15 H15 J14 H14")), # D8-D15
        Subsignal("b",       Pins("H13 G13 J19 H19 G16 G15 G18 G17")), # D0-D7
        IOStandard("LVCMOS33")
    ),


    # HDMI Out
    ("hdmi_out", 0,
        Subsignal("clk_p",   Pins("J20"),   IOStandard("TMDS_33")),
        Subsignal("clk_n",   Pins("J21"),   IOStandard("TMDS_33")),
        Subsignal("data0_p", Pins("J22"),   IOStandard("TMDS_33")),
        Subsignal("data0_n", Pins("H22"),   IOStandard("TMDS_33")),
        Subsignal("data1_p", Pins("K21"),   IOStandard("TMDS_33")),
        Subsignal("data1_n", Pins("K22"),   IOStandard("TMDS_33")),
        Subsignal("data2_p", Pins("H20"),   IOStandard("TMDS_33")),
        Subsignal("data2_n", Pins("G20"),   IOStandard("TMDS_33")),
        Subsignal("scl",     Pins("AA8"),   IOStandard("SSTL135")),
        Subsignal("sda",     Pins("AB8"),   IOStandard("SSTL135")),
    ),

    # RGB TFT-LCD
    ("tft_lcd", 0,
        Subsignal("d", Pins("L14 L13 M13 K19 K18 K16 L16 M16", # D0-D7
                            "H14 J14 H15 J15 J16 K14 K13 L15", # D8-D15
                            "G17 G18 G15 G16 H19 J19 G13 H13"  # G16-D23
        ), IOStandard("LVCMOS33")),
        Subsignal("hsync_n", Pins("M22"), IOStandard("LVCMOS33")),
        Subsignal("vsync_n", Pins("M15"), IOStandard("LVCMOS33")),
        Subsignal("de_n",    Pins("M21"), IOStandard("LVCMOS33")),
        Subsignal("bl",      Pins("W9"), IOStandard("SSTL135")),
        Subsignal("pclk",    Pins("H17"), IOStandard("LVCMOS33")),
        Subsignal("rst",     Pins("Y9"), IOStandard("SSTL135")),
    ),

    # SFP
    ("gtp_refclk", 0,
        Subsignal("p", Pins("F10")),
        Subsignal("n", Pins("E10"))
    ),
    ("sfp_tx", 0,
        Subsignal("p", Pins("B4")),
        Subsignal("n", Pins("A4"))
    ),
    ("sfp_rx", 0,
        Subsignal("p", Pins("B8")),
        Subsignal("n", Pins("A8"))
    ),
    ("sfp_tx_disable_n", 0, Pins("V5"), IOStandard("SSTL135")),
    ("sfp_rx_los",       0, Pins("U6"), IOStandard("SSTL135")),

    # SFP1
    ("sfp_tx", 1,
        Subsignal("p", Pins("D5")),
        Subsignal("n", Pins("C5")),
    ),
    ("sfp_rx", 1,
        Subsignal("p", Pins("D11")),
        Subsignal("n", Pins("C11")),
    ),
    ("sfp_tx_disable_n", 1, Pins("Y6"),  IOStandard("SSTL135")),
    ("sfp_rx_los",       1, Pins("AA6"), IOStandard("SSTL135")),

    ("pcie_x1", 0,
        Subsignal("rst_n", Pins("N15"), IOStandard("LVCMOS33")),
        Subsignal("clk_p", Pins("F6")),
        Subsignal("clk_n", Pins("E6")),
        Subsignal("rx_p",  Pins("D9")),
        Subsignal("rx_n",  Pins("C9")),
        Subsignal("tx_p",  Pins("D7")),
        Subsignal("tx_n",  Pins("C7"))
    ),

    ("pcie_x2", 0,
        Subsignal("rst_n", Pins("N15"), IOStandard("LVCMOS33")),
        Subsignal("clk_p", Pins("F6")),
        Subsignal("clk_n", Pins("E6")),
        Subsignal("rx_p",  Pins("D9 B10")),
        Subsignal("rx_n",  Pins("C9 A10")),
        Subsignal("tx_p",  Pins("D7 B6")),
        Subsignal("tx_n",  Pins("C7 A6"))
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("J3", {
        1: "N14",   2: "N13",
        3: "R14",   4: "P14",
        5: "P17",   6: "N17",
        7: "R16",   8: "P15",
        9: "P16",   10: "R17",
        11: "W17",  12: "V17",
        13: "U18",  14: "U17",
        15: "AB18", 16: "AA18",
        17: "C13",  18: "B13",
        19: "C14",  20: "C15",
        21: "B15",  22: "B16",
        23: "C18",  24: "C19",
        25: "B20",  26: "A20",
        27: "D20",  28: "C20",
        29: "B22",  30: "C22",
        31: "B21",  32: "A21",
        33: "D14",  34: "D15",
        35: "E16",  36: "D16",
    }),
    ("J4", {
        1: "N15",   2: "Y17",
        3: "V10",   4: "W10",
        5: "AA9",   6: "AB10",
        7: "T14",   8: "T15",
        9: "V13",   10: "V14",
        11: "T16",  12: "U16",
        13: "Y14",  14: "W14",
        15: "U15",  16: "V15",
        17: "W16",  18: "W15",
        19: "Y11",  20: "Y12",
        21: "AA10", 22: "AA11",
        23: "AB11", 24: "AB12",
        25: "W11",  26: "W12",
        27: "AA13", 28: "AB13",
        29: "Y13",  30: "AA14",
        31: "AA15", 32: "AB15",
        33: "AB16", 34: "AB17",
        35: "Y16",  36: "AA16",
    }),
]

def raw_j3():
    return [("J3", 0, Pins(" ".join([f"J3:{i+1:d}" for i in range(36)])), IOStandard("LVCMOS33"))]

def raw_j4():
    return [("J4", 0, Pins(" ".join([f"J4:{i+1:d}" for i in range(36)])), IOStandard("LVCMOS33"))]

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self, toolchain="vivado", variant="a7-35"):
        assert variant in ["a7-35", "a7-100"]
        kgates = variant.split("-")[-1]
        self.kgates = kgates
        Xilinx7SeriesPlatform.__init__(self, f"xc7a{kgates}tfgg484-2", _io, _connectors, toolchain=toolchain)
        self.toolchain.bitstream_commands = \
            ["set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]",
             "set_property BITSTREAM.CONFIG.CONFIGRATE 50 [current_design]",
             "set_property CFGBVS VCCO [current_design]",
             "set_property CONFIG_VOLTAGE 3.3 [current_design]",
             "set_property BITSTREAM.CONFIG.UNUSEDPIN PULLUP [current_design]"
            ]
        self.toolchain.additional_commands = \
            ["write_cfgmem -force -format bin -interface spix4 -size 16 "
             "-loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"]
        self.add_platform_command("set_property INTERNAL_VREF 0.675 [get_iobanks 34]")
        self.add_platform_command("set_property INTERNAL_VREF 0.675 [get_iobanks 35]")

    def create_programmer(self):
        return OpenOCD("openocd_alientek_davincipro.cfg", f"bscan_spi_xc7a{self.kgates}t.bit")

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        try:
            self.add_period_constraint(self.lookup_request("eth_clocks").rx, 1e9/125e6)
        except ConstraintError:
            pass

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50",         loose=True), 1e9/50e6)
        self.add_period_constraint(self.lookup_request("usb_clk",       loose=True), 1e9/60e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:rx", loose=True), 1e9/125e6)
