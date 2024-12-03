#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2024 Jiaxun Yang <jiaxun.yang@flygoat.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import Pins, Subsignal, IOStandard, Misc
from litex.build.xilinx import XilinxUSPPlatform, VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk
    ("clk100", 0,
        Subsignal("p", Pins("AY23"), IOStandard("DIFF_SSTL12")),
        Subsignal("n", Pins("BA23"), IOStandard("DIFF_SSTL12")),
    ),
    ("clk400", 0,
        Subsignal("p", Pins("AY22"), IOStandard("DIFF_SSTL12")),
        Subsignal("n", Pins("BA22"), IOStandard("DIFF_SSTL12")),
    ),

    # 400 MHz DDR REF
    ("ddram_refclk", 0,
        Subsignal("p", Pins("G25"), IOStandard("DIFF_SSTL12")),
        Subsignal("n", Pins("G24"), IOStandard("DIFF_SSTL12")),
    ),

    ("ddram_refclk", 1,
        Subsignal("p", Pins("J26"), IOStandard("DIFF_SSTL12")),
        Subsignal("n", Pins("H26"), IOStandard("DIFF_SSTL12")),
    ),

    ("ddram_refclk", 2,
        Subsignal("p", Pins("AE31"), IOStandard("DIFF_SSTL12")),
        Subsignal("n", Pins("AE32"), IOStandard("DIFF_SSTL12")),
    ),

    ("ddram_refclk", 3,
        Subsignal("p", Pins("AW14"), IOStandard("DIFF_SSTL12")),
        Subsignal("n", Pins("AW13"), IOStandard("DIFF_SSTL12")),
    ),

    # LEDs
    ("user_led", 0, Pins("BA20"), IOStandard("LVCMOS12")),
    ("user_led", 1, Pins("BB20"), IOStandard("LVCMOS12")),
    ("user_led", 2, Pins("BB21"), IOStandard("LVCMOS12")),
    ("user_led", 3, Pins("BC21"), IOStandard("LVCMOS12")),
    ("user_led", 4, Pins("BB22"), IOStandard("LVCMOS12")),
    ("user_led", 5, Pins("BC22"), IOStandard("LVCMOS12")),
    ("user_led", 6, Pins("BA24"), IOStandard("LVCMOS12")),
    ("user_led", 7, Pins("BB24"), IOStandard("LVCMOS12")),

    # LED for Running
    ("run_led", 0, Pins("BD20"), IOStandard("LVCMOS12")),

    # Switches
    ("user_sw", 0, Pins("AE12"), IOStandard("LVCMOS12")),
    ("user_sw", 1, Pins("BC23"), IOStandard("LVCMOS12")),
    ("user_sw", 2, Pins("AR21"), IOStandard("LVCMOS12")),

    # PCIe
    ("pcie_x16", 0,
        Subsignal("rst_n", Pins("AR26"), IOStandard("LVCMOS12")),
        Subsignal("clk_n", Pins("AK10")),
        Subsignal("clk_p", Pins("AK11")),
        Subsignal("rx_n", Pins(
            "AF1 AG3 AH1 AJ3 AK1 AL3 AM1 AN3",
            "AP1 AR3 AT1 AU3 AV1 AW3 BA1 BC1")),
        Subsignal("rx_p", Pins(
            "AF2 AG4 AH2 AJ4 AK2 AL4 AM2 AN4",
            "AP2 AR4 AT2 AU4 AV2 AW4 BA2 BC2")),
        Subsignal("tx_n", Pins(
            "AF6 AG8 AH6 AJ8 AK6 AL8 AM6 AN8",
            "AP6 AR8 AT6 AU8 AV6 BB4 BD4 BF4")),
        Subsignal("tx_p", Pins(
            "AF7 AG9 AH7 AJ9 AK7 AL9 AM7 AN9",
            "AP7 AR9 AT7 AU9 AV7 BB5 BD5 BF5")),
    ),

    # PCIe
    ("pcie_x8", 0,
        Subsignal("rst_n", Pins("AR26"), IOStandard("LVCMOS12")),
        Subsignal("clk_n", Pins("AK10")),
        Subsignal("clk_p", Pins("AK11")),
        Subsignal("rx_n", Pins(
            "AF1 AG3 AH1 AJ3 AK1 AL3 AM1 AN3")),
        Subsignal("rx_p", Pins(
            "AF2 AG4 AH2 AJ4 AK2 AL4 AM2 AN4")),
        Subsignal("tx_n", Pins(
            "AF6 AG8 AH6 AJ8 AK6 AL8 AM6 AN8")),
        Subsignal("tx_p", Pins(
            "AF7 AG9 AH7 AJ9 AK7 AL9 AM7 AN9")),
    ),

    # PCIe
    ("pcie_x4", 0,
        Subsignal("rst_n", Pins("AR26"), IOStandard("LVCMOS12")),
        Subsignal("clk_n", Pins("AK10")),
        Subsignal("clk_p", Pins("AK11")),
        Subsignal("rx_n", Pins(
            "AF1 AG3 AH1 AJ3")),
        Subsignal("rx_p", Pins(
            "AF2 AG4 AH2 AJ4")),
        Subsignal("tx_n", Pins(
            "AF6 AG8 AH6 AJ8")),
        Subsignal("tx_p", Pins(
            "AF7 AG9 AH7 AJ9")),
    ),

    # QSFP0 (Upper Port)
    ("qsfp_refclk", 0, # 161.1328125 MHz
        Subsignal("p", Pins("D11")),
        Subsignal("n", Pins("D10")),
    ),
    ("qsfp", 0,
        Subsignal("txp", Pins("E9 D7 C9 A9")),
        Subsignal("txn", Pins("E8 D6 C8 A8")),
        Subsignal("rxp", Pins("E4 D2 C4 A5")),
        Subsignal("rxn", Pins("E3 D1 C3 A4")),
    ),
    ("qsfp_modprsl", 0, Pins("BC7"), IOStandard("LVCMOS12")),
    ("qsfp_intl", 0, Pins("BC8"), IOStandard("LVCMOS12")),
    ("qsfp_resetl", 0, Pins("BA7"), IOStandard("LVCMOS12"), Misc("PULLUP TRUE")),
    ("qsfp_lpmode", 0, Pins("BB9"), IOStandard("LVCMOS12"), Misc("PULLUP TRUE")),

    # Individual SFP breakouts
    ("qsfp0_sfp", 0,
        Subsignal("txp", Pins("E9")),
        Subsignal("txn", Pins("E8")),
        Subsignal("rxp", Pins("E4")),
        Subsignal("rxn", Pins("E3")),
    ),
    ("qsfp0_sfp", 1,
        Subsignal("txp", Pins("D7")),
        Subsignal("txn", Pins("D6")),
        Subsignal("rxp", Pins("D2")),
        Subsignal("rxn", Pins("D1")),
    ),
    ("qsfp0_sfp", 2,
        Subsignal("txp", Pins("C9")),
        Subsignal("txn", Pins("C8")),
        Subsignal("rxp", Pins("C4")),
        Subsignal("rxn", Pins("C3")),
    ),
    ("qsfp0_sfp", 3,
        Subsignal("txp", Pins("A9")),
        Subsignal("txn", Pins("A8")),
        Subsignal("rxp", Pins("A5")),
        Subsignal("rxn", Pins("A4")),
    ),

    # QSFP1 (Lower Port)
    ("qsfp_refclk", 1, # 161.1328125 MHz
        Subsignal("p", Pins("Y11")),
        Subsignal("n", Pins("Y10")),
    ),
    ("qsfp", 1,
        Subsignal("txp", Pins("AA9 Y7 W9 V7")),
        Subsignal("txn", Pins("AA8 Y6 W8 V6")),
        Subsignal("rxp", Pins("AA4 Y2 W4 V2")),
        Subsignal("rxn", Pins("AA3 Y1 W3 V1")),
    ),
    ("qsfp_modprsl", 1, Pins("BB11"), IOStandard("LVCMOS12")),
    ("qsfp_intl", 1, Pins("BC11"), IOStandard("LVCMOS12")),
    ("qsfp_resetl", 1, Pins("BB10"), IOStandard("LVCMOS12"), Misc("PULLUP TRUE")),
    ("qsfp_lpmode", 1, Pins("BB7"), IOStandard("LVCMOS12"), Misc("PULLUP TRUE")),

    # Individual SFP breakouts for QSFP1
    ("qsfp1_sfp", 0,
        Subsignal("txp", Pins("AA9")),
        Subsignal("txn", Pins("AA8")),
        Subsignal("rxp", Pins("AA4")),
        Subsignal("rxn", Pins("AA3")),
    ),
    ("qsfp1_sfp", 1,
        Subsignal("txp", Pins("Y7")),
        Subsignal("txn", Pins("Y6")),
        Subsignal("rxp", Pins("Y2")),
        Subsignal("rxn", Pins("Y1")),
    ),
    ("qsfp1_sfp", 2,
        Subsignal("txp", Pins("W9")),
        Subsignal("txn", Pins("W8")),
        Subsignal("rxp", Pins("W4")),
        Subsignal("rxn", Pins("W3")),
    ),
    ("qsfp1_sfp", 3,
        Subsignal("txp", Pins("V7")),
        Subsignal("txn", Pins("V6")),
        Subsignal("rxp", Pins("V2")),
        Subsignal("rxn", Pins("V1")),
    ),

    ("ddram", 0,
        Subsignal("a", Pins(
            "F23 K23 F24 H23 E23 L23 G22 L25",
            "H24 L24 F22 J24 K22 D24"),
            IOStandard("SSTL12_DCI")),
        Subsignal("ba",    Pins("D23 E25"), IOStandard("SSTL12_DCI")),
        Subsignal("bg",    Pins("D25"), IOStandard("SSTL12_DCI")),
        Subsignal("ras_n", Pins("L22"), IOStandard("SSTL12_DCI")),
        Subsignal("cas_n", Pins("J23"), IOStandard("SSTL12_DCI")),
        Subsignal("we_n",  Pins("E22"), IOStandard("SSTL12_DCI")),
        Subsignal("cs_n",  Pins("B22"), IOStandard("SSTL12_DCI")),
        Subsignal("act_n", Pins("A22"), IOStandard("SSTL12_DCI")),
        Subsignal("dm", Pins(
            "P13 L13 N17 L17 G14 D13 H19 D19", # 0-7
            "R21"), # 8
            IOStandard("POD12_DCI")),
        Subsignal("dq", Pins(
            "L14 P15 M14 P14 M16 R15 N16 N14",  # 0-7
            "J14 K15 H13 J13 J16 K16 J15 H14",  # 8-15
            "N21 N18 M20 M19 P20 P18 R20 M21",  # 16-23
            "J19 L18 J18 K18 J20 L19 K20 L20",  # 24-31
            "E15 F15 D15 E13 D16 G15 E16 F13",  # 32-39
            "B16 A14 A17 C14 C16 B14 B17 A13",  # 40-47
            "E20 F17 G20 F19 F20 G19 E21 F18",  # 48-55
            "C21 A19 B21 A20 D21 B19 B20 D20",  # 56-63
            "N22 P23 M22 P25 M24 R25 M25 N23"), # 64-71
            IOStandard("POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_p", Pins(
            "R16 H17 P19 J21 G17 B15 E18 D18", # 0-7
            "P24"), # 8
            IOStandard("DIFF_POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_n", Pins(
            "P16 H16 N19 H21 G16 A15 E17 C18", # 0-7
            "N24"), # 8
            IOStandard("DIFF_POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("clk_n", Pins("J25"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("clk_p", Pins("K25"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("cke",   Pins("C23"), IOStandard("SSTL12_DCI")),
        Subsignal("odt",     Pins("B26"), IOStandard("SSTL12_DCI")),
        Subsignal("reset_n", Pins("B24"), IOStandard("LVCMOS12")),
        Misc("SLEW=FAST"),
    ),

    ("ddram", 1,
        Subsignal("a", Pins(
            "G27 H28 H27 L28 F29 J28 F28 L27",
            "F27 K28 G29 G26 L29 M27"),
            IOStandard("SSTL12_DCI")),
        Subsignal("ba",    Pins("E27 E28"), IOStandard("SSTL12_DCI")),
        Subsignal("bg",    Pins("D28"), IOStandard("SSTL12_DCI")),
        Subsignal("ras_n", Pins("H29"), IOStandard("SSTL12_DCI")),
        Subsignal("cas_n", Pins("M29"), IOStandard("SSTL12_DCI")),
        Subsignal("we_n",  Pins("J29"), IOStandard("SSTL12_DCI")),
        Subsignal("cs_n",  Pins("B27"), IOStandard("SSTL12_DCI")),
        Subsignal("act_n", Pins("A28"), IOStandard("SSTL12_DCI")),
        Subsignal("dm", Pins(
            "E40 C36 M31 B34 H37 G30 U34 R30", # 0-7
            "T28"), # 8 
            IOStandard("POD12_DCI")),
        Subsignal("dq", Pins(
            "D39 C39 B40 A40 E38 D38 E39 C38",  # 0-7
            "E35 A35 D36 A38 E36 B35 D35 A37",  # 8-15
            "L32 K32 L33 K31 L30 J31 M30 K33",  # 16-23
            "C33 B32 C34 C32 D33 C31 D34 D31",  # 24-31
            "J36 G37 G34 F34 J35 F37 H34 F35",  # 32-39
            "H32 E32 G31 F32 H31 E33 G32 F33",  # 40-47
            "V31 U32 U31 T32 T30 T33 U30 R33",  # 48-55
            "R32 N32 N31 N34 R31 P31 N33 P34",  # 56-63
            "T27 R27 T26 R26 P28 N28 P26 N26"), # 64-71
            IOStandard("POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_p", Pins(
            "B39 B36 K30 A32 H36 J33 V32 M34", # 0-7
            "P29"), # 8
            IOStandard("DIFF_POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_n", Pins(
            "A39 B37 J30 A33 G36 H33 V33 L34", # 0-7
            "N29"), # 8
            IOStandard("DIFF_POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("clk_n", Pins("K27"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("clk_p", Pins("K26"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("cke",   Pins("C29"), IOStandard("SSTL12_DCI")),
        Subsignal("odt",     Pins("D30"), IOStandard("SSTL12_DCI")),
        Subsignal("reset_n", Pins("B29"), IOStandard("LVCMOS12")),
        Misc("SLEW=FAST"),
    ),

    ("ddram", 2,
        Subsignal("a", Pins(
            "AH33 AF34 AD33 AE33 AJ34 AD31 AG32 AF30",
            "AF32 AE30 AJ33 AC32 AF33 AC31"),
            IOStandard("SSTL12_DCI")),
        Subsignal("ba",    Pins("AC33 AC34"), IOStandard("SSTL12_DCI")),
        Subsignal("bg",    Pins("AD34"), IOStandard("SSTL12_DCI")),
        Subsignal("ras_n", Pins("AH34"), IOStandard("SSTL12_DCI")),
        Subsignal("cas_n", Pins("AG34"), IOStandard("SSTL12_DCI")),
        Subsignal("we_n",  Pins("AG31"), IOStandard("SSTL12_DCI")),
        Subsignal("cs_n",  Pins("AA33"), IOStandard("SSTL12_DCI")),
        Subsignal("act_n", Pins("Y31"), IOStandard("SSTL12_DCI")),
        Subsignal("dm", Pins(
            "AJ27 AT33 AW29 AP31 BF39 BC34 BA34 BC31", # 0-7
            "BF32"), # 8
            IOStandard("POD12_DCI")),
        Subsignal("dq", Pins(
            "AK31 AG29 AJ30 AJ31 AJ29 AJ28 AK28 AG30",  # 0-7
            "AP33 AM34 AP34 AL34 AR33 AM32 AN34 AL32",  # 8-15
            "AW31 AU31 AV31 AU32 AT29 AU30 AV32 AT30",  # 16-23
            "AP29 AN31 AR30 AM31 AN29 AL29 AP30 AL30",  # 24-31
            "BE38 BF38 BC38 BD39 BF37 BB38 BE37 BC39",  # 32-39
            "BE35 BB36 BE36 BA35 BD35 BB35 BD36 BC36",  # 40-47
            "AY35 AW34 AY36 AV34 AY33 AV33 BA33 AW33",  # 48-55
            "BB29 AY31 AY30 BB31 BA29 AY32 BA30 BB30",  # 56-63
            "BE30 BE31 BF30 BE32 BD29 BD33 BC29 BE33"), # 64-71
            IOStandard("POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_p", Pins(
            "AH28 AN32 AU29 AM29 BD40 BB37 AW35 BA32", # 0-7
            "BD30"), # 8
            IOStandard("DIFF_POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_n", Pins(
            "AH29 AN33 AV29 AM30 BE40 BC37 AW36 BB32", # 0-7
            "BD31"), # 8
            IOStandard("DIFF_POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("clk_n", Pins("AH32"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("clk_p", Pins("AH31"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("cke",   Pins("AB34"), IOStandard("SSTL12_DCI")),
        Subsignal("odt",     Pins("Y30"), IOStandard("SSTL12_DCI")),
        Subsignal("reset_n", Pins("Y32"), IOStandard("LVCMOS12")),
        Misc("SLEW=FAST"),
    ),

    ("ddram", 3,
        Subsignal("a", Pins(
            "AV14 BA14 AW16 AY11 AV13 BA15 AU14 AY13",
            "AU13 AY15 AY12 AT15 BA12 AW15"),
            IOStandard("SSTL12_DCI")),
        Subsignal("ba",    Pins("AU15 AU16"), IOStandard("SSTL12_DCI")),
        Subsignal("bg",    Pins("AV16"), IOStandard("SSTL12_DCI")),
        Subsignal("ras_n", Pins("BB12"), IOStandard("SSTL12_DCI")),
        Subsignal("cas_n", Pins("AY16"), IOStandard("SSTL12_DCI")),
        Subsignal("we_n",  Pins("BA13"), IOStandard("SSTL12_DCI")),
        Subsignal("cs_n",  Pins("AR15"), IOStandard("SSTL12_DCI")),
        Subsignal("act_n", Pins("AR13"), IOStandard("SSTL12_DCI")),
        Subsignal("dm", Pins(
            "BA25 AN18 BF28 AY17 BF14 AV26 AT19 BE17", # 0-7
            "AP25"), # 8
            IOStandard("POD12_DCI")),
        Subsignal("dq", Pins(
            "AY26 BB26 BA27 AY28 AW28 BB27 AY27 BA28",  # 0-7
            "AM16 AM19 AP19 AM20 AN16 AL20 AN19 AL19",  # 8-15
            "BE25 BE28 BF25 BF27 BC27 BD28 BC26 BE27",  # 16-23
            "AV18 AW18 AW19 AY18 AW20 BA18 AV19 AY20",  # 24-31
            "BC13 BF15 BD14 BE16 BC14 BD15 BE15 BD16",  # 32-39
            "AR28 AU27 AT27 AV27 AR27 AT28 AU26 AV28",  # 40-47
            "AR18 AT18 AU17 AR20 AP20 AU20 AP18 AT20",  # 48-55
            "BB19 BE19 BC17 BF18 BB17 BD18 BC18 BF19",  # 56-63
            "AL25 AP28 AN27 AM27 AM25 AL28 AN28 AL27"), # 64-71
            IOStandard("POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_p", Pins(
            "AW25 AL17 BD26 AV21 BD13 AR25 AR17 BC19", # 0-7
            "AM26"), # 8
            IOStandard("DIFF_POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_n", Pins(
            "AY25 AM17 BE26 AW21 BE13 AT25 AT17 BD19", # 0-7
            "AN26"), # 8
            IOStandard("DIFF_POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("clk_n", Pins("BB14"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("clk_p", Pins("BB15"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("cke",   Pins("AP14"), IOStandard("SSTL12_DCI")),
        Subsignal("odt",     Pins("AN13"), IOStandard("SSTL12_DCI")),
        Subsignal("reset_n", Pins("AL15"), IOStandard("LVCMOS12")),
        Misc("SLEW=FAST"),
    )
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = []

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxUSPPlatform):
    default_clk_name = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self, toolchain="vivado"):
        XilinxUSPPlatform.__init__(self, "xcvu13p-fhgb2104-2l-e", _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        return VivadoProgrammer(flash_part="mt25qu256-spi-x1_x2_x4_x8")

    def do_finalize(self, fragment):
        XilinxUSPPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100", loose=True), 1e9/100e6)
        self.add_period_constraint(self.lookup_request("clk400", loose=True), 1e9/400e6)
        self.add_period_constraint(self.lookup_request("ddram_refclk", 0, loose=True), 1e9/400e6)
        self.add_period_constraint(self.lookup_request("ddram_refclk", 1, loose=True), 1e9/400e6)
        self.add_period_constraint(self.lookup_request("ddram_refclk", 2, loose=True), 1e9/400e6)
        self.add_period_constraint(self.lookup_request("ddram_refclk", 3, loose=True), 1e9/400e6)
        self.add_period_constraint(self.lookup_request("qsfp_refclk", 0, loose=True), 1e9/161.1328125e6)
        self.add_period_constraint(self.lookup_request("qsfp_refclk", 1, loose=True), 1e9/161.1328125e6)

        # Reduce programming time
        self.add_platform_command("set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]")
        self.add_platform_command("set_property BITSTREAM.CONFIG.CONFIGRATE 85.0 [current_design]")
        self.add_platform_command("set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]")
        self.add_platform_command("set_property BITSTREAM.CONFIG.SPI_FALL_EDGE Yes [current_design]")
        
        # Configure voltage and CONFIG_VOLTAGE
        self.add_platform_command("set_property CFGBVS GND [current_design]")
        self.add_platform_command("set_property CONFIG_VOLTAGE 1.8 [current_design]")
