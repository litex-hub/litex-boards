#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2023 Lone Dynamics Corporation <info@lonedynamics.com>
#
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.lattice import LatticeECP5Platform
from litex.build.openfpgaloader import OpenFPGALoader

from litex_boards.extensions.machdyne import MachdyneML1

# IOs ----------------------------------------------------------------------------------------------

# Mozart carrier IOs (ML1 module IOs are in litex_boards.extensions.machdyne).
_io = [
    # Differential Data Multiple Interface
    ("ddmi", 0,
        Subsignal("clk_p",    Pins("B13"),
            IOStandard("LVCMOS33D"), Misc("DRIVE=4")),
        Subsignal("data0_p",  Pins("A11"),
            IOStandard("LVCMOS33D"), Misc("DRIVE=4")),
        Subsignal("data1_p",  Pins("B12"),
            IOStandard("LVCMOS33D"), Misc("DRIVE=4")),
        Subsignal("data2_p",  Pins("B10"),
            IOStandard("LVCMOS33D"), Misc("DRIVE=4")),
    ),

    # USB-C
    ("usb", 0,
        Subsignal("d_p", Pins("A13")),
        Subsignal("d_n", Pins("A14")),
        Subsignal("pullup", Pins("D13")),
        IOStandard("LVCMOS33")
    ),
]

_io_v2 = []

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("X", "A4 A3 B3 A2"), # Module XA-XD signals (XC/XD are the debug UART on ML1 v0/v1).
]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticeECP5Platform):
    default_clk_name   = "clk48"
    default_clk_period = 1e9/48e6

    def __init__(self, revision="v2", device="45F", toolchain="trellis", **kwargs):
        assert revision in MachdyneML1.revisions
        self.revision = revision

        io = list(_io)
        if revision == "v2": io += _io_v2

        LatticeECP5Platform.__init__(self, MachdyneML1.device(device), io, list(_connectors), toolchain=toolchain, **kwargs)
        self.add_extension(MachdyneML1(revision=revision))

    def create_programmer(self, cable):
        return OpenFPGALoader(cable=cable)

    def do_finalize(self, fragment):
        LatticeECP5Platform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk48", loose=True), 1e9/48e6)
