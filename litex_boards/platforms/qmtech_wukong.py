#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Shinken Sanada <sanadashinken@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

# IOs specific to V1 of the board
_io_v1 = [
    # Reset (Key1 button)
    ("cpu_reset",  0, Pins("J8"),  IOStandard("LVCMOS33")),  # key1

    #Clock
    ("clk50"   ,   0, Pins("M22"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led",   0, Pins("J6"),   IOStandard("LVCMOS33")),
    ("user_led",   1, Pins("H6"),   IOStandard("LVCMOS33")),
]

# IOs specific to V2 of the board
_io_v2 = [
    # Reset (Key1 button)
    ("cpu_reset",  0, Pins("M6"),  IOStandard("LVCMOS33")),

    # Clock
    ("clk50"   ,   0, Pins("M21"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led",   0, Pins("V16"),   IOStandard("LVCMOS33")),
    ("user_led",   1, Pins("V17"),   IOStandard("LVCMOS33")),

    # SD-Card
    ("sdcard", 0,
     Subsignal("data", Pins("M5 M7 H6 J6")),
     Subsignal("cmd",  Pins("J8")),
     Subsignal("clk",  Pins("L4")),
     Subsignal("cd",   Pins("N6")),
     Misc("SLEW=FAST"),
     IOStandard("LVCMOS33"),
     ),
]

# IO commons to both versions of the board
_io_common = [
    # Key0 button (Key1 is used as cpu reset and is version specific)
    ("user_btn",   0, Pins("H7"),   IOStandard("LVCMOS33")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("E3")),
        Subsignal("rx", Pins("F3")),
        IOStandard("LVCMOS33"),
    ),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("P18")),
        Subsignal("clk",  Pins("H13")),
        Subsignal("mosi", Pins("R14")),
        Subsignal("miso", Pins("R15")),
        Subsignal("wp",   Pins("P14")),
        Subsignal("hold", Pins("N14")),
        IOStandard("LVCMOS33"),
    ),
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("P18")),
        Subsignal("clk",  Pins("H13")),
        Subsignal("dq",   Pins("R14 R15 P14 N14")),
        IOStandard("LVCMOS33")
    ),

    # DDR3 SDRAM
    ("ddram", 0,
        Subsignal("a", Pins(
            "E17 G17 F17 C17 G16 D16 H16 E16",
            "H14 F15 F20 H15 C18 G15"),
            IOStandard("SSTL135")),
        Subsignal("ba",    Pins("B17 D18 A17"), IOStandard("SSTL135")),
        Subsignal("ras_n", Pins("A19"),  IOStandard("SSTL135")),
        Subsignal("cas_n", Pins("B19"),  IOStandard("SSTL135")),
        Subsignal("we_n",  Pins("A18"),  IOStandard("SSTL135")),
        # cs_n is only wired on V1 of the board but E22 is unconnected on V2
        # so leaving this here shouldn't hurt
        Subsignal("cs_n",  Pins("E22"),  IOStandard("SSTL135")),
        Subsignal("dm", Pins("A22 C22"), IOStandard("SSTL135")),
        Subsignal("dq", Pins(
            "D21 C21 B22 B21 D19 E20 C19 D20",
            "C23 D23 B24 B25 C24 C26 A25 B26"),
            IOStandard("SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("dqs_p", Pins("B20 A23"),
            IOStandard("DIFF_SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("dqs_n", Pins("A20 A24"),
            IOStandard("DIFF_SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("clk_p", Pins("F18"), IOStandard("DIFF_SSTL135")),
        Subsignal("clk_n", Pins("F19"), IOStandard("DIFF_SSTL135")),
        Subsignal("cke",   Pins("E18"), IOStandard("SSTL135")),
        Subsignal("odt",   Pins("G19"), IOStandard("SSTL135")),
        Subsignal("reset_n", Pins("H17"), IOStandard("SSTL135")),
        Misc("SLEW=FAST"),
    ),

    # GMII Ethernet
    ("eth_clocks", 0,
        Subsignal("tx", Pins("M2")),
        Subsignal("gtx", Pins("U1")),
        Subsignal("rx", Pins("P4")),
        IOStandard("LVCMOS33")
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("R1")),
        Subsignal("mdio",    Pins("H1")),
        Subsignal("mdc",     Pins("H2")),
        Subsignal("rx_dv",   Pins("L3")),
        Subsignal("rx_er",   Pins("U5")),
        Subsignal("rx_data", Pins("M4 N3 N4 P3 R3 T3 T4 T5")),
        Subsignal("tx_en",   Pins("T2")),
        Subsignal("tx_er",   Pins("J1")),
        Subsignal("tx_data", Pins("R2 P1 N2 N1 M1 L2 K2 K1")),
        Subsignal("col",     Pins("U4")),
        Subsignal("crs",     Pins("U2")),
        IOStandard("LVCMOS33")
    ),

    # HDMI out
    ("hdmi_out", 0,
        Subsignal("clk_p",   Pins("D4"), IOStandard("TMDS_33")),
        Subsignal("clk_n",   Pins("C4"), IOStandard("TMDS_33")),
        Subsignal("data0_p", Pins("E1"), IOStandard("TMDS_33")),
        Subsignal("data0_n", Pins("D1"), IOStandard("TMDS_33")),
        Subsignal("data1_p", Pins("F2"), IOStandard("TMDS_33")),
        Subsignal("data1_n", Pins("E2"), IOStandard("TMDS_33")),
        Subsignal("data2_p", Pins("G2"), IOStandard("TMDS_33")),
        Subsignal("data2_n", Pins("G1"), IOStandard("TMDS_33")),
        Subsignal("scl",     Pins("B2"), IOStandard("LVCMOS33")),
        Subsignal("sda",     Pins("A2"), IOStandard("LVCMOS33")),
        Subsignal("hdp",     Pins("A3"), IOStandard("LVCMOS33")),
        Subsignal("cec",     Pins("B1"), IOStandard("LVCMOS33")),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("j10", "D5 G5 G7 G8 E5 E6 D6 G6"),
    ("j11", "H4 F4 A4 A5 J4 G4 B4 B5"),
    ("j12", "AB26 AC26 AB24 AC24 AA24 AB25 AA22 AA23",
            " Y25 AA25  W25  Y26  Y22  Y23  W21  Y21",
            " V26  W26  U25  U26  V24  W24  V23  W23",
            " V18  W18  U22  V22  U21  V21  T20  U20",
            " T19 U19"),
    ("jp2", "H21 H22 K21 J21 H26 G26 G25 F25",
            "G20 G21 F23 E23 E26 D26 E25 D25"),
    ("jp3", " AF7  AE7  AD8  AC8  AF9  AE9 AD10 AC10",
            "AA11 AB11 AF11 AE11 AD14 AC14 AF13 AE13",
            "AD12 AC12"),
]

# PMODS --------------------------------------------------------------------------------------------

def sdcard_pmod_io(pmod):
    return [
        # SDCard PMOD:
        # - https://store.digilentinc.com/pmod-microsd-microsd-card-slot/
        ("spisdcard", 0,
            Subsignal("clk",  Pins(f"{pmod}:3")),
            Subsignal("mosi", Pins(f"{pmod}:1"), Misc("PULLUP True")),
            Subsignal("cs_n", Pins(f"{pmod}:0"), Misc("PULLUP True")),
            Subsignal("miso", Pins(f"{pmod}:2"), Misc("PULLUP True")),
            Misc("SLEW=FAST"),
            IOStandard("LVCMOS33"),
        ),
        ("sdcard", 0,
            Subsignal("data", Pins(f"{pmod}:2 {pmod}:4 {pmod}:5 {pmod}:0"), Misc("PULLUP True")),
            Subsignal("cmd",  Pins(f"{pmod}:1"), Misc("PULLUP True")),
            Subsignal("clk",  Pins(f"{pmod}:3")),
            Subsignal("cd",   Pins(f"{pmod}:6")),
            Misc("SLEW=FAST"),
            IOStandard("LVCMOS33"),
        ),
]
_sdcard_pmod_io = sdcard_pmod_io("j10") # SDCARD PMOD on J10.
def ps2_pmod_io(pmod):
    return [
        ("ps2kbd", 0, Pins(f"{pmod}:0 {pmod}:2"), IOStandard("LVCMOS33")), # data, clk
]
_ps2_pmod_io = ps2_pmod_io("j11") # PS2 PMOD on top line of J11

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self, board_version=1, speed_grade=-2, toolchain="vivado"):
        io = _io_common
        if board_version < 2:
            io.extend(_io_v1)
        else:
            io.extend(_io_v2)
        Xilinx7SeriesPlatform.__init__(self, "xc7a100t{}fgg676".format(speed_grade), io, _connectors,  toolchain=toolchain)
        self.toolchain.bitstream_commands = \
            ["set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]"]
        self.toolchain.additional_commands = \
            ["write_cfgmem -force -format bin -interface spix4 -size 16 "
             "-loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"]
        self.add_platform_command("set_property INTERNAL_VREF 0.675 [get_iobanks 16]")
        if board_version < 2:
            self.add_platform_command("set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets clk50_IBUF]")
        self.add_platform_command("set_property CFGBVS VCCO [current_design]")
        self.add_platform_command("set_property CONFIG_VOLTAGE 3.3 [current_design]")

    def create_programmer(self):
        return OpenOCD("openocd_xc7_ft232.cfg", "bscan_spi_xc7a100t.bit")

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
