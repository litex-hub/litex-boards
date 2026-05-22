#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Andrew Elbert Wilson <Andrew.E.Wilson@ieee.org>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxUSPPlatform, VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("sys_clk100", 0,
        Subsignal("p", Pins("T24"), IOStandard("LVDS")),
        Subsignal("n", Pins("U24"), IOStandard("LVDS"))
    ),

    ("ddr_clk100", 0,
        Subsignal("p", Pins("AD20"), IOStandard("LVDS")),
        Subsignal("n", Pins("AE20"), IOStandard("LVDS"))
    ),
    #NO RESET, maybe use okHOST USB later
    #("cpu_reset", 0, Pins("AN8"), IOStandard("LVCMOS18")),

    # Leds
    ("user_led", 0, Pins("G19"), IOStandard("LVCMOS18")),
    ("user_led", 1, Pins("B16"), IOStandard("LVCMOS18")),
    ("user_led", 2, Pins("F22"), IOStandard("LVCMOS18")),
    ("user_led", 3, Pins("E22"), IOStandard("LVCMOS18")),
    ("user_led", 4, Pins("M24"), IOStandard("LVCMOS18")),
    ("user_led", 5, Pins("G22"), IOStandard("LVCMOS18")),

    # Opal Kelly Host USBC interface
    ("okHost", 0, # Uses the FrontPanel API
        Subsignal("okAA",  Pins("T19")),
        Subsignal("okHU",  Pins("U20 U26 T22")),
        Subsignal("okUH",  Pins("V23 T23 U22 U25 U21")),
        Subsignal("okUHU", Pins(
            "P26 P25 R26 R25 R23 R22 P21 P20",
            "R21 R20 P23 N23 T25 N24 N22 V26",
            "N19 V21 N21 W20 W26 W19 Y25 Y26",
            "Y22 V22 W21 AA23 Y23 AA24 W25 AA25")),
        IOStandard("LVCMOS18"),
        Misc("SLEW=FAST"),
    ),

    # MGT RefClk.
    ("mgt_refclk", 0,
        Subsignal("p", Pins("P7")),
        Subsignal("n", Pins("P6")),
    ),

    # SMA.
    ("user_sma_mgt_refclk", 0,
        Subsignal("p", Pins("M7")),
        Subsignal("n", Pins("M6")),
    ),
    ("user_sma_mgt_tx", 0,
        Subsignal("p", Pins("J5")),
        Subsignal("n", Pins("J4")),
    ),
    ("user_sma_mgt_rx", 0,
        Subsignal("p", Pins("H2")),
        Subsignal("n", Pins("H1")),
    ),

    # SFP+.
    ("sfp", 0,
        Subsignal("txp", Pins("N5")),
        Subsignal("txn", Pins("N4")),
        Subsignal("rxp", Pins("M2")),
        Subsignal("rxn", Pins("M1")),
    ),
    ("sfp_tx", 0,
        Subsignal("p", Pins("N5")),
        Subsignal("n", Pins("N4")),
    ),
    ("sfp_rx", 0,
        Subsignal("p", Pins("M2")),
        Subsignal("n", Pins("M1")),
    ),
    ("sfp", 1,
        Subsignal("txp", Pins("L5")),
        Subsignal("txn", Pins("L4")),
        Subsignal("rxp", Pins("K2")),
        Subsignal("rxn", Pins("K1")),
    ),
    ("sfp_tx", 1,
        Subsignal("p", Pins("L5")),
        Subsignal("n", Pins("L4")),
    ),
    ("sfp_rx", 1,
        Subsignal("p", Pins("K2")),
        Subsignal("n", Pins("K1")),
    ),
    ("sfp_tx_disable", 0, Pins("C13"), IOStandard("LVCMOS33")),
    ("sfp_tx_disable", 1, Pins("F13"), IOStandard("LVCMOS33")),
    ("sfp_tx_fault",   0, Pins("C14"), IOStandard("LVCMOS33")),
    ("sfp_tx_fault",   1, Pins("F14"), IOStandard("LVCMOS33")),
    ("sfp_los",        0, Pins("E13"), IOStandard("LVCMOS33")),
    ("sfp_los",        1, Pins("A13"), IOStandard("LVCMOS33")),
    ("sfp_mod_def0",   0, Pins("D14"), IOStandard("LVCMOS33")),
    ("sfp_mod_def0",   1, Pins("A14"), IOStandard("LVCMOS33")),
    ("sfp_i2c", 0,
        Subsignal("scl", Pins("C12")),
        Subsignal("sda", Pins("B12")),
        IOStandard("LVCMOS33"),
    ),
    ("sfp_i2c", 1,
        Subsignal("scl", Pins("G12")),
        Subsignal("sda", Pins("F12")),
        IOStandard("LVCMOS33"),
    ),
    ("sfp_rate_select", 0,
        Subsignal("rs0", Pins("D13")),
        Subsignal("rs1", Pins("E12")),
        IOStandard("LVCMOS33"),
    ),
    ("sfp_rate_select", 1,
        Subsignal("rs0", Pins("B14")),
        Subsignal("rs1", Pins("A12")),
        IOStandard("LVCMOS33"),
    ),

    # DDR4 SDRAM
    ("ddram", 0,
        Subsignal("a", Pins(
            "AD18 AE17 AB17 AE18 AD19 AF17 Y17 AE16",
            "AA17 AC17 AC19 AC16 AF20 AD16"),
            IOStandard("SSTL12_DCI")),
        Subsignal("ba",      Pins("AC18 AF18"), IOStandard("SSTL12_DCI")),
        Subsignal("bg",      Pins("AB19"), IOStandard("SSTL12_DCI")),
        Subsignal("ras_n",   Pins("AA18"), IOStandard("SSTL12_DCI")),
        Subsignal("cas_n",   Pins("AF19"), IOStandard("SSTL12_DCI")),
        Subsignal("we_n",    Pins("AA19"), IOStandard("SSTL12_DCI")),
        Subsignal("cs_n",    Pins("AF22"), IOStandard("SSTL12_DCI")),
        Subsignal("act_n",   Pins("Y18"), IOStandard("SSTL12_DCI")),
        Subsignal("dm",      Pins("AE25 AE22"),
            IOStandard("POD12_DCI")),
        Subsignal("dq",      Pins(
            "AF24 AB25 AB26 AC24 AF25 AB24 AD24 AD25",
            "AB21 AE21 AE23 AD23 AC23 AD21 AC22 AC21"),
            IOStandard("POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_p",   Pins("AC26 AA22"),
            IOStandard("DIFF_POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_n",   Pins("AD26 AB22"),
            IOStandard("DIFF_POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("clk_p",   Pins("Y20"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("clk_n",   Pins("Y21"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("cke",     Pins("AA20"), IOStandard("SSTL12_DCI")),
        Subsignal("odt",     Pins("AB20"), IOStandard("SSTL12_DCI")),
        Subsignal("reset_n", Pins("AE26"), IOStandard("LVCMOS12")),
        Misc("SLEW=FAST"),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("SYZYGYA", {
        # Single ended
        "S0"  : "L18", "S1"  : "M25",
        "S2"  : "K18", "S3"  : "M26",
        "S4"  : "M20", "S5"  : "L24",
        "S6"  : "M21", "S7"  : "L25",
        "S8"  : "J19", "S9"  : "K25",
        "S10" : "J20", "S11" : "K26",
        "S12" : "L22", "S13" : "K22",
        "S14" : "L23", "S15" : "K23",
        "S16" : "H24", "S17" : "L19",
        "S18" : "J21", "S19" : "M19",
        "S20" : "H23", "S21" : "L20",
        "S22" : "K21", "S23" : "K20",
        "S24" : "F24", "S25" : "J26",
        "S26" : "F25", "S27" : "J25",
        # Differential
        "D0P" : "L18", "D1P" : "M25",
        "D0N" : "K18", "D1N" : "M26",
        "D2P" : "M20", "D3P" : "L24",
        "D2N" : "M21", "D3N" : "L25",
        "D4P" : "J19", "D5P" : "K25",
        "D4N" : "J20", "D5N" : "K26",
        "D6P" : "L22", "D7P" : "K22",
        "D6N" : "L23", "D7N" : "K23",
        # Clocks
        "P2C_CLKP" : "J23", "C2P_CLKP" : "H26",
        "P2C_CLKN" : "J24", "C2P_CLKN" : "G26",
    }),
    ("SYZYGYB", {
        # Single ended
        "S0"  : "A22", "S1"  : "A24",
        "S2"  : "A23", "S3"  : "A25",
        "S4"  : "E21", "S5"  : "D24",
        "S6"  : "D21", "S7"  : "D25",
        "S8"  : "E25", "S9"  : "C23",
        "S10" : "E26", "S11" : "B24",
        "S12" : "F23", "S13" : "C21",
        "S14" : "E23", "S15" : "B21",
        "S16" : "D26", "S17" : "C26",
        "S18" : "B26", "S19" : "B25",
        "S20" : "D23", "S21" : "C24",
        "S22" : "B20", "S23" : "C22",
        "S24" : "B22", "S25" : "A20",
        "S26" : "D20", "S27" : "G21",
        # Differential
        "D0P" : "A22", "D1P" : "A24",
        "D0N" : "A23", "D1N" : "A25",
        "D2P" : "E21", "D3P" : "D24",
        "D2N" : "D21", "D3N" : "D25",
        "D4P" : "E25", "D5P" : "C23",
        "D4N" : "E26", "D5N" : "B24",
        "D6P" : "F23", "D7P" : "C21",
        "D6N" : "E23", "D7N" : "B21",
        # Clocks
        "P2C_CLKP" : "G24", "C2P_CLKP" : "H21",
        "P2C_CLKN" : "G25", "C2P_CLKN" : "H22",
    }),
    ("SYZYGYC", {
        # Single ended
        "S0"  : "F20", "S1"  : "C18",
        "S2"  : "E20", "S3"  : "C19",
        "S4"  : "H18", "S5"  : "H17",
        "S6"  : "H19", "S7"  : "G17",
        "S8"  : "F18", "S9"  : "A17",
        "S10" : "F19", "S11" : "A18",
        "S12" : "E16", "S13" : "B15",
        "S14" : "E17", "S15" : "A15",
        "S16" : "A19", "S17" : "B19",
        "S18" : "H16", "S19" : "D16",
        "S20" : "D19", "S21" : "E15",
        "S22" : "G20", "S23" : "C16",
        "S24" : "G16", "S25" : "F15",
        "S26" : "G15", "S27" : "D15",
        # Differential
        "D0P" : "F20", "D1P" : "C18",
        "D0N" : "E20", "D1N" : "C19",
        "D2P" : "H18", "D3P" : "H17",
        "D2N" : "H19", "D3N" : "G17",
        "D4P" : "F18", "D5P" : "A17",
        "D4N" : "F19", "D5N" : "A18",
        "D6P" : "E16", "D7P" : "B15",
        "D6N" : "E17", "D7N" : "A15",
        # Clocks
        "P2C_CLKP" : "E18", "C2P_CLKP" : "C17",
        "P2C_CLKN" : "D18", "C2P_CLKN" : "B17",
    }),
    ("SYZYGYD", {
        # Single ended
        "S0"  : "J12",  "S1"  : "W12",
        "S2"  : "H12",  "S3"  : "W13",
        "S4"  : "Y13",  "S5"  : "H14",
        "S6"  : "AA13", "S7"  : "G14",
        "S8"  : "J13",  "S9"  : "AF14",
        "S10" : "H13",  "S11" : "AF15",
        "S12" : "AE13", "S13" : "AC13",
        "S14" : "AF13", "S15" : "AC14",
        "S16" : "J14",  "S17" : "J15",
        "S18" : "W14",  "S19" : "Y15",
        "S20" : "AB16", "S21" : "W15",
        "S22" : "AB15", "S23" : "AE15",
        "S24" : "AA15", "S25" : "AD15",
        "S26" : "Y16",  "S27" : "W16",
        # Differential
        "D0P" : "J12",  "D1P" : "W12",
        "D0N" : "H12",  "D1N" : "W13",
        "D2P" : "Y13",  "D3P" : "H14",
        "D2N" : "AA13", "D3N" : "G14",
        "D4P" : "J13",  "D5P" : "AF14",
        "D4N" : "H13",  "D5N" : "AF15",
        "D6P" : "AE13", "D7P" : "AC13",
        "D6N" : "AF13", "D7N" : "AC14",
        # Clocks
        "P2C_CLKP" : "AA14", "C2P_CLKP" : "AD13",
        "P2C_CLKN" : "AB14", "C2P_CLKN" : "AD14",
    }),
    ("SYZYGYE", {
        # Gigabit Transceivers
        "RX0P" : "AF2", "TX0P" : "AF7",
        "RX0N" : "AF1", "TX0N" : "AF6",
        "RX1P" : "AE4", "TX1P" : "AE9",
        "RX1N" : "AE3", "TX1N" : "AE8",
        "RX2P" : "AD2", "TX2P" : "AD7",
        "RX2N" : "AD1", "TX2N" : "AD6",
        "RX3P" : "AB2", "TX3P" : "AC5",
        "RX3N" : "AB1", "TX3N" : "AC4",
        "REFCLK0P" : "AB7",
        "REFCLK0N" : "AB6",
        # Single ended
        "S0" : "H9",  "S1" : "J9",
        "S2" : "J10", "S3" : "H11",
        "S4" : "K9",  "S5" : "G9",
        "S6" : "K10", "S7" : "G10",
        "S8" : "J11", "S9" : "G11",
        # Clocks
        "P2C_CLKP" : "E11", "C2P_CLKP" : "F10",
        "P2C_CLKN" : "E10", "C2P_CLKN" : "F9",
    }),
    ("SYZYGYF", {
        # Gigabit Transceivers
        "RX0P" : "Y2", "TX0P" : "AA5",
        "RX0N" : "Y1", "TX0N" : "AA4",
        "RX1P" : "V2", "TX1P" : "W5",
        "RX1N" : "V1", "TX1N" : "W4",
        "RX2P" : "T2", "TX2P" : "U5",
        "RX2N" : "T1", "TX2N" : "U4",
        "RX3P" : "P2", "TX3P" : "R5",
        "RX3N" : "P1", "TX3N" : "R4",
        "REFCLK0P" : "V7",
        "REFCLK0N" : "V6",
        # Single ended
        "S0" : "B9",  "S1" : "A10",
        "S2" : "B10", "S3" : "A9",
        "S4" : "D9",  "S5" : "C9",
        # Clocks
        "P2C_CLKP" : "D11", "C2P_CLKP" : "C11",
        "P2C_CLKN" : "D10", "C2P_CLKN" : "B11",
    }),
    ("pmod1", "AC14 AC13 AF15 AF14 AF13 AE13 H13  J13"),
    ("pmod2", "AB15 AB16 W14  J14  AE15 W15  Y15  J15"),
    ("pmod3", "G14  H14  W13  W12  AA13 Y13  H12  J12"),
    ("pmod4", "AD14 AD13 W16  AD15 AB14 AA14 Y16  AA15"),
]

def dvi_pmod_io(pmoda,pmodb):
    return [
        ("dvi", 0,
            Subsignal("clk",   Pins(f"{pmodb}:1")),
            Subsignal("de",    Pins(f"{pmodb}:6")),
            Subsignal("hsync", Pins(f"{pmodb}:3")),
            Subsignal("vsync", Pins(f"{pmodb}:7")),
            Subsignal("b",     Pins(f"{pmoda}:5 {pmoda}:1 {pmoda}:4 {pmoda}:0")),
            Subsignal("g",     Pins(f"{pmoda}:7 {pmoda}:3 {pmoda}:6 {pmoda}:2")),
            Subsignal("r",     Pins(f"{pmodb}:2 {pmodb}:5 {pmodb}:4 {pmodb}:0")),
            IOStandard("LVCMOS33"),
        )
    ]

_dvi_pmod_io = dvi_pmod_io("pmod2","pmod1") # SDCARD PMOD on JD.

def sdcard_pmod_io(pmod):
    return [
        # SDCard PMOD:
        # - https://store.digilentinc.com/pmod-microsd-microsd-card-slot/
        # - https://github.com/antmicro/arty-expansion-board
        ("spisdcard", 0,
            Subsignal("clk",  Pins(f"{pmod}:3")),
            Subsignal("mosi", Pins(f"{pmod}:1"), Misc("PULLUP True")),
            Subsignal("cs_n", Pins(f"{pmod}:0"), Misc("PULLUP True")),
            Subsignal("miso", Pins(f"{pmod}:2"), Misc("PULLUP True")),
            Misc("SLEW=FAST"),
            IOStandard("LVCMOS33"),
        ),
        ("sdcard", 0,
            Subsignal("data", Pins(f"{pmod}:2 {pmod}:4 {pmod}:5 {pmod}:0"), Misc("PULLUP True")),
            Subsignal("cmd",  Pins(f"{pmod}:1"), Misc("PULLUP True")),
            Subsignal("clk",  Pins(f"{pmod}:3")),
            Subsignal("cd",   Pins(f"{pmod}:6")),
            Misc("SLEW=FAST"),
            IOStandard("LVCMOS33"),
        ),
]

_sdcard_pmod_io = sdcard_pmod_io("pmod3") # SDCARD PMOD on JD.

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxUSPPlatform):
    default_clk_name   = "sys_clk100"
    default_clk_period = 1e9/100e6

    def __init__(self, toolchain="vivado"):
        XilinxUSPPlatform.__init__(self, "xcau25p-ffvb676-2-e", _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment):
        XilinxUSPPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("sys_clk100", loose=True), 1e9/100e6)
        self.add_period_constraint(self.lookup_request("ddr_clk100", loose=True), 1e9/100e6)
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 64]")
