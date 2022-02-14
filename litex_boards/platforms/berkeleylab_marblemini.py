#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Vamsi K Vytla <vamsi.vytla@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause


# The Marble-Mini is a simple AMC FMC carrier board with SFP, 2x FMC, PoE, DDR3:
# https://github.com/BerkeleyLab/Marble-Mini

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform, VivadoProgrammer
from litex.build.openocd import OpenOCD

# TODO:
# - Add the TMDS lanes for the HDMI connector.
# - Populate the SFPs.
# - verify period constraint on mgt_clk1.

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk20_vcxo",    0, Pins("D17"), IOStandard("LVCMOS33")),
    ("clk20_vcxo_en", 0, Pins("E13"), IOStandard("LVCMOS33"), Misc("PULLUP=TRUE")),  # Set it to 1 to enable clk20_-vcxo.
    ("mgt_clk", 0,
        Subsignal("p", Pins("F6")),
        Subsignal("n", Pins("E6"))
    ),

    ("mgt_clk", 1,
        Subsignal("p", Pins("F10")),
        Subsignal("n", Pins("E10"))
    ),

    # Serial
    ("serial", 0,
        Subsignal("rts", Pins("W9")),
        Subsignal("rx",  Pins("U7")),
        Subsignal("tx",  Pins("Y9")),
        IOStandard("LVCMOS25")
    ),

    # RGMII Ethernet
    ("eth_clocks", 0,
        Subsignal("tx", Pins("J15")),
        Subsignal("rx", Pins("L19")),
        IOStandard("LVCMOS25")
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("M17")),
        Subsignal("rx_ctl",  Pins("H15")),
        Subsignal("rx_data", Pins("K13 H14 J14 K14")),
        Subsignal("tx_ctl",  Pins("J16")),
        Subsignal("tx_data", Pins("G15 G16 G13 H13")),
        IOStandard("LVCMOS25"),
    ),

    # DDR3 SDRAM
    ("ddram", 0,
        Subsignal("a", Pins(
            "L6 M5 P6 K6 M1 M3 N2 M6",
            "P1 P2 L4 N5 L3 R1 N3 E3"),
            IOStandard("SSTL135")),
        Subsignal("ba",    Pins("L5 M2 N4"), IOStandard("SSTL135")),
        Subsignal("ras_n", Pins("J4"), IOStandard("SSTL135")),
        Subsignal("cas_n", Pins("J6"), IOStandard("SSTL135")),
        Subsignal("we_n", Pins("K3"),  IOStandard("SSTL135")),
        Subsignal("dm", Pins("G2 E2"), IOStandard("SSTL135")),
        Subsignal("dq", Pins(
            "G3 J1 H4 H5 H2 K1 H3 J5",
            "G1 B1 F1 F3 C2 A1 D2 B2"),
            IOStandard("SSTL135")),
        Subsignal("dqs_p", Pins("K2 E1"), IOStandard("DIFF_SSTL135")),
        Subsignal("dqs_n", Pins("J2 D1"), IOStandard("DIFF_SSTL135")),
        Subsignal("clk_p", Pins("P5"), IOStandard("DIFF_SSTL135")),
        Subsignal("clk_n", Pins("P4"), IOStandard("DIFF_SSTL135")),
        Subsignal("cke",   Pins("L1"), IOStandard("SSTL135")),
        Subsignal("odt",   Pins("K4"), IOStandard("SSTL135")),
        # Subsignal("cs_n", Pins(""), IOStandard("SSTL135")),
        Subsignal("reset_n", Pins("G4"), IOStandard("SSTL135"))
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("PMOD0", "C18 D22 E22 G21 D21 E21 F21 G22"),
    ("PMOD1", "F13 C14 C15 D16 F14 F15 F16 E16"),
    ("FMC1_LPC", {
        "CLK0_M2C_N": "W20",
        "CLK0_M2C_P": "W19",
        "CLK1_M2C_N": "Y19",
        "CLK1_M2C_P": "Y18",
        "LA00_N":     "V20",
        "LA00_P":     "U20",
        "LA01_N":     "V19",
        "LA01_P":     "V18",
        "LA02_N":     "R16",
        "LA02_P":     "P15",
        "LA03_N":     "N14",
        "LA03_P":     "N13",
        "LA04_N":     "W17",
        "LA04_P":     "V17",
        "LA05_N":     "R19",
        "LA05_P":     "P19",
        "LA06_N":     "AB18",
        "LA06_P":     "AA18",
        "LA07_N":     "AA21",
        "LA07_P":     "AA20",
        "LA08_N":     "P17",
        "LA08_P":     "N17",
        "LA09_N":     "T18",
        "LA09_P":     "R18",
        "LA10_N":     "AB20",
        "LA10_P":     "AA19",
        "LA11_N":     "R17",
        "LA11_P":     "P16",
        "LA12_N":     "U18",
        "LA12_P":     "U17",
        "LA13_N":     "W22",
        "LA13_P":     "W21",
        "LA14_N":     "AB22",
        "LA14_P":     "AB21",
        "LA15_N":     "Y22",
        "LA15_P":     "Y21",
        "LA16_N":     "R14",
        "LA16_P":     "P14",
        "LA17_N_CC":  "K19",
        "LA17_P_CC":  "K18",
        "LA18_N_CC":  "H19",
        "LA18_P_CC":  "J19",
        "LA19_N":     "J17",
        "LA19_P":     "K17",
        "LA20_N":     "L15",
        "LA20_P":     "L14",
        "LA21_N":     "N19",
        "LA21_P":     "N18",
        "LA22_N":     "L21",
        "LA22_P":     "M21",
        "LA23_N":     "M20",
        "LA23_P":     "N20",
        "LA24_N":     "H18",
        "LA24_P":     "H17",
        "LA25_N":     "L18",
        "LA25_P":     "M18",
        "LA26_N":     "G20",
        "LA26_P":     "H20",
        "LA27_N":     "M22",
        "LA27_P":     "N22",
        "LA28_N":     "M16",
        "LA28_P":     "M15",
        "LA29_N":     "K22",
        "LA29_P":     "K21",
        "LA30_N":     "K16",
        "LA30_P":     "L16",
        "LA31_N":     "H22",
        "LA31_P":     "J22",
        "LA32_N":     "G18",
        "LA32_P":     "G17",
        "LA33_N":     "J21",
        "LA33_P":     "J20"
    }),
    ("FMC2_LPC", {
        "CLK0_M2C_N": "W4",
        "CLK0_M2C_P": "V4",
        "CLK1_M2C_N": "T4",
        "CLK1_M2C_P": "R4",
        "LA00_N":     "U5",
        "LA00_P":     "T5",
        "LA01_N":     "AA4",
        "LA01_P":     "Y4",
        "LA02_N":     "V3",
        "LA02_P":     "U3",
        "LA03_N":     "V2",
        "LA03_P":     "U2",
        "LA04_N":     "V5",
        "LA04_P":     "U6",
        "LA05_N":     "T6",
        "LA05_P":     "R6",
        "LA06_N":     "U1",
        "LA06_P":     "T1",
        "LA07_N":     "V8",
        "LA07_P":     "V9",
        "LA08_N":     "Y2",
        "LA08_P":     "W2",
        "LA09_N":     "AA3",
        "LA09_P":     "Y3",
        "LA10_N":     "Y1",
        "LA10_P":     "W1",
        "LA11_N":     "AA6",
        "LA11_P":     "Y6",
        "LA12_N":     "W5",
        "LA12_P":     "W6",
        "LA13_N":     "W7",
        "LA13_P":     "V7",
        "LA14_N":     "AB1",
        "LA14_P":     "AA1",
        "LA15_N":     "AB5",
        "LA15_P":     "AA5",
        "LA16_N":     "AB2",
        "LA16_P":     "AB3",
        "LA17_N":     "W12",
        "LA17_P":     "W11",
        "LA18_N":     "V14",
        "LA18_P":     "V13",
        "LA19_N":     "Y12",
        "LA19_P":     "Y11",
        "LA20_N":     "AA11",
        "LA20_P":     "AA10",
        "LA21_N":     "AA14",
        "LA21_P":     "Y13",
        "LA22_N":     "W16",
        "LA22_P":     "W15",
        "LA23_N":     "W10",
        "LA23_P":     "V10",
        "LA24_N":     "Y14",
        "LA24_P":     "W14",
        "LA25_N":     "AB12",
        "LA25_P":     "AB11",
        "LA26_N":     "AA16",
        "LA26_P":     "Y16",
        "LA27_N":     "AB10",
        "LA27_P":     "AA9",
        "LA28_N":     "T15",
        "LA28_P":     "T14",
        "LA29_N":     "U16",
        "LA29_P":     "T16",
        "LA30_N":     "V15",
        "LA30_P":     "U15",
        "LA31_N":     "AB13",
        "LA31_P":     "AA13",
        "LA32_N":     "AB15",
        "LA32_P":     "AA15",
        "LA33_N":     "AB17",
        "LA33_P":     "AB16"
    })
]

