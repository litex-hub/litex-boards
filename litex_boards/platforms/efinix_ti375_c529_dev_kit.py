#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2024 Dolu1990 <charles.papon.90@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.efinix.platform import EfinixPlatform
from litex.build.efinix import EfinixProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk.
    ("clk25",  0, Pins("L17"), IOStandard("1.8_V_LVCMOS")),
    ("clk100", 0, Pins("U4"),  IOStandard("3.3_V_LVCMOS")),

    # Serial.
    ("serial", 0,
        Subsignal("tx", Pins(" E9")),
        Subsignal("rx", Pins("E10")),
        IOStandard("3.3_V_LVTTL"),
        Misc("WEAK_PULLUP"),
    ),

    # Buttons.
    ("user_btn", 0, Pins("U19"), IOStandard("3.3_V_LVCMOS")),

    # DRAM.
    ("dram_pll_refclk", 0, Pins("XXX"), IOStandard("3.3_V_LVTTL_/_LVCMOS")),

    # SDCard.
    ("spisdcard", 0,
        Subsignal("clk",  Pins(" C9")),
        Subsignal("mosi", Pins("C10")),
        Subsignal("cs_n", Pins(" A9")),
        Subsignal("miso", Pins(" B9")),
        IOStandard("3.3_V_LVCMOS"),
    ),
    ("sdcard", 0,
        Subsignal("data", Pins("B9 B10 A8 A9")),
        Subsignal("cmd",  Pins("C10")),
        Subsignal("clk",  Pins("C9")) , #, Misc("SLEWRATE=1"), Misc("DRIVE_STRENGTH=16")
        IOStandard("3.3_V_LVTTL"),
    ),

    # FAN.
    ("fan_speed_control", 0, Pins("T19"), IOStandard("3.3_V_LVCMOS")),
]

# Bank voltage ---------------------------------------------------------------------------------------

_bank_info = [
            ("2A"      , "1.8 V LVCMOS"), # is_dyn_voltage="false" mode_sel_name="2A_MODE_SEL"/>
            ("2B"      , "1.8 V LVCMOS"), # is_dyn_voltage="false" mode_sel_name="2B_MODE_SEL"/>
            ("2C"      , "1.8 V LVCMOS"), # is_dyn_voltage="false" mode_sel_name="2C_MODE_SEL"/>
            ("2D"      , "1.8 V LVCMOS"), # is_dyn_voltage="false" mode_sel_name="2D_MODE_SEL"/>
            ("2E"      , "1.8 V LVCMOS"), # is_dyn_voltage="false" mode_sel_name="2E_MODE_SEL"/>
            ("4A_4B"   , "1.8 V LVCMOS"), # is_dyn_voltage="false" mode_sel_name="4A_4B_MODE_SEL"/>
            ("4C"      , "1.8 V LVCMOS"), # is_dyn_voltage="false" mode_sel_name="4C_MODE_SEL"/>
            ("4D"      , "1.8 V LVCMOS"), # is_dyn_voltage="false" mode_sel_name="4D_MODE_SEL"/>
            ("BL2_BL3" , "3.3 V LVCMOS"), # is_dyn_voltage="false">
            ("BR0"     , "3.3 V LVCMOS"), # is_dyn_voltage="false" mode_sel_name="BR0_MODE_SEL"/>
            ("BR3_BR4" , "3.3 V LVCMOS"), # is_dyn_voltage="false">
            ("TL1_TL5" , "3.3 V LVCMOS"), # is_dyn_voltage="false">
            ("TR0"     , "3.3 V LVCMOS"), # is_dyn_voltage="false" mode_sel_name="TR0_MODE_SEL"/>
            ("TR1"     , "3.3 V LVCMOS"), # is_dyn_voltage="false" mode_sel_name="TR1_MODE_SEL"/>
            ("TR2"     , "3.3 V LVCMOS"), # is_dyn_voltage="false" mode_sel_name="TR2_MODE_SEL"/>
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("pmod0", "G15 G16 F16 F17 G17 A11 A13 A12"),
    ("pmod1", "B12 C14 C13 C12 D12 F12 D13 E13"),
    ("pmod2", "E14 E16 F13 E15 F14 E11 F11 D11"),
    ["p1",
        "---", # 0
        # 3V3      5V     GND GND                 GND GND                 GND GND         ↓
        "--- B21 --- A21 --- --- C22 E21 B22 D21 --- --- B23 F21 A22 F22 --- --- D22 G21",
        #  1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17  18  19  20  ↑
        # 21  22  23  24  25  26  27  28  28  30  31  32  33  34  35  36  37  38  39  40  ↓
        "D23 G22 --- --- F23 H20 E23 G20 --- --- H22 K23 H23 L23 --- --- L19 M21 M19 M22",
        #        GND GND                 GND GND                 GND GND                  ↑
    ],
]

# PMODS --------------------------------------------------------------------------------------------

def raw_pmod_io(pmod):
    return [(pmod, 0, Pins(" ".join([f"{pmod}:{i:d}" for i in range(8)])), IOStandard("3.3_V_LVTTL_/_LVCMOS"))]

def jtag_pmod_io(pmod):
    return [
        ("usb_uart", 0,
            Subsignal("tck", Pins(f"{pmod}:0")),
            Subsignal("tdi", Pins(f"{pmod}:1")),
            Subsignal("tdo", Pins(f"{pmod}:2")),
            Subsignal("tms", Pins(f"{pmod}:3")),
            IOStandard("3.3_V_LVCMOS")
        ),
    ]

def hdmi_px(px):
    return [
        ("hdmi_i2c", 0,
            Subsignal("sda", Pins(f"{px}:26")),
            Subsignal("scl", Pins(f"{px}:28")),
            IOStandard("1.8_V_LVCMOS"),
            Misc("WEAK_PULLUP"),
            Misc("SCHMITT_TRIGGER"),
        ),
        ("hdmi_data", 0,
            Subsignal("clk", Pins(f"{px}:4")),
            Subsignal("de", Pins(f"{px}:33")),
            Subsignal("d", Pins(f"{px}:31 {px}:27 {px}:25 {px}:21 {px}:19 {px}:15 {px}:13 {px}:9 {px}:7 {px}:2 {px}:8 {px}:10 {px}:14 {px}:16 {px}:20 {px}:22")),
            IOStandard("1.8_V_LVCMOS")
        ),
        ("hdmi_sync", 0,
            Subsignal("hsync", Pins(f"{px}:37")),
            Subsignal("vsync", Pins(f"{px}:39")),
            IOStandard("1.8_V_LVCMOS")
        ),
    ]

# Platform -----------------------------------------------------------------------------------------

class Platform(EfinixPlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self, toolchain="efinity"):
        EfinixPlatform.__init__(self, "Ti375C529C4", _io, _connectors, iobank_info=_bank_info, toolchain=toolchain)

    def create_programmer(self):
        return EfinixProgrammer()

    def do_finalize(self, fragment):
        EfinixPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100", loose=True), 1e9/100e6)
