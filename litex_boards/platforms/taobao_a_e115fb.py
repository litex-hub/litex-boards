#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Icenowy Zheng <uwu@icenowy.me>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.altera import AlteraPlatform
from litex.build.altera.programmer import USBBlaster

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk
    ("clk25", 0, Pins("AB11"), IOStandard("3.3-V LVTTL")),
    ("clk27", 0, Pins("A11"),  IOStandard("3.3-V LVTTL")),

    # Rst
    ("cpu_reset_n", 0, Pins("N21"), IOStandard("1.8-V")), # N21

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("V3"),  IOStandard("3.3-V LVTTL")), # GPIOs close to voltage selector
        Subsignal("rx", Pins("AA1"), IOStandard("3.3-V LVTTL"))
    ),

    # LEDs
    ("user_led_n", 0, Pins("A5"), IOStandard("3.3-V LVTTL")), # D3
    ("user_led_n", 1, Pins("B5"), IOStandard("3.3-V LVTTL")), # D4
    ("user_led_n", 2, Pins("C4"), IOStandard("3.3-V LVTTL")), # D5
    ("user_led_n", 3, Pins("C3"), IOStandard("3.3-V LVTTL")), # D6

    # Buttons
    ("user_btn_n", 0, Pins("T1"),  IOStandard("3.3-V LVTTL")),  # K3
    ("user_btn_n", 1, Pins("N22"), IOStandard("3.3-V LVTTL")), # K4
]

# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name   = "clk25"
    default_clk_period = 1e9/25e6

    def __init__(self, toolchain="quartus"):
        AlteraPlatform.__init__(self, "EP4CE115F23I7", _io, toolchain=toolchain)

    def create_programmer(self):
        return USBBlaster()

    def do_finalize(self, fragment):
        AlteraPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk25", loose=True), 1e9/25e6)
        self.add_period_constraint(self.lookup_request("clk27", loose=True), 1e9/27e6)
