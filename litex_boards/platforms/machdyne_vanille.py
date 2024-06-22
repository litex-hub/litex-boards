#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Lone Dynamics Corporation <info@lonedynamics.com>
#
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.lattice import LatticeECP5Platform
from litex.build.openfpgaloader import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io_vx = [

    # Clock
    ("clk48", 0,  Pins("128"),  IOStandard("LVCMOS33")),

    # LED
    ("user_led", 0, Pins("52"), IOStandard("LVCMOS33")),

    # SDRAM
    ("sdram_clock", 0, Pins("72"), IOStandard("LVTTL33")),
    ("sdram", 0,
        Subsignal("a", Pins(
            "81 80 79 78 105 106 107 108 "
            "110 111 82 112 113")),
        Subsignal("ba",    Pins("92 91")),
        Subsignal("cs_n",  Pins("84")),
        Subsignal("cke",   Pins("114")),
        Subsignal("ras_n", Pins("88")),
        Subsignal("cas_n", Pins("89")),
        Subsignal("we_n",  Pins("90")),
        Subsignal("dq", Pins(
            "104 103 102 99 98 97 95 94 ",
            "116 117 118 119 120 121 124 125")),
        Subsignal("dm", Pins("93 115")),
        IOStandard("LVTTL33")
    ),

    # Differential Data Multiple Interface
    ("ddmi", 0,
        Subsignal("clk_p",    Pins("69"),
            IOStandard("LVCMOS33D"), Misc("DRIVE=4")),
        Subsignal("data0_p",  Pins("71"),
            IOStandard("LVCMOS33D"), Misc("DRIVE=4")),
        Subsignal("data1_p",  Pins("74"),
            IOStandard("LVCMOS33D"), Misc("DRIVE=4")),
        Subsignal("data2_p",  Pins("77"),
            IOStandard("LVCMOS33D"), Misc("DRIVE=4")),
    ),

    # USB-C
    ("usb", 0,
        Subsignal("d_p", Pins("40")),
        Subsignal("d_n", Pins("44")),
        Subsignal("pullup", Pins("45")),
        IOStandard("LVCMOS33")
    ),

    # USB HOST
    ("usb_host", 0,
        Subsignal("dp", Pins("39")),
        Subsignal("dm", Pins("41")),
        IOStandard("LVCMOS33")
    ),

    # DEBUG UART (on USB host port)
    #("serial", 0,
    #    Subsignal("tx", Pins("39")),
    #    Subsignal("rx", Pins("41")),
    #    IOStandard("LVCMOS33")
    #),
]

_io_v0 = [

    # SD card w/ SPI interface
    ("spisdcard", 0,
        Subsignal("clk",  Pins("50")),
        Subsignal("mosi", Pins("47")),
        Subsignal("cs_n", Pins("48")),
        Subsignal("miso", Pins("46")),
        Misc("SLEWRATE=FAST"),
        IOStandard("LVCMOS33"),
    ),

]

# Connectors ---------------------------------------------------------------------------------------

_connectors_vx = [

]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticeECP5Platform):
    default_clk_name   = "clk48"
    default_clk_period = 1e9/48e6

    def __init__(self, revision="v0", device="12F", toolchain="trellis", **kwargs):
        assert revision in ["v0"]
        assert device in ["12F", "25F", "45F", "85F"]
        self.revision = revision

        io = _io_vx
        connectors = _connectors_vx

        if revision == "v0": io += _io_v0

        LatticeECP5Platform.__init__(self, f"LFE5U-{device}-6TG144", io, connectors, toolchain=toolchain, **kwargs)

    def create_programmer(self, cable):
        return OpenFPGALoader(cable=cable)

    def do_finalize(self, fragment):
        LatticeECP5Platform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk48", loose=True), 1e9/48e6)
