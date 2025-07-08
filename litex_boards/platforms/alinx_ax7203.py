#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 Aaron Hagan <amhagan@kent.edu>
# SPDX-License-Identifier: BSD-2-Clause
#
# The AX7203 FPGA development board equipped with the AMD Artix 7 series device.
# https://en.alinx.com/Product/FPGA-Development-Boards/Artix-7/AX7203.html

import subprocess

from litex.build.generic_platform import *
from litex.build.xilinx           import Xilinx7SeriesPlatform
from litex.build.openfpgaloader   import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------
_io = [
    # Clk / Rst
    ("clk200", 0,
        Subsignal("p", Pins("R4"), IOStandard("DIFF_SSTL15")),
        Subsignal("n", Pins("T4"), IOStandard("DIFF_SSTL15")),
    ),
    ("cpu_reset_n", 0, Pins("T6"), IOStandard("LVCMOS15")),
    ("hdmi_reset_n", 0, Pins("J19"), IOStandard("LVCMOS33")),

    ("clk148p5", 0,
        Subsignal("p", Pins("F6"), IOStandard("LVCMOS33")),
        Subsignal("n", Pins("E6"), IOStandard("LVCMOS33"))
    ),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("N15"), IOStandard("LVCMOS33")),
        Subsignal("rx", Pins("P20"), IOStandard("LVCMOS33")),
    ),

    # PCIe x4
    ("pcie_x4", 0,
        Subsignal("rst_n", Pins("J20"), IOStandard("LVCMOS33")),
        Subsignal("clk_p", Pins("F10")),
        Subsignal("clk_n", Pins("E10")),
        Subsignal("rx_p",  Pins("D11 B8 B10 D9")),
        Subsignal("rx_n",  Pins("C11 A8 A10 C9")),
        Subsignal("tx_p",  Pins("D5   B4  B6 D7")),
        Subsignal("tx_n",  Pins("C5   A4  A6 C7"))
    ),

    # Leds
    ("user_led", 0, Pins("B13"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("C13"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("D14"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("D15"), IOStandard("LVCMOS33")),

    # HDMI Out
    ("hdmi", 0,
        Subsignal("r",    Pins("V14 H14 J14 K13 K14 L13 L19 L20")),
        Subsignal("g",    Pins("K17 J17 L16 K16 L14 L15 M15 M16")), 
        Subsignal("b",    Pins("L18 M18 N18 N19 M20 N20 L21 M21")),
        Subsignal("de",        Pins("V13")),
        Subsignal("clk",       Pins("M13")),
        Subsignal("vsync",   Pins("T14")),
        Subsignal("hsync",   Pins("T15")),
        Subsignal("scl", Pins("E16")),
        Subsignal("sda", Pins("F16")),
        IOStandard("LVCMOS33")
    ),

    # DDR3 SDRAM
    ("ddram", 0,
        Subsignal("a",     Pins("AA4 AB2 AA5 AB5 AB1 U3 W1 T1 V2 U2 Y1 W2 Y2 U1 V3"), IOStandard("SSTL15")),
        Subsignal("ba",    Pins("AA3 Y3 Y4"), IOStandard("SSTL15")),
        Subsignal("ras_n", Pins("V4"), IOStandard("SSTL15")),
        Subsignal("cas_n", Pins("W4"), IOStandard("SSTL15")),
        Subsignal("we_n",  Pins("AA1"), IOStandard("SSTL15")),
        Subsignal("dm",    Pins("D2 G2 M2 M5"), IOStandard("SSTL15")),
        Subsignal("dq",    Pins("C2 G1 A1 F3 B2 F1 B1 E2", 
                                "H3 G3 H2 H5 J1 J5 K1 H4",
                                "L4 M3 L3 J6 K3 K6 J4 L5",
                                "P1 N4 R1 N2 M6 N5 P6 P2"),
            IOStandard("SSTL15"),
            Misc("IN_TERM=UNTUNED_SPLIT_50")),
        Subsignal("dqs_p", Pins("E1 K2 M1 P5"), IOStandard("DIFF_SSTL15"), Misc("IN_TERM=UNTUNED_SPLIT_50")),
        Subsignal("dqs_n", Pins("D1 J2 L1 P4"), IOStandard("DIFF_SSTL15"), Misc("IN_TERM=UNTUNED_SPLIT_50")),
        Subsignal("clk_p", Pins("R3"), IOStandard("DIFF_SSTL15")),
        Subsignal("clk_n", Pins("R2"), IOStandard("DIFF_SSTL15")),
        Subsignal("cke",   Pins("T5"), IOStandard("SSTL15")),
        Subsignal("odt",   Pins("U5"), IOStandard("SSTL15")),
        Subsignal("reset_n", Pins("W6"), IOStandard("LVCMOS15")),
        Subsignal("cs_n",  Pins("AB3"), IOStandard("SSTL15")), # Fix me
        Misc("SLEW=FAST"),
    ),

    # SPIFlash
    ("flash_cs_n", 0, Pins("T19"), IOStandard("LVCMOS33")),
    ("flash", 0,
        Subsignal("mosi", Pins("P22")),
        Subsignal("miso", Pins("R22")),
        Subsignal("wp",   Pins("P21")),
        Subsignal("hold", Pins("R21")),
        IOStandard("LVCMOS33"),
    )
]

# Platform -----------------------------------------------------------------------------------------
class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk200"
    default_clk_period = 1e9/200e6

    def __init__(self):
        Xilinx7SeriesPlatform.__init__(self, "xc7a200t-fbg484-2", _io, toolchain="vivado")
        self.toolchain.additional_commands = ["write_cfgmem -force -format bin -interface spix4 -size 16 -loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"]
        self.add_platform_command("set_property INTERNAL_VREF 0.750 [get_iobanks 34]")

        self.toolchain.bitstream_commands = [
            "set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]",
            "set_property BITSTREAM.CONFIG.CONFIGRATE 16 [current_design]",
            "set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]",
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

    def detect_ftdi_chip(self):
        lsusb_log = subprocess.run(['lsusb'], capture_output=True, text=True)
        for ftdi_chip in ["ft232", "ft2232", "ft4232"]:
            if f"Future Technology Devices International, Ltd {ftdi_chip.upper()}" in lsusb_log.stdout:
                return ftdi_chip
        return None

    def create_programmer(self, name="openfpgaloader"):
        ftdi_chip = self.detect_ftdi_chip()
        return OpenFPGALoader(cable=ftdi_chip, fpga_part=f"xc7a200tfbg484", freq=10e6)

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk200", loose=True), 1e9/200e6)
