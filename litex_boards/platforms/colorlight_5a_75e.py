#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Vadim Kaushan <admin@disasm.info>
# SPDX-License-Identifier: BSD-2-Clause

# The Colorlight 5A-75E PCB and IOs have been documented by @derekmulcahy and @adamgreig:
# https://github.com/q3k/chubby75/issues/59
# https://github.com/q3k/chubby75/pull/67

from litex.build.generic_platform import *
from litex.build.lattice import LatticeECP5Platform
from litex.build.lattice.programmer import OpenOCDJTAGProgrammer

# IOs ----------------------------------------------------------------------------------------------

# Documented by @derekmulcahy
_io_v7_1 = [
    # Clk
    ("clk25", 0, Pins("P6"), IOStandard("LVCMOS33")),

    # Led
    ("user_led_n", 0, Pins("P11"), IOStandard("LVCMOS33")),

    # Button
    ("user_btn_n", 0, Pins("M13"), IOStandard("LVCMOS33")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("P11")), # led (J19 DATA_LED-)
        Subsignal("rx", Pins("M13")), # btn (J19 KEY+)
        IOStandard("LVCMOS33")
    ),

    # SPIFlash (W25Q32JV)
    ("spiflash", 0,
        Subsignal("cs_n", Pins("N8")),
        #Subsignal("clk",  Pins("")), driven through USRMCLK
        Subsignal("mosi", Pins("T8")),
        Subsignal("miso", Pins("T7")),
        IOStandard("LVCMOS33"),
    ),

    # SDR SDRAM (M12616161A)
    ("sdram_clock", 0, Pins("C6"), IOStandard("LVCMOS33")),
    ("sdram", 0,
        Subsignal("a", Pins(
            "A9 E10 B12 D13 C12 D11 D10 E9",
            "D9 B7 C8")),
        Subsignal("dq", Pins(
            "B13 A11 B9  C11 C9 C10 E8  B5",
            "B6  A6  A5  B4  C3 B3  B2  A2",
            "E2  E4  D3  E5  A4 D4  C4  D5",
            "D6  E6  D8  A8  B8 B10 B11 E11")),
        Subsignal("we_n",  Pins("C7")),
        Subsignal("ras_n", Pins("D7")),
        Subsignal("cas_n", Pins("E7")),
        #Subsignal("cs_n", Pins("")), # gnd
        #Subsignal("cke",  Pins("")), # 3v3
        Subsignal("ba",    Pins("A7")),
        #Subsignal("dm",   Pins("")), # gnd
        IOStandard("LVCMOS33"),
        Misc("SLEWRATE=FAST")
    ),

    # RGMII Ethernet (B50612D)
    ("eth_clocks", 0,
        Subsignal("tx", Pins("M2")),
        Subsignal("rx", Pins("M1")),
        IOStandard("LVCMOS33")
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("P5")),
        Subsignal("mdio",    Pins("T2")),
        Subsignal("mdc",     Pins("P3")),
        Subsignal("rx_ctl",  Pins("N6")),
        Subsignal("rx_data", Pins("N1 M5 N5 M6")),
        Subsignal("tx_ctl",  Pins("M3")),
        Subsignal("tx_data", Pins("L1 L3 P2 L4")),
        IOStandard("LVCMOS33")
    ),
    ("eth_clocks", 1,
        Subsignal("tx", Pins("M12")),
        Subsignal("rx", Pins("M16")),
        IOStandard("LVCMOS33")
    ),
    ("eth", 1,
        Subsignal("rst_n",   Pins("P5")),
        Subsignal("mdio",    Pins("T2")),
        Subsignal("mdc",     Pins("P3")),
        Subsignal("rx_ctl",  Pins("L15")),
        Subsignal("rx_data", Pins("P13 N13 P14 M15")),
        Subsignal("tx_ctl",  Pins("R15")),
        Subsignal("tx_data", Pins("T14 R12 R13 R14")),
        IOStandard("LVCMOS33")
    ),
]

