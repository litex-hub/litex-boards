#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Goran Mahovlic <goran.mahovlic@gmail.com>
# Copyright (c) 2020 Greg Davill <greg.davill@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.lattice import LatticeECP5Platform
#from litex.build.dfu import DFUProg

# IOs ----------------------------------------------------------------------------------------------

_io_r0_1 = [
    # Clk/Rst.
    ("clk25", 0, Pins("G2"), IOStandard("LVCMOS33")),
    ("rst_n", 0, Pins("F1"), IOStandard("LVCMOS33")),

    # RGB Led.
    ("rgb_led", 0,
        Subsignal("r", Pins("A3"), IOStandard("LVCMOS33")),
        Subsignal("g", Pins("B3"), IOStandard("LVCMOS33")),
        Subsignal("b", Pins("B2"),  IOStandard("LVCMOS33")),
    ),

    # Buttons.
    ("user_btn", 0, Pins("E1"), IOStandard("LVCMOS33")),

    # Leds.
    ("user_led", 0, Pins("A3"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("B3"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("B2"),  IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("C3"), IOStandard("LVCMOS33")),
    ("user_led", 4, Pins("C2"), IOStandard("LVCMOS33")),
    ("user_led", 5, Pins("C1"),  IOStandard("LVCMOS33")),
    ("user_led", 6, Pins("D1"), IOStandard("LVCMOS33")),
    ("user_led", 7, Pins("D3"), IOStandard("LVCMOS33")),

    # DDR3 SDRAM.
    ("ddram", 0,
        Subsignal("a", Pins(
            "F18 L17 D19 E18 H16 T20 U17 T17",
            "E16 U19 J17 J16 P17 U20 N20 P18"),
            IOStandard("SSTL135_I")),
        Subsignal("ba",    Pins("P19 G16 P20"), IOStandard("SSTL135_I")),
        Subsignal("ras_n", Pins("R20"),  IOStandard("SSTL135_I")),
        Subsignal("cas_n", Pins("F20"),  IOStandard("SSTL135_I")),
        Subsignal("we_n",  Pins("H17"),  IOStandard("SSTL135_I")),
        Subsignal("cs_n",  Pins("H18"),  IOStandard("SSTL135_I")),
        Subsignal("dm", Pins("F16 U16"), IOStandard("SSTL135_I")),
        Subsignal("dq", Pins(
            "R17 L19 R16 L16 M18 M19 N18 N17",
            "J19 C20 F19 E20 J18 K19 E19 G20"),
            IOStandard("SSTL135_I"),
            Misc("TERMINATION=75")), # Disable to reduce heat.
        Subsignal("dqs_p", Pins("N16 G19"), IOStandard("SSTL135D_I"),
            Misc("TERMINATION=OFF DIFFRESISTOR=100")),
        Subsignal("clk_p",   Pins("L20"), IOStandard("SSTL135D_I")),
        Subsignal("cke",     Pins("N19"),  IOStandard("SSTL135_I")),
        Subsignal("odt",     Pins("T19"), IOStandard("SSTL135_I")),
        Subsignal("reset_n", Pins("T18"), IOStandard("SSTL135_I")),
        Misc("SLEWRATE=FAST")
    ),

    # USB.
    ("usb", 0,
        Subsignal("d_p",    Pins("F4")),
        Subsignal("d_n",    Pins("E3")),
        Subsignal("pullup", Pins("F5")),
        IOStandard("LVCMOS33")
    ),

    # Serial.
    ("serial", 0,
        Subsignal("rx", Pins("N4"), Misc("PULLMODE=UP"),   IOStandard("LVCMOS33")),
        Subsignal("tx", Pins("N3"), Misc("PULLMODE=NONE"), IOStandard("LVCMOS33")),
        Subsignal("tx_enable", Pins("T1"), Misc("PULLMODE=UP")),
        IOStandard("LVCMOS33")
    ),

    # SPIFlash.
    ("spiflash", 0,
        Subsignal("cs_n", Pins("R2")),
        Subsignal("miso", Pins("V2")),
        Subsignal("mosi", Pins("W2")),
        Subsignal("wp", Pins("Y2")),
        Subsignal("hold", Pins("W1")),
        IOStandard("LVCMOS33")
    ),
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("R2")),
        Subsignal("dq", Pins("W2", "V2", "Y2", "W1")),
        IOStandard("LVCMOS33")
    ),

    # SDCard.
    ("sdcard", 0,
        Subsignal("clk",  Pins("G1")),
        Subsignal("cmd",  Pins("P1"), Misc("PULLMODE=UP")),
        Subsignal("data", Pins("B15 B18 E14 P2"), Misc("PULLMODE=UP")),
        IOStandard("LVCMOS33"), Misc("SLEW=FAST")
    ),

    # GPDI
    ("gpdi", 0,
        Subsignal("clk_p",    Pins("J20"), IOStandard("SSTL135D_I"), Misc("DRIVE=4")),
        #Subsignal("clk_n",   Pins("B18"), IOStandard("LVCMOS33D"), Misc("DRIVE=4")),
        Subsignal("data0_p",  Pins("F17"), IOStandard("SSTL135D_I"), Misc("DRIVE=4")),
        #Subsignal("data0_n", Pins("A13"), IOStandard("LVCMOS33D"), Misc("DRIVE=4")),
        Subsignal("data1_p",  Pins("D18"), IOStandard("SSTL135D_I"), Misc("DRIVE=4")),
        #Subsignal("data1_n", Pins("C14"), IOStandard("LVCMOS33D"), Misc("DRIVE=4")),
        Subsignal("data2_p",  Pins("C18"), IOStandard("SSTL135D_I"), Misc("DRIVE=4")),
        #Subsignal("data2_n", Pins("B16"), IOStandard("LVCMOS33D"), Misc("DRIVE=4")),
        #Subsignal("cec",     Pins("A18"), IOStandard("LVCMOS33"), Misc("PULLMODE=UP")),
        #Subsignal("scl",     Pins("E19"), IOStandard("LVCMOS33"), Misc("PULLMODE=UP")),
        #Subsignal("sda",     Pins("B19"), IOStandard("LVCMOS33"), Misc("PULLMODE=UP"))
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors_r0_1 = [
    # Feather 0.1" Header Pin Numbers,
    # Note: Pin nubering is not continuous.
    ("GPIO", "P16 P17"),
]

_connectors_r0_2 = [
    # Feather 0.1" Header Pin Numbers,
    # Note: Pin nubering is not continuous.
    ("GPIO", "P16 P17 K5 J5 - K4 H16 - - R1 P3 P4 G16 N17 L16 C4 T1 - - - - - - - -"),
]


# Standard Feather Pins
feather_serial = [
    ("serial", 0,
        Subsignal("tx", Pins("GPIO:1"), IOStandard("LVCMOS33")),
        Subsignal("rx", Pins("GPIO:0"), IOStandard("LVCMOS33"))
    )
]

feather_i2c = [
    ("i2c", 0,
        Subsignal("sda", Pins("GPIO:2"), IOStandard("LVCMOS33")),
        Subsignal("scl", Pins("GPIO:3"), IOStandard("LVCMOS33"))
    )
]

feather_spi = [
    ("spi",0,
        Subsignal("miso", Pins("GPIO:14"), IOStandard("LVCMOS33")),
        Subsignal("mosi", Pins("GPIO:16"), IOStandard("LVCMOS33")),
        Subsignal("sck",  Pins("GPIO:15"), IOStandard("LVCMOS33"))
    )
]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticeECP5Platform):
    default_clk_name   = "clk25"
    default_clk_period = 1e9/25e6

    def __init__(self, revision="0.1", device="85F", **kwargs):
        assert revision in ["0.1"]
        self.revision = revision
        io         = {"0.1": _io_r0_1}[revision]
        connectors = {"0.1": _connectors_r0_1}[revision]
        LatticeECP5Platform.__init__(self, f"LFE5UM5G-{device}-8BG381C", io, connectors, **kwargs)

#    def create_programmer(self):
#        return DFUProg(vid="1209", pid="5af0")

    def do_finalize(self, fragment):
        LatticeECP5Platform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk25", loose=True), 1e9/25e6)
