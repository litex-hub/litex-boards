#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Fei Gao <feig@princeton.edu>
# Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform, VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk300", 0,
        Subsignal("p", Pins("G31"), IOStandard("DIFF_SSTL12")),
        Subsignal("n", Pins("F31"), IOStandard("DIFF_SSTL12")),
    ),
    ("clk250", 0,
        Subsignal("p", Pins("E12"), IOStandard("DIFF_SSTL12")),
        Subsignal("n", Pins("D12"), IOStandard("DIFF_SSTL12")),
    ),
    ("clk250", 1,
        Subsignal("p", Pins("AW26"), IOStandard("DIFF_SSTL12")),
        Subsignal("n", Pins("AW27"), IOStandard("DIFF_SSTL12")),
    ),
    ("clk125", 0,
        Subsignal("p", Pins("AY24"), IOStandard("LVDS")),
        Subsignal("n", Pins("AY23"), IOStandard("LVDS")),
    ),
    ("clk156", 0,
        Subsignal("p", Pins("H32"), IOStandard("DIFF_SSTL12")),
        Subsignal("n", Pins("G32"), IOStandard("DIFF_SSTL12")),
    ),
    ("cpu_reset", 0, Pins("L19"), IOStandard("LVCMOS12")),

    # Leds
    ("user_led", 0, Pins("AT32"), IOStandard("LVCMOS12")),
    ("user_led", 1, Pins("AV34"), IOStandard("LVCMOS12")),
    ("user_led", 2, Pins("AY30"), IOStandard("LVCMOS12")),
    ("user_led", 3, Pins("BB32"), IOStandard("LVCMOS12")),
    ("user_led", 4, Pins("BF32"), IOStandard("LVCMOS12")),
    ("user_led", 5, Pins("AU37"), IOStandard("LVCMOS12")),
    ("user_led", 6, Pins("AV36"), IOStandard("LVCMOS12")),
    ("user_led", 7, Pins("BA37"), IOStandard("LVCMOS12")),

    # Switches
    ("user_dip_btn", 0, Pins("B17"), IOStandard("LVCMOS12")),
    ("user_dip_btn", 1, Pins("G16"), IOStandard("LVCMOS12")),
    ("user_dip_btn", 2, Pins("J16"), IOStandard("LVCMOS12")),
    ("user_dip_btn", 3, Pins("D21"), IOStandard("LVCMOS12")),

    # Buttons
    ("user_btn_c", 0, Pins("BD23"), IOStandard("LVCMOS18")),
    ("user_btn_n", 0, Pins("BB24"), IOStandard("LVCMOS18")),
    ("user_btn_e", 0, Pins("BE23"), IOStandard("LVCMOS18")),
    ("user_btn_s", 0, Pins("BE22"), IOStandard("LVCMOS18")),
    ("user_btn_w", 0, Pins("BF22"), IOStandard("LVCMOS18")),

    # I2C
    ("i2c", 0,
        Subsignal("scl", Pins("AM24"), IOStandard("LVCMOS18")),
        Subsignal("sda", Pins("AL24"), IOStandard("LVCMOS18")),
    ),
    ("i2c_mux_reset_n", 0, Pins("AL25"), IOStandard("LVCMOS18")),

    # Serial
    ("serial", 0,
        Subsignal("rx",  Pins("AW25"), IOStandard("LVCMOS18")),
        Subsignal("rts", Pins("BB22"), IOStandard("LVCMOS18")),
        Subsignal("tx",  Pins("BB21"), IOStandard("LVCMOS18")),
        Subsignal("cts", Pins("AY25"), IOStandard("LVCMOS18")),
    ),

    # DDR4 memory channel C1. Only use the first 64 data bits
    ("ddram", 0,
        Subsignal("a", Pins(
            "D14 B15 B16 C14 C15 A13 A14 A15",
            "A16 B12 C12 B13 C13 D15"),
            IOStandard("SSTL12_DCI")),
        Subsignal("ba",        Pins("G15 G13"), IOStandard("SSTL12_DCI")),
        Subsignal("bg",        Pins("H13"), IOStandard("SSTL12_DCI")),
        Subsignal("ras_n",     Pins("F15"), IOStandard("SSTL12_DCI")), # A16
        Subsignal("cas_n",     Pins("H15"), IOStandard("SSTL12_DCI")), # A15
        Subsignal("we_n",      Pins("H14"), IOStandard("SSTL12_DCI")), # A14
        Subsignal("cs_n",      Pins("F13"), IOStandard("SSTL12_DCI")),
        Subsignal("act_n",     Pins("E13"), IOStandard("SSTL12_DCI")),
        #Subsignal("ten",       Pins("A20"), IOStandard("SSTL12_DCI")),
        #Subsignal("alert_n",   Pins("R17"), IOStandard("SSTL12_DCI")),
        #Subsignal("par",       Pins("G10"), IOStandard("SSTL12_DCI")),
        Subsignal("dm",        Pins(
            "G11 R18 K17 G18 B18 P20 L23 G22"),
            IOStandard("POD12_DCI")),
        Subsignal("dq",        Pins(
            "F11 E11 F10  F9 H12 G12  E9  D9",
            "R19 P19 M18 M17 N19 N18 N17 M16",
            "L16 K16 L18 K18 J17 H17 H19 H18",
            "F19 F18 E19 E18 G20 F20 E17 D16",
            "D17 C17 C19 C18 D20 D19 C20 B20",
            "N23 M23 R21 P21 R22 P22 T23 R23",
            "K24 J24 M21 L21 K21 J21 K22 J22",
            "H23 H22 E23 E22 F21 E21 F24 F23"),
            IOStandard("POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_p",   Pins("D11 P17 K19 F16 A19 N22 M20 H24"),
		    IOStandard("DIFF_POD12"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_n",   Pins("D10 P16 J19 E16 A18 M22 L20 G23"),
		    IOStandard("DIFF_POD12"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("clk_p",   Pins("F14"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("clk_n",   Pins("E14"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("cke",     Pins("A10"), IOStandard("SSTL12_DCI")),
        Subsignal("odt",     Pins("C8"), IOStandard("SSTL12_DCI")),
        Subsignal("reset_n", Pins("N20"), IOStandard("LVCMOS12")),
        Misc("SLEW=FAST"),
    ),

    # DDR4 memory channel C2.
    ("ddram", 1,
        Subsignal("a", Pins(
            "AM27 AL27 AP26 AP25 AN28 AM28 AP28 AP27",
            "AN26 AM26 AR28 AR27 AV25 AT25"),
            IOStandard("SSTL12_DCI")),
        Subsignal("ba",      Pins("AR25 AU28"), IOStandard("SSTL12_DCI")),
        Subsignal("bg",      Pins("AU27"), IOStandard("SSTL12_DCI")),
        Subsignal("ras_n",   Pins("AV26"), IOStandard("SSTL12_DCI")), # A16
        Subsignal("cas_n",   Pins("AU26"), IOStandard("SSTL12_DCI")), # A15
        Subsignal("we_n",    Pins("AV28"), IOStandard("SSTL12_DCI")), # A14
        Subsignal("cs_n",    Pins("AY29"), IOStandard("SSTL12_DCI")),
        Subsignal("act_n",   Pins("AN25"), IOStandard("SSTL12_DCI")),
        #Subsignal("ten",     Pins("AY35"), IOStandard("SSTL12_DCI")),
        #Subsignal("alert_n", Pins("AR29"), IOStandard("SSTL12_DCI")),
        #Subsignal("par",     Pins("BF29"), IOStandard("SSTL12_DCI")),
        Subsignal("dm",      Pins(
            "BE32 BB31 AV33 AR32 BC34 BE40 AY37 AV35 BE29 BA29"),
            IOStandard("POD12_DCI")),
        Subsignal("dq",      Pins(
            "BD30 BE30 BD32 BE33 BC33 BD33 BC31 BD31",
            "BA32 BB33 BA30 BA31 AW31 AW32 AY32 AY33",
            "AV30 AW30 AU33 AU34 AT31 AU32 AU31 AV31",
            "AR33 AT34 AT29 AT30 AP30 AR30 AN30 AN31",
            "BE34 BF34 BC35 BC36 BD36 BE37 BF36 BF37",
            "BD37 BE38 BC39 BD40 BB38 BB39 BC38 BD38",
            "BB36 BB37 BA39 BA40 AW40 AY40 AY38 AY39",
            "AW35 AW36 AU40 AV40 AU38 AU39 AV38 AV39",
            "BF26 BF27 BD28 BE28 BD27 BE27 BD25 BD26",
            "BC25 BC26 BB28 BC28 AY27 AY28 BA27 BB27"),
            IOStandard("POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_p",   Pins(
            "BF30 AY34 AU29 AP31 BE35 BE39 BA35 AW37 BE25 BA26"),
            IOStandard("DIFF_POD12"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_n",   Pins(
            "BF31 BA34 AV29 AP32 BF35 BF39 BA36 AW38 BF25 BB26"),
            IOStandard("DIFF_POD12"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("clk_p",   Pins("AT26"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("clk_n",   Pins("AT27"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("cke",     Pins("AW28"), IOStandard("SSTL12_DCI")),
        Subsignal("odt",     Pins("BB29"), IOStandard("SSTL12_DCI")),
        Subsignal("reset_n", Pins("BD35"), IOStandard("LVCMOS12")),
        Misc("SLEW=FAST"),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = []

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "clk125"
    default_clk_period = 1e9/125e6

    def __init__(self, toolchain="vivado"):
        XilinxPlatform.__init__(self, "xcvu9p-flga2104-2-e", _io, _connectors, toolchain="vivado")

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk300",    loose=True), 1e9/300e6)
        self.add_period_constraint(self.lookup_request("clk250", 0, loose=True), 1e9/250e6)
        self.add_period_constraint(self.lookup_request("clk250", 1, loose=True), 1e9/250e6)
        self.add_period_constraint(self.lookup_request("clk125",    loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("clk156",    loose=True), 1e9/156e6)
        # DDR4 memory channel C1 Internal Vref
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 71]")
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 72]")
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 73]")
        # DDR4 memory channel C2 Internal Vref
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 40]")
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 41]")
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 42]")
