#
# This file is part of LiteX-Boards.
# FPGA Board Info : https://shop.trenz-electronic.de/en/TE0725-03-35-2C-FPGA-Module-with-Xilinx-Artix-7-XC7A35T-2CSG324C-2-x-50-Pin-with-2.54-mm-pitch
#
# Copyright (c) 2021 Shinken Sanada <sanadashinken@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk100",    0, Pins("P17"), IOStandard("LVCMOS33")),
    ("cpu_reset", 0, Pins("T8"),  IOStandard("LVCMOS33")),

    # Leds
    ("user_led",  0, Pins("M16"), IOStandard("LVCMOS33")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("L18")),
        Subsignal("rx", Pins("M18")),
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

    # HyperRAM
    ("hyperram", 0,
        Subsignal("dq", Pins("E17 B17 F18 F16 G17 D18 B18 A16"), IOStandard("SSTL18_II")),
        Subsignal("rwds", Pins("E18"), IOStandard("SSTL18_II")),
        Subsignal("cs_n", Pins("D17"), IOStandard("SSTL18_II")),
        Subsignal("rst_n", Pins("J17"), IOStandard("SSTL18_II")),
        Subsignal("clk_p", Pins("A13"), IOStandard("DIFF_SSTL18_II")),
        Subsignal("clk_n", Pins("A14"), IOStandard("DIFF_SSTL18_II")),
        Misc("SLEW=FAST"),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("j1", "C6 C5 B7 B6 A6 A5 D8 C7",
           "E6 E5 E7 D7 C4 B4 A4 A3",
           "B1 A1 B3 B2 D5 D4 E3 D3",
           "F4 F3 E2 D2 H2 G2 C2 C1",
           "H1 G1 F1 E1 G6 F6 J3 J2",
           "K2 K1"),
    ("j2", "L1 M1 N2 N1 M3 M2 U1 V1",
           "U4 U3 U2 V2 V5 V4 R3 T3",
           "T5 T4 N5 P5 P4 P3 P2 R2",
           "M4 N4 R1 T1 M6 N6 R6 R5",
           "V7 V6 U9 V9 U7 U6 R7 T6",
           "R8"),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self, toolchain="vivado"):
        XilinxPlatform.__init__(self, "xc7a35tcsg324-2", _io, _connectors, toolchain=toolchain)
        self.toolchain.bitstream_commands = \
        ["set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]"]
        self.toolchain.additional_commands = \
        ["write_cfgmem -force -format bin -interface spix4 -size 16"
         " -loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"]
        self.add_platform_command("set_property CFGBVS VCCO [current_design]")
        self.add_platform_command("set_property CONFIG_VOLTAGE 3.3 [current_design]")

    def create_programmer(self):
        return OpenOCD("openocd_xc7_ft2232.cfg", "bscan_spi_xc7a35t.bit")

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100", loose=True), 1e9/100e6)

#         "set_property SEVERITY {{Warning}} [get_drc_checks UCIO-1]"]

