# This file is Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# License: BSD

# The Colorlight 5A-75B PCB and IOs have been documented by @miek and @smunaut:
# https://github.com/q3k/chubby75/tree/master/5a-75b

from litex.build.generic_platform import *
from litex.build.lattice import LatticePlatform

# IOs ----------------------------------------------------------------------------------------------

_io_v6_1 = [ # Documented by @smunaut
    # clock
    ("clk25", 0, Pins("P3"), IOStandard("LVCMOS33")),

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
            "A12 A11 B12 A11")),
        Subsignal("dq", Pins(
            "D15 E14 E13 D12 E12 D11 C10 B17",
            "B8  A8  C7  A7  A6  B6  A5  B5",
            "D5  C5  D6  C6  E7  D7  E8  D8", # FIXME: D8 was D9
            "E9  D9  E11 C11 C12 D13 D14 C15")),
        Subsignal("we_n",  Pins("A10")),
        Subsignal("ras_n", Pins("B10")),
        Subsignal("cas_n", Pins("A9")),
        #Subsignal("cs_n", Pins("")), # gnd
        #Subsignal("cke",  Pins("")), # 3v3
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
        Subsignal("tx", Pins("")),
        Subsignal("rx", Pins("")),
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

    # sdram (M12616161A)
    ("sdram_clock", 0, Pins("B9"), IOStandard("LVCMOS33")),
    ("sdram", 0,
        Subsignal("a", Pins(
            "A9 E10 B12 D13 C1 D11 D10 E9",
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
        Subsignal("rx", Pins("P5")), # FIXME: already used for rst_n
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

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticePlatform):
    def __init__(self, revision="7.0"):
        assert revision in ["6.1", "7.0"]
        self.revision = revision
        device = {"6.1": "LFE5U-25F-6BG381C", "7.0": "LFE5U-25F-6BG256C"}[revision]
        io     = {"6.1": _io_v6_1,            "7.0": _io_v7_0}[revision]
        LatticePlatform.__init__(self, device, io, toolchain="trellis")
