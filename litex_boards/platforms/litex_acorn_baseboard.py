#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Ilia Sergachev <ilia.sergachev@protonmail.ch>
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# https://github.com/enjoy-digital/litex-acorn-baseboard

from litex.build.generic_platform import *
from litex.build.lattice import LatticePlatform
from litex.build.openfpgaloader import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk50", 0, Pins("L19"), IOStandard("LVCMOS33")),

    # Serial
    ("serial", 0,
        Subsignal("rx", Pins("B20"), IOStandard("LVCMOS33")),
        Subsignal("tx", Pins("A19"), IOStandard("LVCMOS33")),
    ),

    # Buttons
    ("user_btn", 0, Pins("M19"), IOStandard("LVCMOS33")),
    ("user_btn", 1, Pins("M20"), IOStandard("LVCMOS33")),

    # LCD
    ("lcd", 0,
        Subsignal("scl", Pins("P18"), Misc("PULLMODE=UP")),
        Subsignal("sda", Pins("L20"), Misc("PULLMODE=UP")),
        IOStandard("LVCMOS33")
    ),

    # SPIFlash
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("R2")),
        #Subsignal("clk",  Pins("U3")),
        Subsignal("dq",   Pins("W2 V2 Y2 W1")),
        IOStandard("LVCMOS33")
    ),

    # RGMII Ethernet
    ("eth_clocks", 0,
        Subsignal("tx", Pins("M1")),
        Subsignal("rx", Pins("H2")),
        IOStandard("LVCMOS25")
    ),
    ("eth", 0,
        Subsignal("int_n",   Pins("F1")),
        Subsignal("rst_n",   Pins("J3")),
        Subsignal("mdio",    Pins("G2")),
        Subsignal("mdc",     Pins("G1")),
        Subsignal("rx_ctl",  Pins("H1")),
        Subsignal("rx_data", Pins("J1 K2 K1 L2"), Misc("PULLMODE=UP")), # RGMII mode - Advertise all capabilities.
        Subsignal("tx_ctl",  Pins("L1")),
        Subsignal("tx_data", Pins("P1 P2 N1 N2")),
        IOStandard("LVCMOS25")
    ),

    # SDCard
    ("spisdcard", 0,
        Subsignal("clk",  Pins("P19")),
        Subsignal("cs_n", Pins("U19"), Misc("PULLMODE=UP")),
        Subsignal("mosi", Pins("T20"), Misc("PULLMODE=UP")),
        Subsignal("miso", Pins("N20"), Misc("PULLMODE=UP")),
        Misc("SLEWRATE=FAST"),
        IOStandard("LVCMOS33"),
    ),

    ("sdcard", 0,
        Subsignal("clk",  Pins("P19")),
        Subsignal("cd",   Pins("T18"),             Misc("PULLMODE=UP")),
        Subsignal("cmd",  Pins("T20"),             Misc("PULLMODE=UP")),
        Subsignal("data", Pins("N20 N19 U20 U19"), Misc("PULLMODE=UP")),
        Misc("SLEWRATE=FAST"),
        IOStandard("LVCMOS33"),
    ),

    # SerDes
    ("refclk", 0,
        Subsignal("p", Pins("Y11")),
        Subsignal("n", Pins("Y12")),
    ),

    # M2
    ("m2_devslp", 0, Pins("U18"), IOStandard("LVCMOS33")),
    ("m2_perst",  0, Pins("U17"), IOStandard("LVCMOS33")),
    ("m2_pewake", 0, Pins("R16"), IOStandard("LVCMOS33")),
    ("m2_pedet",  0, Pins("T17"), IOStandard("LVCMOS33")),
    ("m2_tx", 0,
        Subsignal("p", Pins("W4")),
        Subsignal("n", Pins("W5")),
    ),
    ("m2_rx", 0,
        Subsignal("p", Pins("Y5")),
        Subsignal("n", Pins("Y6")),
    ),

    # HDMI
    ("hdmi_i2c", 0,
        Subsignal("scl", Pins("C9")),
        Subsignal("sda", Pins("C8")),
        IOStandard("LVCMOS33")
    ),
    ("hdmi", 0,
        Subsignal("clk_p",   Pins("C4"), IOStandard("LVCMOS33D"), Misc("DRIVE=4")),
        Subsignal("data0_p", Pins("A4"), IOStandard("LVCMOS33D"), Misc("DRIVE=4")),
        Subsignal("data1_p", Pins("A2"), IOStandard("LVCMOS33D"), Misc("DRIVE=4")), # P/N Swap on PCB, invert in logic.
        Subsignal("data2_p", Pins("C1"), IOStandard("LVCMOS33D"), Misc("DRIVE=4")), # P/N Swap on PCB, invert in logic.
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("pmod1", "B6   A7  A8  A9  A6  B8  B9 A10"),
    ("pmod2", "A11 A12 A13 A14 B10 B11 B12 B13"),
    ("pmod3", "B15 B16 B17 B18 A15 A16 A17 A18"),
    ("pmod4", "D19 E19 F19 G19 C20 D20 E20 F20"),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticePlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/506

    def __init__(self, toolchain="trellis", **kwargs):
        LatticePlatform.__init__(self, "LFE5UM5G-45F-8BG381I", _io, _connectors, toolchain=toolchain, **kwargs)

    def create_programmer(self):
        return OpenFPGALoader("ecpix5")

    def do_finalize(self, fragment):
        LatticePlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
