#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Greg Davill <greg.davill@gmail.com>
# Copyright (c) 2022 Goran Mahovlic <goran.mahovlic@gmail.com>
# Copyright (c) 2025 Gwenhael Goavec-merou<gwenhael.goavec-merou@trabucayre.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.lattice import LatticeECP5Platform
from litex.build.openfpgaloader import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk/Rst.
    ("clk25", 0, Pins("G2"), IOStandard("LVCMOS33")),
    ("rst_n", 0, Pins("F1"), IOStandard("LVCMOS33")),

    # Leds.
    ("user_led", 0, Pins("A3"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("B3"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("B2"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("C3"), IOStandard("LVCMOS33")),
    ("user_led", 4, Pins("C2"), IOStandard("LVCMOS33")),
    ("user_led", 5, Pins("C1"), IOStandard("LVCMOS33")),
    ("user_led", 6, Pins("D1"), IOStandard("LVCMOS33")),
    ("user_led", 7, Pins("D3"), IOStandard("LVCMOS33")),

    # Buttons.
    ("user_btn", 0, Pins("E1"), IOStandard("LVCMOS33")),
    ("user_btn", 1, Pins("D2"), IOStandard("LVCMOS33")),
    ("user_btn", 2, Pins("F1"), IOStandard("LVCMOS33")),

    # Switches
    ("user_sw", 0, Pins("L18"), IOStandard("LVCMOS33")),
    ("user_sw", 1, Pins("K18"), IOStandard("LVCMOS33")),

    # SDRAM.
    ("sdram_clock", 0, Pins("L20"), IOStandard("LVCMOS33")),
    ("sdram", 0,
        Subsignal("a",     Pins(
            "H16 D19 F16 E18 T19 T18 J16 P18",
            "T20 L19 C20 K19 R20")),
        Subsignal("ba",    Pins("J19 L16")),
        Subsignal("cs_n",  Pins("D20")),
        Subsignal("cke",   Pins("J17")),
        Subsignal("ras_n", Pins("G16")),
        Subsignal("cas_n", Pins("H20")),
        Subsignal("we_n",  Pins("E19")),
        Subsignal("dq",    Pins(
            "J18 G20 G19 E16 F19 F20 H18 F18",
            "P19 N17 M18 N20 N19 M20 M19 L17")),
        Subsignal("dqm",   Pins("E20 P20")),
        IOStandard("LVCMOS33"),
        Misc("SLEWRATE=FAST"),
    ),

    # USB.
    ("usb", 0,
        Subsignal("d_p",    Pins("F4")),
        Subsignal("d_n",    Pins("E3")),
        Subsignal("pullup", Pins("F5")),
        IOStandard("LVCMOS33")
    ),

    # Serial.
    ("serial", 0,
        Subsignal("rx",        Pins("N16"), Misc("PULLMODE=UP")),   # GPIO15
        Subsignal("tx",        Pins("N18"), Misc("PULLMODE=NONE")), # GPIO14
        Subsignal("tx_enable", Pins("T1"),  Misc("PULLMODE=UP")),
        IOStandard("LVCMOS33")
    ),

    # SPIFlash.
    ("spiflash", 0,
        Subsignal("cs_n", Pins("R2")),
        Subsignal("miso", Pins("V2")),
        Subsignal("mosi", Pins("W2")),
        Subsignal("wp",   Pins("Y2")),
        Subsignal("hold", Pins("W1")),
        IOStandard("LVCMOS33")
    ),
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("R2")),
        Subsignal("dq",   Pins("W2 V2 Y2 W1")),
        IOStandard("LVCMOS33")
    ),

    # SDCard.
    ("spisdcard", 0,
        Subsignal("clk",  Pins("G1")),
        Subsignal("mosi", Pins("P1"),  Misc("PULLMODE=UP")),
        Subsignal("cs_n", Pins("P2"),  Misc("PULLMODE=UP")),
        Subsignal("miso", Pins("B15"), Misc("PULLMODE=UP")),
        IOStandard("LVCMOS33"), Misc("SLEW=FAST")
    ),
    ("sdcard", 0,
        Subsignal("clk",  Pins("G1")),
        Subsignal("cmd",  Pins("P1"),             Misc("PULLMODE=UP")),
        Subsignal("data", Pins("B15 R16 E14 P2"), Misc("PULLMODE=UP")),
        IOStandard("LVCMOS33"), Misc("SLEW=FAST")
    ),
    
    # RMII Ethernet (LAN8720A).
    ("eth_clocks", 0,
        Subsignal("ref_clk", Pins("H2")),
        IOStandard("LVCMOS33"),
        Misc("PULLMODE=UP"),
    ),
    ("eth_phy_clk", 0, Pins("H4"), IOStandard("LVCMOS33"), Misc("PULLMODE=UP")),
    ("eth", 0,
        Subsignal("rst_n",   Pins("G5")),
        Subsignal("mdio",    Pins("E6")),
        Subsignal("mdc",     Pins("J5")),
        Subsignal("crs_dv",  Pins("J1")),
        Subsignal("rx_data", Pins("K1 K2")),
        Subsignal("tx_en",   Pins("K3")),
        Subsignal("tx_data", Pins("K5 J4")),
        IOStandard("LVCMOS33"), Misc("PULLMODE=UP DRIVE=4"),
    ),

    # GPDI
    ("gpdi", 0,
        Subsignal("clk_p",   Pins("J20")),
        #Subsignal("clk_n",   Pins("K20")),
        Subsignal("data0_p", Pins("F17")),
        #Subsignal("data0_n", Pins("G18")),
        Subsignal("data1_p", Pins("D18")),
        #Subsignal("data1_n", Pins("E17")),
        Subsignal("data2_p", Pins("C18")),
        #Subsignal("data2_n", Pins("D17")),
        IOStandard("LVCMOS33D"), Misc("DRIVE=4"),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    # RPI4 J1
    ("j1", {
        "GND"               : "---", #  1
        "GND"               : "---", #  2
        "ETH_3P"            : "Y7",  #  3
        "ETH_1P"            : "---", #  4
        "ETH_3N"            : "Y8",  #  5
        "ETH_1N"            : "---", #  6
        "GND"               : "---", #  7
        "GND"               : "---", #  8
        "ETH_2N"            : "W9",  #  9
        "ETH_0N"            : "---", # 10
        "ETH_2P"            : "W8",  # 11
        "ETH_0P"            : "---", # 12
        "GND"               : "---", # 13
        "GND"               : "---", # 14
        "ETH_LED3_n"        : "---", # 15
        "ETH_SYNC_in"       : "---", # 16
        "ETH_LED2_n"        : "---", # 17
        "ETH_SYNC_out"      : "---", # 18
        "ETH_LED1_n"        : "---", # 19
        "EEPROM_nWP"        : "---", # 20
        "PI_LED_ACTIVITY_n" : "---", # 21
        "GND"               : "---", # 22
        "GND"               : "---", # 23
        "GPIO26"            : "V1",  # 24
        "GPIO21"            : "L4",  # 25
        "GPIO19"            : "U1",  # 26
        "GPIO20"            : "L3",  # 27
        "GPIO13"            : "T1",  # 28
        "GPIO16"            : "L1",  # 29
        "GPIO6"             : "R1",  # 30
        "GPIO12"            : "L2",  # 31
        "GND"               : "---", # 32
        "GND"               : "---", # 33
        "GPIO5"             : "N1",  # 34
        "ID_SC"             : "J3",  # 35
        "ID_SD"             : "H1",  # 36
        "GPIO7"             : "P3",  # 37
        "GPIO11"            : "N2",  # 38
        "GPIO8"             : "P4",  # 39
        "GPIO9"             : "L5",  # 40
        "GPIO25"            : "P5",  # 41
        "GND"               : "---", # 42
        "GND"               : "---", # 43
        "GPIO10"            : "K4",  # 44
        "GPIO24"            : "N3",  # 45
        "GPIO22"            : "M3",  # 46
        "GPIO23"            : "N4",  # 47
        "GPIO27"            : "R17", # 48
        "GPIO18"            : "N5",  # 49
        "GPIO17"            : "---", # 50
        "GPIO15"            : "N16", # 51
        "GND"               : "---", # 52
        "GND"               : "---", # 53
        "GPIO4"             : "P16", # 54
        "GPIO14"            : "N18", # 55
        "GPIO3"             : "P17", # 56
        "SD_CLK"            : "G1",  # 57
        "GPIO2"             : "M17", # 58
        "GND"               : "---", # 59
        "GND"               : "---", # 60
        "SD_DAT3"           : "P2",  # 61
        "SD_CMD"            : "P1",  # 62
        "SD_DAT0"           : "B15", # 63
        "SD_DAT5"           : "---", # 64
        "GND"               : "---", # 65
        "GND"               : "---", # 66
        "SD_DAT1"           : "R16", # 67
        "SD_DAT4"           : "---", # 68
        "SD_DAT2"           : "E14", # 69
        "SD_DAT7"           : "---", # 70
        "GND"               : "---", # 71
        "SD_DAT6"           : "---", # 72
        "SD_VDD_Override"   : "---", # 73
        "GND"               : "---", # 74
        "SD_PWR_ON"         : "E15", # 75
        "NC1"               : "---", # 76
        "5V"                : "---", # 77
        "GPIO_VREF"         : "---", # 78
        "5V"                : "---", # 79
        "SCL0"              : "U17", # 80
        "5V"                : "---", # 81
        "SDA0"              : "T17", # 82
        "5V"                : "---", # 83
        "CM4_3V3"           : "---", # 84
        "5V"                : "---", # 85
        "CM4_3V3"           : "---", # 86
        "5V"                : "---", # 87
        "CM4_1V8"           : "---", # 88
        "WL_Disable_n"      : "---", # 89
        "CM4_1V8"           : "---", # 90
        "BT_Disable_n"      : "---", # 91
        "RUN_PG"            : "U16", # 92
        "RPI_BOOTn"         : "---", # 93
        "AnalogIP1"         : "---", # 94
        "PI_LED_nPWR"       : "---", # 95
        "ANAlogIP0"         : "---", # 96
        "Camera_GPIO"       : "U19", # 97
        "GND"               : "---", # 98
        "GLOBAL_EN"         : "U18", # 99
        "EXTRST_n"          : "U20", # 100
    }),

    # RPI4 J2
    ("j2", {
        "USB_OTG_ID"        : "D9",  #  1
        "PCIe_CLK_nREQ"     : "A10", #  2
        "USB_N"             : "B6",  #  3 (also on E3)
        "NC2"               : "---", #  4
        "USB_P"             : "A6",  #  5 (also on F4)
        "NC3"               : "---", #  6
        "GND"               : "---", #  7
        "GND"               : "---", #  8
        "PCIe_nRST"         : "A9",  #  9
        "PCIe_CLK_P"        : "Y11", # 10
        "VDAC_COMP"         : "---", # 11
        "PCIe_CLN_N"        : "Y12", # 12
        "GND"               : "---", # 13
        "GND"               : "---", # 14
        "CAM1_D0_N"         : "B4",  # 15
        "PCIe_RX_P"         : "Y5",  # 16
        "CAM1_D0_P"         : "C4",  # 17
        "PCIe_RX_N"         : "Y6",  # 18
        "GND"               : "---", # 19
        "GND"               : "---", # 20
        "CAM1_D1_N"         : "D5",  # 21
        "PCIe_TX_P"         : "W4",  # 22
        "CAM1_D1_P"         : "E4",  # 23
        "PCIe_TX_N"         : "W5",  # 24
        "GND"               : "---", # 25
        "GND"               : "---", # 26
        "CAM1_C_N"          : "F3",  # 27
        "CAM0_D0_N"         : "A5",  # 28
        "CAM1_C_P"          : "G3",  # 29
        "CAM0_D0_P"         : "A4",  # 30
        "GND"               : "---", # 31
        "GND"               : "---", # 32
        "CAM1_D2_N"         : "---", # 33
        "CAM0_D0_N"         : "A5",  # 34
        "CAM1_D2_P"         : "---", # 35
        "CAM0_D0_P"         : "A4",  # 36
        "GND"               : "---", # 37
        "GND"               : "---", # 38
        "CAM1_D3_N"         : "---", # 39
        "CAM0_C_N"          : "E2",  # 40
        "CAM1_D3_P"         : "---", # 41
        "CAM0_C_P"          : "F2",  # 42
        "HDMI1_HOTPLUG"     : "---", # 43
        "GND"               : "---", # 44
        "HDMI1_SDA"         : "---", # 45
        "HDMI1_TX2_P"       : "C8",  # 46
        "HDMI1_SCL"         : "---", # 47
        "HDMI1_TX2_N"       : "B8",  # 48
        "HDMI1_CEC"         : "---", # 49
        "GND"               : "---", # 50
        "HDMI0_CEC"         : "---", # 51
        "HDMI1_TX1_P"       : "A7",  # 52
        "HDMI0_HOTPLUG"     : "---", # 53
        "HDMI1_TX1_N"       : "A8",  # 54
        "GND"               : "---", # 55
        "GND"               : "---", # 56
        "DSI0_D0_N"         : "E13", # 57
        "HDMI1_TX0_P"       : "B9",  # 58
        "DSI0_D0_P"         : "D13", # 59
        "HDMI1_TX0_N"       : "C10", # 60
        "GND"               : "---", # 61
        "GND"               : "---", # 62
        "DSI0_D1_N"         : "C14", # 63
        "HDMI1_CLK_P"       : "B11", # 64
        "DSI0_D1_P"         : "A14", # 65
        "HDMI1_CLK_N"       : "C11", # 66
        "GND"               : "---", # 67
        "GND"               : "---", # 68
        "DSI0_C_N"          : "E12", # 69
        "HDMI0_TX2_P"       : "C18", # 70
        "DSI0_C_P"          : "D12", # 71
        "HDMI0_TX2_N"       : "D17", # 72
        "GND"               : "---", # 73
        "GND"               : "---", # 74
        "DSI1_D0_N"         : "E13", # 75 (shared with DSI0_D0_N)
        "HDMI0_TX1_P"       : "D18", # 76
        "DSI1_D0_P"         : "D13", # 77 (shared with DSI1_D0_P)
        "HDMI0_TX1_N"       : "E17", # 78
        "GND"               : "---", # 79
        "GND"               : "---", # 80
        "DSI1_D1_N"         : "C14", # 81 (shared with DSI0_D1_N)
        "HDMI0_TX0_P"       : "F17", # 82
        "DSI1_D1_P"         : "C14", # 83 (shared with DSI1_D1_P)
        "HDMI0_TX0_N"       : "G18", # 84
        "GND"               : "---", # 85
        "GND"               : "---", # 86
        "DSI1_C_N"          : "E12", # 87 (shared with DSI0_C_N)
        "HDMI0_CLK_P"       : "J20", # 88
        "DSI1_C_P"          : "D12", # 89 (shared with DSI0_C_P)
        "HDMI0_CLK_N"       : "K20", # 90
        "GND"               : "---", # 91
        "GND"               : "---", # 92
        "DSI1_D2_N"         : "B20", # 93
        "DSI1_D3_N"         : "B19", # 94
        "DSI1_D2_P"         : "A19", # 95
        "DSI1_D3_P"         : "A18", # 96
        "GND"               : "---", # 97
        "GND"               : "---", # 98
        "HDMI0_SDA"         : "---", # 99
        "HDMI0_SCL"         : "---", # 100
    }),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticeECP5Platform):
    default_clk_name   = "clk25"
    default_clk_period = 1e9/25e6

    def __init__(self, revision="0.1", device="85F", **kwargs):
        assert revision in ["0.1"]
        self.revision = revision
        LatticeECP5Platform.__init__(self, f"LFE5U-{device}-8BG381C", _io, _connectors, **kwargs)

    def create_programmer(self):
        return OpenFPGALoader("ulx4m_dfu")

    def do_finalize(self, fragment):
        LatticeECP5Platform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk25", loose=True), 1e9/25e6)
