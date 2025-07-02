#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 Miodrag Milanovic <mmicko@gmail.com>
#
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.colognechip.platform import CologneChipPlatform
from litex.build.openfpgaloader import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk48", 0, Pins("IO_SB_A8"), Misc("SCHMITT_TRIGGER=true")),

    # Leds
    ("user_led_n", 0, Pins("IO_NB_B4")),

    # Serial.
    ("serial", 0,
        Subsignal("tx", Pins("IO_WC_A2")),
        Subsignal("rx", Pins("IO_WC_A0"))
    ),

    # SDRAM
    ("sdram_clock", 0, Pins("IO_SA_A6"), Misc("SLEW=fast")),
    ("sdram", 0,
        Subsignal("a",     Pins(
            "IO_EA_A2 IO_SB_B2 IO_SB_B8 IO_EA_B2 IO_EA_B0 IO_EA_A0 IO_SB_B6 IO_SB_A3",
            "IO_EA_A1 IO_SB_B0 IO_SB_A2 IO_SB_A0 IO_EA_B1")),
        Subsignal("ba",    Pins("IO_EA_B4 IO_SB_B1")),
        Subsignal("cs_n",  Pins("IO_SB_A1")),
        Subsignal("cke",   Pins("IO_SA_A7")),
        Subsignal("ras_n", Pins("IO_SB_B5")),
        Subsignal("cas_n", Pins("IO_SB_B3")),
        Subsignal("we_n",  Pins("IO_SB_A5")),
        Subsignal("dq",    Pins(
            "IO_SA_B5 IO_SA_B4 IO_SA_A5 IO_SB_B7 IO_SA_B7 IO_SB_A6 IO_SA_B6 IO_SA_B8",
            "IO_SA_A2 IO_SA_A4 IO_SA_B2 IO_SA_B0 IO_SA_A0 IO_SA_B3 IO_SA_B1 IO_SA_A3")),
        Subsignal("dm",    Pins("IO_SA_A8 IO_SA_A1"))
    ),

    # VGA
    ("vga", 0,
        Subsignal("hsync_n", Pins("IO_NA_A0")),
        Subsignal("vsync_n", Pins("IO_NA_B0")),
        Subsignal("r",       Pins("IO_NA_B1 IO_NA_A1 IO_NA_A2 IO_NA_A4")),
        Subsignal("g",       Pins("IO_NA_B4 IO_NA_A7 IO_NA_B7 IO_NA_B2")),
        Subsignal("b",       Pins("IO_NA_A3 IO_NA_A5 IO_NA_A6 IO_NA_A8")),
    ),

    # SD card w/ SPI interface
    ("spisdcard", 0,
        Subsignal("clk",  Pins("IO_WC_A4")),
        Subsignal("mosi", Pins("IO_WC_A3")),
        Subsignal("cs_n", Pins("IO_WC_B5")),
        Subsignal("miso", Pins("IO_WC_B3")),
    ),

    # DUAL USB HOST
    ("usb_host", 0,
        Subsignal("dp", Pins("IO_WB_A7 IO_WB_A5")),
        Subsignal("dm", Pins("IO_WB_B7 IO_WB_B5")),
    ),

    # 3.5MM AUDIO
    ("audio_pwm", 0,
        Subsignal("left",  Pins("IO_NB_B0")),
        Subsignal("right", Pins("IO_NB_A0")),
    ),

    # 3.5MM VIDEO
    ("video_dac", 0,
        Subsignal("data", Pins("IO_EB_A8 IO_EB_B4 IO_EB_A4 IO_EB_B5")),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("PMOD", "IO_EB_B2 IO_EB_A2 IO_EB_B3 IO_EB_A3 IO_EB_A0 IO_EB_B0 IO_EB_A1 IO_EB_B1"),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(CologneChipPlatform):
    default_clk_name   = "clk48"
    default_clk_period = 1e9/48e6

    def __init__(self, toolchain="colognechip"):
        CologneChipPlatform.__init__(self, "CCGM1A1", _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        return OpenFPGALoader(cable="dirtyJtag")

    def do_finalize(self, fragment):
        CologneChipPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk48", loose=True), 1e9/48e6)
