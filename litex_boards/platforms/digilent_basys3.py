#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020-2021 Xuanyu Hu <xuanyu.hu@whu.edu.cn>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform, VivadoProgrammer
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk100", 0, Pins("W5"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led",  0, Pins("U16"), IOStandard("LVCMOS33")),
    ("user_led",  1, Pins("E19"), IOStandard("LVCMOS33")),
    ("user_led",  2, Pins("U19"), IOStandard("LVCMOS33")),
    ("user_led",  3, Pins("V19"), IOStandard("LVCMOS33")),
    ("user_led",  4, Pins("W18"), IOStandard("LVCMOS33")),
    ("user_led",  5, Pins("U15"), IOStandard("LVCMOS33")),
    ("user_led",  6, Pins("U14"), IOStandard("LVCMOS33")),
    ("user_led",  7, Pins("V14"), IOStandard("LVCMOS33")),
    ("user_led",  8, Pins("V13"), IOStandard("LVCMOS33")),
    ("user_led",  9, Pins("V3"),  IOStandard("LVCMOS33")),
    ("user_led", 10, Pins("W3"),  IOStandard("LVCMOS33")),
    ("user_led", 11, Pins("U3"),  IOStandard("LVCMOS33")),
    ("user_led", 12, Pins("P3"),  IOStandard("LVCMOS33")),
    ("user_led", 13, Pins("N3"),  IOStandard("LVCMOS33")),
    ("user_led", 14, Pins("P1"),  IOStandard("LVCMOS33")),
    ("user_led", 15, Pins("L1"),  IOStandard("LVCMOS33")),

    # Switches
    ("user_sw",  0, Pins("V17"), IOStandard("LVCMOS33")),
    ("user_sw",  1, Pins("V16"), IOStandard("LVCMOS33")),
    ("user_sw",  2, Pins("W16"), IOStandard("LVCMOS33")),
    ("user_sw",  3, Pins("W17"), IOStandard("LVCMOS33")),
    ("user_sw",  4, Pins("W15"), IOStandard("LVCMOS33")),
    ("user_sw",  5, Pins("V15"), IOStandard("LVCMOS33")),
    ("user_sw",  6, Pins("W14"), IOStandard("LVCMOS33")),
    ("user_sw",  7, Pins("W13"), IOStandard("LVCMOS33")),
    ("user_sw",  8, Pins("V2"),  IOStandard("LVCMOS33")),
    ("user_sw",  9, Pins("T3"),  IOStandard("LVCMOS33")),
    ("user_sw", 10, Pins("T2"),  IOStandard("LVCMOS33")),
    ("user_sw", 11, Pins("R3"),  IOStandard("LVCMOS33")),
    ("user_sw", 12, Pins("W2"),  IOStandard("LVCMOS33")),
    ("user_sw", 13, Pins("U1"),  IOStandard("LVCMOS33")),
    ("user_sw", 14, Pins("T1"),  IOStandard("LVCMOS33")),
    ("user_sw", 15, Pins("R2"),  IOStandard("LVCMOS33")),

    # Buttons
    ("user_btnu", 0, Pins("T18"), IOStandard("LVCMOS33")),
    ("user_btnd", 0, Pins("U17"), IOStandard("LVCMOS33")),
    ("user_btnl", 0, Pins("W19"), IOStandard("LVCMOS33")),
    ("user_btnr", 0, Pins("T17"), IOStandard("LVCMOS33")),
    ("user_btnc", 0, Pins("U18"), IOStandard("LVCMOS33")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("A18")),
        Subsignal("rx", Pins("B18")),
        IOStandard("LVCMOS33"),
    ),

    # VGA
     ("vga", 0,
        Subsignal("hsync_n", Pins("P19")),
        Subsignal("vsync_n", Pins("R18")),
        Subsignal("r", Pins("G19 H19 J19 N19")),
        Subsignal("g", Pins("J17 H17 G17 D17")),
        Subsignal("b", Pins("N18 L18 K18 J18")),
        IOStandard("LVCMOS33")
    ),
    
    # USB PS/2
    ("usbhost", 0,
       Subsignal("ps2_clk", Pins("B6")),
       Subsignal("ps2_data", Pins("A6")),
       IOStandard("LVCMOS33"))

]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("pmoda",    "J1   L2  J2  G2  H1  K2  H2  G3"),
    ("pmodb",    "A14 A16 B15 B16 A15 A17 C15 C16"),
    ("pmodc",    "K17 M18 N17 P18 L17 M19 P17 R18"),
    ("pmodxdac", " J3  L3  M2  N2  K3  M3  M1  N1"),
]

# PMODS --------------------------------------------------------------------------------------------

def sdcard_pmod_io(pmod):
    return [
        # SDCard PMOD:
        # - https://store.digilentinc.com/pmod-microsd-microsd-card-slot/
        ("spisdcard", 0,
            Subsignal("clk",  Pins(f"{pmod}:3")),
            Subsignal("mosi", Pins(f"{pmod}:1"), Misc("PULLUP True")),
            Subsignal("cs_n", Pins(f"{pmod}:0"), Misc("PULLUP True")),
            Subsignal("miso", Pins(f"{pmod}:2"), Misc("PULLUP True")),
            Misc("SLEW=FAST"),
            IOStandard("LVCMOS33"),
        ),
        ("sdcard", 0,
            Subsignal("data", Pins(f"{pmod}:2 {pmod}:4 {pmod}:5 {pmod}:0"), Misc("PULLUP True")),
            Subsignal("cmd",  Pins(f"{pmod}:1"), Misc("PULLUP True")),
            Subsignal("clk",  Pins(f"{pmod}:3")),
            Subsignal("cd",   Pins(f"{pmod}:6")),
            Misc("SLEW=FAST"),
            IOStandard("LVCMOS33"),
        ),

]
_sdcard_pmod_io = sdcard_pmod_io("pmoda") # SDCARD PMOD on JD.

class Platform(XilinxPlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self, toolchain="vivado"):
        XilinxPlatform.__init__(self, "xc7a35t-CPG236-1", _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        return OpenOCD("openocd_xc7_ft2232.cfg", "bscan_spi_xc7a35t.bit")
    
    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100", loose=True), 1e9/100e6)
