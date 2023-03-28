#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2023 Hans Baier <hansfbaier@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import Pins, Subsignal, IOStandard, Misc
from litex.build.xilinx import Xilinx7SeriesPlatform
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk50", 0, Pins("U22"), IOStandard("LVCMOS33")),

    ("cpu_reset", 0,     Pins("P4"),   IOStandard("LVCMOS33")),
    ("prog_b", 0,        Pins("AE16"), IOStandard("LVCMOS33")),

    # The core board does not have a USB serial on it,
    # so you will have to attach an USB to serial adapter
    # on these pins
    ("gpio_serial", 0,
        Subsignal("tx", Pins("J2:7")),
        Subsignal("rx", Pins("J2:8")),
        IOStandard("LVCMOS33")
    ),

    # SPIFlash
    # N25Q064A
    ("spiflash4x", 0,  # clock needs to be accessed through STARTUPE2
        Subsignal("cs_n", Pins("P18")),
        Subsignal("clk",  Pins("H13")),
        Subsignal("dq",   Pins("R14 R15 P14 N14")),
        IOStandard("LVCMOS33")
    ),

    # DDR3 SDRAM
    # MT41K128M16JT-125K
    ("ddram", 0,
        Subsignal("a", Pins("E17 G17 F17 C17 G16 D16 H16 E16 H14 F15 F20 H15 C18 G15"),
            IOStandard("SSTL15")),
        Subsignal("ba",    Pins("B17 D18 A17"), IOStandard("SSTL15")),
        Subsignal("ras_n", Pins("A19"), IOStandard("SSTL15")),
        Subsignal("cas_n", Pins("B19"), IOStandard("SSTL15")),
        Subsignal("we_n",  Pins("A18"), IOStandard("SSTL15")),
        # cs_n is hardwired on the board
        #Subsignal("cs_n",  Pins(""), IOStandard("SSTL15")),
        Subsignal("dm", Pins("A22 C22"), IOStandard("SSTL15")),
        Subsignal("dq", Pins(
            "D21 C21 B22 B21 D19 E20 C19 D20 C23 D23 B24 B25 C24 C26 A25 B26"),
            IOStandard("SSTL15"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("dqs_p", Pins("B20 A23"),
            IOStandard("DIFF_SSTL15"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("dqs_n", Pins("A20 A24"),
            IOStandard("DIFF_SSTL15"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("clk_p", Pins("F18"), IOStandard("DIFF_SSTL15")),
        Subsignal("clk_n", Pins("F19"), IOStandard("DIFF_SSTL15")),
        Subsignal("cke",   Pins("E18"), IOStandard("SSTL15")),
        Subsignal("odt",   Pins("G19"), IOStandard("SSTL15")),
        Subsignal("reset_n", Pins("H17"), IOStandard("SSTL15")),
        Misc("SLEW=FAST"),
    ),
]

# The connectors are named after the daughterboard, not the core board
# because on the different core boards the names vary, but on the
# daughterboard they stay the same, which we need to connect the
# daughterboard peripherals to the core board.
# On this board J2 is U2 and J3 is U4
_connectors = [
    ("J2", {
         # odd row     even row
          7: "D26",     8: "E26",
          9: "D25",    10: "E25",
         11: "G26",    12: "H26",
         13: "E23",    14: "F23",
         15: "F22",    16: "G22",
         17: "J26",    18: "J25",
         19: "G21",    20: "G20",
         21: "H22",    22: "H21",
         23: "J21",    24: "K21",
         25: "K26",    26: "K25",
         27: "K23",    28: "K22",
         29: "M26",    30: "N26",
         31: "L23",    32: "L22",
         33: "P26",    34: "R26",
         35: "M25",    36: "M24",
         37: "N22",    38: "N21",
         39: "P24",    40: "P23",
         41: "P25",    42: "R25",
         43: "T25",    44: "T24",
         45: "V21",    46: "U21",
         47: "W23",    48: "V23",
         49: "Y23",    50: "Y22",
         51: "AA25",   52: "Y25",
         53: "AC24",   54: "AB24",
         55: "Y21",    56: "W21",
         57: "Y26",    58: "W25",
         59: "AC26",   60: "AB26",
    }),
    ("J3", {
        # odd row     even row
         7: "B5",   8: "A5",
         9: "B4",  10: "A4",
        11: "A3",  12: "A2",
        13: "D4",  14: "C4",
        15: "C2",  16: "B2",
        17: "E5",  18: "D5",
        19: "C1",  20: "B1",
        21: "E1",  22: "D1",
        23: "F2",  24: "E2",
        25: "G4",  26: "F4",
        27: "G2",  28: "G1",
        29: "J4",  30: "H4",
        31: "H2",  32: "H1",
        33: "H9",  34: "G9",
        35: "M2",  36: "L2",
        37: "L5",  38: "K5",
        39: "M4",  40: "L4",
        41: "N3",  42: "N2",
        43: "M6",  44: "M5",
        45: "K1",  46: "J1",
        47: "R3",  48: "P3",
        49: "T4",  50: "T3",
        51: "P6",  52: "P5",
        53: "N1",  54: "M1",
        55: "R1",  56: "P1",
        57: "T2",  58: "R2",
        59: "U2",  60: "U1",
    })
]

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6
    kgates             = None

    def __init__(self, kgates=100, toolchain="vivado", with_daughterboard=False):
        assert(kgates in [75, 100], "kgates can only be 75 or 100 representing a XC7A75T, XC7TA100T")
        self.kgates = kgates
        device = f"xc7a{kgates}tfgg676-1"
        io = _io
        connectors = _connectors

        core_leds_name = "onboard_led" if with_daughterboard else "user_led"
        io += [
            (core_leds_name, 0, Pins("T23"),  IOStandard("LVCMOS33")),
            (core_leds_name, 1, Pins("R23"),  IOStandard("LVCMOS33")),
        ]

        if with_daughterboard:
            from litex_boards.platforms.qmtech_daughterboard import QMTechDaughterboard
            daughterboard = QMTechDaughterboard(IOStandard("LVCMOS33"))
            io += daughterboard.io
            connectors += daughterboard.connectors

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
        self.toolchain.f4pga_device = device

    def create_programmer(self):
        bscan_spi = f"bscan_spi_xc7a{self.kgates}t.bit"
        return OpenOCD("openocd_xc7_ft2232.cfg", bscan_spi)


    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)