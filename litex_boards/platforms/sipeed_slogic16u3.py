#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.build.generic_platform import *
from litex.build.gowin.platform   import GowinPlatform
from litex.build.gowin.programmer import GowinProgrammer
from litex.build.openfpgaloader   import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Serial (TXD/RXD).
    ("serial", 0,
        Subsignal("tx", Pins("F14")),
        Subsignal("rx", Pins("E14")),
        IOStandard("LVCMOS33"),
    ),

    # Logic Analyzer channels (CH0..CH15).
    ("la", 0,
        Subsignal("ch", Pins(
            # CH0..CH15:
            "J14 J13 N14 P14 N13 P13 N12 P12 "
            "N11 P11 N10 P10 N9 P9 N8 P8"
        )),
        IOStandard("LVCMOS33"),
    ),
]

_connectors = []

# Platform -----------------------------------------------------------------------------------------

class Platform(GowinPlatform):
    name = "sipeed_slogic16u3"

    def __init__(self, toolchain="gowin"):
        GowinPlatform.__init__(
            self,
            device     = "GW5AT-LV15MG132C1/I0",
            io         = _io,
            connectors = _connectors,
            toolchain  = toolchain,
            devicename = "GW5AT-15A",
        )

        # Bitstream generation options.
        self.toolchain.options["bit_security"] = 0
        self.toolchain.options["bit_encrypt"]  = 0
        self.toolchain.options["bit_compress"] = 0

        # Pin repurposing options.
        self.toolchain.options["use_ready_as_gpio"] = 1
        self.toolchain.options["use_done_as_gpio"]  = 1
        self.toolchain.options["use_mspi_as_gpio"]  = 1
        self.toolchain.options["use_sspi_as_gpio"]  = 1
        self.toolchain.options["use_cpu_as_gpio"]   = 1
        self.toolchain.options["use_i2c_as_gpio"]   = 1

    def create_programmer(self, programmer="gowin"):
        if programmer == "gowin":
            return GowinProgrammer(self.devicename, cable=3)
        elif programmer == "openfpgaloader":
            return OpenFPGALoader(cable="ft2232")
        else:
            raise ValueError(f"Unsupported programmer: {programmer}")

    def do_finalize(self, fragment):
        GowinPlatform.do_finalize(self, fragment)
