#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Andrew Elbert Wilson <andrew.e.wilson@ieee.org>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxUSPlatform, VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk250", 0,
        Subsignal("p", Pins("H22"), IOStandard("LVDS")),
        Subsignal("n", Pins("H23"), IOStandard("LVDS"))
    ),

    ("cpu_reset", 0, Pins("N24"), IOStandard("LVCMOS12")),


    # Serial
    ("serial", 0,
        Subsignal("tx",  Pins("D20")),
        Subsignal("rx",  Pins("C19")),
        IOStandard("LVCMOS18")
    ),

   # MII Ethernet
    ("eth_clocks", 0,
        Subsignal("tx", Pins("G10")),
        Subsignal("rx", Pins("E11")),
        IOStandard("LVCMOS18")
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("D9")),
        #Subsignal("int_n",   Pins("Y14")),
        Subsignal("mdio",    Pins("C8")),
        Subsignal("mdc",     Pins("C9")),
        Subsignal("rx_ctl",  Pins("D11")),
        Subsignal("rx_data", Pins("A10 B10 B11 C11")),
        Subsignal("tx_ctl",  Pins("G9")),
        Subsignal("tx_data", Pins("H8 H9 J9 J10")),
        IOStandard("LVCMOS18")
    ),
    
    # DDR4 SDRAM
    ("ddram", 0,
        Subsignal("a", Pins(
            "AA24 AB24 AB26 AC26 AA22 AB22 Y23 AA23",
            "AC23 AC24 W23 W24 W25 W26"),
            IOStandard("SSTL12_DCI")),
        Subsignal("ba",      Pins("V26 U24"), IOStandard("SSTL12_DCI")),
        Subsignal("bg",      Pins("V24"), IOStandard("SSTL12_DCI")),
        Subsignal("ras_n",   Pins("U26"), IOStandard("SSTL12_DCI")), # A16
        Subsignal("cas_n",   Pins("Y26"), IOStandard("SSTL12_DCI")), # A15
        Subsignal("we_n",    Pins("Y25"), IOStandard("SSTL12_DCI")), # A14
        Subsignal("cs_n",    Pins("V22"), IOStandard("SSTL12_DCI")),
        Subsignal("act_n",   Pins("T24"), IOStandard("SSTL12_DCI")),
        #Subsignal("ten",     Pins("AH16"), IOStandard("SSTL12_DCI")),
        #Subsignal("alert_n", Pins("AJ16"), IOStandard("SSTL12_DCI")),
        #Subsignal("par",     Pins("AD18"), IOStandard("SSTL12_DCI")),
        Subsignal("dm",      Pins("T23 R18 N23 E25"),
            IOStandard("POD12_DCI")),
        Subsignal("dq",      Pins(
            "T22 U22 P26 R26 P23 P24 P25 R25",
            "P21 R21 P18 P19 P20 R20 U20 U21",
            "N26 M26 M24 L24 N22 M22 M25 L25",
            "H26 G26 G25 F25 J24 J25 H24 G24"),
            IOStandard("POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_p",   Pins("R22 T19 K26 F22"),
            IOStandard("DIFF_POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_n",   Pins("R23 T20 J26 F23"),
            IOStandard("DIFF_POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("clk_p",   Pins("AA25"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("clk_n",   Pins("AB25"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("cke",     Pins("V23"), IOStandard("SSTL12_DCI")),
        Subsignal("odt",     Pins("U25"), IOStandard("SSTL12_DCI")),
        Subsignal("reset_n", Pins("T25"), IOStandard("LVCMOS12")),
        Misc("SLEW=FAST"),
    ),

 
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("pmod0", "J13 H13 A13 A12 C12 B12 D13 C13"),
    ("pmod1", "F9  F8  E8  D8  E10 D10 G12 F12"),
]

# PMODS --------------------------------------------------------------------------------------------

def raw_pmod_io(pmod):
    return [(pmod, 0, Pins(" ".join([f"{pmod}:{i:d}" for i in range(8)])), IOStandard("LVCMOS33"))]

def usb_pmod_io(pmod):
    return [
        # USB-UART PMOD: https://store.digilentinc.com/pmod-usbuart-usb-to-uart-interface/
        ("usb_uart", 0,
            Subsignal("tx", Pins(f"{pmod}:1")),
            Subsignal("rx", Pins(f"{pmod}:2")),
            IOStandard("LVCMOS18")
        ),
    ]
_usb_uart_pmod_io = usb_pmod_io("pmod0") # USB-UART PMOD on JB.


def i2s_pmod_io(pmod):
    return [
        # I2S PMOD: https://store.digilentinc.com/pmod-i2s2-stereo-audio-input-and-output/
        ("i2s_rx_mclk", 0, Pins(f"{pmod}:4"), IOStandard("LVCMOS33")),
        ("i2s_rx", 0,
            Subsignal("clk", Pins(f"{pmod}:6")),
            Subsignal("sync", Pins(f"{pmod}:5")),
            Subsignal("rx", Pins(f"{pmod}:7")),
            IOStandard("LVCMOS18"),
        ),
        ("i2s_tx_mclk", 0, Pins(f"{pmod}:0"), IOStandard("LVCMOS33")),
        ("i2s_tx", 0,
            Subsignal("clk",Pins(f"{pmod}:2")),
            Subsignal("sync", Pins(f"{pmod}:1")),
            Subsignal("tx", Pins(f"{pmod}:3")),
            IOStandard("LVCMOS18"),
        ),
    ]
_i2s_pmod_io = i2s_pmod_io("pmod0") # I2S PMOD on JA.

def sdcard_pmod_io(pmod):
    return [
        # SDCard PMOD:
        # - https://store.digilentinc.com/pmod-microsd-microsd-card-slot/
        # - https://github.com/antmicro/arty-expansion-board
        ("spisdcard", 0,
            Subsignal("clk",  Pins(f"{pmod}:3")),
            Subsignal("mosi", Pins(f"{pmod}:1"), Misc("PULLUP True")),
            Subsignal("cs_n", Pins(f"{pmod}:0"), Misc("PULLUP True")),
            Subsignal("miso", Pins(f"{pmod}:2"), Misc("PULLUP True")),
            Misc("SLEW=FAST"),
            IOStandard("LVCMOS18"),
        ),
        ("sdcard", 0,
            Subsignal("data", Pins(f"{pmod}:2 {pmod}:4 {pmod}:5 {pmod}:0"), Misc("PULLUP True")),
            Subsignal("cmd",  Pins(f"{pmod}:1"), Misc("PULLUP True")),
            Subsignal("clk",  Pins(f"{pmod}:3")),
            Subsignal("cd",   Pins(f"{pmod}:6")),
            Misc("SLEW=FAST"),
            IOStandard("LVCMOS18"),
        ),
]
_sdcard_pmod_io = sdcard_pmod_io("pmod0") # SDCARD PMOD on JD.

def numato_sdcard_pmod_io(pmod):
    return [
        # SDCard PMOD:
        # https://numato.com/product/micro-sd-expansion-module/
        # This adaptor does not have the card detect (CD) pin connected
        ("spisdcard", 0,
            Subsignal("clk",  Pins(f"{pmod}:5")),
            Subsignal("mosi", Pins(f"{pmod}:1"), Misc("PULLUP True")),
            Subsignal("cs_n", Pins(f"{pmod}:4"), Misc("PULLUP True")),
            Subsignal("miso", Pins(f"{pmod}:2"), Misc("PULLUP True")),
            Misc("SLEW=FAST"),
            IOStandard("LVCMOS18"),
        ),
        ("sdcard", 0,
            Subsignal("data", Pins(f"{pmod}:2 {pmod}:6 {pmod}:0 {pmod}:4"), Misc("PULLUP True")),
            Subsignal("cmd",  Pins(f"{pmod}:1"), Misc("PULLUP True")),
            Subsignal("clk",  Pins(f"{pmod}:5")),
            Misc("SLEW=FAST"),
            IOStandard("LVCMOS18"),
        ),
]
_numato_sdcard_pmod_io = numato_sdcard_pmod_io("pmod0") # SDCARD PMOD on JD.

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxUSPlatform):
    default_clk_name   = "clk250"
    default_clk_period = 1e9/250e6

    def __init__(self):
        XilinxUSPlatform.__init__(self, "xcku040-fbva676-1-c", _io, _connectors, toolchain="vivado")

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment):
        XilinxUSPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk250", loose=True), 1e9/250e6)
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 44]")
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 45]")
