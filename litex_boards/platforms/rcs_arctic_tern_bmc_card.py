#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Raptor Engineering, LLC
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.lattice import LatticeECP5Platform
from litex.build.lattice.programmer import OpenOCDJTAGProgrammer

import os

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst (module)
    ("clk125",       0, Pins("B6"), IOStandard("LVCMOS33")),
    ("rst_n",        0, Pins("T3"), IOStandard("LVCMOS33")),

    # BMC serial (module)
    ("serial", 0,
        Subsignal("rx", Pins("A7"), IOStandard("LVCMOS33")),
        Subsignal("tx", Pins("B8"), IOStandard("LVCMOS33")),
    ),

    # Host serial (module)
    ("serial", 1,
        Subsignal("rx", Pins("C1"), IOStandard("LVCMOS33")),
        Subsignal("tx", Pins("C2"), IOStandard("LVCMOS33")),
        Subsignal("rts", Pins("C8"), IOStandard("LVCMOS33")),
        Subsignal("cts", Pins("D8"), IOStandard("LVCMOS33")),
    ),

    # DDR3 SDRAM (module)
    ("ddram", 0,
        Subsignal("a", Pins(
            "J1 K1 G2 H2 F1 G1 J4 J3 J5 K3 K2 H1 M5 K4 L4"),
            IOStandard("SSTL135_I")),
        Subsignal("ba",    Pins("K5 L5 M1"), IOStandard("SSTL135_I")),
        Subsignal("ras_n", Pins("L2"), IOStandard("SSTL135_I")),
        Subsignal("cas_n", Pins("N2"), IOStandard("SSTL135_I")),
        Subsignal("we_n",  Pins("N1"), IOStandard("SSTL135_I")),
        Subsignal("cs_n",  Pins("P5"), IOStandard("SSTL135_I")),
        Subsignal("dm", Pins("R20 N18 F20 E18"), IOStandard("SSTL135_I")),
        Subsignal("dq", Pins(
            "T20 U17 T18 U16 U19 T17 U20 U18",
            "L19 M18 L17 L16 L20 M19 L18 M20",
            "J20 K18 F19 K19 J19 J18 G20 K20",
            "G16 H18 H16 F18 J16 E17 J17 H17"),
            IOStandard("SSTL135_I"),
            Misc("TERMINATION=75")),
        Subsignal("dqs_p", Pins("T19 N16 G19 F17"), IOStandard("SSTL135D_I"),
            Misc("TERMINATION=OFF"),
            Misc("DIFFRESISTOR=100")),
        Subsignal("clk_p", Pins("P19 E16"), IOStandard("SSTL135D_I")),
        Subsignal("cke",   Pins("N5"), IOStandard("SSTL135_I")),
        Subsignal("odt",   Pins("M3"), IOStandard("SSTL135_I")),
        Subsignal("reset_n", Pins("L1"), IOStandard("SSTL135_I")),
        Misc("SLEWRATE=FAST"),
    ),

    # PCIe (module)
    ("pcie_x1", 0,
        Subsignal("clk_p", Pins("Y11")),
        Subsignal("clk_n", Pins("Y12")),
        Subsignal("rx_p",  Pins("Y5")),
        Subsignal("rx_n",  Pins("Y6")),
        Subsignal("tx_p",  Pins("W4")),
        Subsignal("tx_n",  Pins("W5")),
        Subsignal("perst", Pins("A6"), IOStandard("LVCMOS33")),
    ),

    # Inter-module SERDES (module)
    ("serdes_x2", 0,
        Subsignal("clk_p", Pins("Y19")),
        Subsignal("clk_n", Pins("W20")),
        Subsignal("rx_p",  Pins("Y14 Y16")),
        Subsignal("rx_n",  Pins("Y15 Y17")),
        Subsignal("tx_p",  Pins("W13 W17")),
        Subsignal("tx_n",  Pins("W14 W18")),
        Subsignal("perst", Pins("A6"), IOStandard("LVCMOS33")),
    ),

    # Bitstream Flash device (module)
    # Contains FPGA bistream, USRMCLK block required for clock output
    ("fpgaspiflash4x", 0,
        Subsignal("cs_n", Pins("R2")),
        Subsignal("dq",   Pins("W2 V2 Y2 W1")),
        IOStandard("LVCMOS33"),
        Misc("SLEWRATE=SLOW"),
        Misc("DRIVE=16"),
    ),

    # BMC firmware Flash device (carrier card)
    ("bmcspiflash4x", 0,
        Subsignal("cs_n", Pins("G5")),
        Subsignal("clk",  Pins("E5")),
        Subsignal("dq",   Pins("E3 F5 D2 H4")),
        IOStandard("LVCMOS33"),
        Misc("SLEWRATE=SLOW"),
        Misc("DRIVE=16"),
    ),

    # Host Flash device (carrier card)
    ("hostspiflash4x", 0,
        Subsignal("cs_n", Pins("E2")),
        Subsignal("clk",  Pins("G3")),
        Subsignal("dq",   Pins("F2 F3 D1 A2")),
        IOStandard("LVCMOS33"),
        Misc("SLEWRATE=SLOW"),
        Misc("DRIVE=16"),
    ),

    # I2C bus 1
    # 3-pin header (carrier card)
    ("i2c_master", 0,
        Subsignal("sda",       Pins("E4"), IOStandard("LVCMOS33"), Misc("PULLMODE=UP")),
        Subsignal("scl",       Pins("D5"), IOStandard("LVCMOS33"), Misc("PULLMODE=UP")),
    ),

    # I2C bus 2
    # 3-pin header (carrier card)
    ("i2c_master", 1,
        Subsignal("sda",       Pins("B1"), IOStandard("LVCMOS33"), Misc("PULLMODE=UP")),
        Subsignal("scl",       Pins("B2"), IOStandard("LVCMOS33"), Misc("PULLMODE=UP")),
    ),

    # I2C bus 3
    # 3-pin header (carrier card)
    ("i2c_master", 2,
        Subsignal("sda",       Pins("C7"), IOStandard("LVCMOS33"), Misc("PULLMODE=UP")),
        Subsignal("scl",       Pins("E8"), IOStandard("LVCMOS33"), Misc("PULLMODE=UP")),
    ),

    # I2C bus 4
    # GPIO expander 1 (module)
    ("i2c_master", 3,
        Subsignal("sda",       Pins("U1"), IOStandard("LVCMOS33"), Misc("PULLMODE=UP")),
        Subsignal("scl",       Pins("R1"), IOStandard("LVCMOS33"), Misc("PULLMODE=UP")),
    ),

    # I2C bus 5
    # GPIO expander 2 (module)
    ("i2c_master", 4,
        Subsignal("sda",       Pins("A12"), IOStandard("LVCMOS33"), Misc("PULLMODE=UP")),
        Subsignal("scl",       Pins("E12"), IOStandard("LVCMOS33"), Misc("PULLMODE=UP")),
    ),

    # I2C bus 9
    ("i2c_master", 5,
        Subsignal("sda",       Pins("R3"), IOStandard("LVCMOS33"), Misc("PULLMODE=UP")),
        Subsignal("scl",       Pins("U2"), IOStandard("LVCMOS33"), Misc("PULLMODE=UP")),
    ),

    # I2C bus 12
    # RTC + digital video + temperature sensor (module)
    # Clock generator + PMBus (carrier card)
    ("i2c_master", 6,
        Subsignal("sda",       Pins("V1"), IOStandard("LVCMOS33"), Misc("PULLMODE=UP")),
        Subsignal("scl",       Pins("T1"), IOStandard("LVCMOS33"), Misc("PULLMODE=UP")),
    ),

    # Host LPC interface (module)
    ("hostlpcslave", 0,
        Subsignal("frame_n",   Pins("D3"), Misc("PULLMODE=UP")),
        Subsignal("reset_n",   Pins("C3"), Misc("PULLMODE=UP")),
        Subsignal("addrdata",  Pins("C4 A3 B4 B3"), Misc("PULLMODE=UP")),
        Subsignal("serirq",    Pins("F4"), Misc("PULLMODE=UP")),
        Subsignal("clk",       Pins("H5"), Misc("PULLMODE=NONE")),
        IOStandard("LVCMOS33"),
        Misc("SLEWRATE=SLOW"),
        Misc("DRIVE=16"),
    ),

    # FSI (carrier card)
    ("openfsi_master", 0,
        Subsignal("clock",          Pins("A18"), IOStandard("LVCMOS33")),
        Subsignal("data",           Pins("B18"), IOStandard("LVCMOS33")),
        Subsignal("data_direction", Pins("T2"), IOStandard("LVCMOS33")),
    ),

    # RGMII Ethernet (module)
    ("eth_clocks", 0,
        Subsignal("tx", Pins("C11")),
        Subsignal("rx", Pins("A9")),
        IOStandard("LVCMOS33")
    ),
    ("eth", 0,
        # Reset is available on GPIO expander 2
        Subsignal("mdio",    Pins("D9")),
        Subsignal("mdc",     Pins("E6")),
        Subsignal("rx_ctl",  Pins("A8")),
        Subsignal("rx_data", Pins("E9 C9 D10 E10")),
        Subsignal("tx_ctl",  Pins("C10")),
        Subsignal("tx_data", Pins("B10 A10 B11 A11")),
        IOStandard("LVCMOS33")
    ),

    # Digital video (module)
    ("dvo", 0,
        Subsignal("r", Pins(
            "C14 E14 D14 E13 D13 C13 E11 C12")),
        Subsignal("g", Pins(
            "B19 B20 C17 C16 C15 D16 D15 E15")),
        Subsignal("b", Pins(
            "A14 A15 B15 A16 B16 A17 A19 B17")),
        Subsignal("de",      Pins("A13")),
        Subsignal("hsync_n", Pins("B13")),
        Subsignal("vsync_n", Pins("B12")),
        Subsignal("clk",     Pins("D11")),
        IOStandard("LVCMOS33")
    ),

    # 4-pin fan headers (carrier card)
    ("pwm_tach_pads", 0,
        Subsignal("pwm1", Pins("C5"), IOStandard("LVCMOS33")),
        Subsignal("pwm2", Pins("E1"), IOStandard("LVCMOS33")),
        Subsignal("pwm3", Pins("H3"), IOStandard("LVCMOS33")),
        Subsignal("pwm4", Pins("A5"), IOStandard("LVCMOS33")),
        Subsignal("tach1", Pins("C6"), IOStandard("LVCMOS33")),
        Subsignal("tach2", Pins("E7"), IOStandard("LVCMOS33")),
        Subsignal("tach3", Pins("D6"), IOStandard("LVCMOS33")),
        Subsignal("tach4", Pins("A4"), IOStandard("LVCMOS33")),
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticeECP5Platform):
    default_clk_name   = "clk125"
    default_clk_period = 1e9/125e6

    def __init__(self, device="LFE5UM5G", speed_grade="6", toolchain="trellis", **kwargs):
        assert device in ["LFE5UM5G", "LFE5UM"]
        if device == "LFE5UM5G":
            speed_grade = "8"
        LatticeECP5Platform.__init__(self, device + "-85F-" + speed_grade + "CABGA381", _io, toolchain=toolchain, **kwargs)

    def request(self, *args, **kwargs):
        return LatticeECP5Platform.request(self, *args, **kwargs)

    def create_programmer(self):
        return OpenOCDJTAGProgrammer("openocd_evn_ecp5.cfg")

    def do_finalize(self, fragment):
        LatticeECP5Platform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk125", loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:rx", 0, loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:rx", 1, loose=True), 1e9/125e6)
