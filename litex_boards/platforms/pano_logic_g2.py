#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019 Tom Keddie <git@bronwenandtom.com>
# Copyright (c) 2020 Antmicro <www.antmicro.com>
# Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# The Pano Logic Zero Client G2 is a thin commercial client from Pano Logic that can be repurposed
# as a generic development board thanks to reverse engineering efforts than can be found at:
# https://github.com/tomverbeure/panologic-g2

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # clock / reset
    ("clk125",    0, Pins("Y13"),  IOStandard("LVCMOS33")),
    ("rst_n",     0, Pins("AB14"), IOStandard("LVCMOS33")),

    # led
    ("user_led", 0, Pins("E12"),  IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("H13"),  IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("F13"),  IOStandard("LVCMOS33")),

    # btn
    ("user_btn_n", 0, Pins("H12"), IOStandard("LVCMOS33")),

    # serial
    ("serial", 0, # hdmi
        Subsignal("tx", Pins("AB19")),
        Subsignal("rx", Pins("AA21")),
        IOStandard("LVCMOS33")
    ),

    # serial
    ("serial", 1, # dvi
        Subsignal("tx", Pins("C14")),
        Subsignal("rx", Pins("C17")),
        IOStandard("LVCMOS33")
    ),

    # spi flash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("T5"),   IOStandard("LVCMOS33")),
        Subsignal("clk",  Pins("Y21"),  IOStandard("LVCMOS33")),
        Subsignal("mosi", Pins("AB20"), IOStandard("LVCMOS33")),
        Subsignal("miso", Pins("AA20"), IOStandard("LVCMOS33"))
    ),

    # ddram
    ("ddram_clock_a", 0,
        Subsignal("p", Pins("H20")),
        Subsignal("n", Pins("J19")),
        IOStandard("DIFF_SSTL18_II"), Misc("IN_TERM=NONE")
    ),
    ("ddram_a", 0,
        Subsignal("a", Pins(
            "F21 F22 E22 G20 F20 K20 K19 E20",
            "C20 C22 G19 F19 D22"),
            IOStandard("SSTL18_II")),
        Subsignal("ba",    Pins("J17 K17 H18"), IOStandard("SSTL18_II")),
        Subsignal("ras_n", Pins("H21"), IOStandard("SSTL18_II")),
        Subsignal("cas_n", Pins("H22"), IOStandard("SSTL18_II")),
        Subsignal("we_n",  Pins("H19"), IOStandard("SSTL18_II")),
        Subsignal("dm",    Pins("M20 L19"), IOStandard("SSTL18_II")),
        Subsignal("dq",    Pins(
            "N20 N22 M21 M22 J20 J22 K21 K22",
            "P21 P22 R20 R22 U20 U22 V21 V22"),
            IOStandard("SSTL18_II")),
        Subsignal("dqs",   Pins("T21 L20"), IOStandard("DIFF_SSTL18_II")),
        Subsignal("dqs_n", Pins("T22 L22"), IOStandard("DIFF_SSTL18_II")),
        Subsignal("cke", Pins("D21"), IOStandard("SSTL18_II")),
        Subsignal("odt", Pins("G22"), IOStandard("SSTL18_II")),
    ),

    ("ddram_clock_b", 0,
        Subsignal("p", Pins("H4")),
        Subsignal("n", Pins("H3")),
        IOStandard("DIFF_SSTL18_II"), Misc("IN_TERM=NONE")
    ),
    ("ddram_b", 0,
        Subsignal("a", Pins(
            "H2 H1 H5 K6 F3 K3 J4 H6",
            "E3 E1 G4 C1 D1"),
            IOStandard("SSTL18_II")),
        Subsignal("ba",    Pins("G3 G1 F1"), IOStandard("SSTL18_II")),
        Subsignal("ras_n", Pins("K5"), IOStandard("SSTL18_II")),
        Subsignal("cas_n", Pins("K4"), IOStandard("SSTL18_II")),
        Subsignal("we_n",  Pins("F2"), IOStandard("SSTL18_II")),
        Subsignal("dm",    Pins("M3 L4"), IOStandard("SSTL18_II")),
        Subsignal("dq",    Pins(
            "N3 N1 M2 M1 J3 J1 K2 K1",
            "P2 P1 R3 R1 U3 U1 V2 V1"),
            IOStandard("SSTL18_II")),
        Subsignal("dqs",   Pins("T2 L3"), IOStandard("DIFF_SSTL18_II")),
        Subsignal("dqs_n", Pins("T1 L1"), IOStandard("DIFF_SSTL18_II")),
        Subsignal("cke", Pins("D2"), IOStandard("SSTL18_II")),
        Subsignal("odt", Pins("J6"), IOStandard("SSTL18_II")),
    ),

    # ethernet
    ("eth_rst_n",  0, Pins("R11"), IOStandard("LVCMOS33")),
    ("eth_clocks", 0,
        Subsignal("tx",  Pins("Y11")),
        Subsignal("gtx", Pins("AA12")),
        Subsignal("rx",  Pins("AB11")),
        IOStandard("LVCMOS33")
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("R11")),
        Subsignal("int_n",   Pins("AA4")),
        Subsignal("mdio",    Pins("AA2")),
        Subsignal("mdc",     Pins("AB6")),
        Subsignal("rx_dv",   Pins("Y7")),
        Subsignal("rx_er",   Pins("Y8")),
        Subsignal("rx_data", Pins("Y3 Y4 R9 R7 V9 R8 U9 Y9")),
        Subsignal("tx_en",   Pins("AA8")),
        Subsignal("tx_er",   Pins("AB8")),
        Subsignal("tx_data", Pins("AB2 AB3 AB4 AB7 AB9 AB10 T7 Y10")),
        Subsignal("col",     Pins("V7")),
        Subsignal("crs",     Pins("W4")),
        IOStandard("LVCMOS33")
    ),

]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "clk125"
    default_clk_period = 1e9/125e6

    def __init__(self, revision="c"):
        assert revision in ["b", "c"]
        device = {"b": "xc6slx150-2-fgg484", "c": "xc6slx100-2-fgg484"}[revision]
        XilinxPlatform.__init__(self, device, _io)
        self.add_platform_command("""CONFIG VCCAUX="2.5";""")
        self.add_period_constraint(self.lookup_request("clk125", loose=True), 1e9/125e6)

    def create_programmer(self):
        return OpenOCD("openocd_xc6_ft232.cfg")
