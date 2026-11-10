#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 Gwenhael Goavec-Merou <gwenhael.goavec-merou@trabucayre.com>
# Copyright (c) 2026 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# AMD/Xilinx Kria KR260 Robotics Starter Kit (K26 SOM, XCK26).
#
# The SOM240_1/SOM240_2 connectors map the K26 SOM's pins to the XCK26's balls (AMD's board files:
# XilinxBoardStore kr260_som/1.1 part0_pins); the carrier's IOs are described on these connectors
# (kr260_carrier/1.0 board.xml, cross-checked with AMD's KR260 platforms' XDCs). The SFP+ cage's
# data lanes are not described there and are not included.

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxUSPPlatform, VivadoProgrammer


# IOs ----------------------------------------------------------------------------------------------

_io = [
]

_connectors = [
    ("som240_1", {
        "a3":  "A2",
        "a4":  "A1",
        "a6":  "C3",
        "a7":  "C2",
        "a9":  "G6",
        "a10": "F6",
        "a12": "G8",
        "a13": "F7",
        "a15": "F11",
        "a16": "J12",
        "a17": "H12",
        "b1":  "C1",
        "b2":  "B1",
        "b4":  "E4",
        "b5":  "E3",
        "b7":  "B3",
        "b8":  "A3",
        "b10": "E5",
        "b11": "D5",
        "b16": "J10",
        "b17": "K13",
        "b18": "K12",
        "b20": "B10",
        "b21": "E12",
        "b22": "D11",
        "c3":  "G1",
        "c4":  "F1",
        "c6":  "G3",
        "c7":  "F3",
        "c9":  "B4",
        "c10": "A4",
        "c12": "D7",
        "c13": "D6",
        "c18": "H11",
        "c19": "G10",
        "c20": "F12",
        "c22": "B11",
        "c23": "A10",
        "c24": "A12",
        "d4":  "F2",
        "d5":  "E2",
        "d7":  "E1",
        "d8":  "D1",
        "d10": "D4",
        "d11": "C4",
        "d13": "F8",
        "d14": "E8",
        "d16": "G11",
        "d17": "F10",
        "d18": "J11",
        "d20": "E10",
        "d21": "D10",
        "d22": "C11",
    }),
    ("som240_2", {
        "a3":  "N4",
        "a4":  "N3",
        "a7":  "V6",
        "a8":  "V5",
        "a11": "J5",
        "a12": "J4",
        "a14": "H4",
        "a15": "H3",
        "a17": "N7",
        "a18": "N6",
        "a20": "J1",
        "a21": "H1",
        "a23": "J7",
        "a24": "H7",
        "a26": "H9",
        "a27": "H8",
        "a29": "AG6",
        "a30": "AG5",
        "a32": "AH2",
        "a33": "AH1",
        "a35": "AB2",
        "a36": "AC2",
        "a38": "AG4",
        "a39": "AH4",
        "a41": "AD7",
        "a42": "AE7",
        "a46": "W10",
        "a47": "Y10",
        "a48": "Y9",
        "a50": "AA8",
        "a51": "AB10",
        "a52": "AB9",
        "a54": "Y14",
        "a55": "Y13",
        "a56": "W12",
        "a58": "W11",
        "a59": "Y12",
        "a60": "AA12",
        "b1":  "T2",
        "b2":  "T1",
        "b5":  "R4",
        "b6":  "R3",
        "b9":  "Y2",
        "b10": "Y1",
        "b12": "L7",
        "b13": "L6",
        "b15": "K2",
        "b16": "J2",
        "b18": "L1",
        "b19": "K1",
        "b21": "M6",
        "b22": "L5",
        "b24": "R8",
        "b25": "T8",
        "b27": "AF8",
        "b28": "AG8",
        "b30": "AD2",
        "b31": "AD1",
        "b33": "AG3",
        "b34": "AH3",
        "b36": "AH8",
        "b37": "AH7",
        "b39": "AE2",
        "b40": "AF2",
        "b44": "AD11",
        "b45": "AD10",
        "b46": "AA11",
        "b48": "AA10",
        "b49": "AB11",
        "b50": "AC11",
        "b52": "AA13",
        "b53": "AB13",
        "b54": "W14",
        "b56": "W13",
        "b57": "AB15",
        "b58": "AB14",
        "c3":  "Y6",
        "c4":  "Y5",
        "c7":  "U4",
        "c8":  "U3",
        "c11": "K4",
        "c12": "K3",
        "c14": "N9",
        "c15": "N8",
        "c17": "U8",
        "c18": "V8",
        "c20": "P7",
        "c21": "P6",
        "c23": "K9",
        "c24": "J9",
        "c26": "AE3",
        "c27": "AF3",
        "c29": "AD5",
        "c30": "AD4",
        "c32": "AC4",
        "c33": "AC3",
        "c35": "AB4",
        "c36": "AB3",
        "c38": "AG9",
        "c39": "AH9",
        "c41": "AE5",
        "c42": "AF5",
        "c46": "AH12",
        "c47": "AH11",
        "c48": "AC12",
        "c50": "AD12",
        "c51": "AE10",
        "c52": "AF10",
        "c54": "AG13",
        "c55": "AH13",
        "c56": "AC14",
        "c58": "AC13",
        "c59": "AE13",
        "c60": "AF13",
        "d1":  "V2",
        "d2":  "V1",
        "d5":  "P2",
        "d6":  "P1",
        "d9":  "W4",
        "d10": "W3",
        "d12": "U9",
        "d13": "V9",
        "d15": "W8",
        "d16": "Y8",
        "d18": "L3",
        "d19": "L2",
        "d21": "R7",
        "d22": "T7",
        "d24": "K8",
        "d25": "K7",
        "d27": "AF7",
        "d28": "AF6",
        "d30": "AE9",
        "d31": "AE8",
        "d33": "AC9",
        "d34": "AD9",
        "d36": "AB8",
        "d37": "AC8",
        "d39": "AB7",
        "d40": "AC7",
        "d44": "AE12",
        "d45": "AF12",
        "d46": "AG10",
        "d48": "AH10",
        "d49": "AF11",
        "d50": "AG11",
        "d52": "AD15",
        "d53": "AD14",
        "d54": "AE15",
        "d56": "AE14",
        "d57": "AG14",
        "d58": "AH14",
    }),
]

