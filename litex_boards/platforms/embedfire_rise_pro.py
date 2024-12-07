#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2024 Yu-Ti Kuo <bobgash2@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause
# embedfire rise pro FPGA: https://detail.tmall.com/item.htm?id=645153441975

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform
from litex.build.openocd import OpenOCD
from litex.build.xilinx.programmer import VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk50"    , 0, Pins("W19"), IOStandard("LVCMOS33")),
    ("cpu_reset", 0, Pins("N15"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led", 0, Pins("M21"),  IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("L21"),  IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("K21"),  IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("K22"),  IOStandard("LVCMOS33")),

    # Buttons
    ("user_sw", 0, Pins("V17"),  IOStandard("LVCMOS33")),
    ("user_sw", 1, Pins("W17"),  IOStandard("LVCMOS33")),
    ("user_sw", 2, Pins("AA18"), IOStandard("LVCMOS33")),
    ("user_sw", 3, Pins("AB18"), IOStandard("LVCMOS33")),

    # Beeper (Buzzer)
    ("beeper", 0, Pins("M17"), IOStandard("LVCMOS33")),

    # Fan
    ("fan", 0, Pins("W22"), IOStandard("LVCMOS33")),

    # Serial CH340G
    ("serial", 0,
        Subsignal("tx", Pins("N17")),
        Subsignal("rx", Pins("P17")),
        IOStandard("LVCMOS33")
    ),

    # I2C EEPROM 24C64
    ("i2c", 0,
        Subsignal("scl", Pins("E22")),
        Subsignal("sda", Pins("D22")),
        IOStandard("LVCMOS33"),
    ),

    # DDR3 SDRAM MT41K256M16
    ("ddram", 0,
        Subsignal("a", Pins(
            "AA4 AB2 AA5 AB3 AB1 U2 W1 R2",
            "V2 U3 Y1 W2 Y2 U1 V3"),
            IOStandard("SSTL135")),
        Subsignal("ba",    Pins("AA1 Y3 AA3"), IOStandard("SSTL135")),
        Subsignal("ras_n", Pins("W6"), IOStandard("SSTL135")),
        Subsignal("cas_n", Pins("U5"), IOStandard("SSTL135")),
        Subsignal("we_n",  Pins("Y4"), IOStandard("SSTL135")),
        Subsignal("cs_n",  Pins("T1"), IOStandard("SSTL135")),
        Subsignal("dm", Pins("D2 G2 M2 M5"), IOStandard("SSTL135")),
        Subsignal("dq", Pins(
            "C2 G1 A1 F3 B2 F1 B1 E2",
            "H3 G3 H2 H5 J1 J5 K1 H4",
            "L4 M3 L3 J6 K3 K6 J4 L5",
            "P1 N4 R1 N2 M6 N5 P6 P2"),
            IOStandard("SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("dqs_p", Pins("E1 K2 M1 P5"),
            IOStandard("DIFF_SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("dqs_n", Pins("D1 J2 L1 P4"),
            IOStandard("DIFF_SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("clk_p", Pins("V4"), IOStandard("DIFF_SSTL135")),
        Subsignal("clk_n", Pins("W4"), IOStandard("DIFF_SSTL135")),
        Subsignal("cke",   Pins("AB5"), IOStandard("SSTL135")),
        Subsignal("odt",   Pins("T5"), IOStandard("SSTL135")),
        Subsignal("reset_n", Pins("R3"), IOStandard("SSTL135")),
        Misc("SLEW=FAST"),
    ),

    # RGMII Ethernet (RTL8211F)
    ("eth_clocks", 0,
        Subsignal("tx", Pins("C18")),
        Subsignal("rx", Pins("C19")),
        IOStandard("LVCMOS33")
    ),
    ("eth", 0,
        #SubSignal("inib"),   Pins("D21")),
        #Subsignal("rst_n",   Pins("E21")),
        Subsignal("mdio",    Pins("G22")),
        Subsignal("mdc",     Pins("G21")),
        Subsignal("rx_ctl",  Pins("C22")),
        Subsignal("rx_data", Pins("D20 C20 A18 A19")),
        Subsignal("tx_ctl",  Pins("B22")),
        Subsignal("tx_data", Pins("B20 A20 B21 A21")),
        IOStandard("LVCMOS33")
    ),

    # SDCard
    ("spisdcard", 0,
        Subsignal("cd",   Pins("AA19")),
        Subsignal("clk",  Pins("Y22")),
        Subsignal("mosi", Pins("Y21")),
        Subsignal("cs_n", Pins("A14")),
        Subsignal("miso", Pins("AB21")),
        Misc("SLEW=FAST"),
        IOStandard("LVCMOS33"),
    ),

    ("sdcard", 0,
        Subsignal("data", Pins("AB21 AB22 AB20 W21"),),
        Subsignal("cmd",  Pins("Y21"),),
        Subsignal("clk",  Pins("Y22")),
        Subsignal("cd",   Pins("AA19")),
        Misc("SLEW=FAST"),
        IOStandard("LVCMOS33"),
    ),
]
# Connectors ---------------------------------------------------------------------------------------

_connectors = [] # ToDo

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self, variant="a7-35", toolchain="vivado"):
        device = {
            "a7-35":  "xc7a35tfgg484-2",
            "a7-100": "xc7a100tfgg484-2",
            "a7-200": "xc7a200tfbg484-2"
        }[variant]
        Xilinx7SeriesPlatform.__init__(self, device, _io, _connectors, toolchain=toolchain)
        self.toolchain.bitstream_commands = \
            ["set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]"]
        self.toolchain.additional_commands = \
            ["write_cfgmem -force -format bin -interface spix4 -size 16 "
            "-loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"]
        self.add_platform_command("set_property INTERNAL_VREF 0.675 [get_iobanks 34]")

    def create_programmer(self):
        return VivadoProgrammer(flash_part="mt25ql128-spi-x1_x2_x4")

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
