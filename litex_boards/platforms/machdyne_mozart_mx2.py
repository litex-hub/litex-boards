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
    ("clk48", 0, Pins("F5"), IOStandard("LVCMOS33")),
    ("clk50", 0, Pins("D4"), IOStandard("LVCMOS33")),

    # DDR3L
    ("ddram", 0,
        Subsignal("a", Pins(
            "F12 D15 J15 E16 G11 F15 H13 G15",
            "H12 H16 H11 H14 E12 G16 J16"),
            IOStandard("SSTL135")),
        Subsignal("ba",      Pins("E15 D11 F13"), IOStandard("SSTL135")),
        Subsignal("ras_n",   Pins("D14"),     IOStandard("SSTL135")),
        Subsignal("cas_n",   Pins("E13"),     IOStandard("SSTL135")),
        Subsignal("we_n",    Pins("G12"),     IOStandard("SSTL135")),
        Subsignal("dm",      Pins("A13 D9"),  IOStandard("SSTL135")),
        Subsignal("dq",      Pins(
            "A14 C12 B14 D13 B16 C11 C16 C14",
            "A9 B10 C8 B12 A8 A12 C9 B11"),
            IOStandard("SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_60")),
        Subsignal("dqs_p",   Pins("B15 B9"),  IOStandard("DIFF_SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_60")),
        Subsignal("dqs_n",   Pins("A15 A10"), IOStandard("DIFF_SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_60")),
        Subsignal("clk_p",   Pins("G14"),     IOStandard("DIFF_SSTL135")),
        Subsignal("clk_n",   Pins("F14"),     IOStandard("DIFF_SSTL135")),
        Subsignal("cke",     Pins("E11"),     IOStandard("SSTL135")),
        Subsignal("odt",     Pins("D16"),     IOStandard("SSTL135")),
        Subsignal("reset_n", Pins("M16"),     IOStandard("LVCMOS33")),
    ),

    # Differential Data Multiple Interface
    ("ddmi", 0,
        Subsignal("clk_p",   Pins("C1"), IOStandard("TMDS_33")),
        Subsignal("clk_n",   Pins("B1"), IOStandard("TMDS_33")),
        Subsignal("data0_p", Pins("E2"), IOStandard("TMDS_33")),
        Subsignal("data0_n", Pins("D1"), IOStandard("TMDS_33")),
        Subsignal("data1_p", Pins("F2"), IOStandard("TMDS_33")),
        Subsignal("data1_n", Pins("E1"), IOStandard("TMDS_33")),
        Subsignal("data2_p", Pins("G2"), IOStandard("TMDS_33")),
        Subsignal("data2_n", Pins("G1"), IOStandard("TMDS_33"))
    ),

    # USB-C
    ("usb", 0,
        Subsignal("d_p",    Pins("B2")),
        Subsignal("d_n",    Pins("A2")),
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
        Subsignal("tx_en",   Pins("G4")),
        Subsignal("crs_dv",  Pins("H3"),    Misc("PULLUP")),
        Subsignal("rst_n",   Pins("H4")),
        IOStandard("LVCMOS33")
    ),

    # LVDS
    ("ds", 0,
        Subsignal("ds0", Pins("M2")),
        Subsignal("ds1", Pins("R2")),
        Subsignal("ds2", Pins("T4")),
        IOStandard("LVDS_25")
    ),

    # DEBUG UART
    ("serial", 0,
        Subsignal("tx", Pins("L2")),
        Subsignal("rx", Pins("L3")),
        IOStandard("LVCMOS33")
    ),

    # MMOD
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("L12")),
        #Subsignal("clk",  Pins("")), # Accessed through STARTUPE2
        Subsignal("dq",   Pins("J13 J14 K15 K16")),
        IOStandard("LVCMOS33")
    ),

    # SD card w/ SD-mode interface
    ("sdcard", 0,
        Subsignal("cd",   Pins("K3")),
        Subsignal("clk",  Pins("R6")),
        Subsignal("cmd",  Pins("T8")),
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

_io_v0 = [
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

        if revision == "v0":
            io += _io_v0

        device = {
            "a7-35":  "xc7a35tftg256-1"
        }[variant]
        Xilinx7SeriesPlatform.__init__(self, device, io, connectors, toolchain=toolchain)
        self.toolchain.bitstream_commands = [
            "set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 1 [current_design]",
            "set_property BITSTREAM.CONFIG.CONFIGRATE 33 [current_design]"
        ]
        self.toolchain.additional_commands = \
            ["write_cfgmem -force -format bin -interface spix1 -size 16 "
             "-loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"]
        self.add_platform_command("set_property INTERNAL_VREF 0.675 [get_iobanks 34]")

    def create_programmer(self):
        bscan_spi = "bscan_spi_xc7a100t.bit" if "xc7a100t" in self.device else "bscan_spi_xc7a35t.bit"
        return OpenOCD("openocd_xc7_ft2232.cfg", bscan_spi)

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_platform_command("set_property INTERNAL_VREF 0.675 [get_iobanks 15]")
        self.add_period_constraint(self.lookup_request("clk48", loose=True), 1e9/48e6)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)

