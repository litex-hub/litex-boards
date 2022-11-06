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
    ("cpu_reset", 0, Pins("P6"), IOStandard("LVCMOS33")),

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
    ("spiflash", 0,  # clock needs to be accessed through STARTUPE2
        Subsignal("cs_n", Pins("L12")),
        Subsignal("mosi", Pins("J13")),
        Subsignal("miso", Pins("J14")),
        Subsignal("wp",   Pins("K15")),
        Subsignal("hold", Pins("K16")),
        IOStandard("LVCMOS33")
    ),
    ("spiflash4x", 0,  # clock needs to be accessed through STARTUPE2
        Subsignal("cs_n", Pins("L12")),
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

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self, variant="au", toolchain="vivado"):
        device = {
            "au":  "xc7a35t-ftg256-1",
            "au+": "xc7a100t-ftg256-2",
        }[variant]

        Xilinx7SeriesPlatform.__init__(self, device, _io, toolchain=toolchain)
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
