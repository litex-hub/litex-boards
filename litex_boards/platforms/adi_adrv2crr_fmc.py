#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Sylvain Munaut <tnt@246tNt.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxUSPPlatform
from litex.build.openocd import OpenOCD

_io = [
    # Clk
    ("clk122m88", 0,
        Subsignal("p", Pins("AN17"), IOStandard("LVDS"), Misc("DIFF_TERM_ADV=TERM_100")),
        Subsignal("n", Pins("AP17"), IOStandard("LVDS"), Misc("DIFF_TERM_ADV=TERM_100"))
    ),

    ("core_clk", 0,
        Subsignal("p", Pins("AU6"), IOStandard("LVDS"), Misc("DIFF_TERM_ADV=TERM_100")),
        Subsignal("n", Pins("AV6"), IOStandard("LVDS"), Misc("DIFF_TERM_ADV=TERM_100"))
    ),

    ("core_clk", 1,
        Subsignal("p", Pins("AV8"), IOStandard("LVDS"), Misc("DIFF_TERM_ADV=TERM_100")),
        Subsignal("n", Pins("AV7"), IOStandard("LVDS"), Misc("DIFF_TERM_ADV=TERM_100"))
    ),

    # Leds
    ("user_led", 0, Pins("AJ16"), IOStandard("LVCMOS18")),
    ("user_led", 1, Pins("AH16"), IOStandard("LVCMOS18")),
    ("user_led", 2, Pins("AJ12"), IOStandard("LVCMOS18")),
    ("user_led", 3, Pins("AK12"), IOStandard("LVCMOS18")),

    # Switches
    ("user_sw", 0, Pins("AW11"), IOStandard("LVCMOS18")),
    ("user_sw", 1, Pins("AW10"), IOStandard("LVCMOS18")),
    ("user_sw", 2, Pins("AN13"), IOStandard("LVCMOS18")),
    ("user_sw", 3, Pins("AN12"), IOStandard("LVCMOS18")),

    # Buttons
    ("user_btn", 0, Pins("AV13"), IOStandard("LVCMOS18")),
    ("user_btn", 1, Pins("AV14"), IOStandard("LVCMOS18")),
    ("user_btn", 2, Pins("AT11"), IOStandard("LVCMOS18")),
    ("user_btn", 3, Pins("AT12"), IOStandard("LVCMOS18")),

    # Serial (on PMOD, compatible with Digilent spec / PmodUSBUART)
    ("serial", 0,
        Subsignal("rx", Pins("AU13"), IOStandard("LVCMOS18")), # PMOD 3
        Subsignal("tx", Pins("AV12"), IOStandard("LVCMOS18")), # PMOD 2
    ),

    # SPI
    ("spi", 0,
        Subsignal("clk",  Pins("AN21")),
        Subsignal("cs_n", Pins("AL18 AL17 AU20 AR10")), # ADRV9009_A, ADRV9009_B, HMC7044_SOM, HMC7044_CAR
        Subsignal("mosi", Pins("AP21")),
        Subsignal("miso", Pins("AR9")),
        IOStandard("LVCMOS18")
    ),

    # I2C
        # On the ADRV9009_ZU11EG SoM
        # ADM1266 @ 0x48
        # AD9542  @ 0x4B
        # ADM1177 @ 0x58
    ("i2c", 0,
        Subsignal("sda", Pins("AU21")),
        Subsignal("scl", Pins("AT21")),
        IOStandard("LVCMOS18")
    ),

        # On the ADRV2CRR_FMC carrier
        # (through TCA9548A, connects to SFP/QSFP/Audio/AD9545/PTN5150/FMC)
        # ADAU1761 @ bus 0 - 0x3b
        # AD9545   @ bus 1 - 0x4a
        # PTN5150  @ bus 2 - 0x1d
        # QSFP     @ bus 3 - 0x5[0-3]
        # SFP      @ bus 4 - 0x5[0-3]
        # FMC_HPC  @ bus 5
        # TCA9548A @       - 0x70
    ("i2c", 1,
        Subsignal("sda", Pins("AN18")),
        Subsignal("scl", Pins("AN19")),
        IOStandard("LVCMOS18")
    ),

    # FAN
    ("fan", 0,
        Subsignal("tach",  Pins("AT13")),
        Subsignal("pwm_n", Pins("AR13")),
        IOStandard("LVCMOS18")
    ),

    # Talise A
    ("talise_ctl", 0,
        Subsignal("reset_n",    Pins("AV9")),
        Subsignal("test",       Pins("AL11")),
        Subsignal("tx1_enable", Pins("AR3")),
        Subsignal("tx2_enable", Pins("AT3")),
        Subsignal("rx1_enable", Pins("AP2")),
        Subsignal("rx2_enable", Pins("AP1")),
        IOStandard("LVCMOS18")
    ),

    ("talise_gpio", 0,
        Subsignal("io",  Pins(
            "AW7 AW6 AU5 AU4 AV4 AW4 AT8 AT7",
            "AT5 AU9 AU8 AR5 AR4 AR7 AP7 AT6",
            "AP4 AP5 AP6")),
        Subsignal("int", Pins("AW9")),
        IOStandard("LVCMOS18")
    ),

    ("talise_refclk", 0,
        Subsignal("p", Pins("N12")),
        Subsignal("n", Pins("N11")),
    ),

    ("talise_sysref", 0,
        Subsignal("p", Pins("AT1"), IOStandard("LVDS"), Misc("DIFF_TERM_ADV=TERM_100")),
        Subsignal("n", Pins("AU1"), IOStandard("LVDS"), Misc("DIFF_TERM_ADV=TERM_100"))
    ),

    ("talise_sync_tx", 0,
        Subsignal("p", Pins("AU3"), IOStandard("LVDS"), Misc("DIFF_TERM_ADV=TERM_100")),
        Subsignal("n", Pins("AV3"), IOStandard("LVDS"), Misc("DIFF_TERM_ADV=TERM_100")),
    ),

    ("talise_sync_tx", 1,
        Subsignal("p", Pins("AV2"), IOStandard("LVDS"), Misc("DIFF_TERM_ADV=TERM_100")),
        Subsignal("n", Pins("AW2"), IOStandard("LVDS"), Misc("DIFF_TERM_ADV=TERM_100")),
    ),

    ("talise_sync_rx", 0,
        Subsignal("p", Pins("AR2"), IOStandard("LVDS")),
        Subsignal("n", Pins("AT2"), IOStandard("LVDS")),
    ),

    ("talise_sync_rx", 1,
        Subsignal("p", Pins("AR18"), IOStandard("LVDS")),
        Subsignal("n", Pins("AT18"), IOStandard("LVDS")),
    ),

    ("talise_jesd_tx", 0,
        Subsignal("p", Pins("D6")),
        Subsignal("n", Pins("D5")),
    ),

    ("talise_jesd_tx", 1,
        Subsignal("p", Pins("C8")),
        Subsignal("n", Pins("C7")),
    ),

    ("talise_jesd_tx", 2,
        Subsignal("p", Pins("B6")),
        Subsignal("n", Pins("B5")),
    ),

    ("talise_jesd_tx", 3,
        Subsignal("p", Pins("A8")),
        Subsignal("n", Pins("A7")),
    ),

    ("talise_jesd_rx", 0,
        Subsignal("p", Pins("D2")),
        Subsignal("n", Pins("D1")),
    ),

    ("talise_jesd_rx", 1,
        Subsignal("p", Pins("C4")),
        Subsignal("n", Pins("C3")),
    ),

    ("talise_jesd_rx", 2,
        Subsignal("p", Pins("B2")),
        Subsignal("n", Pins("B1")),
    ),

    ("talise_jesd_rx", 3,
        Subsignal("p", Pins("A4")),
        Subsignal("n", Pins("A3")),
    ),

    # Talise B
    ("talise_ctl", 1,
        Subsignal("reset_n",    Pins("AH18")),
        Subsignal("test",       Pins("AR17")),
        Subsignal("tx1_enable", Pins("AW5")),
        Subsignal("tx2_enable", Pins("AR8")),
        Subsignal("rx1_enable", Pins("AT20")),
        Subsignal("rx2_enable", Pins("AM20")),
        IOStandard("LVCMOS18")
    ),

    ("talise_gpio", 1,
        Subsignal("io",  Pins(
            "AM11 AN11 AU18 AV18 AV21 AW21 AV17 AW17",
            "AW19 AV16 AW16 AU19 AV19 AM18 AM19 AW20",
            "AM21 AL21 AL10")),
        Subsignal("int", Pins("AK10")),
        IOStandard("LVCMOS18")
    ),

    ("talise_refclk", 1,
        Subsignal("p", Pins("R12")),
        Subsignal("n", Pins("R11")),
    ),

    ("talise_sysref", 1,
        Subsignal("p", Pins("AP11"), IOStandard("LVDS"), Misc("DIFF_TERM_ADV=TERM_100")),
        Subsignal("n", Pins("AP10"), IOStandard("LVDS"), Misc("DIFF_TERM_ADV=TERM_100"))
    ),

    ("talise_sync_tx", 2,
        Subsignal("p", Pins("AK20"), IOStandard("LVDS"), Misc("DIFF_TERM_ADV=TERM_100")),
        Subsignal("n", Pins("AL20"), IOStandard("LVDS"), Misc("DIFF_TERM_ADV=TERM_100")),
    ),

    ("talise_sync_tx", 3,
        Subsignal("p", Pins("AG20"), IOStandard("LVDS"), Misc("DIFF_TERM_ADV=TERM_100")),
        Subsignal("n", Pins("AG19"), IOStandard("LVDS"), Misc("DIFF_TERM_ADV=TERM_100")),
    ),

    ("talise_sync_rx", 2,
        Subsignal("p", Pins("AJ21"), IOStandard("LVDS")),
        Subsignal("n", Pins("AJ20"), IOStandard("LVDS")),
    ),

    ("talise_sync_rx", 3,
        Subsignal("p", Pins("AT17"), IOStandard("LVDS")),
        Subsignal("n", Pins("AT16"), IOStandard("LVDS")),
    ),

    ("talise_jesd_tx", 4,
        Subsignal("p", Pins("H6")),
        Subsignal("n", Pins("H5")),
    ),

    ("talise_jesd_tx", 5,
        Subsignal("p", Pins("G8")),
        Subsignal("n", Pins("G7")),
    ),

    ("talise_jesd_tx", 6,
        Subsignal("p", Pins("F6")),
        Subsignal("n", Pins("F5")),
    ),

    ("talise_jesd_tx", 7,
        Subsignal("p", Pins("E8")),
        Subsignal("n", Pins("E7")),
    ),

    ("talise_jesd_rx", 4,
        Subsignal("p", Pins("H2")),
        Subsignal("n", Pins("H1")),
    ),

    ("talise_jesd_rx", 5,
        Subsignal("p", Pins("G4")),
        Subsignal("n", Pins("G3")),
    ),

    ("talise_jesd_rx", 6,
        Subsignal("p", Pins("F2")),
        Subsignal("n", Pins("F1")),
    ),

    ("talise_jesd_rx", 7,
        Subsignal("p", Pins("E4")),
        Subsignal("n", Pins("E3")),
    ),

    # HMC7044 SoM
    ("hmc7044_som_ctl", 0,
        Subsignal("gpio1", Pins("AK19")),
        Subsignal("gpio2", Pins("AK18")),
        Subsignal("gpio3", Pins("AG21")),
        Subsignal("gpio4", Pins("AH21")),
        Subsignal("reset", Pins("AH19")),
        Subsignal("sync",  Pins("AJ19")),
        IOStandard("LVCMOS18")
    ),

    # HMC7044 Carrier
    ("hmc7044_car_ctl", 0,
        Subsignal("gpio1", Pins("AP20")),
        Subsignal("gpio2", Pins("AR20")),
        Subsignal("gpio3", Pins("AP9")),
        Subsignal("gpio4", Pins("AP8")),
        Subsignal("reset", Pins("AP19")),
        IOStandard("LVCMOS18")
    ),

    # AD9545
    ("ad9545_car_reset_n", 0, Pins("AR19"), IOStandard("LVCMOS18"), Misc("PULLUP")),

    # PCIe
    ("pcie_x1", 0,
        Subsignal("rst_n",  Pins("AH17"), IOStandard("LVCMOS18")),
        Subsignal("wake_n", Pins("AW15"), IOStandard("LVCMOS18")),
        Subsignal("clk_p",  Pins("AH10")),
        Subsignal("clk_n",  Pins("AH9")),
        Subsignal("rx_p",   Pins("AE4")),
        Subsignal("rx_n",   Pins("AE3")),
        Subsignal("tx_p",   Pins("AE8")),
        Subsignal("tx_n",   Pins("AE7")),
    ),

    ("pcie_x2", 0,
        Subsignal("rst_n",  Pins("AH17"), IOStandard("LVCMOS18")),
        Subsignal("wake_n", Pins("AW15"), IOStandard("LVCMOS18")),
        Subsignal("clk_p",  Pins("AH10")),
        Subsignal("clk_n",  Pins("AH9")),
        Subsignal("rx_p",   Pins("AE4 AF2")),
        Subsignal("rx_n",   Pins("AE3 AF1")),
        Subsignal("tx_p",   Pins("AE8 AF6")),
        Subsignal("tx_n",   Pins("AE7 AF5")),
    ),

    ("pcie_x4", 0,
        Subsignal("rst_n",  Pins("AH17"), IOStandard("LVCMOS18")),
        Subsignal("wake_n", Pins("AW15"), IOStandard("LVCMOS18")),
        Subsignal("clk_p",  Pins("AH10")),
        Subsignal("clk_n",  Pins("AH9")),
        Subsignal("rx_p",   Pins("AE4 AF2 AG4 AH2")),
        Subsignal("rx_n",   Pins("AE3 AF1 AG3 AH1")),
        Subsignal("tx_p",   Pins("AE8 AF6 AG8 AH6")),
        Subsignal("tx_n",   Pins("AE7 AF5 AG7 AH5")),
    ),

    ("pcie_x8", 0,
        Subsignal("rst_n",  Pins("AH17"), IOStandard("LVCMOS18")),
        Subsignal("wake_n", Pins("AW15"), IOStandard("LVCMOS18")),
        Subsignal("clk_p",  Pins("AH10")),
        Subsignal("clk_n",  Pins("AH9")),
        Subsignal("rx_p",   Pins("AE4 AF2 AG4 AH2 AJ4 AK2 AL4 AM2")),
        Subsignal("rx_n",   Pins("AE3 AF1 AG3 AH1 AJ3 AK1 AL3 AM1")),
        Subsignal("tx_p",   Pins("AE8 AF6 AG8 AH6 AJ8 AK6 AL8 AM6")),
        Subsignal("tx_n",   Pins("AE7 AF5 AG7 AH5 AJ7 AK5 AL7 AM5")),
    ),

    # DDR4 SDRAM
    ("ddram", 0,
        Subsignal("a", Pins(
            "C31 B31 A27 A28 A30 A31 C28 C29",
            "B29 B30 C27 B28 F30 F31"),
            IOStandard("SSTL12_DCI")),
        Subsignal("act_n", Pins("J30"), IOStandard("SSTL12_DCI")),
        Subsignal("ba",    Pins("D30 D26"), IOStandard("SSTL12_DCI")),
        Subsignal("bg",    Pins("D27"), IOStandard("SSTL12_DCI")),
        Subsignal("ras_n", Pins("E30"), IOStandard("SSTL12_DCI")), # A16
        Subsignal("cas_n", Pins("D29"), IOStandard("SSTL12_DCI")), # A15
        Subsignal("we_n",  Pins("E29"), IOStandard("SSTL12_DCI")), # A14
        Subsignal("cke",   Pins("K30"), IOStandard("SSTL12_DCI")),
        Subsignal("clk_n", Pins("E28"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("clk_p", Pins("E27"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("cs_n",  Pins("G29"), IOStandard("SSTL12_DCI")),
        Subsignal("dm",    Pins("G28 K29 N14 K15"),
            IOStandard("POD12_DCI")),
        Subsignal("dq", Pins(
            "G30 F26 H28 G26 H29 J27 G31 J26",
            "M25 L27 J25 K28 L25 J29 K25 L28",
            "M18 L15 L18 M16 N19 M15 N18 N16",
            "K17 G16 H18 H17 J17 H16 H19 J16"),
            IOStandard("POD12_DCI"),
            Misc("OUTPUT_IMPEDANCE=RDRV_40_40"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_n", Pins("H27 L26 L16 J19"),
            IOStandard("DIFF_POD12"),
            Misc("OUTPUT_IMPEDANCE=RDRV_40_40"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_p", Pins("H26 M26 L17 K19"),
            IOStandard("DIFF_POD12"),
            Misc("OUTPUT_IMPEDANCE=RDRV_40_40"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("odt",     Pins("D31"), IOStandard("SSTL12_DCI")),
        Subsignal("reset_n", Pins("M14"), IOStandard("LVCMOS12")),
        Misc("SLEW=FAST")
    ),

    ("ddram_refclk", 0,
        Subsignal("p", Pins("F27"), IOStandard("LVDS")),
        Subsignal("n", Pins("F28"), IOStandard("LVDS"))
    ),

    # set_property -dict {PACKAGE_PIN K27 IOSTANDARD LVCMOS12} [get_ports ddr4_if_rx_offload_par]
    # set_property -dict {PACKAGE_PIN K18 IOSTANDARD LVCMOS12} [get_ports ddr4_if_rx_offload_alert_n]

    ("ddram", 1,
        Subsignal("a", Pins(
            "G24 G25 G20 G21 J24 H24 J21 H21",
            "J22 H22 J20 N21 M21 K23"),
            IOStandard("SSTL12_DCI")),
        Subsignal("act_n", Pins("E22"), IOStandard("SSTL12_DCI")),
        Subsignal("ba",    Pins("L22 L23"), IOStandard("SSTL12_DCI")),
        Subsignal("bg",    Pins("L20"), IOStandard("SSTL12_DCI")),
        Subsignal("ras_n", Pins("M20"), IOStandard("SSTL12_DCI")), # A16
        Subsignal("cas_n", Pins("L21"), IOStandard("SSTL12_DCI")), # A15
        Subsignal("we_n",  Pins("K24"), IOStandard("SSTL12_DCI")), # A14
        Subsignal("cke",   Pins("K22"), IOStandard("SSTL12_DCI")),
        Subsignal("clk_n", Pins("N23"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("clk_p", Pins("N22"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("cs_n",  Pins("A23"), IOStandard("SSTL12_DCI")),
        Subsignal("dm",    Pins("F17 C19 A22 E24"),
            IOStandard("POD12_DCI")),
        Subsignal("dq", Pins(
            "E20 D16 G18 E17 G19 F18 F20 D17",
            "B19 A16 B20 C17 A20 B16 B18 C16",
            "B25 C21 B24 C22 B26 A21 B21 B23",
            "E23 F21 F23 F22 E25 D22 F25 D21"),
            IOStandard("POD12_DCI"),
            Misc("OUTPUT_IMPEDANCE=RDRV_40_40"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_n", Pins("E18 A17 A26 C24"),
            IOStandard("DIFF_POD12"),
            Misc("OUTPUT_IMPEDANCE=RDRV_40_40"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_p", Pins("E19 A18 A25 D24"),
            IOStandard("DIFF_POD12"),
            Misc("OUTPUT_IMPEDANCE=RDRV_40_40"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("odt",     Pins("D25"), IOStandard("SSTL12_DCI")),
        Subsignal("reset_n", Pins("D20"), IOStandard("LVCMOS12")),
        Misc("SLEW=FAST")
    ),

    ("ddram_refclk", 1,
        Subsignal("p", Pins("H23"), IOStandard("LVDS")),
        Subsignal("n", Pins("G23"), IOStandard("LVDS")),
    ),

    #set_property -dict {PACKAGE_PIN K20 IOSTANDARD LVCMOS12} [get_ports ddr4_if_tx_offload_par]
    #set_property -dict {PACKAGE_PIN D19 IOSTANDARD LVCMOS12} [get_ports ddr4_if_tx_offload_alert_n]

    ("sfp", 0,
        Subsignal("clk_p",  Pins("T10")),
        Subsignal("clk_n",  Pins("T9")),
        Subsignal("rx_p",   Pins("J4")),
        Subsignal("rx_n",   Pins("J3")),
        Subsignal("tx_p",   Pins("J8")),
        Subsignal("tx_n",   Pins("J7")),
    ),
    ("sfp_rx", 0,
        Subsignal("p",      Pins("J4")),
        Subsignal("n",      Pins("J3")),
    ),
    ("sfp_tx", 0,
        Subsignal("p",      Pins("J8")),
        Subsignal("n",      Pins("J7")),
    ),
    ("sfp_tx_disable_n", 0, Pins("AU10")),

    ("qsfp", 0,
        Subsignal("clk_p",   Pins("AB10")),
        Subsignal("clk_n",   Pins("AB9")),
        Subsignal("rx_p",    Pins("AD2 AC4 AB2 AA4")),
        Subsignal("rx_n",    Pins("AD1 AC3 AB1 AA3")),
        Subsignal("tx_p",    Pins("AD6 AC8 AB6 AA8")),
        Subsignal("tx_n",    Pins("AD5 AC7 AB5 AA7")),
    ),
    ("qsfp_ctl", 0,
        Subsignal("intl",    Pins("AW14")),
        Subsignal("lpmode",  Pins("AV11")),
        Subsignal("modprsl", Pins("AL12")),
        Subsignal("resetl",  Pins("AU11")),
        IOStandard("LVCMOS18"),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("pmod", "AW12 AV12 AU13 AU14 AM13 AL13 AK15 AJ1"),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxUSPPlatform):
    default_clk_name   = "clk122m88"
    default_clk_period = 1e9/122.88e6

    def __init__(self):
        XilinxUSPPlatform.__init__(self, "xczu11eg-ffvf1517-2-i", _io, _connectors, toolchain="vivado")

    def do_finalize(self, fragment):
        XilinxUSPPlatform.do_finalize(self, fragment)

        # Constraint
        self.add_period_constraint(self.lookup_request("clk122m88", loose=True), 1e9/122.88e6)
        self.add_period_constraint(self.lookup_request("ddram_refclk", 0, loose=True), 1e9/300e6)
        self.add_period_constraint(self.lookup_request("ddram_refclk", 1, loose=True), 1e9/300e6)

        # VREF for DDR4
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 69]")
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 70]")
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 71]")

        # Shutdown on overheating
        self.add_platform_command("set_property BITSTREAM.CONFIG.OVERTEMPSHUTDOWN ENABLE [current_design]")

        # Reduce programming time
        self.add_platform_command("set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]")

