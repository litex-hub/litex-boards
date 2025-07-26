#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 Denis Bodor <lefinnois@lefinnois.net>
# Copyright (c) 2021 Hans Baier <hansfbaier@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.altera import AlteraPlatform
from litex.build.altera.programmer import USBBlaster

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk
    ("clk50", 0, Pins("G1"), IOStandard("3.3-V LVTTL")),

    # fitted LEDs, active low
    ("user_led",  0, Pins("V10"), IOStandard("3.3-V LVTTL")), # D1
    ("user_led",  1, Pins("U9"),  IOStandard("3.3-V LVTTL")), # D2
    ("user_led",  2, Pins("V9"),  IOStandard("3.3-V LVTTL")), # D3
    ("user_led",  3, Pins("V8"),  IOStandard("3.3-V LVTTL")), # D4
    ("user_led",  4, Pins("V5"),  IOStandard("3.3-V LVTTL")), # D5
    ("user_led",  5, Pins("Y4"),  IOStandard("3.3-V LVTTL")), # D6

    # 7-segments display
    ("seven_seg_ctl", 0,
        Subsignal("dig",      Pins("U11 V16 AA18")),
        Subsignal("segments", Pins("W14 AB19 AB18 V13 U12 V15 AA19 U14")), # A B C D E F G dot
        IOStandard("3.3-V LVTTL")
    ),

    # Button
    ("key", 0, Pins("P4"), IOStandard("3.3-V LVTTL")),
    ("key", 1, Pins("P3"), IOStandard("3.3-V LVTTL")),

    ("serial", 0,
        # Onboard CH340N
        Subsignal("tx", Pins("AA21"), IOStandard("3.3-V LVTTL")),
        Subsignal("rx", Pins("AA22"), IOStandard("3.3-V LVTTL"))
    ),

    # SPIFlash (W25Q128)
    ("spiflash", 0,
        Subsignal("cs_n", Pins("E2")),
        Subsignal("clk",  Pins("K2")),
        Subsignal("mosi", Pins("D1")),
        Subsignal("miso", Pins("K1")),
        IOStandard("3.3-V LVTTL"),
    ),

    # SDR SDRAM
    ("sdram_clock", 0, Pins("W8"), IOStandard("3.3-V LVTTL")),
    ("sdram", 0,
        Subsignal("a",     Pins(
            "V2 V1 U2 U1 T4 T5 V3 Y3",
            "V4 W6 W1 Y6 W7")),
        Subsignal("ba",    Pins("Y1 W2")),
        Subsignal("cs_n",  Pins("Y2")),
        Subsignal("cke",   Pins("Y7")),
        Subsignal("ras_n", Pins("AA3")),
        Subsignal("cas_n", Pins("AB3")),
        Subsignal("we_n",  Pins("AA4")),
        Subsignal("dq", Pins(
            "AB9 AA9 AB8 AA8 AB7 AA7 AB5 AA5",
            "W10 Y10 V11 V12 Y13 W13 V14 W15"),
             Misc("FAST_OUTPUT_ENABLE_REGISTER ON"),
             Misc("FAST_INPUT_REGISTER ON")),
        Subsignal("dm", Pins("AB4 Y8")),
        Misc("CURRENT_STRENGTH_NEW \"MAXIMUM CURRENT\""),
        Misc("FAST_OUTPUT_REGISTER ON"),
        Misc("ALLOW_SYNCH_CTRL_USAGE OFF"),
        IOStandard("3.3-V LVTTL")
    ),

    # SD card
    ("sdcard", 0,
        Subsignal("data", Pins(f"U19 U20 Y17 W17")),
        Subsignal("cmd",  Pins(f"W19")),
        Subsignal("clk",  Pins(f"W20")),
        Subsignal("cd",   Pins(f"T18")),
        Misc("FAST_OUTPUT_REGISTER ON"),
        IOStandard("3.3-V LVTTL"),
    ),
    ("spisdcard", 0,
        Subsignal("clk",  Pins("W20")),
        Subsignal("mosi", Pins("W19"), Misc("WEAK_PULL_UP_RESISTOR ON")),
        Subsignal("cs_n", Pins("W17"), Misc("WEAK_PULL_UP_RESISTOR ON")),
        Subsignal("miso", Pins("U19"), Misc("WEAK_PULL_UP_RESISTOR ON")),
        IOStandard("3.3-V LVTTL"),
    ),

    # Ethernet RTL8211EG
    ("eth_clocks", 0,
        Subsignal("tx",  Pins("U21")),
        Subsignal("gtx", Pins("J22")),
        Subsignal("rx",  Pins("D22")),
        IOStandard("3.3-V LVTTL")
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("P21")),
        Subsignal("mdio",    Pins("Y22")),
        Subsignal("mdc",     Pins("Y21")),
        Subsignal("rx_dv",   Pins("B21")),
        Subsignal("rx_er",   Pins("H21")),
        Subsignal("rx_data", Pins("B22 C21 C22 D21 E21 E22 F21 F22")),
        Subsignal("tx_en",   Pins("M21")),
        Subsignal("tx_er",   Pins("W22")),
        Subsignal("tx_data", Pins("M22 P22 R21 R22 U22 V21 V22 W21")),
        Subsignal("col",     Pins("H22")),
        Subsignal("crs",     Pins("J21")),
        IOStandard("3.3-V LVTTL")
    ),

    # HDMI out
    ("hdmi_out", 0,
        Subsignal("clk_p",   Pins("AA14")),
        Subsignal("clk_n",   Pins("AB14")),
        Subsignal("data0_p", Pins("AA15")),
        Subsignal("data0_n", Pins("AB15")),
        Subsignal("data1_p", Pins("AA16")),
        Subsignal("data1_n", Pins("AB16")),
        Subsignal("data2_p", Pins("AA20")),
        Subsignal("data2_n", Pins("AB20")),
        Subsignal("scl",     Pins("AB13")),
        Subsignal("sda",     Pins("AA10")),
        Subsignal("hdp",     Pins("AB10")),
        Subsignal("cec",     Pins("AA13")),
        IOStandard("3.3-V LVTTL")
    ),
]

