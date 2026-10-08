#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

"""SYZYGY pods, described once as Extensions and usable on any board exposing SYZYGY connectors.

Canonical SYZYGY connector (Opal Kelly SYZYGY specification): a dict connector using the signal
names of the specification as keys:

- Standard ports:
    - S0-S27              : Single-ended signals.
    - D0P/D0N-D7P/D7N     : Differential pairs (aliases of S0-S15: D0P=S0, D0N=S2, D1P=S1, D1N=S3...).
    - P2C_CLKP/P2C_CLKN   : Peripheral to carrier clock.
    - C2P_CLKP/C2P_CLKN   : Carrier to peripheral clock.
- Transceiver ports:
    - TXnP/TXnN, RXnP/RXnN: Transceiver lanes.
    - REFCLKnP/REFCLKnN   : Transceiver reference clocks.

Boards may expose extra signals (ex ButterStick: S28-S31 on the clock pins). Boards declaring their
SYZYGY ports with other keys should expose a canonical alias connector.

Usage:

    from litex_boards.extensions.syzygy import SyzygyGPIO
    platform.add_extension(SyzygyGPIO("SYZYGY0"))
    gpio_pads = platform.request("SYZYGY0")
"""

from litex.build.generic_platform import Pins
from litex.build.extension import Extension

# SYZYGY Extension ---------------------------------------------------------------------------------

class SyzygyExtension(Extension):
    slots          = {"syzygy": None}
    connector_type = "syzygy"

# GPIO ---------------------------------------------------------------------------------------------

class SyzygyGPIO(SyzygyExtension):
    """Raw GPIO resource on S0-S(n-1), named after the host connector (ex: request("SYZYGY0")).

    signals: Number of single-ended signals (default: 28, S0-S27 of a SYZYGY standard port).
    """
    def __init__(self, *args, signals=28, **kwargs):
        self.signals = signals
        SyzygyExtension.__init__(self, *args, **kwargs)

    def define_io(self, platform):
        return [
            (self.bindings["syzygy"], 0, Pins(" ".join(f"syzygy:S{i}" for i in range(self.signals))), *self.iostandard(platform)),
        ]
