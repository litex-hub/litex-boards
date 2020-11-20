#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 <linux.robotdude@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause


from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk200", 0,
        Subsignal("p", Pins("J19"), IOStandard("LVDS_25")),
        Subsignal("n", Pins("H19"), IOStandard("LVDS_25"))
    ),

    # Leds
    ("user_led", 0, Pins("G3"), IOStandard("LVCMOS33"), Misc("PULLUP"), Misc("DRIVE=8")),
    ("user_led", 1, Pins("H3"), IOStandard("LVCMOS33"), Misc("PULLUP"), Misc("DRIVE=8")),
    ("user_led", 2, Pins("G4"),  IOStandard("LVCMOS33"), Misc("PULLUP"), Misc("DRIVE=8")),
    ("user_led", 3, Pins("H4"),  IOStandard("LVCMOS33"), Misc("PULLUP"), Misc("DRIVE=8")),

    # M.2 Led signal
    ("m2_led", 0, Pins("M1"), IOStandard("LVCMOS33"), Misc("DRIVE=8")),

    # SMBus (M.2 spec has pullups on host)
    ("smbus", 0,
        Subsignal("clk", Pins("Y11"), IOStandard("LVCMOS33")),
        Subsignal("data", Pins("Y12"), IOStandard("LVCMOS33")),
        Subsignal("alert_n", Pins("Y13"), IOStandard("LVCMOS33"))
    ),

    # SPIFlash
    ("flash", 0,
        Subsignal("cs_n",  Pins("T19")),
        Subsignal("mosi",  Pins("P22")),
        Subsignal("miso",  Pins("R22")),
        Subsignal("hold",  Pins("R21")),
        IOStandard("LVCMOS33")
    ),
    ("flash4x", 0,  # clock needs to be accessed through STARTUPE2 (pad L12) (90 MHz EMC clock is available)
        Subsignal("cs_n", Pins("T19")),
        Subsignal("dq",   Pins("P22", "R22", "P21", "R21")),
        IOStandard("LVCMOS33")
    ),

    # PCIe clock request
    ("pcie_clkreq_l", 0, Pins("G1"), IOStandard("LVCMOS33")),

    # PCIe
    ("pcie_x1", 0,
        Subsignal("rst_n", Pins("J1"), IOStandard("LVCMOS33")),
        Subsignal("clk_p", Pins("F6")),
        Subsignal("clk_n", Pins("E6")),
        Subsignal("rx_p",  Pins("B10")),
        Subsignal("rx_n",  Pins("A10")),
        Subsignal("tx_p",  Pins("B6")),
        Subsignal("tx_n",  Pins("A6"))
    ),

    ("pcie_x4", 0,
        Subsignal("rst_n", Pins("J1"), IOStandard("LVCMOS33")),
        Subsignal("clk_p", Pins("F6")),
        Subsignal("clk_n", Pins("E6")),
        Subsignal("rx_p",  Pins("B10 B8 D11 D9")),
        Subsignal("rx_n",  Pins("A10 A8 C11 C9")),
        Subsignal("tx_p",  Pins("B6 B4 D5 D7")),
        Subsignal("tx_n",  Pins("A6 A4 C5 C7"))
    ),

    # DDR3 SDRAM
    ("ddram", 0,
        Subsignal("a", Pins(
            "M15 L21 M16 L18 K21 M18 M21 N20",
            "M20 N19 J21 M22 K22 N18 N22"),
            IOStandard("SSTL15")),
        Subsignal("ba",    Pins("L19 J20 L20"), IOStandard("SSTL15")),
        Subsignal("ras_n", Pins("H20"),  IOStandard("SSTL15")),
        Subsignal("cas_n", Pins("K18"),  IOStandard("SSTL15")),
        Subsignal("we_n",  Pins("L16"),  IOStandard("SSTL15")),
        Subsignal("dm", Pins("A19 G22"), IOStandard("SSTL15")),
        Subsignal("dq", Pins(
            "D19 B20 E19 A20 F19 C19 F20 C18",
            "E22 G21 D20 E21 C22 D21 B22 D22"),
            IOStandard("SSTL15"),
            Misc("IN_TERM=UNTUNED_SPLIT_50")),
        Subsignal("dqs_p", Pins("F18 B21"),  IOStandard("DIFF_SSTL15")),
        Subsignal("dqs_n", Pins("E18 A21"), IOStandard("DIFF_SSTL15")),
        Subsignal("clk_p", Pins("K17"), IOStandard("DIFF_SSTL15")),
        Subsignal("clk_n", Pins("J17"), IOStandard("DIFF_SSTL15")),
        Subsignal("cke",   Pins("H22"), IOStandard("SSTL15")),
        Subsignal("odt",   Pins("K19"), IOStandard("SSTL15")),
        Subsignal("reset_n", Pins("K16"), IOStandard("LVCMOS15")),
        Misc("SLEW=FAST"),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    # Digital IO Header
    ("IO", {
        # LVDS pins
        "dio1_p" : "W9",
        "dio1_n" : "Y9",
        "dio2_p" : "Y8",
        "dio2_n" : "Y7",
        "dio3_p" : "AA8",
        "dio3_n" : "AB8",
        "dio4_p" : "V9",
        "dio4_n" : "V8",
        # 3.3V DIO pins (or XADC)
        "aio1_p" : "J5",
        "aio1_n" : "H5",
        "aio2_p" : "K2",
        "aio2_n" : "J2",
        }
    ),

    # Analog Header
    ("XADC", {
        "aio1_p" : "J5",
        "aio1_n" : "H5",
        "aio2_p" : "K2",
        "aio2_n" : "J2",
        }
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "clk200"
    default_clk_period = 1e9/200e6

    def __init__(self):
        XilinxPlatform.__init__(self, "xc7a100t-fgg484-2l", _io, _connectors, toolchain="vivado")
        # Enable fast startup so FPGA is up before PCIe root-complex initialization on host
        self.add_platform_command("set_property BITSTREAM.CONFIG.CONFIGFALLBACK ENABLE [current_design]")
        self.add_platform_command("set_property BITSTREAM.CONFIG.EXTMASTERCCLK_EN Div-1 [current_design]")
        self.add_platform_command("set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]")
        self.add_platform_command("set_property BITSTREAM.CONFIG.SPI_FALL_EDGE YES [current_design]")
        self.add_platform_command("set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]")
        self.add_platform_command("set_property CFGBVS VCCO [current_design]")
        self.add_platform_command("set_property CONFIG_MODE SPIx4 [current_design]")
        self.add_platform_command("set_property CONFIG_VOLTAGE 3.3 [current_design]")

        self.toolchain.additional_commands = \
            ["write_cfgmem -force -format mcs -interface spix4 -size 16 "
             "-loadbit \"up 0x680000 {build_name}.bit\" -file {build_name}.mcs"]

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk200", loose=True), 1e9/200e6)