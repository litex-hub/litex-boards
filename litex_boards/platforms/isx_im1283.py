#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Icenowy Zheng <icenowy@aosc.io>
# Copyright (c) 2015 Yann Sionneau <yann.sionneau@gmail.com>
# Copyright (c) 2015-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform, VivadoProgrammer
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk200", 0,
        Subsignal("p", Pins("E5"), IOStandard("LVDS_25")),
        Subsignal("n", Pins("D5"), IOStandard("LVDS_25")),
    ),

    # Leds
    ("user_led", 0, Pins("A22"),  IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("C22"),  IOStandard("LVCMOS33")),

    # Switches
    ("sw", 0, Pins("C23"), IOStandard("LVCMOS33")),
    ("sw", 1, Pins("B25"), IOStandard("LVCMOS33")),
    ("sw", 2, Pins("A25"), IOStandard("LVCMOS33")),
    ("sw", 3, Pins("A23"), IOStandard("LVCMOS33")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("G24")),
        Subsignal("rx", Pins("F24")),
        IOStandard("LVCMOS33")
    ),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("P18")),
        Subsignal("clk",  Pins("H13")),
        Subsignal("mosi", Pins("R14")),
        Subsignal("miso", Pins("R15")),
        Subsignal("wp",   Pins("P14")),
        Subsignal("hold", Pins("N14")),
        IOStandard("LVCMOS33"),
    ),
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("P18")),
        Subsignal("clk",  Pins("H13")),
        Subsignal("dq",   Pins("R14 R15 P14 N14")),
        IOStandard("LVCMOS33")
    ),

    # DDR3 SDRAM
    ("ddram", 0,
        Subsignal("a", Pins(
            "D4 D3 C2 E3 B2 A2 A5 A4 B5 C3",
            "F2 A3 D1 C4 B4"),
            IOStandard("SSTL15")),
        Subsignal("ba",    Pins("G4 F4 F3"), IOStandard("SSTL15")),
        Subsignal("ras_n", Pins("G2"),  IOStandard("SSTL15")),
        Subsignal("cas_n", Pins("G1"),  IOStandard("SSTL15")),
        Subsignal("we_n",  Pins("E2"),  IOStandard("SSTL15")),
        Subsignal("cs_n",  Pins("E1"),  IOStandard("SSTL15")),
        Subsignal("dm", Pins(
            "U2 T5",
            "L7 K1"
            ), IOStandard("SSTL15")),
        Subsignal("dq", Pins(
            "T2 T4 R2 P4 P3 N4 R3 T3",
            "P8 R6 T8 R5 R8 P6 T7 R7",
            "L5 M7 K3 N6 J3 N7 K5 M6",
            "L3 L2 K2 H2 M2 H1 N3 J1"
            ),
            IOStandard("SSTL15"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("dqs_p", Pins(
            "R1 U6",
            "M4 N1"
            ),
            IOStandard("DIFF_SSTL15"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("dqs_n", Pins(
            "P1 U5",
            "L4 M1"
            ),
            IOStandard("DIFF_SSTL15"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("clk_p", Pins("C1"), IOStandard("DIFF_SSTL15")),
        Subsignal("clk_n", Pins("B1"), IOStandard("DIFF_SSTL15")),
        Subsignal("cke",   Pins("J4"), IOStandard("SSTL15")),
        Subsignal("odt",   Pins("H4"), IOStandard("SSTL15")),
        Subsignal("reset_n", Pins("N2"), IOStandard("SSTL15")),
        Misc("SLEW=FAST"),
    ),

    ## sdcard connector
    ("spisdcard", 0,
        Subsignal("clk",  Pins("P24")),
        Subsignal("mosi", Pins("R25"), Misc("PULLUP True")),
        Subsignal("cs_n", Pins("P25"), Misc("PULLUP True")),
        Subsignal("miso", Pins("N23"), Misc("PULLUP True")),
        Misc("SLEW=FAST"),
        IOStandard("LVCMOS33"),
    ),
    ("sdcard", 0,
        Subsignal("data", Pins("N23 M25 N26 P25"), Misc("PULLUP True")),
        Subsignal("cmd",  Pins("R25"), Misc("PULLUP True")),
        Subsignal("clk",  Pins("P24")),
        Subsignal("cd",   Pins("M26"), Misc("PULLUP True")),
        Misc("SLEW=FAST"),
        IOStandard("LVCMOS33"),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = []

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk200"
    default_clk_period = 1e9/200e6

    def __init__(self, toolchain="vivado"):
        Xilinx7SeriesPlatform.__init__(self, "xc7a100tfgg676-2", _io, _connectors, toolchain=toolchain)
        self.toolchain.bitstream_commands = \
            ["set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 1 [current_design]"]
        self.toolchain.additional_commands = \
            ["write_cfgmem -force -format bin -interface spix1 -size 16 "
             "-loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"]

    def create_programmer(self, name='vivado'):
        if name == 'vivado':
            return VivadoProgrammer()
        elif name == 'openocd':
            bscan_spi = "bscan_spi_xc7a100t.bit"
            return OpenOCD("openocd_xc7_ft2232.cfg", bscan_spi)

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk200:p", loose=True), 1e9/200e6)
