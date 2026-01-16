#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2018 William D. Jones <thor0505@comcast.net>
# Copyright (c) 2020 Staf Verhaegen <staf@fibraservi.eu>
# Copyright (c) 2021 Michael T. Mayers <michael@tweakoz.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import Pins, Subsignal, IOStandard, Misc
from litex.build.xilinx import Xilinx7SeriesPlatform
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
        Subsignal("oe",  Pins("P19"), IOStandard("LVCMOS33")),
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

_connectors = [
    ("pmoda", "G17 G19 N18 L18 H17 H19 J19 K18"),
    # pin 15: XADC, pin 16: XADC, pin 24: VU
    ("j1", "M3 L3 A16 K3 C15 H1 A15 B15 A14 J3 J1 K2 L1 L2 - - M1 N3 P3 M2 N1 N2 P1 -"),
    # pin 25: GND
    ("j2", "- R3 T3 R2 T1 T2 U1 W2 V2 W3 V3 W5 V4 U4 V5 W4 U5 U2 W6 U3 U7 W7 U8 V8")
]

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk12"
    default_clk_period = 1e9/12e6

    def __init__(self, variant="a7-35", toolchain="vivado"):
        device = {
            "a7-35": "xc7a35tcpg236-1"
        }[variant]
        Xilinx7SeriesPlatform.__init__(self, device, _io, _connectors, toolchain=toolchain)
        self.toolchain.additional_commands = [
            (
                "write_cfgmem -force -format bin -interface spix4 -size 16 -loadbit "
                + '"up 0x0 {build_name}.bit" -file {build_name}.bin'
            )
        ]
        self.add_platform_command("set_property CONFIG_VOLTAGE 3.3 [current_design]")
        self.add_platform_command("set_property CFGBVS VCCO [current_design]")
        self.add_platform_command("set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]")
        self.add_platform_command("set_property BITSTREAM.CONFIG.CONFIGRATE 50 [current_design]")
        self.add_platform_command("set_property INTERNAL_VREF 0.75 [get_iobanks 34]")

    def create_programmer(self):
        bscan_spi = "bscan_spi_xc7a15t.bit" if "xc7a15t" in self.device else "bscan_spi_xc7a35t.bit"
        return OpenOCD("openocd_xc7_ft2232.cfg", bscan_spi)

    def do_finalize(self,fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk12", loose=True), self.default_clk_period)
