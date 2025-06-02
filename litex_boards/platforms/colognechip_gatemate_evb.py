#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2023 Gwenhael Goavec-merou<gwenhael.goavec-merou@trabucayre.com>
# SPDX-License-Identifier: BSD-2-Clause

# Board documentation/schematics:
# https://colognechip.com/docs/ds1003-gatemate1-evalboard-3v1-latest.pdf

from litex.build.generic_platform import *
from litex.build.colognechip.platform import CologneChipPlatform
from litex.build.openfpgaloader import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk10",    0, Pins("IO_SB_A8"), Misc("SCHMITT_TRIGGER=true")),

    # Leds
    ("user_led_n", 0, Pins("IO_EB_B1")),
    ("user_led_n", 1, Pins("IO_EB_B2")),
    ("user_led_n", 2, Pins("IO_EB_B3")),
    ("user_led_n", 3, Pins("IO_EB_B4")),
    ("user_led_n", 4, Pins("IO_EB_B5")),
    ("user_led_n", 5, Pins("IO_EB_B6")),
    ("user_led_n", 6, Pins("IO_EB_B7")),
    ("user_led_n", 7, Pins("IO_EB_B8")),

    # Button
    ("user_btn_n", 0, Pins("IO_EB_B0")),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("IO_WA_A8")),
        Subsignal("clk",  Pins("IO_WA_B8"), Misc("SLEW=fast")),
        Subsignal("miso", Pins("IO_WA_B7")),
        Subsignal("mosi", Pins("IO_WA_A7")),
        Subsignal("wp",   Pins("IO_WA_B6")),
        Subsignal("hold", Pins("IO_WA_A6")),
    ),
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("IO_WA_A8")),
        Subsignal("clk",  Pins("IO_WA_B8"), Misc("SLEW=fast")),
        Subsignal("dq",   Pins("IO_WA_B7 IO_WA_A7 IO_WA_B6 IO_WA_A6")),
    ),

    # HyperRAM
    ("hyperram", 0,
        Subsignal("dq", Pins("IO_WB_A5 IO_WB_B5 IO_WB_A6 IO_WB_B6 IO_WB_A7 IO_WB_B7 IO_WB_A8 IO_WB_B8")),
        Subsignal("rwds", Pins("IO_WB_B4")),
        Subsignal("cs_n", Pins("IO_WB_B0")),
        Subsignal("rst_n", Pins("IO_WB_A2")),
        Subsignal("clk_p", Pins("IO_WB_A3")),
        Subsignal("clk_n", Pins("IO_WB_B3")),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("PMODA", "IO_NB_A0 IO_NB_A1 IO_NB_A2 IO_NB_A3 IO_NB_B0 IO_NB_B1 IO_NB_B2 IO_NB_B3"),
    ("PMODB", "IO_NB_A4 IO_NB_A5 IO_NB_A6 IO_NB_A7 IO_NB_B4 IO_NB_B5 IO_NB_B6 IO_NB_B7"),
    ("io_na", "IO_NA_A0 IO_NA_B0",
              "IO_NA_A1 IO_NA_B1",
              "IO_NA_A2 IO_NA_B2",
              "IO_NA_A3 IO_NA_B3",
              "IO_NA_A4 IO_NA_B4",
              "IO_NA_A5 IO_NA_B5",
              "IO_NA_A6 IO_NA_B6",
              "IO_NA_A7 IO_NA_B7",
              "IO_NA_A8 IO_NA_B8"),
    ("io_nb", "IO_NB_A4 IO_NB_A5",
              "IO_NB_A6 IO_NB_A7",
              "IO_NB_B4 IO_NB_B5",
              "IO_NB_B6 IO_NB_B7"),
    ("io_ea", "IO_EA_A0 IO_EA_B0",
              "IO_EA_A1 IO_EA_B1",
              "IO_EA_A2 IO_EA_B2",
              "IO_EA_A3 IO_EA_B3",
              "IO_EA_A4 IO_EA_B4",
              "IO_EA_A5 IO_EA_B5",
              "IO_EA_A6 IO_EA_B6",
              "IO_EA_A7 IO_EA_B7",
              "IO_EA_A8 IO_EA_B8"),
    ("io_sa", "IO_SA_A0 IO_SA_B0",
              "IO_SA_A1 IO_SA_B1",
              "IO_SA_A2 IO_SA_B2",
              "IO_SA_A3 IO_SA_B3",
              "IO_SA_A4 IO_SA_B4",
              "IO_SA_A5 IO_SA_B5",
              "IO_SA_A6 IO_SA_B6",
              "IO_SA_A7 IO_SA_B7",
              "IO_SA_A8 IO_SA_B8"),
    ("io_sb", "IO_SB_A0 IO_SB_B0",
              "IO_SB_A1 IO_SB_B1",
              "IO_SB_A2 IO_SB_B2",
              "IO_SB_A3 IO_SB_B3",
              "IO_SB_A4 IO_SB_B4",
              "IO_SB_A5 IO_SB_B5",
              "IO_SB_A6 IO_SB_B6",
              "IO_SB_A7 IO_SB_B7",
              "IO_SB_A8 IO_SB_B8"),

    ("io_wc", "IO_WC_A0 IO_WC_B0",
              "IO_WC_A1 IO_WC_B1",
              "IO_WC_A2 IO_WC_B2",
              "IO_WC_A3 IO_WC_B3",
              "IO_WC_A4 IO_WC_B4",
              "IO_WC_A5 IO_WC_B5",
              "IO_WC_A6 IO_WC_B6",
              "IO_WC_A7 IO_WC_B7",
              "IO_WC_A8 IO_WC_B8"),
]

# PMODS --------------------------------------------------------------------------------------------

def usb_pmod_io(pmod):
    return [
        # USB-UART PMOD: https://store.digilentinc.com/pmod-usbuart-usb-to-uart-interface/
        ("usb_uart", 0,
            Subsignal("tx", Pins(f"{pmod}:1")),
            Subsignal("rx", Pins(f"{pmod}:2")),
        ),
    ]

def pmods_sdcard_io(pmod):
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
# Platform -----------------------------------------------------------------------------------------

class Platform(CologneChipPlatform):
    default_clk_name   = "clk10"
    default_clk_period = 1e9/10e6

    def __init__(self, toolchain="colognechip"):
        CologneChipPlatform.__init__(self, "CCGM1A1", _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        return OpenFPGALoader("gatemate_evb_jtag")

    def do_finalize(self, fragment):
        CologneChipPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk10", loose=True), 1e9/10e6)
