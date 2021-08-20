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
        Subsignal("tx", Pins("114"), IOStandard("3.3-V LVTTL")),
        Subsignal("rx", Pins("115"),  IOStandard("3.3-V LVTTL"))
    ),

    # SPI Flash (also used for bistream programming, need to use AS mode and set as "input/output" after configuration)
    # no idea why they can't support it in JTAG mode
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("8")),
        Subsignal("clk", Pins("12")),
        Subsignal("dq", Pins("13 6 132 133")),
        IOStandard("3.3-V LVTTL")
    ),
    ("spiflash", 0,
        Subsignal("cs_n", Pins("8")),
        Subsignal("clk", Pins("12")),
        Subsignal("mosi", Pins("13")),
        Subsignal("miso", Pins("6")),
        Subsignal("wp", Pins("132")),
        Subsignal("hold", Pins("133")),
        IOStandard("3.3-V LVTTL"),
    ),

    # set_instance_assignment -name DCLK_PIN OFF -to DCLK
    # set_instance_assignment -name DATA0_PIN OFF -to D0
    # set_instance_assignment -name IO_MAXIMUM_TOGGLE_RATE "0MHz" -to *

    # set_global_assignment -name CYCLONEII_RESERVE_NCEO_AFTER_CONFIGURATION "USE AS REGULAR IO"
    # set_global_assignment -name RESERVE_DATA0_AFTER_CONFIGURATION "USE AS REGULAR IO"
    # set_global_assignment -name RESERVE_DATA1_AFTER_CONFIGURATION "USE AS REGULAR IO"
    # set_global_assignment -name RESERVE_FLASH_NCE_AFTER_CONFIGURATION "USE AS REGULAR IO"
    # set_global_assignment -name RESERVE_DCLK_AFTER_CONFIGURATION "USE AS REGULAR IO"
    # set_global_assignment -name SDC_FILE rz_easyfpga.sdc


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
