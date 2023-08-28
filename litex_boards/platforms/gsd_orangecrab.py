#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Greg Davill <greg.davill@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.lattice import LatticeECP5Platform
from litex.build.dfu import DFUProg

# IOs ----------------------------------------------------------------------------------------------

_io_r0_1 = [
    # Clk / Rst
    ("clk48", 0,  Pins("A9"),  IOStandard("LVCMOS33")),
    ("rst_n", 0, Pins("R16"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led", 0, Pins("V17"), IOStandard("LVCMOS33")), # rgb_led.r
    ("user_led", 1, Pins("T17"), IOStandard("LVCMOS33")), # rgb_led.g
    ("user_led", 2, Pins("J3"),  IOStandard("LVCMOS33")), # rgb_led.b
    ("rgb_led", 0,
        Subsignal("r", Pins("V17"), IOStandard("LVCMOS33")),
        Subsignal("g", Pins("T17"), IOStandard("LVCMOS33")),
        Subsignal("b", Pins("J3"),  IOStandard("LVCMOS33")),
    ),

    # DDR3 SDRAM
    ("ddram", 0,
        Subsignal("a", Pins(
            "A4 D2 C3 C7 D3 D4 D1 B2",
            "C1 A2 A7 C2 C4"),
            IOStandard("SSTL135_I")),
        Subsignal("ba",    Pins("B6 B7 A6"), IOStandard("SSTL135_I")),
        Subsignal("ras_n", Pins("C12"),  IOStandard("SSTL135_I")),
        Subsignal("cas_n", Pins("D13"),  IOStandard("SSTL135_I")),
        Subsignal("we_n",  Pins("B12"),  IOStandard("SSTL135_I")),
        Subsignal("cs_n",  Pins("A12"),  IOStandard("SSTL135_I")),
        Subsignal("dm", Pins("D16 G16"), IOStandard("SSTL135_I")),
        Subsignal("dq", Pins(
            "C17 D15 B17 C16 A15 B13 A17 A13",
            "F17 F16 G15 F15 J16 C18 H16 F18"),
            IOStandard("SSTL135_I"),
            Misc("TERMINATION=75")),
        Subsignal("dqs_p", Pins("B15 G18"), IOStandard("SSTL135D_I"),
            Misc("TERMINATION=OFF DIFFRESISTOR=100")),
        Subsignal("clk_p", Pins("J18"), IOStandard("SSTL135D_I")),
        Subsignal("cke",   Pins("D6"),  IOStandard("SSTL135_I")),
        Subsignal("odt",   Pins("C13"), IOStandard("SSTL135_I")),
        Subsignal("reset_n", Pins("B1"), IOStandard("SSTL135_I")),
        Misc("SLEWRATE=FAST")
    ),

    # USB
    ("usb", 0,
        Subsignal("d_p", Pins("N1")),
        Subsignal("d_n", Pins("M2")),
        Subsignal("pullup", Pins("N2")),
        IOStandard("LVCMOS33")
    ),

    # SPIFlash
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("U17")),
        #Subsignal("clk",  Pins("U16")),
        Subsignal("dq",   Pins("U18 T18 R18 N18")),
        IOStandard("LVCMOS33")
    ),

    # SPI
    ("spi-internal", 0,
        Subsignal("cs_n",   Pins("B11"), Misc("PULLMODE=UP")),
        Subsignal("clk",    Pins("C11")),
        Subsignal("miso",   Pins("A11"), Misc("PULLMODE=UP")),
        Subsignal("mosi",   Pins("A10"), Misc("PULLMODE=UP")),
        Misc("SLEWRATE=SLOW"),
        IOStandard("LVCMOS33"),
    ),

    # SDCard
    ("spisdcard", 0,
        Subsignal("clk",  Pins("K1")),
        Subsignal("mosi", Pins("K2"), Misc("PULLMODE=UP")),
        Subsignal("cs_n", Pins("M1"), Misc("PULLMODE=UP")),
        Subsignal("miso", Pins("J1"), Misc("PULLMODE=UP")),
        Misc("SLEWRATE=FAST"),
        IOStandard("LVCMOS33"),
    ),
]

