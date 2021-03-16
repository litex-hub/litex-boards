#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Sergiu Mosanu <sm7ed@virginia.edu>
#
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import Pins, Subsignal, IOStandard, Misc
from litex.build.xilinx import XilinxPlatform, VivadoProgrammer

# IOs -----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("sysclk", 0,
        Subsignal("n", Pins("BJ44"), IOStandard("LVDS")),
        Subsignal("p", Pins("BJ43"), IOStandard("LVDS")),
    ),
    ("sysclk", 1,
        Subsignal("n", Pins("BJ6"), IOStandard("LVDS")),
        Subsignal("p", Pins("BH6"), IOStandard("LVDS")),
    ),

    ("cpu_reset", 0, Pins("L30"), IOStandard("LVCMOS18")),

    # Leds
    ("gpio_led", 0, Pins("C32"), IOStandard("LVCMOS18")),
    ("gpio_led", 1, Pins("D32"), IOStandard("LVCMOS18")),
    ("gpio_led", 2, Pins("D31"), IOStandard("LVCMOS18")),

    # Switches

    ("gpio_sw", 0, Pins("J30"), IOStandard("LVCMOS18")),
    ("gpio_sw", 1, Pins("J32"), IOStandard("LVCMOS18")),
    ("gpio_sw", 2, Pins("K32"), IOStandard("LVCMOS18")),
    ("gpio_sw", 3, Pins("K31"), IOStandard("LVCMOS18")),

    # Serial
    ("serial", 0,
        Subsignal("rx", Pins("A28"), IOStandard("LVCMOS18")),
        Subsignal("tx", Pins("B33"), IOStandard("LVCMOS18")),
    ),

    # DDR4 SDRAM
    #("ddram_reset_gate", 0, Pins(""), IOStandard("LVCMOS12")),???
    ("ddram", 0,
        Subsignal("a", Pins(
            "BF46 BG43 BK45 BF42 BL45 BF43 BG42 BL43",
            "BK43 BM42 BG45 BD41 BL42 BE44"),
            IOStandard("SSTL12_DCI")),
        Subsignal("act_n", Pins("BH41"), IOStandard("SSTL12_DCI")),
        Subsignal("ba", Pins("BH45 BM47"), IOStandard("SSTL12_DCI")),
        Subsignal("bg", Pins("BF41 BE41"), IOStandard("SSTL12_DCI")),
        Subsignal("cas_n", Pins("BL46"), IOStandard("SSTL12_DCI")), # A15
        Subsignal("cke", Pins("BH42"), IOStandard("SSTL12_DCI")),
        Subsignal("clk_n", Pins("BJ46"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("clk_p", Pins("BH46"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("cs_n",  Pins("BK46"), IOStandard("SSTL12_DCI")),
        Subsignal("dq", Pins(
            "BN32 BP32 BL30 BM30 BP29 BP28 BP31 BN31",
            "BJ31 BH31 BF32 BF33 BH29 BH30 BF31 BG32",
            "BK31 BL31 BK33 BL33 BL32 BM33 BN34 BP34",
            "BH34 BH35 BF35 BF36 BJ33 BJ34 BG34 BG35",
            "BM52 BL53 BL52 BL51 BN50 BN51 BN49 BM48",
            "BE50 BE49 BE51 BD51 BF52 BF51 BG50 BF50",
            "BH50 BJ51 BH51 BH49 BK50 BK51 BJ49 BJ48",
            "BN44 BN45 BM44 BM45 BP43 BP44 BN47 BP47"),
            IOStandard("POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_n", Pins(
            "BN30 BM29 BK30 BG30 BM35 BN35 BK35 BJ32",
            "BM50 BP49 BF48 BG49 BJ47 BK49 BP46 BP42"), #"BJ54 BJ53"
            IOStandard("DIFF_POD12"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_p", Pins(
            "BN29 BM28 BJ29 BG29 BL35 BM34 BK34 BH32",
            "BM49 BP48 BF47 BG48 BH47 BK48 BN46 BN42"), #"BH54 BJ52"
            IOStandard("DIFF_POD12"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("odt", Pins("BG44"), IOStandard("SSTL12_DCI")),
        Subsignal("ras_n", Pins("BH44"), IOStandard("SSTL12_DCI")), # A16
        Subsignal("reset_n", Pins("BG33"), IOStandard("LVCMOS12")),
        Subsignal("we_n",  Pins("BE43"), IOStandard("SSTL12_DCI")), # A14
        Misc("SLEW=FAST")
    ),
        ("ddram", 1,
        Subsignal("a", Pins(
            "BF7 BK1 BF6 BF5 BE3 BE6 BE5 BG7",
            "BJ1 BG2 BJ8 BE4 BL2 BK5"), # BK8 BJ4 BF8
            IOStandard("SSTL12_DCI")),
        Subsignal("act_n", Pins("BG3"), IOStandard("SSTL12_DCI")),
        Subsignal("ba", Pins("BG8 BK4"), IOStandard("SSTL12_DCI")),
        Subsignal("bg", Pins("BF3 BF2"), IOStandard("SSTL12_DCI")),
        Subsignal("cas_n", Pins("BJ4"), IOStandard("SSTL12_DCI")), # A15
        Subsignal("cke", Pins("BE1"), IOStandard("SSTL12_DCI")),
        Subsignal("clk_n", Pins("BJ2"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("clk_p", Pins("BJ3"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("cs_n",  Pins("BL3"), IOStandard("SSTL12_DCI")),
        Subsignal("dq", Pins(
            "A11 A10 A9 A8 B12 B10 C12 B11",
            "E11 D11 E12 F11 F10 E9 F9 G11",
            "H12 G13 H13 H14 J11 J12 J15 J14",
            "A14 C15 A15 B15 F15 E14 F14 F13",
            "BM3 BM4 BM5 BL6 BN4 BN5 BN6 BN7",
            "BJ9 BK9 BK10 BL10 BM9 BN9 BN10 BM10",
            "BM15 BM14 BL15 BM13 BN12 BM12 BP13 BP14",
            "BJ13 BJ12 BH15 BH14 BK14 BK15 BL12 BL13"),
            IOStandard("POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_n", Pins(
            "A13 D9 G15 D14 BM7 BM8 BN14 BK13",
            "BF11 C9 G10 K13 D12 BP6 BP8 BP11"), # "BK11 BH9"
            IOStandard("DIFF_POD12"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_p", Pins(
            "B13 C10 D10 H10 H15 K14 D15 E13",
            "BL7 BP7 BL8 BP9 BN15 BP12 BJ14 BJ11"), #"BH54 BJ52"
            IOStandard("DIFF_POD12"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("odt", Pins("BH2"), IOStandard("SSTL12_DCI")),
        Subsignal("ras_n", Pins("BF8"), IOStandard("SSTL12_DCI")), # A16
        Subsignal("reset_n", Pins("BH12"), IOStandard("LVCMOS12")),
        Subsignal("we_n",  Pins("BK8"), IOStandard("SSTL12_DCI")), # A14
        Misc("SLEW=FAST")
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = []

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "sysclk"
    default_clk_period = 1e9/100e6

    def __init__(self):
        XilinxPlatform.__init__(self, "xcu280-fsvh2892-2L-e-es1", _io, _connectors, toolchain="vivado")

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("sysclk", 0, loose=True), 1e9/100e6)
        self.add_period_constraint(self.lookup_request("sysclk", 1, loose=True), 1e9/100e6)

        # For passively cooled boards, overheating is a significant risk if airflow isn't sufficient
        self.add_platform_command("set_property BITSTREAM.CONFIG.OVERTEMPSHUTDOWN ENABLE [current_design]")
        # Reduce programming time
        self.add_platform_command("set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]")
        # DDR4 memory channel C0 Internal Vref
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 64]")
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 65]")
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 66]")
        # DDR4 memory channel C1 Internal Vref
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 68]")
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 69]")
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 70]")

        # Other suggested configurations
        self.add_platform_command("set_property CONFIG_VOLTAGE 1.8 [current_design]")
        self.add_platform_command("set_property BITSTREAM.CONFIG.CONFIGFALLBACK Enable [current_design]")
        self.add_platform_command("set_property CONFIG_MODE SPIx4 [current_design]")
        self.add_platform_command("set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]")
        self.add_platform_command("set_property BITSTREAM.CONFIG.CONFIGRATE 85.0 [current_design]")
        self.add_platform_command("set_property BITSTREAM.CONFIG.EXTMASTERCCLK_EN disable [current_design]")
        self.add_platform_command("set_property BITSTREAM.CONFIG.SPI_FALL_EDGE YES [current_design]")
        self.add_platform_command("set_property BITSTREAM.CONFIG.UNUSEDPIN Pullup [current_design]")
        self.add_platform_command("set_property BITSTREAM.CONFIG.SPI_32BIT_ADDR Yes [current_design]")