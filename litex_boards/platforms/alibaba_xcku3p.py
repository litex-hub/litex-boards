#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 Derek Kozel <dkozel@bitstovolts.com
# SPDX-License-Identifier: BSD-2-Clause

# The AS02MC04 is an accelerator card from Alibaba Cloud that can be repurposed as a generic FPGA
# PCIe development board. It has PCIe Gen 3 x8 and two SFP+ interfaces.

# More information about the board:
# - https://essenceia.github.io/projects/alibaba_cloud_fpga/
# - https://github.com/TiferKing/as02mc04_hack/
# - https://gist.github.com/Chester-Gillon/765d6286b1c34c7dc26a7b4c4dd0c48c

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxUSPPlatform
from litex.build.openfpgaloader import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk.
    ("clk100", 0,
        Subsignal("p", Pins("E18"), IOStandard("LVDS")),
        Subsignal("n", Pins("D18"), IOStandard("LVDS"))
    ),

    # Optional SFP reference clock (present in pinout; not default)
    ("sfp_mgt_clk", 0,
        Subsignal("p", Pins("K7"), IOStandard("LVDS")),
        Subsignal("n", Pins("K6"), IOStandard("LVDS"))
    ),

    # LEDs.
    ("user_led", 0, Pins("B11"), IOStandard("LVCMOS18")),  # GPIO_LED_1
    ("user_led", 1, Pins("C11"), IOStandard("LVCMOS18")),  # GPIO_LED_2
    ("user_led", 2, Pins("A10"), IOStandard("LVCMOS18")),  # GPIO_LED_3
    ("user_led", 3, Pins("B10"), IOStandard("LVCMOS18")),  # GPIO_LED_4

    # LEDs.
    ("user_led_rgh", 0,
        Subsignal("r", Pins("A13"), IOStandard("LVCMOS18")),  # GPIO_LED_R
        Subsignal("g", Pins("A12"), IOStandard("LVCMOS18")),  # GPIO_LED_G
        Subsignal("h", Pins("B9"),  IOStandard("LVCMOS18")),  # GPIO_LED_H
    ),

    # I2C EEPROMs.
    ("i2c_eeprom", 0,
        Subsignal("scl", Pins("G9"),  IOStandard("LVCMOS18"), Misc("DRIVE=8")),
        Subsignal("sda", Pins("G10"), IOStandard("LVCMOS18"), Misc("DRIVE=8")),
    ),
    ("i2c_eeprom", 0,
        Subsignal("scl", Pins("J14"), IOStandard("LVCMOS18"), Misc("DRIVE=8")),
        Subsignal("sda", Pins("J15"), IOStandard("LVCMOS18"), Misc("DRIVE=8")),
    ),

    # SFP-0.
    ("sfp_mod_def0", 0, Pins("D14"), IOStandard("LVCMOS18")),
    ("sfp_tx_fault", 0, Pins("B14"), IOStandard("LVCMOS18")),
    ("sfp_los",      0, Pins("D13"), IOStandard("LVCMOS18")),
    ("sfp_led",      0, Pins("B12"), IOStandard("LVCMOS18")),
    ("sfp_i2c", 0,
        Subsignal("scl", Pins("C13"), IOStandard("LVCMOS18"), Misc("DRIVE=8")),
        Subsignal("sda", Pins("C14"), IOStandard("LVCMOS18"), Misc("DRIVE=8")),
    ),
    ("sfp", 0,
        Subsignal("txp", Pins("B7")),
        Subsignal("txn", Pins("B6")),
        Subsignal("rxp", Pins("A4")),
        Subsignal("rxn", Pins("A3")),
    ),
    ("sfp_tx", 0,
        Subsignal("p", Pins("B7")),
        Subsignal("n", Pins("B6"))
    ),
    ("sfp_rx", 0,
        Subsignal("p", Pins("A4")),
        Subsignal("n", Pins("A3"))
    ),

    # SFP-1.
    ("sfp_mod_def0", 0, Pins("E11"), IOStandard("LVCMOS18")),
    ("sfp_tx_fault", 0, Pins("F9"),  IOStandard("LVCMOS18")),
    ("sfp_los",      0, Pins("E10"), IOStandard("LVCMOS18")),
    ("sfp_led",      0, Pins("C12"), IOStandard("LVCMOS18")),
    ("sfp_i2c", 1,
        Subsignal("scl", Pins("D10"), IOStandard("LVCMOS18"), Misc("DRIVE=8")),
        Subsignal("sda", Pins("D11"), IOStandard("LVCMOS18"), Misc("DRIVE=8")),
    ),
    ("sfp", 1,
        Subsignal("txp", Pins("D7")),
        Subsignal("txn", Pins("D6")),
        Subsignal("rxp", Pins("B2")),
        Subsignal("rxn", Pins("B1")),
    ),
    ("sfp_tx", 1,
        Subsignal("p", Pins("D7")),
        Subsignal("n", Pins("D6"))
    ),
    ("sfp_rx", 1,
        Subsignal("p", Pins("B2")),
        Subsignal("n", Pins("B1"))
    ),

    # PCIe.
    ("pcie_x1", 0,
        Subsignal("rst_n", Pins("A9"), IOStandard("LVCMOS18")),
        Subsignal("clk_p", Pins("T7")),
        Subsignal("clk_n", Pins("T6")),
        Subsignal("rx_p",  Pins("P2")),
        Subsignal("rx_n",  Pins("P1")),
        Subsignal("tx_p",  Pins("R5")),
        Subsignal("tx_n",  Pins("R4"))
    ),
    ("pcie_x2", 0,
        Subsignal("rst_n", Pins("A9"), IOStandard("LVCMOS18")),
        Subsignal("clk_p", Pins("T7")),
        Subsignal("clk_n", Pins("T6")),
        Subsignal("rx_p",  Pins("P2 T2")),
        Subsignal("rx_n",  Pins("P1 T1")),
        Subsignal("tx_p",  Pins("R5 U5")),
        Subsignal("tx_n",  Pins("R4 U4"))
    ),
    ("pcie_x4", 0,
        Subsignal("rst_n", Pins("A9"), IOStandard("LVCMOS18")),
        Subsignal("clk_p", Pins("T7")),
        Subsignal("clk_n", Pins("T6")),
        Subsignal("rx_p",  Pins("P2 T2 V2  Y2")),
        Subsignal("rx_n",  Pins("P1 T1 V1  Y1")),
        Subsignal("tx_p",  Pins("R5 U5 W5 AA5")),
        Subsignal("tx_n",  Pins("R4 U4 W4 AA4"))
    ),
    ("pcie_x8", 0,
        Subsignal("rst_n", Pins("A9"), IOStandard("LVCMOS18")),
        Subsignal("clk_p", Pins("T7")),
        Subsignal("clk_n", Pins("T6")),
        Subsignal("rx_p",  Pins("P2 T2 V2  Y2 AB2 AD2 AE4 AF2")),
        Subsignal("rx_n",  Pins("P1 T1 V1  Y1 AB1 AD1 AE3 AF1")),
        Subsignal("tx_p",  Pins("R5 U5 W5 AA5 AC5 AD7 AE9 AF7")),
        Subsignal("tx_n",  Pins("R4 U4 W4 AA4 AC4 AD6 AE8 AF6"))
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxUSPPlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self, toolchain="vivado"):
        XilinxUSPPlatform.__init__(self, "xcku3p-ffvb676-2-e", _io, toolchain=toolchain)

    def create_programmer(self):
        return OpenFPGALoader(cable="digilent_hs2", fpga_part="xcku3p-ffvb676")

    def do_finalize(self, fragment):
        XilinxUSPPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100", loose=True), 1e9/100e6)

        # Shutdown on overheating
        self.add_platform_command("set_property BITSTREAM.CONFIG.OVERTEMPSHUTDOWN ENABLE [current_design]")

        # Reduce programming time
        self.add_platform_command("set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]")
