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
    ("clk25", 0, Pins("L17"), IOStandard("1.8_V_LVCMOS")),
    ("clk100", 0, Pins("U4"), IOStandard("3.3_V_LVCMOS")),

    # Serial
    ("serial", 0,
     Subsignal("tx", Pins("E9")),
     Subsignal("rx", Pins("E10")),
     IOStandard("3.3_V_LVTTL"), Misc("WEAK_PULLUP")
     ),

    # Buttons
    ("user_btn", 0, Pins("U19"), IOStandard("3.3_V_LVCMOS")),
]



# Bank voltage ---------------------------------------------------------------------------------------

_bank_info = [
            ("2A"      , "1.8 V LVCMOS"), # is_dyn_voltage="false" mode_sel_name="2A_MODE_SEL"/>
            ("2B"      , "1.8 V LVCMOS"), # is_dyn_voltage="false" mode_sel_name="2B_MODE_SEL"/>
            ("2C"      , "1.8 V LVCMOS"), # is_dyn_voltage="false" mode_sel_name="2C_MODE_SEL"/>
            ("2D"      , "1.8 V LVCMOS"), # is_dyn_voltage="false" mode_sel_name="2D_MODE_SEL"/>
            ("2E"      , "1.8 V LVCMOS"), # is_dyn_voltage="false" mode_sel_name="2E_MODE_SEL"/>
            ("4A_4B"   , "1.8 V LVCMOS"), # is_dyn_voltage="false" mode_sel_name="4A_4B_MODE_SEL"/>
            ("4C"      , "1.8 V LVCMOS"), # is_dyn_voltage="false" mode_sel_name="4C_MODE_SEL"/>
            ("4D"      , "1.8 V LVCMOS"), # is_dyn_voltage="false" mode_sel_name="4D_MODE_SEL"/>
            ("BL2_BL3" , "3.3 V LVCMOS"), # is_dyn_voltage="false">
            ("BR0"     , "3.3 V LVCMOS"), # is_dyn_voltage="false" mode_sel_name="BR0_MODE_SEL"/>
            ("BR3_BR4" , "3.3 V LVCMOS"), # is_dyn_voltage="false">
            ("TL1_TL5" , "3.3 V LVCMOS"), # is_dyn_voltage="false">
            ("TR0"     , "3.3 V LVCMOS"), # is_dyn_voltage="false" mode_sel_name="TR0_MODE_SEL"/>
            ("TR1"     , "3.3 V LVCMOS"), # is_dyn_voltage="false" mode_sel_name="TR1_MODE_SEL"/>
            ("TR2"     , "3.3 V LVCMOS"), # is_dyn_voltage="false" mode_sel_name="TR2_MODE_SEL"/>
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("pmod0", "G15 G16 F16 F17 G17 A11 A13 A12"),
    ("pmod1", "B12 C14 C13 C12 D12 F12 D13 E13"),
]

# PMODS --------------------------------------------------------------------------------------------

def raw_pmod_io(pmod):
    return [(pmod, 0, Pins(" ".join([f"{pmod}:{i:d}" for i in range(8)])), IOStandard("3.3_V_LVTTL_/_LVCMOS"))]

# Platform -----------------------------------------------------------------------------------------

class Platform(EfinixPlatform):
    default_clk_name   = "clk25"
    default_clk_period = 1e9/25e6

    def __init__(self, toolchain="efinity"):
        EfinixPlatform.__init__(self, "Ti375C529C4", _io, _connectors, iobank_info=_bank_info, toolchain=toolchain)

    def create_programmer(self):
        return EfinixProgrammer()

    def do_finalize(self, fragment):
        EfinixPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk25", loose=True), 1e9/25e6)
