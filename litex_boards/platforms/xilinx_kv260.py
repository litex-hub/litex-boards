#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Ilia Sergachev <ilia@sergachev.ch>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform, VivadoProgrammer


# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Fan.
    ("fan", 0, Pins("A12"), IOStandard("LVCMOS33")),

    # Seems like there are no on-board clock sources for PL when PS is not used so here a
    # clock-capable PMOD connector pin is added as a possible clock input (not tested).
    ("pmod_hda16_cc", 0, Pins("B21"), IOStandard("LVCMOS33")),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "pmod_hda16_cc"
    default_clk_period = 1e9/100e6

    def __init__(self, toolchain="vivado"):
        XilinxPlatform.__init__(self, "xck26-sfvc784-2lv-c", _io, toolchain=toolchain)
        self.toolchain.bitstream_commands = \
            ["set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]", ]
        self.default_clk_freq = 1e9 / self.default_clk_period

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment, *args, **kwargs):
        XilinxPlatform.do_finalize(self, fragment, *args, **kwargs)
        self.add_period_constraint(self.lookup_request("pmod_hda16_cc", loose=True), 1e9/100e6)
