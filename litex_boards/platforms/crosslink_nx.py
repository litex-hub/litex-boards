# This file is Copyright (c) 2017 Sergiusz Bazanski <q3k@q3k.org>
# This file is Copyright (c) 2018-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# License: BSD

from litex.build.generic_platform import *
from litex.build.lattice import LatticePlatform
from litex.build.lattice.programmer import OpenOCDJTAGProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    ("clk125", 0, Pins("C11"), IOStandard("LVDS")),
    
    ("GSRN",  0, Pins("G19"), IOStandard("LVCMOS33")),
    ("PROGRAMN",  0, Pins("E11"), IOStandard("LVCMOS33")),
    ("PUSHBUTTON0",  0, Pins("G14"), IOStandard("LVCMOS33")),
    ("PUSHBUTTON1",  0, Pins("G15"), IOStandard("LVCMOS33")),

    ("serial", 0,
        Subsignal("rx", Pins("F16"), IOStandard("LVCMOS33")),
        Subsignal("tx", Pins("F18"), IOStandard("LVCMOS33")),
    ),

    ("user_led", 0, Pins("E16"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("D17"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("D18"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("E18"), IOStandard("LVCMOS33")),
    ("user_led", 4, Pins("F17"), IOStandard("LVCMOS33")),
    ("user_led", 5, Pins("F18"), IOStandard("LVCMOS33")),
    ("user_led", 6, Pins("E17"), IOStandard("LVCMOS33")),
    ("user_led", 7, Pins("F16"), IOStandard("LVCMOS33")),
    ("user_led", 8, Pins("D18"), IOStandard("LVCMOS33")),
    ("user_led", 9, Pins("E18"), IOStandard("LVCMOS33")),
    ("user_led", 10, Pins("F17"), IOStandard("LVCMOS33")),
    ("user_led", 11, Pins("F18"), IOStandard("LVCMOS33")),
    ("user_led", 12, Pins("E17"), IOStandard("LVCMOS33")),
    ("user_led", 13, Pins("F16"), IOStandard("LVCMOS33")),

    ("user_dip_btn", 0, Pins("N14"),  IOStandard("LVCMOS33")),
    ("user_dip_btn", 1, Pins("M14"),  IOStandard("LVCMOS33")),
    ("user_dip_btn", 2, Pins("M16"),  IOStandard("LVCMOS33")),
    ("user_dip_btn", 3, Pins("M15"),  IOStandard("LVCMOS33")),
    ("user_dip_btn", 4, Pins("N15"), IOStandard("LVCMOS33")),
    ("user_dip_btn", 5, Pins("N16"), IOStandard("LVCMOS33")),
    ("user_dip_btn", 6, Pins("M17"), IOStandard("LVCMOS33")),
    ("user_dip_btn", 7, Pins("M18"), IOStandard("LVCMOS33")),

    ("spiflash", 0, # clock needs to be accessed through USRMCLK
        Subsignal("cs_n", Pins("E13")),
        Subsignal("mosi", Pins("D13")),
        Subsignal("miso", Pins("D15")),
        Subsignal("wp",   Pins("D14")),
        Subsignal("hold", Pins("D16")),
        IOStandard("LVCMOS33"),
    ),

    ("spiflash4x", 0, # clock needs to be accessed through USRMCLK
        Subsignal("cs_n", Pins("E13")),
        Subsignal("dq",   Pins("D13 D15 D14 D16")),
        IOStandard("LVCMOS33")
    )

]


# Connectors ---------------------------------------------------------------------------------------

_connectors = [
   ("X3",
        "None",  # (no pin 0)
        "None",  #  1 GND
        "None",  #  2 N/C
        "None",  #  3 +2V5
        "B19",   #  4 EXPCON_IO29
        "B12",   #  5 EXPCON_IO30
        "B9",    #  6 EXPCON_IO31
        "E6",    #  7 EXPCON_IO32
        "D6",    #  8 EXPCON_IO33
        "E7",    #  9 EXPCON_IO34
        "D7",    # 10 EXPCON_IO35
        "B11",   # 11 EXPCON_IO36
        "B6",    # 12 EXPCON_IO37
        "E9",    # 13 EXPCON_IO38
        "D9",    # 14 EXPCON_IO39
        "B8",    # 15 EXPCON_IO40
        "C8",    # 16 EXPCON_IO41
        "D8",    # 17 EXPCON_IO42
        "E8",    # 18 EXPCON_IO43
        "C7",    # 19 EXPCON_IO44
        "C6",    # 20 EXPCON_IO45
        "None",  # 21 +5V
        "None",  # 22 GND
        "None",  # 23 +2V5
        "None",  # 24 GND
        "None",  # 25 +3V3
        "None",  # 26 GND
        "None",  # 27 +3V3
        "None",  # 28 GND
        "None",  # 29 EXPCON_OSC
        "None",  # 30 GND
        "None",  # 31 EXPCON_CLKIN
        "None",  # 32 GND
        "None",  # 33 EXPCON_CLKOUT
        "None",  # 34 GND
        "None",  # 35 +3V3
        "None",  # 36 GND
        "None",  # 37 +3V3
        "None",  # 38 GND
        "None",  # 39 +3V3
        "None",  # 40 GND
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticePlatform):
    default_clk_name   = "clk125"
    default_clk_period = 1e9/125e6

    def __init__(self, device="LIFCL", **kwargs):
        assert device in ["LIFCL"]
        LatticePlatform.__init__(self, device + "-40-9BG400C", _io, _connectors, toolchain="radiant", **kwargs)

    def create_programmer(self):
        return OpenOCDJTAGProgrammer("openocd_versa_ecp5.cfg")

    def do_finalize(self, fragment):
        self.add_period_constraint(self.lookup_request("clk125", loose=True), 1e9/125e6)

