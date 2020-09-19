#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# The Forest Kitten 33 is a cryptocurrency mining accelerator card from SQRL that can be repurposed
# as a generic FPGA PCIe development board: http://www.squirrelsresearch.com/forest-kitten-33

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform, VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    ("clk200", 0,
        Subsignal("p", Pins("BC26"), IOStandard("LVDS")),
        Subsignal("n", Pins("BC27"), IOStandard("LVDS"))
    ),

    ("user_led", 0, Pins("BD25"), IOStandard("LVCMOS18")),
    ("user_led", 1, Pins("BE26"), IOStandard("LVCMOS18")),
    ("user_led", 2, Pins("BD23"), IOStandard("LVCMOS18")),
    ("user_led", 3, Pins("BF26"), IOStandard("LVCMOS18")),
    ("user_led", 4, Pins("BC25"), IOStandard("LVCMOS18")),
    ("user_led", 5, Pins("BB26"), IOStandard("LVCMOS18")),
    ("user_led", 6, Pins("BB25"), IOStandard("LVCMOS18")),

    ("i2c",
        Subsignal("scl", Pins("BB24"), IOStandard("LVCMOS18"), Misc("DRIVE=8")),
        Subsignal("sda", Pins("BA24"), IOStandard("LVCMOS18"), Misc("DRIVE=8")),
    ),

    ("pcie_x2", 0,
        Subsignal("rst_n", Pins("BE24"), IOStandard("LVCMOS18")),
        Subsignal("clk_p", Pins("AD9")),
        Subsignal("clk_n", Pins("AD8")),
        Subsignal("rx_p",  Pins("AL2 AM4")),
        Subsignal("rx_n",  Pins("AL1 AM3")),
        Subsignal("tx_p",  Pins("Y5  AA7")),
        Subsignal("tx_n",  Pins("Y4  AA6")),
    ),

    ("pcie_x4", 0,
        Subsignal("rst_n", Pins("BE24"), IOStandard("LVCMOS18")),
        Subsignal("clk_p", Pins("AD9")),
        Subsignal("clk_n", Pins("AD8")),
        Subsignal("rx_p",  Pins("AL2 AM4 AK4 AN2")),
        Subsignal("rx_n",  Pins("AL1 AM3 AK3 AN1")),
        Subsignal("tx_p",  Pins("Y5  AA7 AB5 AC7")),
        Subsignal("tx_n",  Pins("Y4  AA6 AB4 AC6")),
    ),

    ("pcie_x8", 0,
        Subsignal("rst_n", Pins("BE24"), IOStandard("LVCMOS18")),
        Subsignal("clk_p", Pins("AD9")),
        Subsignal("clk_n", Pins("AD8")),
        Subsignal("rx_p",  Pins("AL2 AM4 AK4 AN2 AP4 AR2 AT4 AU2")),
        Subsignal("rx_n",  Pins("AL1 AM3 AK3 AN1 AP3 AR1 AT3 AU1")),
        Subsignal("tx_p",  Pins("Y5  AA7 AB5 AC7 AD5 AF5 AE7 AH5")),
        Subsignal("tx_n",  Pins("Y4  AA6 AB4 AC6 AD4 AF4 AE6 AH4")),
    ),

    ("pcie_x16", 0,
        Subsignal("rst_n", Pins("BE24"), IOStandard("LVCMOS18")),
        Subsignal("clk_p", Pins("AD9")),
        Subsignal("clk_n", Pins("AD8")),
        Subsignal("rx_p",  Pins("AL2 AM4 AK4 AN2 AP4 AR2 AT4 AU2 AV4 AW2 BA2 BC2 AY4 BB4 BD4 BE6")),
        Subsignal("rx_n",  Pins("AL1 AM3 AK3 AN1 AP3 AR1 AT3 AU1 AV3 AW1 BA1 BC1 AY3 BB3 BD3 BE5")),
        Subsignal("tx_p",  Pins("Y5  AA7 AB5 AC7 AD5 AF5 AE7 AH5 AG7 AJ7 AL7 AM9 AN7 AP9 AR7 AT9")),
        Subsignal("tx_n",  Pins("Y4  AA6 AB4 AC6 AD4 AF4 AE6 AH4 AG6 AJ6 AL6 AM8 AN6 AP8 AR6 AT8")),
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "clk200"
    default_clk_period = 1e9/200e6

    def __init__(self):
        XilinxPlatform.__init__(self, "xcvu33p-fsvh2104-2L-e-es1", _io, toolchain="vivado")

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk200", loose=True), 1e9/200e6)
        # Shutdown on overheatng
        self.add_platform_command("set_property BITSTREAM.CONFIG.OVERTEMPSHUTDOWN ENABLE [current_design]")
        # Reduce programming time
        self.add_platform_command("set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]")
