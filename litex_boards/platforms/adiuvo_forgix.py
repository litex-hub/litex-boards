#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.efinix.platform import EfinixPlatform

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk.
    ("clk32", 0, Pins("B4"), IOStandard("3.3_V_LVTTL_/_LVCMOS")),

    # Leds.
    ("user_led_n", 0, Pins("E1"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=1")), # Red.
    ("user_led_n", 1, Pins("F1"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=1")), # Green.
    ("user_led_n", 2, Pins("G1"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=1")), # Blue.

    # Serial on FPGA header pins 4/5.
    ("serial", 0,
        Subsignal("rx", Pins("A5")),
        Subsignal("tx", Pins("D7")),
        IOStandard("3.3_V_LVTTL_/_LVCMOS"),
    ),

    # RP2350 passive-SPI configuration interface.
    ("fpga_cfg", 0,
        Subsignal("cs_n",     Pins("G3")),
        Subsignal("clk",      Pins("F3")),
        Subsignal("mosi",     Pins("F2")),
        Subsignal("reset_n",  Pins("G4")),
        Subsignal("done",     Pins("F4")),
        Subsignal("status_n", Pins("A4")),
        IOStandard("3.3_V_LVTTL_/_LVCMOS"),
    ),

    # FPGA I/Os routed to the Teensy-style edge connector.
    ("user_io", 0, Pins(
        "A5 D7 C7 D6 G7 G5 G2 F5 F6",
        "E5 C6 B3 B7 A7 A3 C2 D2 E2"),
        IOStandard("3.3_V_LVTTL_/_LVCMOS"),
    ),
]

# Bank voltage -------------------------------------------------------------------------------------

_bank_info = [
    ("1A", "3.3 V LVTTL / LVCMOS"),
    ("1B", "3.3 V LVTTL / LVCMOS"),
    ("1C", "1.1 V"),
    ("2A", "3.3 V LVTTL / LVCMOS"),
    ("2B", "3.3 V LVTTL / LVCMOS"),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    # Teensy-style edge connector. Use "teensy:1" for connector pin 1.
    ("teensy",
        "ZERO "
        "#N/A #N/A #N/A #N/A #N/A A5 D7 C7 #N/A #N/A D6 G7 G5 G2 #N/A #N/A #N/A #N/A #N/A "
        "F5 F6 E5 C6 B3 B7 A7 A3 C2 D2 E2 #N/A #N/A #N/A"
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(EfinixPlatform):
    default_clk_name   = "clk32"
    default_clk_freq   = 32e6
    default_clk_period = 1e9/32e6

    def __init__(self, toolchain="efinity"):
        EfinixPlatform.__init__(self,
            "T8F49C2", _io, _connectors,
            iobank_info = _bank_info,
            toolchain   = toolchain,
            spi_mode    = "passive",
            spi_width   = "1")

    def do_finalize(self, fragment):
        EfinixPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk32", loose=True), 1e9/32e6)
