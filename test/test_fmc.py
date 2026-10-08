#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

import unittest
import importlib

from litex_boards.extensions.fmc import FMCRAID

# Helpers ------------------------------------------------------------------------------------------

def resolved(platform):
    """Return {(resource, number, subsignal): pins} with connectors resolved."""
    r = {}
    for sig, pins, others, (name, number, sub) in platform.constraint_manager.get_sig_constraints():
        for pin in pins:
            assert ":" not in pin, f"{name}:{number}: {pin} not resolved"
        r[(name, number, sub)] = pins
    return r

# Tests --------------------------------------------------------------------------------------------

class TestFMC(unittest.TestCase):
    def test_fmcraid(self):
        # (platform, FMC connector, expected (clk_p, tx_p, rx_p) pins).
        hosts = [
            ("digilent_nexys_video", "LPC", ["F10", "D7", "D9"]),
            ("xilinx_kc705",         "LPC", ["N8",  "F2", "F6"]),
            ("xilinx_kc705",         "HPC", ["C8",  "D2", "E4"]),
            ("digilent_genesys2",    "HPC", ["L8",  "Y2", "AA4"]),
        ]
        for name, fmc, expected in hosts:
            with self.subTest(platform=name, fmc=fmc):
                platform = importlib.import_module(f"litex_boards.platforms.{name}").Platform()
                platform.add_extension(FMCRAID(fmc))
                platform.request("fmc2sata")
                r = resolved(platform)
                self.assertEqual([r[("fmc2sata", 0, s)][0] for s in ["clk_p", "tx_p", "rx_p"]], expected)

if __name__ == "__main__":
    unittest.main()
