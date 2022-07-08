#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform, VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("rst",    0, Pins("G13"), IOStandard("LVCMOS18")),
    ("clk125", 0,
        Subsignal("p", Pins("H9"), IOStandard("DIFF_SSTL15")),
        Subsignal("n", Pins("G9"), IOStandard("DIFF_SSTL15")),
    ),

    # Leds
    ("user_led", 0, Pins("AL11"), IOStandard("LVCMOS12")),
    ("user_led", 1, Pins("AL13"), IOStandard("LVCMOS12")),
    ("user_led", 2, Pins("AK13"), IOStandard("LVCMOS12")),
    ("user_led", 3, Pins("AE15"), IOStandard("LVCMOS12")),
    ("user_led", 4, Pins("AM8"),  IOStandard("LVCMOS12")),
    ("user_led", 5, Pins("AM9"),  IOStandard("LVCMOS12")),
    ("user_led", 6, Pins("AM10"), IOStandard("LVCMOS12")),
    ("user_led", 7, Pins("AM11"), IOStandard("LVCMOS12")),

    # Buttons
    ("user_btn_c", 0, Pins("AL11"), IOStandard("LVCMOS12")),
    ("user_btn_n", 0, Pins("AG13"), IOStandard("LVCMOS12")),
    ("user_btn_s", 0, Pins("AP20"), IOStandard("LVCMOS12")),
    ("user_btn_w", 0, Pins("AK12"), IOStandard("LVCMOS12")),
    ("user_btn_e", 0, Pins("AC14"), IOStandard("LVCMOS12")),

    # Serial
    ("serial", 0,
        Subsignal("cts", Pins("AP17")),
        Subsignal("rts", Pins("AM15")),
        Subsignal("tx",  Pins("AL17")),
        Subsignal("rx",  Pins("AH17")),
        IOStandard("LVCMOS12")
    ),

    # PCIe
    ("pcie_x1", 0,
        Subsignal("rst_n", Pins("L8"), IOStandard("LVCMOS33")),
        Subsignal("clk_p", Pins("AB8")),
        Subsignal("clk_n", Pins("AB7")),
        Subsignal("rx_p",  Pins("AE2")),
        Subsignal("rx_n",  Pins("AE1")),
        Subsignal("tx_p",  Pins("AD4")),
        Subsignal("tx_n",  Pins("AD3")),
    ),
    ("pcie_x2", 0,
        Subsignal("rst_n", Pins("L8"), IOStandard("LVCMOS33")),
        Subsignal("clk_p", Pins("AB8")),
        Subsignal("clk_n", Pins("AB7")),
        Subsignal("rx_p",  Pins("AE2 AF4")),
        Subsignal("rx_n",  Pins("AE1 AF3")),
        Subsignal("tx_p",  Pins("AD4 AE6")),
        Subsignal("tx_n",  Pins("AD3 AE5")),
    ),
    ("pcie_x4", 0,
        Subsignal("rst_n", Pins("L8"), IOStandard("LVCMOS33")),
        Subsignal("clk_p", Pins("AB8")),
        Subsignal("clk_n", Pins("AB7")),
        Subsignal("rx_p",  Pins("AE2 AF4 AG2 AJ2")),
        Subsignal("rx_n",  Pins("AE1 AF3 AG1 AJ1")),
        Subsignal("tx_p",  Pins("AD4 AE6 AG6 AH4")),
        Subsignal("tx_n",  Pins("AD3 AE5 AG5 AH3")),
    ),

    # DDR4 SDRAM
    ("ddram", 0,
        Subsignal("a",       Pins(
            "AK9 AG11 AJ10 AL8 AK10 AH8 AJ9 AG8",
            "AH9 AG10 AH13 AG9 AM13 AF8"),
            IOStandard("SSTL12_DCI")),
        Subsignal("ba",      Pins("AK8 AL12"), IOStandard("SSTL12_DCI")),
        Subsignal("bg",      Pins("AE14"), IOStandard("SSTL12_DCI")),
        Subsignal("ras_n",   Pins("AF11"), IOStandard("SSTL12_DCI")), # A16
        Subsignal("cas_n",   Pins("AE12"), IOStandard("SSTL12_DCI")), # A15
        Subsignal("we_n",    Pins("AC12"), IOStandard("SSTL12_DCI")), # A14
        Subsignal("cs_n",    Pins("AD12"), IOStandard("SSTL12_DCI")),
        Subsignal("act_n",   Pins("AD14"), IOStandard("SSTL12_DCI")),
        # Subsignal("par",     Pins("AC13"), IOStandard("SSTL12_DCI")),
        Subsignal("dm",      Pins("AH18 AD15 AM16 AP18 AE18 AH22 AL20 AP19"),
            IOStandard("POD12_DCI")),
        Subsignal("dq",      Pins(
                "AF16 AF18 AG15 AF17 AF15 AG18 AG14 AE17",
                "AA14 AC16 AB15 AD16 AB16 AC17 AB14 AD17",
                "AJ16 AJ17 AL15 AK17 AJ15 AK18 AL16 AL18",
                "AP13 AP16 AP15 AN16 AN13 AM18 AN17 AN18",
                "AB19 AD19 AC18 AC19 AA20 AE20 AA19 AD20",
                "AF22 AH21 AG19 AG21 AE24 AG20 AE23 AF21",
                "AL22 AJ22 AL23 AJ21 AK20 AJ19 AK19 AJ20",
                "AP22 AN22 AP21 AP23 AM19 AM23 AN19 AN23"),
            IOStandard("POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_p",   Pins("AH14 AA16 AK15 AM14 AA18 AF23 AK22 AM21"),
            IOStandard("DIFF_POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_n",   Pins("AJ14 AA15 AK14 AN14 AB18 AG23 AK23 AN21"),
            IOStandard("DIFF_POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("clk_p",   Pins("AH11"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("clk_n",   Pins("AJ11"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("cke",     Pins("AB13"), IOStandard("SSTL12_DCI")),
        Subsignal("odt",     Pins("AF10"), IOStandard("SSTL12_DCI")),
        Subsignal("reset_n", Pins("AF12"), IOStandard("LVCMOS12")),
        Misc("SLEW=FAST"),
    ),
]


# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "clk125"
    default_clk_period = 1e9/125e6

    def __init__(self, toolchain="vivado"):
        XilinxPlatform.__init__(self, "xczu7ev-ffvc1156-2-e", _io, toolchain=toolchain)

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk125", loose=True), 1e9/125e6)
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 64]")
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 65]")
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 66]")