# Carrier IOs --------------------------------------------------------------------------------------

_io_carrier = [
    # 25MHz single-ended clocks exposed by the carrier.
    ("clk25", 0, Pins("som240_1:a6"),  IOStandard("LVCMOS18")),
    ("clk25", 1, Pins("som240_2:d18"), IOStandard("LVCMOS18")),

    # Fan (active low enable).
    ("fan_en_b", 0, Pins("som240_1:c24"), IOStandard("LVCMOS33")),

    # Board LEDs.
    ("gem2_led", 0, Pins("som240_1:b4"),  IOStandard("LVCMOS18")),
    ("gem2_led", 1, Pins("som240_1:b5"),  IOStandard("LVCMOS18")),
    ("gem2_led", 2, Pins("som240_1:b1"),  IOStandard("LVCMOS18")),
    ("sfp_led",  0, Pins("som240_1:a12"), IOStandard("LVCMOS18")),
    ("sfp_led",  1, Pins("som240_1:a13"), IOStandard("LVCMOS18")),
    ("user_led", 0, Pins("som240_1:d13"), IOStandard("LVCMOS18")),
    ("user_led", 1, Pins("som240_1:d14"), IOStandard("LVCMOS18")),
    ("gem3_led", 0, Pins("som240_2:d21"), IOStandard("LVCMOS18")),
    ("gem3_led", 1, Pins("som240_2:d22"), IOStandard("LVCMOS18")),
    ("gem3_led", 2, Pins("som240_2:b18"), IOStandard("LVCMOS18")),

    # Carrier PHY #0 (GEM2) connected to SOM240_1.
    ("eth_clocks", 0,
        Subsignal("tx", Pins("som240_1:a3")),
        Subsignal("rx", Pins("som240_1:d10")),
        IOStandard("LVCMOS18")
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("som240_1:b2")),
        Subsignal("mdio",    Pins("som240_1:c7")),
        Subsignal("mdc",     Pins("som240_1:c6")),
        Subsignal("rx_ctl",  Pins("som240_1:c10")),
        Subsignal("rx_data", Pins("som240_1:a4 som240_1:b7 som240_1:b8 som240_1:c9")),
        Subsignal("tx_ctl",  Pins("som240_1:c4")),
        Subsignal("tx_data", Pins("som240_1:d7 som240_1:d8 som240_1:d4 som240_1:d5")),
        IOStandard("LVCMOS18")
    ),

    # Carrier PHY #1 (GEM3) connected to SOM240_2.
    ("eth_clocks", 1,
        Subsignal("tx", Pins("som240_2:a20")),
        Subsignal("rx", Pins("som240_2:c11")),
        IOStandard("LVCMOS18")
    ),
    ("eth", 1,
        Subsignal("rst_n",   Pins("som240_2:b19")),
        Subsignal("mdio",    Pins("som240_2:b25")),
        Subsignal("mdc",     Pins("som240_2:b24")),
        Subsignal("rx_ctl",  Pins("som240_2:a15")),
        Subsignal("rx_data", Pins("som240_2:a21 som240_2:b15 som240_2:b16 som240_2:a14")),
        Subsignal("tx_ctl",  Pins("som240_2:d16")),
        Subsignal("tx_data", Pins("som240_2:d12 som240_2:d13 som240_2:c17 som240_2:c18")),
        IOStandard("LVCMOS18")
    ),

    # Carrier-side I2C bus.
    ("i2c_main", 0,
        Subsignal("sda", Pins("som240_1:d16")),
        Subsignal("scl", Pins("som240_1:d17")),
        IOStandard("LVCMOS33")
    ),

    # SFP+ cage: GTH quad 224 lane 2, 156.25 MHz reference clock on MGTREFCLK0_224 (from the
    # carrier), status/control and I2C on the 3.3V HD banks 43/45.
    ("sfp", 0,
        Subsignal("txp", Pins("som240_2:b5")), # MGTHTXP2_224.
        Subsignal("txn", Pins("som240_2:b6")), # MGTHTXN2_224.
        Subsignal("rxp", Pins("som240_2:b1")), # MGTHRXP2_224.
        Subsignal("rxn", Pins("som240_2:b2")), # MGTHRXN2_224.
    ),
    ("sfp_tx", 0,
        Subsignal("p", Pins("som240_2:b5")),
        Subsignal("n", Pins("som240_2:b6")),
    ),
    ("sfp_rx", 0,
        Subsignal("p", Pins("som240_2:b1")),
        Subsignal("n", Pins("som240_2:b2")),
    ),
    ("sfp_refclk", 0,
        Subsignal("p", Pins("som240_2:c3")), # MGTREFCLK0P_224.
        Subsignal("n", Pins("som240_2:c4")), # MGTREFCLK0N_224.
    ),
    ("sfp_tx_fault",   0, Pins("som240_1:c23"), IOStandard("LVCMOS33")),
    ("sfp_tx_disable", 0, Pins("som240_2:a47"), IOStandard("LVCMOS33")),
    ("sfp_mod_abs",    0, Pins("som240_2:a46"), IOStandard("LVCMOS33")),
    ("sfp_los",        0, Pins("som240_1:a16"), IOStandard("LVCMOS33")),
    ("sfp_i2c", 0,
        Subsignal("sda", Pins("som240_2:b50")),
        Subsignal("scl", Pins("som240_2:b49")),
        IOStandard("LVCMOS33")
    ),
]

