#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Kazumoto Kojima <kkojima@rr.iij4u.or.jp>
# SPDX-License-Identifier: BSD-2-Clause

# The Colorlight i5 PCB and IOs have been documented by @wuxx
# https://github.com/wuxx/Colorlight-FPGA-Projects

from litex.build.generic_platform import *
from litex.build.lattice import LatticePlatform
from litex.build.lattice.programmer import EcpDapProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io_v7_0 = [ # Documented by @smunaut
    # Clk
    ("clk25", 0, Pins("P3"), IOStandard("LVCMOS33")),

    # Led
    ("user_led_n", 0, Pins("U16"), IOStandard("LVCMOS33")),

    # Reset button
    ("cpu_reset_n", 0, Pins("K18"), IOStandard("LVCMOS33"), Misc("PULLMODE=UP")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("J17")),
        Subsignal("rx", Pins("H18")),
        IOStandard("LVCMOS33")
    ),

    # SPIFlash (GD25Q16CSIG)
    ("spiflash", 0,
        Subsignal("cs_n", Pins("R2")),
        # https://github.com/m-labs/nmigen-boards/pull/38
        #Subsignal("clk",  Pins("")), driven through USRMCLK
        Subsignal("mosi", Pins("W2")),
        Subsignal("miso", Pins("V2")),
        IOStandard("LVCMOS33"),
    ),

    # SDRAM SDRAM (EM638325-6H)
    ("sdram_clock", 0, Pins("B9"), IOStandard("LVCMOS33")),
    ("sdram", 0,
        Subsignal("a", Pins(
            "B13 C14 A16 A17 B16 B15 A14 A13",
            "A12 A11 B12")),
        Subsignal("dq", Pins(
            "D15 E14 E13 D12 E12 D11 C10 B17",
            "B8  A8  C7  A7  A6  B6  A5  B5",
            "D5  C5  D6  C6  E7  D7  E8  D8",
            "E9  D9  E11 C11 C12 D13 D14 C15")),
        Subsignal("we_n",  Pins("A10")),
        Subsignal("ras_n", Pins("B10")),
        Subsignal("cas_n", Pins("A9")),
        #Subsignal("cs_n", Pins("")), # gnd
        #Subsignal("cke",  Pins("")), # 3v3
        Subsignal("ba",    Pins("B11 C8")), # sdram pin BA0 and BA1
        #Subsignal("dm",   Pins("")), # gnd
        IOStandard("LVCMOS33"),
        Misc("SLEWRATE=FAST")
    ),

    # RGMII Ethernet (B50612D)
    # The order of the two PHYs is swapped with the naming of the connectors
    # on the board so to match with the configuration of their PHYA[0] pins.
    ("eth_clocks", 0,
        Subsignal("tx", Pins("G1")),
        Subsignal("rx", Pins("H2")),
        IOStandard("LVCMOS33")
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("P4")),
        Subsignal("mdio",    Pins("P5")),
        Subsignal("mdc",     Pins("N5")),
        Subsignal("rx_ctl",  Pins("P2")),
        Subsignal("rx_data", Pins("K2 L1 N1 P1")),
        Subsignal("tx_ctl",  Pins("K1")),
        Subsignal("tx_data", Pins("G2 H1 J1 J3")),
        IOStandard("LVCMOS33")
    ),
    ("eth_clocks", 1,
        Subsignal("tx", Pins("U19")),
        Subsignal("rx", Pins("L19")),
        IOStandard("LVCMOS33")
    ),
    ("eth", 1,
        Subsignal("rst_n",   Pins("P4")),
        Subsignal("mdio",    Pins("P5")),
        Subsignal("mdc",     Pins("N5")),
        Subsignal("rx_ctl",  Pins("M20")),
        Subsignal("rx_data", Pins("P20 N19 N20 M19")),
        Subsignal("tx_ctl",  Pins("P19")),
        Subsignal("tx_data", Pins("U20 T19 T20 R20")),
        IOStandard("LVCMOS33")
    ),
]

# From https://github.com/wuxx/Colorlight-FPGA-Projects/blob/master/schematic/i5_v6.0-extboard.pdf and
# https://github.com/wuxx/Colorlight-FPGA-Projects/blob/master/doc/i5_extboard_v1.2_pinout.png
_connectors_v7_0 = [
    ("pmode", "C17 B18 B20 F20 A18 A19 B19 D20"),
    ("pmodf", "D1  C1  C2  E3  E2  D2  B1  A3"),
]

# PMODS --------------------------------------------------------------------------------------------

def sdcard_pmod_io(pmod):
    return [
        # SDCard PMOD:
        # - https://store.digilentinc.com/pmod-microsd-microsd-card-slot/
        ("spisdcard", 0,
            Subsignal("clk",  Pins(f"{pmod}:3")),
            Subsignal("mosi", Pins(f"{pmod}:1"), Misc("PULLMODE=UP")),
            Subsignal("cs_n", Pins(f"{pmod}:0"), Misc("PULLMODE=UP")),
            Subsignal("miso", Pins(f"{pmod}:2"), Misc("PULLMODE=UP")),
            Misc("SLEWRATE=FAST"),
            IOStandard("LVCMOS33"),
        ),
        ("sdcard", 0,
            Subsignal("data", Pins(f"{pmod}:2 {pmod}:4 {pmod}:5 {pmod}:0"), Misc("PULLMODE=UP")),
            Subsignal("cmd",  Pins(f"{pmod}:1"), Misc("PULLMODE=UP")),
            Subsignal("clk",  Pins(f"{pmod}:3")),
            Subsignal("cd",   Pins(f"{pmod}:6")),
            #Misc("SLEWRATE=FAST"),
            IOStandard("LVCMOS33"),
        ),
]
_sdcard_pmod_io = sdcard_pmod_io("pmode") # SDCARD PMOD on P3.

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticePlatform):
    default_clk_name   = "clk25"
    default_clk_period = 1e9/25e6

    def __init__(self, revision="7.0", toolchain="trellis"):
        assert revision in ["7.0"]
        self.revision = revision
        device     = {"7.0": "LFE5U-25F-6BG381C"}[revision]
        io         = {"7.0": _io_v7_0}[revision]
        connectors = {"7.0": _connectors_v7_0}[revision]
        LatticePlatform.__init__(self, device, io, connectors=connectors, toolchain=toolchain)

    def create_programmer(self):
        return EcpDapProgrammer()

    def do_finalize(self, fragment):
        LatticePlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk25",            loose=True), 1e9/25e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:rx", 0, loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:rx", 1, loose=True), 1e9/125e6)
