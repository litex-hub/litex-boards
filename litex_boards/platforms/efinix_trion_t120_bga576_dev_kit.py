#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Franck Jullien <franck.jullien@collshade.fr>
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.efinix.platform import EfinixPlatform
from litex.build.efinix import EfinixProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk
    ("clk40", 0, Pins("P19"), IOStandard("3.3_V_LVTTL_/_LVCMOS")),
    ("clk50", 0, Pins("AA8"), IOStandard("3.3_V_LVTTL_/_LVCMOS")),
    ("clk20", 0, Pins("AA9"), IOStandard("3.3_V_LVTTL_/_LVCMOS")),
    ("clk74_25", 0, Pins("J9"), IOStandard("3.3_V_LVTTL_/_LVCMOS")),

    # Leds
    ("user_led", 0, Pins("AB16"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=3")),
    ("user_led", 1, Pins("AA16"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=3")),
    ("user_led", 2, Pins("AA15"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=3")),
    ("user_led", 3, Pins("Y15"),  IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=3")),
    ("user_led", 4, Pins("Y16"),  IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=3")),
    ("user_led", 5, Pins("W16"),  IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=3")),
    ("user_led", 6, Pins("AD16"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=3")),
    ("user_led", 7, Pins("AC16"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=3")),

    # Buttons
    ("user_btn", 0, Pins("AD15"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("WEAK_PULLUP")),
    ("user_btn", 1, Pins("AC15"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("WEAK_PULLUP")),
    ("user_btn", 2, Pins("W15"),  IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("WEAK_PULLUP")),
    ("user_btn", 3, Pins("V15"),  IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("WEAK_PULLUP")),

    # Switches
    ("user_sw", 0, Pins("U16"),  IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("WEAK_PULLUP")),
    ("user_sw", 1, Pins("T16"),  IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("WEAK_PULLUP")),
    ("user_sw", 2, Pins("T15"),  IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("WEAK_PULLUP")),
    ("user_sw", 3, Pins("U15"),  IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("WEAK_PULLUP")),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("R23")),
        Subsignal("clk",  Pins("P22")),
        Subsignal("mosi", Pins("N24")),
        Subsignal("miso", Pins("N23")),
        #Subsignal("wp",   Pins("R19")),
        #Subsignal("hold", Pins("R17")),
        IOStandard("3.3_V_LVTTL_/_LVCMOS")
    ),

    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("R23")),
        Subsignal("clk",  Pins("P22")),
        Subsignal("dq",   Pins("N24 N23 R19 R17")),
        IOStandard("3.3_V_LVTTL_/_LVCMOS")
    ),

    # RGMII Ethernet
    ("eth_clocks", 0,
        Subsignal("tx", Pins("L16")),
        Subsignal("rx", Pins("M23")),
        IOStandard("3.3_V_LVTTL_/_LVCMOS")
    ),

    ("eth", 0,
        Subsignal("rx_ctl",  Pins("F24")),
        Subsignal("rx_data", Pins("J20 K20 J19 H20")),
        Subsignal("tx_ctl",  Pins("G24")),
        Subsignal("tx_data", Pins("L23 L22 K21 K19")),
        Subsignal("rst_n",   Pins("F21")),
        Subsignal("mdc",     Pins("G21")),
        Subsignal("mdio",    Pins("G19")),
        IOStandard("3.3_V_LVTTL_/_LVCMOS")
    ),

    ("eth_clocks", 1,
        Subsignal("tx", Pins("M18")),
        Subsignal("rx", Pins("M24")),
        IOStandard("3.3_V_LVTTL_/_LVCMOS")
    ),

    ("eth", 1,
        Subsignal("rx_ctl",  Pins("D23")),
        Subsignal("rx_data", Pins("M8 L7 M7 N6")),
        Subsignal("tx_ctl",  Pins("E24")),
        Subsignal("tx_data", Pins("N7 N9 N8 N5")),
        Subsignal("rst_n",   Pins("E23")),
        Subsignal("mdc",     Pins("E22")),
        Subsignal("mdio",    Pins("D24")),
        IOStandard("3.3_V_LVTTL_/_LVCMOS")
    ),

    # DRAM.
    ("dram_pll_refclk", 0, Pins("AA8"), IOStandard("3.3_V_LVTTL_/_LVCMOS")),

    # MIPI
    ("mipi_refclk", 0, Pins("G9"), IOStandard("3.3_V_LVTTL_/_LVCMOS")),
]

# Bank voltage ---------------------------------------------------------------------------------------

_bank_info = [
            ("1A",          "3.3 V LVTTL / LVCMOS"),
            ("1B_1C",       "3.3 V LVTTL / LVCMOS"),
            ("1D_1E_1F_1G", "3.3 V LVTTL / LVCMOS"),
            ("2A",          "3.3 V LVTTL / LVCMOS"),
            ("2B",          "3.3 V LVTTL / LVCMOS"),
            ("2C",          "3.3 V LVTTL / LVCMOS"),
            ("2D",          "3.3 V LVTTL / LVCMOS"),
            ("2E",          "3.3 V LVTTL / LVCMOS"),
            ("2F",          "3.3 V LVTTL / LVCMOS"),
            ("3D_TR_BR",    "3.3 V LVTTL / LVCMOS"),
            ("4A",          "3.3 V LVTTL / LVCMOS"),
            ("4B",          "3.3 V LVTTL / LVCMOS"),
            ("4C",          "3.3 V LVTTL / LVCMOS"),
            ("4D",          "3.3 V LVTTL / LVCMOS"),
            ("4E",          "3.3 V LVTTL / LVCMOS"),
            ("4F",          "3.3 V LVTTL / LVCMOS"),
            ("BL",          "1.2 V"),
            ("TL",          "1.2 V"),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("pmod_a", " T12  V11  Y12  Y10  U12  U11  W12  Y11"),
    ("pmod_b", "AD11 AD10 AC10  W10 AA11 AC11 AA10  V10"),
    ("pmod_c", " A11  D11  J11  G10  B11  E11  H11  F10"),
    ("pmod_d", " D10  A10   A9   D9  E10  B10   B9   C9"),
    ("pmod_e", " C24  B23  A20  A22  B24  A23  B20  B22"),
    ("pmod_f", " V21  V20 AD20 AD19  U21  V19 AC20 AC19"),
]

# PMODS --------------------------------------------------------------------------------------------

def raw_pmod_io(pmod):
    return [(pmod, 0, Pins(" ".join([f"{pmod}:{i:d}" for i in range(8)])), IOStandard("3.3_V_LVTTL_/_LVCMOS"))]

def usb_pmod_io(pmod):
    return [
        # USB-UART PMOD: https://store.digilentinc.com/pmod-usbuart-usb-to-uart-interface/
        ("usb_uart", 0,
            Subsignal("tx", Pins(f"{pmod}:1")),
            Subsignal("rx", Pins(f"{pmod}:2")),
            IOStandard("3.3_V_LVTTL_/_LVCMOS")
        ),
    ]

# Platform -----------------------------------------------------------------------------------------

class Platform(EfinixPlatform):
    default_clk_name   = "clk40"
    default_clk_period = 1e9/40e6

    def __init__(self, toolchain="efinity"):
        EfinixPlatform.__init__(self, "T120F576I4", _io, _connectors, iobank_info=_bank_info, toolchain=toolchain)

    def create_programmer(self):
        return EfinixProgrammer()

    def do_finalize(self, fragment):
        EfinixPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk40", loose=True), 1e9/40e6)
