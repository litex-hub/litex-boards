#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 Denis Bodor <lefinnois@lefinnois.net>
# SPDX-License-Identifier: BSD-2-Clause
#
# PZ-A775T-KFB : https://www.puzhi.com/en/detail/442.html
# Also available with XC7A35T, XC7A75T, XC7A100T, or XC7A200T core module, the PCIe card is always the same.

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform
from litex.build.openfpgaloader import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk200", 0,
        Subsignal("p", Pins("R4"), IOStandard("DIFF_SSTL135")),
        Subsignal("n", Pins("T4"), IOStandard("DIFF_SSTL135"))
    ),
    # From chinese PDF tutorial: "the 125MHz clock supplies differential timing for the GTX interface"
    # But there is no GTX transceivers in Artix-7. It's GTP (GTPE2).
    # In the same PDF, the package name is also incorrectly used as "FFG484" but it should be "FGG484". So "GTX" may actually mean "GTx".
    ("clk125", 0,
        Subsignal("p", Pins("F10")),
        Subsignal("n", Pins("E10"))
    ),
    ("cpu_reset", 0, Pins("R14"), IOStandard("LVCMOS33")),

    # Leds - active high
    ("user_led", 0, Pins("P15"),  IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("R16"),  IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("N13"),  IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("N14"),  IOStandard("LVCMOS33")),
    ("user_led", 4, Pins("AA18"), IOStandard("LVCMOS33")),

    # Leds on core module (under heatsink)
    ("module_led", 0, Pins("P20"), IOStandard("LVCMOS33")),
    ("module_led", 1, Pins("N15"), IOStandard("LVCMOS33")),

    # Buttons
    ("user_btn", 0, Pins("AB18"), IOStandard("LVCMOS33")),
    ("user_btn", 1, Pins("Y18"),  IOStandard("LVCMOS33")),
    ("user_btn", 2, Pins("Y19"),  IOStandard("LVCMOS33")),
    ("user_btn", 3, Pins("U17"),  IOStandard("LVCMOS33")),
    ("user_btn", 4, Pins("U18"),  IOStandard("LVCMOS33")),

    # Serial J4
    ("serial", 0,
        Subsignal("tx", Pins("V18")),
        Subsignal("rx", Pins("V19")),
        IOStandard("LVCMOS33")
    ),

    # I2C / AT24C64
    ("i2c", 0,
        Subsignal("scl", Pins("E21")),
        Subsignal("sda", Pins("D21")),
        IOStandard("LVCMOS33")
    ),

    # SDCard J5
    ("spisdcard", 0,
        Subsignal("clk",  Pins("B20")),
        Subsignal("cs_n", Pins("A21")),
        Subsignal("mosi", Pins("E17"), Misc("PULLUP")),
        Subsignal("miso", Pins("A20"), Misc("PULLUP")),
        Misc("SLEW=FAST"),
        IOStandard("LVCMOS33")
    ),
    ("sdcard", 0,
        Subsignal("clk",  Pins("B20")),
        Subsignal("cmd",  Pins("E17"), Misc("PULLUP True")),
        Subsignal("data", Pins("A20 B21 F16 A21"), Misc("PULLUP True")),
        Misc("SLEW=FAST"),
        IOStandard("LVCMOS33")
    ),

    # SPIFlash
    ("flash_cs_n", 0, Pins("T19"), IOStandard("LVCMOS33")),
    ("flash", 0,
        Subsignal("mosi", Pins("P22")),
        Subsignal("miso", Pins("R22")),
        Subsignal("wp",   Pins("P21")),
        Subsignal("hold", Pins("R21")),
        IOStandard("LVCMOS33"),
    ),

    # DDR3 SDRAM MT41K256M16
    ("ddram", 0,
        Subsignal("a", Pins(
            "AA4 AB2 AA5 AB5 AB1 U3 W1 T1",
            "V2  U2  Y1  W2  Y2  U1 W5"),
            IOStandard("SSTL135")),
        Subsignal("ba",    Pins("AA3 Y3 Y4"), IOStandard("SSTL135")),
        Subsignal("ras_n", Pins("V4"), IOStandard("SSTL135")),
        Subsignal("cas_n", Pins("W4"), IOStandard("SSTL135")),
        Subsignal("we_n",  Pins("AA1"), IOStandard("SSTL135")),
        Subsignal("cs_n",  Pins("AB3"), IOStandard("SSTL135")),
        Subsignal("dm",    Pins("D2 G2 M2 M5"),IOStandard("SSTL135")),
        Subsignal("dq",    Pins(
            "C2 G1 A1 F3 B2 F1 B1 E2",
            "H3 G3 H2 H5 J1 J5 K1 H4",
            "L4 M3 L3 J6 K3 K6 J4 L5",
            "P1 N4 R1 N2 M6 N5 P6 P2"),
            IOStandard("SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("dqs_n", Pins("D1 J2 L1 P4"),
            IOStandard("DIFF_SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("dqs_p", Pins("E1 K2 M1 P5"),
            IOStandard("DIFF_SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("clk_p", Pins("R3"), IOStandard("DIFF_SSTL135")),
        Subsignal("clk_n", Pins("R2"), IOStandard("DIFF_SSTL135")),
        Subsignal("cke",   Pins("T5"), IOStandard("SSTL135")),
        Subsignal("odt",   Pins("U5"), IOStandard("SSTL135")),
        Subsignal("reset_n", Pins("W6"), IOStandard("SSTL135")),
        Misc("SLEW=FAST")
    ),

    # PCIe
    ("pcie_x1", 0,
        Subsignal("rst_n", Pins("A13"), IOStandard("LVCMOS33")),
        Subsignal("clk_p", Pins("F6")),
        Subsignal("clk_n", Pins("E6")),
        Subsignal("rx_p",  Pins("D11")),
        Subsignal("rx_n",  Pins("C11")),
        Subsignal("tx_p",  Pins("D5")),
        Subsignal("tx_n",  Pins("C5")),
    ),
    ("pcie_x2", 0,
        Subsignal("rst_n", Pins("A13"), IOStandard("LVCMOS33")),
        Subsignal("clk_p", Pins("F6")),
        Subsignal("clk_n", Pins("E6")),
        Subsignal("rx_p",  Pins("D11 B8")),
        Subsignal("rx_n",  Pins("C11 A8")),
        Subsignal("tx_p",  Pins("D5 B4")),
        Subsignal("tx_n",  Pins("C5 A4"))
    ),

    # SFP-1 J12
    ("sfp", 0,
        Subsignal("txp", Pins("B6")),
        Subsignal("txn", Pins("A6")),
        Subsignal("rxp", Pins("B10")),
        Subsignal("rxn", Pins("A10")),
    ),
    ("sfp_tx_disable", 0, Pins("A14"),  IOStandard("LVCMOS33")),

    # SFP-2 J11
    ("sfp", 1,
        Subsignal("txp", Pins("D7")),
        Subsignal("txn", Pins("C7")),
        Subsignal("rxp", Pins("D9")),
        Subsignal("rxn", Pins("C9")),
    ),
    ("sfp_tx_disable", 1, Pins("A15"),  IOStandard("LVCMOS33")),

    # RGMII Ethernet (RTL8211F) on core module
    ("eth_clocks", 0,
        Subsignal("tx", Pins("N17")),
        Subsignal("rx", Pins("U20")),
        IOStandard("LVCMOS33")
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("P17")), # marked “reserved” in the manual but used in the sample project (?)
        Subsignal("mdio",    Pins("T20")),
        Subsignal("mdc",     Pins("AA19")),
        Subsignal("rx_ctl",  Pins("AB20")),
        Subsignal("rx_data", Pins("AA20 AB21 AA21 AB22")),
        Subsignal("tx_ctl",  Pins("Y21")),
        Subsignal("tx_data", Pins("V22 W22 W21 Y22")),
        IOStandard("LVCMOS33")
    ),
    # RGMII Ethernet (RTL8211F) on board
    ("eth_clocks", 1,
        Subsignal("tx", Pins("M15")),
        Subsignal("rx", Pins("J19")),
        IOStandard("LVCMOS33")
    ),
    ("eth", 1,
        Subsignal("rst_n",   Pins("L13")),
        Subsignal("mdio",    Pins("J17")),
        Subsignal("mdc",     Pins("N17")),
        Subsignal("rx_ctl",  Pins("H19")),
        Subsignal("rx_data", Pins("J14 H14 J20 J21")),
        Subsignal("tx_ctl",  Pins("M16")),
        Subsignal("tx_data", Pins("K13 K14 L14 L15")),
        IOStandard("LVCMOS33")
    ),

    # HDMI out 0
    ("hdmi_out", 0,
        Subsignal("clk_p",   Pins("B17"), IOStandard("TMDS_33")),
        Subsignal("clk_n",   Pins("B18"), IOStandard("TMDS_33")),
        Subsignal("data0_p", Pins("B15"), IOStandard("TMDS_33")),
        Subsignal("data0_n", Pins("B16"), IOStandard("TMDS_33")),
        Subsignal("data1_p", Pins("D14"), IOStandard("TMDS_33")),
        Subsignal("data1_n", Pins("D15"), IOStandard("TMDS_33")),
        Subsignal("data2_p", Pins("D17"), IOStandard("TMDS_33")),
        Subsignal("data2_n", Pins("C17"), IOStandard("TMDS_33")),
        Subsignal("scl",     Pins("A18"), IOStandard("LVCMOS33")),
        Subsignal("sda",     Pins("A19"), IOStandard("LVCMOS33")),
        Subsignal("hdp",     Pins("D20"), IOStandard("LVCMOS33")),
        Subsignal("cec",     Pins("F19"), IOStandard("LVCMOS33")),
        # HDMI1_OUT_EN C20
    ),

    ("hdmi_out", 1,
        Subsignal("clk_p",   Pins("E19"), IOStandard("TMDS_33")),
        Subsignal("clk_n",   Pins("D19"), IOStandard("TMDS_33")),
        Subsignal("data0_p", Pins("F13"), IOStandard("TMDS_33")),
        Subsignal("data0_n", Pins("F14"), IOStandard("TMDS_33")),
        Subsignal("data1_p", Pins("E13"), IOStandard("TMDS_33")),
        Subsignal("data1_n", Pins("E14"), IOStandard("TMDS_33")),
        Subsignal("data2_p", Pins("C18"), IOStandard("TMDS_33")),
        Subsignal("data2_n", Pins("C19"), IOStandard("TMDS_33")),
        Subsignal("scl",     Pins("C13"), IOStandard("LVCMOS33")),
        Subsignal("sda",     Pins("B13"), IOStandard("LVCMOS33")),
        Subsignal("hdp",     Pins("C14"), IOStandard("LVCMOS33")),
        Subsignal("cec",     Pins("C22"), IOStandard("LVCMOS33")),
        # HDMI1_OUT_EN C15
    ),
]

_connectors = [
    ("JM1", {
#         1: VDD_5V,   2: VDD_3V3,
#         3: GND,      4: GND,
          5: "G17",    6: "J15",
          7: "G18",    8: "H15",
          9: "G15",   10: "K18",
         11: "G16",   12: "K19",
         13: "H17",   14: "H20",
         15: "H18",   16: "G20",
         17: "J22",   18: "M21",
         19: "H22",   20: "L21",
         21: "H13",   22: "L19",
         23: "G13",   24: "L20",
         25: "K21",   26: "N22",
         27: "K22",   28: "M22",
         29: "L16",   30: "N20",
         31: "K16",   32: "M20",
#        33: GND,     34: GND,
#        35: GND,     36: GND,
         37: "M18",   38: "N18",
         39: "L18",   40: "N19",
    }),
    ("JM2", {
#         1: VDD_5V,   2: VDD_3V3,
#         3: GND,      4: GND,
          5: "Y16",    6: "T14",
          7: "AA16",   8: "T15",
          9: "W15",   10: "U15",
         11: "W16",   12: "V15",
         13: "AB16",  14: "V13",
         15: "AB17",  16: "V14",
         17: "W14",   18: "W11",
         19: "Y14",   20: "W12",
         21: "AA15",  22: "Y13",
         23: "AB15",  24: "AA14",
         25: "AA13",  26: "AA10",
         27: "AB13",  28: "AA11",
         29: "AB11",  30: "Y11",
         31: "AB12",  32: "Y12",
#        33: GND,     34: GND,
#        35: GND,     36: GND,
         37: "AA9",   38: "V10",
         39: "AB10",  40: "W10",
    })
]

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk200"
    default_clk_period = 1e9/200e6
    kgates             = None

    def __init__(self, kgates=75, toolchain="vivado"):
        assert(kgates in [35, 75, 100, 200], "kgates can only be 35, 75, 100 or 200, representing a XC7A35T, XC7A75T, XC7TA100T, XC7A200T")
        self.kgates = kgates
        device = "xc7a200tfbg484-2" if kgates == 200 else f"xc7a{kgates}tfgg484-2"
        io = _io
        connectors = _connectors

        Xilinx7SeriesPlatform.__init__(self, device, io, connectors, toolchain=toolchain)

        self.add_platform_command("set_property INTERNAL_VREF 0.750 [get_iobanks 34]")
        self.add_platform_command("set_property INTERNAL_VREF 0.750 [get_iobanks 35]")

        self.toolchain.bitstream_commands = [
            "set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]",
            "set_property BITSTREAM.CONFIG.CONFIGRATE 16 [current_design]",
            "set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]",
            "set_property CFGBVS VCCO [current_design]",
            "set_property CONFIG_VOLTAGE 3.3 [current_design]",
        ]

    def create_programmer(self):
        part = "xc7a200tfbg484" if self.kgates == 200 else f"xc7a{self.kgates}tfgg484"
        return OpenFPGALoader(cable="ft232", fpga_part=part)

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk200",           loose=True), 1e9/200e6)
        self.add_period_constraint(self.lookup_request("clk125",           loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:rx", 0, loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:tx", 0, loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:rx", 1, loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:tx", 1, loose=True), 1e9/125e6)
