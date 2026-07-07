#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.quicklogic import QuickLogicPlatform

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Leds
    ("user_led",   0, Pins("38"), IOStandard("LVCMOS33")), # blue
    ("user_led",   1, Pins("39"), IOStandard("LVCMOS33")), # green
    ("user_led",   2, Pins("34"), IOStandard("LVCMOS33")), # red
    ("rgb_led",    0,
        Subsignal("r", Pins("34")),
        Subsignal("g", Pins("39")),
        Subsignal("b", Pins("38")),
        IOStandard("LVCMOS33"),
    ),

    # Button
    ("user_btn_n", 0, Pins("62"), IOStandard("LVCMOS33")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("8")),
        Subsignal("rx", Pins("9")),
        IOStandard("LVCMOS33"),
    ),

    # SPI
    ("spi", 0,
        Subsignal("cs_n", Pins("11")),
        Subsignal("clk",  Pins("20")),
        Subsignal("mosi", Pins("16")),
        Subsignal("miso", Pins("17")),
        IOStandard("LVCMOS33"),
    ),
    ("spi", 1,
        Subsignal("cs_n", Pins("37")),
        Subsignal("clk",  Pins("40")),
        Subsignal("mosi", Pins("36")),
        Subsignal("miso", Pins("42")),
        IOStandard("LVCMOS33"),
    ),

    # I2C
    ("i2c", 0,
        Subsignal("scl", Pins("4")),
        Subsignal("sda", Pins("5")),
        IOStandard("LVCMOS33"),
    ),
    ("i2c", 1,
        Subsignal("scl", Pins("22")),
        Subsignal("sda", Pins("21")),
        IOStandard("LVCMOS33"),
    ),

    # USB
    ("usb", 0,
        Subsignal("d_p", Pins("10")),
        Subsignal("d_n", Pins("14")),
        IOStandard("LVCMOS33"),
    ),

    # SWD
    ("swd", 0,
        Subsignal("clk", Pins("54")),
        Subsignal("io",  Pins("53")),
        IOStandard("LVCMOS33"),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("J2", "- 28 22 21 37 36 42 40 7 2 4 5"),
    ("J3", "- 8 9 17 16 20 6 55 31 25 47 - - - - 41"),
    ("J8", "27 26 33 32 23 57 56 3 64 62 63 61 59 - - -"),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(QuickLogicPlatform):
    def __init__(self, toolchain="f4pga"):
        QuickLogicPlatform.__init__(self, "ql-eos-s3", _io, _connectors, toolchain=toolchain)
