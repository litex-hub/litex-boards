#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Sylvain Munaut <tnt@246tNt.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxUSPPlatform

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
    ("pmod", "AW12 AV12 AU13 AU14 AM13 AL13 AK15 AJ15"),
    ("FMC_HPC", {
        "DP1_M2C_P"     : "W4",   # A2
        "DP1_M2C_N"     : "W3",   # A3
        "DP2_M2C_P"     : "V2",   # A6
        "DP2_M2C_N"     : "V1",   # A7
        "DP3_M2C_P"     : "U4",   # A10
        "DP3_M2C_N"     : "U3",   # A11
        "DP4_M2C_P"     : "T2",   # A14
        "DP4_M2C_N"     : "T1",   # A15
        "DP5_M2C_P"     : "R4",   # A18
        "DP5_M2C_N"     : "R3",   # A19
        "DP1_C2M_P"     : "Y6",   # A22
        "DP1_C2M_N"     : "Y5",   # A23
        "DP2_C2M_P"     : "V6",   # A26
        "DP2_C2M_N"     : "V5",   # A27
        "DP3_C2M_P"     : "U8",   # A30
        "DP3_C2M_N"     : "U7",   # A31
        "DP4_C2M_P"     : "T6",   # A34
        "DP4_C2M_N"     : "T5",   # A35
        "DP5_C2M_P"     : "R8",   # A38
        "DP5_C2M_N"     : "R7",   # A39
        "DP9_M2C_P"     : "L4",   # B4
        "DP9_M2C_N"     : "L3",   # B5
        "DP8_M2C_P"     : "M2",   # B8
        "DP8_M2C_N"     : "M1",   # B9
        "DP7_M2C_P"     : "N4",   # B12
        "DP7_M2C_N"     : "N3",   # B13
        "DP6_M2C_P"     : "P2",   # B16
        "DP6_M2C_N"     : "P1",   # B17
        "GBTCLK1_M2C_P" : "W12",  # B20
        "GBTCLK1_M2C_N" : "W11",  # B21
        "DP9_C2M_P"     : "L8",   # B24
        "DP9_C2M_N"     : "L7",   # B25
        "DP8_C2M_P"     : "M6",   # B28
        "DP8_C2M_N"     : "M5",   # B29
        "DP7_C2M_P"     : "N8",   # B32
        "DP7_C2M_N"     : "N7",   # B33
        "DP6_C2M_P"     : "P6",   # B36
        "DP6_C2M_N"     : "P5",   # B37
        "DP0_C2M_P"     : "W8",   # C2
        "DP0_C2M_N"     : "W7",   # C3
        "DP0_M2C_P"     : "Y2",   # C6
        "DP0_M2C_N"     : "Y1",   # C7
        "LA06_P"        : "AH22", # C10
        "LA06_N"        : "AJ22", # C11
        "LA10_P"        : "AG22", # C14
        "LA10_N"        : "AG23", # C15
        "LA14_P"        : "G38",  # C18
        "LA14_N"        : "G39",  # C19
        "LA18_CC_P"     : "E34",  # C22
        "LA18_CC_N"     : "D34",  # C23
        "LA27_P"        : "E39",  # C26
        "LA27_N"        : "D39",  # C27
        "GBTCLK0_M2C_P" : "V10",  # D4
        "GBTCLK0_M2C_N" : "V9",   # D5
        "LA01_CC_P"     : "AP25", # D8
        "LA01_CC_N"     : "AP26", # D9
        "LA05_P"        : "AJ25", # D11
        "LA05_N"        : "AJ26", # D12
        "LA09_P"        : "AL22", # D14
        "LA09_N"        : "AL23", # D15
        "LA13_P"        : "H31",  # D17
        "LA13_N"        : "H32",  # D18
        "LA17_CC_P"     : "G35",  # D20
        "LA17_CC_N"     : "G36",  # D21
        "LA23_P"        : "F38",  # D23
        "LA23_N"        : "E38",  # D24
        "LA26_P"        : "A37",  # D26
        "LA26_N"        : "A38",  # D27
        "HA01_CC_P"     : "AM11", # E2
        "HA01_CC_N"     : "AN11", # E3
        "HA05_P"        : "AU18", # E6
        "HA05_N"        : "AV18", # E7
        "HA09_P"        : "AV21", # E9
        "HA09_N"        : "AW21", # E10
        "HA13_P"        : "AV17", # E12
        "HA13_N"        : "AW17", # E13
        "HA16_P"        : "AW19", # E15
        "HA16_N"        : "AV16", # E16
        "HA20_P"        : "AW16", # E18
        "HA20_N"        : "AU19", # E19
        "HA00_CC_P"     : "AV19", # F4
        "HA00_CC_N"     : "AM18", # F5
        "HA04_P"        : "AM19", # F7
        "HA04_N"        : "AW20", # F8
        "HA08_P"        : "AM21", # F10
        "HA08_N"        : "AL21", # F11
        "HA12_P"        : "AT20", # F13
        "HA12_N"        : "AM20", # F14
        "HA15_P"        : "AW5",  # F16
        "HA15_N"        : "AR8",  # F17
        "HA19_P"        : "AL10", # F19
        "CLK1_M2C_P"    : "AN22", # G2
        "CLK1_M2C_N"    : "AP22", # G3
        "LA00_CC_P"     : "AP24", # G6
        "LA00_CC_N"     : "AR24", # G7
        "LA03_P"        : "AK24", # G9
        "LA03_N"        : "AK25", # G10
        "LA08_P"        : "AL25", # G12
        "LA08_N"        : "AM25", # G13
        "LA12_P"        : "AH24", # G15
        "LA12_N"        : "AJ24", # G16
        "LA16_P"        : "AM23", # G18
        "LA16_N"        : "AM24", # G19
        "LA20_P"        : "J32",  # G21
        "LA20_N"        : "H33",  # G22
        "LA22_P"        : "H38",  # G24
        "LA22_N"        : "H39",  # G25
        "LA25_P"        : "C37",  # G27
        "LA25_N"        : "B38",  # G28
        "LA29_P"        : "E32",  # G30
        "LA29_N"        : "E33",  # G31
        "LA31_P"        : "A32",  # G33
        "LA31_N"        : "A33",  # G34
        "LA33_P"        : "D32",  # G36
        "LA33_N"        : "C32",  # G37
        "CLK0_M2C_P"    : "AN23", # H4
        "CLK0_M2C_N"    : "AN24", # H5
        "LA02_P"        : "AW26", # H7
        "LA02_N"        : "AW27", # H8
        "LA04_P"        : "AR25", # H10
        "LA04_N"        : "AT25", # H11
        "LA07_P"        : "AW24", # H13
        "LA07_N"        : "AW25", # H14
        "LA11_P"        : "H36",  # H16
        "LA11_N"        : "H37",  # H17
        "LA15_P"        : "F37",  # H19
        "LA15_N"        : "E37",  # H20
        "LA19_P"        : "C38",  # H22
        "LA19_N"        : "C39",  # H23
        "LA21_P"        : "B33",  # H25
        "LA21_N"        : "B34",  # H26
        "LA24_P"        : "AR22", # H28
        "LA24_N"        : "AT22", # H29
        "LA28_P"        : "E35",  # H31
        "LA28_N"        : "D35",  # H32
        "LA30_P"        : "AK22", # H34
        "LA30_N"        : "AK23", # H35
        "LA32_P"        : "G33",  # H37
        "LA32_N"        : "G34",  # H38
        "HA03_P"        : "AW7",  # J6
        "HA03_N"        : "AW6",  # J7
        "HA07_P"        : "AU5",  # J9
        "HA07_N"        : "AU4",  # J10
        "HA11_P"        : "AV4",  # J12
        "HA11_N"        : "AW4",  # J13
        "HA14_P"        : "AT8",  # J15
        "HA14_N"        : "AT7",  # J16
        "HA18_P"        : "AT5",  # J18
        "HA18_N"        : "AU9",  # J19
        "HA22_P"        : "AU8",  # J21
        "HA22_N"        : "AR5",  # J22
        "HA02_P"        : "AR4",  # K7
        "HA02_N"        : "AR7",  # K8
        "HA06_P"        : "AP7",  # K10
        "HA06_N"        : "AT6",  # K11
        "HA10_P"        : "AP4",  # K13
        "HA10_N"        : "AP5",  # K14
        "HA17_CC_P"     : "AP2",  # K16
        "HA17_CC_N"     : "AP1",  # K17
        "HA21_P"        : "AR3",  # K19
        "HA21_N"        : "AT3",  # K20
        "HA23_P"        : "AP6",  # K22
    }),
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
