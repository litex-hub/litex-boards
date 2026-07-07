#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform, VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # GPIOs
    ("gpio", 0, Pins("K13"), IOStandard("LVCMOS18")),
    ("gpio", 1, Pins("M12"), IOStandard("LVCMOS18")),
    ("gpio", 2, Pins("R10"), IOStandard("LVCMOS18")),
    ("gpio", 3, Pins("N14"), IOStandard("LVCMOS18")),
    ("gpio", 4, Pins("M14"), IOStandard("LVCMOS18")),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("PL_GPIO", "K13 M12 R10 N14 M14"),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    def __init__(self, toolchain="vivado"):
        Xilinx7SeriesPlatform.__init__(self, "xc7z010clg225-1", _io,  _connectors, toolchain=toolchain)

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
