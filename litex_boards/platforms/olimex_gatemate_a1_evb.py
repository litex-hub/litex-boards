#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2024 Gwenhael Goavec-merou<gwenhael.goavec-merou@trabucayre.com>
# SPDX-License-Identifier: BSD-2-Clause

# Board documentation/schematics:
# https://www.olimex.com/Products/FPGA/GateMate/GateMateA1-EVB/open-source-hardware

from litex.build.generic_platform import *
from litex.build.colognechip.platform import CologneChipPlatform
from litex.build.openfpgaloader import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk0",    0, Pins("IO_SB_A8"), Misc("SCHMITT_TRIGGER=true")),

    # Leds
    ("user_led_n", 0, Pins("IO_SB_B6")),

    # Button
    ("user_btn_n", 0, Pins("IO_SB_B7")),

    # Serial.
    ("serial", 0,
        Subsignal("tx", Pins("IO_SA_B6")),
        Subsignal("rx", Pins("IO_SA_A6"))
    ),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("IO_WA_A8")),
        Subsignal("clk",  Pins("IO_WA_B8")),
        Subsignal("miso", Pins("IO_WA_B7")),
        Subsignal("mosi", Pins("IO_WA_A7")),
        Subsignal("wp",   Pins("IO_WA_B6")),
        Subsignal("hold", Pins("IO_WA_B6")),
    ),
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("IO_WA_A8")),
        Subsignal("clk",  Pins("IO_WA_B8")),
        Subsignal("dq",   Pins("IO_WA_B7 IO_WA_A7 IO_WA_B6 IO_WA_B6")),
    ),

    # QPSRAM
    ("qpsram", 0,
        Subsignal("ck",   Pins("IO_WC_B4")),
        Subsignal("cs_n", Pins("IO_WC_A4")),
        Subsignal("data", Pins("IO_WC_A5 IO_WC_B5 IO_WC_A6 IO_WC_B6 IO_WC_A7 IO_WC_B7 IO_WC_A8 IO_WC_B8")),
    ),

    # VGA
    ("vga", 0,
        Subsignal("hsync_n", Pins("IO_WB_A1")),
        Subsignal("vsync_n", Pins("IO_WB_B1")),
        Subsignal("r", Pins("IO_WB_B3 IO_WB_A3 IO_WB_B2 IO_WB_A2")),
        Subsignal("g", Pins("IO_WB_B5 IO_WB_A5 IO_WB_B4 IO_WB_A4")),
        Subsignal("b", Pins("IO_WB_B7 IO_WB_A7 IO_WB_B6 IO_WB_A6")),
    ),

    # PS2 ports.
    ("ps2", 0,
        Subsignal("clk", Pins("IO_WB_A0")),
        Subsignal("data", Pins("iO_WB_B0")),
    ),

]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("PMOD", "IO_EA_A4 IO_EA_A5 IO_EA_A6 IO_EA_A7 IO_EA_B4 IO_EA_B5 IO_EA_B6 IO_EA_B7"),
    #              3V3      GND
    ("UEXT", "-------- -------- IO_EA_A0 IO_EA_B0 IO_EA_A1 IO_EA_B1 IO_EA_A2 IO_EA_B2 IO_EA_A3 IO_EA_B3"),
    ["bank_na1", 
        "---", # 0 
        #   VDD_NA      GND                                                                           ( 1-10)
        " -------- -------- IO_NA_A0 IO_NA_B0 IO_NA_A1 IO_NA_B1 IO_NA_A2 IO_NA_B2 IO_NA_A3 IO_NA_B3",
        #                                                                                             (11-20)
        " IO_NA_A4 IO_NA_B4 IO_NA_A5 IO_NA_B5 IO_NA_A6 IO_NA_B6 IO_NA_A7 IO_NA_B7 IO_NA_A8 IO_NA_B8",
    ],
    ["bank_nb1", 
        "---", # 0 
        #   VDD_NB      GND                                                                           ( 1-10)
        " -------- -------- IO_NB_A0 IO_NB_B0 IO_NB_A1 IO_NB_B1 IO_NB_A2 IO_NB_B2 IO_NB_A3 IO_NB_B3",
        #                                                                                             (11-20)
        " IO_NB_A4 IO_NB_B4 IO_NB_A5 IO_NB_B5 IO_NB_A6 IO_NB_B6 IO_NB_A7 IO_NB_B7 IO_NB_A8 IO_NB_B8",
    ],
    ["bank_eb1", 
        "---", # 0 
        #   VDD_EB      GND                                                                           ( 1-10)
        " -------- -------- IO_EB_A8 IO_EB_B8 IO_EB_A7 IO_EB_B7 IO_EB_A6 IO_EB_B6 IO_EB_A5 IO_EB_B5",
        #                                                                                             (11-20)
        " IO_EB_A4 IO_EB_B4 IO_EB_A3 IO_EB_B3 IO_EB_A2 IO_EB_B2 IO_EB_A1 IO_EB_B1 IO_EB_A0 IO_EB_B0",
    ],
    ["bank_misc1", 
        "---", # 0 
        #      2V5       1V8                                                                            ( 1-10)
        " -------- --------- IO_WA_B5 IO_WC_B3 IO_EA_A8 IO_WC_A3 IO_EA_B8 IO_WC_B2 IO_WB_A8  IO_WC_A2",
        #                                                                                   SER_CLK_N   (11-20)
        " IO_WB_B8  IO_WC_B1 IO_SB_B3 IO_WC_A1 IO_SB_A3 IO_WC_B0 IO_SB_A2 IO_WC_A0 IO_SB_A2 ---------",
        #          SER_CLK_P          SER_TX_P          SER_TX_N          SER_RX_N           SER_RX_P   (21-30)
        " IO_SB_B1 --------- IO_SB_A1 -------- IO_SB_B0 -------- IO_SB_A0 -------- IO_SB_A2 ---------",
        #                         GND      GND                                                          (31-34)
        " IO_SB_A8  IO_SB_A5 -------- --------",
    ],
]

# PMODs --------------------------------------------------------------------------------------------

def pmods_io(pmod):
    return [
        # SDCard PMOD:
        # - https://store.digilentinc.com/pmod-microsd-microsd-card-slot/
        ("spisdcard", 0,
            Subsignal("clk",  Pins(f"{pmod}:3")),
            Subsignal("mosi", Pins(f"{pmod}:1"), Misc("PULLUP=true")),
            Subsignal("cs_n", Pins(f"{pmod}:0"), Misc("PULLUP=true")),
            Subsignal("miso", Pins(f"{pmod}:2"), Misc("PULLUP=true")),
        ),
        ("sdcard", 0,
            Subsignal("data", Pins(f"{pmod}:2 {pmod}:4 {pmod}:5 {pmod}:0"), Misc("PULLUP=true")),
            Subsignal("cmd",  Pins(f"{pmod}:1"), Misc("PULLUP=true")),
            Subsignal("clk",  Pins(f"{pmod}:3")),
            Subsignal("cd",   Pins(f"{pmod}:6")),
        ),
]
_pmods_io = pmods_io("PMOD")

# Platform -----------------------------------------------------------------------------------------

class Platform(CologneChipPlatform):
    default_clk_name   = "clk0"
    default_clk_period = 1e9/10e6

    def __init__(self, toolchain="colognechip"):
        CologneChipPlatform.__init__(self, "CCGM1A1", _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        return OpenFPGALoader(cable="dirtyJtag")

    def do_finalize(self, fragment):
        CologneChipPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk0", loose=True), 1e9/10e6)