_io_r0_2 = [
    # Clk / Rst
    ("clk48", 0, Pins("A9"),  IOStandard("LVCMOS33")),
    ("rst_n", 0, Pins("V17"), IOStandard("LVCMOS33")),

    # Buttons
    ("usr_btn", 0, Pins("J17"), IOStandard("SSTL135_I")),

    # Leds
    ("user_led", 0, Pins("K4"), IOStandard("LVCMOS33")), # rgb_led.r
    ("user_led", 1, Pins("M3"), IOStandard("LVCMOS33")), # rgb_led.g
    ("user_led", 2, Pins("J3"), IOStandard("LVCMOS33")), # rgb_led.b
    ("rgb_led", 0,
        Subsignal("r", Pins("K4"), IOStandard("LVCMOS33")),
        Subsignal("g", Pins("M3"), IOStandard("LVCMOS33")),
        Subsignal("b", Pins("J3"), IOStandard("LVCMOS33")),
    ),

    # DDR3 SDRAM
    ("ddram", 0,
        Subsignal("a", Pins(
            "C4 D2 D3 A3 A4 D4 C3 B2",
            "B1 D1 A7 C2 B6 C1 A2 C7"),
            IOStandard("SSTL135_I")),
        Subsignal("ba",    Pins("D6 B7 A6"), IOStandard("SSTL135_I"),),
        Subsignal("ras_n", Pins("C12"), IOStandard("SSTL135_I")),
        Subsignal("cas_n", Pins("D13"), IOStandard("SSTL135_I")),
        Subsignal("we_n",  Pins("B12"), IOStandard("SSTL135_I")),
        Subsignal("cs_n",  Pins("A12"), IOStandard("SSTL135_I")),
        Subsignal("dm", Pins("D16 G16"), IOStandard("SSTL135_I")),
        Subsignal("dq", Pins(
            "C17 D15 B17 C16 A15 B13 A17 A13",
            "F17 F16 G15 F15 J16 C18 H16 F18"),
            IOStandard("SSTL135_I"),
            Misc("TERMINATION=OFF")), # Misc("TERMINATION=75") Disabled to reduce heat
        Subsignal("dqs_p", Pins("B15 G18"), IOStandard("SSTL135D_I"),
            Misc("TERMINATION=OFF"),
            Misc("DIFFRESISTOR=100")),
        Subsignal("clk_p", Pins("J18"), IOStandard("SSTL135D_I")),
        Subsignal("cke",   Pins("D18"), IOStandard("SSTL135_I")),
        Subsignal("odt",   Pins("C13"), IOStandard("SSTL135_I")),
        Subsignal("reset_n", Pins("L18"), IOStandard("SSTL135_I")),
        Subsignal("vccio", Pins("K16 D17 K15 K17 B18 C6"), IOStandard("SSTL135_II")),
        Subsignal("gnd",   Pins("L15 L16"), IOStandard("SSTL135_II")),
        Misc("SLEWRATE=FAST")
    ),

    # USB
    ("usb", 0,
        Subsignal("d_p", Pins("N1")),
        Subsignal("d_n", Pins("M2")),
        Subsignal("pullup", Pins("N2")),
        IOStandard("LVCMOS33")
    ),

    # SPIFlash
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("U17"), IOStandard("LVCMOS33")),
        #Subsignal("clk",  Pins("U16"), IOStandard("LVCMOS33")),
        Subsignal("dq",   Pins("U18 T18 R18 N18"), IOStandard("LVCMOS33")),
    ),
    ("spiflash", 0,
        Subsignal("cs_n", Pins("U17"), IOStandard("LVCMOS33")),
        #Subsignal("clk",  Pins("U16"), IOStandard("LVCMOS33")), # Note: CLK is bound using USRMCLK block
        Subsignal("miso", Pins("T18"), IOStandard("LVCMOS33")),
        Subsignal("mosi", Pins("U18"), IOStandard("LVCMOS33")),
        Subsignal("wp",   Pins("R18"), IOStandard("LVCMOS33")),
        Subsignal("hold", Pins("N18"), IOStandard("LVCMOS33")),
    ),

    # SDCard
    ("spisdcard", 0,
        Subsignal("clk",  Pins("K1")),
        Subsignal("mosi", Pins("K2"), Misc("PULLMODE=UP")),
        Subsignal("cs_n", Pins("M1"), Misc("PULLMODE=UP")),
        Subsignal("miso", Pins("J1"), Misc("PULLMODE=UP")),
        Misc("SLEWRATE=FAST"),
        IOStandard("LVCMOS33"),
    ),

    ("sdcard", 0,
        Subsignal("clk",  Pins("K1")),
        Subsignal("cmd",  Pins("K2"), Misc("PULLMODE=UP")),
        Subsignal("data", Pins("J1 K3 L3 M1"), Misc("PULLMODE=UP")),
        IOStandard("LVCMOS33"), Misc("SLEWRATE=FAST")
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors_r0_1 = [
    # Feather 0.1" Header Pin Numbers,
    # Note: Pin nubering is not continuous.
    ("GPIO", "N17 M18 C10 C9 - B10 B9 - - C8 B8 A8 H2 J2 N15 R17 N16 - - - - - - - -"),
]

_connectors_r0_2 = [
    # Feather 0.1" Header Pin Numbers,
    # Note: Pin nubering is not continuous.
    ("GPIO", "N17 M18 C10 C9 - B10 B9 - - C8 B8 A8 H2 J2 N15 R17 N16 - L4 N3 N4 H4 G4 T17"),
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
    ("spi", 0,
        Subsignal("miso", Pins("GPIO:14"), IOStandard("LVCMOS33")),
        Subsignal("mosi", Pins("GPIO:16"), IOStandard("LVCMOS33")),
        Subsignal("clk",  Pins("GPIO:15"), IOStandard("LVCMOS33"))
    )
]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticeECP5Platform):
    default_clk_name   = "clk48"
    default_clk_period = 1e9/48e6

    def __init__(self, revision="0.2", device="25F", toolchain="trellis", **kwargs):
        assert revision in ["0.1", "0.2"]
        assert device in ["25F", "45F", "85F"]
        self.revision = revision
        io         = {"0.1": _io_r0_1,            "0.2": _io_r0_2        }[revision]
        connectors = {"0.1": _connectors_r0_1,    "0.2": _connectors_r0_2}[revision]
        LatticeECP5Platform.__init__(self, f"LFE5U-{device}-8MG285C", io, connectors, toolchain=toolchain, **kwargs)

    def create_programmer(self):
        return DFUProg(vid="1209", pid="5af0", alt=0)

    def do_finalize(self, fragment):
        LatticeECP5Platform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk48", loose=True), 1e9/48e6)
