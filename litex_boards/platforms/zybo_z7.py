#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019-2020 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform, VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # clk125
    ("clk125", 0, Pins("L16"), IOStandard("LVCMOS33")),

    # user led
    ("user_led", 0, Pins("M14"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("M15"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("G14"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("D18"), IOStandard("LVCMOS33")),

    # user sw
    ("user_sw", 0, Pins("G15"), IOStandard("LVCMOS33")),
    ("user_sw", 1, Pins("P15"), IOStandard("LVCMOS33")),
    ("user_sw", 2, Pins("W13"), IOStandard("LVCMOS33")),
    ("user_sw", 3, Pins("T16"), IOStandard("LVCMOS33")),

    # user btn
    ("user_btn", 0, Pins("R18"), IOStandard("LVCMOS33")),
    ("user_btn", 1, Pins("P16"), IOStandard("LVCMOS33")),
    ("user_btn", 2, Pins("V16"), IOStandard("LVCMOS33")),
    ("user_btn", 3, Pins("Y16"), IOStandard("LVCMOS33")),

    # serial
    ("serial", 0,
        Subsignal("tx", Pins("T17")),
        Subsignal("rx", Pins("Y17")),
        IOStandard("LVCMOS33")
    ),
]

_ps7_io = [
    # ps7
    ("ps7_clk",   0, Pins(1)),
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

_usb_uart_pmod_io = [
    # USB-UART PMOD on JB:
    # - https://store.digilentinc.com/pmod-usbuart-usb-to-uart-interface/
    ("usb_uart", 0,
        Subsignal("tx", Pins("pmodb:1")),
        Subsignal("rx", Pins("pmodb:2")),
        IOStandard("LVCMOS33")
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("pmoda", "N15 L14 K16 K14 N16 L15 J16 J14"), # XADC
    ("pmodb", "T20 U20 V20 W20 Y18 Y19 W18 W19"),
    ("pmodc", "V15 W15 T11 T10 W14 Y14 T12 U12"),
    ("pmodd", "T14 T15 P14 R14 U14 U15 V17 V18"),
    ("pmode", "V12 W16 J15 H15 V13 U17 T17 Y17"),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "clk128"
    default_clk_period = 1e9/125e6

    def __init__(self):
        XilinxPlatform.__init__(self, "xc7z010-clg400-1", _io,  _connectors, toolchain="vivado")
        self.add_extension(_ps7_io)
        self.add_extension(_usb_uart_pmod_io)

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk125", loose=True), 1e9/125e6)
