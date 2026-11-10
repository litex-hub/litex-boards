#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# AMD/Xilinx Kria KR260 Robotics Starter Kit (K26 SOM, XCK26).
#
# PL pinout from AMD's board files (XilinxBoardStore kr260_carrier 1.0 + kr260_som 1.1 part0_pins),
# cross-checked with the KR260 platforms' XDCs (kria-vitis-platforms: kr260_tsn_rs485pmod,
# kr260_pmod_gps). The SFP+ cage's data lanes are not described there and are not included.

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxUSPPlatform, VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clks (25 MHz from the carrier's Si5332, also the clocks of the PL GEMs' PHYs).
    ("clk25", 0, Pins("C3"), IOStandard("LVCMOS18")), # HPA_CLK0P_CLK.
    ("clk25", 1, Pins("L3"), IOStandard("LVCMOS18")), # HPB_CLK0P_CLK.

    # Fan (active low enable).
    ("fan_en_b", 0, Pins("A12"), IOStandard("LVCMOS33")),

    # Leds.
    ("user_led", 0, Pins("F8"), IOStandard("LVCMOS18")),
    ("user_led", 1, Pins("E8"), IOStandard("LVCMOS18")),
    ("gem_led",  0, Pins("E4 E3 C1"), IOStandard("LVCMOS18")), # PL GEM2.
    ("gem_led",  1, Pins("R7 T7 L1"), IOStandard("LVCMOS18")), # PL GEM3.
    ("sfp_led",  0, Pins("G8 F7"),    IOStandard("LVCMOS18")),

    # I2C.
    ("i2c", 0, # Main (carrier I2C).
        Subsignal("scl", Pins("F10")),
        Subsignal("sda", Pins("G11")),
        IOStandard("LVCMOS33")
    ),
    ("sfp_i2c", 0,
        Subsignal("scl", Pins("AB11")),
        Subsignal("sda", Pins("AC11")),
        IOStandard("LVCMOS33")
    ),

    # RGMII Ethernet (0: PL GEM2, 1: PL GEM3).
    ("eth_clocks", 0,
        Subsignal("tx", Pins("A2")),
        Subsignal("rx", Pins("D4")),
        IOStandard("LVCMOS18")
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("B1")),
        Subsignal("mdio",    Pins("F3")),
        Subsignal("mdc",     Pins("G3")),
        Subsignal("rx_ctl",  Pins("A4")),
        Subsignal("rx_data", Pins("A1 B3 A3 B4")),
        Subsignal("tx_ctl",  Pins("F1")),
        Subsignal("tx_data", Pins("E1 D1 F2 E2")),
        IOStandard("LVCMOS18")
    ),
    ("eth_clocks", 1,
        Subsignal("tx", Pins("J1")),
        Subsignal("rx", Pins("K4")),
        IOStandard("LVCMOS18")
    ),
    ("eth", 1,
        Subsignal("rst_n",   Pins("K1")),
        Subsignal("mdio",    Pins("T8")),
        Subsignal("mdc",     Pins("R8")),
        Subsignal("rx_ctl",  Pins("H3")),
        Subsignal("rx_data", Pins("H1 K2 J2 H4")),
        Subsignal("tx_ctl",  Pins("Y8")),
        Subsignal("tx_data", Pins("U9 V9 U8 V8")),
        IOStandard("LVCMOS18")
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    # PMODs (3.3V), pins 1-4 then 7-10.
    ("pmod0", "H12 E10 D10 C11 B10 E12 D11 B11"),         # PMOD1.
    ("pmod1", "J11 J10 K13 K12 H11 G10 F12 F11"),         # PMOD2.
    ("pmod2", "AE12 AF12 AG10 AH10 AF11 AG11 AH12 AH11"), # PMOD3.
    ("pmod3", "AC12 AD12 AE10 AF10 AD11 AD10 AA11 AA10"), # PMOD4.
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxUSPPlatform):
    default_clk_name   = "clk25"
    default_clk_period = 1e9/25e6

    def __init__(self, toolchain="vivado"):
        XilinxUSPPlatform.__init__(self, "xck26-sfvc784-2lv-c", _io, _connectors, toolchain=toolchain)
        self.toolchain.bitstream_commands = \
            ["set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]", ]

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment, *args, **kwargs):
        XilinxUSPPlatform.do_finalize(self, fragment, *args, **kwargs)
        self.add_period_constraint(self.lookup_request("clk25", 0, loose=True), 1e9/25e6)
        self.add_period_constraint(self.lookup_request("clk25", 1, loose=True), 1e9/25e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:rx", 0, loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:rx", 1, loose=True), 1e9/125e6)
