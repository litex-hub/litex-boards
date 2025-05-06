#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# The Acorn (CLE-101, CLE-215(+)) are cryptocurrency mining accelerator cards from SQRL that can be
# repurposed as generic FPGA PCIe development boards:
# - http://www.squirrelsresearch.com/acorn-cle-101
# - http://www.squirrelsresearch.com/acorn-cle-215-plus
# The 101 variant is eguivalent to the LiteFury and 215 variant equivalent to the NiteFury from
# RHSResearchLLC that are documented at: https://github.com/RHSResearchLLC/NiteFury-and-LiteFury.

import subprocess

from litex.build.generic_platform import *
from litex.build.xilinx           import Xilinx7SeriesPlatform
from litex.build.openocd          import OpenOCD
from litex.build.openfpgaloader   import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst.
    ("clk200", 0,
        Subsignal("p", Pins("J19"), IOStandard("DIFF_SSTL15")),
        Subsignal("n", Pins("H19"), IOStandard("DIFF_SSTL15"))
    ),

    # Leds.
    ("user_led", 0, Pins("G3"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("H3"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("G4"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("H4"), IOStandard("LVCMOS33")),

    # SPIFlash.
    ("flash_cs_n", 0, Pins("T19"), IOStandard("LVCMOS33")),
    ("flash", 0,
        Subsignal("mosi", Pins("P22")),
        Subsignal("miso", Pins("R22")),
        Subsignal("wp",   Pins("P21")),
        Subsignal("hold", Pins("R21")),
        IOStandard("LVCMOS33")
    ),

    # PCIe.
    ("pcie_clkreq_n", 0, Pins("G1"), IOStandard("LVCMOS33")),
    ("pcie_x4", 0,
        Subsignal("rst_n", Pins("J1"), IOStandard("LVCMOS33"), Misc("PULLUP=TRUE")),
        Subsignal("clk_p", Pins("F6")),
        Subsignal("clk_n", Pins("E6")),
        Subsignal("rx_p",  Pins("B10 B8 D11 D9")),
        Subsignal("rx_n",  Pins("A10 A8 C11 C9")),
        Subsignal("tx_p",  Pins("B6  B4  D5 D7")),
        Subsignal("tx_n",  Pins("A6  A4  C5 C7")),
    ),

    # DDR3 SDRAM.
    ("ddram", 0,
        Subsignal("a", Pins(
            "M15 L21 M16 L18 K21 M18 M21 N20",
            "M20 N19 J21 M22 K22 N18 N22 J22"),
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
        #Subsignal("cs_n", Pins(""), IOStandard("SSTL15")),
        Misc("SLEW=FAST"),
    ),
]

_serial_io = [
    # Serial adapter on P2.
    ("serial", 0,
        Subsignal("tx", Pins("K2")),
        Subsignal("rx", Pins("J2")),
        Misc("SLEW=FAST"),
        IOStandard("LVCMOS33"),
    ),
]

_sdcard_io = [
    # SPI SDCard adapter on P2.
    # https://spoolqueue.com/new-design/fpga/migen/litex/2020/08/11/acorn-cle-215.html
    ("spisdcard", 0,
        Subsignal("clk",  Pins("J2")),
        Subsignal("mosi", Pins("J5"), Misc("PULLUP True")),
        Subsignal("cs_n", Pins("H5"), Misc("PULLUP True")),
        Subsignal("miso", Pins("K2"), Misc("PULLUP True")),
        Misc("SLEW=FAST"),
        IOStandard("LVCMOS33"),
    ),
]

_litex_acorn_baseboard_mini_io = [
    # Serial.
    ("serial", 0,
        Subsignal("tx", Pins("G1"),  IOStandard("LVCMOS33")), # CLK_REQ
        Subsignal("rx", Pins("Y13"), IOStandard("LVCMOS18")), # SMB_ALERT_N
    ),

    # PCIe.
    ("pcie_x1", 0,
        Subsignal("rst_n", Pins("J1"), IOStandard("LVCMOS33"), Misc("PULLUP=TRUE")),
        Subsignal("clk_p", Pins("F6")),
        Subsignal("clk_n", Pins("E6")),
        Subsignal("rx_p",  Pins("D9")),
        Subsignal("rx_n",  Pins("C9")),
        Subsignal("tx_p",  Pins("D7")),
        Subsignal("tx_n",  Pins("C7")),
    ),
    # SFP-I2C.
    ("sfp_i2c", 0,
        Subsignal("sda", Pins("Y12")),
        Subsignal("scl", Pins("Y11")),
        IOStandard("LVCMOS18"),
    ),
    # SFP-0.
    ("sfp", 0,
        Subsignal("txp", Pins(" D5")),
        Subsignal("txn", Pins(" C5")),
        Subsignal("rxp", Pins("D11")),
        Subsignal("rxn", Pins("C11")),
    ),
    # SFP-1.
    ("sfp", 1,
        Subsignal("txp", Pins("B4")),
        Subsignal("txn", Pins("A4")),
        Subsignal("rxp", Pins("B8")),
        Subsignal("rxn", Pins("A8")),
    ),
    # SATA.
    ("sata", 0,
        # Inverted on Acorn.
        Subsignal("tx_p",  Pins("B6")),
        Subsignal("tx_n",  Pins("A6")),
        # Inverted on Acorn.
        Subsignal("rx_p",  Pins("B10")),
        Subsignal("rx_n",  Pins("A10")),
    ),
    # Debug.
    ("debug", 0, Pins("H5 J5 J2 K2"), IOStandard("LVCMOS33")),

]
# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk200"
    default_clk_period = 1e9/200e6

    def __init__(self, variant="cle-215+", toolchain="vivado"):
        device = {
            "cle-101":  "xc7a100t-fgg484-2",
            "cle-215":  "xc7a200t-fbg484-2",
            "cle-215+": "xc7a200t-fbg484-3"
        }[variant]

        self.variant = variant

        Xilinx7SeriesPlatform.__init__(self, device, _io, toolchain=toolchain)
        self.add_extension(_serial_io)
        self.add_extension(_sdcard_io)
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
        if ftdi_chip is None:
            raise RuntimeError("No compatible FTDI device found.")
        device = {
            "cle-101":  "xc7a100t",
            "cle-215":  "xc7a200t",
            "cle-215+": "xc7a200t"
        }[self.variant]
        package = {
            "cle-101":  "fgg484",
            "cle-215":  "fbg484",
            "cle-215+": "fbg484"
        }[self.variant]
        if name == "openfpgaloader":
            return OpenFPGALoader(cable=ftdi_chip, fpga_part=f"{device}{package}", freq=10e6)
        elif name == "openocd":
            return OpenOCD(f"openocd_xc7_{ftdi_chip}.cfg", f"bscan_spi_{device}.bit")

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk200", loose=True), 1e9/200e6)
