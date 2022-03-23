#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform, VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst.
    # TODO: Document SI5338A.
    ("clk24",  0, Pins("P26"),  IOStandard("LVCMOS15")),
    ("clk200", 0,
        Subsignal("p", Pins("AJ29"), IOStandard("LVDS")),
        Subsignal("n", Pins("AK30"), IOStandard("LVDS"))
    ),
    ("clk",   0, Pins("AJ29"), IOStandard("LVCMOS15")),
    ("clk",   0, Pins("AK30"), IOStandard("LVCMOS15")),

    # Debug.
    ("debug", 0, Pins("AL34"), IOStandard("LVCMOS15")),
    ("debug", 1, Pins("AM34"), IOStandard("LVCMOS15")),
    ("debug", 2, Pins("AN34"), IOStandard("LVCMOS15")),
    ("debug", 3, Pins("AP34"), IOStandard("LVCMOS15")),


    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("AP9")),
        Subsignal("rx", Pins("AN9")),
        IOStandard("LVCMOS15")
    ),

    # SPIFlash (MX25L25645GSXDI).

    # TODO (Probably similar to KCU105).

    # PCIe
    ("pcie_x1", 0,
        #Subsignal("rst_n", Pins(""), IOStandard("")),
        Subsignal("clk_p", Pins("AB6")),
        Subsignal("clk_n", Pins("AB5")),
        Subsignal("rx_p",  Pins("AB2")),
        Subsignal("rx_n",  Pins("AB1")),
        Subsignal("tx_p",  Pins("AC4")),
        Subsignal("tx_n",  Pins("AC3"))
    ),
    ("pcie_x2", 0,
        #Subsignal("rst_n", Pins(""), IOStandard("")),
        Subsignal("clk_p", Pins("AB6")),
        Subsignal("clk_n", Pins("AB5")),
        Subsignal("rx_p",  Pins("AB2 AD2")),
        Subsignal("rx_n",  Pins("AB1 AD1")),
        Subsignal("tx_p",  Pins("AC4 AE4")),
        Subsignal("tx_n",  Pins("AC3 AE3"))
    ),
    ("pcie_x4", 0,
        #Subsignal("rst_n", Pins(""), IOStandard("")),
        Subsignal("clk_p", Pins("AB6")),
        Subsignal("clk_n", Pins("AB5")),
        Subsignal("rx_p",  Pins("AB2 AD2 AF2 AH2")),
        Subsignal("rx_n",  Pins("AB1 AD1 AF1 AH1")),
        Subsignal("tx_p",  Pins("AC4 AE4 AG4 AH6")),
        Subsignal("tx_n",  Pins("AC3 AE3 AG3 AH5"))
    ),
    ("pcie_x8", 0,
        #Subsignal("rst_n", Pins(""), IOStandard("")),
        Subsignal("clk_p", Pins("AB6")),
        Subsignal("clk_n", Pins("AB5")),
        Subsignal("rx_p",  Pins("AB2 AD2 AF2 AH2 AJ4 AK2 AM2 AP2")),
        Subsignal("rx_n",  Pins("AB1 AD1 AF1 AH1 AJ3 AK1 AM1 AP1")),
        Subsignal("tx_p",  Pins("AC4 AE4 AG4 AH6 AK6 AL4 AM6 AN4")),
        Subsignal("tx_n",  Pins("AC3 AE3 AG3 AH5 AK5 AL3 AM5 AN3"))
    ),

    # DDR3 SDRAM (H5TQ4G63CFR).
    ("ddram", 0,
        Subsignal("a", Pins(
            "AP16 AM19 AL17 AM14 AL19 AL14 AJ18 AK16",
            "AJ19 AK17 AP18 AM17 AL18 AH17 AH14"),
            IOStandard("SSTL15_DCI")),
        Subsignal("ba",    Pins("AN14 AN19 AP14"), IOStandard("SSTL15_DCI")),
        Subsignal("ras_n", Pins("AN16"), IOStandard("SSTL15_DCI")),
        Subsignal("cas_n", Pins("AM16"), IOStandard("SSTL15_DCI")),
        Subsignal("we_n",  Pins("AP15"), IOStandard("SSTL15_DCI")),
        Subsignal("cs_n",  Pins("AM15"), IOStandard("SSTL15_DCI")),
        Subsignal("dm", Pins("AH26 AN26 AJ21 AM21 AH18 AE25 AD21 AD19"),
            IOStandard("SSTL15_DCI"),
            Misc("DATA_RATE=DDR")),
        Subsignal("dq", Pins(
            "AM27 AK28 AH27 AJ28 AK26 AH28 AM26 AK27",
            "AP29 AP28 AM30 AN27 AM29 AN28 AL30 AL29",
            "AM20 AK22 AL20 AL22 AL23 AL24 AK23 AL25",
            "AP25 AM24 AN24 AM22 AN23 AN22 AP24 AP23",
            "AJ16 AG17 AG15 AG19 AH16 AH19 AG14 AG16",
            "AJ24 AG24 AJ23 AF23 AH22 AF24 AH23 AG25",
            "AE20 AF20 AD20 AG20 AE22 AE23 AF22 AG22",
            "AF18 AD15 AF17 AE17 AF14 AE18 AF15 AD16"),
            IOStandard("SSTL15_DCI"),
            Misc("ODT=RTT_40"),
            Misc("DATA_RATE=DDR")),
        Subsignal("dqs_p", Pins("AL27 AN29 AJ20 AP20 AJ15 AH24 AG21 AE16"),
            IOStandard("DIFF_SSTL15_DCI"),
            Misc("ODT=RTT_40"),
            Misc("DATA_RATE=DDR")),
        Subsignal("dqs_n", Pins("AL28 AP30 AK20 AP21 AJ14 AJ25 AH21 AE15"),
            IOStandard("DIFF_SSTL15_DCI"),
             Misc("ODT=RTT_40"),
            Misc("DATA_RATE=DDR")),
        Subsignal("clk_p", Pins("AN18"), IOStandard("DIFF_SSTL15_DCI"), Misc("DATA_RATE=DDR")),
        Subsignal("clk_n", Pins("AN17"), IOStandard("DIFF_SSTL15_DCI"), Misc("DATA_RATE=DDR")),
        Subsignal("cke",   Pins("AK18"), IOStandard("SSTL15_DCI")),
        Subsignal("odt",   Pins("AL15"), IOStandard("SSTL15_DCI")),
        Subsignal("reset_n", Pins("AK15"), IOStandard("SSTL15")),
        Misc("SLEW=FAST"),
        Misc("OUTPUT_IMPEDANCE=RDRV_40_40")
    ),

    # HDMI (through PI3HDX1204)
    ("hdmi_in", 0, # PCIe Edge Side.
        #Subsignal("clk_p",   Pins(""), IOStandard("")),
        #Subsignal("clk_n",   Pins(""), IOStandard("")),
        Subsignal("data0_p", Pins("Y2")),
        Subsignal("data0_n", Pins("Y1")),
        Subsignal("data1_p", Pins("V2")),
        Subsignal("data1_n", Pins("V1")),
        Subsignal("data2_p", Pins("T2")),
        Subsignal("data2_n", Pins("T1")),
    ),
    ("hdmi_in", 1,
        #Subsignal("clk_p",   Pins(""), IOStandard("")),
        #Subsignal("clk_n",   Pins(""), IOStandard("")),
        Subsignal("data0_p", Pins("P2")),
        Subsignal("data0_n", Pins("P1")),
        Subsignal("data1_p", Pins("M2")),
        Subsignal("data1_n", Pins("M1")),
        Subsignal("data2_p", Pins("K2")),
        Subsignal("data2_n", Pins("K1")),
    ),
    ("hdmi_in", 2,
        #Subsignal("clk_p",   Pins(""), IOStandard("")),
        #Subsignal("clk_n",   Pins(""), IOStandard("")),
        Subsignal("data0_p", Pins("H2")),
        Subsignal("data0_n", Pins("H1")),
        Subsignal("data1_p", Pins("F2")),
        Subsignal("data1_n", Pins("F1")),
        Subsignal("data2_p", Pins("E4")),
        Subsignal("data2_n", Pins("E3")),
    ),
    ("hdmi_in", 3,
        #Subsignal("clk_p",   Pins(""), IOStandard("")),
        #Subsignal("clk_n",   Pins(""), IOStandard("")),
        Subsignal("data0_p", Pins("D2")),
        Subsignal("data0_n", Pins("D1")),
        Subsignal("data1_p", Pins("B2")),
        Subsignal("data1_n", Pins("B1")),
        Subsignal("data2_p", Pins("B4")),
        Subsignal("data2_n", Pins("B3")),
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "clk200"
    default_clk_period = 1e9/200e6

    def __init__(self, toolchain="vivado"):
        XilinxPlatform.__init__(self, "xcku040-ffva1156-2-e", _io, toolchain=toolchain)

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk24",  loose=True), 1e9/24e6)
        self.add_period_constraint(self.lookup_request("clk200", loose=True), 1e9/200e6)
        self.add_platform_command("set_property INTERNAL_VREF 0.75 [get_iobanks 44]")
        self.add_platform_command("set_property INTERNAL_VREF 0.75 [get_iobanks 45]")
        self.add_platform_command("set_property INTERNAL_VREF 0.75 [get_iobanks 46]")
