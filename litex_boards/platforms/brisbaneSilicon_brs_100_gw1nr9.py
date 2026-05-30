#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 Gwenhael Goavec-Merou <gwenhael.goavec-merou@trabucayre.com>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.build.generic_platform import *
from litex.build.gowin.platform import GowinPlatform
from litex.build.openfpgaloader import OpenFPGALoader


# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk27", 0, Pins("52"), IOStandard("LVCMOS33"), Misc("PULL_MODE=UP")),

    # Leds
    ("user_led_n", 0, Pins("16"), Misc("PULL_MODE=UP DRIVE=8")),
    ("user_led_n", 1, Pins("15"), Misc("PULL_MODE=UP DRIVE=8")),
    ("user_led_n", 2, Pins("14"), Misc("PULL_MODE=UP DRIVE=8")),
    ("user_led_n", 3, Pins("13"), Misc("PULL_MODE=UP DRIVE=8")),
    ("user_led_n", 4, Pins("11"), Misc("PULL_MODE=UP DRIVE=8")),
    ("user_led_n", 5, Pins("10"), Misc("PULL_MODE=UP DRIVE=8")),

    # Buttons
    ("user_btn_n", 0, Pins("3"), Misc("PULL_MODE=UP")),
    ("user_btn_n", 1, Pins("4"), Misc("PULL_MODE=UP")),

    # Serial
    ("serial", 0,
        Subsignal("rx", Pins("18"), Misc("PULL_MODE=UP")),
        Subsignal("tx", Pins("17"), Misc("PULL_MODE=UP DRIVE=8")),
        IOStandard("LVCMOS33")
    ),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("60"), Misc("PULL_MODE=UP DRIVE=8")),
        Subsignal("clk",  Pins("59"), Misc("PULL_MODE=UP DRIVE=8")),
        Subsignal("miso", Pins("62"), Misc("PULL_MODE=UP")),
        Subsignal("mosi", Pins("61"), Misc("PULL_MODE=UP DRIVE=8")),
        IOStandard("LVCMOS33"),
    ),

    # PSRAM
    ("O_psram_ck",      0, Pins(2)),
    ("O_psram_ck_n",    0, Pins(2)),
    ("O_psram_cs_n",    0, Pins(2)),
    ("O_psram_reset_n", 0, Pins(2)),
    ("IO_psram_dq",     0, Pins(16)),
    ("IO_psram_rwds",   0, Pins(2)),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ["J5", "25 26 27 28 29 30 33 34 35 36 37 38 39 40 41 42"],
    ["J6", "77 76 75 74 73 72 71 70 69 68 57 56 55 54 53 51"],
]

# Platform -----------------------------------------------------------------------------------------

class Platform(GowinPlatform):
    default_clk_name   = "clk27"
    default_clk_period = 1e9/27e6

    def __init__(self, toolchain="gowin"):
        GowinPlatform.__init__(self, "GW1NR-LV9QN88PC7/I6", _io, _connectors, toolchain=toolchain, devicename="GW1NR-9C")
        self.toolchain.options["use_mspi_as_gpio"] = 1
        self.toolchain.options["use_sspi_as_gpio"] = 1

    def create_programmer(self):
        return OpenFPGALoader("brs-100-gw1nr9")

    def do_finalize(self, fragment):
        GowinPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk27", loose=True), 1e9/27e6)
