#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Icenowy Zheng <uwu@icenowy.me>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.altera import AlteraPlatform
from litex.build.openfpgaloader import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk
    ("clk100", 0, Pins("AP20"), IOStandard("1.8 V")),
    # TODO: differiential clocks for transceivers

    # LEDs
    ("user_led", 0, Pins("AM17"), IOStandard("1.8 V")),
    ("user_led", 1, Pins("AH18"), IOStandard("1.8 V")),
    ("user_led", 2, Pins("AJ18"), IOStandard("1.8 V")),
    ("user_led", 3, Pins("AH17"), IOStandard("1.8 V")),
    ("user_led", 4, Pins("AJ16"), IOStandard("1.8 V")),
    ("user_led", 5, Pins("AK17"), IOStandard("1.8 V")),
    ("user_led", 6, Pins("AK16"), IOStandard("1.8 V")),
    ("user_led", 7, Pins("AK18"), IOStandard("1.8 V")),
    ("user_led", 8, Pins("AL18"), IOStandard("1.8 V")),

    # I2C busses
    ("i2c", 0,
        Subsignal("scl", Pins("K20")),
        Subsignal("sda", Pins("L20")),
        IOStandard("1.8 V")
    ), # Bus for accessing the QSFP retimer
    ("i2c", 1,
        Subsignal("scl", Pins("J23")),
        Subsignal("sda", Pins("K21")),
        IOStandard("1.8 V")
    ), # Bus for arbitrary onboard accessories

    # TODO: DDR4 and transceivers
]

# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self, variant="pcie", toolchain="quartus"):
        self.variant = variant
        AlteraPlatform.__init__(self, "10AXF40GAE", _io, toolchain=toolchain)
        self.add_platform_command("set_global_assignment -name RESERVE_DATA0_AFTER_CONFIGURATION \"USE AS REGULAR IO\"")

    def create_programmer(self):
        return OpenFPGALoader(cable="ft232")

    def do_finalize(self, fragment):
        AlteraPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100", loose=True), 1e9/100e6)
