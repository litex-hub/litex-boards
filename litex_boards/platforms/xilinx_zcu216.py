#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Ilia Sergachev <ilia@sergachev.ch>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxUSPPlatform, VivadoProgrammer


# IOs ----------------------------------------------------------------------------------------------

_io = [
    ("clk100", 0,
        Subsignal("p", Pins("G12"), IOStandard("LVDS_25")),
        Subsignal("n", Pins("G11"), IOStandard("LVDS_25"))
    ),
    ("clk300", 0,
        Subsignal("p", Pins("AR20"), IOStandard("DIFF_SSTL12")),
        Subsignal("n", Pins("AR19"), IOStandard("DIFF_SSTL12"))
    ),
    ("clk300", 1,
        Subsignal("p", Pins("G17"), IOStandard("DIFF_SSTL12")),
        Subsignal("n", Pins("F17"), IOStandard("DIFF_SSTL12"))
    ),
    ("cpu_reset", 0, Pins("L14"), IOStandard("LVCMOS18")),

    ("user_led", 0, Pins("C13"), IOStandard("LVCMOS18")),
    ("user_led", 1, Pins("D14"), IOStandard("LVCMOS18")),
    ("user_led", 2, Pins("D12"), IOStandard("LVCMOS18")),
    ("user_led", 3, Pins("D13"), IOStandard("LVCMOS18")),
    ("user_led", 4, Pins("AW18"), IOStandard("LVCMOS12")),
    ("user_led", 5, Pins("AV18"), IOStandard("LVCMOS12")),
    ("user_led", 6, Pins("BA19"), IOStandard("LVCMOS12")),
    ("user_led", 7, Pins("AP21"), IOStandard("LVCMOS12")),

    ("rgb_led", 0,
        Subsignal("r", Pins("AN14"), IOStandard("LVCMOS12")),
        Subsignal("g", Pins("C13"),  IOStandard("LVCMOS18")),
        Subsignal("b", Pins("B26"),  IOStandard("LVCMOS12")),
    ),
    ("rgb_led", 1,
        Subsignal("r", Pins("AP16"), IOStandard("LVCMOS12")),
        Subsignal("g", Pins("D14"),  IOStandard("LVCMOS18")),
        Subsignal("b", Pins("E24"),  IOStandard("LVCMOS12")),
    ),
    ("rgb_led", 2,
        Subsignal("r", Pins("AP14"), IOStandard("LVCMOS12")),
        Subsignal("g", Pins("D12"),  IOStandard("LVCMOS18")),
        Subsignal("b", Pins("G26"),  IOStandard("LVCMOS12")),
    ),
    ("rgb_led", 3,
        Subsignal("r", Pins("AU16"), IOStandard("LVCMOS12")),
        Subsignal("g", Pins("D13"),  IOStandard("LVCMOS18")),
        Subsignal("b", Pins("J23"),  IOStandard("LVCMOS12")),
    ),
    ("rgb_led", 4,
        Subsignal("r", Pins("AW12"), IOStandard("LVCMOS12")),
        Subsignal("g", Pins("AW18"), IOStandard("LVCMOS12")),
        Subsignal("b", Pins("L24"),  IOStandard("LVCMOS12")),
    ),
    ("rgb_led", 5,
        Subsignal("r", Pins("AY16"), IOStandard("LVCMOS12")),
        Subsignal("g", Pins("AV18"), IOStandard("LVCMOS12")),
        Subsignal("b", Pins("P21"),  IOStandard("LVCMOS12")),
    ),
    ("rgb_led", 6,
        Subsignal("r", Pins("BB12"), IOStandard("LVCMOS12")),
        Subsignal("g", Pins("BA19"), IOStandard("LVCMOS12")),
        Subsignal("b", Pins("AV21"), IOStandard("LVCMOS12")),
    ),
    ("rgb_led", 7,
        Subsignal("r", Pins("E25"),  IOStandard("LVCMOS12")),
        Subsignal("g", Pins("AP21"), IOStandard("LVCMOS12")),
        Subsignal("b", Pins("AR21"), IOStandard("LVCMOS12")),
    ),

    ("user_dip", 0, Pins("AY10"), IOStandard("LVCMOS18")),
    ("user_dip", 1, Pins("AY11"), IOStandard("LVCMOS18")),
    ("user_dip", 2, Pins("BA9"),  IOStandard("LVCMOS18")),
    ("user_dip", 3, Pins("AY9"),  IOStandard("LVCMOS18")),
    ("user_dip", 4, Pins("BB9"),  IOStandard("LVCMOS18")),
    ("user_dip", 5, Pins("BA10"), IOStandard("LVCMOS18")),
    ("user_dip", 6, Pins("BB10"), IOStandard("LVCMOS18")),
    ("user_dip", 7, Pins("BB11"), IOStandard("LVCMOS18")),

    ("user_btn_c", 0, Pins("K11"), IOStandard("LVCMOS18")),
    ("user_btn_n", 0, Pins("J11"), IOStandard("LVCMOS18")),
    ("user_btn_s", 0, Pins("H10"), IOStandard("LVCMOS18")),
    ("user_btn_w", 0, Pins("K12"), IOStandard("LVCMOS18")),
    ("user_btn_e", 0, Pins("J12"), IOStandard("LVCMOS18")),

    ("serial", 0,
        Subsignal("tx", Pins("B10")),
        Subsignal("rx", Pins("C10")),
        IOStandard("LVCMOS18"),
    ),

    ("i2c", 0,
        Subsignal("scl", Pins("B11")),
        Subsignal("sda", Pins("C11")),
        IOStandard("LVCMOS18"),
    ),
    ("i2c", 1,
        Subsignal("scl", Pins("C9")),
        Subsignal("sda", Pins("D9")),
        IOStandard("LVCMOS18"),
    ),

    ("mgt_refclk", 0,
        Subsignal("p", Pins("H34")),
        Subsignal("n", Pins("H35")),
    ),

    ("sfp", 0,
        Subsignal("txp", Pins("V38")),
        Subsignal("txn", Pins("V39")),
        Subsignal("rxp", Pins("AC41")),
        Subsignal("rxn", Pins("AC42")),
    ),
    ("sfp_tx", 0,
        Subsignal("p", Pins("V38")),
        Subsignal("n", Pins("V39")),
    ),
    ("sfp_rx", 0,
        Subsignal("p", Pins("AC41")),
        Subsignal("n", Pins("AC42")),
    ),
    ("sfp", 1,
        Subsignal("txp", Pins("U36")),
        Subsignal("txn", Pins("U37")),
        Subsignal("rxp", Pins("AB39")),
        Subsignal("rxn", Pins("AB40")),
    ),
    ("sfp_tx", 1,
        Subsignal("p", Pins("U36")),
        Subsignal("n", Pins("U37")),
    ),
    ("sfp_rx", 1,
        Subsignal("p", Pins("AB39")),
        Subsignal("n", Pins("AB40")),
    ),
    ("sfp", 2,
        Subsignal("txp", Pins("P38")),
        Subsignal("txn", Pins("P39")),
        Subsignal("rxp", Pins("W41")),
        Subsignal("rxn", Pins("W42")),
    ),
    ("sfp_tx", 2,
        Subsignal("p", Pins("P38")),
        Subsignal("n", Pins("P39")),
    ),
    ("sfp_rx", 2,
        Subsignal("p", Pins("W41")),
        Subsignal("n", Pins("W42")),
    ),
    ("sfp", 3,
        Subsignal("txp", Pins("N36")),
        Subsignal("txn", Pins("N37")),
        Subsignal("rxp", Pins("U41")),
        Subsignal("rxn", Pins("U42")),
    ),
    ("sfp_tx", 3,
        Subsignal("p", Pins("N36")),
        Subsignal("n", Pins("N37")),
    ),
    ("sfp_rx", 3,
        Subsignal("p", Pins("U41")),
        Subsignal("n", Pins("U42")),
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxUSPPlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9 / 100e6

    def __init__(self, toolchain="vivado"):
        XilinxUSPPlatform.__init__(self, "xczu49dr-ffvf1760-2-e", _io, toolchain=toolchain)
        self.toolchain.bitstream_commands = \
            ["set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]", ]
        self.default_clk_freq = 1e9 / self.default_clk_period

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment, *args, **kwargs):
        XilinxUSPPlatform.do_finalize(self, fragment, *args, **kwargs)
        self.add_period_constraint(self.lookup_request(self.default_clk_name, loose=True), self.default_clk_period)
