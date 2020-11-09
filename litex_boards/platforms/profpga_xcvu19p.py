#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 David Shah <dave@ds0.me>
# Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2020 Antmicro <www.antmicro.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import Pins, Subsignal, IOStandard, Misc
from litex.build.xilinx import XilinxPlatform, VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # CLK1
    ("clk300", 0,
        Subsignal("n", Pins("CA40"), IOStandard("LVDS")),
        Subsignal("p", Pins("CA39"), IOStandard("LVDS")),
    ),
    # Serial
    ("serial", 0,
        Subsignal("rx", Pins("BE29"), IOStandard("LVCMOS18")),
        Subsignal("tx", Pins("BE30"), IOStandard("LVCMOS18")),
    ),
    # EB-PDS-PCIe-Cable-R3 on TA1
    ("pcie_x4", 0,
        Subsignal("rst_n", Pins("E40"), IOStandard("LVCMOS12")),
        Subsignal("clk_n", Pins("AU10")),
        Subsignal("clk_p", Pins("AU11")),
        Subsignal("rx_n",  Pins("AJ1 AK3 AL1 AM3")),
        Subsignal("rx_p",  Pins("AJ2 AK4 AL2 AM4")),
        Subsignal("tx_n",  Pins("AL6 AM8 AN6 AP8")),
        Subsignal("tx_p",  Pins("AL7 AM9 AN7 AP9")),
    ),
    ("pcie_x8", 0,
        Subsignal("rst_n", Pins("E40"), IOStandard("LVCMOS12")),
        Subsignal("clk_n", Pins("AU10")),
        Subsignal("clk_p", Pins("AU11")),
        Subsignal("rx_n",  Pins("AJ1 AK3 AL1 AM3 AN1 AP3 AR1 AT3")),
        Subsignal("rx_p",  Pins("AJ2 AK4 AL2 AM4 AN2 AP4 AR2 AT4")),
        Subsignal("tx_n",  Pins("AL6 AM8 AN6 AP8 AR6 AT8 AU6 AV8")),
        Subsignal("tx_p",  Pins("AL7 AM9 AN7 AP9 AR7 AT9 AU7 AV9")),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = []

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "clk300"
    default_clk_period = 1e9/300e6

    def __init__(self):
        XilinxPlatform.__init__(self, "xcvu19p-fsva3824-2-e", _io, _connectors, toolchain="vivado")

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        # For passively cooled boards, overheating is a significant risk if airflow isn't sufficient
        self.add_platform_command("set_property BITSTREAM.CONFIG.OVERTEMPSHUTDOWN ENABLE [current_design]")
        # Reduce programming time
        self.add_platform_command("set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]")

        # TA1 pins Internal Vref
        self.add_platform_command("set_property INTERNAL_VREF 0.90 [get_iobanks 69]")
        self.add_platform_command("set_property INTERNAL_VREF 0.90 [get_iobanks 70]")
        self.add_platform_command("set_property INTERNAL_VREF 0.90 [get_iobanks 71]")

        self.add_period_constraint(self.lookup_request("clk300", 0, loose=True), 1e9/300e6)
