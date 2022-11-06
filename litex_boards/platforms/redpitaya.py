#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Gwenhael Goavec-Merou <gwenhael.goavec-merou@trabucayre.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform, VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Leds
    ("user_led", 0, Pins("F16"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("F17"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("G15"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("H15"), IOStandard("LVCMOS33")),
    ("user_led", 4, Pins("K14"), IOStandard("LVCMOS33")),
    ("user_led", 5, Pins("G14"), IOStandard("LVCMOS33")),
    ("user_led", 6, Pins("J15"), IOStandard("LVCMOS33")),
    ("user_led", 7, Pins("J14"), IOStandard("LVCMOS33")),

    ("dac", 0,
        Subsignal("data",
            Pins("M19 M20 L19 L20 K19 J19 J20 H20 G19 G20 F19 F20 D20 D19"),
            Drive(4), Misc("SLEW SLOW")),
        Subsignal("wrt", Pins("M17"), Drive(8), Misc("SLEW FAST")),
        Subsignal("sel", Pins("N16"), Drive(8), Misc("SLEW FAST")),
        Subsignal("clk", Pins("M18"), Drive(8), Misc("SLEW FAST")),
        Subsignal("rst", Pins("N15"), Drive(8), Misc("SLEW FAST")),
        IOStandard("LVCMOS33"),
    ),

    ("pwm_dac", 0, Pins("T10"), IOStandard("LVCMOS18"),
        Drive(8), Misc("SLEW FAST")),
    ("pwm_dac", 1, Pins("T11"), IOStandard("LVCMOS18"),
        Drive(8), Misc("SLEW FAST")),
    ("pwm_dac", 2, Pins("P15"), IOStandard("LVCMOS18"),
        Drive(8), Misc("SLEW FAST")),
    ("pwm_dac", 3, Pins("U13"), IOStandard("LVCMOS18"),
        Drive(8), Misc("SLEW FAST")),

    ("daisy", 0,
        Subsignal("io0_p", Pins("T12")),
        Subsignal("io0_n", Pins("U12")),
        Subsignal("io1_p", Pins("U14")),
        Subsignal("io1_n", Pins("U15")),
        IOStandard("DIFF_HSTL_I_18"),
    ),

    ("daisy", 1,
        Subsignal("io0_p", Pins("P14")),
        Subsignal("io0_n", Pins("R14")),
        Subsignal("io1_p", Pins("N18")),
        Subsignal("io1_n", Pins("P19")),
        IOStandard("DIFF_HSTL_I_18"),
    ),

]

_io_14 = [
    # Clk / Rst
    ("clk125", 0,
        Subsignal("p", Pins("U18")),
        Subsignal("n", Pins("U19")),
        IOStandard("DIFF_HSTL_I_18"),
    ),

    ("adc", 0,
        Subsignal("data_a",
            Pins("Y17 W16 Y16 W15 W14 Y14 W13 V12 V13 T14 T15 V15 T16 V16")),
        Subsignal("data_b",
            Pins("R18 P16 P18 N17 R19 T20 T19 U20 V20 W20 W19 Y19 W18 Y18")),
        Subsignal("cdcs", Pins("V18")),
        IOStandard("LVCMOS18"),
    ),
]

_io_16 = [
    # Clk / Rst
    ("clk122", 0,
        Subsignal("p", Pins("U18")),
        Subsignal("n", Pins("U19")),
        IOStandard("DIFF_HSTL_I_18"),
    ),

    ("adc", 0,
        Subsignal("data_a",
            Pins("V17 U17 Y17 W16 Y16 W15 W14 Y14 W13 V12 V13 T14 T15 V15 T16 V16")),
        Subsignal("data_b",
            Pins("T17 R16 R18 P16 P18 N17 R19 T20 T19 U20 V20 W20 W19 Y19 W18 Y18")),
        Subsignal("cdcs", Pins("V18")),
        IOStandard("LVCMOS18"),
    ),
]

_ps7_io = [
    # PS7
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

_uart_io = [
    ("usb_uart", 0,
        Subsignal("tx", Pins("E1:3")),
        Subsignal("rx", Pins("E1:4")),
        IOStandard("LVCMOS33")
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("E1", "- - G17 G18 H16 H17 J18 H18 K17 K18 L14 L15 L16 L17 K16 J16 M14 M15 - - - - - - - -"),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):

    def __init__(self, board="redpitaya14", toolchain="vivado"):
        if board == "redpitaya14":
            device = "xc7z010clg400-1"
            extension = _io_14
            self.default_clk_name = "clk125"
            self.default_clk_freq = 125e6
        else:
            device = "xc7z020clg400-1"
            extension = _io_16
            self.default_clk_name   = "clk122"
            self.default_clk_freq   = 122e6

        self.default_clk_period = 1e9/self.default_clk_freq

        Xilinx7SeriesPlatform.__init__(self, device, _io,  _connectors, toolchain=toolchain)
        self.add_extension(extension)
        self.add_extension(_ps7_io)
        self.add_extension(_uart_io)

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request(self.default_clk_name, loose=True),
                                   self.default_clk_period)
