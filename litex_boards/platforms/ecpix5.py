#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.lattice import LatticePlatform
from litex.build.lattice.programmer import OpenOCDJTAGProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # clock / reset
    ("clk100", 0, Pins("K23"), IOStandard("LVCMOS33")),
    ("rst_n",  0, Pins("N5"),  IOStandard("LVCMOS33")),

    # led
    ("rgb_led", 0,
        Subsignal("r", Pins("U21")),
        Subsignal("g", Pins("W21")),
        Subsignal("b", Pins("T24")),
        IOStandard("LVCMOS33"),
    ),
    ("rgb_led", 1,
        Subsignal("r", Pins("T23")),
        Subsignal("g", Pins("R21")),
        Subsignal("b", Pins("T22")),
        IOStandard("LVCMOS33"),
    ),
    ("rgb_led", 2,
        Subsignal("r", Pins("P21")),
        Subsignal("g", Pins("R23")),
        Subsignal("b", Pins("P22")),
        IOStandard("LVCMOS33"),
    ),
    ("rgb_led", 3,
        Subsignal("r", Pins("K21")),
        Subsignal("g", Pins("K24")),
        Subsignal("b", Pins("M21")),
        IOStandard("LVCMOS33"),
    ),

    # serial
    ("serial", 0,
        Subsignal("rx", Pins("R26"), IOStandard("LVCMOS33")),
        Subsignal("tx", Pins("R24"), IOStandard("LVCMOS33")),
    ),

    # ddram
    ("ddram", 0,
        Subsignal("a", Pins(
            "T5 M3 L3 V6 K2 W6 K3 L1",
            "H2 L2 N1 J1 M1 K1"),
            IOStandard("SSTL15_I")),
        Subsignal("ba",    Pins("U6 N3 N4"), IOStandard("SSTL15_I")),
        Subsignal("ras_n", Pins("T3"), IOStandard("SSTL15_I")),
        Subsignal("cas_n", Pins("P2"), IOStandard("SSTL15_I")),
        Subsignal("we_n",  Pins("R3"), IOStandard("SSTL15_I")),
        Subsignal("dm", Pins("U4 U1"), IOStandard("SSTL15_I")),
        Subsignal("dq", Pins(
            "T4 W4 R4 W5 R6 P6 P5 P4",
            "R1 W3 T2 V3 U3 W1 T1 W2",),
            IOStandard("SSTL15_I"),
            Misc("TERMINATION=75")),
        Subsignal("dqs_p", Pins("V4 V1"), IOStandard("SSTL15D_I"),
            Misc("TERMINATION=OFF"),
            Misc("DIFFRESISTOR=100")),
        Subsignal("clk_p", Pins("H3"), IOStandard("SSTL15D_I")),
        Subsignal("cke",   Pins("P1"), IOStandard("SSTL15_I")),
        Subsignal("odt",   Pins("P3"), IOStandard("SSTL15_I")),
        Misc("SLEWRATE=FAST"),
    ),

    # ethernet
    ("eth_clocks", 0,
        Subsignal("tx", Pins("A12")),
        Subsignal("rx", Pins("E11")),
        IOStandard("LVCMOS33")
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("C13")),
        Subsignal("mdio",    Pins("A13")),
        Subsignal("mdc",     Pins("C11")),
        Subsignal("rx_ctl",  Pins("A11")),
        Subsignal("rx_data", Pins("B11 A10 B10 A9"), Misc("PULLMODE=UP")), # RGMII mode - Advertise all capabilities.
        Subsignal("tx_ctl",  Pins("C9")),
        Subsignal("tx_data", Pins("D8 C8 B8 A8")),
        IOStandard("LVCMOS33")
    ),

    # sdcard
    ("sdcard", 0,
        Subsignal("data",      Pins("N26 N25 N23 N21"), Misc("PULLMODE=UP")),
        Subsignal("cmd",       Pins("M24"),             Misc("PULLMODE=UP")),
        Subsignal("clk",       Pins("P24")),
        Subsignal("cmd_dir",   Pins("M23")),
        Subsignal("dat0_dir",  Pins("N24")),
        Subsignal("dat13_dir", Pins("P26")),
        IOStandard("LVCMOS33"),
    ),
]

_connectors = []

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticePlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self, **kwargs):
        LatticePlatform.__init__(self, "LFE5UM5G-85F-8BG554I", _io, _connectors, **kwargs)

    def create_programmer(self):
        return OpenOCDJTAGProgrammer("openocd_ecpix5.cfg")

    def do_finalize(self, fragment):
        LatticePlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100", loose=True), 1e9/100e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:rx", 0, loose=True), 1e9/125e6)
