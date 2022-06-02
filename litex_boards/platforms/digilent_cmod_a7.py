#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2018 William D. Jones <thor0505@comcast.net>
# Copyright (c) 2020 Staf Verhaegen <staf@fibraservi.eu>
# Copyright (c) 2021 Michael T. Mayers <michael@tweakoz.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import Pins, Subsignal, IOStandard, Misc
from litex.build.xilinx import XilinxPlatform
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk12", 0, Pins("L17"), IOStandard("LVCMOS33")),

    # Buttons
    ("cpu_reset", 0, Pins("A18"), IOStandard("LVCMOS33")),
    ("user_btn",  0, Pins("B18"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led", 0, Pins("A17"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("C16"), IOStandard("LVCMOS33")),

    ("rgb_led", 0,
        Subsignal("r", Pins("C17")),
        Subsignal("g", Pins("B16")),
        Subsignal("b", Pins("B17")),
        IOStandard("LVCMOS33"),
    ),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("J18")),
        Subsignal("rx", Pins("J17")),
        IOStandard("LVCMOS33")),

    # SRAM
    ("issiram", 0,
        Subsignal("addr", Pins(
            "M18 M19 K17 N17 P17 P18 R18 W19",
            "U19 V19 W18 T17 T18 U17 U18 V16",
            "W16 W17 V15"),
            IOStandard("LVCMOS33")),
        Subsignal("data", Pins(
            "W15 W13 W14 U15 U16 V13 V14 U14"),
            IOStandard("LVCMOS33")),
        Subsignal("wen", Pins("R19"), IOStandard("LVCMOS33")),
        Subsignal("cen", Pins("N19"), IOStandard("LVCMOS33")),
        Misc("SLEW=FAST"),
    ),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("K19")),
        Subsignal("clk",  Pins("E19")),
        Subsignal("mosi", Pins("D18")),
        Subsignal("miso", Pins("D19")),
        Subsignal("wp",   Pins("G18")),
        Subsignal("hold", Pins("F18")),
        IOStandard("LVCMOS33"),
    ),
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("K19")),
        Subsignal("clk",  Pins("E19")),
        Subsignal("dq",   Pins("D18 D19 G18 F18")),
        IOStandard("LVCMOS33")
    ),

]

# Connectors ---------------------------------------------------------------------------------------

_connectors = []

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "clk12"
    default_clk_period = 1e9/12e6

    def __init__(self, variant="a7-35", toolchain="vivado"):
        device = {
            "a7-35": "xc7a35tcpg236-1"
        }[variant]
        XilinxPlatform.__init__(self, device, _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        bscan_spi = "bscan_spi_xc7a15t.bit" if "xc7a15t" in self.device else "bscan_spi_xc7a35t.bit"
        return OpenOCD("openocd_xc7_ft2232.cfg", bscan_spi)

    def do_finalize(self,fragment):
        XilinxPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk12", loose=True), self.default_clk_period)
