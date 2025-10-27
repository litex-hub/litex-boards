#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
# 
# Copyright (c) 2025 Victor Vimbert-Guerlais <victor.vimbertguerlais@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

# The board can be found at https://alchitry.com/

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform
from litex.build.openocd import OpenOCD

_io = [
    # Clk / Rst
    ("clk100", 0, Pins("W19"), IOStandard("LVCMOS33")),
    ("cpu_reset", 0, Pins("N15"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led", 0, Pins("P19"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("P20"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("T21"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("R19"), IOStandard("LVCMOS33")),
    ("user_led", 4, Pins("V22"), IOStandard("LVCMOS33")),
    ("user_led", 5, Pins("U21"), IOStandard("LVCMOS33")),
    ("user_led", 6, Pins("T20"), IOStandard("LVCMOS33")),
    ("user_led", 7, Pins("W20"), IOStandard("LVCMOS33")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("AA21")),
        Subsignal("rx", Pins("AA20")),
        IOStandard("LVCMOS33")
    ),

    ("spiflash", 0,  # clock needs to be accessed through STARTUPE2
        Subsignal("cs_n", Pins("T19")),
        Subsignal("mosi", Pins("P22")),
        Subsignal("miso", Pins("M21")),
        Subsignal("wp",   Pins("L21")),
        Subsignal("hold", Pins("R21")),
        IOStandard("LVCMOS33")
    ),
    
    ("spiflash4x", 0,  # clock needs to be accessed through STARTUPE2
        Subsignal("cs_n", Pins("T19")),
        Subsignal("dq",   Pins("P22", "M21", "L21", "R21")),
        IOStandard("LVCMOS33")
    ),

    # DDR3 SDRAM
    ("ddram", 0,
        Subsignal("a", Pins(
            "K14 M15 N18 K16 L14 K18 M13", # a0 -> a6 (included)
            "L18 L13 M18 K13 L15 M16 L16"), # a7 -> a13
            IOStandard("SSTL135")),
        Subsignal("ba",    Pins("K19 N20 M20"), IOStandard("SSTL135")),
        Subsignal("ras_n", Pins("L20"),  IOStandard("SSTL135")),
        Subsignal("cas_n", Pins("N22"),  IOStandard("SSTL135")),
        Subsignal("we_n",  Pins("L19"),  IOStandard("SSTL135")),
        Subsignal("dm", Pins("H22 G13"), IOStandard("SSTL135")),
        Subsignal("dq", Pins(
            "J22 M21 L21 J20 H20 G20 J21 H19", # dq0 -> dq7 (included)
            "H13 G18 J15 H17 G15 G17 G16 H15"), # dq8 -> dq15
            IOStandard("SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_50")),
        Subsignal("dqs_p",
            Pins("K21 J14"),
            IOStandard("DIFF_SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_50")),
        Subsignal("dqs_n",
            Pins("K22 H14"),
            IOStandard("DIFF_SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_50")),
        Subsignal("clk_p", Pins("K17"), IOStandard("DIFF_SSTL135")),
        Subsignal("clk_n", Pins("J17"), IOStandard("DIFF_SSTL135")),
        Subsignal("cke",   Pins("M22"), IOStandard("SSTL135")),
        Subsignal("odt",   Pins("M17"), IOStandard("SSTL135")),
        Subsignal("cs_n",  Pins("N19"), IOStandard("SSTL135")),
        Subsignal("reset_n", Pins("J19"), IOStandard("SSTL135")),
        Misc("SLEW=FAST"),
    ),
]


class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self, variant="pt_v2", toolchain="vivado"):
        device = {
            "pt_v2":  "xc7a100t-fgg484-2",
        }[variant]

        Xilinx7SeriesPlatform.__init__(self, device, _io, toolchain=toolchain)
        self.add_platform_command("set_property INTERNAL_VREF 0.675 [get_iobanks 15]")

        self.toolchain.bitstream_commands = [
            "set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]",
            "set_property BITSTREAM.CONFIG.CONFIGRATE 66 [current_design]",
            "set_property CONFIG_VOLTAGE 3.3 [current_design]",
            "set_property CFGBVS VCCO [current_design]",
            "set_property BITSTREAM.CONFIG.SPI_32BIT_ADDR NO [current_design]",
            "set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]",
            "set_property BITSTREAM.CONFIG.SPI_FALL_EDGE YES [current_design]",
        ]
        self.toolchain.additional_commands = \
            ["write_cfgmem -force -format bin -interface spix4 -size 4 "
             "-loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"]

    def create_programmer(self):
        return OpenOCD("openocd_xc7_ft2232.cfg", "bscan_spi_xc7a100t.bit")

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100", loose=True), 1e9/100e6)