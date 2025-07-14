#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 Samuele Baisi <samuele.baisi@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform, VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk200", 0,
        Subsignal("p", Pins("R4"), IOStandard("DIFF_SSTL15")),
        Subsignal("n", Pins("T4"), IOStandard("DIFF_SSTL15"))
    ),
    ("rst_n", 0, Pins("P15"), IOStandard("LVCMOS33")), # the closest button to the sdcard reader


    # Leds
    ("user_led", 0, Pins("H15"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("J15"), IOStandard("LVCMOS33")),

    # # Switches  # better to be left alone for now
    # ("user_sw", 0, Pins("A8"),  IOStandard("LVCMOS33")),
    # ("user_sw", 1, Pins("C11"), IOStandard("LVCMOS33")),
    # ("user_sw", 2, Pins("C10"), IOStandard("LVCMOS33")),
    # ("user_sw", 3, Pins("A10"), IOStandard("LVCMOS33")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("T18")),
        Subsignal("rx", Pins("R18")),
        IOStandard("LVCMOS33")
    ),

    # EEPROM
    ("eeprom", 0,
        Subsignal("scl", Pins("K17"), Misc("PULLUP true")),
        Subsignal("sda", Pins("J17"), Misc("PULLUP true")),
        IOStandard("LVCMOS33")
    ),

    # SPI SDCard
    ("spisdcard", 0,
        Subsignal("mosi", Pins("Y21")),
        Subsignal("miso", Pins("P19")),
        Subsignal("clk",  Pins("V20")),
        Subsignal("cs_n", Pins("U18")),
        IOStandard("LVCMOS33"),
    ),

    # SDCard
    ("sdcard", 0,
        Subsignal("data", Pins("P19 R19 U17 U18")),
        Subsignal("cmd",  Pins("Y21")),
        Subsignal("clk",  Pins("V20")),
        Subsignal("cd",   Pins("AA19")),
        IOStandard("LVCMOS33"),
    ),

    # Buttons
    ("user_btn", 0, Pins("P17"), IOStandard("LVCMOS33")),
    ("user_btn", 1, Pins("N17"), IOStandard("LVCMOS33")),
    # ("user_btn", 2, Pins("P15"), IOStandard("LVCMOS33")),  # used for reset

    # SPIFlash
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("T19")),
        Subsignal("dq",   Pins("P22 R22 P21 R21 ")),
        IOStandard("LVCMOS33")
    ),

    # DDR3 SDRAM
    # single chip, 256 MB
    ("ddram", 0,
        Subsignal("a",       Pins(
            "V2 Y4 Y3 AB5 AB3 AA4 AA1 AA3 AB1 W2 W5 W1 AB6 Y2 Y1"),
            IOStandard("SSTL15")),
        Subsignal("ba",      Pins("AA5 W4 AB7"), IOStandard("SSTL15")),
        Subsignal("ras_n",   Pins("Y8"),         IOStandard("SSTL15")),
        Subsignal("cas_n",   Pins("AA8"),        IOStandard("SSTL15")),
        Subsignal("we_n",    Pins("AA6"),        IOStandard("SSTL15")),
        Subsignal("cs_n",    Pins("Y7"),         IOStandard("SSTL15")),
        Subsignal("dm",      Pins("M6 J4"),      IOStandard("SSTL15")),
        Subsignal("dq",      Pins(
                "R1 M5 P2 P6 N4 N5 N2 P1 L5 K3 K6 J6 M2 L3 M3 L4",
        ),
            IOStandard("SSTL15"),
        ),
        Subsignal("dqs_p",   Pins("P5 M1"),
            IOStandard("DIFF_SSTL15"),
        ),
        Subsignal("dqs_n",   Pins("P4 L1"),
            IOStandard("DIFF_SSTL15"),
        ),
        Subsignal("clk_p",   Pins("T5"),  IOStandard("DIFF_SSTL15")),
        Subsignal("clk_n",   Pins("U5"),  IOStandard("DIFF_SSTL15")),
        Subsignal("cke",     Pins("Y9"),  IOStandard("SSTL15")),
        Subsignal("odt",     Pins("AB8"), IOStandard("SSTL15")),
        Subsignal("reset_n", Pins("AB2"), IOStandard("LVCMOS15")),
        # Misc("SLEW=FAST"),
    ),
    # both chips, 512 MB
    ("ddram", 1,
        Subsignal("a",       Pins(
            "V2 Y4 Y3 AB5 AB3 AA4 AA1 AA3 AB1 W2 W5 W1 AB6 Y2 Y1"),
            IOStandard("SSTL15")),
        Subsignal("ba",      Pins("AA5 W4 AB7"),  IOStandard("SSTL15")),
        Subsignal("ras_n",   Pins("Y8"),          IOStandard("SSTL15")),
        Subsignal("cas_n",   Pins("AA8"),         IOStandard("SSTL15")),
        Subsignal("we_n",    Pins("AA6"),         IOStandard("SSTL15")),
        Subsignal("cs_n",    Pins("Y7"),          IOStandard("SSTL15")),
        Subsignal("dm",      Pins("M6 J4 H2 B1"), IOStandard("SSTL15")),
        Subsignal("dq",      Pins(
                "R1 M5 P2 P6 N4 N5 N2 P1 L5 K3 K6 J6 M2 L3 M3 L4",
                "G4 G3 J5 H3 H4 K1 H5 G2 E2 A1 G1 B2 F1 C2 F3 D2",
        ),
            IOStandard("SSTL15"),
        ),
        Subsignal("dqs_p",   Pins("P5 M1 K2 E1"),
            IOStandard("DIFF_SSTL15"),
        ),
        Subsignal("dqs_n",   Pins("P4 L1 J2 D1"),
            IOStandard("DIFF_SSTL15"),
        ),
        Subsignal("clk_p",   Pins("T5"),  IOStandard("DIFF_SSTL15")),
        Subsignal("clk_n",   Pins("U5"),  IOStandard("DIFF_SSTL15")),
        Subsignal("cke",     Pins("Y9"),  IOStandard("SSTL15")),
        Subsignal("odt",     Pins("AB8"), IOStandard("SSTL15")),
        Subsignal("reset_n", Pins("AB2"), IOStandard("LVCMOS15")),
        # Misc("SLEW=FAST"),
    ),

    # RGMII Ethernet (the first port is the closest to the power switch)
    ("eth_clocks", 0,
        Subsignal("rx", Pins("W19")),
        Subsignal("tx", Pins("W20")),
        IOStandard("LVCMOS33"),
    ),
    ("eth_clocks", 1,
        Subsignal("rx", Pins("Y18")),
        Subsignal("tx", Pins("Y19")),
        IOStandard("LVCMOS33"),
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("Y22")),
        Subsignal("mdio",    Pins("V17")),
        Subsignal("mdc",     Pins("W17")),
        Subsignal("rx_ctl",  Pins("V18")),
        Subsignal("rx_data", Pins("U22 V22 T21 U21")),
        Subsignal("tx_ctl",  Pins("U20")),
        Subsignal("tx_data", Pins("W21 W22 AA20 AA21")),
        # Subsignal("col",     Pins("D17")),
        # Subsignal("crs",     Pins("G14")),
        IOStandard("LVCMOS33"),
    ),
    ("eth", 1,
        Subsignal("rst_n",   Pins("AB20")),
        Subsignal("mdio",    Pins("P14")),
        Subsignal("mdc",     Pins("R14")),
        Subsignal("rx_ctl",  Pins("V19")),
        Subsignal("rx_data", Pins("AB21 AB22 AA18 AB18")),
        Subsignal("tx_ctl",  Pins("P20")),
        Subsignal("tx_data", Pins("N13 N14 P16 R17")),
        # Subsignal("col",     Pins("D17")),
        # Subsignal("crs",     Pins("G14")),
        IOStandard("LVCMOS33"),
    ),

    # PCIe.
    ("pcie_x1", 0,
        Subsignal("rst_n", Pins("R16"), IOStandard("LVCMOS33"), Misc("PULLUP=TRUE")),
        Subsignal("clk_p", Pins("F6")),
        Subsignal("clk_n", Pins("E6")),
        Subsignal("rx_p",  Pins("B4")),
        Subsignal("rx_n",  Pins("A4")),
        Subsignal("tx_p",  Pins("B8")),
        Subsignal("tx_n",  Pins("A8"))
    ),
    ("pcie_x2", 0,
        Subsignal("rst_n", Pins("R16"), IOStandard("LVCMOS33"), Misc("PULLUP=TRUE")),
        Subsignal("clk_p", Pins("F6")),
        Subsignal("clk_n", Pins("E6")),
        Subsignal("rx_p",  Pins("B4 D5")),
        Subsignal("rx_n",  Pins("A4 C5")),
        Subsignal("tx_p",  Pins("B8 D11")),
        Subsignal("tx_n",  Pins("A8 C11"))
    ),

    # SFP+
    ("gtp_refclk", 0,
        Subsignal("p", Pins("F6")),
        Subsignal("n", Pins("E6"))
    ),
    ("gtp_refclk", 1,
        Subsignal("p", Pins("F10")),
        Subsignal("n", Pins("E10"))
    ),
    ("sfp", 0,
        Subsignal("rxp", Pins("B6")),
        Subsignal("rxn", Pins("A6")),
        Subsignal("txp", Pins("B10")),
        Subsignal("txn", Pins("A10")),
    ),
    ("sfp", 1,
        Subsignal("rxp", Pins("D7")),
        Subsignal("rxn", Pins("C7")),
        Subsignal("txp", Pins("D9")),
        Subsignal("txn", Pins("C9")),
    ),

    # HDMI Out
    ("hdmi_out", 0,
        Subsignal("clk",     Pins("J21")),
        Subsignal("de",      Pins("H19")),
        Subsignal("hsync",   Pins("J19")),
        Subsignal("vsync",   Pins("J20")),
        Subsignal("scl",     Pins("L19"), Misc("PULLUP true")),
        Subsignal("sda",     Pins("L20"), Misc("PULLUP true")),
        Subsignal("rst_n",   Pins("K18")),
        Subsignal("r",       Pins("L18 M18 N18 N19 N20 M20 K13 K14")),
        Subsignal("g",       Pins("H17 H18 J22 H22 H20 G20 K21 K22")),
        Subsignal("b",       Pins("H13 G13 G15 G16 J14 H14 G17 G18")),
        Subsignal("int",     Pins("K19"), Misc("PULLUP true")),
        IOStandard("LVCMOS33"),
    ),

    # HDMI In
    ("hdmi_in", 0,
        Subsignal("clk",     Pins("C19")),
        Subsignal("de",      Pins("C18")),
        Subsignal("hsync",   Pins("C17")),
        Subsignal("vsync",   Pins("D12")),
        Subsignal("scl",     Pins("E22"), Misc("PULLUP true")),
        Subsignal("sda",     Pins("D22"), Misc("PULLUP true")),
        Subsignal("rst_n",   Pins("F15")),
        Subsignal("r",       Pins("A13 A14 B20 A20 A18 A19 D20 C20")),
        Subsignal("g",       Pins("E13 E14 D14 D15 C13 B13 A15 A16")),
        Subsignal("b",       Pins("F13 F14 F16 E17 C14 C15 E16 D16")),
        Subsignal("int",     Pins("F21")),
        IOStandard("LVCMOS33"),
    )
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = []


# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk200"
    default_clk_period = 1e9/200e6

    def __init__(self, toolchain="vivado"):
        device = "xc7a100tfgg484-1"
        Xilinx7SeriesPlatform.__init__(self, device, _io, _connectors, toolchain=toolchain)
        self.toolchain.bitstream_commands = \
            [
                "set_property CFGBVS VCCO [current_design]",
                "set_property CONFIG_VOLTAGE 3.3 [current_design]",
                "set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]",
                "set_property CONFIG_MODE SPIx4 [current_design]",
                "set_property BITSTREAM.CONFIG.CONFIGRATE 50 [current_design]",

            ]
        self.toolchain.additional_commands = \
            ["write_cfgmem -force -format bin -interface spix4 -size 16 "
             "-loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"]

    def create_programmer(self):
        return VivadoProgrammer(flash_part='mx25l25673g-spi-x1_x2_x4')

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk200", loose=True), 5e8/100e6)
