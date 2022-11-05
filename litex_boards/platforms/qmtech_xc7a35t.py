#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Hans Baier <hansfbaier@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import Pins, Subsignal, IOStandard, Misc
from litex.build.xilinx import Xilinx7SeriesPlatform
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk50", 0, Pins("N11"), IOStandard("LVCMOS33")),

    # The core board does not have a USB serial on it,
    # so you will have to attach an USB to serial adapter
    # on these pins
    ("gpio_serial", 0,
        Subsignal("tx", Pins("J2:7")),
        Subsignal("rx", Pins("J2:8")),
        IOStandard("LVCMOS33")
    ),

    # SPIFlash
    # MT25QL128
    ("spiflash4x", 0,  # clock needs to be accessed through STARTUPE2
        Subsignal("cs_n", Pins("L12")),
        Subsignal("clk",  Pins("E8")),
        Subsignal("dq",   Pins("J13", "J14", "K15", "K16")),
        IOStandard("LVCMOS33")
    ),

    # DDR3 SDRAM
    # MT41J128M16JT-125K
    ("ddram", 0,
        Subsignal("a", Pins("B14 C8 A14 C14 C9 B10 D9 A12 D8 A13 B12 A9 A8 B11"),
            IOStandard("SSTL135")),
        Subsignal("ba", Pins("C16 A15 B15"), IOStandard("SSTL135")),
        Subsignal("ras_n", Pins("B16"), IOStandard("SSTL135")),
        Subsignal("cas_n", Pins("C11"), IOStandard("SSTL135")),
        Subsignal("we_n",  Pins("C12"), IOStandard("SSTL135")),
        # cs_n is hardwired on the board
        #Subsignal("cs_n",  Pins("-"), IOStandard("SSTL135")),
        Subsignal("dm", Pins("F12 H11"), IOStandard("SSTL135")),
        Subsignal("dq", Pins(
            "F15 F13 E16 D11 E12 E13 D16 E11",
            "G12 J16 G16 J15 H14 H12 H16 H13"),
            IOStandard("SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("dqs_p", Pins("D14 G14"),
            IOStandard("DIFF_SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("dqs_n", Pins("D15 F14"),
            IOStandard("DIFF_SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("clk_p", Pins("B9"), IOStandard("DIFF_SSTL135")),
        Subsignal("clk_n", Pins("A10"), IOStandard("DIFF_SSTL135")),
        Subsignal("cke",   Pins("D13"), IOStandard("SSTL135")),
        Subsignal("odt",   Pins("C13"), IOStandard("SSTL135")),
        Subsignal("reset_n", Pins("E15"), IOStandard("SSTL135")),
        Misc("SLEW=FAST"),
    ),
]

# The connectors are named after the daughterboard, not the core board
# because on the different core boards the names vary, but on the
# daughterboard they stay the same, which we need to connect the
# daughterboard peripherals to the core board.
# On this board J2 is U7 and J3 is U8
_connectors = [
    ("J2", {
         # odd row     even row
          7: "M12",   8: "N13",
          9: "N14",  10: "N16",
         11: "P15",  12: "P16",
         13: "R15",  14: "R16",
         15: "T14",  16: "T15",
         17: "P13",  18: "P14",
         19: "T13",  20: "R13",
         21: "T12",  22: "R12",
         23: "L13",  24: "N12",
         25: "K12",  26: "K13",
         27: "P10",  28: "P11",
         29: "N9",   30: "P9",
         31: "T10",  32: "R11",
         33: "T9",   34: "R10",
         35: "T8",   36: "R8",
         37: "T7",   38: "R7",
         39: "T5",   40: "R6",
         41: "P6",   42: "R5",
         43: "N6",   44: "M6",
         45: "L5",   46: "P5",
         47: "T4",   48: "T3",
         49: "R3",   50: "T2",
         51: "R2",   52: "R1",
         53: "M5",   54: "N4",
         55: "P4",   56: "P3",
         57: "N1",   58: "P1",
         59: "M2",   60: "M1",
    }),
    ("J3", {
        # odd row     even row
         7: "B7",   8: "A7",
         9: "B6",  10: "B5",
        11: "E6",  12: "K5",
        13: "J5",  14: "J4",
        15: "G5",  16: "G4",
        17: "C7",  18: "C6",
        19: "D6",  20: "D5",
        21: "A5",  22: "A4",
        23: "B4",  24: "A3",
        25: "D4",  26: "C4",
        27: "C3",  28: "C2",
        29: "B2",  30: "A2",
        31: "C1",  32: "B1",
        33: "E2",  34: "D1",
        35: "E3",  36: "D3",
        37: "F5",  38: "E5",
        39: "F2",  40: "E1",
        41: "F4",  42: "F3",
        43: "G2",  44: "G1",
        45: "H2",  46: "H1",
        47: "K1",  48: "J1",
        49: "L3",  50: "L2",
        51: "H5",  52: "H4",
        53: "J3",  54: "H3",
        55: "K3",  56: "K2",
        57: "L4",  58: "M4",
        59: "N3",  60: "N2",
    })
]

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6

    # these resources conflict with daughterboard resources
    # so they are only used if the daughterboard is not present
    core_resources = [
        ("user_led", 0, Pins("E6"), IOStandard("LVCMOS33")),
        ("cpu_reset", 0, Pins("K5"), IOStandard("LVCMOS33")),
    ]

    def __init__(self, toolchain="vivado", with_daughterboard=False):
        device = "xc7a35tftg256-1"
        io = _io
        connectors = _connectors

        if with_daughterboard:
            from litex_boards.platforms.qmtech_daughterboard import QMTechDaughterboard
            daughterboard = QMTechDaughterboard(IOStandard("LVCMOS33"))
            io += daughterboard.io
            connectors += daughterboard.connectors
        else:
            io += self.core_resources

        Xilinx7SeriesPlatform.__init__(self, device, io, connectors, toolchain=toolchain)
        self.toolchain.bitstream_commands = \
            ["set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]"]
        self.toolchain.additional_commands = \
            ["write_cfgmem -force -format bin -interface spix4 -size 16 "
             "-loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"]
        self.add_platform_command("set_property INTERNAL_VREF 0.675 [get_iobanks 15]")
        self.add_platform_command("set_property CFGBVS VCCO [current_design]")
        self.add_platform_command("set_property CONFIG_VOLTAGE 3.3 [current_design]")
        self.toolchain.f4pga_device = device

    def create_programmer(self):
        bscan_spi = "bscan_spi_xc7a35t.bit"
        return OpenOCD("openocd_xc7_ft2232.cfg", bscan_spi)


    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)