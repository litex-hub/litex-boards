#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2023 Hans Baier <hansfbaier@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

# This is a platform file for the ZXTRES Artix7 Core board
# https://github.com/zxtres/wiki/wiki

from litex.build.generic_platform import Pins, Subsignal, IOStandard, Misc
from litex.build.xilinx import Xilinx7SeriesPlatform
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk50", 0, Pins("Y18"), IOStandard("LVCMOS33")),

    # Leds.
    ("user_led", 0, Pins("H13"),  IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("A18"),  IOStandard("LVCMOS33")),

    # SPIFlash
    ("spiflash", 0,  # clock needs to be accessed through STARTUPE2
        Subsignal("cs_n", Pins("T19")),
        Subsignal("clk",  Pins("T4")),
        Subsignal("mosi", Pins("P22")),
        Subsignal("miso", Pins("R22")),
        Subsignal("wp",   Pins("P21")),
        Subsignal("hold", Pins("R21")),
        IOStandard("LVCMOS33")
    ),

    # SDRAM 32 MB W9825G6KH  (ZXTRES A35T)              
    # SDRAM 2 x 32 MB AS4C32M8SA (ZXTRES+ A100T, ZXTRES++ A200T)
    ("sdram_clock", 0, Pins("G20"), IOStandard("LVCMOS33")),
    ("sdram", 0,
        Subsignal("a",     Pins(
            "H19 K22 J21 J20 G16 J14 H14 G17", 
            "G18 H15 K21 J15 J22")),
        Subsignal("ba",    Pins("J19 H20")),
        Subsignal("cs_n",  Pins("N22")),
        Subsignal("cke",   Pins("H22")), 
        Subsignal("ras_n", Pins("K19")),
        Subsignal("cas_n", Pins("L18")),
        Subsignal("we_n",  Pins("J17")),
        Subsignal("dq", Pins(
            "M13 L13 L16 M15 K16 L14 K17 K14",
            "M21 M22 N19 M20 N18 N20 M16 L15")),
        Subsignal("dm", Pins("M18 L21")),
        IOStandard("LVCMOS33")
    ),    

    # SRAM IS61WV102416BLL
    ("sram", 0,
        Subsignal("a",    Pins("U18 AB18 P15 T18 R17 P14 AB3 Y3 R14 T3 P16 AA3 P17 G2 AA18 Y2 Y1 W1 V3 AB2")),
        Subsignal("dq",   Pins("N17 AA5 N14 N13 R16 AA1 AB1 U3 N2 P2 P1 R1 K6 L1 M1 K4")),
        Subsignal("oe_n", Pins("E1")),
        Subsignal("we_n", Pins("N15")),
        Subsignal("ub_n", Pins("U20")),
        Subsignal("lb_n", Pins("N4")),
        IOStandard("3.3-V LVCMOS"),
    ),

    ("displayport", 0,
        Subsignal("lanes_p", Pins("B4 D5")),
        Subsignal("lanes_n", Pins("A4 C5")),
        Subsignal("aux_p",   Pins("A15")),
        Subsignal("aux_n",   Pins("A16")),
    ),
]

# The connectors are named after the daughterboard, not the core board
# because on the different core boards the names vary, but on the
# daughterboard they stay the same, which we need to connect the
# daughterboard peripherals to the core board.
# On this board J2 is U2 and J3 is U4
_connectors = [
    ("J2", {    # JP2 ZXTRES schematics
         # odd row     even row
        # 1: "INIT_B",  2: "/RESET",    # Active Serial     # Negative Reset          
          7: "W21",     8: "R19",       # Active Serial 
          9: "W19",    10: "W22",
         11: "AA20",   12: "AA21",
         13: "Y21",    14: "Y22",
         15: "AB21",   16: "AB22",
         17: "T20",    18: "W20",
         19: "W17",    20: "V17",
         21: "AB20",   22: "AA19",
         23: "Y19",    24: "V20",
         25: "P20",    26: "P19",
         27: "V18",    28: "V19",
         29: "U17",    30: "V4",
         31: "U5",     32: "V5",
         33: "T6",     34: "T5",
         35: "U6",     36: "R6",
         37: "V9",     38: "U7",
         39: "V8",     40: "W9",
         41: "W7",     42: "V7",
         43: "W5",     44: "W6",
         45: "W4",     46: "Y6",
         47: "Y9",     48: "Y4",
         49: "AB8",    50: "Y8",
         51: "AB7",    52: "AA8",
         53: "AB6",    54: "Y7",
         55: "AB5",    56: "AA6",
         57: "W2",     58: "AA4",
         59: "U2",     60: "V2",
         63: "R22",    64: "L12",
    }),
    ("J3", {    # JP12 ZXTRES schematics
        # odd row     even row
         7: "B1",   8: "B22",
         9: "C2",  10: "B2",
        11: "F4",  12: "L6",
        13: "H18", 14: "N3",
        15: "M3",  16: "M2",
        17: "G1",  18: "F1",
        19: "F3",  20: "E3",
        21: "H17", 22: "D1",
        23: "E2",  24: "D2",
        25: "H4",  26: "G4",
        27: "K1",  28: "J1",
        29: "H2",  30: "G13",
        31: "K2",  32: "J2",
        33: "J5",  34: "H5",
        35: "H3",  36: "G3",
        37: "K18", 38: "J4",
        39: "L19", 40: "L20",
        41: "L3",  42: "K3",
        43: "K13", 44: "J6",
        45: "J16", 46: "M17",
        47: "T21", 48: "U21",
        49: "M6",  50: "M5",
        51: "L5",  52: "L4",
        53: "P5",  54: "P4",
        55: "P6",  56: "N5",
        57: "T1",  58: "U1",
        59: "R3",  60: "R2",
    })
]

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6
    kgates             = None

    def __init__(self, kgates=200, toolchain="vivado", with_daughterboard=False):
        assert(kgates in [35, 100, 200], "kgates can only be 35, 100 or 200 representing a XC7A35T, XC7A100T, XC7A200T")
        self.kgates = kgates
        device = f"xc7a{kgates}tfgg484-2"
        io = _io
        connectors = _connectors

        Xilinx7SeriesPlatform.__init__(self, device, io, connectors, toolchain=toolchain)

        self.toolchain.bitstream_commands = \
            ["set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]",
            "set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]"]
        self.toolchain.additional_commands = \
            ["write_cfgmem -force -format bin -interface spix4 -size 16 "
            "-loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"]

        self.add_platform_command("set_property INTERNAL_VREF 0.750 [get_iobanks 16]")
        self.add_platform_command("set_property CFGBVS VCCO [current_design]")
        self.add_platform_command("set_property CONFIG_VOLTAGE 3.3 [current_design]")

    def create_programmer(self):
        bscan_spi = f"bscan_spi_xc7a{self.kgates}t.bit"
        return OpenOCD("openocd_xc7_ft2232.cfg", bscan_spi)


    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
