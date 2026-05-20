# This file is Copyright (c) 2019 Antti Lukats <antti.lukats@gmail.com>
# This file is Copyright (c) 2015-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# License: BSD

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform, VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    ("user_led_red", 0, Pins("D14"), IOStandard("LVCMOS33")),
    ("user_led_green", 0, Pins("C14"), IOStandard("LVCMOS33")),
#J1
    ("user_sw", 0, Pins("D3"), IOStandard("LVCMOS33")),
#J2
    ("user_btn", 0, Pins("A4"), IOStandard("LVCMOS33")),
#Note we need special constraint for clock or it will fail
    ("clk100", 0, Pins("L5"), IOStandard("LVCMOS33")),
#there is no dedicated reset? at least we need pull-down?
#seems to work as is also
    ("cpu_reset", 0, Pins("A10"), IOStandard("LVCMOS33")),
#
    ("serial", 0,
        Subsignal("tx", Pins("A5")),
        Subsignal("rx", Pins("A12")),
        IOStandard("LVCMOS33")
    ),

    ("hyperram", 0,
        Subsignal("clk", Pins("N1")),
        Subsignal("rst_n", Pins("P3")),
        Subsignal("dq", Pins("P11 P12 N4 P10 P5 N10 N11 P13")),
        Subsignal("cs0_n", Pins("P2")),
        Subsignal("rwds", Pins("P4")),
        IOStandard("LVCMOS33")
    ),


#    ("spiflash4x", 0,
#        Subsignal("cs_n", Pins("L13")),
#        Subsignal("clk", Pins("L16")),
#        Subsignal("dq", Pins("K17", "K18", "L14", "M14")),
#        IOStandard("LVCMOS33")
#    ),
#    ("spiflash", 0,
#        Subsignal("cs_n", Pins("L13")),
#        Subsignal("clk", Pins("L16")),
#        Subsignal("mosi", Pins("K17")),
#        Subsignal("miso", Pins("K18")),
#        Subsignal("wp", Pins("L14")),
#        Subsignal("hold", Pins("M14")),
#        IOStandard("LVCMOS33"),
#    ),

]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("porta", "C3 E4 C5 B3 A3 D4 C4 A2"),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name = "clk100"
    default_clk_period = 10.0

    def __init__(self, variant="s7-25"):
        device = {
            "s7-25": "xc7s25ftgb196-1"
        }[variant]
        XilinxPlatform.__init__(self, device, _io, _connectors, toolchain="vivado")
        self.toolchain.bitstream_commands = \
            ["set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]"]
        self.toolchain.additional_commands = \
            ["write_cfgmem -force -format bin -interface spix4 -size 16 "
             "-loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"]
# required as s7-mini has global clock on regular io pin
        self.add_platform_command("set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets clk100_IBUF]")
#fixme change spi flash type
    def create_programmer(self):
        return VivadoProgrammer(flash_part="n25q128-3.3v-spi-x1_x2_x4")
