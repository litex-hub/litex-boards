#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Yonggang Liu <ggang.liu@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform, VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk100",    0, Pins("U18"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led", 0, Pins("M14"),  IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("M15"),  IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("K16"),  IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("J18"),  IOStandard("LVCMOS33")),

    # Buttons
    ("user_btn", 0, Pins("N15"), IOStandard("LVCMOS33")),
    ("user_btn", 1, Pins("N16"), IOStandard("LVCMOS33")),
    ("user_btn", 2, Pins("R17"), IOStandard("LVCMOS33")),
    ("user_btn", 3, Pins("T17"), IOStandard("LVCMOS33")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("W19"), IOStandard("LVCMOS33")),
        Subsignal("rx", Pins("W18"), IOStandard("LVCMOS33")),
    ),
]

_ps7_io = [
    # PS7
    ("ps7_clk",   0, Pins("E7")),
    ("ps7_porb",  0, Pins(1)),
    ("ps7_srstb", 0, Pins(1)),
    ("ps7_mio",   0, Pins(54)),
    ("ps7_ddram", 0,
        Subsignal("addr",    Pins(15)),
        Subsignal("ba",      Pins(3)),
        Subsignal("cas_n",   Pins(1)),
        Subsignal("ck_n",    Pins(1)),
        Subsignal("ck_p",    Pins(1)),
        Subsignal("cke",     Pins(1)),
        Subsignal("cs_n",    Pins(1)),
        Subsignal("dm",      Pins(4)),
        Subsignal("dq",      Pins(32)),
        Subsignal("dqs_n",   Pins(4)),
        Subsignal("dqs_p",   Pins(4)),
        Subsignal("odt",     Pins(1)),
        Subsignal("ras_n",   Pins(1)),
        Subsignal("reset_n", Pins(1)),
        Subsignal("we_n",    Pins(1)),
        Subsignal("vrn",     Pins(1)),
        Subsignal("vrp",     Pins(1)),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("pmodb",    "B12 B12 C12"),
    ("pmodhdmi", "N18 P19 V20 W20 T20 U20 N20 P20 R18 R16 Y18 Y19 V16"),
    ("pmodj10",  "W19 W18 R14 P14 Y17 Y16 W15 V15 Y14 W14 P18 N17 U15 U14 P16 P15 U17 T16 V18 V17 T15 T14 V13 U13 W13 V12 U12 T12 T10 T11 A20 B19 B20 C20"),
    ("pmodj11",  "F17 F16 F20 F19 G20 G19 H18 J18 L20 L19 M20 M19 K18 K17 J19 K19 H20 J20 L17 L16 M18 M17 D20 D19 E19 E18 G18 G17 H17 H16 G15 H15 J14 K14"),
]

# PMODS --------------------------------------------------------------------------------------------

_usb_uart_pmod_io = [
    # USB-UART PMOD on JB:
    # - https://store.digilentinc.com/pmod-usbuart-usb-to-uart-interface/
    ("serial", 0,
        Subsignal("tx", Pins("pmodj10:0")),
        Subsignal("rx", Pins("pmodj10:1")),
        IOStandard("LVCMOS33")
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self):
        Xilinx7SeriesPlatform.__init__(self, "xc7z010clg400-1", _io, _connectors, toolchain="vivado")
        #self.add_extension(_ps7_io)
        #self.add_extension(_usb_uart_pmod_io)

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100", loose=True), 1e9/100e6)
