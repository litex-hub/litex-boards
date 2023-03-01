#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Antmicro <www.antmicro.com>
# Copyright (c) 2019 David Shah <dave@ds0.me>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxUSPPlatform, VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk125", 0,
        Subsignal("p", Pins("F23"), IOStandard("LVDS")),
        Subsignal("n", Pins("E23"), IOStandard("LVDS")),
    ),
    ("clk300", 0,
        Subsignal("p", Pins("AH18"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("n", Pins("AH17"), IOStandard("DIFF_SSTL12_DCI")),
    ),
    ("cpu_reset", 0, Pins("M11"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led", 0, Pins("D5"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("D6"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("A5"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("B5"), IOStandard("LVCMOS33")),

    # Buttons
    ("user_btn", 0, Pins("B4"), IOStandard("LVCMOS33")),
    ("user_btn", 1, Pins("C4"), IOStandard("LVCMOS33")),
    ("user_btn", 2, Pins("B3"), IOStandard("LVCMOS33")),
    ("user_btn", 3, Pins("C3"), IOStandard("LVCMOS33")),

    # Switches
    ("user_dip", 0, Pins("E4"), IOStandard("LVCMOS33")),
    ("user_dip", 1, Pins("D4"), IOStandard("LVCMOS33")),
    ("user_dip", 2, Pins("F5"), IOStandard("LVCMOS33")),
    ("user_dip", 3, Pins("F4"), IOStandard("LVCMOS33")),

    # Serial
    ("serial", 0,
        Subsignal("cts", Pins("A19")),
        Subsignal("rts", Pins("C18")),
        Subsignal("tx", Pins("C19")),
        Subsignal("rx", Pins("A20")),
        IOStandard("LVCMOS18")
    ),

    # I2C
    ("i2c", 0,
        Subsignal("sda", Pins("P12")),
        Subsignal("scl", Pins("N12")),
        IOStandard("LVCMOS33")
    ),

    # DDR4 SDRAM
    ("ddram", 0,
        Subsignal("a",       Pins(
            "AH16 AG14 AG15 AF15 AF16 AJ14 AH14 AF17",
            "AK17 AJ17 AK14 AK15 AL18 AK18"),
            IOStandard("SSTL12_DCI")),
        Subsignal("ba",      Pins("AL15 AL16"), IOStandard("SSTL12_DCI")),
        Subsignal("bg",      Pins("AC16 AB16"), IOStandard("SSTL12_DCI")),
        Subsignal("ras_n",   Pins("AD15"), IOStandard("SSTL12_DCI")), # A16
        Subsignal("cas_n",   Pins("AA14"), IOStandard("SSTL12_DCI")), # A15
        Subsignal("we_n",    Pins("AA16"), IOStandard("SSTL12_DCI")), # A14
        Subsignal("cs_n",    Pins("AA15"), IOStandard("SSTL12_DCI")), # also AL17 AN17 AN16 for larger SODIMMs
        Subsignal("act_n",   Pins("AC17"), IOStandard("SSTL12_DCI")),
        #Subsignal("alert_n", Pins("AB15"), IOStandard("SSTL12_DCI")),
        #Subsignal("par",     Pins("AD16"), IOStandard("SSTL12_DCI")),
        Subsignal("dm",      Pins("AH22 AE18 AL20 AP19 AF11 AH12 AK13 AN12"),
            IOStandard("POD12_DCI")),
        Subsignal("dq",      Pins(
                "AE24 AE23 AF22 AF21 AG20 AG19 AH21 AG21",
                "AA20 AA19 AD19 AC18 AE20 AD20 AC19 AB19",
                "AJ22 AJ21 AK20 AJ20 AK19 AJ19 AL23 AL22",
                "AN23 AM23 AP23 AN22 AP22 AP21 AN19 AM19",
                "AC13 AB13 AF12 AE12 AF13 AE13 AE14 AD14",
                "AG8  AF8  AG10 AG11 AH13 AG13 AJ11 AH11",
                "AK9  AJ9  AK10 AJ10 AL12 AK12 AL10 AL11",
                "AM8  AM9  AM10 AM11 AP11 AN11 AP9  AP10"),
            IOStandard("POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_p",   Pins("AF23 AA18 AK22 AM21 AC12 AG9 AK8 AN9"),
            IOStandard("DIFF_POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_n",   Pins("AG23 AB18 AK23 AN21 AD12 AH9 AL8 AN8"),
            IOStandard("DIFF_POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("clk_p",   Pins("AF18"), IOStandard("DIFF_SSTL12_DCI")), # also AJ16 for larger SODIMMs
        Subsignal("clk_n",   Pins("AG18"), IOStandard("DIFF_SSTL12_DCI")), # also AJ15 for larger SODIMMs
        Subsignal("cke",     Pins("AD17"), IOStandard("SSTL12_DCI")), # also AM15 for larger SODIMMs
        Subsignal("odt",     Pins("AE15"), IOStandard("SSTL12_DCI")), # also AM16 for larger SODIMMs
        Subsignal("reset_n", Pins("AB14"), IOStandard("LVCMOS12")),
        Misc("SLEW=FAST"),
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxUSPPlatform):
    default_clk_name   = "clk125"
    default_clk_period = 1e9/125e6

    def __init__(self, toolchain="vivado"):
        XilinxUSPPlatform.__init__(self, "xczu7ev-ffvc1156-2-i", _io, toolchain=toolchain)

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment):
        XilinxUSPPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk125", loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("clk300", loose=True), 1e9/125e6)
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 64]")
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 65]")
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 66]")
