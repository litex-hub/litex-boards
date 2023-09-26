#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022-2023 Icenowy Zheng <uwu@icenowy.me>
# Copyright (c) 2022 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.build.generic_platform import *
from litex.build.gowin.platform import GowinPlatform
from litex.build.gowin.programmer import GowinProgrammer
from litex.build.openfpgaloader import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst.
    ("clk50",  0, Pins("P16"), IOStandard("LVCMOS33")),
    ("rst",    0, Pins("U4"),  IOStandard("LVCMOS15")),

    # Serial.
    ("serial", 0,
        Subsignal("rx", Pins("P15")),
        Subsignal("tx", Pins("N16")),
        IOStandard("LVCMOS33")
    ),

    # Leds
    ("led_n", 0,  Pins("J14"), IOStandard("LVCMOS33")),
    ("led_n", 1,  Pins("R26"), IOStandard("LVCMOS33")),
    ("led_n", 2,  Pins("L20"), IOStandard("LVCMOS33")),
    ("led_n", 3,  Pins("M25"), IOStandard("LVCMOS33")),
    ("led_n", 4,  Pins("N21"), IOStandard("LVCMOS33")),
    ("led_n", 5,  Pins("N23"), IOStandard("LVCMOS33")),

    # RGMII Ethernet
    ("eth_clocks", 0,
        Subsignal("tx", Pins("H24")),
        Subsignal("rx", Pins("C23")),
        IOStandard("LVCMOS33")
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("E17")),
        Subsignal("mdio",    Pins("K22")),
        Subsignal("mdc",     Pins("K23")),
        Subsignal("rx_ctl",  Pins("C22")),
        Subsignal("rx_data", Pins("B26 C26 D26 E26")),
        Subsignal("tx_ctl",  Pins("J24")),
        Subsignal("tx_data", Pins("K21 J21 L19 K18")),
        IOStandard("LVCMOS33"),
    ),
    ("ephy_clk", 0, Pins("E18"), IOStandard("LVCMOS33")),

    ("sdram_clock", 0, Pins("AC26"), IOStandard("LVCMOS33")),
    ("sdram", 0,
        Subsignal("a",   Pins(
            "V17 U15 V16 U16 T23 T25 R25 P25",
            "W23 V23 W21 U24 U25")),
        Subsignal("dq",  Pins(
            "V22  U22  W19  V19  Y20 W20 V26 U26",
            "AB25 AB26 AA25 AA24 Y26 Y25 W26 W25")),
        Subsignal("ba",    Pins("P21 Y21")),
        Subsignal("cas_n", Pins("P24")),
        Subsignal("cs_n",  Pins("U14")),
        Subsignal("ras_n", Pins("P23")),
        Subsignal("we_n",  Pins("R23")),
        IOStandard("LVCMOS33"),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
        # TODO
]

# Platform -----------------------------------------------------------------------------------------

class Platform(GowinPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self, dock="standard", toolchain="gowin"):
        GowinPlatform.__init__(self, "GW5AST-LV138FPG676AES", _io, _connectors, toolchain=toolchain, devicename="GW5AST-138B")

        self.toolchain.options["use_sspi_as_gpio"] = 1
        self.toolchain.options["use_cpu_as_gpio"]  = 1
        self.toolchain.options["rw_check_on_ram"]  = 1
        self.toolchain.options["bit_security"]     = 0
        self.toolchain.options["bit_encrypt"]      = 0
        self.toolchain.options["bit_compress"]     = 0

    def create_programmer(self, kit="openfpgaloader"):
        return OpenFPGALoader(cable="ft2232")

    def do_finalize(self, fragment):
        GowinPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
