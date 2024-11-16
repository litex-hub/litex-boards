#
# This file is part of LiteX-Boards.
# FPGA Board Info : https://shop.trenz-electronic.de/de/TE0890-01-P1C-5-A-S7-Mini-Fully-Open-Source-Modul-mit-AMD-Spartan-7-7S25-64-Mbit-HyperRAM?c=525
#
# Copyright (c) 2024 Philip Kirkpatrick <s.philip.kirkpatrick@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform
from litex.build.openfpgaloader import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk100",    0, Pins("L5"), IOStandard("LVCMOS33")),
    ("cpu_reset", 0, Pins("B10"),  IOStandard("LVCMOS33")),

    # Leds
    ("user_led",  0, Pins("D14"), IOStandard("LVCMOS33")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("A5")),
        Subsignal("rx", Pins("A12")),
        IOStandard("LVCMOS33")
    ),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("C11")),
        Subsignal("clk",  Pins("A8")),
        Subsignal("mosi", Pins("B11")),
        Subsignal("miso", Pins("B12")),
        IOStandard("LVCMOS33"),
    ),

    # HyperRAM
    ("hyperram", 0,
        Subsignal("dq", Pins("P11 P12 N4 P10 P5 N10 N11 P13"), IOStandard("LVCMOS33")),
        Subsignal("rwds", Pins("P4"), IOStandard("LVCMOS33")),
        Subsignal("cs_n", Pins("P2"), IOStandard("LVCMOS33")),
        Subsignal("rst_n", Pins("P3"), IOStandard("LVCMOS33")),
        Subsignal("clk", Pins("N1"), IOStandard("LVCMOS33")),
        Misc("SLEW=FAST"),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("j1", " A2  C4  D4  A3  B3  C5  E4  C3",
           " B2  C1  D2  F1  B1  D1  E2  G1",
           " F3  F4  H3  J3  F2  G4  H4  J4",
           " K3  L2  M2  M4  K4  L3  M3  M5"),
    ("j2", "J12 M14 K12 M12 J11 N14 K11 M11",
           "H13 J13 L12 L14 H14 J14 L13 M13",
           "F14 E12 F11 H12 G14 F12 G11 H11",
           "E11 C10 D12 E13 C12 D10 D13 F13"),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self, toolchain="vivado"):
        Xilinx7SeriesPlatform.__init__(self, "xc7s25ftgb196-1", _io, _connectors, toolchain=toolchain)
        self.toolchain.bitstream_commands = \
        ["set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 1 [current_design]"]
        self.toolchain.additional_commands = \
        ["write_cfgmem -force -format bin -interface spix1 -size 8"
         " -loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"]
        self.add_platform_command("set_property CFGBVS VCCO [current_design]")
        self.add_platform_command("set_property CONFIG_VOLTAGE 3.3 [current_design]")
        # For some reason this board places the clock on a non clock dedicated pin.
        # Tell Vivado to ignore this and just deal with it.
        self.add_platform_command("set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets clk100_IBUF]")

    def create_programmer(self):
        # OpenFPGALoader doesn't have a spiOverJtag bit for the ftgb196 package, but does have one
        # for the csga225.  Based on a hint from bscan_spi_bitstreams, it seems the package doesn't
        # matter, so lie here to make it work.
        # (https://github.com/quartiq/bscan_spi_bitstreams/blob/master/xilinx_bscan_spi.py#L358) 
        return OpenFPGALoader(cable="ft2232", fpga_part=f"xc7s25csga225")

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100", loose=True), 1e9/100e6)
