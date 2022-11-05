#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Gary Wong <gtw@gnu.org>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.lattice import LatticeECP5Platform
from litex.build.lattice.programmer import OpenOCDJTAGProgrammer

import os

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clock
    ("clk25",  0, Pins("P3"), IOStandard("LVCMOS33")),

    # LEDs
    ("user_led", 0, Pins("N16"), IOStandard("LVCMOS15"), Misc("OPENDRAIN=ON")),
    ("user_led", 1, Pins("P20"), IOStandard("LVCMOS15"), Misc("OPENDRAIN=ON")),
    ("user_led", 2, Pins("R20"), IOStandard("LVCMOS15"), Misc("OPENDRAIN=ON")),
    ("user_led", 3, Pins("N20"), IOStandard("LVCMOS15"), Misc("OPENDRAIN=ON")),
    ("user_led", 4, Pins("U20"), IOStandard("LVCMOS15"), Misc("OPENDRAIN=ON")),
    ("user_led", 5, Pins("M20"), IOStandard("LVCMOS15"), Misc("OPENDRAIN=ON")),
    ("user_led", 6, Pins("T20"), IOStandard("LVCMOS15"), Misc("OPENDRAIN=ON")),
    ("user_led", 7, Pins("D6"),  IOStandard("LVCMOS33"), Misc("OPENDRAIN=ON")),

    # USB FIFO
    ("usb_fifo", 0,
      Subsignal( "data",  Pins("N2 M1 M3 L1 L2 K1 K2 J1")),
      Subsignal( "rxf_n", Pins("H1")),
      Subsignal( "txe_n", Pins("H2")),
      Subsignal( "rd_n",  Pins("G1")),
      Subsignal( "wr_n",  Pins("G2")),
      Subsignal( "siwua", Pins("F1"))
    ),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("R2"), IOStandard("LVCMOS33")),
        Subsignal("mosi", Pins("W2"), IOStandard("LVCMOS33")),
        Subsignal("miso", Pins("V2"), IOStandard("LVCMOS33")),
        Subsignal("wp",   Pins("Y2"), IOStandard("LVCMOS33")),
        Subsignal("hold", Pins("W1"), IOStandard("LVCMOS33")),
    ),
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("R2"),          IOStandard("LVCMOS33")),
        Subsignal("dq",   Pins("W2 V2 Y2 W1"), IOStandard("LVCMOS33")),
    ),

    # SDCard
    ("spisdcard", 0,
        Subsignal("clk",  Pins("A9")),
        Subsignal("mosi", Pins("E9"), Misc("PULLMODE=UP")),
        Subsignal("cs_n", Pins("B8"), Misc("PULLMODE=UP")),
        Subsignal("miso", Pins("D9"), Misc("PULLMODE=UP")),
        Misc("SLEWRATE=FAST"),
        IOStandard("LVCMOS33"),
    ),
    ("sdcard", 0,
        Subsignal("clk",  Pins("A9")),
        Subsignal("cmd",  Pins("E9"), Misc("PULLMODE=UP")),
        Subsignal("data", Pins("D9 B9 C8 B8"), Misc("PULLMODE=UP")),
        Misc("SLEWRATE=FAST"),
        IOStandard("LVCMOS33"),
    ),

    # USB ULPI
    ("ulpi", 0,
        Subsignal("clk",   Pins("C6")),
        Subsignal("stp",   Pins("D7")),
        Subsignal("dir",   Pins("A7")),
        Subsignal("nxt",   Pins("C7")),
        Subsignal("reset", Pins("D8")),
        Subsignal("data",  Pins("A5 B5 A4 B4 A3 B3 A2 B2")),
        IOStandard("LVCMOS33")
    ),

    # DDR3 SDRAM
    ("dram_vtt_en", 0, Pins("M19"), IOStandard("LVCMOS15"), Misc("OPENDRAIN=ON")),
    ("ddram", 0,
        Subsignal("a", Pins(
            "E18 H16 D18 L16 H17 E17 G18 C18 "
            "G16 D17 J16 F18 J17 F16 F17"
        ),
        IOStandard("SSTL15_I")),
      Subsignal("ba",    Pins("M18 H18 L17"), IOStandard("SSTL15_I")),
      Subsignal("ras_n", Pins("R17"), IOStandard("SSTL15_I")),
      Subsignal("cas_n", Pins("R16"), IOStandard("SSTL15_I")),
      Subsignal("we_n",  Pins("M17"), IOStandard("SSTL15_I")),
      Subsignal("cs_n",  Pins("P17"), IOStandard("SSTL15_I")),
      Subsignal("dm", Pins("F20 T18"), IOStandard("SSTL15_I")),
      Subsignal("dq", Pins(
          "J20 F19 J19 E19 K19 E20 K20 G20",
          "T17 U16 P18 U17 N19 U18 P19 U19"),
          IOStandard("SSTL15_I"),
          Misc("TERMINATION=50")),
      Subsignal("dqs_p", Pins("G19 T19"), IOStandard("SSTL15D_I"),
          Misc("TERMINATION=OFF"),
          Misc("DIFFRESISTOR=100")),
      Subsignal("clk_p"  , Pins("K16"), IOStandard("SSTL15D_I")),
      Subsignal("cke",     Pins("D19"), IOStandard("SSTL15_I")),
      #Subsignal("odt",    Pins("")), Not connected.
      Subsignal("reset_n", Pins("L20"), IOStandard("SSTL15_I")),
      # Pseudo-VCCIO pads: SSTL15_II for 10 mA drive strength, see FPGA-TN-02035, section 6.7.
      Subsignal( "vccio", Pins( "C20 E16 J18 K18 L18 L19 N17 N18 T16" ),
          IOStandard( "SSTL15_II" ) ),
      Misc("SLEWRATE=FAST")),

    # MII Ethernet
    ("eth_clocks", 0,
        Subsignal("rx", Pins("L5")),
        Subsignal("tx", Pins("P1")),
        IOStandard("LVCMOS33"),
    ),
    ("eth", 0,
        Subsignal("rx_data", Pins("N3 N4 N5 P4")),
        Subsignal("rx_dv",   Pins("M5")),
        Subsignal("tx_data", Pins("N1 L4 L3 K4")),
        Subsignal("tx_en",   Pins("P2")),
        Subsignal("mdc",     Pins("P5")),
        Subsignal("mdio",    Pins("J5")),
        Subsignal("rx_er",   Pins("K5")),
        Subsignal("int_n",   Pins("M4")),
        #Subsignal("rst_n",   Pins("")), # Not connected
        IOStandard("LVCMOS33")
    ),

    # HDMI output
    ("hdmi", 0,
       Subsignal("data0", Pins("G3")),
       Subsignal("data1", Pins("F4")),
       Subsignal("data2", Pins("C1")),
       Subsignal("clk", Pins("E4") ),
       IOStandard("LVCMOS33D"),
       Misc("DRIVE=8 SLEWRATE=FAST")),

    # USB host 1
    ("usbhost", 0,
       Subsignal("dp", Pins("B6")),
       Subsignal("dn", Pins("A6")),
       IOStandard("LVCMOS33"))
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = []

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticeECP5Platform):
    default_clk_name   = "clk25"
    default_clk_period = 1e9/25e6

    def __init__(self, toolchain="trellis", **kwargs):
        LatticeECP5Platform.__init__(self, "LFE5U-85F-8BG381", _io, _connectors, toolchain=toolchain, **kwargs)

    def request(self, *args, **kwargs):
        return LatticeECP5Platform.request(self, *args, **kwargs)

    def create_programmer(self):
        return OpenOCDJTAGProgrammer("openocd_fpc_iii.cfg")

    def do_finalize(self, fragment):
        LatticeECP5Platform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk25",  loose=True), 1e9/25e6)
