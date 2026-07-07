#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 Anton Kuzmin <ak@gmm7550.dev>
#
# Based on CologneChip GateMate Evaluation Board (colognechip_gatemate_evb)
# Copyright (c) 2023 Gwenhael Goavec-merou<gwenhael.goavec-merou@trabucayre.com>
# SPDX-License-Identifier: BSD-2-Clause

# Board documentation/schematics:
# https://www.gmm7550.dev/doc/module.html

from litex.build.generic_platform import *
from litex.build.colognechip.platform import CologneChipPlatform
from litex.build.openfpgaloader import OpenFPGALoader

_io = [
    # Main reference clock (100 MHz, module PLL)
    ("ser_clk", 0, Pins("SER_CLK")),

    # SPI NOR Flash (FPGA configuration, MUXed with signals on P5 connector)
    ("spiflash", 0,
        Subsignal("cs_n", Pins("IO_WA_A8")),
        Subsignal("clk",  Pins("IO_WA_B8")),
        Subsignal("mosi", Pins("IO_WA_B7")), # D0
        Subsignal("miso", Pins("IO_WA_A7")), # D1
        Subsignal("wp",   Pins("IO_WA_B6")), # D2
        Subsignal("hold", Pins("IO_WA_A6")), # D3
    ),
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("IO_WA_A8")),
        Subsignal("clk",  Pins("IO_WA_B8")),
        Subsignal("dq",   Pins("IO_WA_B7 IO_WA_A7 IO_WA_B6 IO_WA_A6")),
    ),

    # UART
    ("serial", 0,
     Subsignal("rx", Pins("IO_WA_B6")), # SPI D2, P5/J5 pin 31
     Subsignal("tx", Pins("IO_WA_A6")), # SPI D3, P5/J5 pin 33
     ),

    # Status LEDs on the USB 3 Adapter board
    ("led_red_n", 0,  Pins("IO_WA_A2")), # CFG_FAILED_N, P5/J5 pin 35
    ("led_green", 0,  Pins("IO_WA_B2")), # CFG_DONE,     P5/J5 pin 36

    # JTAG
    ("jtag", 0,
     Subsignal("tck", Pins("IO_WA_A5")),
     Subsignal("tms", Pins("IO_WA_B4")),
     Subsignal("tdi", Pins("IO_WA_A4")),
     Subsignal("tdo", Pins("IO_WA_B3")),
     ),
]

