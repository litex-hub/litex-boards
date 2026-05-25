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

    # HDMI
    ("hdmi_out", 0,
        Subsignal("txp",   Pins("M4 L6 K4")),
        Subsignal("txn",   Pins("M3 L5 K3")),
        Subsignal("clk_p", Pins("H9"), IOStandard("LVDS")),
        Subsignal("clk_n", Pins("G9"), IOStandard("LVDS")),
        Subsignal("scl",   Pins("B1"), IOStandard("LVCMOS33")),
        Subsignal("sda",   Pins("C1"), IOStandard("LVCMOS33")),
        Subsignal("en",    Pins("A2"), IOStandard("LVCMOS33")),
        Subsignal("cec",   Pins("A3"), IOStandard("LVCMOS33")),
        Subsignal("hpd",   Pins("E3"), IOStandard("LVCMOS33")),
    ),
    ("hdmi_in", 0,
        Subsignal("rxp",     Pins("N2 L2 J2")),
        Subsignal("rxn",     Pins("N1 L1 J1")),
        Subsignal("clk_p",   Pins("R10")),
        Subsignal("clk_n",   Pins("R9")),
        Subsignal("hpd",     Pins("F6"), IOStandard("LVCMOS33")),
        Subsignal("pwr_det", Pins("E5"), IOStandard("LVCMOS33")),
        Subsignal("scl",     Pins("D2"), IOStandard("LVCMOS33")),
        Subsignal("sda",     Pins("E2"), IOStandard("LVCMOS33")),
    ),
    ("hdmi_ctl", 0,
        Subsignal("scl",        Pins("D1"), IOStandard("LVCMOS33")),
        Subsignal("sda",        Pins("E1"), IOStandard("LVCMOS33")),
        Subsignal("clkgen_lol", Pins("N11"), IOStandard("LVCMOS33")),
        Subsignal("clkgen_rst", Pins("M12"), IOStandard("LVCMOS33")),
        Subsignal("rec_clk_p",  Pins("G14"), IOStandard("LVDS")),
        Subsignal("rec_clk_n",  Pins("F13"), IOStandard("LVDS")),
        Subsignal("refclk_p",   Pins("T8")),
        Subsignal("refclk_n",   Pins("T7")),
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

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("pmod0", "G8 H8 G7 H7 G6 H6 J6 J7"),
    ("pmod1", "J9 K9 K8 L8 L10 M10 M8 M9"),
    ("FMC_LPC", {
        "CLK0_M2C_N"      : "E14",
        "CLK0_M2C_P"      : "E15",
        "CLK1_M2C_N"      : "F10",
        "CLK1_M2C_P"      : "G10",
        "DP0_C2M_N"       : "H3",
        "DP0_C2M_P"       : "H4",
        "DP0_M2C_N"       : "G1",
        "DP0_M2C_P"       : "G2",
        "GBTCLK0_M2C_C_N" : "V7",
        "GBTCLK0_M2C_C_P" : "V8",
        "LA00_CC_N"       : "F16",
        "LA00_CC_P"       : "F17",
        "LA01_CC_N"       : "H17",
        "LA01_CC_P"       : "H18",
        "LA02_N"          : "K20",
        "LA02_P"          : "L20",
        "LA03_N"          : "K18",
        "LA03_P"          : "K19",
        "LA04_N"          : "L16",
        "LA04_P"          : "L17",
        "LA05_N"          : "J17",
        "LA05_P"          : "K17",
        "LA06_N"          : "G19",
        "LA06_P"          : "H19",
        "LA07_N"          : "J15",
        "LA07_P"          : "J16",
        "LA08_N"          : "E17",
        "LA08_P"          : "E18",
        "LA09_N"          : "G16",
        "LA09_P"          : "H16",
        "LA10_N"          : "K15",
        "LA10_P"          : "L15",
        "LA11_N"          : "A12",
        "LA11_P"          : "A13",
        "LA12_N"          : "F18",
        "LA12_P"          : "G18",
        "LA13_N"          : "F15",
        "LA13_P"          : "G15",
        "LA14_N"          : "C12",
        "LA14_P"          : "C13",
        "LA15_N"          : "C16",
        "LA15_P"          : "D16",
        "LA16_N"          : "C17",
        "LA16_P"          : "D17",
        "LA17_CC_N"       : "E10",
        "LA17_CC_P"       : "F11",
        "LA18_CC_N"       : "D10",
        "LA18_CC_P"       : "D11",
        "LA19_N"          : "C11",
        "LA19_P"          : "D12",
        "LA20_N"          : "E12",
        "LA20_P"          : "F12",
        "LA21_N"          : "A10",
        "LA21_P"          : "B10",
        "LA22_N"          : "H12",
        "LA22_P"          : "H13",
        "LA23_N"          : "A11",
        "LA23_P"          : "B11",
        "LA24_N"          : "A6",
        "LA24_P"          : "B6",
        "LA25_N"          : "C6",
        "LA25_P"          : "C7",
        "LA26_N"          : "B8",
        "LA26_P"          : "B9",
        "LA27_N"          : "A7",
        "LA27_P"          : "A8",
        "LA28_N"          : "L13",
        "LA28_P"          : "M13",
        "LA29_N"          : "J10",
        "LA29_P"          : "K10",
        "LA30_N"          : "D9",
        "LA30_P"          : "E9",
        "LA31_N"          : "E7",
        "LA31_P"          : "F7",
        "LA32_N"          : "E8",
        "LA32_P"          : "F8",
        "LA33_N"          : "C8",
        "LA33_P"          : "C9",
    }),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxUSPPlatform):
    default_clk_name   = "clk125"
    default_clk_period = 1e9/125e6

    def __init__(self, toolchain="vivado"):
        XilinxUSPPlatform.__init__(self, "xczu7ev-ffvc1156-2-i", _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment):
        XilinxUSPPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk125", loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("clk300", loose=True), 1e9/300e6)
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 64]")
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 65]")
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 66]")
