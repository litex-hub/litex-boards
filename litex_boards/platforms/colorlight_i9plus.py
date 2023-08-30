#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2023 Charles-Henri Mousset <ch.mousset@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk.
    ("clk25", 0, Pins("K4"), IOStandard("LVCMOS33")),

    # Leds.
    ("user_led", 0, Pins("A18"), IOStandard("LVCMOS33")),

    # RGMII Ethernet (B50612D) PHY 0.
    ("eth_clocks", 0, # U5 is SDIO phy #0
        Subsignal("tx", Pins("A1")),
        Subsignal("rx", Pins("H4")),
        IOStandard("LVCMOS33")
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("H2")),
        Subsignal("mdio",    Pins("G2")),
        Subsignal("mdc",     Pins("G1")),
        Subsignal("rx_ctl",  Pins("F1")),
        Subsignal("rx_data", Pins("E3 E2 E1 F3")),
        Subsignal("tx_ctl",  Pins("D1")),
        Subsignal("tx_data", Pins("B2 B1 C2 D2")),
        IOStandard("LVCMOS33")
    ),
    # RGMII Ethernet (B50612D) PHY 1.
    ("eth_clocks", 1, # U9 is SDIO phy #1
        Subsignal("tx", Pins("M6")),
        Subsignal("rx", Pins("L3")),
        IOStandard("LVCMOS33")
    ),
    ("eth", 1,
        Subsignal("rst_n",   Pins("H2")),
        Subsignal("mdio",    Pins("G2")),
        Subsignal("mdc",     Pins("G1")),
        Subsignal("rx_ctl",  Pins("R1")),
        Subsignal("rx_data", Pins("N2 N3 P1 P2")),
        Subsignal("tx_ctl",  Pins("N5")),
        Subsignal("tx_data", Pins("M5 M2 N4 P4")),
        IOStandard("LVCMOS33")
    ),
    # SDRRAM (M12L64322A).
    ("sdram_clock", 0, Pins("E14"), IOStandard("LVCMOS33")),
    ("sdram", 0,
        Subsignal("a", Pins(
            "C20 C19 C13 F13 G13 G15 "
            "F14 F18 E13 E18 C14 A13")),  # Address pin A11 routed but NC on M12L64322A
        Subsignal("dq", Pins(
            "F21 E22 F20 E21 F19 D22 E19 D21 "
            "K21 L21 K22 M21 L20 M22 N20 M20 "
            "B18 D20 A19 A21 A20 B21 C22 B22 "
            "G21 G22 H20 H22 J20 J22 G20 J21 "
            )),
        Subsignal("we_n",  Pins("D17")),
        Subsignal("ras_n", Pins("A14")),
        Subsignal("cas_n", Pins("D14")),
        #Subsignal("cs_n", Pins("")), # GND
        #Subsignal("cke",  Pins("")), # 3V3
        Subsignal("ba",    Pins("D19 B13")),
        #Subsignal("dm",   Pins("")), # GND
        IOStandard("LVCMOS33"),
        Misc("SLEWRATE=FAST")
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("dimm",
        "- "
        "    GND      5V     GND      5V     GND      5V     GND      5V     GND      5V"  #   1-10
        "    GND      5V      NC      NC ETH1_1P ETH2_1P ETH1_1N ETH2_1N      NC      NC"  #  11-20
        "ETH1_2N ETH2_2N ETH1_2P ETH2_2P      NC      NC ETH1_3P ETH2_3P ETH1_3N ETH2_3N"  #  21-30
        "     NC      NC ETH1_4N ETH2_4N ETH1_4P ETH2_4P      NC      NC     GND     GND"  #  31-40
        "     R2      P5      P6      T6      R6      U7      T1      U6      T3      U5"  #  41-50
        "     T4      V5      T4      U1     GND     GND      U2      H3      U3      J1"  #  51-60
        "     V2      K1      V3      L1      W1      M1      Y1      J2     AA1      K2"  #  61-70
        "    AB1      K3      W2      G3      Y2      J4     AB2      G4     AA3      F4"  #  71-80
        "    AB3      L4      Y3      R3      W4      M3     AA4      V4      Y4      R4"  #  81-90
        "    AB5      T5     AA5      J5      Y6      J6     AB6      W5     AA6      L5"  #  91-100
        "     Y7      L6     AB7      W6     GND     GND     GND     GND     AA8      V7"  # 101-110
        "    AB8     N13      Y8     N14      W7     P15      Y9     P16      V8     R16"  # 111-120
        "     W9     N17      V9     V17     R14     P17     P14     U17     W17     T18"  # 121-130
        "    Y18     R17    AA18     U18     W19     R18    AB18     N18     Y19     R19"  # 131-140
        "   AA19     N19     V18     N15     V19     M16    AB20     M15    AA20     L15"  # 141-150
        "   AA21     L16    AB21     K14     Y21     N22     GND     GND    AB22     J14"  # 151-160
        "    W20     J15     Y22     J19     W21     H13     W22     H14     V20     H17"  # 161-170
        "    V22     H15     U21     G18     U20     G17     T20     G16     P19     F16"  # 171-180
        "    P20     F15     M18     E17     L19     E16     J17     D16     K18     D15"  # 181-190
        "    K19     C18     K16     C17     H18     B20     H19     B17      NC      NC"  # 191-200
    )
]

def pmod_uart(port="P2"):
    if port == "P2":
        return [
        ("serial", 0,
            Subsignal("tx", Pins("dimm:41")),
            Subsignal("rx", Pins("dimm:51")),
            IOStandard("LVCMOS33"))
        ]
    else:
        raise ValueError(f"port {port} not in ['P2']")

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk25"
    default_clk_period = 1e9/25e6

    def __init__(self, toolchain="vivado"):
        Xilinx7SeriesPlatform.__init__(self, "xc7a50tfgg484-1", _io, _connectors, toolchain=toolchain)
        self.toolchain.bitstream_commands = \
            ["set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]"]
        self.toolchain.additional_commands = \
            ["write_cfgmem -force -format bin -interface spix4 -size 16 "
             "-loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"]


    def create_programmer(self, cfg="openocd_xc7_ft2232.cfg"):
        return OpenOCD(cfg, "bscan_spi_xc7a50t.bit")

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request(self.default_clk_name, loose=True), self.default_clk_period)
