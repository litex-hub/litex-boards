#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020-2022 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.lattice import LatticeECP5Platform
from litex.build.openfpgaloader import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk100", 0, Pins("K23"), IOStandard("LVCMOS33")),
    ("rst_n",  0, Pins("N5"),  IOStandard("LVCMOS33")),

    # Leds
    ("rgb_led", 0,
        Subsignal("r", Pins("P21")),
        Subsignal("g", Pins("R23")),
        Subsignal("b", Pins("P22")),
        IOStandard("LVCMOS33"),
    ),
    ("rgb_led", 1,
        Subsignal("r", Pins("K21")),
        Subsignal("g", Pins("K24")),
        Subsignal("b", Pins("M21")),
        IOStandard("LVCMOS33"),
    ),
    ("rgb_led", 2,
        Subsignal("r", Pins("U21")),
        Subsignal("g", Pins("W21")),
        Subsignal("b", Pins("T24")),
        IOStandard("LVCMOS33"),
    ),
    ("rgb_led", 3,
        Subsignal("r", Pins("T23")),
        Subsignal("g", Pins("R21")),
        Subsignal("b", Pins("T22")),
        IOStandard("LVCMOS33"),
    ),

    # Serial
    ("serial", 0,
        Subsignal("rx", Pins("R26"), IOStandard("LVCMOS33")),
        Subsignal("tx", Pins("R24"), IOStandard("LVCMOS33")),
    ),

    # DDR3 SDRAM
    ("ddram", 0,
        Subsignal("a", Pins(
            "T5 M3 L3 V6 K2 W6 K3 L1",
            "H2 L2 N1 J1 M1 K1 H1"),
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

    # RGMII Ethernetx
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

    # SDCard
    ("sdcard", 0,
        Subsignal("data",      Pins("N26 N25 N23 N21"), Misc("PULLMODE=UP")),
        Subsignal("cmd",       Pins("M24"),             Misc("PULLMODE=UP")),
        Subsignal("clk",       Pins("P24")),
        Subsignal("cd",        Pins("L22")),
        Subsignal("cmd_dir",   Pins("M23")),
        Subsignal("dat0_dir",  Pins("N24")),
        Subsignal("dat13_dir", Pins("P26")),
        IOStandard("LVCMOS33"),
    ),

    # Sata
    ("sata", 0,
        Subsignal("clk_p", Pins("AF12")),
        Subsignal("clk_n", Pins("AF13")),
        Subsignal("rx_p", Pins("AF15")),
        Subsignal("rx_n", Pins("AF16")),
        Subsignal("tx_p", Pins("AD16")),
        Subsignal("tx_n", Pins("AD17")),
        IOStandard("LVCMOS33"),
    ),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("AA2")),
        Subsignal("mosi", Pins("AE2")),
        Subsignal("miso", Pins("AD2")),
        Subsignal("wp", Pins("AF2")),
        Subsignal("hold", Pins("AE1")),
        IOStandard("LVCMOS33")
    ),
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("AA2")),
        Subsignal("dq", Pins("AE2", "AD2", "AF2", "AE1")),
        IOStandard("LVCMOS33")
    ),

    # USB
    ("ulpi", 0,
        Subsignal("rst",  Pins("E23")),
        Subsignal("clk",  Pins("H24")),
        Subsignal("dir",  Pins("F22")),
        Subsignal("nxt",  Pins("F23")),
        Subsignal("stp",  Pins("H23")),
        Subsignal("data", Pins("M26 L25 L26 K25 K26 J23 P25 H25")),
        IOStandard("LVCMOS33")
    ),

    # HDMI / IT6613
    ("hdmi", 0,
        Subsignal("r", Pins("AD26 AE25 AF25 AE26 E10 D11 D10 C10  D9  E8 H5 J4")),
        Subsignal("g", Pins("AA23 AA22 AA24 AA25  E1  F2  F1 D17 D16 E16 J6 H6")),
        Subsignal("b", Pins("AD25 AC26 AB24 AB25  B3  C3  D3  B1  C2  D2 D1 E3")),
        Subsignal("de",    Pins("A3")),
        Subsignal("clk",   Pins("C1")),
        Subsignal("vsync", Pins("A4")),
        Subsignal("hsync", Pins("B4")),
        Subsignal("sda", Pins("E17")),
        Subsignal("scl", Pins("C17")),
        IOStandard("LVCMOS33")
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("pmod0", "T25 U25 U24 V24 T26 U26 V26 W26"),
    ("pmod1", "U23 V23 U22 V21 W25 W24 W23 W22"),
    ("pmod2", "J24 H22 E21 D18 K22 J21 H21 D22"),
    ("pmod3", "E4 F4 E6 H4 F3 D4 D5 F5"),
    ("pmod4", "E26 D25 F26 F25 C26 C25 A25 A24"),
    ("pmod5", "D19 C21 B21 C22 D21 A21 A22 A23"),
    ("pmod6", "C16 B17 C18 B19 A17 A18 A19 C19"),
    ("pmod7", "D14 B14 E14 B16 C14 A14 A15 A16"),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticeECP5Platform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self, device="85F", toolchain="trellis", **kwargs):
        assert device in ["45F", "85F"]
        LatticeECP5Platform.__init__(self, f"LFE5UM5G-{device}-8BG554I", _io, _connectors, toolchain=toolchain, **kwargs)

    def create_programmer(self):
        return OpenFPGALoader("ecpix5")

    def do_finalize(self, fragment):
        LatticeECP5Platform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100", loose=True), 1e9/100e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:rx", 0, loose=True), 1e9/125e6)
