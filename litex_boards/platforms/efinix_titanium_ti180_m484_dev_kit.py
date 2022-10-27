#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Franck Jullien <franck.jullien@collshade.fr>
# Copyright (c) 2022 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.efinix.platform import EfinixPlatform
from litex.build.efinix import EfinixProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk
    # ("clk25", 0, Pins("J22"), IOStandard("1.8_V_LVCMOS")), # GPIOT_P_11 CAUTION! unconnected in dev kit
    ("clk33", 0, Pins("K17"), IOStandard("1.8_V_LVCMOS")), # GPIOL_32
    ("clk50", 0, Pins("C1"), IOStandard("1.8_V_LVCMOS")), # GPIOB_P_11
    ("clk74_25", 0, Pins("L16"), IOStandard("1.8_V_LVCMOS")), # GPIOL_26

    # SD-Card
    ("spisdcard", 0,
        # Subsignal("clk",  Pins("B12")), # GPIOR_15 CLK
        # Subsignal("mosi", Pins("C12"), Misc("WEAK_PULLUP")), # GPIOR_16 CMD
        # Subsignal("cs_n", Pins("A12"), Misc("WEAK_PULLUP")), # GPIOR_13 CD/DAT3
        # Subsignal("miso", Pins("B14"), Misc("WEAK_PULLUP")), # GPIOR_18 DAT0
        Subsignal("clk",  Pins("F16")), # GPIOR_62 CLK
        Subsignal("mosi", Pins("F17"), Misc("WEAK_PULLUP")), # GPIOR_60 CMD
        Subsignal("cs_n", Pins("G17"), Misc("WEAK_PULLUP")), # GPIOR_59 CD/DAT3
        Subsignal("miso", Pins("G15"), Misc("WEAK_PULLUP")), # GPIOR_61 DAT0
        IOStandard("1.8_V_LVCMOS"),
    ),
    ("sdcard", 0,
        # Subsignal("data", Pins("B14 A14 D12 A12"), Misc("WEAK_PULLUP")),
        # Subsignal("cmd",  Pins("C12"), Misc("WEAK_PULLUP")),
        # Subsignal("clk",  Pins("B12")),
        Subsignal("data", Pins("G15 F15 H15 G17"), Misc("WEAK_PULLUP")),
        Subsignal("cmd",  Pins("F17"), Misc("WEAK_PULLUP")),
        Subsignal("clk",  Pins("F16")),
        IOStandard("1.8_V_LVCMOS"),
    ),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("G10")), # UART_TXD GPIOR_67
        Subsignal("rx", Pins("F8")), # UART_RXD GPIOR_68
        IOStandard("3.3_V_LVCMOS"), Misc("WEAK_PULLUP")
    ),

    # Leds
    # ("user_led", 0,
    #     Subsignal("r", Pins("J15")),
    #     Subsignal("g", Pins("H10")),
    #     Subsignal("b", Pins("K14")),
    #     IOStandard("1.8_V_LVCMOS"),
    # ),
    # ("user_led", 1,
    #     Subsignal("r", Pins("H15")),
    #     Subsignal("g", Pins("H11")),
    #     Subsignal("b", Pins("J14")),
    #     IOStandard("1.8_V_LVCMOS"),
    # ),
    # led1 CDONE
    ("user_led", 0, Pins("E1"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=3")), # led2 GPIOB_N_02
    ("user_led", 1, Pins("F1"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=3")), # led3 GPIOB_P_02
    ("user_led", 2, Pins("C2"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=3")), # led4 GPIOB_P_13
    ("user_led", 3, Pins("E3"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=3")), # led5 GPIOB_P_14
    ("user_led", 4, Pins("B1"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=3")), # led6 GPIOB_N_11
    ("user_led", 5, Pins("B2"), IOStandard("3.3_V_LVTTL_/_LVCMOS"), Misc("DRIVE_STRENGTH=3")), # led7 GPIOB_P_12

    # Buttons
    ("user_btn", 0, Pins("D2"), IOStandard("1.8_V_LVCMOS")), # sw3 GPIOB_N_13
    ("user_btn", 1, Pins("E4"), IOStandard("1.8_V_LVCMOS")), # sw4 GPIOB_N_14

    # Switches
    # ("user_sw", 0, Pins("F3"), IOStandard("1.8_V_LVCMOS")),
    # ("user_sw", 1, Pins("E3"), IOStandard("1.8_V_LVCMOS")),

    # SPIFlash
    ("spiflash", 0,
        # Subsignal("cs_n", Pins("P1")), # GPIOL_P_01 SSL_N
        # Subsignal("clk",  Pins("N1")), # GPIOL_N_01 CCK
        # Subsignal("mosi", Pins("M1")), # GPIOL_P_03 CDI0
        # Subsignal("miso", Pins("L1")), # GPIOL_N_03 CDI1
        Subsignal("cs_n", Pins("E2")), # GPIOB_P_08 SSL_N
        Subsignal("clk",  Pins("J2")), # GPIOB_N_01 CCK
        Subsignal("mosi", Pins("G2")), # GPIOB_P_09 CDI0
        Subsignal("miso", Pins("H2")), # GPIOB_N_09 CDI1
        IOStandard("1.8_V_LVCMOS")
    ),

    # HyperRAM (X16)
    # ("hyperram", 0,
    #     Subsignal("dq",  Pins(
    #         "B6 C6 A5 A6  F7  F8  E7  D7",
    #         "B9 A9 F9 E9 C10 D10 A10 B10"
    #     ), IOStandard("1.8_V_LVCMOS")),
    #     Subsignal("rwds",  Pins("B8 C8"), IOStandard("1.8_V_LVCMOS")),
    #     Subsignal("cs_n",  Pins("A8"),    IOStandard("1.8_V_LVCMOS")),
    #     Subsignal("rst_n", Pins("D5"),    IOStandard("1.8_V_LVCMOS")),
    #     Subsignal("clk",   Pins("B7"),    IOStandard("1.8_V_LVCMOS")),
    #     Misc("SLEWRATE=FAST")
    # ),

    # MIPI
    # ("mipi_tx", 0,
    #     Subsignal("clk",   Pins("D13"), IOStandard("1.2_V_LVCMOS")),
    #     Subsignal("data0", Pins("C15"), IOStandard("1.2_V_LVCMOS")),
    #     Subsignal("data1", Pins("D14"), IOStandard("1.2_V_LVCMOS")),
    #     Subsignal("data2", Pins("E14"), IOStandard("1.2_V_LVCMOS")),
    #     Subsignal("data3", Pins("E12"), IOStandard("1.2_V_LVCMOS")),
    #     Misc("SLEWRATE=FAST")
    # ),

    # MIPI
    # ("mipi_rx", 0,
    #     Subsignal("clk",   Pins("M15"), IOStandard("1.2_V_LVCMOS")),
    #     Subsignal("data0", Pins("K11"), IOStandard("1.2_V_LVCMOS")),
    #     Subsignal("data1", Pins("L13"), IOStandard("1.2_V_LVCMOS")),
    #     Misc("SLEWRATE=FAST")
    # ),

    # ("cam_i2c", 0,
    #     Subsignal("sda",   Pins("H4"), Misc("WEAK_PULLUP")),
    #     Subsignal("scl",   Pins("H5"), Misc("WEAK_PULLUP")),
    #     Subsignal("reset", Pins("R14")),
    #     IOStandard("1.8_V_LVCMOS")
    # ),

    # RGMII Ethernet
    # Use P1 socket
    # ("eth_clocks", 0,
    #     Subsignal("tx", Pins("G11")), # GPIOR_P_14
    #     Subsignal("rx", Pins("C14")), # GPIOR_P_19_PLLIN0
    #     IOStandard("1.8_V_LVCMOS")
    # ),

    # ("eth", 0,
    #     Subsignal("rx_ctl",  Pins("D14")), # GPIOR_N_18
    #     Subsignal("rx_data", Pins("D13 C13 E14 E15")), # GPIOR_N_17, P_17, N_16, P_16
    #     Subsignal("tx_ctl",  Pins("G15")), # GPIOR_P_13
    #     Subsignal("tx_data", Pins("H12 H13 F13 G13")), # GPIOR_N_10_CLK9_N, P_10_CLK9_P, N_12, P_12
    #     Subsignal("rst_n",   Pins("B5")), # GPIOL_10
    #     Subsignal("mdc",     Pins("J3")), # GPIOL_N_05
    #     Subsignal("mdio",    Pins("K4")), # GPIOL_P_05
    #     IOStandard("1.8_V_LVCMOS")
    # ),
]

iobank_info = [
            # ("1A", "1.8 V LVCMOS"),
            # ("1B", "1.8 V LVCMOS"),
            ("2A_2B_2C", "1.8 V LVCMOS"),
            ("3A", "1.8 V LVCMOS"),
            ("3B_3C", "1.8 V LVCMOS"),
            ("4A", "1.8 V LVCMOS"),
            ("4B", "1.8 V LVCMOS"),
            ("4C", "1.8 V LVCMOS"),
            ("BL", "1.8 V LVCMOS"),
            ("BR", "3.3 V LVCMOS"),
            ("TL", "1.8 V LVCMOS"),
            ("TR", "1.8 V LVCMOS"),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    # ["P1", " - H14 - G14 - - F12 G13 E12 F13 - - E15 H13 E14 H12 - - C13 G15 D13 F15",
    #        " - - D15 G11 D14 F11 - - C14 N14 C15 P14 - - K4 A4 J3 B5"],
]

# Platform -----------------------------------------------------------------------------------------

class Platform(EfinixPlatform):
    # default_clk_name   = "clk25"
    # default_clk_period = 1e9/25e6
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self, toolchain="efinity"):
        EfinixPlatform.__init__(self, "Ti180M484C4", _io, _connectors, iobank_info=iobank_info, toolchain=toolchain)

    def create_programmer(self):
        return EfinixProgrammer()

    def do_finalize(self, fragment):
        EfinixPlatform.do_finalize(self, fragment)
        # self.add_period_constraint(self.lookup_request("clk25", loose=True), 1e9/25e6)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
