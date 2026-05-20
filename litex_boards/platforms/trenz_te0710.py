# This file is Copyright (c) 2019 Antti Lukats <antti.lukats@gmail.com>
# This file is Copyright (c) 2015-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# License: BSD

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform, VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    ("user_led", 0, Pins("L15"), IOStandard("LVCMOS33")), # LED4
#    ("user_led", 1, Pins("E26"), IOStandard("LVCMOS33")),

# P17
    ("clk100", 0, Pins("F4"), IOStandard("SSTL15")),
# 
    ("cpu_reset", 0, Pins("F5"), IOStandard("LVCMOS15")),
#
    ("serial", 0,
        Subsignal("tx", Pins("B8")),
        Subsignal("rx", Pins("A8")),
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
    ("porta", "H21 G21 L22 K21 H23 K22 J21 G24"),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name = "clk100"
    default_clk_period = 10.0

    def __init__(self, variant="a7-35-2c"):
        device = {
            "a7-35-2c": "xc7a35tcsg324-2",
            "a7-35-2i": "xc7a35tcsg324-2"
        }[variant]
        XilinxPlatform.__init__(self, device, _io, _connectors, toolchain="vivado")
        self.add_platform_command("""
set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
""")
        self.toolchain.bitstream_commands = \
            ["set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]"]
        self.toolchain.additional_commands = \
            ["write_cfgmem -force -format bin -interface spix4 -size 16 "
             "-loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"]
# required as s7-mini has global clock on regular io pin
#        self.add_platform_command("set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets clk100_IBUF]")
#fixme change spi flash type
    def create_programmer(self):
        return VivadoProgrammer(flash_part="n25q128-3.3v-spi-x1_x2_x4")
