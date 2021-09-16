#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Ilia Sergachev <ilia.sergachev@protonmail.ch>
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.lattice import LatticePlatform
from litex.build.openfpgaloader import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk50", 0, Pins("L19"), IOStandard("LVCMOS33")),

    # Serial
    ("serial", 0,
        Subsignal("rx", Pins("B20"), IOStandard("LVCMOS33")),
        Subsignal("tx", Pins("A19"), IOStandard("LVCMOS33")),
    ),

    # Buttons
    ("user_btn", 0, Pins("M19"), IOStandard("LVCMOS33")),
    ("user_btn", 1, Pins("M20"), IOStandard("LVCMOS33")),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("pmod1", "B6   A7  A8  A9  A6  B8  B9 A10"),
    ("pmod2", "A11 A12 A13 A14 B10 B11 B12 B13"),
    ("pmod3", "B15 B16 B17 B18 A15 A16 A17 A18"),
    ("pmod4", "D19 E19 F19 G19 C20 D20 E20 F20"),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticePlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/506

    def __init__(self, toolchain="trellis", **kwargs):
        LatticePlatform.__init__(self, "LFE5UM5G-45F-8BG381I", _io, _connectors, toolchain=toolchain, **kwargs)

    def create_programmer(self):
        return OpenFPGALoader("ecpix5")

    def do_finalize(self, fragment):
        LatticePlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
