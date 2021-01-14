#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 David Shah <dave@ds0.me>
# Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# Modified for Alveo U280 by Sergiu Mosanu based on XCU1525
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import Pins, Subsignal, IOStandard, Misc
from litex.build.xilinx import XilinxPlatform, VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------

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
    ("user_led", 0, Pins("C32"), IOStandard("LVCMOS18")),
    ("user_led", 1, Pins("D32"), IOStandard("LVCMOS18")),
    ("user_led", 2, Pins("D31"), IOStandard("LVCMOS18")),

    # Serial
    ("serial", 0,
        Subsignal("rx", Pins("A28"), IOStandard("LVCMOS18")),
        Subsignal("tx", Pins("B33"), IOStandard("LVCMOS18")),
    ),

    # # PCIe
    # ("pcie_x2", 0,
    #     Subsignal("rst_n", Pins("BD21"), IOStandard("LVCMOS12")),
    #     Subsignal("clk_n", Pins("AM10")),
    #     Subsignal("clk_p", Pins("AM11")),
    #     Subsignal("rx_n",  Pins("AF1 AG3")),
    #     Subsignal("rx_p",  Pins("AF2 AG4")),
    #     Subsignal("tx_n",  Pins("AF6 AG8")),
    #     Subsignal("tx_p",  Pins("AF7 AG9")),
    # ),
    # ("pcie_x4", 0,
    #     Subsignal("rst_n", Pins("BD21"), IOStandard("LVCMOS12")),
    #     Subsignal("clk_n", Pins("AM10")),
    #     Subsignal("clk_p", Pins("AM11")),
    #     Subsignal("rx_n",  Pins("AF1 AG3 AH1 AJ3")),
    #     Subsignal("rx_p",  Pins("AF2 AG4 AH2 AJ4")),
    #     Subsignal("tx_n",  Pins("AF6 AG8 AH6 AJ8")),
    #     Subsignal("tx_p",  Pins("AF7 AG9 AH7 AJ9")),
    # ),
    # ("pcie_x8", 0,
    #     Subsignal("rst_n", Pins("BD21"), IOStandard("LVCMOS12")),
    #     Subsignal("clk_n", Pins("AM10")),
    #     Subsignal("clk_p", Pins("AM11")),
    #     Subsignal("rx_n",  Pins("AF1 AG3 AH1 AJ3 AK1 AL3 AM1 AN3")),
    #     Subsignal("rx_p",  Pins("AF2 AG4 AH2 AJ4 AK2 AL4 AM2 AN4")),
    #     Subsignal("tx_n",  Pins("AF6 AG8 AH6 AJ8 AK6 AL8 AM6 AN8")),
    #     Subsignal("tx_p",  Pins("AF7 AG9 AH7 AJ9 AK7 AL9 AM7 AN9")),
    # ),
    # ("pcie_x16", 0,
    #     Subsignal("rst_n", Pins("BD21"), IOStandard("LVCMOS12")),
    #     Subsignal("clk_n", Pins("AM10")),
    #     Subsignal("clk_p", Pins("AM11")),
    #     Subsignal("rx_n", Pins("AF1 AG3 AH1 AJ3 AK1 AL3 AM1 AN3 AP1 AR3 AT1 AU3 AV1 AW3 BA1 BC1")),
    #     Subsignal("rx_p", Pins("AF2 AG4 AH2 AJ4 AK2 AL4 AM2 AN4 AP2 AR4 AT2 AU4 AV2 AW4 BA2 BC2")),
    #     Subsignal("tx_n", Pins("AF6 AG8 AH6 AJ8 AK6 AL8 AM6 AN8 AP6 AR8 AT6 AU8 AV6 BB4 BD4 BF4")),
    #     Subsignal("tx_p", Pins("AF7 AG9 AH7 AJ9 AK7 AL9 AM7 AN9 AP7 AR9 AT7 AU9 AV7 BB5 BD5 BF5")),
    # ),

    # DDR4 SDRAM
    ("ddram", 0,
        Subsignal("a", Pins(
            "BF46 BG43 BK45 BF42 BL45 BF43 BG42 BL43",
            "BK43 BM42 BG45 BD41 BL42 BE44"), #"BE43 BL46 BH44"
            IOStandard("SSTL12_DCI")),
        Subsignal("act_n", Pins("BH41"), IOStandard("SSTL12_DCI")),
        Subsignal("ba", Pins("BH45 BM47"), IOStandard("SSTL12_DCI")),
        Subsignal("bg", Pins("BF41 BE41"), IOStandard("SSTL12_DCI")),
        Subsignal("ras_n", Pins("BH44"), IOStandard("SSTL12_DCI")), # A16
        Subsignal("cas_n", Pins("BL46"), IOStandard("SSTL12_DCI")), # A15
        Subsignal("we_n",  Pins("BE43"), IOStandard("SSTL12_DCI")), # A14
        Subsignal("cke",   Pins("BH42"), IOStandard("SSTL12_DCI")),
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
            # Misc("OUTPUT_IMPEDANCE=RDRV_40_40"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_n", Pins(
            "BN30 BM29 BK30 BG30 BM35 BN35 BK35 BJ32",
            "BM50 BP49 BF48 BG49 BJ47 BK49 BP46 BP42"), #"BJ54 BJ53"
            IOStandard("DIFF_POD12"),
            # Misc("OUTPUT_IMPEDANCE=RDRV_40_40"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_p", Pins(
            "BN29 BM28 BJ29 BG29 BL35 BM34 BK34 BH32",
            "BM49 BP48 BF47 BG48 BH47 BK48 BN46 BN42"), #"BH54 BJ52"
            IOStandard("DIFF_POD12"),
            # Misc("OUTPUT_IMPEDANCE=RDRV_40_40"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("odt",     Pins("BG44"), IOStandard("SSTL12_DCI")),
        Subsignal("reset_n", Pins("BG33"), IOStandard("LVCMOS12")),
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
        # ------------------------------------------------------------------------
        # # DDR4 memory channel C0 Clock constraint / Internal Vref
        # self.add_period_constraint(self.lookup_request("clk300", 0, loose=True), 1e9/300e6)
        # self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 40]")
        # self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 41]")
        # self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 42]")
        # # DDR4 memory channel C1 Clock constraint / Internal Vref
        # self.add_period_constraint(self.lookup_request("clk300", 1, loose=True), 1e9/300e6)
        # self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 65]")
        # self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 66]")
        # self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 67]")
        # # DDR4 memory channel C2 Clock constraint / Internal Vref
        # self.add_period_constraint(self.lookup_request("clk300", 2, loose=True), 1e9/300e6)
        # self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 46]")
        # self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 47]")
        # self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 48]")
        # # DDR4 memory channel C3 Clock constraint / Internal Vref
        # self.add_period_constraint(self.lookup_request("clk300", 3, loose=True), 1e9/300e6)
        # self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 70]")
        # self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 71]")
        # self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 72]")
