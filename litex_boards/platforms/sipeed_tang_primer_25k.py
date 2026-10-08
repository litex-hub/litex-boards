#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2023 Gwenhael Goavec-Merou <gwenhael.goavec-merou@trabucayre.com>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.build.generic_platform import *
from litex.build.gowin.platform import GowinPlatform
from litex.build.gowin.programmer import GowinProgrammer
from litex.build.openfpgaloader import OpenFPGALoader

from litex_boards.extensions.sdram_modules import MiSTerSDRAM, SipeedSDRAM
from litex_boards.extensions.sipeed        import TangPrimer25KDock


# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst.
    ("clk50",  0, Pins("E2"), IOStandard("LVCMOS33")),

    # SPIFlash.
    ("spiflash", 0,
        Subsignal("cs_n", Pins("E6"), IOStandard("LVCMOS33")),
        Subsignal("clk",  Pins("E7"), IOStandard("LVCMOS33")),
        Subsignal("mosi", Pins("D6"), IOStandard("LVCMOS33")),
        Subsignal("miso", Pins("E5"), IOStandard("LVCMOS33")),
        Subsignal("wp",   Pins("D5"), IOStandard("LVCMOS33")),
        Subsignal("hold", Pins("E4"), IOStandard("LVCMOS33")),
    ),
    ("spiflashx4", 0,
        Subsignal("cs_n", Pins("E6"),          IOStandard("LVCMOS33")),
        Subsignal("clk",  Pins("E7"),          IOStandard("LVCMOS33")),
        Subsignal("dq",   Pins("D6 E5 D5 E4"), IOStandard("LVCMOS33")),
    ),
]

# Dock 204 Pins SODIMM Connector -------------------------------------------------------------------

_connectors = [
    ["J1",
        # -------------------------------------------------
        "---", # 0
        # GND GND                                   ( 1-10).
        " --- --- L9  H5  K9  J5  J8  L5  K8  K5",
        #                 GND                       (11-20).
        "  F7  H8  F6  H7 ---  G7  E8  G8  B3  F5",
        #             3V3     3V3 GND GND 3V3       (21-30).
        "  C3  G5  E3 ---  D7 --- --- --- ---  L6",
        # 3V3                                       (31-40).
        " ---  K6 J11  K7 J10  J7 H11  L7 H10  L8",
        #                 GND                 GND   (41-50).
        " G11 L10 G10 K10 --- K11 D11 L11 D10 ---",
        #                                 GND GND   (51-60).
        " C11 E11 C10 E10 B11 A11 B10 A10 --- ---",
    ],
    ["J2",
        # ----------------------------------------------------------------------
        "---", # 0
        # GND     3V3         3V3                                       ( 1-10).
        " ---     ---      B2 ---      C2  L2      F2  L1      F1  K1",
        #                                                     GND       (11-20).
        "  A1      K2      D8  J4      E1  K4      D1  G2     ---  G1",
        # TCK             TMS         TDO         TDI         GND       (21-30).
        "  C1      L4      B1  L3      A2  J1      A3  J2     ---  G4",
        #                             GND             1V8         1V8   (31-40).
        " M0_D3_P  H4 M0_D3_N  H1     ---  H2 M0_D2_P --- M0_D2_N ---",
        # GND     2V5         2V5         3V3     GND 3V3         3V3   (41-50).
        " ---     --- M0_CK_P --- M0_CK_N ---     --- --- M0_D1_P ---",
        #          5V     GND GND          5V          5V     GND  5V   (51-60).
        " M0_D1_N ---     --- --- M0_D0_P --- M0_D0_N ---     --- ---",
    ],
]

# SDRAMs -------------------------------------------------------------------------------------------

def misterSDRAM(conn="j3"):
    return MiSTerSDRAM(conn).get_io(GowinPlatform)

def sipeedSDRAM(conn="j3"):
    return SipeedSDRAM(conn).get_io(GowinPlatform)

# Docks --------------------------------------------------------------------------------------------

docks = {
    "standard" : TangPrimer25KDock(),
}

# Platform -----------------------------------------------------------------------------------------

class Platform(GowinPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self, dock="standard", toolchain="gowin"):

        GowinPlatform.__init__(self, "GW5A-LV25MG121NC1/I0", _io, _connectors, toolchain=toolchain, devicename="GW5A-25A")
        if dock is not None:
            if dock not in docks:
                raise ValueError(f"Unsupported dock {dock}, supported: {', '.join(docks)} or None (SoM only).")
            self.add_extension(docks[dock])

        self.toolchain.options["use_mspi_as_gpio"]  = 1 # spi flash
        self.toolchain.options["use_i2c_as_gpio"]   = 1 # SDRAM / J3
        self.toolchain.options["use_ready_as_gpio"] = 1 # led
        self.toolchain.options["use_done_as_gpio"]  = 1 # led
        self.toolchain.options["use_cpu_as_gpio"]   = 1 # clk
        self.toolchain.options["rw_check_on_ram"]   = 1

    def create_programmer(self, kit="openfpgaloader"):
        if kit == "gowin":
            return GowinProgrammer(self.devicename)
        elif kit == "openfpgaloader":
            return OpenFPGALoader(cable="ft2232")
        else:
            raise ValueError(f"Unsupported programmer kit: {kit}")

    def do_finalize(self, fragment):
        GowinPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
