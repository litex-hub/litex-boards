#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Alex Petrov <sysman@sysman.net>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform, VivadoProgrammer
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk100",    0, Pins("G27"), IOStandard("LVCMOS33")),
    ("cpu_reset", 0, Pins("W12"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led",  0, Pins("AJ22"), IOStandard("LVCMOS33")), # D3
    ("user_led",  1, Pins("AJ21"), IOStandard("LVCMOS33")), # D4
    ("user_led",  2, Pins("AK21"), IOStandard("LVCMOS33")), # D5
    ("user_led",  3, Pins("AK20"), IOStandard("LVCMOS33")), # D6
    ("user_led",  4, Pins("AK19"), IOStandard("LVCMOS33")), # D7
    ("user_led",  5, Pins("AJ19"), IOStandard("LVCMOS33")), # D8
    ("user_led",  6, Pins("AK18"), IOStandard("LVCMOS33")), # D9
    ("user_led",  7, Pins("AJ18"), IOStandard("LVCMOS33")), # D10

    # Buttons
    ("user_btn_k3", 0, Pins("AK15"), IOStandard("LVCMOS33")),
    ("user_btn_k2", 0, Pins("AK16"), IOStandard("LVCMOS33")),

    # Serial (CH340)
    ("serial", 0,
        Subsignal("tx", Pins("AK23")),
        Subsignal("rx", Pins("AJ23")),
        IOStandard("LVCMOS33")
    ),

    # SPIFlash (Micron N25Q256A (32MB))
    ("spiflash", 0,
        Subsignal("cs_n", Pins("V26"), IOStandard("LVCMOS33")),
        Subsignal("mosi", Pins("R30"), IOStandard("LVCMOS33")),
        Subsignal("miso", Pins("T30"), IOStandard("LVCMOS33")),
        Subsignal("wp",   Pins("R28"), IOStandard("LVCMOS33")),
        Subsignal("hold", Pins("T28"), IOStandard("LVCMOS33"))
    ),
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("V26"), IOStandard("LVCMOS33")),
        Subsignal("dq",   Pins("R30 T30 R28 T28"), IOStandard("LVCMOS33"))
    ),

]

# Connectors ---------------------------------------------------------------------------------------

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

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self, toolchain="vivado"):
        Xilinx7SeriesPlatform.__init__(self, "xc7k420tl-ffg901", _io, toolchain=toolchain)

    def create_programmer(self):
        return OpenOCD("openocd_xc7_ft2232.cfg", "bscan_spi_xc7a420t.bit")

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100", loose=True), 1e9/100e6)
