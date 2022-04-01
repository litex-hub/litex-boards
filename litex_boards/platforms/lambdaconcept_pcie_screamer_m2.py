#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2016-2022 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk.
    ("clk100", 0, Pins("R2"), IOStandard("LVCMOS33")),

    # Leds.
    ("user_led", 0, Pins("V17"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("U17"), IOStandard("LVCMOS33")),

    # Serial.
    ("serial", 0,
        Subsignal("tx", Pins("U4")),
        Subsignal("rx", Pins("V4")),
        IOStandard("LVCMOS33"),
    ),

    # PCIe.
    ("pcie_x1", 0,
        Subsignal("rst_n", Pins("M1"), IOStandard("LVCMOS33"), Misc("PULLUP=TRUE")),
        Subsignal("clk_p", Pins("D6")),
        Subsignal("clk_n", Pins("D5")),
        Subsignal("rx_p",  Pins("E4")),
        Subsignal("rx_n",  Pins("E3")),
        Subsignal("tx_p",  Pins("H2")),
        Subsignal("tx_n",  Pins("H1"))
    ),
    ("pcie_x4", 0,
        Subsignal("rst_n", Pins("M1"), IOStandard("LVCMOS33"), Misc("PULLUP=TRUE")),
        Subsignal("clk_p", Pins("D6")),
        Subsignal("clk_n", Pins("D5")),
        Subsignal("rx_p",  Pins("E4 A4 C4 G4")),
        Subsignal("rx_n",  Pins("E3 A3 C3 G3")),
        Subsignal("tx_p",  Pins("H2 F2 D2 B2")),
        Subsignal("tx_n",  Pins("H1 F1 D1 B1"))
    ),

    # USB-FIFO.
    ("usb_fifo_clock", 0, Pins("E13"), IOStandard("LVCMOS33")),
    ("usb_fifo", 0,
        Subsignal("rst",  Pins("U15")),
        Subsignal("data", Pins(
            "B9   A9  C9 A10 B10 B11 A12 B12",
            "A13 A14 B14 A15 B15 B16 A17 B17",
            "C17 C18 D18 E17 E18 E16 F18 F17",
            "G17 H18 D13 C14 D14 D15 C16 D16")),
        Subsignal("be",    Pins("L18 M17 N18 N17")),
        Subsignal("rxf_n", Pins("R18")),
        Subsignal("txe_n", Pins("P18")),
        Subsignal("rd_n",  Pins("R16")),
        Subsignal("wr_n",  Pins("T18")),
        Subsignal("oe_n",  Pins("T15")),
        Subsignal("siwua", Pins("R17")),
        IOStandard("LVCMOS33"),
        Misc("SLEW=FAST")
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self):
        XilinxPlatform.__init__(self, "xc7a35t-csg325-2", _io, toolchain="vivado")
        self.toolchain.bitstream_commands = \
            ["set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]",
             "set_property BITSTREAM.CONFIG.CONFIGRATE 40 [current_design]"]
        self.toolchain.additional_commands = \
            ["write_cfgmem -force -format bin -interface spix4 -size 16 "
             "-loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"]

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100", loose=True), 1e9/100e6)

