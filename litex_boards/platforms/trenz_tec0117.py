#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Pepijn de Vos <pepijndevos@gmail.com>
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.build.generic_platform import *
from litex.build.gowin.platform import GowinPlatform
from litex.build.openfpgaloader import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk12",  0, Pins("35"), IOStandard("LVCMOS33")),
    ("clk100", 0, Pins("63"), IOStandard("LVCMOS33")),
    ("rst_n",  0, Pins("77"), IOStandard("LVCMOS33")),

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
        Subsignal("rx", Pins("16"), IOStandard("LVCMOS33")),
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
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("51")),
        Subsignal("clk",  Pins("49")),
        Subsignal("dq",   Pins("48 53 54 50")),
        IOStandard("LVCMOS33")
    ),

    # SPIFlash (FTDI Chip)
    ("spiflash", 1,
        Subsignal("cs_n", Pins("13"), IOStandard("LVCMOS33")),
        Subsignal("clk",  Pins("16"), IOStandard("LVCMOS33")),
        Subsignal("miso", Pins("14"), IOStandard("LVCMOS33")),
        Subsignal("mosi", Pins("15"), IOStandard("LVCMOS33")),
    ),

    # SDRAM (embedded in SIP, requires specific IO naming)
    ("O_sdram_clk",   0, Pins(1),  IOStandard("LVCMOS33")),
    ("O_sdram_cke",   0, Pins(1),  IOStandard("LVCMOS33")),
    ("O_sdram_cs_n",  0, Pins(1),  IOStandard("LVCMOS33")),
    ("O_sdram_cas_n", 0, Pins(1),  IOStandard("LVCMOS33")),
    ("O_sdram_ras_n", 0, Pins(1),  IOStandard("LVCMOS33")),
    ("O_sdram_wen_n", 0, Pins(1),  IOStandard("LVCMOS33")),
    ("O_sdram_dqm",   0, Pins(2),  IOStandard("LVCMOS33")),
    ("O_sdram_addr",  0, Pins(12), IOStandard("LVCMOS33")),
    ("O_sdram_ba",    0, Pins(2),  IOStandard("LVCMOS33")),
    ("IO_sdram_dq",   0, Pins(16), IOStandard("LVCMOS33")),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("pmod", "47 41 38 40 36 42 39 37"),
]

# PMODs --------------------------------------------------------------------------------------------

def sdcard_pmod_io(pmod):
    return [
        # SDCard PMOD:
        # - https://store.digilentinc.com/pmod-microsd-microsd-card-slot/
        # - https://github.com/antmicro/arty-expansion-board
        ("spisdcard", 0,
            Subsignal("clk",  Pins(f"{pmod}:3")),
            Subsignal("mosi", Pins(f"{pmod}:1"), Misc("PULL_MODE=UP")),
            Subsignal("cs_n", Pins(f"{pmod}:0"), Misc("PULL_MODE=UP")),
            Subsignal("miso", Pins(f"{pmod}:2"), Misc("PULL_MODE=UP")),
            IOStandard("LVCMOS33"),
        ),
        ("sdcard", 0,
            Subsignal("data", Pins(f"{pmod}:2 {pmod}:4 {pmod}:5 {pmod}:0"), Misc("PULL_MODE=UP")),
            Subsignal("cmd",  Pins(f"{pmod}:1"), Misc("PULL_MODE=UP")),
            Subsignal("clk",  Pins(f"{pmod}:3")),
            Subsignal("cd",   Pins(f"{pmod}:6")),
            IOStandard("LVCMOS33"),
        ),
]
_sdcard_pmod_io = sdcard_pmod_io("pmod")

# Platform -----------------------------------------------------------------------------------------

class Platform(GowinPlatform):
    default_clk_name   = "clk12"
    default_clk_period = 1e9/12e6

    def __init__(self, toolchain="gowin"):
        GowinPlatform.__init__(self, "GW1NR-LV9QN88C6/I5", _io, _connectors, toolchain=toolchain, devicename="GW1NR-9")

    def create_programmer(self):
        return OpenFPGALoader("littleBee")

    def do_finalize(self, fragment):
        GowinPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk12",  loose=True), 1e9/12e6)
        self.add_period_constraint(self.lookup_request("clk100", loose=True), 1e9/100e6)
