#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2023 Charles-Henri Mousset <ch.mousset@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

# The Colorlight 5A-75B PCB and IOs have been documented by @miek and @smunaut:
# https://github.com/q3k/chubby75/tree/master/5a-75b
# The Colorlight 5A-907 PCB, which is heavily based on the 5A-75B, has been documented by @chmouss:
# https://github.com/chmousset/colorlight_reverse


from litex.build.generic_platform import *
from litex.build.lattice import LatticeECP5Platform
from litex.build.lattice.programmer import OpenOCDJTAGProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io_v7_0 = [ # Documented by @miek and @chmouss
    # Clk
    ("clk25", 0, Pins("P6"), IOStandard("LVCMOS33")),

    # Led
    ("user_led_n", 0, Pins("P11"), IOStandard("LVCMOS33")),

    # Button
    ("user_btn_n", 0, Pins("M13"), IOStandard("LVCMOS33")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("P15")), # FAN pin 1
        Subsignal("rx", Pins("L14")), # FAN pin 2
        IOStandard("LVCMOS33")
    ),

    ("uartbone", 0,
        Subsignal("tx", Pins("F15")), # EXT_VOL pin 1
        Subsignal("rx", Pins("E16")), # EXT_VOL pin 2
        IOStandard("LVCMOS33")
    ),

    # SPIFlash (W25Q32JV)
    ("spiflash", 0,
        # clk
        Subsignal("cs_n", Pins("N8")),
        #Subsignal("clk",  Pins("")), driven through USRMCLK
        Subsignal("mosi", Pins("T8")),
        Subsignal("miso", Pins("T7")),
        IOStandard("LVCMOS33"),
    ),

    # SDR SDRAM (M126L6161A)
    ("sdram_clock", 0, Pins("C6"), IOStandard("LVCMOS33")),
    ("sdram", 0,
        Subsignal("a", Pins(
            "A9 E10 B12 D13 C12 D11 D10 E9",
            "D9 B7 C8")),
        Subsignal("dq", Pins(
            "B13 C11 C10 A11 C9 E8  B6  B9",
            "A6  B5  A5  B4  B3 C3  A2  B2",
            "E2  D3  A4  E4  D4 C4  E5  D5",
            "E6  D6  D8  A8  B8 B10 B11 E11")),
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
        #Subsignal("rst_n",   Pins("P5")),
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
        #Subsignal("rst_n",   Pins("P5")),
        Subsignal("mdio",    Pins("T2")),
        Subsignal("mdc",     Pins("P3")),
        Subsignal("rx_ctl",  Pins("L15")),
        Subsignal("rx_data", Pins("P13 N13 P14 M15")),
        Subsignal("tx_ctl",  Pins("R15")),
        Subsignal("tx_data", Pins("T14 R12 R13 R14")),
        IOStandard("LVCMOS33")
    ),

    # USB
    # To use the USB:
    # shunt R124 and R134
    # remove R107
    # connect R107's pad towards FPGA to R124 shunt through a 1.5k resistor
    # note: it conflicts with uartbone
    ("usb", 0,
        Subsignal("d_p", Pins("F15")),  # EXT_VOL pin 1
        Subsignal("d_n", Pins("E16")),  # EXT_VOL pin 2
        Subsignal("pullup", Pins("A12")),  # R107's pad towards FPGA
        IOStandard("LVCMOS33")
    ),
]

# Documented by @chmouss
_connectors_v7_0 = [
    ("door", "- - P16"),
    ("smoke", "- - M14 -"),
    ("fan", "- P15 L14"),
    ("ext_vol", "- F15 E16"),
    # pinout:  1  2  3   4   5   6 7  8  9   10  11  12  13 14  15  16  17  18  19  20 21  22  23  24  25  26
    ("j1", "-  L2 K1 F12 J14 B16 - J5 K2 F3  F1  T4  G3  -  G2  H3  R5  H5  J4  K3  -  R8  G1  K4  C2  P8  E3"),
    ("j2", "-  L2 K1 F12 J14 B16 - J2 J1 H4  K5  R7  P1  -  R1  L5  P7  F2  P4  R2  -  N7  M8  M9  T6  M7  R6"),
    ("j3", "-  L2 K1 F12 J14 B16 - G4 G5 M11 N11 L13 P12 -  K15 N12 G13 L16 K16 J15 -  G12 J16 J12 H15 F13 G16"),
    ("j4", "-  L2 K1 F12 J14 B16 - F5 F4 H13 J13 E15 H12 -  G14 H14 D16 G15 A15 F16 -  F14 A14 E13 B14 E14 A13"),
]


# Platform -----------------------------------------------------------------------------------------

class Platform(LatticeECP5Platform):
    default_clk_name   = "clk25"
    default_clk_period = 1e9/25e6

    def __init__(self, revision="7.0", toolchain="trellis"):
        assert revision in ["7.0"]
        self.revision = revision
        device     = {"7.0": "LFE5U-25F-6BG256C"}[revision]
        io         = {"7.0": _io_v7_0           }[revision]
        connectors = {"7.0": _connectors_v7_0   }[revision]
        LatticeECP5Platform.__init__(self, device, io, connectors=connectors, toolchain=toolchain)

    def create_programmer(self):
        return OpenOCDJTAGProgrammer("openocd_colorlight_5a_75b.cfg")

    def do_finalize(self, fragment):
        LatticeECP5Platform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk25",            loose=True), 1e9/25e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:rx", 0, loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:rx", 1, loose=True), 1e9/125e6)
