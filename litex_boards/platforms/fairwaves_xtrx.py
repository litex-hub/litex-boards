#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# https://www.crowdsupply.com/fairwaves/xtrx

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk/Rst.
    ("clk60", 0, Pins("C16"), IOStandard("LVCMOS25")),

    # Leds.
    ("user_led", 0, Pins("N18"),  IOStandard("LVCMOS25")),

    # PCIe.
    ("pcie_x1", 0,
        Subsignal("rst_n", Pins("T3"), IOStandard("LVCMOS25"), Misc("PULLUP=TRUE")),
        Subsignal("clk_p", Pins("B8")),
        Subsignal("clk_n", Pins("A8")),
        Subsignal("rx_p",  Pins("B10")),
        Subsignal("rx_n",  Pins("A10")),
        Subsignal("tx_p",  Pins("B6")),
        Subsignal("tx_n",  Pins("A6")),
    ),

    # SPIFlash.
    ("flash_cs_n", 0, Pins("K19"), IOStandard("LVCMOS25")),
    ("flash", 0,
        Subsignal("mosi", Pins("D18")),
        Subsignal("miso", Pins("D19")),
        Subsignal("wp",   Pins("G18")),
        Subsignal("hold", Pins("F18")),
        IOStandard("LVCMOS25")
    ),

    # I2C
    ("i2c", 0,
        Subsignal("scl", Pins("M1"), Misc("PULLUP=True")),
        Subsignal("sda", Pins("N1"), Misc("PULLUP=True")),
        IOStandard("LVCMOS33"),
    ),

    # GPS.
    ("gps", 0,
        Subsignal("pps", Pins("P3"), Misc("PULLDOWN=True")),
        Subsignal("txd", Pins("N2"), Misc("PULLUP=True")),
        Subsignal("rxd", Pins("L1"), Misc("PULLUP=True")),
        IOStandard("LVCMOS33")
    ),

    # AUX. (Split/Move/Rename?)
    ("aux", 0,
        Subsignal("fpga_clk_vctcxo", Pins("N17"), Misc("PULLDOWN=True")),
        Subsignal("en_tcxo",         Pins("R19"), Misc("PULLUP=True")),
        Subsignal("ext_clk",         Pins("V17"), Misc("PULLDOWN=True")),
        Subsignal("en_gps",          Pins("L18")),
        Subsignal("iovcc_sel",       Pins("V19")),
        Subsignal("en_smsigio",      Pins("D17")),
        IOStandard("LVCMOS25")
    ),

    # RF-Switches / SKY13330, SKY13384.
    ("rfswitches", 0,
        Subsignal("tx", Pins("P1"),    Misc("PULLUP=True")),
        Subsignal("rx", Pins("K3 J3"), Misc("PULLUP=True")),
        IOStandard("LVCMOS33")
    ),

    # RF-IC / LMS7002M.
    ("rfic",
        # SPI / Control.
        Subsignal("saen",    Pins("W13")),
        Subsignal("sdio",    Pins("W16"), Misc("PULLDOWN=True")),
        Subsignal("sdo",     Pins("W15"), Misc("PULLDOWN=True")),
        Subsignal("sclk",    Pins("W14")),
        Subsignal("reset",   Pins("U19")),
        Subsignal("gpwrdwn", Pins("W17")),
        Subsignal("rxen",    Pins("W18")),
        Subsignal("txen",    Pins("W19")),

        # Port1.
        Subsignal("diq1",   Pins("J19 H17 G17 K17 H19 U16 J17 P19 U17 N19 V15 V16")),
        Subsignal("txnrx1", Pins("M19")),
        Subsignal("iqsel1", Pins("P17")),
        Subsignal("mclk1",  Pins("L17")),
        Subsignal("fclk1",  Pins("G19")),

        # Port2.
        Subsignal("diq2",   Pins("W2 U2 V3 V4 V5 W7 V2 W4 U5 V8 U7 U8")),
        Subsignal("txnrx2", Pins("U4")),
        Subsignal("iqsel2", Pins("U3")),
        Subsignal("mclk2",  Pins("W5")),
        Subsignal("fclk2",  Pins("W6")),

        # IOStandard/Slew Rate.
        IOStandard("LVCMOS25"),
        Misc("SLEW=FAST"),
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "clk60"
    default_clk_period = 1e9/60e6

    def __init__(self):
        XilinxPlatform.__init__(self, "xc7a50tcpg236-2", _io, toolchain="vivado")

        self.toolchain.bitstream_commands = [
            "set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]",
            "set_property BITSTREAM.CONFIG.CONFIGRATE 16 [current_design]",
            "set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]"
        ]
        self.toolchain.additional_commands = [
            # Non-Multiboot SPI-Flash bitstream generation.
            "write_cfgmem -force -format bin -interface spix4 -size 16 -loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin",

            # Multiboot SPI-Flash Operational bitstream generation.
            "set_property BITSTREAM.CONFIG.TIMER_CFG 0x0001fbd0 [current_design]",
            "set_property BITSTREAM.CONFIG.CONFIGFALLBACK Enable [current_design]",
            "write_bitstream -force {build_name}_operational.bit ",
            "write_cfgmem -force -format bin -interface spix4 -size 16 -loadbit \"up 0x0 {build_name}_operational.bit\" -file {build_name}_operational.bin",

            # Multiboot SPI-Flash Fallback bitstream generation.
            "set_property BITSTREAM.CONFIG.NEXT_CONFIG_ADDR 0x00400000 [current_design]",
            "write_bitstream -force {build_name}_fallback.bit ",
            "write_cfgmem -force -format bin -interface spix4 -size 16 -loadbit \"up 0x0 {build_name}_fallback.bit\" -file {build_name}_fallback.bin"
        ]

    def create_programmer(self):
        return OpenOCD("openocd_xc7_ft232.cfg", "bscan_spi_xc7a50t.bit")

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk60", loose=True), 1e9/60e6)
