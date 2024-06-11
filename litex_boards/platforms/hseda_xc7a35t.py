#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2024 Akio Lin <akioolin@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # CPU Clock
    ("clk50",     0, Pins("D4"), IOStandard("LVCMOS33")),

    # CPU Reset
    ("cpu_reset", 0, Pins("C4"), IOStandard("LVCMOS33")),

    # User LEDs
    ("user_led",  0, Pins("K12"), IOStandard("LVCMOS33")),
    ("user_led",  1, Pins("L14"), IOStandard("LVCMOS33")),
    ("user_led",  2, Pins("L13"), IOStandard("LVCMOS33")),
    ("user_led",  3, Pins("M14"), IOStandard("LVCMOS33")),

    # User Keys
    ("user_btn",  0, Pins("D11"), IOStandard("SSTL15")),
    ("user_btn",  1, Pins("G11"), IOStandard("SSTL15")),
    ("user_btn",  2, Pins("H11"), IOStandard("SSTL15")),
    ("user_btn",  3, Pins("K13"), IOStandard("LVCMOS33")),

    # UART
    ("serial", 0,
        Subsignal("tx", Pins("E6")),
        Subsignal("rx", Pins("C7")),
        IOStandard("LVCMOS33")
    ),

    # I2C bus for RTC DS1302
    ("i2c", 0,
        Subsignal("sda", Pins("N13"), IOStandard("LVCMOS33")),
        Subsignal("scl", Pins("M12"), IOStandard("LVCMOS33")),
    ),

    # RST for RTC DS1302
	("gpio", 0, Pins("P13"), IOStandard("LVCMOS33")),

    # SD-Card.
    ("sdcard", 0,
#        Subsignal("cd",   Pins("N6")),
        Subsignal("cmd",  Pins("M4")),
        Subsignal("clk",  Pins("N4")),
        Subsignal("data", Pins("P3 P4 N3 M5")),
        Misc("SLEW=FAST"),
        IOStandard("LVCMOS33"),
    ),

    # SPIFlash
    # N25Q128A13ESE40F
    ("spiflash", 0,
        Subsignal("cs_n", Pins("L12")),
        Subsignal("clk",  Pins("E8")),
        Subsignal("mosi", Pins("J13")),
        Subsignal("miso", Pins("J14")),
        Subsignal("wp",   Pins("K15")),
        Subsignal("hold", Pins("K16")),
        IOStandard("LVCMOS33"),
    ),
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("L12")),
        Subsignal("clk",  Pins("E8")),
        Subsignal("dq",   Pins("J13", "J14", "K15", "K16")),
        IOStandard("LVCMOS33")
    ),

    # DDR3 SDRAM
    # MT41K128M16JT-125
    ("ddram", 0,
        Subsignal("a", Pins("C11 A12 D9 A15 B12 C9 B11 D8 B10 C8 C12 A9 B14 A8"),
            IOStandard("SSTL15")),
        Subsignal("ba",    Pins("C14 A13 B15"), IOStandard("SSTL15")),
        Subsignal("ras_n", Pins("C16"), IOStandard("SSTL15")),
        Subsignal("cas_n", Pins("D13"), IOStandard("SSTL15")),
        Subsignal("we_n",  Pins("B16"), IOStandard("SSTL15")),
        # cs_n is hardwired on the board
        #Subsignal("cs_n",  Pins("-"), IOStandard("SSTL135")),
        Subsignal("dm", Pins("F12 G16"), IOStandard("SSTL15")),
        Subsignal("dq", Pins(
            "F15 F13 E15 E13 D16 E11 E16 E12",
            "H13 H16 G15 H14 H12 J15 G12 J16"),
            IOStandard("SSTL15"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("dqs_p", Pins("D14 G14"),
            IOStandard("DIFF_SSTL15"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("dqs_n", Pins("D15 F14"),
            IOStandard("DIFF_SSTL15"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("clk_p", Pins("B9"), IOStandard("DIFF_SSTL15")),
        Subsignal("clk_n", Pins("A10"), IOStandard("DIFF_SSTL15")),
        Subsignal("cke",   Pins("A14"), IOStandard("SSTL15")),
        Subsignal("odt",   Pins("C13"), IOStandard("SSTL15")),
        Subsignal("reset_n", Pins("D10"), IOStandard("LVCMOS15")),
        Misc("SLEW=FAST"),
    ),
]

# On board J6, J7
_connectors = [
    ("J6", {
         #odd row    even row
                     2: "M16",
          3: "N16",  4: "L15",
                     6: "M15",
          7: "R16",  8: "P16",
          9: "R15", 10: "P15",
         11: "T15", 12: "P14",
         13: "T14", 14: "N14",
         15: "N12", 16: "T13",
         17: "N11", 18: "R13",
         19: "R11", 20: "T12",
         21: "R10", 22: "R12",
         23: "T10", 24: "P11",
         25: "T9",  26: "P10",
         27: "T8",  28: "P9",
         29: "T7",  30: "N9",
         31: "R7",  32: "R8",
         33: "R6",  34: "P8",
         35: "T5",  36: "N6",
         37: "R5",  38: "M6",
         39: "P6",
    }),
    ("J7", {
         #odd row    even row
                     2: "K3",
          3: "J3",   4: "J4",
                     6: "J5",
          7: "H4",   8: "G4",
          9: "H5",  10: "G5",
         11: "G1",  12: "F3",
         13: "G2",  14: "F4",
         15: "F2",  16: "C2",
         17: "E1",  18: "C3",
         19: "E2",  20: "D3",
         21: "D1",  22: "E3",
         23: "C1",  24: "A4",
         25: "B1",  26: "A5",
         27: "B2",  28: "E5",
         29: "A2",  30: "F5",
         31: "A3",  32: "D5",
         33: "B4",  34: "D6",
         35: "B5",  36: "A7",
         37: "B6",  38: "B7",
         39: "C6",
    })
]

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self, toolchain="vivado", with_core_resources=True):
        device = "xc7a35tftg256-1"
        io = _io
        connectors = _connectors

        Xilinx7SeriesPlatform.__init__(self, device, io, connectors, toolchain=toolchain)

        self.toolchain.bitstream_commands = \
            ["set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]"]
        self.toolchain.additional_commands = \
            ["write_cfgmem -force -format bin -interface spix4 -size 16 "
            "-loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"]
        self.add_platform_command("set_property INTERNAL_VREF 0.750 [get_iobanks 15]")
        self.add_platform_command("set_property CFGBVS VCCO [current_design]")
        self.add_platform_command("set_property CONFIG_VOLTAGE 3.3 [current_design]")

    def create_programmer(self):
        bscan_spi = "bscan_spi_xc7a35t.bit"
        return OpenOCD("openocd_xc7_ft232.cfg", bscan_spi)

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
