#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform, VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst (SI5338A).

    # TODO (We'll use the 100MHz PCIe Clock for now).

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

    # DRAM (H5TQ4G63CFR).

    # TODO.

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
    def __init__(self):
        XilinxPlatform.__init__(self, "xcku040-ffva1156-2-e", _io, toolchain="vivado")

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
