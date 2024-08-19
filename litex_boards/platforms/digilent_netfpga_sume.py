#"
# This file is part of LiteX-Boards.
#
# Copyright (c) 2024 Gustavo Bastos <gustavocerq7@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform, VivadoProgrammer
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk200", 0, 
    	Subsignal("p", Pins("H19"),IOStandard("DIFF_SSTL15")),
    	Subsignal("n", Pins("G18"),IOStandard("DIFF_SSTL15")),
    	Misc("SLEW=FAST"),
    	Misc("VCCAUX_IO=NORMAL")
    ),
    
    ("clk233", 0,
        Subsignal("p", Pins("E34"), IOStandard("DIFF_SSTL15")),
        Subsignal("n", Pins("E35"), IOStandard("DIFF_SSTL15")),
        Misc("SLEW=FAST"),
        Misc("VCCAUX_IO=NORMAL")
    ),
    	
    # CPU Reset	
    ("cpu_reset_n", 0, Pins("AR13"), IOStandard("LVCMOS15"), Misc("VCCAUX_IO=NORMAL")),
    
    # Leds
    ("user_led",  0, Pins("AR22"), IOStandard("LVCMOS15"), Misc("VCCAUX_IO=NORMAL")),
    ("user_led",  1, Pins("AR23"), IOStandard("LVCMOS15"), Misc("VCCAUX_IO=NORMAL")),

    # Buttons
    ("user_btn", 0, Pins("BB12"), IOStandard("LVCMOS15"), Misc("VCCAUX_IO=NORMAL")),
    ("user_btn", 1, Pins("AR13"), IOStandard("LVCMOS15"), Misc("VCCAUX_IO=NORMAL")),

    # Serial
    ("serial", 0,
        Subsignal("rx", Pins("AY19")),
        Subsignal("tx", Pins("BA19")),
        Subsignal("rts",Pins("BB16")),
        Subsignal("cts",Pins("BA16")), 
        IOStandard("LVCMOS15"),
        Misc("VCCAUX_IO=NORMAL")
    ),

    # DDR3  SDRAM
    ("ddram", 0,
        Subsignal("a", Pins(
            "F35 B36 H33 D32 B34 A36 E33 E32",
            "C33 F34 F36 B32 C34 E37 F32 G33"),
            IOStandard("SSTL15")),
        Subsignal("ba",    Pins("B37 A35 A34"), IOStandard("SSTL15")),
        Subsignal("ras_n", Pins("D38"), IOStandard("SSTL15")),
        Subsignal("cas_n", Pins("D37"), IOStandard("SSTL15")),
        Subsignal("we_n",  Pins("A37"), IOStandard("SSTL15")),
        Subsignal("dm", Pins("K28 G24 L24 N26 W30 M31 J32 L31"), IOStandard("SSTL15")),
        Subsignal("dq", Pins(
            "K27 K24 J27 J28 K25 J25 G28 G29",
            "H21 H24 H23 G21 J21 G22 G26 G27",
            "M21 M24 J22 J23 K22 K23 L25 L26",
            "P21 P26 N23 N24 P25 N25 L27 M27",
            "U29 V30 U31 V31 Y29 V29 W31 Y30",
            "N29 N30 R30 N31 R28 N28 P28 P30",
            "J35 K35 L35 M34 M33 L34 J33 H34",
            "J31 K30 L32 M32 K29 H30 J30 H31"),
            IOStandard("SSTL15_T_DCI")),
        Subsignal("dqs_p", Pins("H28 H25 M22 P22 T29 M28 K33 L29"), IOStandard("DIFF_SSTL15_T_DCI")),
        Subsignal("dqs_n", Pins("H29 H26 L22 P23 T30 M29 K34 L30"), IOStandard("DIFF_SSTL15_T_DCI")),
        Subsignal("clk_p", Pins("C35 D35"), IOStandard("DIFF_SSTL15")),
        Subsignal("clk_n", Pins("C36 D36"), IOStandard("DIFF_SSTL15")),
        Subsignal("cke",   Pins("D33"), IOStandard("SSTL15"),),
        Subsignal("odt",   Pins("B39"), IOStandard("SSTL15")),
        Subsignal("cs_n",  Pins("A39"), IOStandard("SSTL15")),
        Subsignal("reset_n", Pins("B33"), IOStandard("LVCMOS15")),
        Misc("SLEW=FAST"),
        Misc("VCCAUX_IO=NORMAL"),
    ),
    
    # I2C
    ("i2c", 0,
    	Subsignal("scl", Pins("AK24"), IOStandard("LVCMOS18")),
    	Subsignal("sda", Pins("AK25"), IOStandard("LVCMOS18")),
    	Misc("VCCAUX_IO=NORMAL")
    ),

]

# Connectors ---------------------------------------------------------------------------------------
_connectors = []
# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk200"
    default_clk_period = 1e9/200e6

    def __init__(self, toolchain="vivado"):
        Xilinx7SeriesPlatform.__init__(self, "xc7vx690tffg1761-3", _io, _connectors, toolchain=toolchain)
        self.add_platform_command("set_property CFGBVS GND [current_design]")
        self.add_platform_command("set_property CONFIG_VOLTAGE 1.8 [current_design]")
        self.add_platform_command("set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]")
                
        self.add_platform_command("set_property INTERNAL_VREF 0.750 [get_iobanks 34]")
        self.add_platform_command("set_property INTERNAL_VREF 0.750 [get_iobanks 35]")
        self.add_platform_command("set_property INTERNAL_VREF 0.750 [get_iobanks 36]")
        self.add_platform_command("set_property INTERNAL_VREF 0.750 [get_iobanks 37]")
        self.add_platform_command("set_property INTERNAL_VREF 0.750 [get_iobanks 38]")
        self.add_platform_command("set_property INTERNAL_VREF 0.750 [get_iobanks 39]")

    def create_programmer(self):
        return OpenOCD() #not tested

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk200",             loose=True), 1e9/200e6)
