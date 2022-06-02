#
# This file is part of LiteX-Boards.
# FPGA Board Info : http://www.e-elements.com/product/show/id/11.shtml
#
# Copyright (c) 2020 Shinken Sanada <sanadashinken@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk100",    0, Pins("P17"), IOStandard("LVCMOS33")),
    ("cpu_reset", 0, Pins("P15"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led",  0, Pins("K3"), IOStandard("LVCMOS33")),
    ("user_led",  1, Pins("M1"), IOStandard("LVCMOS33")),
    ("user_led",  2, Pins("L1"), IOStandard("LVCMOS33")),
    ("user_led",  3, Pins("K6"), IOStandard("LVCMOS33")),
    ("user_led",  4, Pins("J5"), IOStandard("LVCMOS33")),
    ("user_led",  5, Pins("H5"), IOStandard("LVCMOS33")),
    ("user_led",  6, Pins("H6"), IOStandard("LVCMOS33")),
    ("user_led",  7, Pins("K1"), IOStandard("LVCMOS33")),
    ("user_led",  8, Pins("K2"), IOStandard("LVCMOS33")),
    ("user_led",  9, Pins("J2"), IOStandard("LVCMOS33")),
    ("user_led", 10, Pins("J3"), IOStandard("LVCMOS33")),
    ("user_led", 11, Pins("H4"), IOStandard("LVCMOS33")),
    ("user_led", 12, Pins("J4"), IOStandard("LVCMOS33")),
    ("user_led", 13, Pins("G3"), IOStandard("LVCMOS33")),
    ("user_led", 14, Pins("G4"), IOStandard("LVCMOS33")),
    ("user_led", 15, Pins("F6"), IOStandard("LVCMOS33")),

    # Switches
    ("user_sw",  0, Pins("R1"), IOStandard("LVCMOS33")),
    ("user_sw",  1, Pins("N4"), IOStandard("LVCMOS33")),
    ("user_sw",  2, Pins("M4"), IOStandard("LVCMOS33")),
    ("user_sw",  3, Pins("R2"), IOStandard("LVCMOS33")),
    ("user_sw",  4, Pins("P2"), IOStandard("LVCMOS33")),
    ("user_sw",  5, Pins("P3"), IOStandard("LVCMOS33")),
    ("user_sw",  6, Pins("P4"), IOStandard("LVCMOS33")),
    ("user_sw",  7, Pins("P5"), IOStandard("LVCMOS33")),
    ("user_sw",  8, Pins("T5"), IOStandard("LVCMOS33")),
    ("user_sw",  9, Pins("T3"), IOStandard("LVCMOS33")),
    ("user_sw", 10, Pins("R3"), IOStandard("LVCMOS33")),
    ("user_sw", 11, Pins("V4"), IOStandard("LVCMOS33")),
    ("user_sw", 12, Pins("V5"), IOStandard("LVCMOS33")),
    ("user_sw", 13, Pins("V2"), IOStandard("LVCMOS33")),
    ("user_sw", 14, Pins("U2"), IOStandard("LVCMOS33")),
    ("user_sw", 15, Pins("U3"), IOStandard("LVCMOS33")),

    # Buttons
    ("user_btn", 0, Pins("R11"), IOStandard("LVCMOS33")),
    ("user_btn", 1, Pins("R17"), IOStandard("LVCMOS33")),
    ("user_btn", 2, Pins("R15"), IOStandard("LVCMOS33")),
    ("user_btn", 3, Pins("V1"),  IOStandard("LVCMOS33")),
    ("user_btn", 4, Pins("U4"),  IOStandard("LVCMOS33")),

	# Seven Segment
    ("seven_seg_ctl", 0, Pins("G2"), IOStandard("LVCMOS33")),
    ("seven_seg_ctl", 1, Pins("C2"), IOStandard("LVCMOS33")),
    ("seven_seg_ctl", 2, Pins("C1"), IOStandard("LVCMOS33")),
    ("seven_seg_ctl", 3, Pins("H1"), IOStandard("LVCMOS33")),
    ("seven_seg_ctl", 4, Pins("G1"), IOStandard("LVCMOS33")),
    ("seven_seg_ctl", 5, Pins("F1"), IOStandard("LVCMOS33")),
    ("seven_seg_ctl", 6, Pins("E1"), IOStandard("LVCMOS33")),
    ("seven_seg_ctl", 7, Pins("G6"), IOStandard("LVCMOS33")),
    ("seven_seg", 0, Pins("B4 A4 A3 B1 A1 B3 B2 D5"), IOStandard("LVCMOS33")),
    ("seven_seg", 1, Pins("D4 E3 D3 F4 F3 E2 D2 H2"), IOStandard("LVCMOS33")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("T4")),
        Subsignal("rx", Pins("N5")),
        IOStandard("LVCMOS33")
    ),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("L13")),
        Subsignal("clk",  Pins("E9")),
        Subsignal("mosi", Pins("K17")),
        Subsignal("miso", Pins("K18")),
        Subsignal("wp",   Pins("L14")),
        Subsignal("hold", Pins("M14")),
        IOStandard("LVCMOS33"),
    ),
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("L13")),
        Subsignal("clk",  Pins("E9")),
        Subsignal("dq",   Pins("K17 K18 L14 M14")),
        IOStandard("LVCMOS33")
    ),

    # VGA
     ("vga", 0,
        Subsignal("r",     Pins("F5 C6 C5 B7")),
        Subsignal("g",     Pins("B6 A6 A5 D8")),
        Subsignal("b",     Pins("C7 E6 E5 E7")),
        Subsignal("hsync", Pins("D7")),
        Subsignal("vsync", Pins("C4")),
        IOStandard("LVCMOS33")
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("j5", "B16 B17 A15 A16 A13 A14 A18 B18",
           "F13 F14 B13 B14 C14 D14 A11 B11",
           "E15 E16 D15 C15 H16 G16 F15 F16",
           "H14 G14 E17 D17 K13 J13 H17 G17",),
]

# PMODS --------------------------------------------------------------------------------------------
'''
    # SPI
    ("spi", 0,
        Subsignal("clk",  Pins("F1")),
        Subsignal("cs_n", Pins("C1")),
        Subsignal("mosi", Pins("H1")),
        Subsignal("miso", Pins("G1")),
        IOStandard("LVCMOS33"),
    ),

    # I2C
    ("i2c", 0,
        Subsignal("scl", Pins("L18")),
        Subsignal("sda", Pins("M18")),
        Subsignal("scl_pup", Pins("A14")),
        Subsignal("sda_pup", Pins("A13")),
        IOStandard("LVCMOS33"),
    ),
'''

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self, toolchain="vivado"):
        XilinxPlatform.__init__(self, "xc7a35ticsg324-1L", _io, _connectors, toolchain=toolchain)
        self.toolchain.bitstream_commands = \
        ["set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]"]
        self.toolchain.additional_commands = \
        ["write_cfgmem -force -format bin -interface spix4 -size 16"
         " -loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"]
        self.add_platform_command("set_property SEVERITY {{Warning}} [get_drc_checks UCIO-1]")

    def create_programmer(self):
        return OpenOCD("openocd_xc7_ft2232.cfg", "bscan_spi_xc7a35t.bit")

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100", loose=True), 1e9/100e6)

