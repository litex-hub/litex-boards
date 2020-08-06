# This file is Copyright (c) 2017 Sergiusz Bazanski <q3k@q3k.org>
# This file is Copyright (c) 2018-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# License: BSD

from litex.build.generic_platform import *
from litex.build.lattice import LatticePlatform
from litex.build.lattice.programmer import OpenOCDJTAGProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    ("clk16", 0, Pins("K2"), IOStandard("LVCMOS33")),
    
    ("GSRN",  0, Pins("G19"), IOStandard("LVCMOS33")),
    ("PROGRAMN",  0, Pins("E11"), IOStandard("LVCMOS33")),
    ("PUSHBUTTON0",  0, Pins("G14"), IOStandard("LVCMOS33")),
    ("PUSHBUTTON1",  0, Pins("G15"), IOStandard("LVCMOS33")),

    ("serial", 0,
        Subsignal("rx", Pins("F16"), IOStandard("LVCMOS33")),
        Subsignal("tx", Pins("F18"), IOStandard("LVCMOS33")),
    ),

    ("user_led", 0, Pins("E17"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("F13"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("G13"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("F14"), IOStandard("LVCMOS33")),
    ("user_led", 4, Pins("L16"), IOStandard("LVCMOS33")),
    ("user_led", 5, Pins("L15"), IOStandard("LVCMOS33")),
    ("user_led", 6, Pins("L20"), IOStandard("LVCMOS33")),
    ("user_led", 7, Pins("L19"), IOStandard("LVCMOS33")),
    ("user_led", 8, Pins("R17"), IOStandard("LVCMOS33")),
    ("user_led", 9, Pins("R18"), IOStandard("LVCMOS33")),
    ("user_led", 10, Pins("U20"), IOStandard("LVCMOS33")),
    ("user_led", 11, Pins("T20"), IOStandard("LVCMOS33")),
    ("user_led", 12, Pins("W20"), IOStandard("LVCMOS33")),
    ("user_led", 13, Pins("V20"), IOStandard("LVCMOS33")),

    ("user_dip_btn", 0, Pins("N14"),  IOStandard("LVCMOS33")),
    ("user_dip_btn", 1, Pins("M14"),  IOStandard("LVCMOS33")),
    ("user_dip_btn", 2, Pins("M16"),  IOStandard("LVCMOS33")),
    ("user_dip_btn", 3, Pins("M15"),  IOStandard("LVCMOS33")),
    ("user_dip_btn", 4, Pins("N15"), IOStandard("LVCMOS33")),
    ("user_dip_btn", 5, Pins("N16"), IOStandard("LVCMOS33")),
    ("user_dip_btn", 6, Pins("M17"), IOStandard("LVCMOS33")),
    ("user_dip_btn", 7, Pins("M18"), IOStandard("LVCMOS33")),

    ("spiflash", 0, 
        Subsignal("cs_n", Pins("E13")),
        Subsignal("clk", Pins("E12")),
        Subsignal("mosi", Pins("D13")),
        Subsignal("miso", Pins("D15")),
        Subsignal("wp",   Pins("D14")),
        Subsignal("hold", Pins("D16")),
        IOStandard("LVCMOS33")
    ),

    ("spiflash4x", 0, 
        Subsignal("cs_n", Pins("E13")),
        Subsignal("clk", Pins("E12")),
        Subsignal("dq",   Pins("D13 D15 D14 D16")),
        IOStandard("LVCMOS33")
    )
]


# Connectors ---------------------------------------------------------------------------------------

_connectors = [
   #TODO PMOD0
   #TODO PMOD1
   #TODO PMOD2
   #TODO FMC
   #TODO ADC
   #TODO D-PHY
   #TODO R-RPI
]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticePlatform):
    default_clk_name   = "clk16"
    default_clk_period = 1e9/16e6

    def __init__(self, device="LIFCL", **kwargs):
        assert device in ["LIFCL"]
        LatticePlatform.__init__(self, device + "-40-9BG400C", _io, _connectors, toolchain="radiant", **kwargs)

    def create_programmer(self):
        return OpenOCDJTAGProgrammer("openocd_versa_ecp5.cfg") #TODO Make cfg for Crosslink-NX-Eval

    def do_finalize(self, fragment):
        self.add_period_constraint(self.lookup_request("clk16", loose=True), 1e9/16e6)

