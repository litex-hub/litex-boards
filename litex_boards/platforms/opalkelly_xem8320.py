#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Andrew Elbert Wilson <Andrew.E.Wilson@ieee.org>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxUSPPlatform, VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("sys_clk100", 0,
        Subsignal("p", Pins("T24"), IOStandard("LVDS")),
        Subsignal("n", Pins("U24"), IOStandard("LVDS"))
    ),

    ("ddr_clk100", 0,
        Subsignal("p", Pins("AD20"), IOStandard("LVDS")),
        Subsignal("n", Pins("AE20"), IOStandard("LVDS"))
    ),
    #NO RESET, maybe use okHOST USB later
    #("cpu_reset", 0, Pins("AN8"), IOStandard("LVCMOS18")),

    # Leds
    ("user_led", 0, Pins("G19"), IOStandard("LVCMOS18")),
    ("user_led", 1, Pins("B16"), IOStandard("LVCMOS18")),
    ("user_led", 2, Pins("F22"), IOStandard("LVCMOS18")),
    ("user_led", 3, Pins("E22"), IOStandard("LVCMOS18")),
    ("user_led", 4, Pins("M24"), IOStandard("LVCMOS18")),
    ("user_led", 5, Pins("G22"), IOStandard("LVCMOS18")),

    # Opal Kelly Host USBC interface
    ("okHost", 0, # Uses the FrontPanel API
        Subsignal("okAA",  Pins("T19")),
        Subsignal("okHU",  Pins("U20 U26 T22")),
        Subsignal("okUH",  Pins("V23 T23 U22 U25 U21")),
        Subsignal("okUHU", Pins(
            "P26 P25 R26 R25 R23 R22 P21 P20",
            "R21 R20 P23 N23 T25 N24 N22 V26",
            "N19 V21 N21 W20 W26 W19 Y25 Y26",
            "Y22 V22 W21 AA23 Y23 AA24 W25 AA25")),
        IOStandard("LVCMOS18"),
        Misc("SLEW=FAST"),
    ),

    # TODO: Add SMA & SFP+

    # DDR4 SDRAM
    ("ddram", 0,
        Subsignal("a", Pins(
            "AD18 AE17 AB17 AE18 AD19 AF17 Y17 AE16",
            "AA17 AC17 AC19 AC16 AF20 AD16"),
            IOStandard("SSTL12_DCI")),
        Subsignal("ba",      Pins("AC18 AF18"), IOStandard("SSTL12_DCI")),
        Subsignal("bg",      Pins("AB19"), IOStandard("SSTL12_DCI")),
        Subsignal("ras_n",   Pins("AA18"), IOStandard("SSTL12_DCI")), 
        Subsignal("cas_n",   Pins("AF19"), IOStandard("SSTL12_DCI")), 
        Subsignal("we_n",    Pins("AA19"), IOStandard("SSTL12_DCI")), 
        Subsignal("cs_n",    Pins("AF22"), IOStandard("SSTL12_DCI")),
        Subsignal("act_n",   Pins("Y18"), IOStandard("SSTL12_DCI")),
        Subsignal("dm",      Pins("AE25 AE22"),
            IOStandard("POD12_DCI")),
        Subsignal("dq",      Pins(
            "AF24 AB25 AB26 AC24 AF25 AB24 AD24 AD25",
            "AB21 AE21 AE23 AD23 AC23 AD21 AC22 AC21"),
            IOStandard("POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_p",   Pins("AC26 AA22"),
            IOStandard("DIFF_POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_n",   Pins("AD26 AB22"),
            IOStandard("DIFF_POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("clk_p",   Pins("Y20"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("clk_n",   Pins("Y21"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("cke",     Pins("AA20"), IOStandard("SSTL12_DCI")),
        Subsignal("odt",     Pins("AB20"), IOStandard("SSTL12_DCI")),
        Subsignal("reset_n", Pins("AE26"), IOStandard("LVCMOS12")),
        Misc("SLEW=FAST"),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

# TODO: SYZYGY Connectors & SYZYGY to PMODS!

_connectors = [
    ("pmod1", "AC14 AC13 AF15 AF14 AF13 AE13 H13  J13"),
    ("pmod2", "AB15 AB16 W14  J14  AE15 W15  Y15  J15"),
    ("pmod3", "G14  H14  W13  W12  AA13 Y13  H12  J12"),
    ("pmod4", "AD14 AD13 W16  AD15 AB14 AA14 Y16  AA15"),
]

def dvi_pmod_io(pmoda,pmodb):
    return [
        ("dvi", 0,
            Subsignal("clk",   Pins(f"{pmodb}:1")),
            Subsignal("de",    Pins(f"{pmodb}:6")),
            Subsignal("hsync", Pins(f"{pmodb}:3")),
            Subsignal("vsync", Pins(f"{pmodb}:7")),
            Subsignal("b",     Pins(f"{pmoda}:5 {pmoda}:1 {pmoda}:4 {pmoda}:0")),
            Subsignal("g",     Pins(f"{pmoda}:7 {pmoda}:3 {pmoda}:6 {pmoda}:2")),
            Subsignal("r",     Pins(f"{pmodb}:2 {pmodb}:5 {pmodb}:4 {pmodb}:0")),
            IOStandard("LVCMOS33"),
        )
    ]

_dvi_pmod_io = dvi_pmod_io("pmod2","pmod1") # SDCARD PMOD on JD.

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
            IOStandard("LVCMOS33"),
        ),
        ("sdcard", 0,
            Subsignal("data", Pins(f"{pmod}:2 {pmod}:4 {pmod}:5 {pmod}:0"), Misc("PULLUP True")),
            Subsignal("cmd",  Pins(f"{pmod}:1"), Misc("PULLUP True")),
            Subsignal("clk",  Pins(f"{pmod}:3")),
            Subsignal("cd",   Pins(f"{pmod}:6")),
            Misc("SLEW=FAST"),
            IOStandard("LVCMOS33"),
        ),
]

_sdcard_pmod_io = sdcard_pmod_io("pmod3") # SDCARD PMOD on JD.

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxUSPPlatform):
    default_clk_name   = "sys_clk100"
    default_clk_period = 1e9/100e6

    def __init__(self, toolchain="vivado"):
        XilinxUSPPlatform.__init__(self, "xcau25p-ffvb676-2-e", _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment):
        XilinxUSPPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("sys_clk100", loose=True), 1e9/100e6)
        self.add_period_constraint(self.lookup_request("ddr_clk100", loose=True), 1e9/100e6)
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 64]")
