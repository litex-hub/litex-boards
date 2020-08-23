#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2018-2019 Rohit Singh <rohit@rohitksingh.in>
# Copyright (c) 2019 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # clk / rst
    ("clk100", 0, Pins("W19"), IOStandard("LVCMOS33")),

    # leds (only a single rgb led, aliased here also)
    ("user_led", 0, Pins("AB21"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("AB22"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("U20"),  IOStandard("LVCMOS33")),

    # rgb led, active-low
    ("rgb_led", 0,
        Subsignal("r", Pins("AB21")),
        Subsignal("g", Pins("AB22")),
        Subsignal("b", Pins("U20")),
        IOStandard("LVCMOS33"),
    ),

    # flash
    ("flash", 0,
        Subsignal("cs_n",  Pins("T19")),
        Subsignal("mosi",  Pins("P22")),
        Subsignal("miso",  Pins("R22")),
        Subsignal("hold",  Pins("R21")),
        Subsignal("rst_n", Pins("R19")),
        IOStandard("LVCMOS33")
    ),

    ("flash4x", 0,  # clock needs to be accessed through STARTUPE2
        Subsignal("cs_n", Pins("T19")),
        Subsignal("dq",   Pins("P22", "R22", "P21", "R21")),
        IOStandard("LVCMOS33")
    ),

    # tpm
    ("tpm", 0,
        Subsignal("clk",   Pins("W20")),
        Subsignal("rst_n", Pins("V19")),
        Subsignal("cs_n",  Pins("Y18")),
        Subsignal("mosi",  Pins("Y19")),
        Subsignal("miso",  Pins("V18")),
        IOStandard("LVCMOS33"),
    ),

    # pcie
    ("pcie_x1", 0,
        Subsignal("rst_n", Pins("AB20"), IOStandard("LVCMOS33"), Misc("PULLUP=TRUE")),
        Subsignal("clk_p", Pins("F6")),
        Subsignal("clk_n", Pins("E6")),
        Subsignal("rx_p",  Pins("B8")),
        Subsignal("rx_n",  Pins("A8")),
        Subsignal("tx_p",  Pins("B4")),
        Subsignal("tx_n",  Pins("A4"))
    ),

    ("pcie_x4", 0,
        Subsignal("rst_n", Pins("AB20"), IOStandard("LVCMOS33"), Misc("PULLUP=TRUE")),
        Subsignal("clk_p", Pins("F6")),
        Subsignal("clk_n", Pins("E6")),
        Subsignal("rx_p",  Pins("B8 D11 B10 D9")),
        Subsignal("rx_n",  Pins("A8 C11 A10 C9")),
        Subsignal("tx_p",  Pins("B4 D5 B6 D7")),
        Subsignal("tx_n",  Pins("A4 C5 A6 C7"))
    ),

    # dram
    ("ddram", 0,
        Subsignal("a", Pins(
            "U6 T5 Y6 T6  V2 T4 Y2 R2",
            "Y1 R4 W5 W1 AA6 U2"),
            IOStandard("SSTL15")),
        Subsignal("ba",    Pins("W6 U5 R6"), IOStandard("SSTL15")),
        Subsignal("ras_n", Pins("V5"),  IOStandard("SSTL15")),
        Subsignal("cas_n", Pins("T1"),  IOStandard("SSTL15")),
        Subsignal("we_n",  Pins("R3"),  IOStandard("SSTL15")),
        Subsignal("dm", Pins("Y7 AA1"), IOStandard("SSTL15")),
        Subsignal("dq", Pins(
            "Y8 AB6 W9  AA8 AB7 V7 AB8  W7",
            "V4 AB2 AA5 AB3 AB5 W4 AB1 AA4"),
            IOStandard("SSTL15"),
            Misc("IN_TERM=UNTUNED_SPLIT_50")),
        Subsignal("dqs_p", Pins("V9 Y3"),  IOStandard("DIFF_SSTL15")),
        Subsignal("dqs_n", Pins("V8 AA3"), IOStandard("DIFF_SSTL15")),
        Subsignal("clk_p", Pins("U3"), IOStandard("DIFF_SSTL15")),
        Subsignal("clk_n", Pins("V3"), IOStandard("DIFF_SSTL15")),
        Subsignal("cke",   Pins("U1"), IOStandard("SSTL15")),
        Subsignal("odt",   Pins("W2"), IOStandard("SSTL15")),
        Subsignal("reset_n", Pins("U7"), IOStandard("LVCMOS15")),
        Subsignal("cs_n", Pins("T3"), IOStandard("SSTL15")),
        Misc("SLEW=FAST"),
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self):
        XilinxPlatform.__init__(self, "xc7a200t-fbg484-2", _io, toolchain="vivado")
        self.add_platform_command("set_property INTERNAL_VREF 0.750 [get_iobanks 34]")
        self.toolchain.bitstream_commands = [
            "set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]",
            "set_property BITSTREAM.CONFIG.CONFIGRATE 16 [current_design]",
            "set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]"
        ]
        self.toolchain.additional_commands = \
            ["write_cfgmem -force -format bin -interface spix4 -size 16 "
             "-loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"]

    def create_programmer(self):
        return OpenOCD("openocd_xc7_ft232.cfg", "bscan_spi_xc7a200t.bit")

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100", loose=True), 1e9/100e6)
