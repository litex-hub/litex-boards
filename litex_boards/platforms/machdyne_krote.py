#
# This file is part of LiteX-Boards.
# Copyright (c) 2018 William D. Jones <thor0505@comcast.net>
# Copyright (c) 2019 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2022 Lone Dynamics Corporation <info@lonedynamics.com>
#
# SPDX-License-Identifier: BSD-2-Clause
#
# Krote FPGA board: https://github.com/machdyne/krote
#

from litex.build.generic_platform import *
from litex.build.lattice import LatticeiCE40Platform

# IOs ----------------------------------------------------------------------------------------------

_io = [

    # Clk / Rst
    ("clk100", 0, Pins("B6"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led", 0, Pins("E2 F1 G2 J2"), IOStandard("LVCMOS33")),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("K10"), IOStandard("LVCMOS33")),
        Subsignal("clk",  Pins("L10"), IOStandard("LVCMOS33")),
        Subsignal("mosi", Pins("K9"), IOStandard("LVCMOS33")),
        Subsignal("miso", Pins("J9"), IOStandard("LVCMOS33")),
    ),

]


# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("PMODA",  "E1 B1 A2 A4 D1 C1 A1 A3"),
    ("PMODB",  "L3 L1 H1 G3 L2 K1 J1 F2"),
    ("PMODC",  "A8 A10 C11 A9 D10 B11 D11"),
    ("PMODD",  "E9 G10 F10 H11 E11 G11 G9"),
    ("PMODE",  "L8 K5 K3 L5 L7 K4 K2 L4")
]

# Default peripherals
serial = [
    ("serial", 0,
        Subsignal("tx", Pins("PMODE:1")),
        Subsignal("rx", Pins("PMODE:2")),
        IOStandard("LVCMOS33")
    )
]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticeiCE40Platform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self, toolchain="icestorm"):
        LatticeiCE40Platform.__init__(self, "ice40-hx8k-bg121", _io, _connectors, toolchain=toolchain)
        self.add_extension(serial)

    def do_finalize(self, fragment):
        LatticeiCE40Platform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100", loose=True), 1e9/100e6)
