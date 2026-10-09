#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

import unittest
import warnings

from litex.build.generic_platform import IOStandard

from litex_boards.extensions.syzygy import SyzygyGPIO

# Helpers ------------------------------------------------------------------------------------------

def resolved(platform):
    """Return {(resource, number, subsignal): (pins, others)} with connectors resolved."""
    r = {}
    for sig, pins, others, (name, number, sub) in platform.constraint_manager.get_sig_constraints():
        for pin in pins:
            assert ":" not in pin, f"{name}:{number}: {pin} not resolved"
        r[(name, number, sub)] = (pins, others)
    return r

def iostd(others):
    return [c.name for c in others if isinstance(c, IOStandard)]

# Tests --------------------------------------------------------------------------------------------

class TestSyzygy(unittest.TestCase):
    def test_gpio_butterstick(self):
        from litex_boards.platforms import gsd_butterstick
        platform = gsd_butterstick.Platform()
        platform.add_extension(SyzygyGPIO("SYZYGY0", signals=32))
        platform.request("SYZYGY0")
        pins, others = resolved(platform)[("SYZYGY0", 0, None)]
        self.assertEqual(len(pins), 32)
        self.assertEqual(pins[:2], ["G2", "J3"])
        self.assertEqual(pins[28:], ["H2", "P1", "G1", "P2"]) # S28-S31 on clock pins.
        self.assertEqual(iostd(others), ["LVCMOS33"])

    def test_gpio_xem8320(self):
        from litex_boards.platforms import opalkelly_xem8320
        platform = opalkelly_xem8320.Platform()
        platform.add_extension(SyzygyGPIO("SYZYGYA", iostandard="LVCMOS18"))
        platform.request("SYZYGYA")
        pins, others = resolved(platform)[("SYZYGYA", 0, None)]
        self.assertEqual(len(pins), 28)
        self.assertEqual(pins[-1], "J25")
        self.assertEqual(iostd(others), ["LVCMOS18"])

    def test_deprecated_butterstick_helper(self):
        from litex_boards.platforms import gsd_butterstick
        from litex_boards.compat import DEPRECATION_RELEASE
        with self.assertWarnsRegex(FutureWarning, DEPRECATION_RELEASE) as cm:
            io = gsd_butterstick.raw_syzygy_io("SYZYGY1")
        self.assertEqual(cm.filename, __file__) # Warning points to the caller.
        self.assertEqual(io[0][0], "SYZYGY1")
        self.assertEqual(len(io[0][2].identifiers), 32)

if __name__ == "__main__":
    unittest.main()