# GMM-7550 Module Connectors
_connectors = [
    # West ------------------------
    ("P1", "-", # 0
    "   ---      ---  ", # 1 2
    "IO_WB_B1 IO_WB_B0", # 3 4
    "IO_WB_A1 IO_WB_A0", # 5 6
    "   ---      ---  ", # 7 8
    "IO_WB_B2 IO_WB_B3", # 9 10
    "IO_WB_A2 IO_WB_A3", # 11 12
    "   ---      ---  ", # 13 14
    "IO_WB_B4 IO_WB_B5", # 15 16
    "IO_WB_A4 IO_WB_A5", # 17 18
    "   ---      ---  ", # 19 20
    "IO_WB_B6 IO_WB_B7", # 21 22
    "IO_WB_A6 IO_WB_A7", # 23 24
    "   ---      ---  ", # 25 26
    "IO_WB_B8 IO_WC_B0", # 27 28
    "IO_WB_A8 IO_WC_A0", # 29 30
    "---   ---  ", # 31 32
    "---    ---   ", # 33 34
    "---   ---  ", # 35 36
    "IO_WC_B1 IO_WC_B3", # 37 38
    "IO_WC_A1 IO_WC_A3", # 39 40
    "   ---      ---  ", # 41 42
    "IO_WC_B2 IO_WC_B5", # 43 44
    "IO_WC_A2 IO_WC_A5", # 45 46
    "   ---      ---  ", # 47 48
    "IO_WC_B4 IO_WC_B8", # 49 50
    "IO_WC_A4 IO_WC_A8", # 51 52
    "   ---      ---  ", # 53 54
    "IO_WC_B6 IO_WC_B7", # 55 56
    "IO_WC_A6 IO_WC_A7", # 57 58
    "   ---      ---  ", # 59 60
     ),
    # North ------------------------
    ("P2", "-", # 0
    "   ---      ---  ", # 1 2
    "IO_NA_B2 IO_NA_B0", # 3 4
    "IO_NA_A2 IO_NA_A0", # 5 6
    "   ---      ---  ", # 7 8
    "IO_NA_B3 IO_NA_B1", # 9 10
    "IO_NA_A3 IO_NA_A1", # 11 12
    "   ---      ---  ", # 13 14
    "IO_NA_B5 IO_NA_B4", # 15 16
    "IO_NA_A5 IO_NA_A4", # 17 18
    "   ---      ---  ", # 19 20
    "IO_NA_B6 IO_NA_B7", # 21 22
    "IO_NA_A6 IO_NA_A7", # 23 24
    "   ---      ---  ", # 25 26
    "IO_NA_B8 IO_NB_B0", # 27 28
    "IO_NA_A8 IO_NB_A0", # 29 30
    "---   ---  ", # 31 32
    "---    ---   ", # 33 34
    "---   ---  ", # 35 36
    "IO_NB_B1 IO_NB_B2", # 37 38
    "IO_NB_A1 IO_NB_A2", # 39 40
    "   ---      ---  ", # 41 42
    "IO_NB_B3 IO_NB_B4", # 43 44
    "IO_NB_A3 IO_NB_A4", # 45 46
    "   ---      ---  ", # 47 48
    "IO_NB_B5 IO_NB_B7", # 49 50
    "IO_NB_A5 IO_NB_A7", # 51 52
    "   ---      ---  ", # 53 54
    "IO_NB_B6 IO_NB_B8", # 55 56
    "IO_NB_A6 IO_NB_A8", # 57 58
    "   ---      ---  ", # 59 60
     ),
    # East ------------------------
    ("P3", "-", # 0
    "   ---      ---  ", # 1 2
    "IO_EB_B7 IO_EB_B8", # 3 4
    "IO_EB_A7 IO_EB_A8", # 5 6
    "   ---      ---  ", # 7 8
    "IO_EB_B5 IO_EB_B4", # 9 10
    "IO_EB_A5 IO_EB_A4", # 11 12
    "   ---      ---  ", # 13 14
    "IO_EB_B6 IO_EB_B2", # 15 16
    "IO_EB_A6 IO_EB_A2", # 17 18
    "   ---      ---  ", # 19 20
    "IO_EB_B3 IO_EB_B0", # 21 22
    "IO_EB_A3 IO_EB_A0", # 23 24
    "   ---      ---  ", # 25 26
    "IO_EB_B1 IO_EA_B7", # 27 28
    "IO_EB_A1 IO_EA_A7", # 29 30
    "---   ---  ", # 31 32
    "---    ---   ", # 33 34
    "---   ---  ", # 35 36
    "IO_EA_B8 IO_EA_B4", # 37 38
    "IO_EA_A8 IO_EA_A4", # 39 40
    "   ---      ---  ", # 41 42
    "IO_EA_B6 IO_EA_B2", # 43 44
    "IO_EA_A6 IO_EA_A2", # 45 46
    "   ---      ---  ", # 47 48
    "IO_EA_B5 IO_EA_B1", # 49 50
    "IO_EA_A5 IO_EA_A1", # 51 52
    "   ---      ---  ", # 53 54
    "IO_EA_B3 IO_EA_B0", # 55 56
    "IO_EA_A3 IO_EA_A0", # 57 58
    "   ---      ---  ", # 59 60
     ),
    # South ------------------------
    ("P4", "-", # 0
    "   ---      ---  ", # 1 2
    "IO_SB_B8 IO_SB_B3", # 3 4
    "IO_SB_A8 IO_SB_A3", # 5 6
    "   ---      ---  ", # 7 8
    "IO_SB_B6 IO_SB_B2", # 9 10
    "IO_SB_A6 IO_SB_A2", # 11 12
    "   ---      ---  ", # 13 14
    "IO_SB_B5 IO_SB_B1", # 15 16
    "IO_SB_A5 IO_SB_A1", # 17 18
    "   ---      ---  ", # 19 20
    "IO_SB_B7 IO_SB_B0", # 21 22
    "IO_SB_A7 IO_SB_A0", # 23 24
    "   ---      ---  ", # 25 26
    "IO_SB_B4 IO_SA_B8", # 27 28
    "IO_SB_A4 IO_SA_A8", # 29 30
    "---   ---  ", # 31 32
    "---    ---   ", # 33 34
    "---   ---  ", # 35 36
    "IO_SA_B6 IO_SA_B7", # 37 38
    "IO_SA_A6 IO_SA_A7", # 39 40
    "   ---      ---  ", # 41 42
    "IO_SA_B4 IO_SA_B5", # 43 44
    "IO_SA_A4 IO_SA_A5", # 45 46
    "   ---      ---  ", # 47 48
    "IO_SA_B2 IO_SA_B3", # 49 50
    "IO_SA_A2 IO_SA_A3", # 51 52
    "   ---      ---  ", # 53 54
    "IO_SA_B1 IO_SA_B0", # 55 56
    "IO_SA_A1 IO_SA_A0", # 57 58
    "   ---      ---  ", # 59 60
     ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(CologneChipPlatform):
    default_clk_name   = "ser_clk"
    default_clk_period = 1e9/100e6

    def __init__(self, toolchain="peppercorn"):
        CologneChipPlatform.__init__(self, "CCGM1A1", _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        return OpenFPGALoader(cable="dirtyJtag")

    def do_finalize(self, fragment):
        CologneChipPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request(self.default_clk_name, loose=True),
                                   self.default_clk_period)
