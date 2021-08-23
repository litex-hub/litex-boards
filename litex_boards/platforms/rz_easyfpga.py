#
# This file is part of LiteX-Boards.
#
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.altera import AlteraPlatform
from litex.build.altera.programmer import USBBlaster

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk
    ("clk50", 0, Pins("23"), IOStandard("3.3-V LVTTL")),

    # Leds
    ("user_led", 0, Pins("84"), IOStandard("3.3-V LVTTL")),
    ("user_led", 1, Pins("85"), IOStandard("3.3-V LVTTL")),
    ("user_led", 2, Pins("86"), IOStandard("3.3-V LVTTL")),
    ("user_led", 3, Pins("87"), IOStandard("3.3-V LVTTL")),

    # Serial
    ("serial", 0,
        # Compatible with cheap FT232 based cables (ex: Gaoominy 6Pin Ftdi Ft232Rl Ft232)
        # GND on JP1 Pin 12.
        Subsignal("tx", Pins("128"), IOStandard("3.3-V LVTTL")),
        Subsignal("rx", Pins("126"), IOStandard("3.3-V LVTTL"))
    ),

    # SDRAM
    ("sdram_clock", 0, Pins("43"), IOStandard("3.3-V LVTTL")),
    ("sdram", 0,
        Subsignal("a", Pins(
            "76 77 80 83 68 67 66 65",
            "64 60 75 59")),
        Subsignal("ba",    Pins("73 74")),
        Subsignal("cs_n",  Pins("72")),
        Subsignal("cke",   Pins("58")),
        Subsignal("ras_n", Pins("71")),
        Subsignal("cas_n", Pins("70")),
        Subsignal("we_n",  Pins("69")),
        Subsignal("dq", Pins(
            "28 30 31 32 33 34 38 39",
            "54 53 52 51 50 49 46 44")),
        Subsignal("dm", Pins("42 55")),
        IOStandard("3.3-V LVTTL")
    ),
]


# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self):
        AlteraPlatform.__init__(self, "EP4CE6E22C8", _io)

    def create_programmer(self):
        return USBBlaster()

    def do_finalize(self, fragment):
        AlteraPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
        # Generate PLL clock in STA
        self.toolchain.additional_sdc_commands.append("derive_pll_clocks")
        # Calculates clock uncertainties
        self.toolchain.additional_sdc_commands.append("derive_clock_uncertainty")
