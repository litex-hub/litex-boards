#
# This file is part of LiteX-Boards.
#
# Support for the ZTEX USB-FGPA Module 2.13:
# <https://www.ztex.de/usb-fpga-2/usb-fpga-2.13.e.html>
# With (no-so-optional) expansion, either the ZTEX Debug board:
# <https://www.ztex.de/usb-fpga-2/debug.e.html>
# Or the SBusFPGA adapter board:
# <https://github.com/rdolbeau/SBusFPGA>
#
# Copyright (c) 2015 Yann Sionneau <yann.sionneau@gmail.com>
# Copyright (c) 2015-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2020-2021 Romain Dolbeau <romain@dolbeau.org>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    ## 48 MHz clock reference
    ("clk48", 0, Pins("P15"), IOStandard("LVCMOS33")),
    ## embedded 256 MiB DDR3 DRAM
    ("ddram", 0,
        Subsignal("a", Pins("C5 B6 C7 D5 A3 E7 A4 C6", "A6 D8 B2 A5 B3 B7"),
            IOStandard("SSTL135")),
        Subsignal("ba",    Pins("E5 A1 E6"), IOStandard("SSTL135")),
        Subsignal("ras_n", Pins("E3"), IOStandard("SSTL135")),
        Subsignal("cas_n", Pins("D3"), IOStandard("SSTL135")),
        Subsignal("we_n",  Pins("D4"), IOStandard("SSTL135")),
#        Subsignal("cs_n",  Pins(""), IOStandard("SSTL135")),
        Subsignal("dm", Pins("G1 G6"), IOStandard("SSTL135")),
        Subsignal("dq", Pins(
            "H1 F1 E2 E1 F4 C1 F3 D2",
            "G4 H5 G3 H6 J2 J3 K1 K2"),
            IOStandard("SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("dqs_p", Pins("H2 J4"),
            IOStandard("DIFF_SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("dqs_n", Pins("G2 H4"),
            IOStandard("DIFF_SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("clk_p", Pins("C4"), IOStandard("DIFF_SSTL135")),
        Subsignal("clk_n", Pins("B4"), IOStandard("DIFF_SSTL135")),
        Subsignal("cke",   Pins("B1"), IOStandard("SSTL135")),
        Subsignal("odt",   Pins("F5"), IOStandard("SSTL135")),
        Subsignal("reset_n", Pins("J5"), IOStandard("SSTL135")),
        Misc("SLEW=FAST"),
    ),
]

_debug_io = [
    ## leds on the debug board
    ("user_led", 0, Pins("H15"),  IOStandard("lvcmos33")), #LED0
    ("user_led", 1, Pins("J13"),  IOStandard("lvcmos33")), #LED1
    ("user_led", 2, Pins("J14"),  IOStandard("lvcmos33")), #LED2
    ("user_led", 3, Pins("H14"),  IOStandard("lvcmos33")), #LED3
    ("user_led", 4, Pins("H17"),  IOStandard("lvcmos33")), #LED4
    ("user_led", 5, Pins("G14"),  IOStandard("lvcmos33")), #LED5
    ("user_led", 6, Pins("G17"),  IOStandard("lvcmos33")), #LED6
    ("user_led", 7, Pins("G16"),  IOStandard("lvcmos33")), #LED7
    ("user_led", 8, Pins("G18"),  IOStandard("lvcmos33")), #LED8
    ("user_led", 9, Pins("H16"),  IOStandard("lvcmos33")), #LED9
    ("user_led", 10, Pins("U9"),  IOStandard("lvcmos33")), #LED10
    ("user_led", 11, Pins("V9"),  IOStandard("lvcmos33")), #LED11
    ("user_led", 12, Pins("U8"),  IOStandard("lvcmos33")), #LED12
    ("user_led", 13, Pins("V7"),  IOStandard("lvcmos33")), #LED13
    ("user_led", 14, Pins("U7"),  IOStandard("lvcmos33")), #LED14
    ("user_led", 15, Pins("V6"),  IOStandard("lvcmos33")), #LED15
    ("user_led", 16, Pins("U6"),  IOStandard("lvcmos33")), #LED16
    ("user_led", 17, Pins("V5"),  IOStandard("lvcmos33")), #LED17
    ("user_led", 18, Pins("T8"),  IOStandard("lvcmos33")), #LED18
    ("user_led", 19, Pins("V4"),  IOStandard("lvcmos33")), #LED19
    ("user_led", 20, Pins("R8"),  IOStandard("lvcmos33")), #LED20
    ("user_led", 21, Pins("T5"),  IOStandard("lvcmos33")), #LED21
    ("user_led", 22, Pins("R7"),  IOStandard("lvcmos33")), #LED22
    ("user_led", 23, Pins("T4"),  IOStandard("lvcmos33")), #LED23
    ("user_led", 24, Pins("T6"),  IOStandard("lvcmos33")), #LED24
    ("user_led", 25, Pins("U4"),  IOStandard("lvcmos33")), #LED25
    ("user_led", 26, Pins("R6"),  IOStandard("lvcmos33")), #LED26
    ("user_led", 27, Pins("U3"),  IOStandard("lvcmos33")), #LED27
    ("user_led", 28, Pins("R5"),  IOStandard("lvcmos33")), #LED28
    ("user_led", 29, Pins("V1"),  IOStandard("lvcmos33")), #LED29
    ## arbitrary selection of pins for the console
    ("serial", 0,
     Subsignal("tx", Pins("A13")), # A13 in B29
     Subsignal("rx", Pins("A11")), # A11 in B30
     IOStandard("LVCMOS33")
    ),
]

_sbus_io = [
    ## leds on the SBus board
    ("user_led", 0, Pins("U8"),  IOStandard("lvcmos33")), #LED0
    ("user_led", 1, Pins("U7"),  IOStandard("lvcmos33")), #LED1
    ("user_led", 2, Pins("U6"),  IOStandard("lvcmos33")), #LED2
    ("user_led", 3, Pins("T8"),  IOStandard("lvcmos33")), #LED3
    ("user_led", 4, Pins("P4"),  IOStandard("lvcmos33")), #LED4
    ("user_led", 5, Pins("P3"),  IOStandard("lvcmos33")), #LED5
    ("user_led", 6, Pins("T1"),  IOStandard("lvcmos33")), #LED6
    ("user_led", 7, Pins("R1"),  IOStandard("lvcmos33")), #LED7
    ("user_led", 8, Pins("U1"),  IOStandard("lvcmos33")), #SBUS_DATA_OE_LED
    ("user_led", 9, Pins("T3"),  IOStandard("lvcmos33")), #SBUS_DATA_OE_LED_2
    ## serial header for console
    ("serial", 0,
     Subsignal("tx", Pins("V9")), # FIXME: might be the other way round
     Subsignal("rx", Pins("U9")),
     IOStandard("LVCMOS33")
    ),
    ## sdcard connector
    ("spisdcard", 0,
        Subsignal("clk",  Pins("R8")),
        Subsignal("mosi", Pins("T5"), Misc("PULLUP")),
        Subsignal("cs_n", Pins("V6"), Misc("PULLUP")),
        Subsignal("miso", Pins("V5"), Misc("PULLUP")),
        Misc("SLEW=FAST"),
        IOStandard("LVCMOS33"),
    ),
    ("sdcard", 0,
        Subsignal("data", Pins("V5 V4 V7 V6"), Misc("PULLUP")),
        Subsignal("cmd",  Pins("T5"), Misc("PULLUP")),
        Subsignal("clk",  Pins("R8")),
        #Subsignal("cd",   Pins("V6")),
        Misc("SLEW=FAST"),
        IOStandard("LVCMOS33"),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "clk48"
    default_clk_period = 1e9/48e6

    def __init__(self, variant="ztex2.13a", toolchain="vivado", expansion="debug"):
        device = {
            "ztex2.13a":  "xc7a35tcsg324-1",
            #"ztex2.13b":  "xc7a50tcsg324-1", #untested
            #"ztex2.13b2": "xc7a50tcsg324-1", #untested
            #"ztex2.13c":  "xc7a75tcsg324-2", #untested
            #"ztex2.13d":  "xc7a100tcsg324-2", #untested
        }[variant]
        XilinxPlatform.__init__(self, device, _io, _connectors, toolchain=toolchain)
        if (expansion == "debug"):
            self.add_extension(_debug_io)
        else:
            if (expansion == "sbus"):
                self.add_extension(_sbus_io)
        self.toolchain.bitstream_commands = \
            ["set_property BITSTREAM.CONFIG.SPI_32BIT_ADDR No [current_design]",
             "set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 2 [current_design]",
             "set_property BITSTREAM.CONFIG.CONFIGRATE 66 [current_design]",
             "set_property BITSTREAM.GENERAL.COMPRESS true [current_design]"
             ]

    def create_programmer(self):
        bscan_spi = "bscan_spi_xc7a35t.bit"
        return OpenOCD("openocd_xc7_ft2232.cfg", bscan_spi) #FIXME

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk48", loose=True), 1e9/48e6)
