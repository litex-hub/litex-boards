#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2018-2019 Rohit Singh <rohit@rohitksingh.in>
# Copyright (c) 2018 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk100", 0, Pins("W19"), IOStandard("LVCMOS33")),
    ("rst",    0, Pins("P17"), IOStandard("LVCMOS33")),

    # Leds (only a single rgb led, aliased here also)
    ("user_led", 0, Pins("W21"),  IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("W22"),  IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("AA20"), IOStandard("LVCMOS33")),
    ("rgb_led", 0,
        Subsignal("r", Pins("W21")),
        Subsignal("g", Pins("W22")),
        Subsignal("b", Pins("AA20")),
        IOStandard("LVCMOS33"),
    ),

    # Serial
    ("serial", 0,
        Subsignal("tx",    Pins("R14")),
        Subsignal("rx",    Pins("P14")),
        Subsignal("rts",   Pins("R18")),
        Subsignal("cts",   Pins("T18")),
        Subsignal("cbus0", Pins("N17")),
        IOStandard("LVCMOS33")
    ),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("T19")),
        Subsignal("mosi", Pins("P22")),
        Subsignal("miso", Pins("R22")),
        Subsignal("vvp",  Pins("P21")),
        Subsignal("hold", Pins("R21")),
        IOStandard("LVCMOS33")
    ),
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("T19")),
        #Subsignal("clk",  Pins("")), # Accessed through STARTUPE2.
        Subsignal("dq",   Pins("P22", "R22", "P21", "R21")),
        IOStandard("LVCMOS33")
    ),

    # TPM
    ("tpm", 0,
        Subsignal("clk",   Pins("Y18")),
        Subsignal("rst_n", Pins("AA19")),
        Subsignal("cs_n",  Pins("Y19")),
        Subsignal("mosi",  Pins("V18")),
        Subsignal("miso",  Pins("V19")),
        IOStandard("LVCMOS33"),
    ),

    # PCIe
    ("pcie_x1", 0,
        Subsignal("rst_n", Pins("W20"), IOStandard("LVCMOS33"), Misc("PULLUP=TRUE")),
        Subsignal("clk_p", Pins("F6")),
        Subsignal("clk_n", Pins("E6")),
        Subsignal("rx_p",  Pins("B8")),
        Subsignal("rx_n",  Pins("A8")),
        Subsignal("tx_p",  Pins("B4")),
        Subsignal("tx_n",  Pins("A4"))
    ),

    # DDR3 SDRAM
    ("ddram", 0,
        Subsignal("a", Pins(
            "U6 T5 Y6 T6  V2 T4 Y2 R2",
            "Y1 R4 W5 W1 AA6 U2"),
            IOStandard("SSTL15")),
        Subsignal("ba",    Pins("W6 U5 R6"), IOStandard("SSTL15")),
        Subsignal("ras_n", Pins("V5"), IOStandard("SSTL15")),
        Subsignal("cas_n", Pins("T1"), IOStandard("SSTL15")),
        Subsignal("we_n",  Pins("R3"), IOStandard("SSTL15")),
        Subsignal("dm", Pins("Y7 K1"), IOStandard("SSTL15")),
        Subsignal("dq", Pins(
            "Y8 AB6 W9 AA8 AB7 V7 AB8 W7",
            "H4 G2 J5 H2 H5 G4 J1 G3"),
            IOStandard("SSTL15"),
            Misc("IN_TERM=UNTUNED_SPLIT_50")),
        Subsignal("dqs_p", Pins("V9 K2"), IOStandard("DIFF_SSTL15")),
        Subsignal("dqs_n", Pins("V8 J2"), IOStandard("DIFF_SSTL15")),
        Subsignal("clk_p", Pins("U3"), IOStandard("DIFF_SSTL15")),
        Subsignal("clk_n", Pins("V3"), IOStandard("DIFF_SSTL15")),
        Subsignal("cke",   Pins("U1"), IOStandard("SSTL15")),
        Subsignal("odt",   Pins("W2"), IOStandard("SSTL15")),
        Subsignal("reset_n", Pins("U7"), IOStandard("LVCMOS15")),
        Subsignal("cs_n", Pins("T3"), IOStandard("SSTL15")),
        Misc("SLEW=FAST"),
    ),

     # SDCard
     ("sdcard", 0,
        Subsignal("data", Pins("P19 Y22 Y21 T21")),
        Subsignal("cmd",  Pins("U21")),
        Subsignal("clk",  Pins("R19")),
        Misc("SLEW=FAST"),
        IOStandard("LVCMOS33"),
    ),

    # SFP0
    ("sfp_tx", 0,
        Subsignal("p", Pins("B6")),
        Subsignal("n", Pins("A6"))
    ),
    ("sfp_rx", 0,
        Subsignal("p", Pins("B10")),
        Subsignal("n", Pins("A10"))
    ),
    ("sfp_tx_disable_n", 0, Pins("V22"),  IOStandard("LVCMOS33")),
    ("sfp_rx_los",       0, Pins("AB21"), IOStandard("LVCMOS33")),

    # SFP1
    ("sfp_tx", 1,
        Subsignal("p", Pins("D7")),
        Subsignal("n", Pins("C7")),
    ),
    ("sfp_rx", 1,
        Subsignal("p", Pins("D9")),
        Subsignal("n", Pins("C9")),
    ),
    ("sfp_tx_disable_n", 1, Pins("P15"), IOStandard("LVCMOS33")),
    ("sfp_rx_los",       1, Pins("R17"), IOStandard("LVCMOS33")),
]

