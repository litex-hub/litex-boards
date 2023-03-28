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
    ("clk50", 0, Pins("W19"), IOStandard("LVCMOS33")),

    ("cpu_reset", 0,     Pins("Y6"),   IOStandard("LVCMOS33")),
    ("prog_b", 0,        Pins("N12"), IOStandard("LVCMOS33")),

    # The core board does not have a USB serial on it,
    # so you will have to attach an USB to serial adapter
    # on these pins
    ("gpio_serial", 0,
        Subsignal("tx", Pins("J2:7")),
        Subsignal("rx", Pins("J2:8")),
        IOStandard("LVCMOS33")
    ),

    # SPIFlash
    # 128Mbit SPI FLASH
    ("spiflash4x", 0,  # clock needs to be accessed through STARTUPE2
        Subsignal("cs_n", Pins("T19")),
        Subsignal("clk",  Pins("L12")),
        Subsignal("dq",   Pins("P22 R22 P21 R21")),
        IOStandard("LVCMOS33")
    ),

    # DDR3 SDRAM
    # MT41K128M16JT-125K
    ("ddram", 0,
        Subsignal("a", Pins("A15 D14 A14 D15 E14 F14 E13 C13 E16 B13 C17 F13 F16 A13"),
            IOStandard("SSTL15")),
        Subsignal("ba",    Pins("D16 E17 B15"), IOStandard("SSTL15")),
        Subsignal("ras_n", Pins("B17"), IOStandard("SSTL15")),
        Subsignal("cas_n", Pins("B16"), IOStandard("SSTL15")),
        Subsignal("we_n",  Pins("A16"), IOStandard("SSTL15")),
        # cs_n is hardwired on the board
        #Subsignal("cs_n",  Pins(""), IOStandard("SSTL15")),
        Subsignal("dm", Pins("F19 D20"), IOStandard("SSTL15")),
        Subsignal("dq", Pins(
            "B20 A18 A20 D19 A19 C18 C19 E19 C20 D22 D21 E21 C22 G21 B22 E22"),
            IOStandard("SSTL15"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("dqs_p", Pins("F18 B21"),
            IOStandard("DIFF_SSTL15"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("dqs_n", Pins("E18 A21"),
            IOStandard("DIFF_SSTL15"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("clk_p", Pins("C14"), IOStandard("DIFF_SSTL15")),
        Subsignal("clk_n", Pins("C15"), IOStandard("DIFF_SSTL15")),
        Subsignal("cke",   Pins("B18"), IOStandard("SSTL15")),
        Subsignal("odt",   Pins("D17"), IOStandard("SSTL15")),
        Subsignal("reset_n", Pins("F15"), IOStandard("SSTL15")),
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
          7: "H22",     8: "J22",
          9: "H18",    10: "H17",
         11: "K22",    12: "K21",
         13: "G20",    14: "H20",
         15: "H19",    16: "J19",
         17: "J21",    18: "J20",
         19: "J17",    20: "K17",
         21: "L20",    22: "L19",
         23: "H14",    24: "J14",
         25: "K14",    26: "K13",
         27: "M16",    28: "M15",
         29: "M20",    30: "N20",
         31: "M22",    32: "N22",
         33: "L15",    34: "L14",
         35: "N19",    36: "N18",
         37: "P17",    38: "N17",
         39: "T18",    40: "R18",
         41: "Y22",    42: "Y21",
         43: "U21",    44: "T21",
         45: "V20",    46: "U20",
         47: "U18",    48: "U17",
         49: "V19",    50: "V18",
         51: "AB22",   52: "AB21",
         53: "AA21",   54: "AA20",
         55: "AB20",   56: "AA19",
         57: "Y19",    58: "Y18",
         59: "AB18",   60: "AA18",
    }),
    ("J3", {
        # odd row     even row
         7: "B1",   8: "A1",
         9: "C2",  10: "B2",
        11: "E1",  12: "D1",
        13: "E2",  14: "D2",
        15: "G1",  16: "F1",
        17: "H2",  18: "G2",
        19: "K1",  20: "J1",
        21: "K2",  22: "J2",
        23: "M1",  24: "L1",
        25: "K4",  26: "J4",
        27: "L3",  28: "K3",
        29: "M3",  30: "M2",
        31: "P2",  32: "N2",
        33: "R1",  34: "P1",
        35: "P5",  36: "P4",
        37: "R4",  38: "T4",
        39: "T5",  40: "U5",
        41: "T1",  42: "U1",
        43: "W1",  44: "Y1",
        45: "AA1", 46: "AB1",
        47: "AB3", 48: "AB2",
        49: "V4",  50: "W4",
        51: "Y3",  52: "AA3",
        53: "Y4",  54: "AA4",
        55: "AA5", 56: "AB5",
        57: "AB7", 58: "AB6",
        59: "AA8", 60: "AB8",
    })
]

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6
    kgates             = None

    def __init__(self, kgates=200, toolchain="vivado", with_daughterboard=False):
        assert(kgates in [100, 200], "kgates can only be 100 or 200 representing a XC7A7100T, XC7TA200T")
        self.kgates = kgates
        device = f"xc7a{kgates}tfbg484-1"
        io = _io
        connectors = _connectors

        core_leds_name = "onboard_led" if with_daughterboard else "user_led"
        io += [
            (core_leds_name, 0, Pins("F3"),  IOStandard("LVCMOS33")),
            (core_leds_name, 1, Pins("E3"),  IOStandard("LVCMOS33")),
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
