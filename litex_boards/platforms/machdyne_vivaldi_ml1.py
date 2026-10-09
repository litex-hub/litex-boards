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

# Vivaldi carrier IOs (ML1 module IOs are in litex_boards.extensions.machdyne).
_io = [
    # I2C
    ("i2c", 0,
        Subsignal("sda", Pins("A13")),
        Subsignal("scl", Pins("B13")),
        IOStandard("LVCMOS33")
    ),
]

_io_v2 = [
    # ETHERNET (2nd port, on module XA-XD signals only available on ML1 v2).
    ("eth", 1,
        Subsignal("rx_data", Pins("B3 A2"), Misc("PULLMODE=UP")),
        Subsignal("tx_data", Pins("A4 A3")),
        Subsignal("tx_en", Pins("R12")),
        Subsignal("crs_dv", Pins("T13"), Misc("PULLMODE=UP")),
        Subsignal("rst_n", Pins("T14")),
        IOStandard("LVCMOS33")
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = []

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