# Documented by @adamgreig
_io_v6_0 = [
    # Clk
    ("clk25", 0, Pins("P6"), IOStandard("LVCMOS33")),

    # Led
    ("user_led_n", 0, Pins("T6"), IOStandard("LVCMOS33")),

    # Button
    ("user_btn_n", 0, Pins("R7"),  IOStandard("LVCMOS33")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("T6")), # led (J19 DATA_LED-)
        Subsignal("rx", Pins("R7")), # btn (J19 KEY+)
        IOStandard("LVCMOS33")
    ),

    # SPIFlash (25Q32JVSIQ)
    ("spiflash", 0,
        Subsignal("cs_n", Pins("N8")),
        #Subsignal("clk",  Pins("")), driven through USRMCLK
        Subsignal("mosi", Pins("T8")),
        Subsignal("miso", Pins("T7")),
        IOStandard("LVCMOS33"),
    ),

    # SDR SDRAM (M12L64322A-5T)
    ("sdram_clock", 0, Pins("C8"), IOStandard("LVCMOS33")),
    ("sdram", 0,
        Subsignal("a",     Pins("A9 B9 B10 C10 D9 C9 E9 D8 E8 C7 B8")),
        Subsignal("dq",    Pins(
            "D5 C5 E5 C6 D6 E6 D7 E7",
            "D10 C11 D11 C12 E10 C13 D13 E11",
            "A5 B4 A4 B3 A3 C3 A2 B2",
            "D14 B14 A14 B13 A13 B12 B11 A11")),
        Subsignal("we_n",  Pins("B5")),
        Subsignal("ras_n", Pins("B6")),
        Subsignal("cas_n", Pins("A6")),
        #Subsignal("cs_n", Pins("")), # gnd
        #Subsignal("cke",  Pins("")), # 3v3
        Subsignal("ba",    Pins("B7 A8")),
        #Subsignal("dm",   Pins("")), # gnd
        Misc("SLEWRATE=FAST"),
        IOStandard("LVCMOS33"),
    ),

    # RGMII Ethernet (RTL8211FD)
    ("eth_clocks", 0,
        Subsignal("tx", Pins("L1")),
        Subsignal("rx", Pins("J1")),
        IOStandard("LVCMOS33")
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("R6")),
        Subsignal("mdio",    Pins("T4")),
        Subsignal("mdc",     Pins("R5")),
        Subsignal("rx_ctl",  Pins("J2")),
        Subsignal("rx_data", Pins("K2 J3 K1 K3")),
        Subsignal("tx_ctl",  Pins("L2")),
        Subsignal("tx_data", Pins("M2 M1 P1 R1")),
        IOStandard("LVCMOS33")
    ),
    ("eth_clocks", 1,
        Subsignal("tx", Pins("J16")),
        Subsignal("rx", Pins("M16")),
        IOStandard("LVCMOS33")
    ),
    ("eth", 1,
        Subsignal("rst_n",   Pins("R6")),
        Subsignal("mdio",    Pins("T4")),
        Subsignal("mdc",     Pins("R5")),
        Subsignal("rx_ctl",  Pins("P16")),
        Subsignal("rx_data", Pins("M15 R16 L15 L16")),
        Subsignal("tx_ctl",  Pins("K14")),
        Subsignal("tx_data", Pins("K16 J15 J14 K15")),
        IOStandard("LVCMOS33")
    ),
]

# From https://github.com/q3k/chubby75/blob/master/5a-75e/hardware_V7.1.md
_connectors_v7_1 = [
    ("j1",  "F3  F1  G3  - G2  H3  H5  F15 L2 K1 J5 K2 B16 J14 F12 -"),
    ("j2",  "G4  G5  J2  - H2  J1  J3  F15 L2 K1 J5 K2 B16 J14 F12 -"),
    ("j3",  "J4  K3  G1  - K4  C2  E3  F15 L2 K1 J5 K2 B16 J14 F12 -"),
    ("j4",  "C1  A3  F4  - E1  F5  D1  F15 L2 K1 J5 K2 B16 J14 F12 -"),
    ("j5",  "H4  K5  P1  - R1  L5  F2  F15 L2 K1 J5 K2 B16 J14 F12 -"),
    ("j6",  "N3  M4  T4  - R5  R3  N4  F15 L2 K1 J5 K2 B16 J14 F12 -"),
    ("j7",  "P4  R2  M8  - M9  T6  R6  F15 L2 K1 J5 K2 B16 J14 F12 -"),
    ("j8",  "R8  R7  P8  - P7  N7  M7  F15 L2 K1 J5 K2 B16 J14 F12 -"),
    ("j9",  "M11 N11 P12 - K15 N12 L16 F15 L2 K1 J5 K2 B16 J14 F12 -"),
    ("j10", "T13 N14 M14 - P16 T15 L14 F15 L2 K1 J5 K2 B16 J14 F12 -"),
    ("j11", "K16 J15 J16 - J12 H15 G16 F15 L2 K1 J5 K2 B16 J14 F12 -"),
    ("j12", "P15 L12 L13 - D14 R16 E16 F15 L2 K1 J5 K2 B16 J14 F12 -"),
    ("j13", "H13 J13 H12 - G14 H14 G15 F15 L2 K1 J5 K2 B16 J14 F12 -"),
    ("j14", "E14 D16 C15 - B15 C16 C14 F15 L2 K1 J5 K2 B16 J14 F12 -"),
    ("j15", "A15 F16 A14 - E13 B14 A13 F15 L2 K1 J5 K2 B16 J14 F12 -"),
    ("j16", "G13 G12 E15 - F14 F13 C13 F15 L2 K1 J5 K2 B16 J14 F12 -"),
]

