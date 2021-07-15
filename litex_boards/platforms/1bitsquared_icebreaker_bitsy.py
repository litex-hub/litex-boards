#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Piotr Esden-Tempski <piotr@esden.net>
# Copyright (c) 2021 Sylvain Munaut <tnt@246tNt.com>
# SPDX-License-Identifier: BSD-2-Clause

# iCEBreaker Bitsy FPGA:
# - 1BitSquared Store: https://1bitsquared.com/collections/fpga/products/icebreaker-bitsy
# - Design files: https://github.com/icebreaker-fpga/icebreaker

from litex.build.dfu import DFUProg
from litex.build.generic_platform import *
from litex.build.lattice import LatticePlatform

# IOs ----------------------------------------------------------------------------------------------

_io_v0 = [
    # Clk / Rst
    ("clk12", 0, Pins("35"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led_n",    0, Pins("11"), IOStandard("LVCMOS33")),
    ("user_led_n",    1, Pins("37"), IOStandard("LVCMOS33")),

    ("user_ledr_n",   0, Pins("11"), IOStandard("LVCMOS33")), # Color-specific alias
    ("user_ledg_n",   0, Pins("37"), IOStandard("LVCMOS33")), # Color-specific alias

    # Button
    ("user_btn_n",    0, Pins("10"), IOStandard("LVCMOS33")),

    # USB
    ("usb", 0,
        Subsignal("d_p", Pins("43")),
        Subsignal("d_n", Pins("42")),
        Subsignal("pullup", Pins("38")),
        IOStandard("LVCMOS33")
    ),

    # Serial
    ("serial", 0,
        Subsignal("rx", Pins("18")),
        Subsignal("tx", Pins("19"), Misc("PULLUP")),
        IOStandard("LVCMOS33")
    ),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("16"), IOStandard("LVCMOS33")),
        Subsignal("clk",  Pins("15"), IOStandard("LVCMOS33")),
        Subsignal("miso", Pins("17"), IOStandard("LVCMOS33")),
        Subsignal("mosi", Pins("14"), IOStandard("LVCMOS33")),
        Subsignal("wp",   Pins("12"), IOStandard("LVCMOS33")),
        Subsignal("hold", Pins("13"), IOStandard("LVCMOS33")),
    ),
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("16"), IOStandard("LVCMOS33")),
        Subsignal("clk",  Pins("15"), IOStandard("LVCMOS33")),
        Subsignal("dq",   Pins("14 17 12 13"), IOStandard("LVCMOS33")),
    ),
]

_io_v1 = [
    # Clk / Rst
    ("clk12", 0, Pins("35"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led_n",    0, Pins("25"), IOStandard("LVCMOS33")),
    ("user_led_n",    1, Pins( "6"), IOStandard("LVCMOS33")),

    ("user_ledr_n",   0, Pins("25"), IOStandard("LVCMOS33")), # Color-specific alias
    ("user_ledg_n",   0, Pins( "6"), IOStandard("LVCMOS33")), # Color-specific alias

    # Button
    ("user_btn_n",    0, Pins( "2"), IOStandard("LVCMOS33")),

    # USB
    ("usb", 0,
        Subsignal("d_p", Pins("42")),
        Subsignal("d_n", Pins("38")),
        Subsignal("pullup", Pins("37")),
        IOStandard("LVCMOS33")
    ),

    # Serial
    ("serial", 0,
        Subsignal("rx", Pins("47")),
        Subsignal("tx", Pins("44"), Misc("PULLUP")),
        IOStandard("LVCMOS33")
    ),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("16"), IOStandard("LVCMOS33")),
        Subsignal("clk",  Pins("15"), IOStandard("LVCMOS33")),
        Subsignal("miso", Pins("17"), IOStandard("LVCMOS33")),
        Subsignal("mosi", Pins("14"), IOStandard("LVCMOS33")),
        Subsignal("wp",   Pins("18"), IOStandard("LVCMOS33")),
        Subsignal("hold", Pins("19"), IOStandard("LVCMOS33")),
    ),
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("16"), IOStandard("LVCMOS33")),
        Subsignal("clk",  Pins("15"), IOStandard("LVCMOS33")),
        Subsignal("dq",   Pins("14 17 18 19"), IOStandard("LVCMOS33")),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors_v0 = [
]

_connectors_v1 = [
    ("PIN",   "47 44 48 45  4  3  9 10 11 12 21 13 20 25 23 27 26 28 31 32 34 36 43 46"),
    ("PMOD1", "47 48  4  9 44 45  3 10"),
    ("PMOD2", "43 32 26 28 36 31 27 34"),
    ("PMOD3", "23 12 13 11 25 21 20 46")
]


# Platform -----------------------------------------------------------------------------------------

class Platform(LatticePlatform):
    default_clk_name   = "clk12"
    default_clk_period = 1e9/12e6

    def __init__(self, revision="v1", toolchain="icestorm"):
        assert revision in ["v0", "v1"]
        io, connectors = {
            "v0": (_io_v0, _connectors_v0),
            "v1": (_io_v1, _connectors_v1),
        }[revision]
        LatticePlatform.__init__(self, "ice40-up5k-sg48", io, connectors, toolchain=toolchain)

    def create_programmer(self):
        return DFUProg(vid="1d50", pid="6146")

    def do_finalize(self, fragment):
        LatticePlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk12", loose=True), 1e9/12e6)
