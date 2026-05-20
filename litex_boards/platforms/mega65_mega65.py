# This file is Copyright (c) 2019 Antti Lukats <antti.lukats@gmail.com>
# This file is Copyright (c) 2015-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# License: BSD

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform, VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    ("user_led", 0, Pins("U22"), IOStandard("LVCMOS33")), # LED4
#    ("user_led", 1, Pins("E26"), IOStandard("LVCMOS33")),

# 
    ("clk100", 0, Pins("V13"), IOStandard("LVCMOS33")),
# 
    ("cpu_reset", 0, Pins("L15"), IOStandard("LVCMOS33")),
# Debug UART
    ("serial", 0,
        Subsignal("tx", Pins("L13")),
        Subsignal("rx", Pins("L14")),
        IOStandard("LVCMOS33")
    ),

    ("hyperram", 0,
        Subsignal("clk", Pins("D22")),
        Subsignal("rstn_n", Pins("B22")),
        Subsignal("dq", Pins("A21 D21 C20 A20 B20 A19 E21 E22")),
        Subsignal("cs_n", Pins("C22")),
        Subsignal("rwds", Pins("B21")),
        IOStandard("LVCMOS33")
    ),

    ("eth_clocks", 0,
        Subsignal("ref_clk", Pins("L4")),
        IOStandard("LVCMOS33"),
    ),

    ("eth", 0,
        Subsignal("rst_n", Pins("K6")),
        Subsignal("rx_data", Pins("P4 L1")),
        Subsignal("crs_dv", Pins("K4")),
        Subsignal("tx_en", Pins("J4")),
        Subsignal("tx_data", Pins("L3 K3")),
        Subsignal("mdc", Pins("J6")),
        Subsignal("mdio", Pins("L5")),
        Subsignal("rx_er", Pins("M6")),
#        Subsignal("int_n", Pins("")),
        IOStandard("LVCMOS33")
     ),


#   ("eth_clocks", 0,
#        Subsignal("tx", Pins("")),
#        Subsignal("rx", Pins("")),
#        IOStandard("LVCMOS33"),
#    ),
#    ("eth", 0,
#        Subsignal("rst_n", Pins("K6")),
#        Subsignal("mdio", Pins("L5")),
#        Subsignal("mdc", Pins("J6")),
#        Subsignal("rx_dv", Pins("")),
#        Subsignal("rx_er", Pins("")),
#        Subsignal("rx_data", Pins("")),
#        Subsignal("tx_en", Pins("")),
#        Subsignal("tx_data", Pins("")),
#        Subsignal("col", Pins("")),
#        Subsignal("crs", Pins("")),
#        IOStandard("LVCMOS33"),
#    ),



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
    ("porta", "*"),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name = "clk100"
    default_clk_period = 10.0

    def __init__(self, variant="a7-100-1c"):
        device = {
            "a7-100-1c": "xc7a100tfgg484-1"
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
