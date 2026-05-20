# This file is Copyright (c) 2019 Antti Lukats <antti.lukats@gmail.com>
# This file is Copyright (c) 2018-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# License: BSD

from litex.build.generic_platform import *
from litex.build.microsemi import MicrosemiPlatform

# IOs ----------------------------------------------------------------------------------------------


_io = [
    ("clk12", 0, Pins("A2"), IOStandard("LVCMOS33")),

#    ("rst_n", 0, Pins("F5"), IOStandard("LVCMOS33")),

    ("user_led", 0, Pins("A3"), IOStandard("LVCMOS33")),

    ("user_btn", 0, Pins("A6"), IOStandard("LVCMOS33")),

    ("serial", 0,
        Subsignal("tx", Pins("A7")),
        Subsignal("rx", Pins("A5")),
        IOStandard("LVCMOS33")
    ),

#    ("spiflash4x", 0,
#        Subsignal("clk", Pins("J1")),
#        Subsignal("cs_n", Pins("H1")),
#        Subsignal("dq", Pins("F2 F1 M7 M8")),
#        IOStandard("LVCMOS25")
#    ),
#    ("spiflash", 0,
#        Subsignal("clk", Pins("J1")),
#        Subsignal("cs_n", Pins("H1")),
#        Subsignal("mosi", Pins("F2")),
#        Subsignal("miso", Pins("F1")),
#        Subsignal("wp", Pins("M7")),
#        Subsignal("hold", Pins("M8")),
#        IOStandard("LVCMOS25"),
#    ),

]

# Platform -----------------------------------------------------------------------------------------

class Platform(MicrosemiPlatform):
    default_clk_name = "clk12"
    default_clk_period = 83.0

    def __init__(self):
        MicrosemiPlatform.__init__(self, "MPF100T-FCVG484-1", _io)