_pmod0_pins    = ["PMOD0:{}".format(i) for i in range(8)]
_pmod1_pins    = ["PMOD1:{}".format(i) for i in range(8)]
break_off_pmod = [
    ("pmod0", 0, Pins(*_pmod0_pins), IOStandard("LVCMOS33")),
    ("pmod1", 0, Pins(*_pmod1_pins), IOStandard("LVCMOS33")),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "clk20_vcxo"
    default_clk_period = 1e9/20e6

    def __init__(self, toolchain="vivado"):
        XilinxPlatform.__init__(self, "xc7a100t-2fgg484", _io, _connectors, toolchain=toolchain)
        self.toolchain.bitstream_commands = [
            "set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]"
        ]
        self.toolchain.additional_commands = [
            "write_cfgmem -force -format bin -interface spix4 -size 16 -loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"
        ]
        self.add_platform_command("set_property INTERNAL_VREF 0.675 [get_iobanks 35]")
        self.add_platform_command("set_property CFGBVS VCCO [current_design]")
        self.add_platform_command("set_property CONFIG_VOLTAGE 3.3 [current_design]")

    def create_programmer(self):
        return OpenOCD("openocd_marblemini.cfg")

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk20_vcxo",  loose=True),   1e9/20e6)
        self.add_period_constraint(self.lookup_request("mgt_clk", 0,  loose=True),   1e9/125e6)
        self.add_period_constraint(self.lookup_request("mgt_clk", 1,  loose=True),   1e9/125e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:rx", loose=True), 1e9/125e6)
