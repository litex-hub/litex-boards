#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Icenowy Zheng <icenowy@aosc.io>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.build.generic_platform import *
from litex.build.gowin.platform import GowinPlatform
from litex.build.gowin.programmer import GowinProgrammer
from litex.build.openfpgaloader import OpenFPGALoader


# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk27",  0, Pins("52"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led", 0, Pins("10"), IOStandard("LVCMOS18")),
    ("user_led", 1, Pins("11"), IOStandard("LVCMOS18")),
    ("user_led", 2, Pins("13"), IOStandard("LVCMOS18")),
    ("user_led", 3, Pins("14"), IOStandard("LVCMOS18")),
    ("user_led", 4, Pins("15"), IOStandard("LVCMOS18")),
    ("user_led", 5, Pins("16"), IOStandard("LVCMOS18")),

    # Buttons.
    ("user_btn", 0, Pins("3"), IOStandard("LVCMOS18")),
    ("user_btn", 1, Pins("4"), IOStandard("LVCMOS18")),

    # Serial
    ("serial", 0,
        Subsignal("rx", Pins("18")),
        Subsignal("tx", Pins("17")),
        IOStandard("LVCMOS33")
    ),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("60"), IOStandard("LVCMOS33")),
        Subsignal("clk",  Pins("59"), IOStandard("LVCMOS33")),
        Subsignal("miso", Pins("62"), IOStandard("LVCMOS33")),
        Subsignal("mosi", Pins("61"), IOStandard("LVCMOS33")),
    ),

    ("spisdcard", 0,
        Subsignal("clk",  Pins("36")),
        Subsignal("mosi", Pins("37")),
        Subsignal("cs_n", Pins("38")),
        Subsignal("miso", Pins("39")),
        IOStandard("LVCMOS33"),
    ),

    # PSRAM
    ("O_psram_ck",      0, Pins(2)),
    ("O_psram_ck_n",    0, Pins(2)),
    ("O_psram_cs_n",    0, Pins(2)),
    ("O_psram_reset_n", 0, Pins(2)),
    ("IO_psram_dq",     0, Pins(16)),
    ("IO_psram_rwds",   0, Pins(2)),

    # HDMI.
    ("hdmi", 0,
        Subsignal("clk_p",   Pins("69")),
        Subsignal("clk_n",   Pins("68")),
        Subsignal("data0_p", Pins("71")),
        Subsignal("data0_n", Pins("70")),
        Subsignal("data1_p", Pins("73")),
        Subsignal("data1_n", Pins("72")),
        Subsignal("data2_p", Pins("75")),
        Subsignal("data2_n", Pins("74")),
        Misc("PULL_MODE=NONE"),
    ),

    # SPI RGB LCD.
    ("spilcd", 0,
        Subsignal("reset", Pins("47")),
        Subsignal("cs",    Pins("48")),
        Subsignal("clk",   Pins("79")),
        Subsignal("mosi",  Pins("77")),
        Subsignal("rs",    Pins("47")),
        IOStandard("LVCMOS33"),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ["J6", "38 37 36 39 25 26 27 28 29 30 33 34 40 35 41 42 51 53 54 55 56 57 68 69"],
    ["J7", "63 86 85 84 83 82 81 80 79 77 76 75 74 73 72 71 70  - 48 49 31 32  -  -"],
]

# Platform -----------------------------------------------------------------------------------------

class Platform(GowinPlatform):
    default_clk_name   = "clk27"
    default_clk_period = 1e9/27e6

    def __init__(self, toolchain="gowin"):
        GowinPlatform.__init__(self, "GW1NR-LV9QN88PC6/I5", _io, _connectors, toolchain=toolchain, devicename="GW1NR-9C")
        self.toolchain.options["use_mspi_as_gpio"] = 1

    def create_programmer(self, kit="openfpgaloader"):
        if kit == "gowin":
            return GowinProgrammer(self.devicename)
        else: 
            return OpenFPGALoader(cable="ft2232")

    def do_finalize(self, fragment):
        GowinPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk27", loose=True), 1e9/27e6)
