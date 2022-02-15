#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Derek Mulcahy <derekmulcahy@gmail.com>
# Copyright (c) 2019-2020 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform, VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst - FIXME: A placeholder for an external clock
    ("clk100", 0, Pins("H16"), IOStandard("LVCMOS33")),

    # Leds - FIXME: A placeholder for an external LED
    ("user_led", 0, Pins("G14"), IOStandard("LVCMOS33")),

    # UART - FIXME: A placeholder for an external UART
    ("serial", 0,
        Subsignal("tx", Pins("D19")),
        Subsignal("rx", Pins("D20")),
        IOStandard("LVCMOS33"),
    ),

    # PS7
    ("ps7_clk",   0, Pins(1)),
    ("ps7_porb",  0, Pins(1)),
    ("ps7_srstb", 0, Pins(1)),
    ("ps7_mio",   0, Pins(54)),
    ("ps7_ddram", 0,
        Subsignal("addr",    Pins(15)),
        Subsignal("ba",      Pins(3)),
        Subsignal("cas_n",   Pins(1)),
        Subsignal("ck_n",    Pins(1)),
        Subsignal("ck_p",    Pins(1)),
        Subsignal("cke",     Pins(1)),
        Subsignal("cs_n",    Pins(1)),
        Subsignal("dm",      Pins(4)),
        Subsignal("dq",      Pins(32)),
        Subsignal("dqs_n",   Pins(4)),
        Subsignal("dqs_p",   Pins(4)),
        Subsignal("odt",     Pins(1)),
        Subsignal("ras_n",   Pins(1)),
        Subsignal("reset_n", Pins(1)),
        Subsignal("we_n",    Pins(1)),
        Subsignal("vrn",     Pins(1)),
        Subsignal("vrp",     Pins(1)),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("ja1", "- - - G14 E18 D20 E19 D19 - - F16 B20 F17 C20 - - E17 A20 D18 B19 - - F19 G20 F20 G19 - - J20 G18 H20 G17 - - J18 H17 H18 H16 - -"),
    ("ja2", "- - - J15 L14 J16 L15 K16 - - M14 G15 M15 H15 - - N15 J14 N16 K14 - - L19 J19 L20 K19 - - M17 M20 M18 M19 - - L16 K18 L17 K17 - -"),
    ("jb1", "- - - T19 T11 U12 T10 T12 - - P14 W13 R14 V12 - - U13 T14 V13 T14 - - T16 Y17 U17 Y16 - - W14 W15 Y14 V15 - - U14 U19 U15 U18 - -"),
    ("jb2", "- - - R19 N17 P16 P18 P15 - - T17 R17 R18 R16 - - V17 W19 V18 W18 - - T20 W16 U20 V16 - - V20 Y19 W20 Y18 - - N20 P19 P20 N18 - -"),
    ("jc1", "- - - V5  U7  U10 V7  T9  - - T5  Y13 U5  Y12 - - V11 W6  V10 V6  - - V8  Y11 W8  W11 - - U9  W9  U8  W10 - - Y9  Y6  Y8  Y7  - -"),
    # ("xadc", "N15 L14 K16 K14 N16 L15 J16 J14"),
    # ("mrcc", "H17 H16 K18 K17 U19 U18 P19 N18 Y6 Y7"),
    # ("srcc", "J18 H18 L16 L17 U14 U15 N20 P20 Y9 Y8"),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    # The clock speed depends on the PS7 PLL configuration for the FCLK_CLK0 signal.
    default_clk_name   = "clk100"
    default_clk_freq   = 100e6

    def __init__(self, variant="z7-10", toolchain="vivado"):
        device = {
            "z7-10": "xc7z010-clg400-1",
            "z7-20": "xc7z020-clg400-3"
        }[variant]
        XilinxPlatform.__init__(self, device, _io,  _connectors, toolchain=toolchain)
        self.default_clk_period = 1e9 / self.default_clk_freq
        self.toolchain.bitstream_commands = [
            "set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]"
        ]

    def create_programmer(self):
        return VivadoProgrammer(flash_part="n25q128a")

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request(self.default_clk_name, loose=True), self.default_clk_period)
