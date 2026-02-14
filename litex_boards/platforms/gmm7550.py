#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 Anton Kuzmin <ak@gmm7550.dev>
#
# Based on CologneChip GateMate Evaluation Board (colognechip_gatemate_evb)
# Copyright (c) 2023 Gwenhael Goavec-merou<gwenhael.goavec-merou@trabucayre.com>
# SPDX-License-Identifier: BSD-2-Clause

# Board documentation/schematics:
# https://www.gmm7550.dev/doc/module.html

from litex.build.generic_platform import *
from litex.build.colognechip.platform import CologneChipPlatform
from litex.build.openfpgaloader import OpenFPGALoader

# GMM-7550 with USB 3 Adapter board -- pre-defined IO

_io = [
    # Main reference clock (100 MHz, module PLL)
    ("ser_clk", 0, Pins("SER_CLK")),

    # UART
    ("serial", 0,
     Subsignal("tx", Pins("IO_WA_A6")), # SPI D3, P5/J5 pin 33
     Subsignal("rx", Pins("IO_WA_B6")), # SPI D2, P5/J5 pin 31
     ),

    # Status LEDs on the USB 3 Adapter board
    ("led_red_n", 0,  Pins("IO_WA_A2")), # CFG_FAILED_N, P5/J5 pin 35
    ("led_green", 0,  Pins("IO_WA_B2")), # CFG_DONE,     P5/J5 pin 36
]

# GMM-7550 Module Connectors
_connectors = [
    # West ------------------------
    ("P1", "-", # 0
     ""),
    # North ------------------------
    ("P2", "-", # 0
     ""),
    # East ------------------------
    ("P3", "-", # 0
     ""),
    # South ------------------------
    ("P4", "-", # 0
     "      --- ---",      # 1  2
     "IO_SB_B8  IO_SB_B3", # 3  4
     "IO_SB_A8  IO_SB_A3", # 5  6
     "      --- ---",      # 7  8
     "IO_SB_B6  IO_SB_B2", # 9  10
     ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(CologneChipPlatform):
    default_clk_name   = "ser_clk"
    default_clk_period = 1e9/100e6

    def __init__(self, toolchain="peppercorn"):
        CologneChipPlatform.__init__(self, "CCGM1A1", _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        return OpenFPGALoader(cable="dirtyJtag")

    def do_finalize(self, fragment):
        CologneChipPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request(self.default_clk_name, loose=True),
                                   self.default_clk_period)
