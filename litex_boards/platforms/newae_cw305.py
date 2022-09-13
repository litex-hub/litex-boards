#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Leds
    ("user_led", 0, Pins("T2"),  IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("T3"),  IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("T4"),  IOStandard("LVCMOS33")),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = []

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    def __init__(self, toolchain="vivado"):
        XilinxPlatform.__init__(self, "xc7a100t-ftg256-2", _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        return OpenOCD("openocd_xc7_ft232.cfg", "bscan_spi_xc7a100t.bit")

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
