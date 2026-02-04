#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 Victor-zyy <gt7591665@gmail.com>
# Copyright (c) 2026 Matt Reverzani <mrev@posteo.de>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform, VivadoProgrammer
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk50",     0, Pins("J19"), IOStandard("LVCMOS33")), #50MHz
    ("cpu_reset", 0, Pins("L18"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led", 0, Pins("M18"),  IOStandard("LVCMOS33")), #green_led 1
    ("user_led", 1, Pins("N18"),  IOStandard("LVCMOS33")), #green_led 2

    # Switches

    # Buttons
    ("user_btn", 0, Pins("AA1"), IOStandard("LVCMOS33")), #KEY1
    ("user_btn", 1, Pins("W1"),  IOStandard("LVCMOS33")), #KEY2

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("V2")), # connect UART-RX
        Subsignal("rx", Pins("U2")), # connect UART-TX
        IOStandard("LVCMOS33")
    ),

    # I2C
    ("i2c", 0,
        Subsignal("sda", Pins("H22")),
        Subsignal("scl", Pins("J22")),
        IOStandard("LVCMOS33")
    ),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("T19")),
        Subsignal("mosi", Pins("P22")),
        Subsignal("miso", Pins("R22")),
        Subsignal("wp",   Pins("P21"), Misc("PULLUP=TRUE")),
        Subsignal("hold", Pins("R21"), Misc("PULLUP=TRUE")),
        IOStandard("LVCMOS33")
    ),
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("T19")),
        Subsignal("dq",   Pins("P22 R22 P21 R21"), Misc("PULLUP=TRUE")),
        IOStandard("LVCMOS33")
    ),

    # DDR3 SDRAM
    ("ddram", 0,
        Subsignal("a", Pins(
            "P1 M6 K3 K4 M5 J6 N2 K6",
            "P2 L1 M2 P6 L4 L5 N5"), #256Mbyte 4Gbits DDR3
            IOStandard("SSTL15")),
        Subsignal("ba",    Pins("J4 R1 M1"), IOStandard("SSTL15")),
        Subsignal("ras_n", Pins("M3"), IOStandard("SSTL15")),
        Subsignal("cas_n", Pins("N3"), IOStandard("SSTL15")),
        Subsignal("we_n",  Pins("L6"), IOStandard("SSTL15")),
        Subsignal("dm", Pins("E2 H3"), IOStandard("SSTL15")),
        Subsignal("dq", Pins(
            "B2 F1 B1 D2 C2 F3 A1 G1",
            "J5 G2 K1 G3 H2 H5 J1 H4"),
            IOStandard("SSTL15"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("dqs_p", Pins("E1 K2"),IOStandard("DIFF_SSTL15")),
        Subsignal("dqs_n", Pins("D1 J2"),IOStandard("DIFF_SSTL15")),
        Subsignal("clk_p", Pins("P5"), IOStandard("DIFF_SSTL15")),
        Subsignal("clk_n", Pins("P4"), IOStandard("DIFF_SSTL15")),
        Subsignal("cke",   Pins("N4"), IOStandard("SSTL15")),
        Subsignal("odt",   Pins("L3"), IOStandard("SSTL15")),
        Subsignal("reset_n", Pins("F4"), IOStandard("SSTL15")),
        Misc("SLEW=FAST"),
    ),

    # SDCard
    ("spisdcard", 0,
        Subsignal("clk",  Pins("U7")),
        Subsignal("cs_n", Pins("Y8")),
        Subsignal("miso", Pins("W9")),
        Subsignal("mosi", Pins("AA8")),
        IOStandard("LVCMOS33"),
    ),
    ("sdcard", 0,
        Subsignal("clk",  Pins("U7")),
        Subsignal("cmd",  Pins("AA8"), Misc("PULLUP=TRUE")),
        Subsignal("data", Pins("W9 Y9 Y7 Y8"), Misc("PULLUP=TRUE")),
        Misc("SLEW=FAST"),
        Misc("DRIVE=8"),
        IOStandard("LVCMOS33"),
    ),

    # RGMII Ethernet (RTL8211F)
    ("eth_clocks", 0,
        Subsignal("tx", Pins("K17"), Misc("SLEW=FAST"), Misc("DRIVE=8")),
        Subsignal("rx", Pins("K18")),
        IOStandard("LVCMOS33")
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("N22")),
        Subsignal("mdio",    Pins("M20"), Misc("PULLUP=TRUE")),
        Subsignal("mdc",     Pins("M22")),
        Subsignal("rx_ctl",  Pins("K19")),
        Subsignal("rx_data", Pins("L14 L16 M15 M16")),
        Subsignal("tx_ctl",  Pins("N20"), Misc("SLEW=FAST"), Misc("DRIVE=8")),
        Subsignal("tx_data", Pins("K16 L15 L13 M13"), Misc("SLEW=FAST"), Misc("DRIVE=8")),
        IOStandard("LVCMOS33")
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("pmoda", "W21 W22 N17 P17 P19 R19 R18 T18 T21 U21 U22 V22 Y21 Y22 AA20 AA21 AB21 AB22 AA19 AB20 U20 V20 Y18"),
    ("pmodb", "Y19 W19 W20 AA18 AB18 V18 V19 V17 W17 U17 U18 P14 R14 P16 R17 N13 N14 P15 R16 AB7 AB6"),
    ("pmodc", "F13 F14 E13 E14 D14 D15 E16 D16 D17 C17 C13 B13 A13 A14 C14 C15 A15 A16 B15 B16 F16 E17 A18"),
    ("pmodd", "A19 B17 B18 B20 A20 F19 F20 E19 D19 C18 C19 F18 E18 D20 C20 B21 A21 D21 G21 C22 B22"),
]

# PMODS --------------------------------------------------------------------------------------------


# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self, variant="200t", programmer="vivado",toolchain="vivado"):
        device = {
            "35t"  : "xc7a35t-fgg484-2",
            "100t" : "xc7a100t-fgg484-2",
            "200t" : "xc7a200t-fbg484-2"
        }[variant]
        self.programmer = programmer
        Xilinx7SeriesPlatform.__init__(self, device, _io, _connectors, toolchain="vivado")
        self.toolchain.bitstream_commands = \
            ["set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]"]
        self.toolchain.additional_commands = \
            ["write_cfgmem -force -format bin -interface spix4 -size 16 "
             "-loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"]
        self.add_platform_command("set_property INTERNAL_VREF 0.750 [get_iobanks 35]")

    def create_programmer(self):
        if self.programmer == "vivado":
            return VivadoProgrammer(flash_part="is25lp128f-spi-x1_x2_x4")
        elif self.programmer == "openocd":
            if "xc7a35t" in self.device:
                proxy = "bscan_spi_xc7a35t.bit"
            elif "xc7a100t" in self.device:
                proxy = "bscan_spi_xc7a100t.bit"
            else:
                proxy = "bscan_spi_xc7a200t.bit"
            return OpenOCD("openocd_xc7_ft2232.cfg", proxy)
        else:
            raise ValueError(f"Unknown programmer: {self.programmer}")

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
