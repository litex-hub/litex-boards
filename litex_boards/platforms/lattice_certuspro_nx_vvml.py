#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2024 Enjoy-Digital <enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.lattice import LatticeNexusPlatform
from litex.build.openfpgaloader import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Figure A.6
    ("clk24", 0, Pins("M20"), IOStandard("LVCMOS18")),
    ("clk27", 0, Pins("M22"), IOStandard("LVCMOS18")),

    # 8.1. General Purpose Push Buttons - all logic zero when pressed
    ("gsrn",     0, Pins("R5"),  IOStandard("LVCMOS33")),  # SW4
    ("programn", 0, Pins("C20"), IOStandard("LVCMOS33")),  # SW5
    ("user_btn", 0, Pins("N1"),  IOStandard("LVCMOS33")),  # SW2
    ("user_btn", 1, Pins("N2"),  IOStandard("LVCMOS33")),  # SW3

    # 8.1. DIP Switch
    ("user_dip_btn", 0, Pins("AA15"), IOStandard("LVCMOS33")),
    ("user_dip_btn", 1, Pins("AB16"), IOStandard("LVCMOS33")),
    ("user_dip_btn", 1, Pins("W16"),  IOStandard("LVCMOS33")),

    # Figure 8.1 UART Topology
    ("serial", 0,
        Subsignal("rx", Pins("E22"), IOStandard("LVCMOS33")),
        Subsignal("tx", Pins("D22"), IOStandard("LVCMOS33")),
    ),

    # 7.1. General Purpose LEDs (Inverted)
    ("user_led", 0, Pins("M6"), IOStandard("LVCMOS33")),  # Bank 6 Green
    ("user_led", 1, Pins("M7"), IOStandard("LVCMOS33")),  # Bank 6 Green
    ("user_led", 2, Pins("N6"), IOStandard("LVCMOS33")),  # Bank 6 Green
    ("user_led", 3, Pins("N5"), IOStandard("LVCMOS33")),  # Bank 6 Green

    ("rgb_led", 0,
        Subsignal("r", Pins("P2")), # Bank 6 LED4 Red
        Subsignal("g", Pins("P1")), # Bank 6 LED4 Green
        Subsignal("b", Pins("P3")), # Bank 6 LED4 Blue
        IOStandard("LVCMOS33")
    ),
    ("rgb_led", 1,
        Subsignal("r", Pins("R3")), # Bank 6 LED5 Red
        Subsignal("g", Pins("R4")), # Bank 6 LED5 Green
        Subsignal("b", Pins("P4")), # Bank 6 LED5 Blue
        IOStandard("LVCMOS33")
    ),

    ("spiflash", 0,
        Subsignal("cs_n", Pins("F17")),
        Subsignal("clk",  Pins("F15")),
        Subsignal("mosi", Pins("E18")),
        Subsignal("miso", Pins("C21")),
        Subsignal("wp",   Pins("C22")),
        Subsignal("hold", Pins("E16")),
        IOStandard("LVCMOS33")
    ),

    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("F17")),
        Subsignal("clk",  Pins("F15")),
        Subsignal("dq",   Pins("E18 C21 C22 E16")),
        IOStandard("LVCMOS33")
    ),

    # HyperRAM
    ("hyperram", 0,
        Subsignal("dq",    Pins("V18 W19 AB19 AB20 AB21 AB18 AA17 W18"), IOStandard("LVCMOS18H")),
        Subsignal("rwds",  Pins("V19"),  IOStandard("LVCMOS18H")),
        Subsignal("cs_n",  Pins("AA18"), IOStandard("LVCMOS18H")),
        Subsignal("rst_n", Pins("AB17"), IOStandard("LVCMOS18H")),
        Subsignal("clk",   Pins("Y19"),  IOStandard("LVDS")),
        # Subsignal("clk_n", Pins("Y18"), IOStandard("LVDS")),
        Misc("SLEWRATE=FAST")
    ),
    ("hyperram", 1,
        Subsignal("dq",    Pins("V22 AA20 V21 U21 U20 Y22 AA22 AA21"), IOStandard("LVCMOS18H")),
        Subsignal("rwds",  Pins("Y21"),  IOStandard("LVCMOS18H")),
        Subsignal("cs_n",  Pins("AA19"), IOStandard("LVCMOS18H")),
        Subsignal("rst_n", Pins("U18"),  IOStandard("LVCMOS18H")),
        Subsignal("clk",   Pins("W22"),  IOStandard("LVDS")),
        # Subsignal("clk_n", Pins("W21"), IOStandard("LVDS")),
        Misc("SLEWRATE=FAST")
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    # Table 6.2 PMOD Header
    # PMOD signal number:
    #          1  2  3   4   7  8  9  10
    ("PMOD0", "L6 L8 L10 K10 J6 H6 H7 H8"),
    ("PMOD1", "L1 K2 K3  J1  L2 M1 M2 K1"),
    ("PMOD2", "L4 H1 G5  J9  L3 J2 H4 G7"),
    ("PMOD3", "J7 K6 H5  K4  K8 J8 L9 K9"),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticeNexusPlatform):
    default_clk_name   = "clk24"
    default_clk_period = 1e9/24e6

    def __init__(self, device="LFCPNX", toolchain="radiant", **kwargs):
        assert device in ["LFCPNX"]
        LatticeNexusPlatform.__init__(self, device + "-100-9BBG484I", _io, _connectors, toolchain=toolchain, **kwargs)
        # SPI Pins may be used as General IO Pins (see FPGA-AN-02048 4.1.7)
        self.add_platform_command("ldc_set_sysconfig {{MASTER_SPI_PORT=DISABLE}}")
        # Evaluation mode (with free license)
        self.toolchain.set_prj_strategy_opts({"bit_ip_eval": "true"})

    def create_programmer(self):
        return OpenFPGALoader()

    def do_finalize(self, fragment):
        LatticeNexusPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk24", loose=True), 1e9/24e6)
