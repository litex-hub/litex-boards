#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# https://www.crowdsupply.com/fairwaves/xtrx

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform
from litex.build.openfpgaloader import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk/Rst.
    ("clk60", 0, Pins("C16"), IOStandard("LVCMOS25")),

    # Leds.
    ("user_led", 0, Pins("N18"),  IOStandard("LVCMOS25")),
    ("user_led2", 0, Pins("G3 M2 G2"),  IOStandard("LVCMOS33")), # GPIO LED

    # PCIe.
    ("pcie_x1", 0,
        Subsignal("rst_n", Pins("T3"), IOStandard("LVCMOS25"), Misc("PULLUP=TRUE")),
        Subsignal("clk_p", Pins("B8")),
        Subsignal("clk_n", Pins("A8")),
        Subsignal("rx_p",  Pins("B6")),
        Subsignal("rx_n",  Pins("A6")),
        Subsignal("tx_p",  Pins("B2")),
        Subsignal("tx_n",  Pins("A2")),
    ),

    ("pcie_x2", 0,
        Subsignal("rst_n", Pins("T3"), IOStandard("LVCMOS25"), Misc("PULLUP=TRUE")),
        Subsignal("clk_p", Pins("B8")),
        Subsignal("clk_n", Pins("A8")),
        Subsignal("rx_p",  Pins("B6 B4")),
        Subsignal("rx_n",  Pins("A6 A4")),
        Subsignal("tx_p",  Pins("B2 D2")),
        Subsignal("tx_n",  Pins("A2 D1")),
    ),

    # USB
    ("usb", 0,
        Subsignal("usb_d",    Pins("B17 A17 B16 A16 B15 A15 A14 C15")),
        Subsignal("usb_stp",  Pins("C17"), Misc("PULLUP=TRUE")),
        Subsignal("usb_clk",  Pins("C16")),
        Subsignal("usb_dir",  Pins("B18")),
        Subsignal("usb_nxt",  Pins("A18")),
        Subsignal("usb_nrst", Pins("M18"), Misc("PULLDOWN=True")),
        Subsignal("usb_26m",  Pins("E19")),
        IOStandard("LVCMOS25")
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

    # Power-Down.
    ("pwrdwn_n", 0, Pins("R19"), IOStandard("LVCMOS25")),

    # I2C buses.
    ("i2c", 0,
        Subsignal("scl", Pins("U14"), Misc("PULLUP=True")),
        Subsignal("sda", Pins("U15"), Misc("PULLUP=True")),
        IOStandard("LVCMOS25"),
    ),
    ("i2c", 1,
        Subsignal("scl", Pins("M1"), Misc("PULLUP=True")),
        Subsignal("sda", Pins("N1"), Misc("PULLUP=True")),
        IOStandard("LVCMOS33"),
    ),

    # XSYNC SPI bus.
    ("xsync_spi", 1,
        Subsignal("cs_n", Pins("H1")), # GPIO9
        Subsignal("clk",  Pins("J1")), # GPIO10
        Subsignal("mosi", Pins("N3")), # GPIO8
        IOStandard("LVCMOS33"),
    ),

    # Synchro.
    ("synchro", 0,
        Subsignal("pps_in", Pins("M3")), # GPIO0
        Subsignal("pps_out",Pins("L3")), # GPIO1
        IOStandard("LVCMOS33"),
    ),

    # GPS.
    ("gps", 0,
        Subsignal("rst_n", Pins("L18"), IOStandard("LVCMOS25")),
        Subsignal("pps",   Pins("P3"),  Misc("PULLDOWN=True")),
        Subsignal("rx" ,   Pins("N2"),  Misc("PULLUP=True")),
        Subsignal("tx" ,   Pins("L1"),  Misc("PULLUP=True")),
        IOStandard("LVCMOS33")
    ),

    # VCTCXO.
    ("vctcxo", 0,
        Subsignal("en",  Pins("R19"), Misc("PULLUP=True")),
        Subsignal("sel", Pins("V17"), Misc("PULLDOWN=True")), # ext_clk
        Subsignal("clk", Pins("N17"), Misc("PULLDOWN=True")),
        IOStandard("LVCMOS25")
    ),

    # GPIO
    ("gpio", 0, Pins("H2 J2 N3 H1 J1 K2 L2"), IOStandard("LVCMOS33")),

    # AUX.
    ("aux", 0,
        Subsignal("iovcc_sel",  Pins("V19")),
        Subsignal("en_smsigio", Pins("D17")),
        Subsignal("option",     Pins("V14")),
        Subsignal("gpio13",     Pins("T17")),
        IOStandard("LVCMOS25")
    ),

    # RF-Switches / SKY13330, SKY13384.
    ("rf_switches", 0,
        Subsignal("tx", Pins("P1"),    Misc("PULLUP=True")),
        Subsignal("rx", Pins("K3 J3"), Misc("PULLUP=True")),
        IOStandard("LVCMOS33")
    ),

    # RF-IC / LMS7002M.
    ("lms7002m", 0,
        # Control.
        Subsignal("rst_n",    Pins("U19")),
        Subsignal("pwrdwn_n", Pins("W17")),
        Subsignal("rxen",     Pins("W18")),
        Subsignal("txen",     Pins("W19")),

        # SPI.
        Subsignal("clk",  Pins("W14")),
        Subsignal("cs_n", Pins("W13")),
        Subsignal("mosi", Pins("W16"), Misc("PULLDOWN=True")),
        Subsignal("miso", Pins("W15"), Misc("PULLDOWN=True")),

        # RX-Interface (LMS -> FPGA).
        Subsignal("diq1",   Pins("J19 H17 G17 K17 H19 U16 J17 P19 U17 N19 V15 V16")),
        Subsignal("txnrx1", Pins("M19")),
        Subsignal("iqsel1", Pins("P17")),
        Subsignal("mclk1",  Pins("L17")),
        Subsignal("fclk1",  Pins("G19")),

        # RX-Interface (FPGA -> LMS).
        Subsignal("diq2",   Pins("W2 U2 V3 V4 V5 W7 V2 W4 U5 V8 U7 U8")),
        Subsignal("txnrx2", Pins("U4")),
        Subsignal("iqsel2", Pins("U3")),
        Subsignal("mclk2",  Pins("W5")),
        Subsignal("fclk2",  Pins("W6")),

        # IOStandard/Slew Rate.
        IOStandard("LVCMOS25"),
        Misc("SLEW=FAST"),
    ),

    # SIM.
    ("sim", 0,
        Subsignal("mode",    Pins("R3")),
        Subsignal("enable",  Pins("U1")),
        Subsignal("clk",     Pins("T1")),
        Subsignal("reset",   Pins("R2")),
        Subsignal("data",    Pins("T2")),
        IOStandard("LVCMOS25")
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk60"
    default_clk_period = 1e9/60e6

    def __init__(self, variant="xc7a50t", toolchain="vivado"):
        assert variant in ["xc7a35t", "xc7a50t"]
        self.variant = variant
        device = {
            "xc7a35t" : "xc7a35tcpg236-3",
            "xc7a50t" : "xc7a50tcpg236-2",
        }[variant]
        Xilinx7SeriesPlatform.__init__(self, "xc7a50tcpg236-2", _io, toolchain=toolchain)

        self.toolchain.bitstream_commands = [
            "set_property BITSTREAM.CONFIG.UNUSEDPIN Pulldown [current_design]",
            "set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]",
            "set_property BITSTREAM.CONFIG.EXTMASTERCCLK_EN Disable [current_design]",
            "set_property BITSTREAM.CONFIG.CONFIGRATE 66 [current_design]",
            "set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]",
            "set_property BITSTREAM.CONFIG.SPI_FALL_EDGE YES [current_design]",
            "set_property CFGBVS VCCO [current_design]",
            "set_property CONFIG_VOLTAGE 3.3 [current_design]",
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
        return OpenFPGALoader(cable="digilent_hs2", fpga_part=f"{self.variant}cpg236", freq=10e6)

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk60", loose=True), 1e9/60e6)
