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
    # Clk / Rst
    ("clk300", 0,
        Subsignal("n", Pins("AY38"), IOStandard("DIFF_SSTL12")),
        Subsignal("p", Pins("AY37"), IOStandard("DIFF_SSTL12")),
    ),
    ("clk300", 1,
        Subsignal("n", Pins("AW19"), IOStandard("DIFF_SSTL12")),
        Subsignal("p", Pins("AW20"), IOStandard("DIFF_SSTL12")),
    ),
    ("clk300", 2,
        Subsignal("n", Pins("E32"), IOStandard("DIFF_SSTL12")),
        Subsignal("p", Pins("F32"), IOStandard("DIFF_SSTL12")),
    ),
    ("clk300", 3,
        Subsignal("n", Pins("H16"), IOStandard("DIFF_SSTL12")),
        Subsignal("p", Pins("J16"), IOStandard("DIFF_SSTL12")),
    ),

    # Leds
    ("user_led", 0, Pins("BC21"), IOStandard("LVCMOS12")),
    ("user_led", 1, Pins("BB21"), IOStandard("LVCMOS12")),
    ("user_led", 2, Pins("BA20"), IOStandard("LVCMOS12")),

    # Serial
    ("serial", 0,
        Subsignal("rx", Pins("BF18"), IOStandard("LVCMOS12")),
        Subsignal("tx", Pins("BB20"), IOStandard("LVCMOS12")),
    ),

    # PCIe
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

    # DDR4 SDRAM
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
            Misc("OUTPUT_IMPEDANCE=RDRV_40_40"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_n", Pins("BB36 AU30 BB30 BD29 AM32 BF38 AL29 AW33"),
            IOStandard("DIFF_POD12"),
            Misc("OUTPUT_IMPEDANCE=RDRV_40_40"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_p", Pins("BB35 AU29 BA30 BD28 AM31 BE38 AL28 AV33"),
            IOStandard("DIFF_POD12"),
            Misc("OUTPUT_IMPEDANCE=RDRV_40_40"),
            Misc("PRE_EMPHASIS=RDRV_240"),
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
        Subsignal("dm",    Pins("BE8 BE15 BE22 BA10 AY13 BB14 AN14 AW16"),
            IOStandard("POD12_DCI")),
        Subsignal("dq", Pins(
            " BC7  BD7  BD8  BD9  BF7  BE7 BD10 BE10",
            "BF12 BE13 BD14 BD13 BF14 BF13 BD16 BD15",
            "BF25 BE25 BF24 BD25 BC23 BD23 BF23 BE23",
            "BA14 BA13 BA12 BB12  BC9  BB9  BA7  BA8",
            "AU13 AW14 AW13 AV13 AU14 BA11 AY11 AV14",
            "BA18 BA17 AY18 AY17 BD11 BC11 BA15 BB15",
            "AR13 AP13 AN13 AM13 AT15 AR15 AM14 AL14",
            "AV16 AV17 AU17 AU16 BB17 BB16 AT17 AT18"),
            IOStandard("POD12_DCI"),
            Misc("OUTPUT_IMPEDANCE=RDRV_40_40"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_n", Pins("BF9 BE11 BD24 BB10 AY15 BC12 AT13 AW18"),
            IOStandard("DIFF_POD12"),
            Misc("OUTPUT_IMPEDANCE=RDRV_40_40"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_p", Pins("BF10 BE12 BC24 BB11 AW15 BC13 AT14 AV18"),
            IOStandard("DIFF_POD12"),
            Misc("OUTPUT_IMPEDANCE=RDRV_40_40"),
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
        Subsignal("dm",    Pins("T30 M27 R28 H26 C37 H33 G37 M34"),
            IOStandard("POD12_DCI")),
        Subsignal("dq", Pins(
            "P29 P30 R30 N29 N32 M32 P31 L32",
            "H29 G29 J28 H28 K27 L27 K26 K25",
            "P25 R25 L25 M25 P26 R26 N27 N28",
            "F27 D28 E27 E28 G26 F29 G27 F28",
            "A38 A37 B37 C36 B40 C39 A40 D39",
            "G36 H36 H37 J36 G34 G35 K37 K38",
            "E38 D38 E35 F35 E36 E37 F38 G38",
            "K35 J35 K33 L33 J33 J34 N34 P34"),
            IOStandard("POD12_DCI"),
            Misc("OUTPUT_IMPEDANCE=RDRV_40_40"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_n", Pins("M31 J26 M26 D30 A39 H38 E40 L36"),
            IOStandard("DIFF_POD12"),
            Misc("OUTPUT_IMPEDANCE=RDRV_40_40"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_p", Pins("N31 J25 N26 D29 B39 J38 E39 L35"),
            IOStandard("DIFF_POD12"),
            Misc("OUTPUT_IMPEDANCE=RDRV_40_40"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("odt",     Pins("E33"), IOStandard("SSTL12_DCI")),
        Subsignal("reset_n", Pins("D36"), IOStandard("LVCMOS12")),
        Misc("SLEW=FAST")
    ),

    ("ddram", 3,
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
        Subsignal("dm",    Pins("T13 N17 D24 B19 H19 H23 M22 N22"),
            IOStandard("POD12_DCI")),
        Subsignal("dq", Pins(
            "M16 N16 N14 N13 R15 T15 P13 P14",
            "R17 R18 M20 M19 N18 N19 R20 T20",
            "B24 A23 A22 B25 C24 C23 C22 B22",
            "C18 C19 C21 B21 A17 A18 B20 A20",
            "E18 E17 E20 F20 D19 H18 D20 J18",
            "G21 E22 G22 F22 G25 F24 E25 F25",
            "J24 G24 J23 H24 L23 K21 L24 K22",
            "P24 N24 R23 T24 N23 P21 P23 R21"),
            IOStandard("POD12_DCI"),
            Misc("OUTPUT_IMPEDANCE=RDRV_40_40"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_n", Pins("P15 P18 A24 B17 F17 E23 H21 R22"),
            IOStandard("DIFF_POD12"),
            Misc("OUTPUT_IMPEDANCE=RDRV_40_40"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_p", Pins("R16 P19 A25 C17 F18 F23 J21 T22"),
            IOStandard("DIFF_POD12"),
            Misc("OUTPUT_IMPEDANCE=RDRV_40_40"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("odt",     Pins("C16"), IOStandard("SSTL12_DCI")),
        Subsignal("reset_n", Pins("D21"), IOStandard("LVCMOS12")),
        Misc("SLEW=FAST")
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = []

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "clk300"
    default_clk_period = 1e9/300e6

    def __init__(self, toolchain="vivado"):
        XilinxPlatform.__init__(self, "xcvu9p-fsgd2104-2l-e", _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        # For passively cooled boards, overheating is a significant risk if airflow isn't sufficient
        self.add_platform_command("set_property BITSTREAM.CONFIG.OVERTEMPSHUTDOWN ENABLE [current_design]")
        # Reduce programming time
        self.add_platform_command("set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]")
        # DDR4 memory channel C0 Clock constraint / Internal Vref
        self.add_period_constraint(self.lookup_request("clk300", 0, loose=True), 1e9/300e6)
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 40]")
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 41]")
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 42]")
        # DDR4 memory channel C1 Clock constraint / Internal Vref
        self.add_period_constraint(self.lookup_request("clk300", 1, loose=True), 1e9/300e6)
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 65]")
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 66]")
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 67]")
        # DDR4 memory channel C2 Clock constraint / Internal Vref
        self.add_period_constraint(self.lookup_request("clk300", 2, loose=True), 1e9/300e6)
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 46]")
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 47]")
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 48]")
        # DDR4 memory channel C3 Clock constraint / Internal Vref
        self.add_period_constraint(self.lookup_request("clk300", 3, loose=True), 1e9/300e6)
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 70]")
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 71]")
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 72]")
