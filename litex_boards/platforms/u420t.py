#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2018-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause
# Kintex7-420T
# Part xc7k420tiffg901-2L v0.2 update
# ported by Alex Petrov aka sysman

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform, VivadoProgrammer
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    # u420t clk_y1 G27/ clk_y3 E25
    ("clk100", 0, Pins("G27"), IOStandard("LVCMOS33")),
    #("sysclk", 0, Pins("E25"), IOStandard("LVCMOS33")),
    #("clk100", 0,
    #    Subsignal("p", Pins("AB27"), IOStandard("DIFF_SSTL15")),
    #    Subsignal("n", Pins("AA27"), IOStandard("DIFF_SSTL15"))
    #),
    ("cpu_reset", 0, Pins("W12"), IOStandard("LVCMOS33")),

    # Leds board: D3-D10
    ("user_led",  0, Pins("AJ22"), IOStandard("LVCMOS33")),
    ("user_led",  1, Pins("AJ21"), IOStandard("LVCMOS33")),
    ("user_led",  2, Pins("AK21"), IOStandard("LVCMOS33")),
    ("user_led",  3, Pins("AK20"), IOStandard("LVCMOS33")),
    ("user_led",  4, Pins("AK19"), IOStandard("LVCMOS33")),
    ("user_led",  5, Pins("AJ19"), IOStandard("LVCMOS33")),
    ("user_led",  6, Pins("AK18"), IOStandard("LVCMOS33")),
    ("user_led",  7, Pins("AJ18"), IOStandard("LVCMOS33")),

    # Buttons
    ("user_btn_k3", 0, Pins("AK15"), IOStandard("LVCMOS33")),
    ("user_btn_k2", 0, Pins("AK16"), IOStandard("LVCMOS33")),
 #   ("user_btnb", 0, Pins("AB11"), IOStandard("LVCMOS33")),

    # http://www.wch-ic.com/products/CH340.html
    # Serial CH340 , warning: wrong schema
    ("serial", 0,
        Subsignal("tx", Pins("AK23")), ## U340 schem rx
        Subsignal("rx", Pins("AJ23")), ## U340 schem tx
        IOStandard("LVCMOS33")
    ),

    # SPIFlash (Micron N25Q256A (32MB))
    ("spiflash", 0,
        Subsignal("cs_n", Pins("V26"), IOStandard("LVCMOS33")),
        #Subsignal("clk",  Pins("G7"), IOStandard("LVCMOS33")),
        Subsignal("mosi", Pins("R30"), IOStandard("LVCMOS33")),
        Subsignal("miso", Pins("T30"), IOStandard("LVCMOS33")),
        Subsignal("wp",   Pins("R28"), IOStandard("LVCMOS33")),
        Subsignal("hold", Pins("T28"), IOStandard("LVCMOS33"))
    ),
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("V26"), IOStandard("LVCMOS33")),
        #Subsignal("clk",  Pins("")), # driven through JTAG H13 #T22 ?
        Subsignal("dq",   Pins("R30 T30 R28 T28"), IOStandard("LVCMOS33"))
    ),

]

# Connectors ---------------------------------------------------------------------------------------
# to add connector
_connectors = [
# main board connector, pins as marked
( "main", {
   #    usb- 1 2 usb+ not used U3 usb3320 don't use
   #    GND  3 4 GND
   # QSPI_CS 5 6 QSPI_D1
   # QSPI_D0 7 8 QSPI_CLK
   9:  "B29",
   # 10: "Program_B"  key3 reset button
   11: "A28",
   12: "B27",
   13: "A27",
   14: "A26",
   15: "B25",
   16: "A25",
   17: "B24",
   18: "B23",
   19: "A23",
   20: "B22",
   21: "A22",
   22: "A21",
   23: "B20",
   24: "A20",
   # 25,26,27,28: GND
   # 29,30,31,32: V12
 })
]

# PMODS --------------------------------------------------------------------------------------------


# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self, toolchain="vivado"):
        XilinxPlatform.__init__(self, "xc7k420tl-ffg901", _io, toolchain=toolchain)
#        self.add_platform_command("")
#        self.add_platform_command("set_property INTERNAL_VREF 0.900 [current_design]")
#        self.add_platform_command("set_property INTERNAL_VREF 0.900 [get_iobanks 34]")

    def create_programmer(self):
        return OpenOCD("openocd_xc7_ft2232.cfg", "bscan_spi_xc7a420t.bit")

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100", loose=True), 1e9/100e6)