_connectors = [
    ("LPC", {
        # FMC GTP Section
        "DP0_M2C_P"     : "D11",
        "DP0_M2C_N"     : "C11",

        "GBTCLK0_M2C_P" : "F10",
        "GBTCLK0_M2C_N" : "E10",

        "DP0_C2M_P"     : "D5",
        "DP0_C2M_N"     : "C5",

        # FMC Clock and Misc signals
        "PG_C2M"        : "V20",
        "PRSNT_M2C_L"   : "W17",
        "CLK0_M2C_P"    : "C18",
        "CLK0_M2C_N"    : "C19",
        "CLK1_M2C_P"    : "K18",
        "CLK1_M2C_N"    : "K19",
        "FMC_TCK"       : "V12",
        "FMC_TDI"       : "U13", # FPGA_TDO_FMC_TDI
        "FMC_TDO"       : "R13",
        "FMC_TMS"       : "T13",
        "FMC_SCL"       : "N13",
        "FMC_SDA"       : "N14",

        # FMC LA Bank GPIOs
        "LA00_CC_P"     : "D17",
        "LA00_CC_N"     : "C17",
        "LA01_CC_P"     : "J19",
        "LA01_CC_N"     : "H19",
        "LA02_P"        : "E19",
        "LA02_N"        : "D19",
        "LA03_P"        : "F13",
        "LA03_N"        : "F14",
        "LA04_P"        : "F18",
        "LA04_N"        : "E18",
        "LA05_P"        : "L19",
        "LA05_N"        : "L20",
        "LA06_P"        : "J22",
        "LA06_N"        : "H22",
        "LA07_P"        : "B20",
        "LA07_N"        : "A20",
        "LA08_P"        : "F16",
        "LA08_N"        : "E17",
        "LA09_P"        : "N22",
        "LA09_N"        : "M22",
        "LA10_P"        : "H20",
        "LA10_N"        : "G20",
        "LA11_P"        : "A18",
        "LA11_N"        : "A19",
        "LA12_P"        : "C14",
        "LA12_N"        : "C15",
        "LA13_P"        : "M18",
        "LA13_N"        : "L18",
        "LA14_P"        : "K21",
        "LA14_N"        : "K22",
        "LA15_P"        : "F19",
        "LA15_N"        : "F20",
        "LA16_P"        : "E13",
        "LA16_N"        : "E14",
        "LA17_CC_P"     : "B17",
        "LA17_CC_N"     : "B18",
        "LA18_CC_P"     : "J20",
        "LA18_CC_N"     : "J21",
        "LA19_P"        : "D20",
        "LA19_N"        : "C20",
        "LA20_P"        : "E16",
        "LA20_N"        : "D16",
        "LA21_P"        : "C22",
        "LA21_N"        : "B22",
        "LA22_P"        : "D14",
        "LA22_N"        : "D15",
        "LA23_P"        : "N18",
        "LA23_N"        : "N19",
        "LA24_P"        : "B21",
        "LA24_N"        : "A21",
        "LA25_P"        : "B15",
        "LA25_N"        : "B16",
        "LA26_P"        : "N20",
        "LA26_N"        : "M20",
        "LA27_P"        : "M21",
        "LA27_N"        : "L21",
        "LA28_P"        : "E22",
        "LA28_N"        : "D22",
        "LA29_P"        : "C13",
        "LA29_N"        : "B13",
        "LA30_P"        : "E21",
        "LA30_N"        : "D21",
        "LA31_P"        : "A15",
        "LA31_N"        : "A16",
        "LA32_P"        : "G21",
        "LA32_N"        : "G22",
        "LA33_P"        : "A13",
        "LA33_N"        : "A14",
        }
    )
]

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self, toolchain="vivado"):
        Xilinx7SeriesPlatform.__init__(self, "xc7a200t-fbg484-2", _io, _connectors, toolchain=toolchain)
        self.add_platform_command("set_property INTERNAL_VREF 0.750 [get_iobanks 34]")
        self.add_platform_command("set_property INTERNAL_VREF 0.750 [get_iobanks 35]")
        self.toolchain.bitstream_commands = [
            "set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]",
            "set_property BITSTREAM.CONFIG.CONFIGRATE 16 [current_design]",
            "set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]"
        ]
        self.toolchain.additional_commands = \
            ["write_cfgmem -force -format bin -interface spix4 -size 16 "
             "-loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"]

    def create_programmer(self):
        return OpenOCD("openocd_xc7_ft232.cfg", "bscan_spi_xc7a200t.bit")

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100", loose=True), 1e9/100e6)
