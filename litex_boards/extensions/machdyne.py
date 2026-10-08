#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2023 Lone Dynamics Corporation <info@lonedynamics.com>
# SPDX-License-Identifier: BSD-2-Clause

"""Machdyne FPGA modules, shared by the Machdyne carrier boards.

The modules carry the FPGA: their IOs are described with FPGA balls and plugged by the carrier
platforms (ex: Mozart ML1, Vivaldi ML1), which only add the IOs specific to the carrier:

    platform.add_extension(MachdyneML1(revision="v2"))
"""

from litex.build.generic_platform import *
from litex.build.extension import Extension

# ML1 Module ---------------------------------------------------------------------------------------

_ml1_io = [
    # Clock
    ("clk48", 0,  Pins("A7"),  IOStandard("LVCMOS33")),
    ("clk50", 0,  Pins("C7"),  IOStandard("LVCMOS33")),

    # SDRAM
    ("sdram_clock", 0, Pins("F16"), IOStandard("LVTTL33")),
    ("sdram", 0,
        Subsignal("a", Pins(
            "M13 M14 L14 L13 G12 G13 G14 G15",
            "F12 F13 T15 F14 E14")),
        Subsignal("ba",    Pins("P14 N13")),
        Subsignal("cs_n",  Pins("J16")),
        Subsignal("cke",   Pins("F15")),
        Subsignal("ras_n", Pins("K15")),
        Subsignal("cas_n", Pins("K16")),
        Subsignal("we_n",  Pins("L15")),
        Subsignal("dq", Pins(
            "R15 R16 P16 P15 N16 N14 M16 M15",
            "E15 D16 D14 C16 C15 C14 B15 B16")),
        Subsignal("dm", Pins("L16 E16")),
        IOStandard("LVTTL33")
    ),

    # DUAL USB HOST
    ("usb_host", 0,
        Subsignal("dp", Pins("A9 C8")),
        Subsignal("dm", Pins("A10 B8")),
        IOStandard("LVCMOS33")
    ),

    # ETHERNET
    ("eth", 0,
        Subsignal("rx_data", Pins("E4 D4"), Misc("PULLMODE=UP")),
        Subsignal("tx_data", Pins("E6 D6")),
        Subsignal("tx_en", Pins("C5")),
        Subsignal("crs_dv", Pins("A5"), Misc("PULLMODE=UP")),
        Subsignal("rst_n", Pins("B5")),
        IOStandard("LVCMOS33")
    ),

    # SD card w/ SD-mode interface (external pull-ups).
    ("sdcard", 0,
        Subsignal("cd", Pins("A6"), Misc("PULLMODE=NONE")),
        Subsignal("clk", Pins("L3"), Misc("PULLMODE=NONE")),
        Subsignal("cmd", Pins("M1"), Misc("PULLMODE=NONE")),
        Subsignal("data", Pins("L1 M2 M3 L2"), Misc("PULLMODE=NONE")),
        #Misc("SLEWRATE=FAST"),
        IOStandard("LVCMOS33")
    ),

    # SD card w/ SPI interface
    ("spisdcard", 0,
        Subsignal("clk",  Pins("L3")),
        Subsignal("mosi", Pins("M1")),
        Subsignal("cs_n", Pins("L2")),
        Subsignal("miso", Pins("L1")),
        Misc("SLEWRATE=FAST"),
        IOStandard("LVCMOS33"),
    ),
]

_ml1_serial_io = {
    # DEBUG UART on module XC/XD signals (v0/v1).
    "v0" : [
        ("serial", 0,
            Subsignal("tx", Pins("B3")),
            Subsignal("rx", Pins("A2")),
            IOStandard("LVCMOS33")
        ),
    ],
    # DEBUG UART moved on v2, XA-XD module signals available to the carrier.
    "v2" : [
        ("serial", 0,
            Subsignal("tx", Pins("B4")),
            Subsignal("rx", Pins("C4")),
            IOStandard("LVCMOS33")
        ),
    ],
}
_ml1_serial_io["v1"] = _ml1_serial_io["v0"]

class MachdyneML1(Extension):
    """Machdyne ML1 module: ECP5 (BG256), SDRAM and the module signals used identically by its
    carriers (dual USB host, RMII Ethernet, SD card, debug UART).
    """
    slots     = {}
    revisions = ["v0", "v1", "v2"]
    devices   = ["12F", "25F", "45F", "85F"]

    def __init__(self, revision="v2", **kwargs):
        assert revision in self.revisions
        self.revision = revision
        Extension.__init__(self, **kwargs)

    @classmethod
    def device(cls, device="45F"):
        assert device in cls.devices
        return f"LFE5U-{device}-6BG256"

    def define_io(self, platform):
        return [*_ml1_io, *_ml1_serial_io[self.revision]]
