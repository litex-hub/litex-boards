#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk.
    ("sma_clk_in",  0, Pins("N11"), IOStandard("LVCMOS33")),
    ("sma_clk_out", 0, Pins("T13"), IOStandard("LVCMOS33")),

    # Leds.
    ("user_led", 0, Pins("T2"),  IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("T3"),  IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("T4"),  IOStandard("LVCMOS33")),

    # Buttons.
    ("user_btn", 0, Pins("R1"), IOStandard("LVCMOS33")),

    # Switches.
    ("user_sw", 0, Pins("J16"), IOStandard("LVCMOS33")),
    ("user_sw", 1, Pins("K16"), IOStandard("LVCMOS33")),
    ("user_sw", 2, Pins("K15"), IOStandard("LVCMOS33")),
    ("user_sw", 3, Pins("L14"), IOStandard("LVCMOS33")),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ["expansion",
        # -------------------------------------------------
        "---", # 0
        # -------------------------------------------------
        # 3V3 3V3 GND GND
        " --- --- --- --- A12 B12 A14 A13 A15 B15 C12 C11 B14 C14 B16 C16 C13 D13",
        # 3V3 3V3 GND GND                                         TRI CLK GND GND
        " --- --- --- --- D15 --- E15 D16 E13 E16 F15 F12 E11 F13 --- --- --- ---",
    ],
]

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    def __init__(self, toolchain="vivado"):
        Xilinx7SeriesPlatform.__init__(self, "xc7a100t-ftg256-2", _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        return OpenOCD("openocd_xc7_ft232.cfg", "bscan_spi_xc7a100t.bit")

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
