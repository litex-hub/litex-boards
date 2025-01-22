#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2023 Icenowy Zheng <uwu@icenowy.me>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.build.generic_platform import *
from litex.build.gowin.platform import GowinPlatform
from litex.build.gowin.programmer import GowinProgrammer
from litex.build.openfpgaloader import OpenFPGALoader


# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst.
    ("clk27",  0, Pins("4"), IOStandard("LVCMOS33")),

    # Serial.
    ("serial", 0,
        Subsignal("rx", Pins("70")),
        Subsignal("tx", Pins("69")),
        IOStandard("LVCMOS33")
    ),

    # SPIFlash.
    ("spiflash", 0,
        Subsignal("cs_n", Pins("60"), IOStandard("LVCMOS33")),
        Subsignal("clk",  Pins("59"), IOStandard("LVCMOS33")),
        Subsignal("miso", Pins("62"), IOStandard("LVCMOS33")),
        Subsignal("mosi", Pins("61"), IOStandard("LVCMOS33")),
    ),

    # SDCard.
    ("spisdcard", 0,
        Subsignal("clk",  Pins("83")),
        Subsignal("mosi", Pins("82")),
        Subsignal("cs_n", Pins("81")),
        Subsignal("miso", Pins("84")),
        IOStandard("LVCMOS33"),
    ),
    ("sdcard", 0,
        Subsignal("data", Pins("84 85 80 81")),
        Subsignal("cmd",  Pins("82")),
        Subsignal("clk",  Pins("83")),
        IOStandard("LVCMOS33"),
    ),
    
    ("hdmi", 0,
        Subsignal("clk_p", Pins("33")),
        Subsignal("clk_n", Pins("34")),
        Subsignal("data0_p", Pins("35")),
        Subsignal("data0_n", Pins("36")),
        Subsignal("data1_p", Pins("37")),
        Subsignal("data1_n", Pins("38")),
        Subsignal("data2_p", Pins("39")),
        Subsignal("data2_n", Pins("40")),
    ),

    # HDMI
    ("hdmi", 0,
        Subsignal("clk_p",   Pins("33")),
        Subsignal("clk_n",   Pins("34")),
        Subsignal("data0_p", Pins("35")),
        Subsignal("data0_n", Pins("36")),
        Subsignal("data1_p", Pins("37")),
        Subsignal("data1_n", Pins("38")),
        Subsignal("data2_p", Pins("39")),
        Subsignal("data2_n", Pins("40")),
        Subsignal("hdp", Pins("26"), IOStandard("LVCMOS18")),
        Subsignal("cec", Pins("25"), IOStandard("LVCMOS18")),
        Subsignal("sda", Pins("53")),
        Subsignal("scl", Pins("52")),
        Misc("PULL_MODE=NONE"),
    ),

    # Leds
    ("led_n", 0,  Pins("15"), IOStandard("LVCMOS33")),
    ("led_n", 1,  Pins("16"), IOStandard("LVCMOS33")),
    ("led_n", 2,  Pins("17"), IOStandard("LVCMOS33")),
    ("led_n", 3,  Pins("18"), IOStandard("LVCMOS33")),
    ("led_n", 4,  Pins("19"), IOStandard("LVCMOS33")),
    ("led_n", 5,  Pins("20"), IOStandard("LVCMOS33")),

    # RGB Led.
    ("rgb_led", 0, Pins("79"), IOStandard("LVCMOS33")),

    # Buttons.
    ("btn", 0,  Pins("88"), IOStandard("LVCMOS33")),
    ("btn", 1,  Pins("87"), IOStandard("LVCMOS33")),

    # SDRAM (embedded in SIP, requires specific IO naming)
    ("O_sdram_clk",   0, Pins(1),  IOStandard("LVCMOS33")),
    ("O_sdram_cke",   0, Pins(1),  IOStandard("LVCMOS33")),
    ("O_sdram_cs_n",  0, Pins(1),  IOStandard("LVCMOS33")),
    ("O_sdram_cas_n", 0, Pins(1),  IOStandard("LVCMOS33")),
    ("O_sdram_ras_n", 0, Pins(1),  IOStandard("LVCMOS33")),
    ("O_sdram_wen_n", 0, Pins(1),  IOStandard("LVCMOS33")),
    ("O_sdram_dqm",   0, Pins(4),  IOStandard("LVCMOS33")),
    ("O_sdram_addr",  0, Pins(11), IOStandard("LVCMOS33")),
    ("O_sdram_ba",    0, Pins(2),  IOStandard("LVCMOS33")),
    ("IO_sdram_dq",   0, Pins(32), IOStandard("LVCMOS33")),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
        ("J5", "- - - 76 80 42 41 56 54 51 48 55 49 86 79 - - 72 71 53 52"),
        ("J6", "- 73 74 75 85 77 15 16 27 28 25 26 29 30 31 17 20 19 18 - -")
]

# Platform -----------------------------------------------------------------------------------------

class Platform(GowinPlatform):
    default_clk_name   = "clk27"
    default_clk_period = 1e9/27e6

    def __init__(self, dock="standard", toolchain="gowin"):

        GowinPlatform.__init__(self, "GW2AR-LV18QN88C8/I7", _io, _connectors, toolchain=toolchain, devicename="GW2AR-18C")

        self.toolchain.options["use_mspi_as_gpio"]  = 1
        self.toolchain.options["use_sspi_as_gpio"]  = 1
        self.toolchain.options["use_ready_as_gpio"] = 1
        self.toolchain.options["use_done_as_gpio"]  = 1
        self.toolchain.options["rw_check_on_ram"]   = 1

    def create_programmer(self, kit="openfpgaloader"):
        return OpenFPGALoader(cable="ft2232")

    def do_finalize(self, fragment):
        GowinPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk27", loose=True), 1e9/27e6)
