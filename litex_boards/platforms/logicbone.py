#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Owen Kirby <oskirby@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause
#
# Logicbone ECP5:
# - Design files: https://github.com/oskirby/logicbone
# - Bootloader: https://github.com/oskirby/tinydfu-bootloader
#

from litex.build.generic_platform import *
from litex.build.lattice import LatticePlatform
from litex.build.dfu import DFUProg

# IOs ----------------------------------------------------------------------------------------------

_io_rev0 = [
    # Clk / Rst
    ("clk25", 0, Pins("M19"),  IOStandard("LVCMOS18")),
    ("rst_n",  0, Pins("C17"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led", 0, Pins("D16"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("C15"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("C13"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("B13"), IOStandard("LVCMOS33")),

    # Buttons
    ("user_btn", 0, Pins("U2"), IOStandard("LVCMOS33")),

    # DDR3 SDRAM
    ("ddram", 0,
        Subsignal("a", Pins(
            "D5 F4 B3 F3 E5 C3 C4 A5",
            "A3 B5 G3 F5 D2 A4 D3 E3"),
            IOStandard("SSTL135_I")),
        Subsignal("ba",    Pins("B4 H5 N2"), IOStandard("SSTL135_I")),
        Subsignal("ras_n", Pins("L1"), IOStandard("SSTL135_I")),
        Subsignal("cas_n", Pins("M1"), IOStandard("SSTL135_I")),
        Subsignal("we_n",  Pins("E4"), IOStandard("SSTL135_I")),
        Subsignal("cs_n",  Pins("M3"), IOStandard("SSTL135_I")),
        #Subsignal("dm", Pins("L4 J5"), IOStandard("SSTL135_I")),
        Subsignal("dm", Pins("L5 H3"), IOStandard("SSTL135_I")), # HACK: I broke the DM pins, so we'll use some NC pins instead.
        Subsignal("dq", Pins(
            "G2 K1 F1 K3 H2 J3 G1 H1",
            "B1 E1 A2 F2 C1 E2 C2 D1"),
            IOStandard("SSTL135_I"),
            Misc("TERMINATION=75")),
        Subsignal("dqs_p", Pins("K2 H4"), IOStandard("SSTL135D_I"),
            Misc("TERMINATION=OFF"),
            Misc("DIFFRESISTOR=100")),
        Subsignal("clk_p", Pins("M4"), IOStandard("SSTL135D_I")),
        Subsignal("cke",   Pins("K4"), IOStandard("SSTL135_I")),
        Subsignal("odt",   Pins("C5"), IOStandard("SSTL135_I")),
        Subsignal("reset_n", Pins("P1"), IOStandard("SSTL135_I")),
        Misc("SLEWRATE=FAST"),
    ),

    # USB
    ("usb", 0,
        Subsignal("d_p", Pins("B12")),
        Subsignal("d_n", Pins("C12")),
        Subsignal("pullup", Pins("C16")),
        IOStandard("LVCMOS33")
    ),

    # Serial
    ("serial", 0,
        Subsignal("rx", Pins("B6"), IOStandard("LVCMOS33")),
        Subsignal("tx", Pins("A7"), IOStandard("LVCMOS33")),
    ),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("R2"), IOStandard("LVCMOS33")),
        #Subsignal("clk",  Pins("U3"), IOStandard("LVCMOS33")), # Note: CLK is bound using USRMCLK block
        Subsignal("miso", Pins("V2"), IOStandard("LVCMOS33")),
        Subsignal("mosi", Pins("W2"), IOStandard("LVCMOS33")),
        Subsignal("wp",   Pins("Y2"), IOStandard("LVCMOS33")),
        Subsignal("hold", Pins("W1"), IOStandard("LVCMOS33")),
    ),
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("R2"), IOStandard("LVCMOS33")),
        #Subsignal("clk",  Pins("U3"), IOStandard("LVCMOS33")), # Note: CLK is bound using USRMCLK block
        Subsignal("dq",   Pins("W2 V2 Y2 W1"), IOStandard("LVCMOS33")),
    ),

    # SDCard
    ("spisdcard", 0,
        Subsignal("clk",  Pins("E11")),
        Subsignal("mosi", Pins("D15"), Misc("PULLMODE=UP")),
        Subsignal("cs_n", Pins("E14"), Misc("PULLMODE=UP")),
        Subsignal("miso", Pins("D13"), Misc("PULLMODE=UP")),
        Misc("SLEWRATE=FAST"),
        IOStandard("LVCMOS33"),
    ),
    ("sdcard", 0,
        Subsignal("clk",  Pins("E11")),
        Subsignal("cmd",  Pins("D15"), Misc("PULLMODE=UP")),
        Subsignal("data", Pins("D13 E13 E15 E14"), Misc("PULLMODE=UP")),
        Subsignal("cd",   Pins("D14"), Misc("PULLMODE=UP")),
        IOStandard("LVCMOS33"), Misc("SLEWRATE=FAST")
    ),

    # I2C
    ("i2c", 0,
        Subsignal("sda", Pins("V1")),
        Subsignal("scl", Pins("U1")),
        IOStandard("LVCMOS33")
    ),

    # RGMII Ethernet
    ("eth_clocks", 0,
        Subsignal("tx", Pins("A15")),
        Subsignal("rx", Pins("B18")),
        Subsignal("ref", Pins("A19")),
        IOStandard("LVCMOS33")
    ),

    ("eth", 0,
        #Subsignal("rst_n",   Pins("U17")), # Stolen for SYS_RESETn on prototypes.
        Subsignal("int_n",   Pins("B20"), Misc("PULLMODE=UP")), # HACK: Should have a pullup on the board.
        Subsignal("mdio",    Pins("B19"), Misc("PULLMODE=UP")), # HACK: Should have a pullup on the board.
        Subsignal("mdc",     Pins("D12")),
        Subsignal("tx_ctl",  Pins("B15")),
        Subsignal("tx_data", Pins("A12 A13 C14 A14")),
        Subsignal("rx_ctl",  Pins("A18")),
        Subsignal("rx_data", Pins("B17 A17 B16 A16")),
        IOStandard("LVCMOS33")
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors_rev0 = [
    ("P8",
        "None",         # No pin 0
        "None", "None", # GND
        "C20", "D19",   # P8_LVDS1
        "D20", "E19",   # P8_LVDS2
        "E20", "F19",   # P8_LVDS3
        "F20", "G20",   # P8_LVDS4
        "None", "None",
        "None", "None",
        "None", "None",
        "None", "None",
        "None", "None",
        "None", "None",
        "G19", "H20",   # P8_LVDS5
        "J20", "K20",   # P8_LVDS6
        "C18", "D17",   # P8_LVDS7
        "D18", "E17",   # P8_LVDS8
        "E18", "F18",   # P8_LVDS9
        "F17", "G18",   # P8_LVDS10
        "E16", "F16",   # P8_LVDS11
        "G16", "H16",   # P8_LVDS12
        "J17", "J16",   # P8_LVDS13
        "H18", "H17",   # P8_LVDS14
        "J19", "K19",   # P8_LVDS15
        "J18", "K18"),  # P8_LVDS16
    ("P9",
        "None",         # No pin 0
        "None", "None", # GND
        "None", "None", # VCC3V3
        "None", "None", # CAPE_5V
        "None", "None", # VBUS
        "None", "None", # PWR_BUTTON, SYS_RESETn
        "A11", "B11",   # GPIO11, GPIO12
        "A10", "C10",   # GPIO13, GPIO14
        "A9",  "B9",    # GPIO15, GPIO16
        "C11", "A8",    # GPIO17, GPIO18
        "None", "None", # I2C Bus
        "D9",  "C8",    # GPIO21, GPIO22
        "B8",  "A7",    # GPIO23, GPIO24
        "A6",  "B6",    # GPIO25, GPIO26
        "D8",  "C7",    # GPIO27, P9_SPI_CSEL
        "D7",  "C6",    # P9_SPI_D0, P9_SPI_D1
        "D6",  "None",  # P9_SPI_SCLK, VADC
        "None", "None", # AIN4, GNDA
        "None", "None", # AIN6, AIN5
        "None", "None", # AIN2, AIN3
        "None", "None", # AIN0, AIN1
        "B10", "E10",   # CLKOUT, GPIO42
        "None", "None", # GND
        "None", "None") # GND
]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticePlatform):
    default_clk_name   = "clk25"
    default_clk_period = 1e9/25e6

    def __init__(self, revision="rev0", device="45F", toolchain="trellis", **kwargs):
        assert revision in ["rev0"]
        self.revision = revision
        io         = {"rev0": _io_rev0          }[revision]
        connectors = {"rev0": _connectors_rev0  }[revision]
        LatticePlatform.__init__(self, f"LFE5UM5G-{device}-8BG381C", io, connectors, toolchain=toolchain, **kwargs)

    def create_programmer(self):
        return DFUProg(vid="1d50", pid="6130")

    def do_finalize(self, fragment):
        LatticePlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk25", loose=True), 1e9/25e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:rx", loose=True), 1e9/125e6)
