#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Sergiu Mosanu <sm7ed@virginia.edu>
#
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import Pins, Subsignal, IOStandard, Misc
from litex.build.xilinx import XilinxUSPPlatform, VivadoProgrammer

# IOs -----------------------------------------------------------------------------------------------

_io = [
    # 100MHz Clk / Rst
    ("sysclk", 0,
        Subsignal("n", Pins("BJ44"), IOStandard("DIFF_SSTL12")),
        Subsignal("p", Pins("BJ43"), IOStandard("DIFF_SSTL12")),
    ),
    ("sysclk", 1,
        Subsignal("n", Pins("BJ6"), IOStandard("DIFF_SSTL12")),
        Subsignal("p", Pins("BH6"), IOStandard("DIFF_SSTL12")),
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
            "BK43 BM42 BG45 BD41 BL42 BE44"), # we_n=BE43 cas_n=BL46 ras_n=BH44
            IOStandard("SSTL12_DCI")),
        Subsignal("we_n",  Pins("BE43"), IOStandard("SSTL12_DCI")), # A14
        Subsignal("cas_n", Pins("BL46"), IOStandard("SSTL12_DCI")), # A15
        Subsignal("ras_n", Pins("BH44"), IOStandard("SSTL12_DCI")), # A16
        Subsignal("act_n", Pins("BH41"), IOStandard("SSTL12_DCI")),
        Subsignal("ba",    Pins("BH45 BM47"), IOStandard("SSTL12_DCI")),
        Subsignal("bg",    Pins("BF41 BE41"), IOStandard("SSTL12_DCI")),
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
            # ECC excluded 8 pins
            # "BG54 BG53 BE53 BE54 BH52 BG52 BK54 BK53"
            IOStandard("POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_n", Pins(
            "BN30 BM29 BK30 BG30 BM35 BN35 BK35 BJ32",
            "BM50 BP49 BF48 BG49 BJ47 BK49 BP46 BP42"), #"BJ54 BJ53"
            IOStandard("DIFF_POD12"), # DIFF_POD12_DCI
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_p", Pins(
            "BN29 BM28 BJ29 BG29 BL35 BM34 BK34 BH32",
            "BM49 BP48 BF47 BG48 BH47 BK48 BN46 BN42"), #"BH54 BJ52"
            IOStandard("DIFF_POD12"), # DIFF_POD12_DCI
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("odt",     Pins("BG44"), IOStandard("SSTL12_DCI")),
        Subsignal("reset_n", Pins("BG33"), IOStandard("LVCMOS12")),
        Misc("SLEW=FAST")
    ),
    ("ddram", 1,
        Subsignal("a", Pins(
            "BF7 BK1 BF6 BF5 BE3 BE6 BE5 BG7",
            "BJ1 BG2 BJ8 BE4 BL2 BK5"), # we_n=BK8 cas_n=BJ4 ras_n=BF8
            IOStandard("SSTL12_DCI")),
        Subsignal("we_n",  Pins("BK8"), IOStandard("SSTL12_DCI")), # A14
        Subsignal("cas_n", Pins("BJ4"), IOStandard("SSTL12_DCI")), # A15
        Subsignal("ras_n", Pins("BF8"), IOStandard("SSTL12_DCI")), # A16
        Subsignal("act_n", Pins("BG3"), IOStandard("SSTL12_DCI")),
        Subsignal("ba",    Pins("BG8 BK4"), IOStandard("SSTL12_DCI")),
        Subsignal("bg",    Pins("BF3 BF2"), IOStandard("SSTL12_DCI")),
        Subsignal("cke",   Pins("BE1"), IOStandard("SSTL12_DCI")),
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
            # ECC excluded 8 pins
            # "BE9 BE10 BF10 BE11 BG13 BG12 BG9 BG10"
            IOStandard("POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_n", Pins(
            "A13 C9 D9 G10 G15 K13 D14 D12",
            "BM7 BP6 BM8 BP8 BN14 BP11 BK13 BK11"), #"BF11 BH9"
            IOStandard("DIFF_POD12"), # DIFF_POD12_DCI
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_p", Pins(
            "B13 C10 D10 H10 H15 K14 D15 E13",
            "BL7 BP7 BL8 BP9 BN15 BP12 BJ14 BJ11"), #"BF12 BH10"
            IOStandard("DIFF_POD12"), # DIFF_POD12_DCI
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("odt",     Pins("BH2"), IOStandard("SSTL12_DCI")),
        Subsignal("reset_n", Pins("BH12"), IOStandard("LVCMOS12")),
        Misc("SLEW=FAST")
    ),

    # I2C (not tested on hardware)
    ("i2c_rst_n", 0, Pins("B31"), IOStandard("LVCMOS18")),
    ("i2c", 0,
        Subsignal("scl", Pins("C30"), IOStandard("LVCMOS18")),
        Subsignal("sda", Pins("C33"), IOStandard("LVCMOS18")),
    ),

    # QSFP Clock (not tested on hardware)
    ("qsfp_156mhz_clock", 0,
        Subsignal("n", Pins("T43")),
        Subsignal("p", Pins("T42")),
    ),
    ("qsfp_156mhz_clock", 1,
        Subsignal("n", Pins("P43")),
        Subsignal("p", Pins("P42")),
    ),

    # PCIe (hardware tests in progress)
    ("pcie_x16", 0,
        Subsignal("rst_n", Pins("BH26"), IOStandard("LVCMOS18")),
        Subsignal("clk_n", Pins("AR14")),
        Subsignal("clk_p", Pins("AR15")),
        Subsignal("rx_n", Pins(
            "AL1 AM3 AN5 AN1 AP3 AR1 AT3 AU1",
            "AV3 AW5 AW1 AY3 BA5 BA1 BB3 BC1")),
        Subsignal("rx_p", Pins(
            "AL2 AM4 AN6 AN2 AP4 AR2 AT4 AU2",
            "AV4 AW6 AW2 AY4 BA6 BA2 BB4 BC2")),
        Subsignal("tx_n", Pins(
            "AL10 AM8 AN10 AP8 AR10 AR6 AT8 AU10",
            "AU6 AV8 AW10 AY8 BA10 BB8 BC10 BC6")),
        Subsignal("tx_p", Pins(
            "AL11 AM9 AN11 AP9 AR11 AR7 AT9 AU11",
            "AU7 AV9 AW11 AY9 BA11 BB9 BC11 BC7")),
    ),

    # PCIe (hardware tests in progress)
    ("pcie_x4", 0,
        Subsignal("rst_n", Pins("BH26"), IOStandard("LVCMOS18")),
        Subsignal("clk_n", Pins("AR14")),
        Subsignal("clk_p", Pins("AR15")),
        Subsignal("rx_n",  Pins("AL1 AM3 AN5 AN1")),
        Subsignal("rx_p",  Pins("AL2 AM4 AN6 AN2")),
        Subsignal("tx_n",  Pins("AL10 AM8 AN10 AP8")),
        Subsignal("tx_p",  Pins("AL11 AM9 AN11 AP9")),
    ),

    # QSFP28 (not tested on hardware)
    ("qsfp28", 0,
        Subsignal("clk_n", Pins("R41")),
        Subsignal("clk_p", Pins("R40")),
        #Subsignal("fs0", Pins(""), IOStandard("LVCMOS18")), # not found in u280 pins
        #Subsignal("fs1", Pins(""), IOStandard("LVCMOS18")), # not found in u280 pins
        Subsignal("intl", Pins("B32")),
        Subsignal("lpmode", Pins("C29")),
        Subsignal("modprsl", Pins("A33")),
        Subsignal("modskll", Pins("A31")),
        #Subsignal("refclk_reset", Pins(""), IOStandard("LVCMOS12")), # not found in u280 pins
        Subsignal("resetl", Pins("B30")),
        Subsignal("rxn", Pins("L54 K52 J54 H52")),
        Subsignal("rxp", Pins("L53 K51 J53 H51")),
        Subsignal("txn", Pins("L49 L45 K47 J49")),
        Subsignal("txp", Pins("L48 L44 K46 J48")),
    ),
    ("qsfp28", 1,
        Subsignal("clk_n", Pins("M43")),
        Subsignal("clk_p", Pins("M42")),
        #Subsignal("fs0", Pins(""), IOStandard("LVCMOS18")), # not found in u280 pins
        #Subsignal("fs1", Pins(""), IOStandard("LVCMOS18")), # not found in u280 pins
        Subsignal("intl", Pins("E29")),
        Subsignal("lpmode", Pins("F29")),
        Subsignal("modprsl", Pins("F33")),
        Subsignal("modskll", Pins("D30")),
        #Subsignal("refclk_reset", Pins(""), IOStandard("LVCMOS12")), # not found in u280 pins
        Subsignal("resetl", Pins("E33")),
        Subsignal("rxn", Pins("G54 F52 E54 D52")),
        Subsignal("rxp", Pins("G53 F51 E53 D51")),
        Subsignal("txn", Pins("G49 E49 C49 A50")),
        Subsignal("txp", Pins("G48 E48 C48 A49")),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = []

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxUSPPlatform):
    default_clk_name   = "sysclk"
    default_clk_period = 1e9/100e6

    def __init__(self, toolchain="vivado"):
        XilinxUSPPlatform.__init__(self, "xcu280-fsvh2892-2L-e-es1", _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment):
        XilinxUSPPlatform.do_finalize(self, fragment)
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

        # For HBM2 IP in Vivado 2019.2 (https://www.xilinx.com/support/answers/72607.html)
        self.add_platform_command("connect_debug_port dbg_hub/clk [get_nets apb_clk]")