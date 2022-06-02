#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2018-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2021 Michael T. Mayers <michael@tweakoz.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform, VivadoProgrammer
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk100",    0, Pins("E3"),  IOStandard("LVCMOS33")),
    ("cpu_reset", 0, Pins("C12"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led",  0, Pins("T8"), IOStandard("LVCMOS33")),
    ("user_led",  1, Pins("V9"), IOStandard("LVCMOS33")),
    ("user_led",  2, Pins("R8"), IOStandard("LVCMOS33")),
    ("user_led",  3, Pins("T6"), IOStandard("LVCMOS33")),
    ("user_led",  4, Pins("T5"), IOStandard("LVCMOS33")),
    ("user_led",  5, Pins("T4"), IOStandard("LVCMOS33")),
    ("user_led",  6, Pins("U7"), IOStandard("LVCMOS33")),
    ("user_led",  7, Pins("U6"), IOStandard("LVCMOS33")),
    ("user_led",  8, Pins("V4"), IOStandard("LVCMOS33")),
    ("user_led",  9, Pins("U3"), IOStandard("LVCMOS33")),
    ("user_led", 10, Pins("V1"), IOStandard("LVCMOS33")),
    ("user_led", 11, Pins("R1"), IOStandard("LVCMOS33")),
    ("user_led", 12, Pins("P5"), IOStandard("LVCMOS33")),
    ("user_led", 13, Pins("U1"), IOStandard("LVCMOS33")),
    ("user_led", 14, Pins("R2"), IOStandard("LVCMOS33")),
    ("user_led", 15, Pins("P2"), IOStandard("LVCMOS33")),

    # 7SEG DISPLAY
    ("segled_an",  0, Pins("N6"), IOStandard("LVCMOS33")),
    ("segled_an",  1, Pins("M6"), IOStandard("LVCMOS33")),
    ("segled_an",  2, Pins("M3"), IOStandard("LVCMOS33")),
    ("segled_an",  3, Pins("N5"), IOStandard("LVCMOS33")),
    ("segled_an",  4, Pins("N2"), IOStandard("LVCMOS33")),
    ("segled_an",  5, Pins("N4"), IOStandard("LVCMOS33")),
    ("segled_an",  6, Pins("L1"), IOStandard("LVCMOS33")),
    ("segled_an",  7, Pins("M1"), IOStandard("LVCMOS33")),

    ("segled_ca",  0, Pins("L3"), IOStandard("LVCMOS33")),
    ("segled_cb",  0, Pins("N1"), IOStandard("LVCMOS33")),
    ("segled_cc",  0, Pins("L5"), IOStandard("LVCMOS33")),
    ("segled_cd",  0, Pins("L4"), IOStandard("LVCMOS33")),
    ("segled_ce",  0, Pins("K3"), IOStandard("LVCMOS33")),
    ("segled_cf",  0, Pins("M2"), IOStandard("LVCMOS33")),
    ("segled_cg",  0, Pins("L6"), IOStandard("LVCMOS33")),
    ("segled_dp",  0, Pins("M4"), IOStandard("LVCMOS33")),

    ("rgb_led", 0,
        Subsignal("r", Pins("K6")),
        Subsignal("g", Pins("H6")),
        Subsignal("b", Pins("L16")),
        IOStandard("LVCMOS33"),
    ),
    ("rgb_led", 1,
        Subsignal("r", Pins("K5")),
        Subsignal("g", Pins("F13")),
        Subsignal("b", Pins("F6")),
        IOStandard("LVCMOS33"),
    ),

    # Switches
    ("user_sw",  0, Pins("U9"), IOStandard("LVCMOS33")),
    ("user_sw",  1, Pins("U8"), IOStandard("LVCMOS33")),
    ("user_sw",  2, Pins("R7"), IOStandard("LVCMOS33")),
    ("user_sw",  3, Pins("R6"), IOStandard("LVCMOS33")),
    ("user_sw",  4, Pins("R5"), IOStandard("LVCMOS33")),
    ("user_sw",  5, Pins("V7"), IOStandard("LVCMOS33")),
    ("user_sw",  6, Pins("V6"), IOStandard("LVCMOS33")),
    ("user_sw",  7, Pins("V5"), IOStandard("LVCMOS33")),
    ("user_sw",  8, Pins("U4"),  IOStandard("LVCMOS33")),
    ("user_sw",  9, Pins("V2"),  IOStandard("LVCMOS33")),
    ("user_sw", 10, Pins("U2"), IOStandard("LVCMOS33")),
    ("user_sw", 11, Pins("T3"), IOStandard("LVCMOS33")),
    ("user_sw", 12, Pins("T1"),  IOStandard("LVCMOS33")),
    ("user_sw", 13, Pins("R3"), IOStandard("LVCMOS33")),
    ("user_sw", 14, Pins("P3"), IOStandard("LVCMOS33")),
    ("user_sw", 15, Pins("P4"), IOStandard("LVCMOS33")),

    # Buttons
    ("user_btn", 0, Pins("T16"), IOStandard("LVCMOS33")),
    ("user_btn", 1, Pins("R10"), IOStandard("LVCMOS33")),
    ("user_btn", 2, Pins("F15"), IOStandard("LVCMOS33")),
    ("user_btn", 3, Pins("V10"), IOStandard("LVCMOS33")),
    ("user_btn", 4, Pins("E16"), IOStandard("LVCMOS33")),

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

    # SRAM
    ("cellularram", 0,
        Subsignal("addr", Pins(
            "J18 H17 H15 J17 H16 K15 K13 N15",
            "V16 U14 V14 V12 P14 U16 R15 N14",
            "N16 M13 V17 U17 T10 M16 U13"),
        ),
        Subsignal("data", Pins(
            "R12 T11 U12 R13 U18 R17 T18 R18",
            "F18 G18 G17 M18 M17 P18 N17 P17"),
        ),
        Subsignal("oen",  Pins("H14")),
        Subsignal("wen",  Pins("R11")),
        Subsignal("clk",  Pins("T15")),
        Subsignal("adv",  Pins("T13")),
        Subsignal("wait", Pins("T14")),
        Subsignal("cen",  Pins("L18")),
        Subsignal("ub",   Pins("J13")),
        Subsignal("lb",   Pins("J15")),
        Subsignal("cre",  Pins("J14")),
        Misc("SLEW=FAST"),
        IOStandard("LVCMOS33"),
    ),

    # RMII Ethernet
    ("eth_clocks", 0,
        Subsignal("ref_clk", Pins("D5")),
        IOStandard("LVCMOS33"),
    ),

    ("aud_pwm", 0,
        Subsignal("pwm_out", Pins("A11")),
        Subsignal("enable", Pins("D12")),
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
    ("pmoda",    "B13 F14 D17 E17 G13 C17 D18 E18"),
    ("pmodb",    "G14 P15 V11 V15 K16 R16  T9 U11"),
    ("pmodc",    "K2   E7  J3  J4  K1  E6  J2  G6"),
    ("pmodd",    "H4   H1  G1  G3  H2  G4  G2  F3"),
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

class Platform(XilinxPlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self, toolchain="vivado"):
        XilinxPlatform.__init__(self, "xc7a100t-CSG324-1", _io, _connectors, toolchain=toolchain)
        self.add_platform_command("set_property INTERNAL_VREF 0.750 [get_iobanks 34]")

    def create_programmer(self):
        return OpenOCD("openocd_xc7_ft2232.cfg", "bscan_spi_xc7a100t.bit")

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100",             loose=True), 1e9/100e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:ref_clk", loose=True), 1e9/50e6)
