#"
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019-2024 Florent Kermarrec <florent@enjoy-digital.fr>
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
    
    ("ddram", 1,
        Subsignal("a", Pins(
            "G17 J20 H18 D21 D18 C21 J17 E17",
            "B21 A19 E20 A17 K19 C20 F17 K17"),
            IOStandard("SSTL15")),
        Subsignal("ba",    Pins("F20 D17 B19"), IOStandard("SSTL15")),
        Subsignal("ras_n", Pins("B17"), IOStandard("SSTL15")),
        Subsignal("cas_n", Pins("D20"), IOStandard("SSTL15")),
        Subsignal("we_n",  Pins("H20"), IOStandard("SSTL15")),
        Subsignal("dm", Pins("M13 J13 G14 A14 B23 D26 A31 F31"), IOStandard("SSTL15")),
        Subsignal("dq", Pins(
            "M11 M12 N14 M14 N13 L12 L14 N15",
            "K15 K14 H14 L16 K13 H13 H15 J15",
            "E14 F15 F16 E15 G12 F12 E13 F14",
            "D15 D16 B16 C16 E12 C13 B14 D13",
            "C24 A25 B26 B27 B22 A22 C23 A24",
            "D25 C25 E24 E23 D22 D23 E22 F22",
            "A29 A30 A32 D28 C28 C29 D27 C31",
            "D30 E30 C30 F30 F27 F26 F29 E29"),
            IOStandard("SSTL15_T_DCI")),
        Subsignal("dqs_p", Pins("N16 K12 H16 C15 A26 F25 B28 E27"), IOStandard("DIFF_SSTL15_T_DCI")),
        Subsignal("dqs_n", Pins("M16 J12 G16 C14 A27 E25 B29 E28"), IOStandard("DIFF_SSTL15_T_DCI")),
        Subsignal("clk_p", Pins("G19 E19"), IOStandard("DIFF_SSTL15")),
        Subsignal("clk_n", Pins("F19 E18"), IOStandard("DIFF_SSTL15")),
        Subsignal("cke",   Pins("M17"), IOStandard("SSTL15")),
        Subsignal("odt",   Pins("J18"), IOStandard("SSTL15")),
        Subsignal("cs_n",  Pins("C19"), IOStandard("SSTL15")),
        Subsignal("reset", Pins("A15"), IOStandard("LVCMOS15")),
        Misc("SLEW=FAST"),
        Misc("VCCAUX_IO=NORMAL")
    ),
    
    # SDCard
    ("spisdcard", 0,
        Subsignal("rst",  Pins("BB12"), IOStandard("LVCMOS15"), Misc("VCCAUX_IO=NORMAL")),
        Subsignal("clk",  Pins("AJ25")),
        Subsignal("mosi", Pins("AJ26")),
        Subsignal("cs_n", Pins("AL26")),
        Subsignal("miso", Pins("AY29")),
        Misc("SLEW=FAST"),
        IOStandard("LVCMOS18"),
    ),
    
    ("sdcard", 0,
        Subsignal("rst",  Pins("BB12"), IOStandard("LVCMOS15"), Misc("VCCAUX_IO=NORMAL")),
        Subsignal("data", Pins("AY29 AM28 AL25 AL26")),
        Subsignal("cmd",  Pins("AJ26")),
        Subsignal("clk",  Pins("AJ25")),
        Subsignal("cd",   Pins("AW35")),
        Misc("SLEW=FAST"),
        IOStandard("LVCMOS18"),
    ),
    
    # I2C
    ("i2c", 0,
    	Subsignal("scl", Pins("AK24"), IOStandard("LVCMOS18")),
    	Subsignal("sda", Pins("AK25"), IOStandard("LVCMOS18")),
    	Misc("VCCAUX_IO=NORMAL")
    ),
    
    # SFP - Ethernet
    ("sfp_clk", 0,
    	Subsignal("p", Pins("AW32"), IOStandard("LVDS")), #
    	Subsignal("n", Pins("AW33"), IOStandard("LVDS"))
    ),
    
    ("sfp", 0,
    	Subsignal("txp", Pins("A6")),
    	Subsignal("txn", Pins("A5")),
    	Subsignal("rxn", Pins("B3")),
    	Subsignal("rxp", Pins("B4"))
    ),
    
    ("sfp", 1,
    	Subsignal("txp", Pins("B8")),
    	Subsignal("txn", Pins("B7")),
    	Subsignal("rxn", Pins("C1")),
    	Subsignal("rxp", Pins("C2"))
    ),
    
    
    ("sfp", 2,
    	Subsignal("txp", Pins("C6")),
    	Subsignal("txn", Pins("C5")),
    	Subsignal("rxn", Pins("D3")),
    	Subsignal("rxp", Pins("D4"))
    ),
    
    ("sfp", 3,
    	Subsignal("txp", Pins("D8")),
    	Subsignal("txn", Pins("D7")),
    	Subsignal("rxn", Pins("E1")),
    	Subsignal("rxp", Pins("E2"))
    ),

    ("sfp_tx_disable_n", 0, Pins("M18"), IOStandard("LVCMOS15")),
    ("sfp_led", Pins("G13 L15"), IOStandard("LVCMOS15")),
    ("sfp_mod_detect", Pins("N18"), IOStandard("LVCMOS15")),
    ("sfp_rs", Pins("N19 P18"), IOStandard("LVCMOS15")),
    ("sfp_rx_los", Pins("L17"), IOStandard("LVCMOS15")),
    ("sfp_tx_fault_n", Pins("M19"), IOStandard("LVCMOS15")),
    
    ("sfp_tx_disable_n", 1, Pins("B31"), IOStandard("LVCMOS15")),
    ("sfp_led", 1, Pins("AL22 BA20"), IOStandard("LVCMOS15")),
    ("sfp_mod_detect", 1, Pins("AL19"), IOStandard("LVCMOS15")),
    ("sfp_rs", 1, Pins("P20 N20"), IOStandard("LVCMOS15")),
    ("sfp_rx_los", 1, Pins("L20"), IOStandard("LVCMOS15")),
    ("sfp_tx_disable", 1, Pins("B31"), IOStandard("LVCMOS15")),
    ("sfp_tx_fault", 1, Pins("C26"), IOStandard("LVCMOS15")),
    	
    ("sfp_tx_disable_n", 2, Pins("J38"), IOStandard("LVCMOS15")),
    ("sfp_led", 2, Pins("AY18 AY17"), IOStandard("LVCMOS15")),
    ("sfp_mod_detect", 2, Pins("J37"), IOStandard("LVCMOS15")),
    ("sfp_rs", 2, Pins("F39 G36"), IOStandard("LVCMOS15")),
    ("sfp_rx_los", 2, Pins("G37"), IOStandard("LVCMOS15")),
    ("sfp_tx_disable", 2, Pins("J38"), IOStandard("LVCMOS15")),
    ("sfp_tx_fault", 2, Pins("E39"), IOStandard("LVCMOS15")),
    	
    ("sfp_tx_disable_n", 3, Pins("L21"), IOStandard("LVCMOS15")),
    ("sfp_led", 3, Pins("P31 K32"), IOStandard("LVCMOS15")),
    ("sfp_mod_detect", 3, Pins("H36"), IOStandard("LVCMOS15")),
    ("sfp_rs", 3, Pins("H38 G38"), IOStandard("LVCMOS15")),
    ("sfp_rx_los", 3, Pins("J36"), IOStandard("LVCMOS15")),
    ("sfp_tx_disable", 3, Pins("L21"), IOStandard("LVCMOS15")),
    ("sfp_tx_fault", 3, Pins("J26"), IOStandard("LVCMOS15"))
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
        return OpenOCD("openocd_xc7_ft2232.cfg", "xc7vx690t.bit")

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk200",             loose=True), 1e9/200e6)
