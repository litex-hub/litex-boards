#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Hans Baier <hansfbaier@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

# iCESugar FPGA: https://www.aliexpress.com/item/4001201771358.html

from litex.build.generic_platform import *
from litex.build.lattice import LatticePlatform
from litex.build.lattice.programmer import IceSugarProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk12", 0, Pins("35"), IOStandard("LVCMOS33")),

    # Leds R / G / B
    ("user_led_n",    0, Pins("40"), IOStandard("LVCMOS33")),
    ("user_led_n",    1, Pins("39"), IOStandard("LVCMOS33")),
    ("user_led_n",    2, Pins("41"), IOStandard("LVCMOS33")),

    # RGB led, active-low, alias for Leds
    ("rgb_led", 0,
        Subsignal("r", Pins("40")),
        Subsignal("g", Pins("39")),
        Subsignal("b", Pins("31")),
        IOStandard("LVCMOS33"),
    ),

    # Switches / jumper-attached to PMOD4
    ("user_sw", 0, Pins("18"), IOStandard("LVCMOS18")),
    ("user_sw", 1, Pins("19"), IOStandard("LVCMOS18")),
    ("user_sw", 2, Pins("20"), IOStandard("LVCMOS18")),
    ("user_sw", 3, Pins("21"), IOStandard("LVCMOS18")),

    # Serial
    ("serial", 0,
        Subsignal("rx", Pins("4")),
        Subsignal("tx", Pins("6"), Misc("PULLUP")),
        IOStandard("LVCMOS33")
    ),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("16"), IOStandard("LVCMOS33")),
        Subsignal("clk",  Pins("15"), IOStandard("LVCMOS33")),
        Subsignal("miso", Pins("17"), IOStandard("LVCMOS33")),
        Subsignal("mosi", Pins("14"), IOStandard("LVCMOS33")),
    ),

    # USB
    ("usb", 0,
        Subsignal("d_p", Pins("10")),
        Subsignal("d_n", Pins("9")),
        Subsignal("pullup", Pins("11")),
        IOStandard("LVCMOS33")
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    # Pin order similar to iCEBreaker to allow PMODs reuse.
    ("PMOD1", "10  6  3 48  9  4  2 47"),
    ("PMOD2", "46 44 42 37 45 43 38 36"),
    ("PMOD3", "34 31 27 25 32 28 26 23"),
    ("J7",    "48 - 3 47 - 2"), # Numbering similar to PMODS: 0: Marked pin.
]

# PMODS --------------------------------------------------------------------------------------------

def led_pmod_io_v11(pmod, offset=0):
    return [
        # LED PMOD: https://www.aliexpress.com/item/1005001504777342.html
        # Contrary to the supplied schematic, the two nibbles seem to be swapped on the board.
        ("user_led_n", offset + 0,  Pins(f"{pmod}:4"), IOStandard("LVCMOS33")),
        ("user_led_n", offset + 1,  Pins(f"{pmod}:5"), IOStandard("LVCMOS33")),
        ("user_led_n", offset + 2,  Pins(f"{pmod}:6"), IOStandard("LVCMOS33")),
        ("user_led_n", offset + 3,  Pins(f"{pmod}:7"), IOStandard("LVCMOS33")),
        ("user_led_n", offset + 4,  Pins(f"{pmod}:0"), IOStandard("LVCMOS33")),
        ("user_led_n", offset + 5,  Pins(f"{pmod}:1"), IOStandard("LVCMOS33")),
        ("user_led_n", offset + 6,  Pins(f"{pmod}:2"), IOStandard("LVCMOS33")),
        ("user_led_n", offset + 7,  Pins(f"{pmod}:3"), IOStandard("LVCMOS33")),
    ]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticePlatform):
    default_clk_name   = "clk12"
    default_clk_period = 1e9/12e6

    def __init__(self, toolchain="icestorm"):
        LatticePlatform.__init__(self, "ice40-up5k-sg48", _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        return IceSugarProgrammer()

    def do_finalize(self, fragment):
        LatticePlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk12", loose=True), 1e9/12e6)
