#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019 Arnaud Durand <arnaud.durand@unifr.ch>
# Copyright (c) 2022 Martin Hubacek @hubmartin (Twitter)
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.lattice import LatticeECP5Platform
from litex.build.lattice.programmer import OpenOCDJTAGProgrammer

import os

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk27",        0, Pins("E17"), IOStandard("LVCMOS33")),
    ("clk100",       0, Pins("C5"),  IOStandard("LVDS")),
    ("ext_clk50",    0, Pins("B11"), IOStandard("LVCMOS33")),
    ("ext_clk50_en", 0, Pins("C11"), IOStandard("LVCMOS33")),
    ("rst_n",        0, Pins("AH1"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led", 0, Pins("AG30"), IOStandard("LVCMOS25")),
    ("user_led", 1, Pins("AK29"), IOStandard("LVCMOS25")),
    ("user_led", 2, Pins("AK30"), IOStandard("LVCMOS25")),
    ("user_led", 3, Pins("AH32"), IOStandard("LVCMOS25")),
    ("user_led", 4, Pins("AG32"), IOStandard("LVCMOS25")),
    ("user_led", 5, Pins("AJ29"), IOStandard("LVCMOS25")),
    ("user_led", 6, Pins("AM28"), IOStandard("LVCMOS25")),
    ("user_led", 7, Pins("AM29"), IOStandard("LVCMOS25")),

    # ws2812
    ("ws2812", 0, Pins("AK31"), IOStandard("LVCMOS25")),

    # Buttons
    ("user_dip_btn", 1, Pins("J1"),  IOStandard("LVCMOS33")),
    ("user_dip_btn", 2, Pins("H1"),  IOStandard("LVCMOS33")),
    ("user_dip_btn", 3, Pins("K1"),  IOStandard("LVCMOS33")),
    ("user_dip_btn", 4, Pins("E15"), IOStandard("LVCMOS25")),
    ("user_dip_btn", 5, Pins("D16"), IOStandard("LVCMOS25")),
    ("user_dip_btn", 6, Pins("B16"), IOStandard("LVCMOS25")),
    ("user_dip_btn", 7, Pins("C16"), IOStandard("LVCMOS25")),
    ("user_dip_btn", 8, Pins("A16"), IOStandard("LVCMOS25")),

    ("button_1", 0, Pins("P4"), IOStandard("LVCMOS25")),

    # Serial
    ("serial", 0,
        Subsignal("rx", Pins("AL28"), IOStandard("LVCMOS25")), ##LVCMOS25
        Subsignal("tx", Pins("AK28"), IOStandard("LVCMOS25")), ##LVCMOS25
    ),

    # DDR3 SDRAM
    ("ddram", 0,
        Subsignal("a", Pins(
            " W4  Y5  AB6  P3  AB5  W5  AC6  Y7",
            "AC7  AD6 W1   Y6  U1   AD7"),
            IOStandard("SSTL135_I")),
        Subsignal("ba",    Pins("U3 Y4 W3"), IOStandard("SSTL135_I")),
        Subsignal("ras_n", Pins("C2"), IOStandard("SSTL135_I")),
        Subsignal("cas_n", Pins("T1"), IOStandard("SSTL135_I")),
        Subsignal("we_n",  Pins("P1"), IOStandard("SSTL135_I")),
        Subsignal("cs_n",  Pins("P2"), IOStandard("SSTL135_I")),
        Subsignal("dm", Pins("AB3 R6 F2 H6"), IOStandard("SSTL135_I")),
        Subsignal("dq", Pins(
            "AC5 AC2 AB4 AE3 W2 AD4 Y1 AB1",
            "V6  P4  V7  T7  U6 T4  U7 U4",
            "H2 K1 F1 L2 E1 K3 H3 H1",
            "N7 J6 L4 K7 P7 L7 K6 H5"),
            IOStandard("SSTL135_I"),
            Misc("TERMINATION=75")),
        Subsignal("dqs_p", Pins("AC3 R4 K2 N3"), IOStandard("SSTL135D_I"),
            Misc("TERMINATION=OFF"),
            Misc("DIFFRESISTOR=100")),
        Subsignal("clk_p", Pins("R3 J4"), IOStandard("SSTL135D_I")),
        Subsignal("cke",   Pins("T2"), IOStandard("SSTL135_I")),
        Subsignal("odt",   Pins("V1"), IOStandard("SSTL135_I")),
        Subsignal("reset_n", Pins("C4"), IOStandard("SSTL135_I")),
        Misc("SLEWRATE=FAST"),
    ),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("AJ3"), IOStandard("LVCMOS33")),
        Subsignal("mosi",   Pins("AK2"), IOStandard("LVCMOS33")),
        Subsignal("miso",   Pins("AJ2"), IOStandard("LVCMOS33")),
        #Subsignal("wp",     Pins("Y2"), IOStandard("LVCMOS33")),
        #Subsignal("hold",   Pins("W1"), IOStandard("LVCMOS33")),
    ),
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("R2"),          IOStandard("LVCMOS33")),
        Subsignal("dq",   Pins("W2 V2 Y2 W1"), IOStandard("LVCMOS33")),
    ),

    # HDMI
    ("hdmi", 0,
        Subsignal("clk", Pins("E25")),
        Subsignal("hsync_n", Pins("D25")),
        Subsignal("vsync_n", Pins("A25")),
        
        Subsignal("de", Pins("C25")),

        Subsignal("r", Pins("AE27 AD27 AB29 AB30 AB28 AB27 AC26 Y27 D24 W28 F25 F17")),
        Subsignal("g", Pins("AD26 T26 R26 A24 T32 AC30 AB31 V32 W32 Y26 W30 T30")),
        Subsignal("b", Pins("T31 R32 Y32 W31 T29 U28 V27 V26 AC31 AB32 AC32 AD32")),
  
        Subsignal("sda", Pins("AJ1")),
        Subsignal("scl", Pins("AG1")),

        IOStandard("LVCMOS25")
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticeECP5Platform):
    default_clk_name   = "clk27"
    default_clk_period = 1e9/27e6

    def __init__(self, toolchain="trellis", **kwargs):
        LatticeECP5Platform.__init__(self, "LFE5UM-85F-8BG756", _io, toolchain=toolchain, **kwargs)

    def request(self, *args, **kwargs):
        import time
        if "serial" in args:
            msg =  "FT2232H will be used as serial, make sure that:\n"
            msg += " -the hardware has been modified: R22 and R23 should be removed, two 0 Ω resistors shoud be populated on R34 and R35.\n"
            msg += " -the chip is configured as UART with virtual COM on port B (With FTProg or https://github.com/trabucayre/fixFT2232_ecp5evn)."
            print(msg)
            time.sleep(2)
        if "ext_clk50" in args:
            print("An oscillator must be populated on X5.")
            time.sleep(2)

        return LatticeECP5Platform.request(self, *args, **kwargs)

    def create_programmer(self):
        return OpenOCDJTAGProgrammer("openocd_evn_ecp5.cfg")

    def do_finalize(self, fragment):
        LatticeECP5Platform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk27",  loose=True), 1e9/27e6)
        self.add_period_constraint(self.lookup_request("clk100", loose=True), 1e9/100e6)
