#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Piotr Esden-Tempski <piotr@esden.net>
# Copyright (c) 2021 Sylvain Munaut <tnt@246tNt.com>
# Copyright (c) 2023 Michael Welling <mwelling@ieee.org>
# SPDX-License-Identifier: BSD-2-Clause

# ICE-V wireless

from litex.build.dfu import DFUProg
from litex.build.generic_platform import *
from litex.build.lattice import LatticeiCE40Platform

# IOs ----------------------------------------------------------------------------------------------

_io_v0 = [
    # Clk / Rst
    ("clk12", 0, Pins("35"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led_n",    0, Pins("39"), IOStandard("LVCMOS33")),
    ("user_led_n",    1, Pins("40"), IOStandard("LVCMOS33")),
    ("user_led_n",    2, Pins("41"), IOStandard("LVCMOS33")),

    # Button
    ("user_btn_n",    0, Pins("19"), IOStandard("LVCMOS33")),

    # USB
    ("usb", 0,
        Subsignal("d_p", Pins("4")),
        Subsignal("d_n", Pins("3")),
        Subsignal("pullup", Pins("45")),
        IOStandard("LVCMOS33")
    ),

    # Serial
    ("serial", 0,
        Subsignal("rx", Pins("11")),
        Subsignal("tx", Pins("12"), Misc("PULLUP")),
        IOStandard("LVCMOS33")
    ),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("37"), IOStandard("LVCMOS33")),
        Subsignal("clk",  Pins("28"), IOStandard("LVCMOS33")),
        Subsignal("mosi", Pins("26"), IOStandard("LVCMOS33")),
        Subsignal("miso", Pins("23"), IOStandard("LVCMOS33")),
        Subsignal("wp",   Pins("25"), IOStandard("LVCMOS33")),
        Subsignal("hold", Pins("27"), IOStandard("LVCMOS33")),
    ),
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("37"), IOStandard("LVCMOS33")),
        Subsignal("clk",  Pins("28"), IOStandard("LVCMOS33")),
        Subsignal("dq",   Pins("26 23 25 27"), IOStandard("LVCMOS33")),
    ),
]


# Connectors ---------------------------------------------------------------------------------------

_connectors_v0 = [
    ("PMOD1", "19 12 11  9 18 21 10  8"),
    ("PMOD2", " 4 48 47 46  3 45 44  2"),
    ("PMOD3", "42 43 32 13 38 36 31 20")
]


# Platform -----------------------------------------------------------------------------------------

class Platform(LatticeiCE40Platform):
    default_clk_name   = "clk12"
    default_clk_period = 1e9/12e6

    def __init__(self, revision="v0", toolchain="icestorm"):
        assert revision in ["v0"]
        io, connectors = {
            "v0": (_io_v0, _connectors_v0),
        }[revision]
        LatticeiCE40Platform.__init__(self, "ice40-up5k-sg48", io, connectors, toolchain=toolchain)

    def create_programmer(self):
        return DFUProg(vid="1d50", pid="6146")

    def do_finalize(self, fragment):
        LatticeiCE40Platform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk12", loose=True), 1e9/12e6)
