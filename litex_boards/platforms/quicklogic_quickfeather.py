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
    ("user_led",   0, Pins("38"), IOStandard("LVCMOS33")), # blue
    ("user_led",   1, Pins("39"), IOStandard("LVCMOS33")), # green
    ("user_led",   2, Pins("34"), IOStandard("LVCMOS33")), # red

    # Button
    ("user_btn_n", 0, Pins("62"), IOStandard("LVCMOS33")),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(QuickLogicPlatform):
    def __init__(self, toolchain="symbiflow"):
        QuickLogicPlatform.__init__(self, "ql-eos-s3", _io, toolchain=toolchain)

