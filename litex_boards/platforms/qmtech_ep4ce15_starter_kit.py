#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Franck Jullien <franck.jullien@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.altera import AlteraPlatform
from litex.build.altera.programmer import USBBlaster

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk
    ("clk50", 0, Pins("T2"), IOStandard("3.3-V LVTTL")),

    # LED
    ("led", 0, Pins("E3"), IOStandard("3.3-V LVTTL")),

    # Button
    ("key", 0, Pins("J4"), IOStandard("3.3-V LVTTL")),

    ("serial", 0,
        Subsignal("tx", Pins("Y22"), IOStandard("3.3-V LVTTL")),
        Subsignal("rx", Pins("Y21"), IOStandard("3.3-V LVTTL"))
    ),

    # 7-segments display
    ("seven_seg_ctl", 0,
        Subsignal("dig", Pins("Y13 W13 V13")),
        Subsignal("segments", Pins("V15 U20 W20 Y17 W15 W17 U19")),
        Subsignal("dot", Pins("W19")),
        IOStandard("3.3-V LVTTL")
    ),

    # VGA
    ("vga", 0,
        Subsignal("hsync_n", Pins("AA13")),
        Subsignal("vsync_n", Pins("AB10")),
        Subsignal("r", Pins("AB19 AA19 AB20 AA20 AA21")),
        Subsignal("g", Pins("AB16 AA16 AB17 AA17 AA18 AB18")),
        Subsignal("b", Pins("AA14 AB13 AA15 AB14 AB15")),
        IOStandard("3.3-V LVTTL")
    ),

    # SPIFlash (W25Q64)
    ("spiflash", 0,
        # clk
        Subsignal("cs_n", Pins("E2")),
        Subsignal("clk",  Pins("K2")),
        Subsignal("mosi", Pins("D1")),
        Subsignal("miso", Pins("E2")),
        IOStandard("3.3-V LVTTL"),
    ),

    # SDR SDRAM
    ("sdram_clock", 0, Pins("Y6"), IOStandard("3.3-V LVTTL")),
    ("sdram", 0,
        Subsignal("a",     Pins(
            "V2 V1 U2 U1 V3 V4 Y2 AA1",
            "Y3 V5 W1 Y4 V6")),
        Subsignal("ba",    Pins("Y1 W2")),
        Subsignal("cs_n",  Pins("AA3")),
        Subsignal("cke",   Pins("W6")),
        Subsignal("ras_n", Pins("AB3")),
        Subsignal("cas_n", Pins("AA4")),
        Subsignal("we_n",  Pins("AB4")),
        Subsignal("dq", Pins(
            "AA10 AB9 AA9 AB8 AA8 AB7 AA7 AB5",
            "Y7 W8 Y8 V9 V10 Y10 W10 V11")),
        Subsignal("dm", Pins("AA5 W7")),
        IOStandard("3.3-V LVTTL")
    ),

    # GMII Ethernet
    ("eth_clocks", 0,
        Subsignal("tx",  Pins("R22")),
        Subsignal("gtx", Pins("L21")),
        Subsignal("rx",  Pins("F21")),
        IOStandard("3.3-V LVTTL")
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("N22")),
        Subsignal("mdio",    Pins("W21")),
        Subsignal("mdc",     Pins("W22")),
        Subsignal("rx_dv",   Pins("D22")),
        Subsignal("rx_er",   Pins("K22")),
        Subsignal("rx_data", Pins("D21 E22 E21 F22 H22 H21 J22 J21")),
        Subsignal("tx_en",   Pins("M22")),
        Subsignal("tx_er",   Pins("V21")),
        Subsignal("tx_data", Pins("M21 N21 P22 P21 R21 U22 U21 V22")),
        Subsignal("col",     Pins("K21")),
        Subsignal("crs",     Pins("L22")),
        IOStandard("3.3-V LVTTL")
    ),
]

_connectors = [
    ("J11", {
          1: "R1",   7: "R2",
          2: "P1",   8: "P2",
          3: "N1",   9: "N2",
          4: "M1",  10: "M2",
          5: "-" ,  11: "-",
          6: "-" ,  12: "-",
    }),
    ("J10", {
          1: "J1",   7: "J2",
          2: "H1",   8: "H2",
          3: "F1",   9: "F2",
          4: "E1",  10: "D2",
          5: "-" ,  11: "-",
          6: "-" ,  12: "-",
    }),
    ("JP1", {
          1: "-",    2: "-",
          3: "A8",   4: "B8",
          5: "A7",   6: "B7",
          7: "A6",   8: "B6",
          9: "A5",  10: "B5",
         11: "A4",  12: "B4",
         13: "A3",  14: "B3",
         15: "B1",  16: "B2",
         17: "C1",  18: "C2",
    }),
    ("J12", {
          1: "-",    2: "-",
          3: "C22",  4: "C21",
          5: "B22",  6: "B21",
          7: "H20",  8: "H19",
          9: "F20", 10: "F19",
         11: "C20", 12: "D20",
         13: "C19", 14: "D19",
         15: "C17", 16: "D17",
         17: "A20", 18: "B20",
         19: "A19", 20: "B19",
         21: "A18", 22: "B18",
         23: "A17", 24: "B17",
         25: "A16", 26: "B16",
         27: "A15", 28: "B15",
         29: "A14", 30: "B14",
         31: "A13", 32: "B13",
         33: "A10", 34: "B10",
         35: "A9",  36: "B9",
         37: "-",   38: "-",
         39: "-",   40: "-",
    })
]

# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self, toolchain="quartus"):
        AlteraPlatform.__init__(self, "EP4CE15F23C8", _io, _connectors, toolchain=toolchain)
        self.add_platform_command("set_global_assignment -name CYCLONEII_RESERVE_NCEO_AFTER_CONFIGURATION \"USE AS REGULAR IO\"")

    def create_programmer(self):
        return USBBlaster()

    def do_finalize(self, fragment):
        AlteraPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
