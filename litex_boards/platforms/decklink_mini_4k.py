#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst.
    ("clk100", 0, Pins("P16"), IOStandard("LVCMOS25")),
    ("clk24",  0, Pins("M21"), IOStandard("LVCMOS25")),

    # Debug
    ("debug", 0, Pins("R7"), IOStandard("LVCMOS25")),
    ("debug", 1, Pins("R6"), IOStandard("LVCMOS25")),
    ("debug", 2, Pins("T7"), IOStandard("LVCMOS25")),
    ("debug", 3, Pins("T8"), IOStandard("LVCMOS25")),

    # Fan
    ("fan", 0, Pins("R18"), IOStandard("LVCMOS25")),

    # Flash
    ("flash_cs_n", 0, Pins("P18"), IOStandard("LVCMOS25")),
    ("flash", 0,
        Subsignal("mosi", Pins("R14")),
        Subsignal("miso", Pins("R15")),
        Subsignal("vpp",  Pins("P14")),
        Subsignal("hold", Pins("N14")),
        IOStandard("LVCMOS25")
    ),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("R7")), # debug0
        Subsignal("rx", Pins("R6")), # debug1
        IOStandard("LVCMOS25")
    ),

    # PCIe
    ("pcie_x4", 0,
        Subsignal("rst_n", Pins("M19"), IOStandard("LVCMOS25"), Misc("PULLUP=TRUE")),
        Subsignal("clk_p", Pins("F11")),
        Subsignal("clk_n", Pins("E11")),
        Subsignal("rx_p",  Pins("B11 D14 B13 D12")),
        Subsignal("rx_n",  Pins("A11 C14 A13 C12")),
        Subsignal("tx_p",  Pins("B7   D8  B9 D10")),
        Subsignal("tx_n",  Pins("A7   C8  A9 C10"))
    ),

    # DDR3 SDRAM
    ("ddram", 0,
        Subsignal("a", Pins(
            "K2 M5 M2 K1 N6 J1 P1 H2",
            "R1 M1 M6 N3 M7 H1"),
            IOStandard("SSTL15")),
        Subsignal("ba",    Pins("K3 N2 L3"), IOStandard("SSTL15")),
        Subsignal("ras_n", Pins("L7"), IOStandard("SSTL15")),
        Subsignal("cas_n", Pins("L5"), IOStandard("SSTL15")),
        Subsignal("we_n",  Pins("L2"), IOStandard("SSTL15")),
        Subsignal("cs_n",  Pins("K5"), IOStandard("SSTL15")),
        Subsignal("dm", Pins("G8 J6 D5 A3"), IOStandard("SSTL15")),
        Subsignal("dq", Pins(
            "G6 H8 F7 F8 D6 H9 E6 H6",
            "J5 G4 L8 F4 K6 G5 K7 K8",
            "A4 D4 B4 E5 C4 F3 C3 D3",
            "G1 D1 G2 A2 E1 E2 F2 C2"),
            IOStandard("SSTL15"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("dqs_p", Pins("H7 J4 B5 C1"),
            IOStandard("DIFF_SSTL15"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("dqs_n", Pins("G7 H4 A5 B1"),
            IOStandard("DIFF_SSTL15"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("clk_p", Pins("P4"), IOStandard("DIFF_SSTL15")),
        Subsignal("clk_n", Pins("N4"), IOStandard("DIFF_SSTL15")),
        Subsignal("cke",   Pins("N7"), IOStandard("SSTL15")),
        Subsignal("odt",   Pins("J3"), IOStandard("SSTL15")),
        Subsignal("reset_n", Pins("N1"), IOStandard("SSTL15")),
        Misc("SLEW=FAST"),
    ),

    # SDI
    ("sdi_refclk_sel", 0, Pins("AB26"), IOStandard("LVCMOS25")),
    ("sdi_refclk", 0,
        Subsignal("p", Pins("AA13")),
        Subsignal("n", Pins("AB13")),
    ),
    ("sdi_refclk", 1,
        Subsignal("p", Pins("AA11")),
        Subsignal("n", Pins("AB11")),
    ),
    ("sdi_data", 0,
        Subsignal("txp", Pins("AC10")),
        Subsignal("txn", Pins("AD10")),
        Subsignal("rxp", Pins("AC12")),
        Subsignal("rxn", Pins("AD12")),
    ),

    # HDMI (through 75DP159)
    ("hdmi_out", 0,
        Subsignal("clk_p",   Pins("U14"), IOStandard("LVDS_25")),
        Subsignal("clk_n",   Pins("V14"), IOStandard("LVDS_25")),
        Subsignal("data0_p", Pins("AE7")),
        Subsignal("data0_n", Pins("AF7")),
        Subsignal("data1_p", Pins("AC8")),
        Subsignal("data1_n", Pins("AD8")),
        Subsignal("data2_p", Pins("AE9")),
        Subsignal("data2_n", Pins("AF9")),
        # FIXME: Find a way to avoid RX pads.
        Subsignal("rx0_p", Pins("AE11")),
        Subsignal("rx0_n", Pins("AF11")),
        Subsignal("rx1_p", Pins("AC14")),
        Subsignal("rx1_n", Pins("AD14")),
        Subsignal("rx2_p", Pins("AE13")),
        Subsignal("rx2_n", Pins("AF13")),

    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self, toolchain="vivado"):
        Xilinx7SeriesPlatform.__init__(self, "xc7a100t-fgg676-3", _io, toolchain=toolchain)
        self.toolchain.bitstream_commands = \
            ["set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]"]
        self.toolchain.additional_commands = \
            ["write_cfgmem -force -format bin -interface spix4 -size 16 "
             "-loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"]
        self.add_platform_command("set_property INTERNAL_VREF 0.750 [get_iobanks 34]")
        self.add_platform_command("set_property INTERNAL_VREF 0.750 [get_iobanks 35]")

    def create_programmer(self):
        return OpenOCD("openocd_xc7_ft232.cfg", "bscan_spi_xc7a100t.bit")

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100", loose=True), 1e9/100e6)
        self.add_period_constraint(self.lookup_request("clk24",  loose=True), 1e9/24e6)