_connectors = [
    ("J12", {
          1: "B1",    2: "B2",
          3: "B3",    4: "A3",
          5: "B4",    6: "A4",
          7: "B5",    8: "A5",
          9: "B6",   10: "A6",
#        11: VIN_5V, 12: GND,
         13: "A7",   14: "B7",
         15: "A8",   16: "B8",
         17: "A9",   18: "B9",
         19: "A10",  20: "B10",
         21: "D15",  22: "C15",
         23: "B13",  24: "A13",
         25: "B14",  26: "A14",
         27: "B15",  28: "A15",
#        29: 3V3,    30: GND,
         31: "B16",  32: "A16",
         33: "B17",  34: "A17",
         35: "B18",  36: "A18",
         37: "B19",  38: "A19",
         39: "B20",  40: "A20",
    }),

    ("J13", {
          1: "F10",   2: "D10",
          3: "F11",   4: "E11",
          5: "E13",   6: "E12",
          7: "D13",   8: "C13",
          9: "C10",  10: "E14",
#        11: VIN_5V, 12: GND,
         13: "E15",  14: "E16",
         15: "C17",  16: "D17",
         17: "F17",  18: "C19",
         19: "C20",  20: "D19",
         21: "H17",  22: "D20",
         23: "F19",  24: "F20",
         25: "L22",  26: "L21",
         27: "M19",  28: "M20",
#        29: 3V3,    30: GND,
         31: "N19",  32: "N20",
         33: "N18",  34: "P20",
         35: "H19",  36: "H18",
         37: "J18",  38: "H20",
         39: "K19",  40: "K18",
    }),

    ("JP1", {
#         1: 3V3,     2: GND,
          3: "C8",    4: "E9", # with 4K7 pullup both
          5: "E7",    6: "C7",
          7: "E1",    8: "E6",
          9: "F1",   10: "F2",
         11: "C4",   12: "E5",
         13: "D2",   14: "C3",
         15: "G4",   16: "E4",
         17: "G3",   18: "E3",
    }),

    ("J10", {
          1: "J1",    2: "J2",
          3: "H1",    4: "H2",
          5: "P5",    6: "R5",
          7: "M5",    8: "N5",
#         9: GND,    10: GND,
#        11: 3V3,    12: 3V3,
    }),

    ("J11", {
          1: "R2",    2: "R1",
          3: "P2",    4: "P1",
          5: "N2",    6: "N1",
          7: "M2",    8: "M1",
#         9: GND,    10: GND,
#        11: 3V3,    12: 3V3,
    }),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self, toolchain="quartus", with_core_resources=True):
        device = "10CL080YU484C8G"
        io = _io
        connectors = _connectors

        AlteraPlatform.__init__(self, device, io, connectors, toolchain=toolchain)

        # Generate PLL clock in STA
        self.toolchain.additional_sdc_commands.append("derive_pll_clocks")
        # Calculates clock uncertainties
        self.toolchain.additional_sdc_commands.append("derive_clock_uncertainty")

    def create_programmer(self):
        return USBBlaster()

    def do_finalize(self, fragment):
        AlteraPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
