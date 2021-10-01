#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.quicklogic import QuickLogicPlatform

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Leds
    ("user_led", 0, Pins("H7"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("G7"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("F6"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("E8"), IOStandard("LVCMOS33")),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(QuickLogicPlatform):
    def __init__(self):
        QuickLogicPlatform.__init__(self, "ql-eos-s3", _io, toolchain="symbiflow")

