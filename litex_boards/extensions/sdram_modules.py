#
# This file is part of LiteX-Boards.
#
# SPDX-License-Identifier: BSD-2-Clause

"""SDRAM modules plugged on 40-pin headers (as on Sipeed Tang boards/docks).

IOStandard is the platform's 3.3V default; Misc constraints are Gowin specific (these modules are
currently only used on Gowin boards).
"""

from litex.build.generic_platform import Subsignal, Pins, Misc
from litex.build.extension import Extension

# MiSTer SDRAM -------------------------------------------------------------------------------------

class MiSTerSDRAM(Extension):
    """MiSTer SDRAM module (32MB, 16-bit)."""
    slots = {"conn": None}

    def define_io(self, platform):
        return [
            ("sdram_clock", 0, Pins("conn:20"),
                *self.iostandard(platform),
                Misc("PULL_MODE=NONE DRIVE=16"),
            ),
            ("sdram", 0,
                Subsignal("a",   Pins(
                    "conn:37 conn:38 conn:39 conn:40 conn:28 conn:25 conn:26 conn:23",
                    "conn:24 conn:21 conn:36 conn:22 conn:19")
                ),
                Subsignal("dq",  Pins(
                    "conn:1  conn:2  conn:3  conn:4  conn:5  conn:6  conn:7  conn:8",
                    "conn:18 conn:17 conn:16 conn:15 conn:14 conn:13 conn:10 conn:9")
                ),
                Subsignal("ba",    Pins("conn:34 conn:35")),
                Subsignal("cas_n", Pins("conn:31")),
                Subsignal("cs_n",  Pins("conn:33")),
                Subsignal("ras_n", Pins("conn:32")),
                Subsignal("we_n",  Pins("conn:27")),
                *self.iostandard(platform),
            ),
        ]

# Sipeed SDRAM -------------------------------------------------------------------------------------

class SipeedSDRAM(Extension):
    """Sipeed SDRAM module (32MB, 16-bit, with DQM)."""
    slots = {"conn": None}

    def define_io(self, platform):
        return [
            ("sdram_clock", 0, Pins("conn:20"),
                *self.iostandard(platform),
                Misc("PULL_MODE=NONE DRIVE=16"),
            ),
            ("sdram", 0,
                Subsignal("a",   Pins(
                    "conn:37 conn:38 conn:39 conn:40 conn:28 conn:25 conn:26 conn:23",
                    "conn:24 conn:21 conn:36 conn:22 conn:19")
                ),
                Subsignal("dq",  Pins(
                    "conn:1  conn:2  conn:3  conn:4  conn:5  conn:6  conn:7  conn:8",
                    "conn:18 conn:17 conn:16 conn:15 conn:14 conn:13 conn:10 conn:9"),
                ),
                Subsignal("ba",    Pins("conn:34 conn:35")),
                Subsignal("cas_n", Pins("conn:31")),
                Subsignal("cs_n",  Pins("conn:33")),
                Subsignal("ras_n", Pins("conn:32")),
                Subsignal("we_n",  Pins("conn:27")),
                Subsignal("dm",    Pins("conn:29 conn:30")),
                *self.iostandard(platform),
            ),
        ]
