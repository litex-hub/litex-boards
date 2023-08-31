#!/usr/bin/env python3

#
# This file is part of LiteX.
#
# Copyright (c) 2015-2020 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2020 Antmicro <www.antmicro.com>
# Copyright (c) 2017 Pierre-Olivier Vauboin <po@lambdaconcept>
# Copyright (c) 2023 Victor Suarez Rovere <suarezvictor@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

import sys
import argparse

from migen import *

from litex.build.generic_platform import *
from litex.build.sim import SimPlatform

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst.
    ("sys_clk", 0, Pins(1)),
    ("sys_rst", 0, Pins(1)),

    # Serial.
    ("serial", 0,
        Subsignal("source_valid", Pins(1)),
        Subsignal("source_ready", Pins(1)),
        Subsignal("source_data",  Pins(8)),

        Subsignal("sink_valid",   Pins(1)),
        Subsignal("sink_ready",   Pins(1)),
        Subsignal("sink_data",    Pins(8)),
    ),

    # Ethernet (Stream Endpoint).
    ("eth_clocks", 0,
        Subsignal("tx", Pins(1)),
        Subsignal("rx", Pins(1)),
    ),
    ("eth", 0,
        Subsignal("source_valid", Pins(1)),
        Subsignal("source_ready", Pins(1)),
        Subsignal("source_data",  Pins(8)),

        Subsignal("sink_valid",   Pins(1)),
        Subsignal("sink_ready",   Pins(1)),
        Subsignal("sink_data",    Pins(8)),
    ),

    # Ethernet (XGMII).
    ("xgmii_eth", 0,
        Subsignal("rx_data",      Pins(64)),
        Subsignal("rx_ctl",       Pins(8)),
        Subsignal("tx_data",      Pins(64)),
        Subsignal("tx_ctl",       Pins(8)),
    ),

    # Ethernet (GMII).
    ("gmii_eth", 0,
        Subsignal("rx_data",      Pins(8)),
        Subsignal("rx_dv",        Pins(1)),
        Subsignal("rx_er",        Pins(1)),
        Subsignal("tx_data",      Pins(8)),
        Subsignal("tx_en",        Pins(1)),
        Subsignal("tx_er",        Pins(1)),
    ),

    # I2C.
    ("i2c", 0,
        Subsignal("scl",     Pins(1)),
        Subsignal("sda_out", Pins(1)),
        Subsignal("sda_in",  Pins(1)),
    ),

    # SPI-Flash (X1).
    ("spiflash", 0,
        Subsignal("cs_n", Pins(1)),
        Subsignal("clk",  Pins(1)),
        Subsignal("mosi", Pins(1)),
        Subsignal("miso", Pins(1)),
        Subsignal("wp",   Pins(1)),
        Subsignal("hold", Pins(1)),
    ),

    # SPI-Flash (X4).
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins(1)),
        Subsignal("clk",  Pins(1)),
        Subsignal("dq",   Pins(4)),
    ),

    # Tristate GPIOs (for sim control/status).
    ("gpio", 0,
        Subsignal("oe", Pins(32)),
        Subsignal("o",  Pins(32)),
        Subsignal("i",  Pins(32)),
    ),

    # Video (VGA).
    ("vga", 0,
        Subsignal("hsync", Pins(1)),
        Subsignal("vsync", Pins(1)),
        Subsignal("de",    Pins(1)),
        Subsignal("r",     Pins(8)),
        Subsignal("g",     Pins(8)),
        Subsignal("b",     Pins(8)),
    )
]

# Platform -----------------------------------------------------------------------------------------

class Platform(SimPlatform):
    def __init__(self):
        SimPlatform.__init__(self, "SIM", _io)
