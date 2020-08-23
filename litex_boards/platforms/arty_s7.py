#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2018 William D. Jones <thor0505@comcast.net>
# Copyright (c) 2020 Staf Verhaegen <staf@fibraservi.eu>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import Pins, Subsignal, IOStandard, Misc
from litex.build.xilinx import XilinxPlatform
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    ("user_led", 0, Pins("E18"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("F13"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("E13"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("H15"), IOStandard("LVCMOS33")),

    ("rgb_led", 0,
        Subsignal("r", Pins("J15")),
        Subsignal("g", Pins("G17")),
        Subsignal("b", Pins("F15")),
        IOStandard("LVCMOS33")
    ),

    ("rgb_led", 1,
        Subsignal("r", Pins("E15")),
        Subsignal("g", Pins("F18")),
        Subsignal("b", Pins("E14")),
        IOStandard("LVCMOS33")
    ),

    ("user_sw", 0, Pins("H14"), IOStandard("LVCMOS33")),
    ("user_sw", 1, Pins("H18"), IOStandard("LVCMOS33")),
    ("user_sw", 2, Pins("G18"), IOStandard("LVCMOS33")),
    ("user_sw", 3, Pins("M5"),  IOStandard("SSTL135")),

    ("user_btn", 0, Pins("G15"), IOStandard("LVCMOS33")),
    ("user_btn", 1, Pins("K16"), IOStandard("LVCMOS33")),
    ("user_btn", 2, Pins("J16"), IOStandard("LVCMOS33")),
    ("user_btn", 3, Pins("H13"), IOStandard("LVCMOS33")),

    ("clk100", 0, Pins("R2"), IOStandard("SSTL135")),

    ("cpu_reset", 0, Pins("C18"), IOStandard("LVCMOS33")),

    ("serial", 0,
        Subsignal("tx", Pins("R12")),
        Subsignal("rx", Pins("V12")),
        IOStandard("LVCMOS33")),

    ("spi", 0,
        Subsignal("clk",  Pins("G16")),
        Subsignal("cs_n", Pins("H16")),
        Subsignal("mosi", Pins("H17")),
        Subsignal("miso", Pins("K14")),
        IOStandard("LVCMOS33")
    ),

    ("i2c", 0,
        Subsignal("scl", Pins("J14")),
        Subsignal("sda", Pins("J13")),
        IOStandard("LVCMOS33"),
    ),

    ("spiflash4x", 0,  # clock needs to be accessed through STARTUPE2
        Subsignal("cs_n", Pins("M13")),
        Subsignal("clk",  Pins("D11")),
        Subsignal("dq",   Pins("K17", "K18", "L14", "M15")),
        IOStandard("LVCMOS33")
    ),
    ("spiflash", 0,  # clock needs to be accessed through STARTUPE2
        Subsignal("cs_n", Pins("M13")),
        Subsignal("clk",  Pins("D11")),
        Subsignal("mosi", Pins("K17")),
        Subsignal("miso", Pins("K18")),
        Subsignal("wp",   Pins("L14")),
        Subsignal("hold", Pins("M15")),
        IOStandard("LVCMOS33")
    ),

    ("ddram", 0,
        Subsignal("a", Pins(
            "U2 R4 V2 V4 T3 R7 V6 T6",
            "U7 V7 P6 T5 R6 U6"),
            IOStandard("SSTL135")),
        Subsignal("ba", Pins("V5 T1 U3"), IOStandard("SSTL135")),
        Subsignal("ras_n", Pins("U1"), IOStandard("SSTL135")),
        Subsignal("cas_n", Pins("V3"), IOStandard("SSTL135")),
        Subsignal("we_n",  Pins("P7"), IOStandard("SSTL135")),
        Subsignal("cs_n",  Pins("R3"), IOStandard("SSTL135")),
        Subsignal("dm", Pins("K4 M3"), IOStandard("SSTL135")),
        Subsignal("dq", Pins(
            "K2 K3 L4 M6 K6 M4 L5 L6",
            "N4 R1 N1 N5 M2 P1 M1 P2"),
            IOStandard("SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("dqs_p", Pins("K1 N3"),
            IOStandard("DIFF_SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("dqs_n", Pins("L1 N2"),
            IOStandard("DIFF_SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("clk_p", Pins("R5"), IOStandard("DIFF_SSTL135")),
        Subsignal("clk_n", Pins("T4"), IOStandard("DIFF_SSTL135")),
        Subsignal("cke",   Pins("T2"), IOStandard("SSTL135")),
        Subsignal("odt",   Pins("P5"), IOStandard("SSTL135")),
        Subsignal("reset_n", Pins("J6"), IOStandard("SSTL135")),
        Misc("SLEW=FAST"),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("pmoda", "L17 L18 M14 N14 M16 M17 M18 N18"),
    ("pmodb", "P17 P18 R18 T18 P14 P15 N15 P16"),
    ("pmodc", "U15 V16 U17 U18 U16 P13 R13 V14"),
    ("pmodd", "V15 U12 V13 T12 T13 R11 T11 U11"),
    ("ck_io", {
        # Outer Digital Header
        "ck_io0"  : "L13",
        "ck_io1"  : "N13",
        "ck_io2"  : "L16",
        "ck_io3"  : "R14",
        "ck_io4"  : "T14",
        "ck_io5"  : "R16",
        "ck_io6"  : "R17",
        "ck_io7"  : "V17",
        "ck_io8"  : "R15",
        "ck_io9"  : "T15",
        "ck_io10" : "H16",
        "ck_io11" : "H17",
        "ck_io12" : "K14",
        "ck_io13" : "G16",

        # Inner Digital Header
        "ck_io26" : "U11",
        "ck_io27" : "T11",
        "ck_io28" : "R11",
        "ck_io29" : "T13",
        "ck_io30" : "T12",
        "ck_io31" : "V13",
        "ck_io32" : "U12",
        "ck_io33" : "V15",
        "ck_io34" : "V14",
        "ck_io35" : "R13",
        "ck_io36" : "P13",
        "ck_io37" : "U16",
        "ck_io38" : "U18",
        "ck_io39" : "U17",
        "ck_io40" : "V16",
        "ck_io41" : "U15",

        # Outer Analog Header as Digital IO
        "ck_a0" : "G13",
        "ck_a1" : "B16",
        "ck_a2" : "A16",
        "ck_a3" : "C13",
        "ck_a4" : "C14",
        "ck_a5" : "D18",

        # Inner Analog Header as Digital IO
        "ck_a6"  : "B14",
        "ck_a7"  : "A14",
        "ck_a8"  : "D16",
        "ck_a9"  : "D17",
        "ck_a10" : "D14",
        "ck_a11" : "D15",
        }
    ),
    ("XADC", {
        # Outer Analog Header
        "vaux0_p"  : "B13",
        "vaux0_n"  : "A13",
        "vaux1_p"  : "B15",
        "vaux1_n"  : "A15",
        "vaux9_p"  : "E12",
        "vaux9_n"  : "D12",
        "vaux2_p"  : "B17",
        "vaux2_n"  : "A17",
        "vaux10_p" : "C17",
        "vaux10_n" : "B18",
        "vaux11_p" : "E16",
        "vaux11_n" : "E17",

        # Inner Analog Header
        "vaux8_p" : "B14",
        "vaux8_n" : "A14",
        "vaux3_p" : "D16",
        "vaux3_n" : "D17",
        }
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self, variant="s7-50"):
        device = {
            "s7-25": "xc7s25csga324-1",
            "s7-50": "xc7s50csga324-1"
        }[variant]
        XilinxPlatform.__init__(self, device, _io, _connectors, toolchain="vivado")
        self.toolchain.bitstream_commands = \
            ["set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]"]
        self.toolchain.additional_commands = \
            ["write_cfgmem -force -format bin -interface spix4 -size 16 "
             "-loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"]
        self.add_platform_command("set_property INTERNAL_VREF 0.675 [get_iobanks 34]")

    def create_programmer(self):
        bscan_spi = "bscan_spi_xc7s50.bit" if "xc7s50" in self.device else "bscan_spi_xc7a25.bit"
        return OpenOCD("openocd_xc7_ft2232.cfg", bscan_spi)

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100", loose=True), 1e9/100e6)