_connectors_carrier = [
    ("pmod1", "som240_1:a17 som240_1:d20 som240_1:d21 som240_1:d22 som240_1:b20 som240_1:b21 som240_1:b22 som240_1:c22"),
    ("pmod2", "som240_1:d18 som240_1:b16 som240_1:b17 som240_1:b18 som240_1:c18 som240_1:c19 som240_1:c20 som240_1:a15"),
    ("pmod3", "som240_2:d44 som240_2:d45 som240_2:d46 som240_2:d48 som240_2:d49 som240_2:d50 som240_2:c46 som240_2:c47"),
    ("pmod4", "som240_2:c48 som240_2:c50 som240_2:c51 som240_2:c52 som240_2:b44 som240_2:b45 som240_2:b46 som240_2:b48"),

    # Raspberry Pi header (J21, 40 pins, 3.3V: HD banks 43/44), by header pin number.
    ("RASP", {
         1: "--",           # 3V3
         2: "--",           # 5V0
         3: "som240_2:d54", # GPIO2  (SDA)
         4: "--",           # 5V0
         5: "som240_2:d56", # GPIO3  (SCL)
         6: "--",           # GND
         7: "som240_2:d57", # GPIO4  (GPCLK0)
         8: "som240_2:b54", # GPIO14 (TXD)
         9: "--",           # GND
        10: "som240_2:b56", # GPIO15 (RXD)
        11: "som240_2:b58", # GPIO17
        12: "som240_2:a54", # GPIO18 (PCM_CLK)
        13: "som240_2:a52", # GPIO27
        14: "--",           # GND
        15: "som240_2:a59", # GPIO22
        16: "som240_2:a60", # GPIO23
        17: "--",           # 3V3
        18: "som240_2:a48", # GPIO24
        19: "som240_2:c59", # GPIO10 (MOSI)
        20: "--",           # GND
        21: "som240_2:c58", # GPIO9  (MISO)
        22: "som240_2:a50", # GPIO25
        23: "som240_2:c60", # GPIO11 (SCLK)
        24: "som240_2:c56", # GPIO8  (CE0)
        25: "--",           # GND
        26: "som240_2:c55", # GPIO7  (CE1)
        27: "som240_2:d52", # GPIO0  (ID_SD)
        28: "som240_2:d53", # GPIO1  (ID_SC)
        29: "som240_2:d58", # GPIO5
        30: "--",           # GND
        31: "som240_2:c54", # GPIO6
        32: "som240_2:b52", # GPIO12 (PWM0)
        33: "som240_2:b53", # GPIO13 (PWM1)
        34: "--",           # GND
        35: "som240_2:a55", # GPIO19 (PCM_FS)
        36: "som240_2:b57", # GPIO16
        37: "som240_2:a51", # GPIO26
        38: "som240_2:a56", # GPIO20 (PCM_DIN)
        39: "--",           # GND
        40: "som240_2:a58", # GPIO21 (PCM_DOUT)
    }),
]