# From https://github.com/q3k/chubby75/blob/master/5a-75e/hardware_V6.0.md
_connectors_v6_0 = [
    ("j1",  "C4  D4  E4  - D3  E3  F4  N4 N5 N3 P3 P4 M3 N1 M4 -"),
    ("j2",  "F3  F5  G3  - G4  H3  H4  N4 N5 N3 P3 P4 M3 N1 M4 -"),
    ("j3",  "G5  H5  J5  - J4  B1  C2  N4 N5 N3 P3 P4 M3 N1 M4 -"),
    ("j4",  "C1  D1  E2  - E1  F2  F1  N4 N5 N3 P3 P4 M3 N1 M4 -"),
    ("j5",  "G2  G1  H2  - K5  K4  L3  N4 N5 N3 P3 P4 M3 N1 M4 -"),
    ("j6",  "L4  L5  P2  - R2  T2  R3  N4 N5 N3 P3 P4 M3 N1 M4 -"),
    ("j7",  "T3  R4  M5  - P5  N6  N7  N4 N5 N3 P3 P4 M3 N1 M4 -"),
    ("j8",  "P7  M7  P8  - R8  M8  M9  N4 N5 N3 P3 P4 M3 N1 M4 -"),
    ("j9",  "P11 N11 M11 - T13 R12 R13 N4 N5 N3 P3 P4 M3 N1 M4 -"),
    ("j10", "R14 T14 D16 - C15 C16 B16 N4 N5 N3 P3 P4 M3 N1 M4 -"),
    ("j11", "B15 C14 T15 - P15 R15 P12 N4 N5 N3 P3 P4 M3 N1 M4 -"),
    ("j12", "P13 N12 N13 - M12 P14 N14 N4 N5 N3 P3 P4 M3 N1 M4 -"),
    ("j13", "H15 H14 G16 - F16 G15 F15 N4 N5 N3 P3 P4 M3 N1 M4 -"),
    ("j14", "E15 E16 L12 - L13 M14 L14 N4 N5 N3 P3 P4 M3 N1 M4 -"),
    ("j15", "J13 K13 J12 - H13 H12 G12 N4 N5 N3 P3 P4 M3 N1 M4 -"),
    ("j16", "G14 G13 F12 - F13 F14 E14 N4 N5 N3 P3 P4 M3 N1 M4 -"),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticeECP5Platform):
    default_clk_name = "clk25"
    default_clk_period = 1e9/25e6

    def __init__(self, revision="7.1", toolchain="trellis"):
        assert revision in ["6.0", "7.1"]
        self.revision = revision
        device = {"6.0": "LFE5U-25F-6BG256C", "7.1": "LFE5U-25F-6BG256C"}[revision]
        io = {"6.0": _io_v6_0, "7.1": _io_v7_1}[revision]
        connectors = {"6.0": _connectors_v6_0, "7.1": _connectors_v7_1}[revision]
        LatticeECP5Platform.__init__(self, device, io, connectors=connectors, toolchain=toolchain)

    def create_programmer(self):
        return OpenOCDJTAGProgrammer("openocd_colorlight_5a_75b.cfg")

    def do_finalize(self, fragment):
        LatticeECP5Platform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk25",            loose=True), 1e9/25e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:rx", 0, loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:rx", 1, loose=True), 1e9/125e6)
