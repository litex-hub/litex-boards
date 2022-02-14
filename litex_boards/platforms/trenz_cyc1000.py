#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Jakub Cabal <jakubcabal@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.altera import AlteraPlatform
from litex.build.altera.programmer import USBBlaster

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk12", 0, Pins("M2"),  IOStandard("3.3-V LVTTL")),

    # Leds
    ("user_led", 0, Pins("M6"), IOStandard("3.3-V LVTTL")),
    ("user_led", 1, Pins("T4"), IOStandard("3.3-V LVTTL")),
    ("user_led", 2, Pins("T3"), IOStandard("3.3-V LVTTL")),
    ("user_led", 3, Pins("R3"), IOStandard("3.3-V LVTTL")),
    ("user_led", 4, Pins("T2"), IOStandard("3.3-V LVTTL")),
    ("user_led", 5, Pins("R4"), IOStandard("3.3-V LVTTL")),
    ("user_led", 6, Pins("N5"), IOStandard("3.3-V LVTTL")),
    ("user_led", 7, Pins("N3"), IOStandard("3.3-V LVTTL")),

    # Button
    ("key", 0, Pins("N6"), IOStandard("3.3-V LVTTL")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("T7"), IOStandard("3.3-V LVTTL")),
        Subsignal("rx", Pins("R7"), IOStandard("3.3-V LVTTL")),
    ),
     # SDR SDRAM
    ("sdram_clock", 0, Pins("B14"), IOStandard("3.3-V LVTTL")),
    ("sdram", 0,
        Subsignal("a", Pins(
            "A3 B5 B4 B3 C3 D3 E6 E7",
            "D6 D8 A5 E8 A2 C6")),
        Subsignal("ba",    Pins("A4 B6")),
        Subsignal("cs_n",  Pins("A6")),
        Subsignal("cke",   Pins("F8")),
        Subsignal("ras_n", Pins("B7")),
        Subsignal("cas_n", Pins("C8")),
        Subsignal("we_n",  Pins("A7")),
        Subsignal("dq", Pins(
            "B10 A10 B11 A11 A12 D9 B12 C9",
            "D11 E11 A15 E9 D14 F9 C14 A14")),
        Subsignal("dm", Pins("B13 D12")),
        IOStandard("3.3-V LVTTL")
    ),

    # ECPQ
    ("epcq", 0,
        Subsignal("data0", Pins("H2")),
        Subsignal("dclk",  Pins("H1")),
        Subsignal("ncs0",  Pins("D2")),
        Subsignal("asd0",  Pins("C1")),
        IOStandard("3.3-V LVTTL")
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name   = "clk12"
    default_clk_period = 1e9/12e6

    def __init__(self, toolchain="quartus"):
        AlteraPlatform.__init__(self, "10CL025YU256C8G", _io, toolchain=toolchain)

    def create_programmer(self):
        return USBBlaster(cable_name="Arrow-USB-Blaster")

    def do_finalize(self, fragment):
        AlteraPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk12", loose=True), 1e9/12e6)
        # Generate PLL clock in STA
        self.toolchain.additional_sdc_commands.append("derive_pll_clocks")
        # Calculates clock uncertainties
        self.toolchain.additional_sdc_commands.append("derive_clock_uncertainty")
