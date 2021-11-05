#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# https://www.crowdsupply.com/fairwaves/xtrx

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Leds.
    ("user_led", 0, Pins("N18"),  IOStandard("LVCMOS25")),

    # PCIe.
    ("pcie_x1", 0,
        Subsignal("rst_n", Pins("T3"), IOStandard("LVCMOS25"), Misc("PULLUP=TRUE")),
        Subsignal("clk_p", Pins("B8")),
        Subsignal("clk_n", Pins("A8")),
        Subsignal("rx_p",  Pins("B10")),
        Subsignal("rx_n",  Pins("A10")),
        Subsignal("tx_p",  Pins("B6")),
        Subsignal("tx_n",  Pins("A6")),
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "clk60"
    default_clk_period = 1e9/60e6

    def __init__(self):
        XilinxPlatform.__init__(self, "xc7a50tcpg236-2", _io, toolchain="vivado")

        self.toolchain.bitstream_commands = [
            "set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]",
            "set_property BITSTREAM.CONFIG.CONFIGRATE 16 [current_design]",
            "set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]"
        ]
        self.toolchain.additional_commands = \
            ["write_cfgmem -force -format bin -interface spix4 -size 16 "
             "-loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"]

    def create_programmer(self):
        return OpenOCD("openocd_xc7_ft232.cfg", "bscan_spi_xc7a50t.bit")

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