# PSU config ---------------------------------------------------------------------------------------
psu_config = {
    "PSU_BANK_0_IO_STANDARD":                    "LVCMOS18",
    "PSU_BANK_1_IO_STANDARD":                    "LVCMOS18",
    "PSU_BANK_2_IO_STANDARD":                    "LVCMOS18",
    "PSU_BANK_3_IO_STANDARD":                    "LVCMOS18",

    "PSU__GPIO0_MIO__IO":                        "MIO 0 .. 25",
    "PSU__GPIO0_MIO__PERIPHERAL__ENABLE":        "1",
    "PSU__GPIO1_MIO__IO":                        "MIO 26 .. 51",
    "PSU__GPIO1_MIO__PERIPHERAL__ENABLE":        "1",

    "PSU__QSPI__PERIPHERAL__ENABLE":             "1",
    "PSU__QSPI__PERIPHERAL__DATA_MODE":          "x4",
    "PSU__QSPI__PERIPHERAL__IO":                 "MIO 0 .. 5",
    "PSU__QSPI__PERIPHERAL__MODE":               "Single",
    "PSU__QSPI__GRP_FBCLK__ENABLE":              "0",
    "PSU__CRL_APB__QSPI_REF_CTRL__SRCSEL":       "IOPLL",
    "PSU__CRL_APB__QSPI_REF_CTRL__FREQMHZ":      "125",

    "PSU__SPI1__PERIPHERAL__ENABLE":             "1",
    "PSU__SPI1__GRP_SS1__ENABLE":                "0",
    "PSU__CRL_APB__SPI1_REF_CTRL__SRCSEL":       "IOPLL",
    "PSU__CRL_APB__SPI1_REF_CTRL__FREQMHZ":      "200",

    "PSU__DISPLAYPORT__PERIPHERAL__ENABLE":      "1",
    "PSU__DPAUX__PERIPHERAL__ENABLE":            "1",
    "PSU__DPAUX__PERIPHERAL__IO":                "MIO 27 .. 30",
    "PSU__DP__LANE_SEL":                         "Single Lower",
    "PSU__DP__REF_CLK_SEL":                      "Ref Clk1",
    "PSU__DP__REF_CLK_FREQ":                     "27",
    "PSU__CRF_APB__DP_VIDEO_REF_CTRL__SRCSEL":   "VPLL",
    "PSU__CRF_APB__DP_VIDEO_REF_CTRL__FREQMHZ":  "300",
    "PSU__CRF_APB__DP_AUDIO_REF_CTRL__SRCSEL":   "RPLL",
    "PSU__CRF_APB__DP_AUDIO_REF_CTRL__FREQMHZ":  "25",
    "PSU__CRF_APB__DP_STC_REF_CTRL__SRCSEL":     "RPLL",
    "PSU__CRF_APB__DP_STC_REF_CTRL__FREQMHZ":    "27",

    "PSU__PMU__PERIPHERAL__ENABLE":              "1",
    "PSU__PMU__GPO0__ENABLE":                    "0",
    "PSU__PMU__GPO1__ENABLE":                    "0",
    "PSU__PMU__GPO2__ENABLE":                    "0",
    "PSU__PMU__GPO3__ENABLE":                    "1",
    "PSU__PMU__GPO4__ENABLE":                    "0",
    "PSU__PMU__GPO5__ENABLE":                    "0",
    "PSU__PMU__GPI0__ENABLE":                    "1",
    "PSU__PMU__GPI1__ENABLE":                    "0",
    "PSU__PMU__GPI2__ENABLE":                    "0",
    "PSU__PMU__GPI3__ENABLE":                    "0",
    "PSU__PMU__GPI4__ENABLE":                    "0",
    "PSU__PMU__GPI5__ENABLE":                    "1",

    "PSU_MIO_45_PULLUPDOWN":                     "disable",
    "PSU_MIO_47_PULLUPDOWN":                     "disable",
    "PSU_MIO_49_PULLUPDOWN":                     "disable",
    "PSU_MIO_34_DIRECTION":                      "inout",
    "PSU_MIO_43_DIRECTION":                      "inout",
    "PSU_MIO_44_DIRECTION":                      "inout",
    "PSU_MIO_0_DRIVE_STRENGTH":                  "4",
    "PSU_MIO_1_DRIVE_STRENGTH":                  "4",
    "PSU_MIO_2_DRIVE_STRENGTH":                  "4",
    "PSU_MIO_3_DRIVE_STRENGTH":                  "4",
    "PSU_MIO_4_DRIVE_STRENGTH":                  "4",
    "PSU_MIO_5_DRIVE_STRENGTH":                  "4",
    "PSU_MIO_6_DRIVE_STRENGTH":                  "4",
    "PSU_MIO_7_DRIVE_STRENGTH":                  "4",
    "PSU_MIO_8_DRIVE_STRENGTH":                  "4",
    "PSU_MIO_9_DRIVE_STRENGTH":                  "4",
    "PSU_MIO_10_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_11_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_12_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_13_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_14_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_15_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_16_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_17_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_18_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_19_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_20_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_21_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_22_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_23_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_24_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_25_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_27_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_29_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_32_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_33_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_34_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_35_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_36_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_38_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_39_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_40_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_41_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_42_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_43_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_44_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_46_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_47_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_48_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_49_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_50_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_51_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_54_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_56_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_57_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_58_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_59_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_60_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_61_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_62_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_63_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_64_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_65_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_66_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_67_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_68_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_69_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_70_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_71_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_72_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_73_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_74_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_75_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_76_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_77_DRIVE_STRENGTH":                 "4",
    "PSU_MIO_0_SLEW":                            "slow",
    "PSU_MIO_1_SLEW":                            "slow",
    "PSU_MIO_2_SLEW":                            "slow",
    "PSU_MIO_3_SLEW":                            "slow",
    "PSU_MIO_4_SLEW":                            "slow",
    "PSU_MIO_5_SLEW":                            "slow",
    "PSU_MIO_6_SLEW":                            "slow",
    "PSU_MIO_7_SLEW":                            "slow",
    "PSU_MIO_8_SLEW":                            "slow",
    "PSU_MIO_9_SLEW":                            "slow",
    "PSU_MIO_10_SLEW":                           "slow",
    "PSU_MIO_11_SLEW":                           "slow",
    "PSU_MIO_12_SLEW":                           "slow",
    "PSU_MIO_13_SLEW":                           "slow",
    "PSU_MIO_14_SLEW":                           "slow",
    "PSU_MIO_15_SLEW":                           "slow",
    "PSU_MIO_16_SLEW":                           "slow",
    "PSU_MIO_17_SLEW":                           "slow",
    "PSU_MIO_18_SLEW":                           "slow",
    "PSU_MIO_19_SLEW":                           "slow",
    "PSU_MIO_20_SLEW":                           "slow",
    "PSU_MIO_21_SLEW":                           "slow",
    "PSU_MIO_22_SLEW":                           "slow",
    "PSU_MIO_23_SLEW":                           "slow",
    "PSU_MIO_24_SLEW":                           "slow",
    "PSU_MIO_25_SLEW":                           "slow",
    "PSU_MIO_27_SLEW":                           "slow",
    "PSU_MIO_29_SLEW":                           "slow",
    "PSU_MIO_32_SLEW":                           "slow",
    "PSU_MIO_33_SLEW":                           "slow",
    "PSU_MIO_34_SLEW":                           "slow",
    "PSU_MIO_35_SLEW":                           "slow",
    "PSU_MIO_36_SLEW":                           "slow",
    "PSU_MIO_38_SLEW":                           "slow",
    "PSU_MIO_39_SLEW":                           "slow",
    "PSU_MIO_40_SLEW":                           "slow",
    "PSU_MIO_41_SLEW":                           "slow",
    "PSU_MIO_42_SLEW":                           "slow",
    "PSU_MIO_43_SLEW":                           "slow",
    "PSU_MIO_44_SLEW":                           "slow",
    "PSU_MIO_46_SLEW":                           "slow",
    "PSU_MIO_47_SLEW":                           "slow",
    "PSU_MIO_48_SLEW":                           "slow",
    "PSU_MIO_49_SLEW":                           "slow",
    "PSU_MIO_50_SLEW":                           "slow",
    "PSU_MIO_51_SLEW":                           "slow",
    "PSU_MIO_54_SLEW":                           "slow",
    "PSU_MIO_56_SLEW":                           "slow",
    "PSU_MIO_57_SLEW":                           "slow",
    "PSU_MIO_58_SLEW":                           "slow",
    "PSU_MIO_59_SLEW":                           "slow",
    "PSU_MIO_60_SLEW":                           "slow",
    "PSU_MIO_61_SLEW":                           "slow",
    "PSU_MIO_62_SLEW":                           "slow",
    "PSU_MIO_63_SLEW":                           "slow",
    "PSU_MIO_64_SLEW":                           "slow",
    "PSU_MIO_65_SLEW":                           "slow",
    "PSU_MIO_66_SLEW":                           "slow",
    "PSU_MIO_67_SLEW":                           "slow",
    "PSU_MIO_68_SLEW":                           "slow",
    "PSU_MIO_69_SLEW":                           "slow",
    "PSU_MIO_70_SLEW":                           "slow",
    "PSU_MIO_71_SLEW":                           "slow",
    "PSU_MIO_72_SLEW":                           "slow",
    "PSU_MIO_73_SLEW":                           "slow",
    "PSU_MIO_74_SLEW":                           "slow",
    "PSU_MIO_75_SLEW":                           "slow",
    "PSU_MIO_76_SLEW":                           "slow",
    "PSU_MIO_77_SLEW":                           "slow",

    "PSU__DDRC__VREF":                           "1",
    "PSU__DDRC__ECC":                            "Disabled",
    "PSU__DDRC__BUS_WIDTH":                      "64 Bit",
    "PSU__DDRC__DRAM_WIDTH":                     "16 Bits",
    "PSU__DDRC__MEMORY_TYPE":                    "DDR 4",
    "PSU__DDRC__COMPONENTS":                     "Components",
    "PSU__DDRC__SPEED_BIN":                      "DDR4_2400R",
    "PSU__DDRC__DEVICE_CAPACITY":                "8192 MBits",
    "PSU__DDRC__RANK_ADDR_COUNT":                "0",
    "PSU__DDRC__BG_ADDR_COUNT":                  "1",
    "PSU__DDRC__BANK_ADDR_COUNT":                "2",
    "PSU__DDRC__ROW_ADDR_COUNT":                 "16",
    "PSU__DDRC__COL_ADDR_COUNT":                 "10",
    "PSU__DDRC__CL":                             "16",
    "PSU__DDRC__CWL":                            "14",
    "PSU__DDRC__T_RCD":                          "16",
    "PSU__DDRC__T_RP":                           "16",
    "PSU__DDRC__T_RC":                           "47.06",
    "PSU__DDRC__T_RAS_MIN":                      "33",
    "PSU__DDRC__T_FAW":                          "30.0",
    "PSU__DDRC__DDR4_T_REF_MODE":                "0",
    "PSU__DDRC__DDR4_T_REF_RANGE":               "Normal (0-85)",
    "PSU__DDRC__PHY_DBI_MODE":                   "0",
    "PSU__DDRC__PARITY_ENABLE":                  "0",
    "PSU__DDRC__CLOCK_STOP_EN":                  "0",
    "PSU__DDRC__DDR4_CAL_MODE_ENABLE":           "0",
    "PSU__DDRC__DDR4_CRC_CONTROL":               "0",
    "PSU__DDRC__TRAIN_DATA_EYE":                 "1",
    "PSU__DDRC__TRAIN_READ_GATE":                "1",
    "PSU__DDRC__TRAIN_WRITE_LEVEL":              "1",
    "PSU__DDRC__DDR4_ADDR_MAPPING":              "0",
    "PSU__DDRC__BRC_MAPPING":                    "ROW_BANK_COL",
    "PSU__DDRC__DM_DBI":                         "DM_NO_DBI",
    "PSU__DDRC__PER_BANK_REFRESH":               "0",
    "PSU__DDRC__FGRM":                           "1X",
    "PSU__DDRC__LP_ASR":                         "manual normal",
    "PSU__DDRC__DIMM_ADDR_MIRROR":               "0",
    "PSU__DDRC__STATIC_RD_MODE":                 "0",
    "PSU__DDRC__SELF_REF_ABORT":                 "0",

    "PSU__PSS_REF_CLK__FREQMHZ":                 "33.333",

    "PSU__OVERRIDE__BASIC_CLOCK":                "0",

    "PSU__CRF_APB__APLL_CTRL__SRCSEL":           "PSS_REF_CLK",
    "PSU__CRF_APB__DPLL_CTRL__SRCSEL":           "PSS_REF_CLK",
    "PSU__CRF_APB__VPLL_CTRL__SRCSEL":           "PSS_REF_CLK",
    "PSU__CRL_APB__IOPLL_CTRL__SRCSEL":          "PSS_REF_CLK",
    "PSU__CRL_APB__RPLL_CTRL__SRCSEL":           "PSS_REF_CLK",
    "PSU__CRF_APB__DDR_CTRL__SRCSEL":            "DPLL",
    "PSU__CRF_APB__DDR_CTRL__FREQMHZ":           "1200",
    "PSU__CRL_APB__CPU_R5_CTRL__SRCSEL":         "RPLL",
    "PSU__CRL_APB__CPU_R5_CTRL__FREQMHZ":        "533.333",
    "PSU__CRF_APB__ACPU_CTRL__SRCSEL":           "APLL",
    "PSU__CRF_APB__ACPU__FRAC_ENABLED":          "1",
    "PSU__CRF_APB__ACPU_CTRL__FREQMHZ":          "1333.333",
    "PSU__CRF_APB__GPU_REF_CTRL__SRCSEL":        "IOPLL",
    "PSU__CRF_APB__GPU_REF_CTRL__FREQMHZ":       "600",

    "PSU__SWDT0__PERIPHERAL__ENABLE":            "1",
    "PSU__SWDT1__PERIPHERAL__ENABLE":            "1",

    "PSU__TTC0__PERIPHERAL__ENABLE":             "1",
    "PSU__IOU_SLCR__IOU_TTC_APB_CLK__TTC0_SEL":  "APB",
    "PSU__TTC1__PERIPHERAL__ENABLE":             "1",
    "PSU__IOU_SLCR__IOU_TTC_APB_CLK__TTC1_SEL":  "APB",
    "PSU__TTC2__PERIPHERAL__ENABLE":             "1",
    "PSU__IOU_SLCR__IOU_TTC_APB_CLK__TTC2_SEL":  "APB",
    "PSU__TTC3__PERIPHERAL__ENABLE":             "1",
    "PSU__IOU_SLCR__IOU_TTC_APB_CLK__TTC3_SEL":  "APB",

    # PL0 clk
    "PSU__CRL_APB__PL0_REF_CTRL__SRCSEL":        "IOPLL",
    "PSU__CRL_APB__PL0_REF_CTRL__FREQMHZ":       "100",

    # PL1 clk
    "PSU__FPGA_PL1_ENABLE":                      "1",
    "PSU__CRL_APB__PL1_REF_CTRL__SRCSEL":        "IOPLL",
    "PSU__CRL_APB__PL1_REF_CTRL__FREQMHZ":       "100",

    "PSU__CRL_APB__DBG_LPD_CTRL__SRCSEL":        "IOPLL",
    "PSU__CRL_APB__DBG_LPD_CTRL__FREQMHZ":       "250",
    "PSU__CRF_APB__DBG_FPD_CTRL__SRCSEL":        "IOPLL",
    "PSU__CRF_APB__DBG_FPD_CTRL__FREQMHZ":       "250",
    "PSU__CRF_APB__DBG_TRACE_CTRL__SRCSEL":      "IOPLL",
    "PSU__CRF_APB__DBG_TRACE_CTRL__FREQMHZ":     "250",
    "PSU__CRF_APB__DBG_TSTMP_CTRL__SRCSEL":      "IOPLL",
    "PSU__CRF_APB__DBG_TSTMP_CTRL__FREQMHZ":     "250",
    "PSU__CRL_APB__IOU_SWITCH_CTRL__SRCSEL":     "IOPLL",
    "PSU__CRL_APB__IOU_SWITCH_CTRL__FREQMHZ":    "250",
    "PSU__CRL_APB__LPD_SWITCH_CTRL__SRCSEL":     "IOPLL",
    "PSU__CRL_APB__LPD_SWITCH_CTRL__FREQMHZ":    "500",
    "PSU__CRL_APB__LPD_LSBUS_CTRL__SRCSEL":      "IOPLL",
    "PSU__CRL_APB__LPD_LSBUS_CTRL__FREQMHZ":     "100",
    "PSU__CRL_APB__TIMESTAMP_REF_CTRL__SRCSEL":  "IOPLL",
    "PSU__CRL_APB__TIMESTAMP_REF_CTRL__FREQMHZ": "100",
    "PSU__CRL_APB__PCAP_CTRL__SRCSEL":           "IOPLL",
    "PSU__CRL_APB__PCAP_CTRL__FREQMHZ":          "200",
    "PSU__CRL_APB__ADMA_REF_CTRL__SRCSEL":       "IOPLL",
    "PSU__CRL_APB__ADMA_REF_CTRL__FREQMHZ":      "500",
    "PSU__CRF_APB__DPDMA_REF_CTRL__SRCSEL":      "APLL",
    "PSU__CRF_APB__DPDMA_REF_CTRL__FREQMHZ":     "600",
    "PSU__CRF_APB__GDMA_REF_CTRL__SRCSEL":       "DPLL",
    "PSU__CRF_APB__GDMA_REF_CTRL__FREQMHZ":      "600",
    "PSU__CRF_APB__TOPSW_MAIN_CTRL__SRCSEL":     "DPLL",
    "PSU__CRF_APB__TOPSW_MAIN_CTRL__FREQMHZ":    "533.33",
    "PSU__CRF_APB__TOPSW_LSBUS_CTRL__SRCSEL":    "IOPLL",
    "PSU__CRF_APB__TOPSW_LSBUS_CTRL__FREQMHZ":   "100",

    "PSU__ENET0__PERIPHERAL__ENABLE":            "1",
    "PSU__ENET0__PERIPHERAL__IO":                "GT Lane0",
    "PSU__CRL_APB__GEM0_REF_CTRL__SRCSEL":       "IOPLL",
    "PSU__CRL_APB__GEM0_REF_CTRL__FREQMHZ":      "125",
    "PSU__GEM0__REF_CLK_SEL":                    "Ref Clk0",
    "PSU__GEM0__REF_CLK_FREQ":                   "125",

    "PSU__ENET1__PERIPHERAL__ENABLE":            "1",
    "PSU__ENET1__PERIPHERAL__IO":                "MIO 38 .. 49",
    "PSU__ENET1__GRP_MDIO__ENABLE":              "1",
    "PSU__ENET1__GRP_MDIO__IO":                  "MIO 50 .. 51",
    "PSU__CRL_APB__GEM1_REF_CTRL__SRCSEL":       "IOPLL",
    "PSU__CRL_APB__GEM1_REF_CTRL__FREQMHZ":      "125",

    "PSU__CRL_APB__GEM_TSU_REF_CTRL__SRCSEL":    "IOPLL",
    "PSU__CRL_APB__GEM_TSU_REF_CTRL__FREQMHZ":   "250",

    "PSU__DISPLAYPORT__LANE0__ENABLE":           "1",
    "PSU__DISPLAYPORT__LANE0__IO":               "GT Lane1",

    "PSU__USB0__PERIPHERAL__ENABLE":             "1",
    "PSU__USB0__PERIPHERAL__IO":                 "MIO 52 .. 63",
    "PSU__CRL_APB__USB0_BUS_REF_CTRL__SRCSEL":   "IOPLL",
    "PSU__CRL_APB__USB0_BUS_REF_CTRL__FREQMHZ":  "250",
    "PSU__USB3_0__PERIPHERAL__ENABLE":           "1",
    "PSU__USB3_0__PERIPHERAL__IO":               "GT Lane2",
    "PSU__USB0__REF_CLK_SEL":                    "Ref Clk2",
    "PSU__USB0__REF_CLK_FREQ":                   "26",
    "PSU__USB1__PERIPHERAL__ENABLE":             "1",
    "PSU__USB1__PERIPHERAL__IO":                 "MIO 64 .. 75",
    "PSU__CRL_APB__USB1_BUS_REF_CTRL__SRCSEL":   "IOPLL",
    "PSU__CRL_APB__USB1_BUS_REF_CTRL__FREQMHZ":  "250",
    "PSU__USB1__RESET__ENABLE":                  "1",
    "PSU__USB1__RESET__IO":                      "MIO 77",
    "PSU__USB3_1__PERIPHERAL__ENABLE":           "1",
    "PSU__USB3_1__PERIPHERAL__IO":               "GT Lane3",
    "PSU__USB1__REF_CLK_SEL":                    "Ref Clk3",
    "PSU__USB1__REF_CLK_FREQ":                   "26",
    "PSU__USB__RESET__MODE":                     "Separate MIO Pin",
    "PSU__USB0__RESET__ENABLE":                  "1",
    "PSU__USB0__RESET__IO":                      "MIO 76",
    "PSU__CRL_APB__USB3_DUAL_REF_CTRL__SRCSEL":  "IOPLL",
    "PSU__CRL_APB__USB3_DUAL_REF_CTRL__FREQMHZ": "20",
}

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxUSPPlatform):
    default_clk_name   = "clk25"
    default_clk_period = 1e9/25e6

    def __init__(self, toolchain="vivado"):
        XilinxUSPPlatform.__init__(self, "xck26-sfvc784-2lv-c", _io, _connectors, toolchain=toolchain)

        # PSU config.
        self.psu_config = psu_config

        # Carrier IOs/Connector.
        self.add_extension(_io_carrier)
        self.add_connector(_connectors_carrier)

        self.toolchain.bitstream_commands = [
            "set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]",
        ]
        self.default_clk_freq = 1e9 / self.default_clk_period

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment, *args, **kwargs):
        XilinxUSPPlatform.do_finalize(self, fragment, *args, **kwargs)
        self.add_period_constraint(self.lookup_request("clk25", 0, loose=True), 1e9/25e6)
        self.add_period_constraint(self.lookup_request("clk25", 1, loose=True), 1e9/25e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:rx", 0, loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:rx", 1, loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("sfp_refclk", 0, loose=True), 1e9/156.25e6)
