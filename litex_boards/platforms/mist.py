#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Krzysztof Jankowski <yanekx@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.altera import AlteraPlatform
from litex.build.altera.programmer import USBBlaster

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk27", 0, Pins("54")),
    ("clk27", 0, Pins("54")),

    # Leds
    ("user_led", 0, Pins("7"),
        Misc("CURRENT_STRENGTH_NEW 4MA")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("46")),
        Subsignal("rx", Pins("31")),
    ),

    # VGA
    ("vga", 0,
        Subsignal("hsync_n", Pins("119")),
        Subsignal("vsync_n", Pins("136")),
        Subsignal("r", Pins("135 137 141 142 143 144")),
        Subsignal("g", Pins("106 110 111 112 113 114")),
        Subsignal("b", Pins("115 120 121 125 132 133")),
        Misc("CURRENT_STRENGTH_NEW \"MAXIMUM CURRENT\""),
    ),

    # Audio
    ("audio", 0,
        Subsignal("l", Pins("65")),
        Subsignal("r", Pins("80")),
        Misc("CURRENT_STRENGTH_NEW 4MA"),
    ),


    # SPI
    ("spi", 0,
        Subsignal("do", Pins("105")),
        Subsignal("di", Pins("88")),
        Subsignal("sck", Pins("126")),
        Subsignal("ss2", Pins("127")),
        Subsignal("ss3", Pins("91")),
        Subsignal("ss4", Pins("90")),
    ),

    # SDR SDRAM
    ("sdram_clock", 0, Pins("43"),
        Misc("CURRENT_STRENGTH_NEW \"MAXIMUM CURRENT\""), IOStandard("3.3-V LVTTL")),
    ("sdram", 0,
        Subsignal("a", Pins("49 44 42 39 4 6 8 10 11 28 50 30 32")),
        Subsignal("dq", Pins("83 79 77 76 72 71 69 68 86 87 98 99 100 101 103 104"),
            Misc("FAST_INPUT_REGISTER ON"), Misc("FAST_OUTPUT_ENABLE_REGISTER ON")),
        Subsignal("ba", Pins("58 51")),
        Subsignal("dm", Pins("67 85")),     # DQML, DQMH
        Subsignal("ras_n", Pins("60")),
        Subsignal("cas_n", Pins("64")),
        Subsignal("we_n", Pins("66")),
        Subsignal("cs_n", Pins("59")),
        Subsignal("cke", Pins("33")),
        Misc("FAST_OUTPUT_REGISTER ON"),
        Misc("CURRENT_STRENGTH_NEW \"MAXIMUM CURRENT\""),
    ),

    # Others
    ("conf_data0", 0, Pins("13")),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name   = "clk27"
    default_clk_period = 1e9/27e6

    def __init__(self, toolchain="quartus"):
        AlteraPlatform.__init__(self, "EP3C25E144C8", _io, toolchain="quartus")
        self.add_platform_command("set_global_assignment -name FAMILY \"Cyclone III\"")
        self.add_platform_command("set_global_assignment -name DEVICE_FILTER_PIN_COUNT 144")
        self.add_platform_command("set_global_assignment -name CYCLONEII_OPTIMIZATION_TECHNIQUE BALANCED")
        self.add_platform_command("set_global_assignment -name USE_CONFIGURATION_DEVICE OFF")
        self.add_platform_command("set_global_assignment -name CYCLONEIII_CONFIGURATION_SCHEME \"PASSIVE SERIAL\"")
        self.add_platform_command("set_global_assignment -name RESERVE_ALL_UNUSED_PINS_WEAK_PULLUP \"AS INPUT TRI-STATED\"")
        self.add_platform_command("set_global_assignment -name CYCLONEII_RESERVE_NCEO_AFTER_CONFIGURATION \"USE AS REGULAR IO\"")
        self.add_platform_command("set_global_assignment -name RESERVE_DATA0_AFTER_CONFIGURATION \"USE AS REGULAR IO\"")
        self.add_platform_command("set_global_assignment -name RESERVE_DATA1_AFTER_CONFIGURATION \"USE AS REGULAR IO\"")
        self.add_platform_command("set_global_assignment -name RESERVE_FLASH_NCE_AFTER_CONFIGURATION \"USE AS REGULAR IO\"")
        self.add_platform_command("set_global_assignment -name RESERVE_DCLK_AFTER_CONFIGURATION \"USE AS REGULAR IO\"")
        self.add_platform_command("set_global_assignment -name STRATIX_DEVICE_IO_STANDARD \"3.3-V LVTTL\"")

    def create_programmer(self):
        return USBBlaster()

    def do_finalize(self, fragment):
        AlteraPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk27", 0, loose=True), 1e9/27e6)
        self.add_period_constraint(self.lookup_request("clk27", 1, loose=True), 1e9/27e6)

