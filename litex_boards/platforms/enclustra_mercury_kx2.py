#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Mark Standke <mstandke@cern.ch>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk200", 0,
        Subsignal("p", Pins("AB11"), IOStandard("LVDS")),
        Subsignal("n", Pins("AC11"), IOStandard("LVDS"))
    ),
    ("cpu_reset_n", 0, Pins("G9"), IOStandard("LVCMOS25")),

    # Leds
    ("user_led", 0, Pins("U9"),  IOStandard("LVCMOS15")),
    ("user_led", 1, Pins("V12"), IOStandard("LVCMOS15")),
    #("user_led", 2, Pins("V13"), IOStandard("LVCMOS15")),
    #("user_led", 3, Pins("W13"), IOStandard("LVCMOS15")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("W11")),
        Subsignal("rx", Pins("AB16")),
        IOStandard("LVCMOS15")  # FIXME: LVCMOS15 or LVCMOS33?
     ),

    # DDR3 SDRAM
    ("ddram", 0,
        Subsignal("a", Pins(
            "AE11 AF9 AD10 AB10  AA9 AB9 AA8 AC8",
            "AA7  AE8 AF10 AD8  AE10 AF8 AC7"),
            IOStandard("SSTL15")),
        Subsignal("ba",    Pins("AD11 AA10 AF12"), IOStandard("SSTL15")),
        Subsignal("ras_n", Pins("AE13"), IOStandard("SSTL15")),
        Subsignal("cas_n", Pins("AE12"), IOStandard("SSTL15")),
        Subsignal("we_n",  Pins("AA12"), IOStandard("SSTL15")),
        Subsignal("cs_n",  Pins("Y12"), IOStandard("SSTL15")),
        Subsignal("dm", Pins(
            "Y3 U5 AD4 AC4 AF19 AC16 AB19 V14"),
            IOStandard("SSTL15")),
        Subsignal("dq", Pins(
            "AA2    Y2  AB2   V1   Y1   W1  AC2   V2",
            "W3     V3   U1   U7   U6   V4   V6   U2",
            "AE3   AE6  AF3  AD1  AE1  AE2  AF2  AE5",
            "AD5    Y5  AC6   Y6  AB4  AD6  AB6  AC3",
            "AD16 AE17 AF15 AF20 AD15 AF14 AE15 AF17",
            "AA14 AA15 AC14 AD14 AB14 AB15 AA17 AA18",
            "AB20 AD19 AC19 AA20 AA19 AC17 AD18 AB17",
            "W15   W16  W14   V16 V19  V17  V18  Y17"),
            IOStandard("SSTL15_T_DCI")),
        Subsignal("dqs_p", Pins("AB1 W6 AF5 AA5 AE18 Y15 AD20 W18"),
            IOStandard("DIFF_SSTL15")),
        Subsignal("dqs_n", Pins("AC1 W5 AF4 AB5 AF18 Y16 AE20 W19"),
            IOStandard("DIFF_SSTL15")),
        Subsignal("clk_p", Pins("AB12"), IOStandard("DIFF_SSTL15")),
        Subsignal("clk_n", Pins("AC12"), IOStandard("DIFF_SSTL15")),
        Subsignal("cke",   Pins("AA13"), IOStandard("SSTL15")),
        Subsignal("odt",   Pins("AD13"), IOStandard("SSTL15")),
        Subsignal("reset_n", Pins("AB7"), IOStandard("LVCMOS15")),
        Misc("SLEW=FAST"),
        Misc("VCCAUX_IO=HIGH")
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "clk200"
    default_clk_period = 1e9/200e6

    def __init__(self, toolchain="vivado"):
        XilinxPlatform.__init__(self, " xc7k160tffg676-2", _io, toolchain=toolchain)

    def create_programmer(self):
        return OpenOCD("openocd_xc7_ft232.cfg", "bscan_spi_xc7k160t.bit")

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk200", loose=True), 1e9/200e6)
