#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Franck Jullien <franck.jullien@collshade.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.efinix.platform import EfinixPlatform
from litex.build.efinix import EfinixProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk
    ("clk25", 0, Pins("B2"), IOStandard("1.8_V_LVCMOS")),
    ("clk33", 0, Pins("P2"), IOStandard("1.8_V_LVCMOS")),
    ("clk74_25", 0, Pins("A11"), IOStandard("1.8_V_LVCMOS")),

    # SD-Card
    ("spisdcard", 0,
        Subsignal("clk",  Pins("B12")),
        Subsignal("mosi", Pins("C12"), Misc("WEAK_PULLUP")),
        Subsignal("cs_n", Pins("A12"), Misc("WEAK_PULLUP")),
        Subsignal("miso", Pins("B14"), Misc("WEAK_PULLUP")),
        IOStandard("1.8_V_LVCMOS"),
    ),
    ("sdcard", 0,
        Subsignal("data", Pins("B14 A14 D12 A12"), Misc("WEAK_PULLUP")),
        Subsignal("cmd",  Pins("C12"), Misc("WEAK_PULLUP")),
        Subsignal("clk",  Pins("B12")),
        IOStandard("3.3_V_LVCMOS"),
    ),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("R4")),
        Subsignal("rx", Pins("R3")),
        IOStandard("3.3_V_LVCMOS"), Misc("WEAK_PULLUP")
    ),

    # Leds
    ("user_led", 0,
        Subsignal("r", Pins("J15")),
        Subsignal("g", Pins("H10")),
        Subsignal("b", Pins("K14")),
        IOStandard("1.8_V_LVCMOS"),
    ),
    ("user_led", 1,
        Subsignal("r", Pins("H15")),
        Subsignal("g", Pins("H11")),
        Subsignal("b", Pins("J14")),
        IOStandard("1.8_V_LVCMOS"),
    ),

    # Buttons
    ("user_btn", 0, Pins("K13"), IOStandard("1.8_V_LVCMOS")),
    ("user_btn", 1, Pins("J13"), IOStandard("1.8_V_LVCMOS")),
    ("user_btn", 2, Pins("C5"),  IOStandard("1.8_V_LVCMOS")),
    ("user_btn", 3, Pins("R13"), IOStandard("1.8_V_LVCMOS")),

    # Switches
    ("user_sw", 0, Pins("F3"), IOStandard("1.8_V_LVCMOS")),
    ("user_sw", 1, Pins("E3"), IOStandard("1.8_V_LVCMOS")),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("P1")),
        Subsignal("clk",  Pins("N1")),
        Subsignal("mosi", Pins("M1")),
        Subsignal("miso", Pins("L1")),
        IOStandard("1.8_V_LVCMOS")
    ),

    # HyperRAM (X16)
    ("hyperram", 0,
        Subsignal("dq",  Pins(
            "B6 C6 A5 A6  F7  F8  E7  D7",
            "B9 A9 F9 E9 C10 D10 A10 B10"
        ), IOStandard("1.8_V_LVCMOS")),
        Subsignal("rwds",  Pins("B8 C8"), IOStandard("1.8_V_LVCMOS")),
        Subsignal("cs_n",  Pins("A8"),    IOStandard("1.8_V_LVCMOS")),
        Subsignal("rst_n", Pins("D5"),    IOStandard("1.8_V_LVCMOS")),
        Subsignal("clk",   Pins("B7"),    IOStandard("1.8_V_LVCMOS")),
        Misc("SLEWRATE=FAST")
    ),

    # MIPI
    ("mipi_tx", 0,
        Subsignal("clk",   Pins("D13"), IOStandard("1.2_V_LVCMOS")),
        Subsignal("data0", Pins("C15"), IOStandard("1.2_V_LVCMOS")),
        Subsignal("data1", Pins("D14"), IOStandard("1.2_V_LVCMOS")),
        Subsignal("data2", Pins("E14"), IOStandard("1.2_V_LVCMOS")),
        Subsignal("data3", Pins("E12"), IOStandard("1.2_V_LVCMOS")),
        Misc("SLEWRATE=FAST")
    ),

    # MIPI
    ("mipi_rx", 0,
        Subsignal("clk",   Pins("M15"), IOStandard("1.2_V_LVCMOS")),
        Subsignal("data0", Pins("K11"), IOStandard("1.2_V_LVCMOS")),
        Subsignal("data1", Pins("L13"), IOStandard("1.2_V_LVCMOS")),
        Misc("SLEWRATE=FAST")
    ),

    ("cam_i2c", 0,
        Subsignal("sda",   Pins("H4"), Misc("WEAK_PULLUP")),
        Subsignal("scl",   Pins("H5"), Misc("WEAK_PULLUP")),
        Subsignal("reset", Pins("R14")),
        IOStandard("1.8_V_LVCMOS")
    ),
]

iobank_info = [
            ("1A", "1.8 V LVCMOS"),
            ("1B", "1.8 V LVCMOS"),
            ("2A", "1.8 V LVCMOS"),
            ("2B", "1.8 V LVCMOS"),
            ("3A", "1.2 V LVCMOS"),
            ("3B", "1.2 V LVCMOS"),
            ("4A", "1.2 V LVCMOS"),
            ("4B", "1.2 V LVCMOS"),
            ("BL", "1.8 V LVCMOS"),
            ("BR", "1.8 V LVCMOS"),
            ("TL", "1.8 V LVCMOS"),
            ("TR", "1.8 V LVCMOS"),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ["P1", " - H14 - G14 - - F12 G13 E12 F13 - - E15 H13 E14 H12 - - C13 G15 D13 F15",
           " - - D15 G11 D14 F11 - - C14 N14 C15 P14 - - K4 A4 J3 B5"],
]

# Platform -----------------------------------------------------------------------------------------

class Platform(EfinixPlatform):
    default_clk_name   = "clk25"
    default_clk_period = 1e9/50e6

    def __init__(self, toolchain="efinity"):
        EfinixPlatform.__init__(self, "Ti60F225C3", _io, _connectors, iobank_info=iobank_info, toolchain=toolchain)

    def create_programmer(self):
        return EfinixProgrammer()

    def do_finalize(self, fragment):
        EfinixPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk25", loose=True), 1e9/50e6)
