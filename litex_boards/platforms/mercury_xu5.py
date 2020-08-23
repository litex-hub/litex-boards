#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Antmicro <www.antmicro.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform, VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    ("clk100", 0,
        Subsignal("n", Pins("AD4"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("p", Pins("AD5"), IOStandard("DIFF_SSTL12_DCI")),
    ),

    ("clk100_gtr", 0,
        Subsignal("p", Pins("C21"), IOStandard("DIFF_SSTL12")),
        Subsignal("n", Pins("C22"), IOStandard("DIFF_SSTL12")),
    ),

    ("clk27_gtr", 0,
        Subsignal("p", Pins("A21"), IOStandard("DIFF_SSTL12")),
        Subsignal("n", Pins("A22"), IOStandard("DIFF_SSTL12")),
    ),

    ("clk33", 0, Pins("AD4"), IOStandard("SSTL12")),

    ("cpu_reset", 0, Pins("N19"), IOStandard("LVCMOS33")),

    ("user_led", 0, Pins("H2"),   IOStandard("LVCMOS18")),
    ("user_led", 1, Pins("P9"),   IOStandard("LVCMOS18")),
    ("user_led", 2, Pins("K5"),   IOStandard("LVCMOS18")),

    ("serial", 0,
        Subsignal("rx", Pins("AA10")),  # Module connector A: A60 (Meccury PE1: "IO B" connector 32)
        Subsignal("tx", Pins("AA11")),  # Module connector A: A58 (Meccury PE1: "IO B" connector 31)
        IOStandard("LVCMOS33"),
    ),

    ("i2c", 0,
        Subsignal("scl", Pins("D12")),
        Subsignal("sda", Pins("C12")),
        IOStandard("LVCMOS18")
    ),

    ("ddram", 0,
        Subsignal("a",       Pins(
            "AC4 AC3 AB4 AB3 AB2 AC2 AB1 AC1",
            "AB5 AG4 AH4 AG3 AH3 AE3"),       IOStandard("SSTL12_DCI")),
        Subsignal("we_n",    Pins("AF3"),     IOStandard("SSTL12_DCI")),  # A14
        Subsignal("cas_n",   Pins("AE2"),     IOStandard("SSTL12_DCI")),  # A15
        Subsignal("ras_n",   Pins("AF2"),     IOStandard("SSTL12_DCI")),  # A16
        Subsignal("ba",      Pins("AH1 AF1"), IOStandard("SSTL12_DCI")),
        Subsignal("bg",      Pins("AG1"),     IOStandard("SSTL12_DCI")),
        Subsignal("cs_n",    Pins("AH9"),     IOStandard("SSTL12_DCI")),
        Subsignal("act_n",   Pins("AH2"),     IOStandard("SSTL12_DCI")),
        Subsignal("dm",      Pins("AC9 AG9"), IOStandard("POD12_DCI")),
        Subsignal("dq",      Pins(
            "AB6 AC6 AE9 AE8 AB8 AC8 AB7 AC7",
            "AE5 AF5 AF8 AG8 AH8 AH7 AF7 AF6"), IOStandard("POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_p",   Pins("AD7 AG6"), IOStandard("DIFF_POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_n",   Pins("AE7 AG5"), IOStandard("DIFF_POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("clk_p",   Pins("AD2"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("clk_n",   Pins("AD1"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("cke",     Pins("AH6"), IOStandard("SSTL12_DCI")),
        Subsignal("odt",     Pins("AE4"), IOStandard("SSTL12_DCI")),
        Subsignal("reset_n", Pins("G4"),  IOStandard("LVCMOS18")),
        Misc("SLEW=FAST"),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = []

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self):
        XilinxPlatform.__init__(self, "xczu2eg-sfvc784-1-i", _io, _connectors, toolchain="vivado")

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100",     loose=True), 1e9/100e6)
        self.add_period_constraint(self.lookup_request("clk100_gtr", loose=True), 1e9/100e6)
        self.add_period_constraint(self.lookup_request("clk27_gtr",  loose=True), 1e9/27e6)
        self.add_period_constraint(self.lookup_request("clk33",      loose=True), 1e9/33e6)
        self.add_platform_command("set_property BITSTREAM.CONFIG.OVERTEMPSHUTDOWN ENABLE [current_design]")
        self.add_platform_command("set_property BITSTREAM.CONFIG.UNUSEDPIN PULLNONE [current_design]")
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 64]")
