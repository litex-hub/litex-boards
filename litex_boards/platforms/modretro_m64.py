#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause
#
# M64 MLB, schematic 100-0610 dated 2026-08-12:
# https://support.modretro.com/en_us/articles/m64-open-source-files-ByrpukdUGg
# https://github.com/ModRetro/oss-m64-console
# https://cdn.shopify.com/s/files/1/0829/2034/1806/files/M64_MLB_SCH.pdf?v=1786637413
# https://cdn.shopify.com/s/files/1/0829/2034/1806/files/M64_MLB_ASY.pdf?v=1786637413
#
# JTAG: J10, TC2050-IDC with TC2050-XILINX adapter, 1.8V (sheet 20).
# Pin 1: VREF, 2: TMS, 4: TCK, 6: TDO, 8: TDI, 3/5/7/9: GND, 10: NC.
# The STM32 controls the power rails, SD card and LEDs. The MT25QU256 configuration
# flash is shared with the MCU; FPGA access needs STARTUPE3 and MCU coordination.

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxUSPPlatform, VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst (sheets 3, 9, 10, 30).
    ("clk50",       0, Pins("AB21"), IOStandard("LVCMOS18")),
    ("cpu_reset_n", 0, Pins("AA13"), IOStandard("LVCMOS33")),

    # Programmable clocks from the 8T49N241, I2C address 0x7c (sheets 3, 8, 10).
    # Their schematic "100_" prefix denotes impedance, not a 100MHz frequency.
    ("clk_ref", 0,
        Subsignal("p", Pins("AD21")),
        Subsignal("n", Pins("AE21")),
        IOStandard("LVDS"), Misc("DIFF_TERM=TRUE"),
    ),
    ("clk_alt", 0,
        Subsignal("p", Pins("AD20")),
        Subsignal("n", Pins("AE20")),
        IOStandard("LVDS"), Misc("DIFF_TERM=TRUE"),
    ),
    ("clk_gth", 0,
        Subsignal("p", Pins("P7")),
        Subsignal("n", Pins("P6")),
    ),
    ("clkgen_i2c", 0,
        Subsignal("scl", Pins("AD25")),
        Subsignal("sda", Pins("AD26")),
        IOStandard("LVCMOS18"),
    ),
    ("clkgen", 0,
        Subsignal("rst_n", Pins("AB26")),
        Subsignal("int_n", Pins("AB25")),
        Subsignal("lol",   Pins("AC26")),
        IOStandard("LVCMOS18"),
    ),

    # Serial debug, J18 (unpopulated): pin 4 RX, 5 TX, 1 GND, 3.3V (sheets 9, 20).
    ("serial", 0,
        Subsignal("tx", Pins("W15")),
        Subsignal("rx", Pins("W12")),
        IOStandard("LVCMOS33"),
    ),

    # STM32 interfaces (sheets 9, 24).
    ("serial_mcu", 0,
        Subsignal("tx", Pins("AB14")),
        Subsignal("rx", Pins("AA14")),
        IOStandard("LVCMOS33"),
    ),
    ("spi_mcu", 0,
        Subsignal("clk",  Pins("AC13")),
        Subsignal("cs_n", Pins("AB16")),
        Subsignal("dq",   Pins("AC14 AB15 AA15 Y15")),
        IOStandard("LVCMOS33"),
    ),

    # PSRAM, x16 DDR, DQS/DM[1:0] (sheets 11, 12, 18, 19).
    ("psram", 0, # U2, APS256XXN-OB9-BG.
        Subsignal("clk",  Pins("D26")),
        Subsignal("cs_n", Pins("D24")),
        Subsignal("dq",   Pins("G25 F25 G24 H24 H23 H26 J26 G26 E25 E26 E23 D25 C26 C24 B26 B25")),
        Subsignal("dqs",  Pins("F24 D23")),
        IOStandard("LVCMOS18"), Misc("SLEW=FAST"),
    ),
    ("psram", 1, # U17, APS256XXN-OB9-BG.
        Subsignal("clk",  Pins("L23")),
        Subsignal("cs_n", Pins("M25")),
        Subsignal("dq",   Pins("L20 L19 J19 J20 J21 K21 M20 M21 K23 L24 M26 L25 K26 J24 K25 J23")),
        Subsignal("dqs",  Pins("M19 L22")),
        IOStandard("LVCMOS18"), Misc("SLEW=FAST"),
    ),
    ("psram", 2, # U11, APS256XXN-OB9-BG.
        Subsignal("clk",  Pins("T24")),
        Subsignal("cs_n", Pins("T25")),
        Subsignal("dq",   Pins("P19 R20 N19 N21 N23 R23 P20 R21 V26 U24 U25 R25 P25 R26 P26 N24")),
        Subsignal("dqs",  Pins("R22 U26")),
        IOStandard("LVCMOS18"), Misc("SLEW=FAST"),
    ),
    ("psram", 3, # U12, APS512XXN-OB9-BG.
        Subsignal("clk",  Pins("Y23")),
        Subsignal("cs_n", Pins("AA23")),
        Subsignal("dq",   Pins("V19 W19 U20 T22 T23 U21 W20 V22 W23 AA25 AA24 W24 Y26 Y25 W25 W26")),
        Subsignal("dqs",  Pins("V21 Y22")),
        IOStandard("LVCMOS18"), Misc("SLEW=FAST"),
    ),

    # HDMI, GTH bank 226 through SN75DP159 (sheets 7, 8, 13).
    ("hdmi", 0,
        Subsignal("clk_p",  Pins("G5")),
        Subsignal("clk_n",  Pins("G4")),
        Subsignal("data0_p", Pins("J5")),
        Subsignal("data0_n", Pins("J4")),
        Subsignal("data1_p", Pins("L5")),
        Subsignal("data1_n", Pins("L4")),
        Subsignal("data2_p", Pins("N5")),
        Subsignal("data2_n", Pins("N4")),
    ),
    ("hdmi_ctrl", 0,
        Subsignal("hpd",    Pins("J13")),
        Subsignal("oe",     Pins("H13")),
        Subsignal("pwr_en", Pins("J11")),
        Subsignal("cec",    Pins("J15")),
        IOStandard("LVCMOS33"),
    ),
    ("hdmi_i2c", 0,
        Subsignal("scl", Pins("D14")),
        Subsignal("sda", Pins("H14")),
        IOStandard("LVCMOS33"),
    ),
    ("hdmi_ddc", 0,
        Subsignal("scl", Pins("J12")),
        Subsignal("sda", Pins("H12")),
        IOStandard("LVCMOS33"),
    ),

    # N64 controller ports (sheets 5, 9).
    ("n64_controller", 0, Pins("AE13"), IOStandard("LVCMOS33")),
    ("n64_controller", 1, Pins("AD13"), IOStandard("LVCMOS33")),
    ("n64_controller", 2, Pins("AE15"), IOStandard("LVCMOS33")),
    ("n64_controller", 3, Pins("AD15"), IOStandard("LVCMOS33")),

    # User / Expansion IO, J25 (sheet 10).
    ("gpio", 0, Pins("J25:5 J25:6 J25:8 J25:9 J25:11 J25:12 J25:14 J25:15"), IOStandard("LVCMOS18")),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("J25", {
        5:  "AF22", # GPIO_BONUS_0.
        6:  "AE22", # GPIO_BONUS_1.
        8:  "AF25", # GPIO_BONUS_2.
        9:  "AF24", # GPIO_BONUS_3.
        11: "AE26", # GPIO_BONUS_4.
        12: "AE25", # GPIO_BONUS_5.
        14: "AC24", # GPIO_BONUS_6.
        15: "AB24", # GPIO_BONUS_7.
    }),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxUSPPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self, toolchain="vivado"):
        XilinxUSPPlatform.__init__(self, "xcau15p-ffvb676-2-e", _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment):
        XilinxUSPPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
        self.add_platform_command("set_property CONFIG_VOLTAGE 1.8 [current_design]")
