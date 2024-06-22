#
# This file is part of LiteX-Boards.
#
#
# Copyright (c) 2015 Yann Sionneau <yann.sionneau@gmail.com>
# Copyright (c) 2015-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2024 Lone Dynamics Corporation <info@lonedynamics.com>
#
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform
from litex.build.openfpgaloader import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io_vx = [

    # Clock
    ("clk48", 0,  Pins("F5"),  IOStandard("LVCMOS33")),
    ("clk50", 0,  Pins("D4"),  IOStandard("LVCMOS33")),

    # SDRAM
    ("sdram_clock", 0, Pins("C8"), IOStandard("LVTTL")),
    ("sdram", 0,
        Subsignal("a", Pins(
            "D15 D16 E15 E16 C9 D9 D8 C7",
            "E6 D6 C16 D5 E5")),
        Subsignal("ba",    Pins("B9 A8")),
        Subsignal("cs_n",  Pins("A9")),
        Subsignal("cke",   Pins("C4")),
        Subsignal("ras_n", Pins("B10")),
        Subsignal("cas_n", Pins("A10")),
        Subsignal("we_n",  Pins("B11")),
        Subsignal("dq", Pins(
            "B16 A15 B15 A14 B14 A13 C13 A12",
            "B6 C6 A5 B5 A4 B4 C3 A3")),
        Subsignal("dm", Pins("B12 A7")),
        IOStandard("LVTTL")
    ),

    # Differential Data Multiple Interface
    ("ddmi", 0,
        Subsignal("clk_p",    Pins("C1"), IOStandard("TMDS_33")),
        Subsignal("clk_n",    Pins("B1"), IOStandard("TMDS_33")),
        Subsignal("data0_p",  Pins("E2"), IOStandard("TMDS_33")),
        Subsignal("data0_n",  Pins("D1"), IOStandard("TMDS_33")),
        Subsignal("data1_p",  Pins("F2"), IOStandard("TMDS_33")),
        Subsignal("data1_n",  Pins("E1"), IOStandard("TMDS_33")),
        Subsignal("data2_p",  Pins("G2"), IOStandard("TMDS_33")),
        Subsignal("data2_n",  Pins("G1"), IOStandard("TMDS_33"))
    ),

    # USB-C
    ("usb", 0,
        Subsignal("d_p", Pins("B2")),
        Subsignal("d_n", Pins("A2")),
        Subsignal("pullup", Pins("C2")),
        IOStandard("LVCMOS33")
    ),

    # DUAL USB HOST
    ("usb_host", 0,
        Subsignal("dp", Pins("H2 K1")),
        Subsignal("dm", Pins("H1 J1")),
        IOStandard("LVCMOS33")
    ),

    # ETHERNET
    ("eth", 0,
        Subsignal("rx_data", Pins("F3 F4"), Misc("PULLUP")),
        Subsignal("tx_data", Pins("D3 E3")),
        Subsignal("tx_en", Pins("G4")),
        Subsignal("crs_dv", Pins("H3"), Misc("PULLUP")),
        Subsignal("rst_n", Pins("H4")),
        IOStandard("LVCMOS33")
    ),

    # LVDS
    ("lvds", 0,
        Subsignal("tx_p", Pins("R2")),
        Subsignal("tx_n", Pins("R1")),
        Subsignal("rx_p", Pins("T4")),
        Subsignal("rx_n", Pins("T3")),
        IOStandard("LVDS_25")
    ),

    # MMOD
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("L12")),
        #Subsignal("clk",  Pins("")), # Accessed through STARTUPE2
        Subsignal("dq",   Pins("J13 J14 K15 K16")),
        IOStandard("LVCMOS33")
    ),

    # DEBUG UART
    ("serial", 0,
        Subsignal("tx", Pins("L2")),
        Subsignal("rx", Pins("L3")),
        IOStandard("LVCMOS33")
    ),
]

_io_v0 = [

    # SD card w/ SD-mode interface
    ("sdcard", 0,
        Subsignal("cd", Pins("K3")),
        Subsignal("clk", Pins("R6")),
        Subsignal("cmd", Pins("T8")),
        Subsignal("data", Pins("T7 P8 T9 T5")),
        IOStandard("LVCMOS33")
    ),

    # SD card w/ SPI interface
    ("spisdcard", 0,
        Subsignal("clk",  Pins("R6")),
        Subsignal("mosi", Pins("T8")),
        Subsignal("cs_n", Pins("T5")),
        Subsignal("miso", Pins("T7")),
        IOStandard("LVCMOS33"),
    ),

]

# Connectors ---------------------------------------------------------------------------------------

_connectors_vx = [

]

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk48"
    default_clk_period = 1e9/48e6

    def __init__(self, revision="v0", variant="a7-35", toolchain="vivado"):

        assert revision in ["v0"]
        self.revision = revision

        io = _io_vx
        connectors = _connectors_vx

        if revision == "v0": io += _io_v0

        device = {
            "a7-35":  "xc7a35tftg256-1"
        }[variant]
        Xilinx7SeriesPlatform.__init__(self, device, io, connectors, toolchain=toolchain)
        self.toolchain.bitstream_commands = \
            ["set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]"]
        self.toolchain.additional_commands = \
            ["write_cfgmem -force -format bin -interface spix4 -size 16 "
             "-loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"]
        self.add_platform_command("set_property INTERNAL_VREF 0.675 [get_iobanks 34]")

    def create_programmer(self):
        bscan_spi = "bscan_spi_xc7a100t.bit" if "xc7a100t" in self.device else "bscan_spi_xc7a35t.bit"
        return OpenOCD("openocd_xc7_ft2232.cfg", bscan_spi)

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk48", loose=True), 1e9/48e6)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)

