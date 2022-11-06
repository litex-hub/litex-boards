#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2018-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform, VivadoProgrammer
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk100", 0, Pins("E3"), IOStandard("LVCMOS33")),
    ("cpu_reset", 0, Pins("C12"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led",  0, Pins("H17"), IOStandard("LVCMOS33")),
    ("user_led",  1, Pins("K15"), IOStandard("LVCMOS33")),
    ("user_led",  2, Pins("J13"), IOStandard("LVCMOS33")),
    ("user_led",  3, Pins("N14"), IOStandard("LVCMOS33")),
    ("user_led",  4, Pins("R18"), IOStandard("LVCMOS33")),
    ("user_led",  5, Pins("V17"), IOStandard("LVCMOS33")),
    ("user_led",  6, Pins("U17"), IOStandard("LVCMOS33")),
    ("user_led",  7, Pins("U16"), IOStandard("LVCMOS33")),
    ("user_led",  8, Pins("V16"), IOStandard("LVCMOS33")),
    ("user_led",  9, Pins("T15"), IOStandard("LVCMOS33")),
    ("user_led", 10, Pins("U14"), IOStandard("LVCMOS33")),
    ("user_led", 11, Pins("T16"), IOStandard("LVCMOS33")),
    ("user_led", 12, Pins("V15"), IOStandard("LVCMOS33")),
    ("user_led", 13, Pins("V14"), IOStandard("LVCMOS33")),
    ("user_led", 14, Pins("V12"), IOStandard("LVCMOS33")),
    ("user_led", 15, Pins("V11"), IOStandard("LVCMOS33")),

    # Switches
    ("user_sw",  0, Pins("J15"), IOStandard("LVCMOS33")),
    ("user_sw",  1, Pins("L16"), IOStandard("LVCMOS33")),
    ("user_sw",  2, Pins("M13"), IOStandard("LVCMOS33")),
    ("user_sw",  3, Pins("R15"), IOStandard("LVCMOS33")),
    ("user_sw",  4, Pins("R17"), IOStandard("LVCMOS33")),
    ("user_sw",  5, Pins("T18"), IOStandard("LVCMOS33")),
    ("user_sw",  6, Pins("U18"), IOStandard("LVCMOS33")),
    ("user_sw",  7, Pins("R13"), IOStandard("LVCMOS33")),
    ("user_sw",  8, Pins("T8"),  IOStandard("LVCMOS33")),
    ("user_sw",  9, Pins("U8"),  IOStandard("LVCMOS33")),
    ("user_sw", 10, Pins("R16"), IOStandard("LVCMOS33")),
    ("user_sw", 11, Pins("T13"), IOStandard("LVCMOS33")),
    ("user_sw", 12, Pins("H6"),  IOStandard("LVCMOS33")),
    ("user_sw", 13, Pins("U12"), IOStandard("LVCMOS33")),
    ("user_sw", 14, Pins("U11"), IOStandard("LVCMOS33")),
    ("user_sw", 15, Pins("V10"), IOStandard("LVCMOS33")),

    # Buttons
    ("user_btn", 0, Pins("N17"), IOStandard("LVCMOS33")),
    ("user_btn", 1, Pins("P18"), IOStandard("LVCMOS33")),
    ("user_btn", 2, Pins("P17"), IOStandard("LVCMOS33")),
    ("user_btn", 3, Pins("M17"), IOStandard("LVCMOS33")),
    ("user_btn", 4, Pins("M18"), IOStandard("LVCMOS33")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("D4")),
        Subsignal("rx", Pins("C4")),
        IOStandard("LVCMOS33"),
    ),

    # SDCard
    ("spisdcard", 0,
        Subsignal("rst",  Pins("E2")),
        Subsignal("clk",  Pins("B1")),
        Subsignal("mosi", Pins("C1"), Misc("PULLUP True")),
        Subsignal("cs_n", Pins("D2"), Misc("PULLUP True")),
        Subsignal("miso", Pins("C2"), Misc("PULLUP True")),
        Misc("SLEW=FAST"),
        IOStandard("LVCMOS33"),
    ),
    ("sdcard", 0,
        Subsignal("rst",  Pins("E2"),          Misc("PULLUP True")),
        Subsignal("data", Pins("C2 E1 F1 D2"), Misc("PULLUP True")),
        Subsignal("cmd",  Pins("C1"),          Misc("PULLUP True")),
        Subsignal("clk",  Pins("B1")),
        Subsignal("cd",   Pins("A1")),
        Misc("SLEW=FAST"),
        IOStandard("LVCMOS33"),
    ),

    # DDR2 SDRAM
    ("ddram", 0,
        Subsignal("a", Pins(
            "M4 P4 M6 T1 L3 P5 M2 N1",
            "L4 N5 R2 K5 N6"),
            IOStandard("SSTL18_II")),
        Subsignal("ba",    Pins("P2 P3 R1"), IOStandard("SSTL18_II")),
        Subsignal("ras_n", Pins("N4"), IOStandard("SSTL18_II")),
        Subsignal("cas_n", Pins("L1"), IOStandard("SSTL18_II")),
        Subsignal("we_n",  Pins("N2"), IOStandard("SSTL18_II")),
        Subsignal("dm", Pins("T6 U1"), IOStandard("SSTL18_II")),
        Subsignal("dq", Pins(
            "R7 V6 R8 U7 V7 R6 U6 R5",
            "T5 U3 V5 U4 V4 T4 V1 T3"),
            IOStandard("SSTL18_II"),
            Misc("IN_TERM=UNTUNED_SPLIT_50")),
        Subsignal("dqs_p", Pins("U9 U2"), IOStandard("DIFF_SSTL18_II")),
        Subsignal("dqs_n", Pins("V9 V2"), IOStandard("DIFF_SSTL18_II")),
        Subsignal("clk_p", Pins("L6"), IOStandard("DIFF_SSTL18_II")),
        Subsignal("clk_n", Pins("L5"), IOStandard("DIFF_SSTL18_II")),
        Subsignal("cke",   Pins("M1"), IOStandard("SSTL18_II")),
        Subsignal("odt",   Pins("M3"), IOStandard("SSTL18_II")),
        Subsignal("cs_n",  Pins("K6"), IOStandard("SSTL18_II")),
        Misc("SLEW=FAST"),
    ),

    # RMII Ethernet
    ("eth_clocks", 0,
        Subsignal("ref_clk", Pins("D5")),
        IOStandard("LVCMOS33"),
    ),

    ("eth", 0,
        Subsignal("rst_n",   Pins("B3")),
        Subsignal("rx_data", Pins("C11 D10")),
        Subsignal("crs_dv",  Pins("D9")),
        Subsignal("tx_en",   Pins("B9")),
        Subsignal("tx_data", Pins("A10 A8")),
        Subsignal("mdc",     Pins("C9")),
        Subsignal("mdio",    Pins("A9")),
        Subsignal("rx_er",   Pins("C10")),
        Subsignal("int_n",   Pins("B8")),
        IOStandard("LVCMOS33")
     ),

    # VGA
     ("vga", 0,
        Subsignal("hsync_n", Pins("B11")),
        Subsignal("vsync_n", Pins("B12")),
        Subsignal("r", Pins("A4 C5 B4 A3")),
        Subsignal("g", Pins("A6 B6 A5 C6")),
        Subsignal("b", Pins("D7 C7 B7 D8")),
        IOStandard("LVCMOS33")
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("pmoda", "C17 D18 E18 G17 D17 E17 F18 G18"),
    ("pmodb", "D14 F16 G16 H14 E16 F13 G13 H16"),
    ("pmodc", "K1 F6 J2 G6 E7 J3 J4 E6"),
    ("pmodd", "H4 H1 G1 G3 H2 G4 G2 F3"),
    ("pmodxdac", "A13 A15 B16 B18 A14 A16 B17 A18"),
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
_sdcard_pmod_io = sdcard_pmod_io("pmodd") # SDCARD PMOD on JD.

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self, toolchain="vivado"):
        Xilinx7SeriesPlatform.__init__(self, "xc7a100tcsg324-1", _io, _connectors, toolchain=toolchain)
        self.add_platform_command("set_property INTERNAL_VREF 0.900 [get_iobanks 34]")

    def create_programmer(self):
        return OpenOCD("openocd_xc7_ft2232.cfg", "bscan_spi_xc7a100t.bit")

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100",             loose=True), 1e9/100e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:ref_clk", loose=True), 1e9/50e6)
