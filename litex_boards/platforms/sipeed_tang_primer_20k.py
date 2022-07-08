#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Icenowy Zheng <icenowy@aosc.io>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.build.generic_platform import *
from litex.build.gowin.platform import GowinPlatform
from litex.build.gowin.programmer import GowinProgrammer
from litex.build.openfpgaloader import OpenFPGALoader


# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk27",  0, Pins("H11"), IOStandard("LVCMOS33")),

    # Serial
    ("serial", 0,
        Subsignal("rx", Pins("T13")),
        Subsignal("tx", Pins("M11")),
        IOStandard("LVCMOS33")
    ),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("M9"),  IOStandard("LVCMOS33")),
        Subsignal("clk",  Pins("L10"), IOStandard("LVCMOS33")),
        Subsignal("miso", Pins("P10"), IOStandard("LVCMOS33")),
        Subsignal("mosi", Pins("R10"), IOStandard("LVCMOS33")),
    ),

    # SDCard
    ("spisdcard", 0,
        Subsignal("clk",  Pins("N10")),
        Subsignal("mosi", Pins("R14")),
        Subsignal("cs_n", Pins("N11")),
        Subsignal("miso", Pins("M8")),
        IOStandard("LVCMOS33"),
    ),
    ("sdcard", 0,
        Subsignal("data", Pins("M8 M7 M10 N11")),
        Subsignal("cmd",  Pins("R14")),
        Subsignal("clk",  Pins("N10")),
        Subsignal("cd",   Pins("D15")),
        IOStandard("LVCMOS33"),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = []

# Platform -----------------------------------------------------------------------------------------

class Platform(GowinPlatform):
    default_clk_name   = "clk27"
    default_clk_period = 1e9/27e6

    def __init__(self, toolchain="gowin"):
        GowinPlatform.__init__(self, "GW2A-LV18PG256C8/I7", _io, _connectors, toolchain=toolchain, devicename="GW2A-18C")
        self.toolchain.options["use_mspi_as_gpio"] = 1
        self.toolchain.options["use_sspi_as_gpio"] = 1

    def create_programmer(self, kit="openfpgaloader"):
        return OpenFPGALoader(cable="ft2232")

    def do_finalize(self, fragment):
        GowinPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk27", loose=True), 1e9/27e6)
