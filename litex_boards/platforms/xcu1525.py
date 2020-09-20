#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 David Shah <dave@ds0.me>
# Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import Pins, Subsignal, IOStandard, Misc
from litex.build.xilinx import XilinxPlatform, VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # clk
    ("clk300", 0,
        Subsignal("n", Pins("AY38"), IOStandard("DIFF_SSTL12")),
        Subsignal("p", Pins("AY37"), IOStandard("DIFF_SSTL12")),
    ),

    # led
    ("user_led", 0, Pins("BC21"), IOStandard("LVCMOS12")),
    ("user_led", 1, Pins("BB21"), IOStandard("LVCMOS12")),
    ("user_led", 2, Pins("BA20"), IOStandard("LVCMOS12")),

    # serial
    ("serial", 0,
        Subsignal("rx", Pins("BF18"), IOStandard("LVCMOS12")),
        Subsignal("tx", Pins("BB20"), IOStandard("LVCMOS12")),
    ),

    # pcie
    ("pcie_x2", 0,
        Subsignal("rst_n", Pins("BD21"), IOStandard("LVCMOS12")),
        Subsignal("clk_n", Pins("AM10")),
        Subsignal("clk_p", Pins("AM11")),
        Subsignal("rx_n",  Pins("AF1 AG3")),
        Subsignal("rx_p",  Pins("AF2 AG4")),
        Subsignal("tx_n",  Pins("AF6 AG8")),
        Subsignal("tx_p",  Pins("AF7 AG9")),
    ),

    ("pcie_x4", 0,
        Subsignal("rst_n", Pins("BD21"), IOStandard("LVCMOS12")),
        Subsignal("clk_n", Pins("AM10")),
        Subsignal("clk_p", Pins("AM11")),
        Subsignal("rx_n",  Pins("AF1 AG3 AH1 AJ3")),
        Subsignal("rx_p",  Pins("AF2 AG4 AH2 AJ4")),
        Subsignal("tx_n",  Pins("AF6 AG8 AH6 AJ8")),
        Subsignal("tx_p",  Pins("AF7 AG9 AH7 AJ9")),
    ),

    ("pcie_x8", 0,
        Subsignal("rst_n", Pins("BD21"), IOStandard("LVCMOS12")),
        Subsignal("clk_n", Pins("AM10")),
        Subsignal("clk_p", Pins("AM11")),
        Subsignal("rx_n",  Pins("AF1 AG3 AH1 AJ3 AK1 AL3 AM1 AN3")),
        Subsignal("rx_p",  Pins("AF2 AG4 AH2 AJ4 AK2 AL4 AM2 AN4")),
        Subsignal("tx_n",  Pins("AF6 AG8 AH6 AJ8 AK6 AL8 AM6 AN8")),
        Subsignal("tx_p",  Pins("AF7 AG9 AH7 AJ9 AK7 AL9 AM7 AN9")),
    ),

    ("pcie_x16", 0,
        Subsignal("rst_n", Pins("BD21"), IOStandard("LVCMOS12")),
        Subsignal("clk_n", Pins("AM10")),
        Subsignal("clk_p", Pins("AM11")),
        Subsignal("rx_n", Pins("AF1 AG3 AH1 AJ3 AK1 AL3 AM1 AN3 AP1 AR3 AT1 AU3 AV1 AW3 BA1 BC1")),
        Subsignal("rx_p", Pins("AF2 AG4 AH2 AJ4 AK2 AL4 AM2 AN4 AP2 AR4 AT2 AU4 AV2 AW4 BA2 BC2")),
        Subsignal("tx_n", Pins("AF6 AG8 AH6 AJ8 AK6 AL8 AM6 AN8 AP6 AR8 AT6 AU8 AV6 BB4 BD4 BF4")),
        Subsignal("tx_p", Pins("AF7 AG9 AH7 AJ9 AK7 AL9 AM7 AN9 AP7 AR9 AT7 AU9 AV7 BB5 BD5 BF5")),
    ),

    # ddram
    ("ddram", 0,
        Subsignal("a", Pins(
            "AT36 AV36 AV37 AW35 AW36 AY36 AY35 BA40",
            "BA37 BB37 AR35 BA39 BB40 AN36"),
            IOStandard("SSTL12_DCI")),
        Subsignal("act_n", Pins("BB39"), IOStandard("SSTL12_DCI")),
        Subsignal("ba",    Pins("AT35 AT34"), IOStandard("SSTL12_DCI")),
        Subsignal("bg",    Pins("BC37 BC39"), IOStandard("SSTL12_DCI")),
        Subsignal("ras_n", Pins("AR36"), IOStandard("SSTL12_DCI")), # A16
        Subsignal("cas_n", Pins("AP36"), IOStandard("SSTL12_DCI")), # A15
        Subsignal("we_n",  Pins("AP35"), IOStandard("SSTL12_DCI")), # A14
        Subsignal("cke",   Pins("BC38"), IOStandard("SSTL12_DCI")),
        Subsignal("clk_n", Pins("AW38"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("clk_p", Pins("AV38"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("cs_n",  Pins("AR33"), IOStandard("SSTL12_DCI")),
        Subsignal("dm",    Pins("BC31 AY27 BB26 BD26 AP30 BF39 AR30 BA32"),
            IOStandard("POD12_DCI")),
        Subsignal("dq", Pins(
            "BB31 BB32 AY33 AY32 BC33 BC32 BB34 BC34",
            "AT28 AT27 AU27 AV27 AV28 AV29 AW30 AY30",
            "BA28 BA27 AW28 AW29 BC27 BB27 BA29 BB29",
            "BE28 BF28 BE30 BD30 BF27 BE27 BF29 BF30",
            "AT32 AU32 AM30 AL30 AR31 AN31 AR32 AN32",
            "BD40 BD39 BF42 BF43 BF41 BE40 BE37 BF37",
            "AM27 AN27 AP28 AP29 AM29 AN29 AR28 AR27",
            "AW34 AV32 AV31 AV34 BA35 BA34 AW31 AY31"),
            IOStandard("POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_n", Pins("BB36 AU30 BB30 BD29 AM32 BF38 AL29 AW33"),
            IOStandard("DIFF_POD12"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_p", Pins("BB35 AU2 BA30 BD28 AM31 BE38 AL28 AV33"),
            IOStandard("DIFF_POD12"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("odt",     Pins("AP34"), IOStandard("SSTL12_DCI")),
        Subsignal("reset_n", Pins("AU31"), IOStandard("LVCMOS12")),
        Misc("SLEW=FAST")
    ),
    ("ddram", 1,
        Subsignal("a", Pins(
            "AN24 AT24 AW24 AN26 AY22 AY23 AV24 BA22",
            "AY25 BA23 AM26 BA25 BB22 AL24"),
            IOStandard("SSTL12_DCI")),
        Subsignal("act_n", Pins("AW25"), IOStandard("SSTL12_DCI")),
        Subsignal("ba",    Pins("AU24 AP26"), IOStandard("SSTL12_DCI")),
        Subsignal("bg",    Pins("BC22 AW26"), IOStandard("SSTL12_DCI")),
        Subsignal("ras_n", Pins("AN23"), IOStandard("SSTL12_DCI")), # A16
        Subsignal("cas_n", Pins("AM25"), IOStandard("SSTL12_DCI")), # A15
        Subsignal("we_n",  Pins("AL25"), IOStandard("SSTL12_DCI")), # A14
        Subsignal("cke",   Pins("BB25"), IOStandard("SSTL12_DCI")),
        Subsignal("clk_n", Pins("AU25"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("clk_p", Pins("AT25"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("cs_n",  Pins("AV23"), IOStandard("SSTL12_DCI")),
        Subsignal("dm",    Pins("BE8 AY13 BA10 AN14 BE15 BB14 AW16 AM17"),
            IOStandard("POD12_DCI")),
        Subsignal("dq", Pins(
            " BD9  BD7  BC7  BD8 BD10 BE10  BE7  BF7",
            "AU13 AV13 AW13 AW14 AU14 AY11 AV14 BA11",
            "BA12 BB12 BA13 BA14  BC9  BB9  BA7  BA8",
            "AN13 AR13 AM13 AP13 AM14 AR15 AL14 AT15",
            "BE13 BD14 BF12 BD13 BD15 BD16 BF14 BF13",
            "AY17 BA17 AY18 BA18 BA15 BB15 BC11 BD11",
            "AV16 AV17 AU16 AU17 BB17 BB16 AT18 AT17",
            "AM15 AL15 AN17 AN16 AR18 AP18 AL17 AL16"),
            IOStandard("POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_n", Pins("BF9 AY15 BB10 AT13 BE11 BC12 AW18 AR16"),
            IOStandard("DIFF_POD12"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_p", Pins("BF10 AW15 BB11 AT14 BE12 BC13 AV18 AP16"),
            IOStandard("DIFF_POD12"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("odt",     Pins("AW23"), IOStandard("SSTL12_DCI")),
        Subsignal("reset_n", Pins("AR17"), IOStandard("LVCMOS12")),
        Misc("SLEW=FAST")
    ),
    ("ddram", 2,
        Subsignal("a", Pins(
            "L29 A33 C33 J29 H31 G31 C32 B32",
            "A32 D31 A34 E31 M30 F33"),
            IOStandard("SSTL12_DCI")),
        Subsignal("act_n", Pins("B31"), IOStandard("SSTL12_DCI")),
        Subsignal("ba",    Pins("D33 B36"), IOStandard("SSTL12_DCI")),
        Subsignal("bg",    Pins("C31 J30"), IOStandard("SSTL12_DCI")),
        Subsignal("ras_n", Pins("K30"), IOStandard("SSTL12_DCI")), # A16
        Subsignal("cas_n", Pins("G32"), IOStandard("SSTL12_DCI")), # A15
        Subsignal("we_n",  Pins("A35"), IOStandard("SSTL12_DCI")), # A14
        Subsignal("cke",   Pins("G30"), IOStandard("SSTL12_DCI")),
        Subsignal("clk_n", Pins("B34"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("clk_p", Pins("C34"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("cs_n",  Pins("B35"), IOStandard("SSTL12_DCI")),
        Subsignal("dm",    Pins("R28 M27 H26 C29 G37 T30 M34 H33"),
            IOStandard("POD12_DCI")),
        Subsignal("dq", Pins(
            "R25 P25 M25 L25 P26 R26 N27 N28",
            "J28 H29 H28 G29 K25 L27 K26 K27",
            "F27 E27 E28 D28 G27 G26 F28 F29",
            "D26 C26 B27 B26 A29 A30 C27 C28",
            "F35 E38 D38 E35 E36 E37 F38 G38",
            "P30 R30 P29 N29 L32 M32 P31 N32",
            "J35 K35 L33 K33 J34 J33 N34 P34",
            "H36 G36 H37 J36 K37 K38 G35 G34"),
            IOStandard("POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_n", Pins("M26 J26 D30 A28 E40 M31 L36 H38"),
            IOStandard("DIFF_POD12"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_p", Pins("N26 J25 D29 A27 E39 N31 L35 J38"),
            IOStandard("DIFF_POD12"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("odt",     Pins("E33"), IOStandard("SSTL12_DCI")),
        Subsignal("reset_n", Pins("D36"), IOStandard("LVCMOS12")),
        Misc("SLEW=FAST")
    ),
    ("ddram", 4,
        Subsignal("a", Pins(
            "K15 B15 F14 A15 C14 A14 B14 E13",
            "F13 A13 D14 C13 B13 K16"),
            IOStandard("SSTL12_DCI")),
        Subsignal("act_n", Pins("H13"), IOStandard("SSTL12_DCI")),
        Subsignal("ba",    Pins("J15 H14"), IOStandard("SSTL12_DCI")),
        Subsignal("bg",    Pins("D13 J13"), IOStandard("SSTL12_DCI")),
        Subsignal("ras_n", Pins("F15"), IOStandard("SSTL12_DCI")), # A16
        Subsignal("cas_n", Pins("E15"), IOStandard("SSTL12_DCI")), # A15
        Subsignal("cke",   Pins("K13"), IOStandard("SSTL12_DCI")), # A14
        Subsignal("we_n",  Pins("D15"), IOStandard("SSTL12_DCI")),
        Subsignal("clk_n", Pins("L13"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("clk_p", Pins("L14"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("cs_n",  Pins("B16"), IOStandard("SSTL12_DCI")),
        Subsignal("dm",    Pins("N22 M22 K18 N17 D24  B19 H19 H23"),
            IOStandard("POD12_DCI")),
        Subsignal("dq", Pins(
            "P24 N24 T24 R23 N23 P21 P23 R21",
            "J24 J23 H24 G24 L24 L23 K22 K21",
            "G20 H17 F19 G17 J20 L19 L18 J19",
            "M19 M20 R18 R17 R20 T20 N18 N19",
            "A23 A22 B24 B25 B22 C22 C24 C23",
            "C19 C18 C21 B21 A18 A17 A20 B20",
            "E17 F20 E18 E20 D19 D20 H18 J18",
            "F22 E22 G22 G21 F24 E25 F25 G25"),
            IOStandard("POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_n", Pins("R22 H21 K20 P18 A24 B17 F17 E23"),
            IOStandard("DIFF_POD12"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_p", Pins("T22 J21 L20 P19 A25 C17 F18 F23"),
            IOStandard("DIFF_POD12"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("odt",     Pins("C16"), IOStandard("SSTL12_DCI")),
        Subsignal("reset_n", Pins("D21"), IOStandard("LVCMOS12")),
        Misc("SLEW=FAST")
    ),
]

_connectors = []

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "clk300"
    default_clk_period = 1e9/300e6

    def __init__(self):
        XilinxPlatform.__init__(self, "xcvu9p-fsgd2104-2l-e", _io, _connectors, toolchain="vivado")

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk300", 0, loose=True), 1e9/300e6)
        # For passively cooled boards, overheating is a significant risk if airflow isn't sufficient
        self.add_platform_command("set_property BITSTREAM.CONFIG.OVERTEMPSHUTDOWN ENABLE [current_design]")
        # Reduce programming time
        self.add_platform_command("set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]")
        # DDR4 memory channel C0 Internal Vref
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 41]")
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 42]")
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 43]")
        # DDR4 memory channel C1 Internal Vref
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 65]")
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 66]")
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 67]")
        # DDR4 memory channel C2 Internal Vref
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 46]")
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 47]")
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 48]")
        # DDR4 memory channel C3 Internal Vref
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 70]")
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 71]")
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 72]")
