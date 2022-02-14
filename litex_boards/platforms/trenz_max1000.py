#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019-2021 Antti Lukats <antti.lukats@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause
#
# http://trenz.org/max1000-info

from litex.build.generic_platform import *
from litex.build.altera import AlteraPlatform
from litex.build.altera.programmer import USBBlaster

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk12", 0, Pins("H6"), IOStandard("3.3-V LVTTL")),

    # Leds
    ("user_led", 0, Pins("A8"),  IOStandard("3.3-V LVTTL")),
    ("user_led", 1, Pins("A9"),  IOStandard("3.3-V LVTTL")),
    ("user_led", 2, Pins("A11"), IOStandard("3.3-V LVTTL")),
    ("user_led", 3, Pins("A10"), IOStandard("3.3-V LVTTL")),
    ("user_led", 4, Pins("B10"), IOStandard("3.3-V LVTTL")),
    ("user_led", 5, Pins("C9"),  IOStandard("3.3-V LVTTL")),
    ("user_led", 6, Pins("C10"), IOStandard("3.3-V LVTTL")),
    ("user_led", 7, Pins("D8"),  IOStandard("3.3-V LVTTL")),

    # Buttons
    ("user_btn", 0, Pins("E6"), IOStandard("3.3-V LVTTL")),
    ("user_btn", 1, Pins("E7"), IOStandard("3.3-V LVTTL")), # nConfig.

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("B4"), IOStandard("3.3-V LVTTL")),
        Subsignal("rx", Pins("A4"), IOStandard("3.3-V LVTTL"))
    ),

    # SPI Flash
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("B3")),
        Subsignal("clk", Pins("A3")),
        Subsignal("dq", Pins("A2", "B2", "B9", "C4")),
        IOStandard("3.3-V LVTTL")
    ),
    ("spiflash", 0,
        Subsignal("cs_n", Pins("B3")),
        Subsignal("clk", Pins("A3")),
        Subsignal("mosi", Pins("A2")),
        Subsignal("miso", Pins("B2")),
        Subsignal("wp", Pins("B9")),
        Subsignal("hold", Pins("C4")),
        IOStandard("3.3-V LVTTL"),
    ),

    # SDRAM
    ("sdram_clock", 0, Pins("M9"), IOStandard("3.3-V LVTTL")),
    ("sdram", 0,
        Subsignal("a", Pins(
            "K6  M5 N5 J8 N10 M11 N9 L10",
            "M13 N8 N4 M10")),
        Subsignal("ba",    Pins("N6 K8")),
        Subsignal("cs_n",  Pins("M4")),
        Subsignal("cke",   Pins("M8")),
        Subsignal("ras_n", Pins("M7")),
        Subsignal("cas_n", Pins("N7")),
        Subsignal("we_n",  Pins("K7")),
        Subsignal("dq", Pins(
            "D11 G10 F10  F9 E10  D9  G9  F8",
            "F13 E12 E13 D12 C12 B12 B13 A12")),
        Subsignal("dm", Pins("E9 F12")),
        IOStandard("3.3-V LVTTL")
    ),

    # all IO not connected to peripherals mapped to MFIO
    #                 <-        LEDS           -> <-         PMOD      -> <-                     D0..D14, D11R, D12R                  -> <-     AIN0..AIN7    -> JE [C O  I  S  i1 i2]sw
    ("bbio", 0, Pins("A8 A9 A11 A10 B10 C9 C10 D8 M3 L3 M2 M1 N3 N2 K2 K1 H8 K10 H5 H4 J1 J2 L12 J12 J13 K11 K12 J10 H10 H13 G12 B11 G13 E1 C2 C1 D1 E3 F1 E4 B1 E5 J6 J7 K5 L5 J5 L4 E6"),
        IOStandard("3.3-V LVTTL")),


]

# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name   = "clk12"
    default_clk_period = 1e9/12e6

    def __init__(self, toolchain="quartus"):
        AlteraPlatform.__init__(self, "10M08SAU169C8G", _io, toolchain=toolchain)
        self.add_platform_command("set_global_assignment -name FAMILY \"MAX 10\"")
        self.add_platform_command("set_global_assignment -name ENABLE_CONFIGURATION_PINS OFF")
        self.add_platform_command("set_global_assignment -name INTERNAL_FLASH_UPDATE_MODE \"SINGLE IMAGE WITH ERAM\"")

    def create_programmer(self):
        return USBBlaster()

    def do_finalize(self, fragment):
        AlteraPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk12", loose=True), 1e9/12e6)
        # Generate PLL clock in STA
        self.toolchain.additional_sdc_commands.append("derive_pll_clocks")
        # Calculates clock uncertainties
        self.toolchain.additional_sdc_commands.append("derive_clock_uncertainty")



