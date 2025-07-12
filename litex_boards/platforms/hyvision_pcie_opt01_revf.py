#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 Hans Baier <foss@hans-baier.de>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform, VivadoProgrammer
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk50",  0, Pins("D24"), IOStandard("LVCMOS33")),
    ("clk200", 0,
        Subsignal("p", Pins("AA10"), IOStandard("DIFF_SSTL18_II")),
        Subsignal("n", Pins("AB10"), IOStandard("DIFF_SSTL18_II")),
    ),

    # fitted LEDs, active high
    ("user_led",  0, Pins("D26"), IOStandard("LVCMOS33")), # D5
    ("user_led",  1, Pins("D25"), IOStandard("LVCMOS33")), # D3
    ("user_led",  2, Pins("C26"), IOStandard("LVCMOS33")), # D6
    ("user_led",  3, Pins("C21"), IOStandard("LVCMOS33")), # D4
    ("user_led",  4, Pins("G25"), IOStandard("LVCMOS33")), # D8
    ("user_led",  5, Pins("F25"), IOStandard("LVCMOS33")), # D7
    ("user_led",  6, Pins("E26"), IOStandard("LVCMOS33")), # D10
    ("user_led",  7, Pins("E25"), IOStandard("LVCMOS33")), # D9

    # outside facing LEDs on face plate
    ("user_led",   8, Pins("E15"), IOStandard("LVCMOS33")), # red 1
    ("user_led",   9, Pins("E16"), IOStandard("LVCMOS33")), # green 1
    ("user_led",  10, Pins("E17"), IOStandard("LVCMOS33")), # red 2
    ("user_led",  11, Pins("E18"), IOStandard("LVCMOS33")), # green 2

    # not fitted LEDs
    ("user_led",  12, Pins("J26"), IOStandard("LVCMOS33")), # D12
    ("user_led",  13, Pins("J25"), IOStandard("LVCMOS33")), # D14
    ("user_led",  14, Pins("H26"), IOStandard("LVCMOS33")), # D13
    ("user_led",  15, Pins("G26"), IOStandard("LVCMOS33")), # D15

    # Switches
    ("user_sw", 0, Pins("D19"), IOStandard("LVCMOS33")),
    ("user_sw", 1, Pins("C19"), IOStandard("LVCMOS33")),

    # Testpoints
    ("tp", 1, Pins("A15"), IOStandard("LVCMOS33")),
    ("tp", 2, Pins("C16"), IOStandard("LVCMOS33")),
    ("tp", 3, Pins("B15"), IOStandard("LVCMOS33")),
    ("tp", 4, Pins("D16"), IOStandard("LVCMOS33")),
    ("tp", 5, Pins("B14"), IOStandard("LVCMOS33")),
    ("tp", 6, Pins("A14"), IOStandard("LVCMOS33")),
    ("tp", 7, Pins("C17"), IOStandard("LVCMOS33")),
    ("tp", 8, Pins("D18"), IOStandard("LVCMOS33")),
    ("tp", 9, Pins("C18"), IOStandard("LVCMOS33")),

    # Not sure about this, but the documentation says 2X SPI
    # and these pins are the standard configuration pins
    ("spiflash2x", 0,  # clock needs to be accessed through STARTUPE2
        Subsignal("cs_n", Pins("C23")),
        Subsignal("dq",   Pins("B24 A25")),
        IOStandard("LVCMOS33")
    ),

    # DDR2 SDRAM.
    ("ddram", 0,
        Subsignal("cke",   Pins("AC12"),        IOStandard("SSTL18_II")),
        Subsignal("ras_n", Pins("AA9"),         IOStandard("SSTL18_II")),
        Subsignal("cas_n", Pins("AB9"),         IOStandard("SSTL18_II")),
        Subsignal("we_n",  Pins("AC9"),         IOStandard("SSTL18_II")),
        Subsignal("ba",    Pins("AC7 AB7 AD8"), IOStandard("SSTL18_II")),
        Subsignal("a",     Pins("AC8 AA7 AA8 AF7 AE7 W8 V9 Y10 Y11 Y7 Y8 W9 W10"),
            IOStandard("SSTL18_II")),
        Subsignal("dq",    Pins(
            " U5  U2  U1  V3  W3 U7 V6  V4  Y2  V2  V1  W1  Y1 AB2 AC2 AA3 ",
            "AA4 AB4 AC4 AC3 AC6 Y6 Y5 AD6 AD1 AE1 AE3 AE2 AE6 AE5 AF3 AF2"),
            IOStandard("SSTL18_II_T_DCI")),
        Subsignal("dqs_p", Pins("W6 AB1 AA5 AF5"), IOStandard("DIFF_SSTL18_II_T_DCI")), # AF5: Doubtful.
        Subsignal("dqs_n", Pins("W5 AC1 AB5 AF4"), IOStandard("DIFF_SSTL18_II_T_DCI")), # AF4: Doubtful.
        Subsignal("clk_p", Pins("V11 V8"),         IOStandard("DIFF_SSTL18_II")),
        Subsignal("clk_n", Pins("W11 V7"),         IOStandard("DIFF_SSTL18_II")),
        Subsignal("dm",    Pins("U6 Y3 AB6 AD4"),  IOStandard("SSTL18_II")),
        Subsignal("odt",   Pins("AA13"),           IOStandard("SSTL18_II")), # FIXME: re-adds AA12 when 2nd chip working
        Subsignal("cs_n",  Pins("AD9"),            IOStandard("SSTL18_II")), # FIXME: re-adds AB12 when 2nd chip working
        Misc("SLEW=FAST"),
    ),

    ("pcie_x1", 0,
        Subsignal("rst_n", Pins("D10"), IOStandard("LVCMOS33")),
        Subsignal("clk_p", Pins("D6")),
        Subsignal("clk_n", Pins("D5")),
        Subsignal("rx_p",  Pins("B6")),
        Subsignal("rx_n",  Pins("B5")),
        Subsignal("tx_p",  Pins("A4")),
        Subsignal("tx_n",  Pins("A3"))
    ),
    ("pcie_x2", 0,
        Subsignal("rst_n", Pins("D10"), IOStandard("LVCMOS33")),
        Subsignal("clk_p", Pins("D6")),
        Subsignal("clk_n", Pins("D5")),
        Subsignal("rx_p",  Pins("B6 C4")),
        Subsignal("rx_n",  Pins("B5 C3")),
        Subsignal("tx_p",  Pins("A4 B2")),
        Subsignal("tx_n",  Pins("A3 B1"))
    ),
    ("pcie_x4", 0,
        Subsignal("rst_n", Pins("D10"), IOStandard("LVCMOS33")),
        Subsignal("clk_p", Pins("D6")),
        Subsignal("clk_n", Pins("D5")),
        Subsignal("rx_p",  Pins("B6 C4 E4 G4")),
        Subsignal("rx_n",  Pins("B5 C3 E3 G3")),
        Subsignal("tx_p",  Pins("A4 B2 D2 F2")),
        Subsignal("tx_n",  Pins("A3 B1 D1 F1"))
    ),

    # SFP
    ("sfp", 0,  # SFP CN1
        Subsignal("txp", Pins("H2")),
        Subsignal("txn", Pins("H1")),
        Subsignal("rxp", Pins("J4")),
        Subsignal("rxn", Pins("J3")),
        Subsignal("sda", Pins("A10"), IOStandard("LVCMOS33")),
        Subsignal("scl", Pins("B10"), IOStandard("LVCMOS33")),
    ),
    ("sfp_tx", 0,  # SFP CN1
        Subsignal("p", Pins("H2")),
        Subsignal("n", Pins("H1")),
    ),
    ("sfp_rx", 0,  # SFP CN1
        Subsignal("p", Pins("J4")),
        Subsignal("n", Pins("J3")),
    ),
    ("sfp_tx_fault",   0, Pins("A9"),  IOStandard("LVCMOS33")),
    ("sfp_tx_disable", 0, Pins("B9"),  IOStandard("LVCMOS33")),
    ("sfp_mod_abs",    0, Pins("C9"),  IOStandard("LVCMOS33")),
    ("sfp_rs0",        0, Pins("D9"),  IOStandard("LVCMOS33")),
    ("sfp_los",        0, Pins("C11"), IOStandard("LVCMOS33")),
    ("sfp_rs1",        0, Pins("D11"), IOStandard("LVCMOS33")),

    ("sfp", 1,  # SFP CN2
        Subsignal("txp", Pins("K2")),
        Subsignal("txn", Pins("K1")),
        Subsignal("rxp", Pins("L4")),
        Subsignal("rxn", Pins("L3")),
        Subsignal("sda", Pins("E13"), IOStandard("LVCMOS33")),
        Subsignal("scl", Pins("D13"), IOStandard("LVCMOS33")),
    ),
    ("sfp_tx", 1,  # SFP CN2
        Subsignal("p", Pins("K2")),
        Subsignal("n", Pins("K1")),
    ),
    ("sfp_rx", 1,  # SFP CN2
        Subsignal("p", Pins("L4")),
        Subsignal("n", Pins("L3")),
    ),
    ("sfp_tx_fault",   1, Pins("C12"), IOStandard("LVCMOS33")),
    ("sfp_tx_disable", 1, Pins("E12"), IOStandard("LVCMOS33")),
    ("sfp_mod_abs",    1, Pins("C13"), IOStandard("LVCMOS33")),
    ("sfp_rs0",        1, Pins("F14"), IOStandard("LVCMOS33")),
    ("sfp_los",        1, Pins("C14"), IOStandard("LVCMOS33")),
    ("sfp_rs1",        1, Pins("D14"), IOStandard("LVCMOS33")),

    # DVP
    ("dvp", 0,
        Subsignal("r",    Pins("H22 G22 F22 E21 D21 N19 P20 P21")),
        Subsignal("g",    Pins("M19 C24 C22 N21 M21 L22 K22 J21")),
        Subsignal("b",    Pins("J23 H24 L23 K23 G24 F24 F23 E23")),
        Subsignal("cc_d", Pins("R22 T22 R21 T20")),
        Subsignal("lval", Pins("U20")),
        Subsignal("fval", Pins("T18")),
        Subsignal("dval", Pins("M20")),
        Subsignal("pclk", Pins("D23")),
        Subsignal("dtx",  Pins("T19")),
        Subsignal("drx",  Pins("U19")),
        Subsignal("drx",  Pins("U19")),
        IOStandard("LVCMOS33")
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ( "J9", {
        1:  "N26",  2: "P26",
        3:  "M25",  4: "M26",
        5:  "K25",  6: "K26",
        7:  "T23",  8: "T24",
        9:  "P24", 10: "R23",
        11: "N22", 12: "P23",
        13: "M24", 14: "N24",
        15: "L24", 16: "M22",
    })
]

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk200"
    default_clk_period = 1e9/200e6

    def __init__(self, toolchain="vivado"):
        Xilinx7SeriesPlatform.__init__(self, "xc7k70t-fbg676-1", _io, toolchain=toolchain)

    def create_programmer(self):
        return OpenOCD("openocd_xc7_ft2232.cfg", "bscan_spi_xc7a70t.bit")

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk200", loose=True), 1e9/200e6)
