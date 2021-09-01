#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Greg Davill <greg.davill@gmail.com>
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.lattice import LatticePlatform
from litex.build.lattice.programmer import OpenOCDJTAGProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io_r1_0 = [
    # Clk
    ("clk30", 0, Pins("B12"),  IOStandard("LVCMOS33")),

    # Leds
    ("user_led",       0, Pins("C13"), IOStandard("LVCMOS33")),
    ("user_led",       1, Pins("D12"), IOStandard("LVCMOS33")),
    ("user_led",       2, Pins(" U2"), IOStandard("LVCMOS33")),
    ("user_led",       3, Pins(" T3"), IOStandard("LVCMOS33")),
    ("user_led",       4, Pins("D13"), IOStandard("LVCMOS33")),
    ("user_led",       5, Pins("E13"), IOStandard("LVCMOS33")),
    ("user_led",       6, Pins("C16"), IOStandard("LVCMOS33")),
    ("user_led_color", 0, Pins("T1 R1 U1"), IOStandard("LVCMOS33")),

    # Buttons
    ("user_btn", 0, Pins("U16"), IOStandard("SSTL135_I")),
    ("user_btn", 1, Pins("T17"), IOStandard("SSTL135_I")),

    # DDR3 SDRAM
    ("ddram", 0,
        Subsignal("a", Pins(
            "G16 E19 E20 F16 F19 E16 F17 L20 "
            "M20 E18 G18 D18 H18 C18 D17 G20 "),
            IOStandard("SSTL135_I")),
        Subsignal("ba",    Pins("H16 F20 H20"), IOStandard("SSTL135_I")),
        Subsignal("ras_n", Pins("K18"),     IOStandard("SSTL135_I")),
        Subsignal("cas_n", Pins("J17"),     IOStandard("SSTL135_I")),
        Subsignal("we_n",  Pins("G19"),     IOStandard("SSTL135_I")),
        Subsignal("cs_n",  Pins("J20 J16"), IOStandard("SSTL135_I")),
        Subsignal("dm", Pins("U20 L18"), IOStandard("SSTL135_I")),
        Subsignal("dq", Pins(
            "U19 T18 U18 R20 P18 P19 P20 N20",
            "L19 L17 L16 R16 N18 R17 N17 P17"),
            IOStandard("SSTL135_I"),
            Misc("TERMINATION=75")),
        Subsignal("dqs_p", Pins("T19 N16"), IOStandard("SSTL135D_I"),
            Misc("TERMINATION=OFF"),
            Misc("DIFFRESISTOR=100")),
        Subsignal("clk_p",   Pins("C20 J19"), IOStandard("SSTL135D_I")),
        Subsignal("cke",     Pins("F18 J18"), IOStandard("SSTL135_I")),
        Subsignal("odt",     Pins("K20 H17"), IOStandard("SSTL135_I")),
        Subsignal("reset_n", Pins("E17"), IOStandard("SSTL135_I")),
        Misc("SLEWRATE=FAST")
    ),

    # RGMII Ethernet
    ("eth_clocks", 0,
        Subsignal("tx", Pins("E15")),
        Subsignal("rx", Pins("D11")),
        IOStandard("LVCMOS33"),
        Misc("SLEWRATE=FAST"),
    ),

    ("eth", 0,
        Subsignal("rst_n",   Pins("B20")),
        Subsignal("mdio",    Pins("D16")),
        Subsignal("mdc",     Pins("A19")),
        Subsignal("rx_data", Pins("A16 C17 B17 A17")),
        Subsignal("tx_ctl",  Pins("D15")),
        Subsignal("rx_ctl",  Pins("B18")),
        Subsignal("tx_data", Pins("C15 B16 A18 B19")),
        IOStandard("LVCMOS33"),
        Misc("SLEWRATE=FAST")
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors_r1_0 = []

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticePlatform):
    default_clk_name   = "clk30"
    default_clk_period = 1e9/30e6

    def __init__(self, revision="1.0", device="85F", toolchain="trellis", **kwargs):
        assert revision in ["1.0"]
        self.revision = revision
        io         = {"1.0": _io_r1_0}[revision]
        connectors = {"1.0": _connectors_r1_0}[revision]
        LatticePlatform.__init__(self, f"LFE5UM5G-{device}-8BG381C", io, connectors, toolchain=toolchain, **kwargs)

    def create_programmer(self):
        return OpenOCDJTAGProgrammer("openocd_butterstick.cfg")

    def do_finalize(self, fragment):
        LatticePlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk30", loose=True), 1e9/30e6)
