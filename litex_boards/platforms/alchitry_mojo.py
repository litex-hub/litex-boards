#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Nathaniel Lewis <github@nrlewis.dev>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxSpartan6Platform

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk50", 0, Pins("P56"), IOStandard("LVCMOS33")),
    ("cpu_reset", 0, Pins("P38"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led", 0, Pins("P134"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("P133"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("P132"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("P131"), IOStandard("LVCMOS33")),
    ("user_led", 4, Pins("P127"), IOStandard("LVCMOS33")),
    ("user_led", 5, Pins("P126"), IOStandard("LVCMOS33")),
    ("user_led", 6, Pins("P124"), IOStandard("LVCMOS33")),
    ("user_led", 7, Pins("P123"), IOStandard("LVCMOS33")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("P59")),
        Subsignal("rx", Pins("P55")),
        IOStandard("LVCMOS33")
    ),

    # AVR signals
    ("tx_busy", 0, Pins("P39"), IOStandard("LVCMOS33")),
    ("cclk", 0, Pins("P70"), IOStandard("LVCMOS33")),
]

_hdmi_shield = [
    # SDRAM
    ("sdram_clock", 0, Pins("P29"), IOStandard("LVCMOS33"), Misc("SLEW=FAST")),
    ("sdram", 0,
        Subsignal("a", Pins("P101 P102 P104 P105 P5 P6 P7 P8 P9 P10 P88 P27 P26")),
        Subsignal("dq", Pins("P75 P78 P79 P80 P34 P35 P40 P41")),
        Subsignal("ba", Pins("P85 P87")),
        Subsignal("dm", Pins("P74")),
        Subsignal("ras_n", Pins("P83")),
        Subsignal("cas_n", Pins("P82")),
        Subsignal("we_n", Pins("P81")),
        Subsignal("cs_n", Pins("P84")),
        Subsignal("cke", Pins("P30")),
        IOStandard("LVCMOS33"),
        Misc("SLEW = FAST")
    ),

    # HDMI Out (HDMI 1)
    ("hdmi_out", 0,
        # TODO: do clock pins need "CLOCK_DEDICATED_ROUTE = FALSE" ?
        Subsignal("clk_p", Pins("P144")),
        Subsignal("clk_n", Pins("P143")),
        Subsignal("data0_p", Pins("P142")),
        Subsignal("data0_n", Pins("P141")),
        Subsignal("data1_p", Pins("P140")),
        Subsignal("data1_n", Pins("P139")),
        Subsignal("data2_p", Pins("P138")),
        Subsignal("data2_n", Pins("P137")),
        IOStandard("TMDS_33")
    ),

    # HDMI Out DDC Bus
    ("hdmi_out_sda", 0, Pins("P2"), IOStandard("LVCMOS33")),
    ("hdmi_out_scl", 0, Pins("P1"), IOStandard("LVCMOS33")),

    # HDMI In (HDMI 2)
    ("hdmi_in", 0,
        # TODO: do clock pins need "CLOCK_DEDICATED_ROUTE = FALSE" ?
        Subsignal("clk_p", Pins("P121")),
        Subsignal("clk_n", Pins("P120")),
        Subsignal("data0_p", Pins("P119")),
        Subsignal("data0_n", Pins("P118")),
        Subsignal("data1_p", Pins("P117")),
        Subsignal("data1_n", Pins("P116")),
        Subsignal("data2_p", Pins("P115")),
        Subsignal("data2_n", Pins("P114")),
        IOStandard("TMDS_33")
    ),

    # HDMI In DDC Bus
    ("hdmi_in_sda", 0, Pins("P111"), IOStandard("LVCMOS33")),
    ("hdmi_in_scl", 0, Pins("P112"), IOStandard("LVCMOS33")),
]

_sdram_shield = [
    # SDRAM
    ("sdram_clock", 0, Pins("P5"), IOStandard("LVCMOS33"), Misc("SLEW=FAST")),
    ("sdram", 0,
        Subsignal("a", Pins("P118 P119 P120 P121 P138 P139 P140 P141 P142 P143 P137 P144 P1")),
        Subsignal("dq", Pins("P101 P102 P104 P105 P7 P8 P9 P10")),
        Subsignal("ba", Pins("P116 P117")),
        Subsignal("dm", Pins("P6")),
        Subsignal("ras_n", Pins("P114")),
        Subsignal("cas_n", Pins("P112")),
        Subsignal("we_n", Pins("P111")),
        Subsignal("cs_n", Pins("P115")),
        Subsignal("cke", Pins("P2")),
        IOStandard("LVCMOS33"),
        Misc("SLEW = FAST")
    )
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxSpartan6Platform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self, toolchain="ise"):
        XilinxSpartan6Platform.__init__(self, "xc6slx9-2-tqg144", _io, toolchain=toolchain)
        self.toolchain.additional_commands = ["write_bitstream -force -bin_file {build_name}"]

    def do_finalize(self, fragment):
        XilinxSpartan6Platform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
