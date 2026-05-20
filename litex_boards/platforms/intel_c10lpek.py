# This file is Copyright (c) 2019 Antti Lukats <antti.lukats@gmail.com>
# This file is Copyright (c) 2014-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# License: BSD

from litex.build.generic_platform import *
from litex.build.altera import AlteraPlatform
from litex.build.altera.programmer import USBBlaster

# IOs ----------------------------------------------------------------------------------------------

_io = [
    ("clk50", 0, Pins("E1"), IOStandard("3.3-V LVTTL")),

    ("user_led", 0, Pins("L14"), IOStandard("3.3-V LVTTL")),
    ("user_led", 1, Pins("K15"), IOStandard("3.3-V LVTTL")),
    ("user_led", 2, Pins("J14"), IOStandard("3.3-V LVTTL")),
    ("user_led", 3, Pins("J13"), IOStandard("3.3-V LVTTL")),

#    ("cpu_reset", 0, Pins("E2"), IOStandard("3.3-V LVTTL")), # GND

    ("cpu_reset", 0, Pins("E15"), IOStandard("3.3-V LVTTL")), # PB0 low active !

    ("sw", 0, Pins("M16"), IOStandard("3.3-V LVTTL")), # DIP 0
    ("sw", 1, Pins("A8"), IOStandard("3.3-V LVTTL")),
    ("sw", 2, Pins("A9"), IOStandard("3.3-V LVTTL")),

    # no usb serial on the EK board! 
    ("serial", 0,
        Subsignal("tx", Pins("L13"), IOStandard("3.3-V LVTTL")), # GPIO 0
        Subsignal("rx", Pins("L16"), IOStandard("3.3-V LVTTL"))  # GPIO 1
    ),
 
    ("epcs", 0,
        Subsignal("data0", Pins("H2")),
        Subsignal("dclk", Pins("H1")),
        Subsignal("ncs0", Pins("D2")),
        Subsignal("asd0", Pins("C1")),
        IOStandard("3.3-V LVTTL")
    ),

    ("hyperram", 0,
        Subsignal("clk", Pins("P14")), # P14 R14
        Subsignal("clk_n", Pins("R14")), # P14 R14
        Subsignal("rst_n", Pins("N9")),
        Subsignal("dq", Pins("T12 T13 T11 R10 T10 R11 R12 R13")),
        Subsignal("cs0_n", Pins("P9 N12")), # RAM, Flash
        Subsignal("rwds", Pins("T14")),
        IOStandard("1.8 V")
    ),


#    ("i2c", 0,
#        Subsignal("sclk", Pins("F2")),
#        Subsignal("sdat", Pins("F1")),
#        IOStandard("3.3-V LVTTL")
#    ),


#    ("gpio_leds", 0,
#        Pins("AB10 AA10 AA9"),
#        IOStandard("3.3-V LVTTL")
#    ),


    #ETH 
#    ("eth_clocks", 0,
#        Subsignal("tx", Pins("")),
#        Subsignal("rx", Pins("")),
#        IOStandard("3.3-V LVTTL"),
#    ),
#    ("eth", 0,
#        Subsignal("rst_n", Pins("")),
#        Subsignal("mdio", Pins("")),
#        Subsignal("mdc", Pins("")),
#        Subsignal("rx_dv", Pins("")),
#        Subsignal("rx_er", Pins("")),
#        Subsignal("rx_data", Pins("")),
#        Subsignal("tx_en", Pins("")),
#        Subsignal("tx_data", Pins("")),
#        Subsignal("col", Pins("")),
#        Subsignal("crs", Pins("")),
#        IOStandard("3.3-V LVTTL"),
#    ),


]

# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name = "clk50"
    default_clk_period = 20

    def __init__(self):
        AlteraPlatform.__init__(self, "10CL025YU256I7G", _io)
        self.add_platform_command("set_global_assignment -name FAMILY \"Cyclone 10 LP\"")

    def create_programmer(self):
        return USBBlaster()
