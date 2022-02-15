#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# Work-In-Progress...

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst.

    # TODO.

    # Debug.
    ("debug", 0, Pins("A15"), IOStandard("LVCMOS33")),
    ("debug", 1, Pins("C14"), IOStandard("LVCMOS33")),
    ("debug", 2, Pins("B14"), IOStandard("LVCMOS33")),
    ("debug", 3, Pins("A14"), IOStandard("LVCMOS33")),

    # Fan.
    ("fan", 0, Pins(""), IOStandard("LVCMOS33")),

    # Flash.
    ("flash_cs_n", 0, Pins("C23"), IOStandard("LVCMOS33")),
    ("flash", 0,
        Subsignal("mosi", Pins("B24")),
        Subsignal("miso", Pins("A25")),
        Subsignal("vpp",  Pins("B22")),
        Subsignal("hold", Pins("A22")),
        IOStandard("LVCMOS33")
    ),

    # PCIe.
    ("pcie_x4", 0,
        Subsignal("rst_n", Pins("K21"), IOStandard("LVCMOS33"), Misc("PULLUP=TRUE")),
        Subsignal("clk_p", Pins("K6")),
        Subsignal("clk_n", Pins("K5")),
        Subsignal("rx_p",  Pins("J4 L4 N4 R4")),
        Subsignal("rx_n",  Pins("J3 L3 N3 R3")),
        Subsignal("tx_p",  Pins("H2 K2 M2 P2")),
        Subsignal("tx_n",  Pins("H1 K1 M1 P1"))
    ),

    # DRAM (MT47H64M16).

    # HDMI Out.

    # TODO.

    # HDMI In.

    # TODO.
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "debug"   # FIXME.
    default_clk_period = 1e9/100e6 # FIXME.

    def __init__(self, toolchain="vivado"):
        XilinxPlatform.__init__(self, "xc7k70t-fbg676-1", _io, toolchain=toolchain)

    def create_programmer(self):
        return OpenOCD("openocd_xc7_ft232.cfg", "bscan_spi_xc7a70t.bit")

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
