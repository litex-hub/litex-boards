# This file is Copyright (c) 2020 Vadim Kaushan <admin@disasm.info>
# License: BSD

# The Colorlight 5A-75E PCB and IOs have been documented by @derekmulcahy:
# https://github.com/q3k/chubby75/issues/59

from litex.build.generic_platform import *
from litex.build.lattice import LatticePlatform
from litex.build.lattice.programmer import OpenOCDJTAGProgrammer

# IOs ----------------------------------------------------------------------------------------------

# Documented by @derekmulcahy
_io_v7_1 = [
    # clock
    ("clk25", 0, Pins("P6"), IOStandard("LVCMOS33")),

    # led
    ("user_led_n", 0, Pins("P11"), IOStandard("LVCMOS33")),

    # btn
    ("user_btn_n", 0, Pins("M13"), IOStandard("LVCMOS33")),

    # serial
    ("serial", 0,
        Subsignal("tx", Pins("P11")), # led (J19 DATA_LED-)
        Subsignal("rx", Pins("M13")), # btn (J19 KEY+)
        IOStandard("LVCMOS33")
    ),

    # spiflash (W25Q32JV)
    ("spiflash", 0,
        # clk
        Subsignal("cs_n", Pins("N8")),
        #Subsignal("clk",  Pins("")), driven through USRMCLK
        Subsignal("mosi", Pins("T8")),
        Subsignal("miso", Pins("T7")),
        IOStandard("LVCMOS33"),
    ),

    # sdram (M12616161A)
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

    # ethernet (B50612D)
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

# from https://github.com/q3k/chubby75/blob/master/5a-75b/hardware_V7.1.md
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


# Platform -----------------------------------------------------------------------------------------

class Platform(LatticePlatform):
    default_clk_name = "clk25"
    default_clk_period = 1e9/25e6

    def __init__(self, revision="7.1"):
        assert revision in ["7.1"]
        self.revision = revision
        device = {"7.1": "LFE5U-25F-6BG256C"}[revision]
        io = {"7.1": _io_v7_1}[revision]
        connectors = {"7.1": _connectors_v7_1}[revision]
        LatticePlatform.__init__(self, device, io, connectors=connectors, toolchain="trellis")

    def create_programmer(self):
        return OpenOCDJTAGProgrammer("openocd_colorlight_5a_75b.cfg")

    def do_finalize(self, fragment):
        LatticePlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk25",            loose=True), 1e9/25e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:rx", 0, loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:rx", 1, loose=True), 1e9/125e6)
