#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# The Colorlight 5A-75B PCB and IOs have been documented by @miek and @smunaut:
# https://github.com/q3k/chubby75/tree/master/5a-75b

from litex.build.generic_platform import *
from litex.build.lattice import LatticePlatform
from litex.build.lattice.programmer import OpenOCDJTAGProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io_v6_1 = [ # Documented by @smunaut
    # clock
    ("clk25", 0, Pins("P3"), IOStandard("LVCMOS33")),

    # led
    ("user_led_n", 0, Pins("U16"), IOStandard("LVCMOS33")),

    # btn
    ("user_btn_n", 0, Pins("R16"), IOStandard("LVCMOS33")),

    # serial
    # There seems to be some capacitance on KEY+ pin, so high baudrates may not work (>9600bps).
    ("serial", 0,
        Subsignal("tx", Pins("U16")), # led (J19 DATA_LED-)
        Subsignal("rx", Pins("R16")), # btn (J19 KEY+)
        IOStandard("LVCMOS33")
    ),

    # spi flash (GD25Q16CSIG)
    ("spiflash", 0,
        Subsignal("cs_n", Pins("R2")),
        Subsignal("clk",  Pins("U3")),
        Subsignal("mosi", Pins("W2")),
        Subsignal("miso", Pins("V2")),
        IOStandard("LVCMOS33"),
    ),

    # sdram (EM636165-6G)
    ("sdram_clock", 0, Pins("B9"), IOStandard("LVCMOS33")),
    ("sdram", 0,
        Subsignal("a", Pins(
            "B13 C14 A16 A17 B16 B15 A14 A13",
            "A12 A11 B12")),
        Subsignal("dq", Pins(
            "D15 E14 E13 D12 E12 D11 C10 B17",
            "B8  A8  C7  A7  A6  B6  A5  B5",
            "D5  C5  D6  C6  E7  D7  E8  D8",
            "E9  D9  E11 C11 C12 D13 D14 C15")),
        Subsignal("we_n",  Pins("A10")),
        Subsignal("ras_n", Pins("B10")),
        Subsignal("cas_n", Pins("A9")),
        #Subsignal("cs_n", Pins("")), # gnd
        #Subsignal("cke",  Pins("")), # 3v3
        Subsignal("ba",    Pins("B11")), # sdram pin a11 is ba
        #Subsignal("dm",   Pins("")), # gnd
        IOStandard("LVCMOS33"),
        Misc("SLEWRATE=FAST")
    ),

    # ethernet (B50612D)
    ("eth_clocks", 0,
        Subsignal("tx", Pins("G1")),
        Subsignal("rx", Pins("H2")),
        IOStandard("LVCMOS33")
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("P4")),
        Subsignal("mdio",    Pins("P5")),
        Subsignal("mdc",     Pins("N5")),
        Subsignal("rx_ctl",  Pins("P2")),
        Subsignal("rx_data", Pins("K2 L1 N1 P1")),
        Subsignal("tx_ctl",  Pins("K1")),
        Subsignal("tx_data", Pins("G2 H1 J1 J3")),
        IOStandard("LVCMOS33")
    ),

    ("eth_clocks", 1,
        Subsignal("tx", Pins("U19")),
        Subsignal("rx", Pins("L19")),
        IOStandard("LVCMOS33")
    ),
    ("eth", 1,
        Subsignal("rst_n",   Pins("P4")),
        Subsignal("mdio",    Pins("P5")),
        Subsignal("mdc",     Pins("N5")),
        Subsignal("rx_ctl",  Pins("L19")),
        Subsignal("rx_data", Pins("P20 N19 N20 N19")),
        Subsignal("tx_ctl",  Pins("P19")),
        Subsignal("tx_data", Pins("U20 T19 T20 R20")),
        IOStandard("LVCMOS33")
    ),
]

_io_v7_0 = [ # Documented by @miek
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

    ("usb", 0,
        Subsignal("d_p", Pins("M8")),
        Subsignal("d_n", Pins("R2")),
        Subsignal("pullup", Pins("P4")),
        IOStandard("LVCMOS33")
    ),
]

# from https://github.com/miek/chubby75/blob/5a-75b-v7_pinout/5a-75b/hardware_V6.1.md
_connectors_v6_1 = [
    ("j1", "B3  A2  B2   - B1  C2  C1  J17 F1  E2  E1  F2  C18 J18 H16 -"),
    ("j2", "D2  H3  H4   - J4  B4  A3  J17 F1  E2  E1  F2  C18 J18 H16 -"),
    ("j3", "D1  J5  K4   - K5  K3  E5  J17 F1  E2  E1  F2  C18 J18 H16 -"),
    ("j4", "N3  N4  R3   - T3  R1  T1  J17 F1  E2  E1  F2  C18 J18 H16 -"),
    ("j5", "U17 U18 T17  - T18 K20 L20 J17 F1  E2  E1  F2  C18 J18 H16 -"),
    ("j6", "J20 K19 J19  - G20 H20 G19 J17 F1  E2  E1  F2  C18 J18 H16 -"),
    ("j7", "F19 F20 E20  - D20 E19 D19 J17 F1  E2  E1  F2  C18 J18 H16 -"),
    ("j8", "B20 C20 B19  - B18 A19 A18 J17 F1  E2  E1  F2  C18 J18 H16 -"),
]

# from https://github.com/q3k/chubby75/blob/master/5a-75b/hardware_V7.0.md
_connectors_v7_0 = [
    ("j1", "F3  F1  G3  - G2  H3  H5  F15 L2 K1 J5 K2 B16 J14 F12 -"),
    ("j2", "J4  K3  G1  - K4  C2  E3  F15 L2 K1 J5 K2 B16 J14 F12 -"),
    ("j3", "H4  K5  P1  - R1  L5  F2  F15 L2 K1 J5 K2 B16 J14 F12 -"),
    ("j4", "P4  R2  M8  - M9  T6  R6  F15 L2 K1 J5 K2 B16 J14 F12 -"),
    ("j5", "M11 N11 P12 - K15 N12 L16 F15 L2 K1 J5 K2 B16 J14 F12 -"),
    ("j6", "K16 J15 J16 - J12 H15 G16 F15 L2 K1 J5 K2 B16 J14 F12 -"),
    ("j7", "H13 J13 H12 - G14 H14 G15 F15 L2 K1 J5 K2 B16 J14 F12 -"),
    ("j8", "A15 F16 A14 - E13 B14 A13 F15 L2 K1 J5 K2 B16 J14 F12 -"),
]



# Platform -----------------------------------------------------------------------------------------

class Platform(LatticePlatform):
    default_clk_name   = "clk25"
    default_clk_period = 1e9/25e6

    def __init__(self, revision="7.0"):
        assert revision in ["6.1", "7.0"]
        self.revision = revision
        device     = {"6.1": "LFE5U-25F-6BG381C", "7.0": "LFE5U-25F-6BG256C"}[revision]
        io         = {"6.1": _io_v6_1,            "7.0": _io_v7_0}[revision]
        connectors = {"6.1": _connectors_v6_1,            "7.0": _connectors_v7_0}[revision]
        LatticePlatform.__init__(self, device, io, connectors=connectors, toolchain="trellis")

    def create_programmer(self):
        return OpenOCDJTAGProgrammer("openocd_colorlight_5a_75b.cfg")

    def do_finalize(self, fragment):
        LatticePlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk25",            loose=True), 1e9/25e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:rx", 0, loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:rx", 1, loose=True), 1e9/125e6)