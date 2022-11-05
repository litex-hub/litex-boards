#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2015 Robert Jordens <jordens@gmail.com>
# Copyright (c) 2015 Sebastien Bourdeauducq <sb@m-labs.hk>
# Copyright (c) 2015 Yann Sionneau <yann.sionneau@gmail.com>
# Copyright (c) 2016-2017 Tim 'mithro' Ansell <mithro@mithis.com>
# Copyright (c) 2019 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxSpartan6Platform
from litex.build.xilinx.programmer import XC3SProg

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk50", 0, Pins("H17"), IOStandard("LVTTL")),

    # Leds
    ("user_led", 0, Pins("V16"), IOStandard("LVTTL"), Drive(8), Misc("SLEW=QUIETIO")),  # Green at hdmi
    ("user_led", 1, Pins("U16"), IOStandard("LVTTL"), Drive(8), Misc("SLEW=QUIETIO")),  # Red at hdmi
    ("user_led", 2, Pins("A16"), IOStandard("LVTTL"), Drive(8), Misc("SLEW=QUIETIO")),  # Green at msd
    ("user_led", 3, Pins("A15"), IOStandard("LVTTL"), Drive(8), Misc("SLEW=QUIETIO")),  # Red at msd
    ("user_led", 4, Pins("A12"), IOStandard("LVTTL"), Drive(8), Misc("SLEW=QUIETIO")),  # Red at usb

    # Buttons
    ("user_btn", 0, Pins("N14"), IOStandard("LVTTL"), Misc("PULLDOWN")),

    # Serial
    ("serial", 0,
        Subsignal("tx",  Pins("A10")),
        Subsignal("rx",  Pins("A11"), Misc("PULLUP")),
        Subsignal("cts", Pins("C10"), Misc("PULLUP")),
        Subsignal("rts", Pins("A9"),  Misc("PULLUP")),
        IOStandard("LVTTL"),
    ),

    # USB FIFO
    ("usb_fifo", 0,
        Subsignal("data",  Pins("A11 A10 C10 A9 B9 A8 B8 A7")),
        Subsignal("rxf_n", Pins("C7")),
        Subsignal("txe_n", Pins("A6")),
        Subsignal("rd_n",  Pins("B6")),
        Subsignal("wr_n",  Pins("A5")),
        Subsignal("siwua", Pins("C5")),
        IOStandard("LVTTL"),
    ),

    # HDMI
    ("hdmi", 0,
        Subsignal("clk_p",     Pins("U5"), IOStandard("TMDS_33")),
        Subsignal("clk_n",     Pins("V5"), IOStandard("TMDS_33")),
        Subsignal("data0_p",   Pins("T6"), IOStandard("TMDS_33")),
        Subsignal("data0_n",   Pins("V6"), IOStandard("TMDS_33")),
        Subsignal("data1_p",   Pins("U7"), IOStandard("TMDS_33")),
        Subsignal("data1_n",   Pins("V7"), IOStandard("TMDS_33")),
        Subsignal("data2_p",   Pins("U8"), IOStandard("TMDS_33")),
        Subsignal("data2_n",   Pins("V8"), IOStandard("TMDS_33")),
        Subsignal("scl",       Pins("V9"), IOStandard("I2C")),
        Subsignal("sda",       Pins("T9"), IOStandard("I2C")),
        Subsignal("hpd_notif", Pins("R8"), IOStandard("LVTTL")),
    ),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("V3")),
        Subsignal("clk",  Pins("R15")),
        Subsignal("mosi", Pins("T13")),
        Subsignal("miso", Pins("R13"), Misc("PULLUP")),
        Subsignal("wp",   Pins("T14")),
        Subsignal("hold", Pins("V14")),
        Misc("SLEW=FAST"),
        IOStandard("LVTTL")
    ),
    ("spiflash2x", 0,
        Subsignal("cs_n", Pins("V3")),
        Subsignal("clk",  Pins("R15")),
        Subsignal("dq",   Pins("T13 R13"), Misc("PULLUP")),
        Subsignal("wp",   Pins("T14")),
        Subsignal("hold", Pins("V14")),
        Misc("SLEW=FAST"),
        IOStandard("LVTTL"),
    ),
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("V3")),
        Subsignal("clk",  Pins("R15")),
        Subsignal("dq",   Pins("T13 R13 T14 V14"), Misc("PULLUP")),
        Misc("SLEW=FAST"),
        IOStandard("LVTTL"),
    ),

    # SDCard
    ("spisdcard", 0,
        Subsignal("cs_n", Pins("A2"), Misc("PULLUP")),
        Subsignal("clk",  Pins("A3")),
        Subsignal("mosi", Pins("B3")),
        Subsignal("miso", Pins("B4"), Misc("PULLUP")),
        IOStandard("SDIO")
    ),
    ("sdcard", 0,
        Subsignal("clk", Pins("A3")),
        Subsignal("cmd", Pins("B3"),          Misc("PULLUP")),
        Subsignal("dat", Pins("B4 A4 B2 A2"), Misc("PULLUP")),
        IOStandard("SDIO")
    ),

    # Audio
    ("audio", 0,
        Subsignal("l", Pins("R7"), Misc("SLEW=SLOW")),
        Subsignal("r", Pins("T7"), Misc("SLEW=SLOW")),
        IOStandard("LVTTL"),
    ),

    # LPDDR SDRAM
    ("ddram_clock", 0,
        Subsignal("p", Pins("G3")),
        Subsignal("n", Pins("G1")),
        IOStandard("MOBILE_DDR")
    ),
    ("ddram", 0,
        Subsignal("a", Pins(
            "J7 J6 H5 L7 F3 H4 H3 H6",
            "D2 D1 F4 D3 G6")),
        Subsignal("ba",    Pins("F2 F1")),
        Subsignal("cke",   Pins("H7")),
        Subsignal("ras_n", Pins("L5")),
        Subsignal("cas_n", Pins("K5")),
        Subsignal("we_n",  Pins("E3")),
        Subsignal("dq", Pins(
            "L2 L1 K2 K1 H2 H1 J3 J1",
            "M3 M1 N2 N1 T2 T1 U2 U1")),
        Subsignal("dqs", Pins("L4 P2")),
        Subsignal("dm", Pins("K3 K4")),
        IOStandard("MOBILE_DDR")
    ),

    # PMOD
    ("pmod", 0,
        Subsignal("d", Pins("D9 C8 D6 C4 B11 C9 D8 C6")),
        IOStandard("LVTTL")
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("A", "U18 T17 P17 P16 N16 N17 M16 L15 L17 K15 K17 J16 H15 H18 F18 D18"),
    ("B", "C18 E18 G18 H16 J18 K18 K16 L18 L16 M18 N18 N15 P15 P18 T18 U17"),
    ("C", "F17 F16 E16 G16 F15 G14 F14 H14 H13 J13 G13 H12 K14 K13 K12 L12"),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxSpartan6Platform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self, toolchain="ise"):
        XilinxSpartan6Platform.__init__(self, "xc6slx45-csg324-3", _io, _connectors, toolchain="ise")
        self.toolchain.bitgen_opt += " -g Compress -g ConfigRate:6"

    def create_programmer(self):
        return XC3SProg(cable="ftdi")

    def do_finalize(self, fragment):
        XilinxSpartan6Platform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
