#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2018-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause
# Kintex7-420T
# Part xc7k420tiffg901-2L
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

    # SPIFlash (Micron N25Q256A / mt25ql256 (32MB))
    #("spiflash4x", 0,
    #    Subsignal("cs_n", Pins("V26")),
        #Subsignal("clk",  Pins("")), # driven through JTAG H13 #T22 ?
    #    Subsignal("dq", Pins("R30","T30","R28","T28")),
    #    IOStandard("LVCMOS33"),
    #),


]

# Connectors ---------------------------------------------------------------------------------------
# to add connector 
_connectors = []

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
