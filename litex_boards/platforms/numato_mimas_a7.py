#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2018-2019 Rohit Singh <rohit@rohitksingh.in>
# Copyright (c) 2020 Feliks Montez <feliks.montez@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk100", 0, Pins("H4"), IOStandard("LVCMOS33")),
    ("cpu_reset", 0, Pins("M2"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led", 0, Pins("K17"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("J17"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("L14"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("L15"), IOStandard("LVCMOS33")),
    ("user_led", 4, Pins("L16"), IOStandard("LVCMOS33")),
    ("user_led", 5, Pins("K16"), IOStandard("LVCMOS33")),
    ("user_led", 6, Pins("M15"), IOStandard("LVCMOS33")),
    ("user_led", 7, Pins("M16"), IOStandard("LVCMOS33")),

    # Switches
    ("user_sw", 0, Pins("B21"), IOStandard("LVCMOS33")),
    ("user_sw", 1, Pins("A21"), IOStandard("LVCMOS33")),
    ("user_sw", 2, Pins("E22"), IOStandard("LVCMOS33")),
    ("user_sw", 3, Pins("D22"), IOStandard("LVCMOS33")),
    ("user_sw", 4, Pins("E21"), IOStandard("LVCMOS33")),
    ("user_sw", 5, Pins("D21"), IOStandard("LVCMOS33")),
    ("user_sw", 6, Pins("G21"), IOStandard("LVCMOS33")),
    ("user_sw", 7, Pins("G22"), IOStandard("LVCMOS33")),

    # Buttons
    ("user_btn", 0, Pins("P20"), IOStandard("LVCMOS33")),
    ("user_btn", 1, Pins("P19"), IOStandard("LVCMOS33")),
    ("user_btn", 2, Pins("P17"), IOStandard("LVCMOS33")),
    ("user_btn", 3, Pins("N17"), IOStandard("LVCMOS33")),

    # Serial
    ("serial", 0, # Can be used when FT2232H's Channel A configured to ASYNC Serial (UART) mode
        Subsignal("tx", Pins("Y21")),
        Subsignal("rx", Pins("Y22")),
        IOStandard("LVCMOS33")
    ),

    # USB FIFO
    ("usb_fifo", 0, # Can be used when FT2232H's Channel A configured to ASYNC FIFO 245 mode
        Subsignal("data",  Pins("Y22 Y21 AB22 AA21 AB21 AA20 AB20 AA18")),
        Subsignal("rxf_n", Pins("W21")),
        Subsignal("txe_n", Pins("V22")),
        Subsignal("rd_n",  Pins("AA19")),
        Subsignal("wr_n",  Pins("W22")),
        Subsignal("siwua", Pins("U21")),
        Subsignal("oe_n",  Pins("T21")),
        Misc("SLEW=FAST"),
        Drive(8),
        IOStandard("LVCMOS33"),
    ),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("T19")),
        Subsignal("clk",  Pins("L12")),
        Subsignal("mosi", Pins("P22")),
        Subsignal("miso", Pins("R22")),
        Subsignal("wp",   Pins("P21")),
        Subsignal("hold", Pins("R21")),
        IOStandard("LVCMOS33"),
    ),
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("T19")),
        Subsignal("clk",  Pins("L12")),
        Subsignal("dq",   Pins("P22", "R22", "P21", "R21")),
        IOStandard("LVCMOS33")
    ),

    # DDR3 SDRAM
    ("ddram", 0,
        Subsignal("a", Pins(
            "U6 T5 Y6 T6 V2 T4 Y2 R2",
            "Y1 R4 W5 W1 AA6 U2"),
            IOStandard("SSTL15")),
        Subsignal("ba",    Pins("W6 U5 R6"), IOStandard("SSTL15")),
        Subsignal("ras_n", Pins("V5"),  IOStandard("SSTL15")),
        Subsignal("cas_n", Pins("T1"),  IOStandard("SSTL15")),
        Subsignal("we_n",  Pins("R3"),  IOStandard("SSTL15")),
        Subsignal("dm", Pins("Y7 AA1"), IOStandard("SSTL15")),
        Subsignal("dq", Pins(
            "Y8 AB6 W9  AA8 AB7 V7 AB8 W7",
            "V4 AB2 AA5 AB3 AB5 W4 AB1 AA4"),
            IOStandard("SSTL15"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("dqs_p", Pins("V9 Y3"),  IOStandard("DIFF_SSTL15")),
        Subsignal("dqs_n", Pins("V8 AA3"), IOStandard("DIFF_SSTL15")),
        Subsignal("clk_p", Pins("U3"), IOStandard("DIFF_SSTL15")),
        Subsignal("clk_n", Pins("V3"), IOStandard("DIFF_SSTL15")),
        Subsignal("cke",   Pins("U1"), IOStandard("SSTL15")),
        Subsignal("odt",   Pins("W2"), IOStandard("SSTL15")),
        Subsignal("cs_n",  Pins("T3"), IOStandard("SSTL15")),
        Subsignal("reset_n", Pins("U7"), IOStandard("SSTL15")),
        Misc("SLEW=FAST"),
    ),

    # I2C EEPROM
    ("eeprom", 0,
        Subsignal("scl", Pins("N5")),
        Subsignal("sda", Pins("P6")),
        IOStandard("LVCMOS33")
    ),

    # RGMII Ethernet
    ("eth_clocks", 0,
        Subsignal("tx", Pins("U20")),
        Subsignal("rx", Pins("W19")),
        IOStandard("LVCMOS33")
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("R14"), IOStandard("LVCMOS33")),
        Subsignal("int_n",   Pins("V19")),
        Subsignal("mdio",    Pins("P16")),
        Subsignal("mdc",     Pins("R19")),
        Subsignal("rx_ctl",  Pins("Y19")),
        Subsignal("rx_data", Pins("AB18 W20 W17 V20")),
        Subsignal("tx_ctl",  Pins("T20")),
        Subsignal("tx_data", Pins("V18 U18 V17 U17")),
        IOStandard("LVCMOS33")
    ),

    # HDMI In
    ("hdmi_in", 0,
        Subsignal("clk_p",   Pins("K4"), IOStandard("TMDS_33")),
        Subsignal("clk_n",   Pins("J4"), IOStandard("TMDS_33")),
        Subsignal("data0_p", Pins("K1"), IOStandard("TMDS_33")),
        Subsignal("data0_n", Pins("J1"), IOStandard("TMDS_33")),
        Subsignal("data1_p", Pins("M1"), IOStandard("TMDS_33")),
        Subsignal("data1_n", Pins("L1"), IOStandard("TMDS_33")),
        Subsignal("data2_p", Pins("P2"), IOStandard("TMDS_33")),
        Subsignal("data2_n", Pins("N2"), IOStandard("TMDS_33")),
        Subsignal("scl",     Pins("J2"), IOStandard("LVCMOS33")),
        Subsignal("sda",     Pins("H2"), IOStandard("LVCMOS33")),
        Subsignal("hpd_en",  Pins("G2"), IOStandard("LVCMOS33")),
        Subsignal("cec",     Pins("K2"), IOStandard("LVCMOS33")), # FIXME
        # Subsignal("txen", Pins("R3"), IOStandard("LVCMOS33")),  # FIXME
    ),

    # HDMI Out
    ("hdmi_out", 0,
        Subsignal("clk_p",   Pins("L3"), IOStandard("TMDS_33")),
        Subsignal("clk_n",   Pins("K3"), IOStandard("TMDS_33")),
        Subsignal("data0_p", Pins("B1"), IOStandard("TMDS_33")),
        Subsignal("data0_n", Pins("A1"), IOStandard("TMDS_33")),
        Subsignal("data1_p", Pins("E1"), IOStandard("TMDS_33")),
        Subsignal("data1_n", Pins("D1"), IOStandard("TMDS_33")),
        Subsignal("data2_p", Pins("G1"), IOStandard("TMDS_33")),
        Subsignal("data2_n", Pins("F1"), IOStandard("TMDS_33")),
        Subsignal("scl",     Pins("D2"), IOStandard("LVCMOS33")),
        Subsignal("sda",     Pins("C2"), IOStandard("LVCMOS33")),
        Subsignal("cec",     Pins("E2"), IOStandard("LVCMOS33")), # FIXME
        Subsignal("hdp",     Pins("B2"), IOStandard("LVCMOS33")), # FIXME
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("P12", "J20 J21 K21 K22 H20 G20 J19 H19",
            "J22 H22 K18 K19 L19 L20 M21 N22",
            "N20 M20 M18 L18 N18 N19 H17 H18",
            "G17 G18 G15 G16 J15 H15 K13 K14",
            "M13 K14 M13 L13 J14 H14 H13 G13"),
    ("P13", "F19 F20 E19 D19 D20 C20 C22 B22",
            "F18 E18 C18 C19 D17 C17 B20 A20",
            "B17 B18 A18 A19 E16 D16 B15 B16",
            "A15 A16 C14 C15 A13 A14 C13 B13",
            "D14 D15 E13 E14 F13 F14 F16 E17")
]

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self, toolchain="vivado"):
        Xilinx7SeriesPlatform.__init__(self, "xc7a50tfgg484-1", _io, _connectors, toolchain=toolchain)
        self.toolchain.bitstream_commands = \
            ["set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]"]
        self.toolchain.additional_commands = \
            ["write_cfgmem -force -format bin -interface spix4 -size 16 "
             "-loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"]
        self.add_platform_command("set_property INTERNAL_VREF 0.675 [get_iobanks 34]")

    def create_programmer(self):
        return OpenOCD("openocd_xc7_ft2232.cfg", "bscan_spi_xc7a50t.bit")

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100",        loose=True), 1e9/100e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:rx", loose=True), 1e9/125e6)
