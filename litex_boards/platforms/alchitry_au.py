#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Nathaniel Lewis <github@nrlewis.dev>
# SPDX-License-Identifier: BSD-2-Clause

# The Alchitry Au is the "gold" standard for FPGA development boards.
#
# The larger of the twin successors to the Mojo V3, this board is produced
# by SparkFun - https://www.sparkfun.com/products/16527.

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk100", 0, Pins("N14"), IOStandard("LVCMOS33")),
    ("cpu_reset_n", 0, Pins("P6"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led", 0, Pins("K13"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("K12"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("L14"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("L13"), IOStandard("LVCMOS33")),
    ("user_led", 4, Pins("M16"), IOStandard("LVCMOS33")),
    ("user_led", 5, Pins("M14"), IOStandard("LVCMOS33")),
    ("user_led", 6, Pins("M12"), IOStandard("LVCMOS33")),
    ("user_led", 7, Pins("N16"), IOStandard("LVCMOS33")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("P16")),
        Subsignal("rx", Pins("P15")),
        IOStandard("LVCMOS33")
    ),

    # I2C
    ("i2c", 0,
        Subsignal("scl", Pins("E6")),
        Subsignal("sda", Pins("K5")),
        IOStandard("LVCMOS33"),
    ),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("L12")),
        #Subsignal("clk",  Pins("")), # Accessed through STARTUPE2.
        Subsignal("mosi", Pins("J13")),
        Subsignal("miso", Pins("J14")),
        Subsignal("wp",   Pins("K15")),
        Subsignal("hold", Pins("K16")),
        IOStandard("LVCMOS33")
    ),
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("L12")),
        #Subsignal("clk",  Pins("")), # Accessed through STARTUPE2.
        Subsignal("dq",   Pins("J13", "J14", "K15", "K16")),
        IOStandard("LVCMOS33")
    ),

    # DDR3 SDRAM
    ("ddram", 0,
        Subsignal("a", Pins(
            "F12 G16 G15 E16 H11 G12 H16",
            "H12 J16 H13 E12 H14 F13 J15"),
            IOStandard("SSTL135")),
        Subsignal("ba",    Pins("E13 F15 E15"), IOStandard("SSTL135")),
        Subsignal("ras_n", Pins("D11"),  IOStandard("SSTL135")),
        Subsignal("cas_n", Pins("D14"),  IOStandard("SSTL135")),
        Subsignal("we_n",  Pins("E11"),  IOStandard("SSTL135")),
        Subsignal("dm", Pins("A14 C9"), IOStandard("SSTL135")),
        Subsignal("dq", Pins(
            "A13 B16 B14 C11 C13 C16 C12 C14",
            "D8  B11 C8  B10 A12 A8  B12 A9"),
            IOStandard("SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_50")),
        Subsignal("dqs_p",
            Pins("B15 B9"),
            IOStandard("DIFF_SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_50")),
        Subsignal("dqs_n",
            Pins("A15 A10"),
            IOStandard("DIFF_SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_50")),
        Subsignal("clk_p", Pins("G14"), IOStandard("DIFF_SSTL135")),
        Subsignal("clk_n", Pins("F14"), IOStandard("DIFF_SSTL135")),
        Subsignal("cke",   Pins("D15"), IOStandard("SSTL135")),
        Subsignal("odt",   Pins("G11"), IOStandard("SSTL135")),
        Subsignal("cs_n",  Pins("D16"), IOStandard("SSTL135")),
        Subsignal("reset_n", Pins("D13"), IOStandard("SSTL135")),
        Misc("SLEW=FAST"),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("A", { # X3.
         2: "T8",  3: "T7",
         5: "T5",  6: "R5",
         8: "R8",  9: "P8",
        11: "L2", 12: "L3",
        14: "J1", 15: "K1",
        17: "H1", 18: "H2",
        20: "G1", 21: "G2",
        23: "K5", 24: "E6",
        27: "M6", 28: "N6",
        30: "H5", 31: "H4",
        33: "J3", 34: "H3",
        36: "J5", 37: "J4",
        39: "K3", 40: "K2",
        42: "N9", 43: "P9",
        45: "R7", 46: "R6",
        48: "T9", 49: "T10",
    }),
    ("B", { # X4.
         2: "D1",  3: "E2",
         5: "A2",  6: "B2",
         8: "E1",  9: "F2",
        11: "F3", 12: "F4",
        14: "A3", 15: "B4",
        17: "A4", 18: "A5",
        20: "B5", 21: "B6",
        23: "A7", 24: "B7",
        27: "C7", 28: "C6",
        30: "D6", 31: "D5",
        33: "F5", 34: "E5",
        36: "G5", 37: "G4",
        39: "D4", 40: "C4",
        42: "E3", 43: "D3",
        45: "C3", 46: "C2",
        48: "C1", 49: "B1",
    }),
    ("C", { # X5.
         2: "T13",  3: "R13",
         5: "T12",  6: "R12",
         8: "R11", 10: "R10",
        11: "N2",  12: "N3",
        14: "P3",  15: "P4",
        17: "M4",  18: "L4",
        20: "N4",  21: "M5",
        23: "L5",  24: "P5",
        27: "T4",  28: "T3",
        30: "R3",  31: "T2",
        33: "R2",  34: "R1",
        36: "N1",  37: "P1",
        39: "M2",  40: "M1",
        41: "N13", 43: "P13",
        45: "N11", 46: "N12",
        48: "P10", 49: "P11",
    }),
    ("D", { # X6.
         2: "L14",  3: "L13",
         5: "M12",  6: "N16",
         8: "R16", 10: "R15",
        11: "P14", 12: "M15",
        14: "P15", 15: "P16",
        39: "P6",  40: "N14",
        41: "T14", 43: "T15",
        45: "M14", 46: "M16",
        48: "K12", 49: "K13",
    }),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self, variant="au", toolchain="vivado"):
        device = {
            "au":  "xc7a35t-ftg256-1",
            "au+": "xc7a100t-ftg256-2",
        }[variant]

        Xilinx7SeriesPlatform.__init__(self, device, _io, _connectors, toolchain=toolchain)
        self.add_platform_command("set_property INTERNAL_VREF 0.675 [get_iobanks 15]")

        self.toolchain.bitstream_commands = [
            "set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]",
            "set_property BITSTREAM.CONFIG.CONFIGRATE 33 [current_design]",
            "set_property CONFIG_VOLTAGE 3.3 [current_design]",
            "set_property CFGBVS VCCO [current_design]",
            "set_property BITSTREAM.CONFIG.SPI_32BIT_ADDR NO [current_design]",
            "set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 1 [current_design]",
            "set_property BITSTREAM.CONFIG.SPI_FALL_EDGE YES [current_design]",
        ]
        self.toolchain.additional_commands = \
            ["write_cfgmem -force -format bin -interface spix1 -size 4 "
             "-loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"]

    def create_programmer(self):
        return OpenOCD("openocd_xc7_ft2232.cfg", "bscan_spi_xc7a35t.bit")

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100", loose=True), 1e9/100e6)
