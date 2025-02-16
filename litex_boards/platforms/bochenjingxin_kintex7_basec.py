#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 Yuji Yamada <yamada@arch.cs.titech.ac.jp>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk50",       0, Pins("G22"), IOStandard("LVCMOS33")),
    ("cpu_reset",   0, Pins("D26"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led", 0, Pins("A23"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("A24"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("D23"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("C24"), IOStandard("LVCMOS33")),
    ("user_led", 4, Pins("C26"), IOStandard("LVCMOS33")),
    ("user_led", 5, Pins("D24"), IOStandard("LVCMOS33")),
    ("user_led", 6, Pins("D25"), IOStandard("LVCMOS33")),
    ("user_led", 7, Pins("E25"), IOStandard("LVCMOS33")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("C22")),
        Subsignal("rx", Pins("B20")),
        IOStandard("LVCMOS33"),
    ),

    # OLED
    ("oled", 0,
        Subsignal("scl", Pins("J24")),
        Subsignal("sda", Pins("J25")),
        Subsignal("dc", Pins("H22")),
        Subsignal("rst", Pins("J21")),
        IOStandard("LVCMOS33"),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = []

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self, toolchain="vivado"):
        device = "xc7k325tffg676-1" # FIXME: Should be xc7k325tffg676-2
        Xilinx7SeriesPlatform.__init__(self, device, _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        return VivadoProgrammer() # Correct?

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
        self.add_platform_command("set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]")
        self.add_platform_command("set_property BITSTREAM.CONFIG.CONFIGRATE 50 [current_design]")
        self.add_platform_command("set_property CONFIG_VOLTAGE 3.3 [current_design]")
        self.add_platform_command("set_property CFGBVS VCCO [current_design]")
        self.add_platform_command("set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]")
