#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2018 William D. Jones <thor0505@comcast.net>
# Copyright (c) 2020 Staf Verhaegen <staf@fibraservi.eu>
# Copyright (c) 2021 Michael T. Mayers <michael@tweakoz.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import Pins, Subsignal, IOStandard, Misc
from litex.build.xilinx import Xilinx7SeriesPlatform

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk50", 0, Pins("N14"), IOStandard("LVCMOS33")),
    ("clk_en", 0, Pins("H16"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led", 0, Pins("M1"),  IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("A14"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("A13"), IOStandard("LVCMOS33")),

    # FPGA control.
    ("fpga_done", 0, Pins("H10"), IOStandard("LVCMOS33")),
    ("fpga_prog", 0, Pins("L9"),  IOStandard("LVCMOS33")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("N11")), # BDBUS1
        Subsignal("rx", Pins("E11")), # BDBUS0
        IOStandard("LVCMOS33")
    ),

    # FPGA Direct I/O.
    ("dio", 0,
        Pins(
            "C12 C11 D9 A9 A8 A10 B9 B6 B5 E12"
        ),
        IOStandard("LVCMOS33"),
    ),

    # 5V tolerant level-shifted I/O.
    ("io", 0,
        Pins(
            "G1 G2 F2 E1 E2 C2 B2 B1 A2 H2",
            "B10 C8 C9 T13 R12 P11 T2 T4 T5 T7",
            "K5 A3 C6 D4 F5 D8 P1 C7 M2 N1",
            "C1 D1 L2 G5 H5 H1 K1 K2 J1 J3"),
        IOStandard("LVCMOS33"),
    ),

    # DAC
    ("dac", 0,
        Subsignal("mosi", Pins("K12")),
        Subsignal("ldac", Pins("P14")),
        Subsignal("clk",  Pins("N13")),
        Subsignal("cs_n", Pins("K16")),
        IOStandard("LVCMOS33"),
    ),

    # ADC
    ("adc", 0,
        Subsignal("miso", Pins("G15")),
        Subsignal("mosi", Pins("J16")),
        Subsignal("clk",  Pins("P10")),
        Subsignal("cs_n", Pins("K15")),
        IOStandard("LVCMOS33"),
    ),

    # XADC
    ("xadc", 0,
        Subsignal("vp",     Pins("H8")),
        Subsignal("vn",     Pins("J7")),
        Subsignal("vref_p", Pins("J8")),
        Subsignal("vref_n", Pins("H7")),
        IOStandard("LVCMOS33"),
    ),

    # SRAM
    ("issiram", 0,
        Subsignal("addr", Pins(
            "M4 N3 N4 P3 M5 E5 D5 D3",
            "B7 B4 J4 H4 H3 G4 E6 A7",
            "A5 A4 C4"),
            IOStandard("LVCMOS33")),
        Subsignal("data", Pins(
            "L5 L3 L4 R2 F3 F4 E3 D6"),
            IOStandard("LVCMOS33")),
        Subsignal("wen", Pins("R1"), IOStandard("LVCMOS33")),
        Subsignal("cen", Pins("M6"), IOStandard("LVCMOS33")),
        Misc("SLEW=FAST"),
    ),

    # RMII Ethernet
    ("eth_clocks", 0,
        Subsignal("ref_clk", Pins("D13")),
        IOStandard("LVCMOS33"),
    ),
    ("eth", 0,
        Subsignal("tx_data", Pins("C14 B14")),
        Subsignal("tx_en",   Pins("B16")),
        Subsignal("rx_data", Pins("H12 H13")),
        Subsignal("crs_dv",  Pins("E13")),
        Subsignal("rx_er",   Pins("L13")),
        Subsignal("mdc",     Pins("D14")),
        Subsignal("mdio",    Pins("D16")),
        Subsignal("int_n",   Pins("G11")),
        Subsignal("rst_n",   Pins("F15")),
        Subsignal("led",     Pins("A12 A15")),
        IOStandard("LVCMOS33"),
    ),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("L12")),
        Subsignal("clk",  Pins("E8")),
        Subsignal("mosi", Pins("J13")),
        Subsignal("miso", Pins("J14"), Misc("PULLUP")),
        IOStandard("LVCMOS33"),
        Misc("SLEW=FAST"),
    ),

    # Wi-Fi module header.
    ("wifi", 0,
        Subsignal("rx",    Pins("R6")),
        Subsignal("tx",    Pins("R7")),
        Subsignal("reset", Pins("R5")),
        Subsignal("en",    Pins("R8")),
        IOStandard("LVCMOS33"),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("DIO", "C12 C11 D9 A9 A8 A10 B9 B6 B5 E12"),
    ("IO",
        "G1 G2 F2 E1 E2 C2 B2 B1 A2 H2 "
        "B10 C8 C9 T13 R12 P11 T2 T4 T5 T7 "
        "K5 A3 C6 D4 F5 D8 P1 C7 M2 N1 "
        "C1 D1 L2 G5 H5 H1 K1 K2 J1 J3"),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self, toolchain="vivado"):
        Xilinx7SeriesPlatform.__init__(self, "xc7a35tftg256-1", _io, _connectors, toolchain=toolchain)

    def do_finalize(self,fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), self.default_clk_period)
