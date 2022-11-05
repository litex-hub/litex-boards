#
# This file is part of LiteX-Boards.
# Copyright (c) 2021 Omkar Bhilare <ombhilare999@gmail.com>
# Copyright (c) 2021 Michael Welling <mwelling@ieee.org>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.lattice import LatticeiCE40Platform
from litex.build.lattice.programmer import TinyProgProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk100", 0, Pins("61"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led", 0, Pins("28 29 31 32"), IOStandard("LVCMOS33")),

    ("user_btn_n",    0, Pins( "25"), IOStandard("LVCMOS33")),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("71"), IOStandard("LVCMOS33")),
        Subsignal("clk",  Pins("70"), IOStandard("LVCMOS33")),
        Subsignal("mosi", Pins("67"), IOStandard("LVCMOS33")),
        Subsignal("miso", Pins("68"), IOStandard("LVCMOS33")),
    ),

    # SDR SDRAM
    ("sdram_clock", 0, Pins("93"), IOStandard("LVCMOS33")),
    ("sdram", 0,
        Subsignal("a",     Pins("118 117 116 101 81 83 90 91 82 84 119 85 87")),
        Subsignal("dq",    Pins("96 97 98 99 95 80 79 78")),
        Subsignal("we_n",  Pins("128")),
        Subsignal("ras_n", Pins("124")),
        Subsignal("cas_n", Pins("125")),
        Subsignal("cs_n",  Pins("122")),
        Subsignal("cke",   Pins("88")),
        Subsignal("ba",    Pins("121 120")),
        Subsignal("dm",    Pins("94")),
        IOStandard("LVCMOS33"),
        Misc("SLEWRATE=FAST")
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    # A2-H2, Pins 1-13
    # H9-A6, Pins 14-24
    # G1-J2, Pins 25-31
    ("GPIO",  " 37  39  42  44  38  41  43  45"),
    ("GPIO1", " 47  49  55  60  48  52  56  62"),
    ("GPIO2", "107 112 114 129 110 113 115 130"),
    ("GPIO3", "  7   9  15  12   4   8  10  11"),
    ("grove", " 73  74  75  76 104 102 106 105")
]

# Default peripherals
serial = [
    ("serial", 0,
        Subsignal("tx", Pins("GPIO:0")),
        Subsignal("rx", Pins("GPIO:1")),
        IOStandard("LVCMOS33")
    )
]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticeiCE40Platform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self, toolchain="icestorm"):
        LatticeiCE40Platform.__init__(self, "ice40-hx8k-tq144:4k", _io, _connectors, toolchain=toolchain)
        self.add_extension(serial)

    def create_programmer(self):
        return TinyProgProgrammer()

    def do_finalize(self, fragment):
        LatticeiCE40Platform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100", loose=True), 1e9/100e6)
