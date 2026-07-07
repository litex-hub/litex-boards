#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Alain Lou <alainzlou@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.altera import AlteraPlatform
from litex.build.altera.programmer import USBBlaster

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk
    ("clk50", 0, Pins("23"), IOStandard("3.3-V LVTTL")),
    ("rst_n", 0, Pins("25"), IOStandard("3.3-V LVTTL")),

    # Leds
    ("user_led", 0, Pins("84"), IOStandard("3.3-V LVTTL")),
    ("user_led", 1, Pins("85"), IOStandard("3.3-V LVTTL")),
    ("user_led", 2, Pins("86"), IOStandard("3.3-V LVTTL")),
    ("user_led", 3, Pins("87"), IOStandard("3.3-V LVTTL")),

    # Buttons
    ("user_btn_n", 0, Pins("88"), IOStandard("3.3-V LVTTL")),
    ("user_btn_n", 1, Pins("89"), IOStandard("3.3-V LVTTL")),
    ("user_btn_n", 2, Pins("90"), IOStandard("3.3-V LVTTL")),
    ("user_btn_n", 3, Pins("91"), IOStandard("3.3-V LVTTL")),

    # Serial
    ("serial", 0,
        # Uses the 9 pin serial connector
        Subsignal("tx", Pins("114"), IOStandard("3.3-V LVTTL")),
        Subsignal("rx", Pins("115"), IOStandard("3.3-V LVTTL"))
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

    # VGA
    ("vga", 0,
        Subsignal("r",  Pins("106")),
        Subsignal("g",  Pins("105")),
        Subsignal("b",  Pins("104")),
        Subsignal("hs", Pins("101")),
        Subsignal("vs", Pins("103")),
        IOStandard("3.3-V LVTTL"),
    ),

    # 7-Segment Display
    ("seven_seg", 0, Pins("128 121 125 129 132 126 124 127"), IOStandard("3.3-V LVTTL")),
    ("seven_seg_ctrl_n", 0, Pins("133 135 136 137"), IOStandard("3.3-V LVTTL")),

    # PS/2
    ("ps2", 0,
        Subsignal("clk", Pins("119")),
        Subsignal("dat", Pins("120")),
        IOStandard("3.3-V LVTTL"),
    ),

    # I2C
    ("i2c", 0,
        Subsignal("scl", Pins("112")),
        Subsignal("sda", Pins("113")),
        IOStandard("3.3-V LVTTL"),
    ),
    ("i2c", 1,
        Subsignal("scl", Pins("99")),
        Subsignal("sda", Pins("98")),
        IOStandard("3.3-V LVTTL"),
    ),

    # Buzzer
    ("buzzer_n", 0, Pins("110"), IOStandard("3.3-V LVTTL")),

    # LCD
    ("lcd_hd44780", 0,
        Subsignal("rs", Pins("141")),
        Subsignal("rw", Pins("138")),
        Subsignal("e",  Pins("143")),
        Subsignal("d",  Pins("142 1 144 3 2 10 7 11")),
        IOStandard("3.3-V LVTTL"),
    ),

    # IR Receiver
    ("cir", 0,
        Subsignal("rx", Pins("100")),
        IOStandard("3.3-V LVTTL"),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("GPIO0",
        "- - 11 7 2 144 142 138 136 133 129 127 125 121 119 114 112 110 - "
        "- - 24 10 3 1 143 141 137 135 132 128 126 124 120 115 113 111 - "
    ),
    ("GPIO1",
        "- - 106 105 104 103 101 100 99 98 91 90 89 88 87 86 85 84 - -"
    ),
    ("GPIO2",
        "30 32 34 39 43 46 50 52 54 58 60 65 67 71 73 75 77 83 - - - "
        "28 31 33 38 42 44 51 53 55 59 64 66 68 70 72 74 76 80 - - -"
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self, toolchain="quartus"):
        AlteraPlatform.__init__(self, "EP4CE6E22C8", _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        return USBBlaster()

    def do_finalize(self, fragment):
        AlteraPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
