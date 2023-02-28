#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# The Colorlight 5A-75B PCB and IOs have been documented by @miek and @smunaut:
# https://github.com/q3k/chubby75/tree/master/5a-75b

from litex.build.generic_platform import *
from litex.build.lattice import LatticeECP5Platform
from litex.build.lattice.programmer import OpenOCDJTAGProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io_v7_0 = [ # Documented by @miek
    # Clk
    ("clk25", 0, Pins("P6"), IOStandard("LVCMOS33")),

    # Led
    ("user_led_n", 0, Pins("P11"), IOStandard("LVCMOS33")),

    # Button
    ("user_btn_n", 0, Pins("M13"), IOStandard("LVCMOS33")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("P11")), # led (J19 DATA_LED-)
        Subsignal("rx", Pins("M13")), # btn (J19 KEY+)
        IOStandard("LVCMOS33")
    ),

    # SPIFlash (W25Q32JV)
    ("spiflash", 0,
        # clk
        Subsignal("cs_n", Pins("N8")),
        #Subsignal("clk",  Pins("")), driven through USRMCLK
        Subsignal("mosi", Pins("T8")),
        Subsignal("miso", Pins("T7")),
        IOStandard("LVCMOS33"),
    ),

    # SDR SDRAM (M126L6161A)
    ("sdram_clock", 0, Pins("C6"), IOStandard("LVCMOS33")),
    ("sdram", 0,
        Subsignal("a", Pins(
            "A9 E10 B12 D13 C12 D11 D10 E9",
            "D9 B7 C8")),
        Subsignal("dq", Pins(
            "B13 C11 C10 A11 C9 E8  B6  B9",
            "A6  B5  A5  B4  B3 C3  A2  B2",
            "E2  D3  A4  E4  D4 C4  E5  D5",
            "E6  D6  D8  A8  B8 B10 B11 E11")),
        Subsignal("we_n",  Pins("C7")),
        Subsignal("ras_n", Pins("D7")),
        Subsignal("cas_n", Pins("E7")),
        #Subsignal("cs_n", Pins("")), # gnd
        #Subsignal("cke",  Pins("")), # 3v3
        Subsignal("ba",    Pins("A7")),
        #Subsignal("dm",   Pins("")), # gnd
        IOStandard("LVCMOS33"),
        Misc("SLEWRATE=FAST")
    ),

    # RGMII Ethernet (B50612D)
    ("eth_clocks", 0,
        Subsignal("tx", Pins("M2")),
        Subsignal("rx", Pins("M1")),
        IOStandard("LVCMOS33")
    ),
    ("eth", 0,
        #Subsignal("rst_n",   Pins("P5")),
        Subsignal("mdio",    Pins("T2")),
        Subsignal("mdc",     Pins("P3")),
        Subsignal("rx_ctl",  Pins("N6")),
        Subsignal("rx_data", Pins("N1 M5 N5 M6")),
        Subsignal("tx_ctl",  Pins("M3")),
        Subsignal("tx_data", Pins("L1 L3 P2 L4")),
        IOStandard("LVCMOS33")
    ),
    ("eth_clocks", 1,
        Subsignal("tx", Pins("M12")),
        Subsignal("rx", Pins("M16")),
        IOStandard("LVCMOS33")
    ),
    ("eth", 1,
        #Subsignal("rst_n",   Pins("P5")),
        Subsignal("mdio",    Pins("T2")),
        Subsignal("mdc",     Pins("P3")),
        Subsignal("rx_ctl",  Pins("L15")),
        Subsignal("rx_data", Pins("P13 N13 P14 M15")),
        Subsignal("tx_ctl",  Pins("R15")),
        Subsignal("tx_data", Pins("T14 R12 R13 R14")),
        IOStandard("LVCMOS33")
    ),

    # USB
    ("usb", 0,
        Subsignal("d_p", Pins("M8")),
        Subsignal("d_n", Pins("R2")),
        Subsignal("pullup", Pins("P4")),
        IOStandard("LVCMOS33")
    ),
]

# From https://github.com/q3k/chubby75/blob/master/5a-75b/hardware_V7.0.md
_connectors_v7_0 = [
    ("j1", "- "),
    ("j2", "- "),
    ("j3", "- "),
    ("j4", "- "),
]


# Platform -----------------------------------------------------------------------------------------

class Platform(LatticeECP5Platform):
    default_clk_name   = "clk25"
    default_clk_period = 1e9/25e6

    def __init__(self, revision="7.0", toolchain="trellis"):
        assert revision in ["6.1", "7.0", "8.0"]
        self.revision = revision
        device     = {"7.0": "LFE5U-25F-6BG256C"}[revision]
        io         = {"7.0": _io_v7_0           }[revision]
        connectors = {"7.0": _connectors_v7_0   }[revision]
        LatticeECP5Platform.__init__(self, device, io, connectors=connectors, toolchain=toolchain)

    def create_programmer(self):
        return OpenOCDJTAGProgrammer("openocd_colorlight_5a_75b.cfg")

    def do_finalize(self, fragment):
        LatticeECP5Platform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk25",            loose=True), 1e9/25e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:rx", 0, loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:rx", 1, loose=True), 1e9/125e6)
