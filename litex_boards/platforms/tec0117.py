#!/usr/bin/env python3

from migen import *

from litex.build.generic_platform import *
from litex.build.gowin.platform import GowinPlatform
from litex.build.openfpgaloader import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk12", 0, Pins("35"), IOStandard("LVCMOS33")),
    ("rst",   0, Pins("77"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led", 0, Pins("86"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("85"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("84"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("83"), IOStandard("LVCMOS33")),
    ("user_led", 4, Pins("82"), IOStandard("LVCMOS33")),
    ("user_led", 5, Pins("81"), IOStandard("LVCMOS33")),
    ("user_led", 6, Pins("80"), IOStandard("LVCMOS33")),
    ("user_led", 7, Pins("79"), IOStandard("LVCMOS33")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("15"), IOStandard("LVCMOS33")),
        Subsignal("rx", Pins("16"), IOStandard("LVCMOS33"))
    ),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("51"), IOStandard("LVCMOS33")),
        Subsignal("clk",  Pins("49"), IOStandard("LVCMOS33")),
        Subsignal("miso", Pins("53"), IOStandard("LVCMOS33")),
        Subsignal("mosi", Pins("48"), IOStandard("LVCMOS33")),
        Subsignal("wp",   Pins("54"), IOStandard("LVCMOS33")),
        Subsignal("hold", Pins("50"), IOStandard("LVCMOS33")),
    ),

    # SPIFlash (FTDI Chip)
    ("spiflash", 1,
        Subsignal("cs_n", Pins("13"), IOStandard("LVCMOS33")),
        Subsignal("clk",  Pins("16"), IOStandard("LVCMOS33")),
        Subsignal("miso", Pins("14"), IOStandard("LVCMOS33")),
        Subsignal("mosi", Pins("15"), IOStandard("LVCMOS33")),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("PMOD", "47 41 38 40 - - 36 42 39 37"),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(GowinPlatform):
    default_clk_name   = "clk12"
    default_clk_period = 1e9/12e6

    def __init__(self):
        GowinPlatform.__init__(self, "GW1NR-LV9QN88C6/I5", _io, toolchain="gowin", devicename='GW1NR-9')

    def create_programmer(self):
        return OpenFPGALoader("littlebee")
