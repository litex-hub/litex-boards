#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Andrew Dennison <andrew@motec.com.au>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.efinix.platform import EfinixPlatform
from litex.build.openfpgaloader import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk
    ("clk33", 0, Pins("C3"), IOStandard("3.3_V_LVTTL_/_LVCMOS")),  # net PLL_IN

    # Buttons
    ("user_btn", 0, Pins("C5"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("WEAK_PULLUP")),
    ("user_btn", 1, Pins("C9"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("WEAK_PULLUP")),

    # Leds
    ("user_led", 0, Pins("B3"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=3")),
    ("user_led", 1, Pins("J6"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=3")),
    ("user_led", 2, Pins("D7"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=3")),
    ("user_led", 3, Pins("D8"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=3")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("F3")),  # net TXD
        Subsignal("rx", Pins("H2")),  # net RXD
        IOStandard("3.3_V_LVTTL_/_LVCMOS")
     ),

    # SPIFlash (W25Q128JVSIM)
    ("spiflash", 0,
        Subsignal("cs_n", Pins("J4")),  # net SPI_SS
        Subsignal("clk",  Pins("H4")),  # net SPI_SCLK
        Subsignal("mosi", Pins("F4")),  # net SPI_MOSI
        Subsignal("miso", Pins("H3")),  # net SPI_MISO
        #Subsignal("wp",   Pins("")),
        #Subsignal("hold", Pins("")),
        IOStandard("3.3_V_LVTTL_/_LVCMOS")
     ),

    # SDCard
    ("spisdcard", 0,
        # All 4 SPI signals below have 10k pullup on dev board
        Subsignal("clk",  Pins("J2")),  # net SD_SCLK
        Subsignal("cs_n", Pins("G5")),  # net SD_CS
        Subsignal("mosi", Pins("G4")),  # net SD_DI
        Subsignal("miso", Pins("J3")),  # net SD_DO
        Subsignal("det",  Pins("G3")),  # net CD2
        Misc("SLEW=FAST"),
        IOStandard("3.3_V_LVTTL_/_LVCMOS")
     ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    # Wacky PMOD pinout misunderstood by others too
    # resulting in this order: GPIOL_12,14,16,19,13,15,17,18
    ("pmod", "G1 E2 C2 D3 F1 E1 D2 E3"),
    # GPIOR_020..28, 30..32, 34..36
    ("j1", "F8 E7 F7 E6 F6 F5 G9 H9 J9 J8 G8 H8 J7 G6 H6"),
    # GPIOR_19..10, 08..05, 03, 01, 00
    ("j2", "E8 D9 D8 D7 C9 B9 D6 C8 B8 A9 A8 C7 C6 B6 A6 B5 A5"),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(EfinixPlatform):
    default_clk_name = "clk33"
    default_clk_period = 1e9/33.333e6

    def __init__(self, toolchain="efinity"):
        EfinixPlatform.__init__(self, "T8F81C2", _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        return OpenFPGALoader("xyloni_spi")

    def do_finalize(self, fragment):
        EfinixPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk33", loose=True), 1e9/33.333e6)
