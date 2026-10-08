#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

import unittest

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform

from litex_boards.extensions import pmod

# Helpers ------------------------------------------------------------------------------------------

_io = [("clk", 0, Pins("A1"), IOStandard("LVCMOS33"))]

_connectors = [
    ("pmoda", "B1 B2 B3 B4 B5 B6 B7 B8"),
    ("pmodb", "C1 C2 C3 C4 C5 C6 C7 C8"),
    ("PMODC", {0: "E1", 1: "E2", 2: "E3", 3: "E4", 4: "E5", 5: "E6", 6: "E7", 7: "E8"}),
    ("pmodx", "F1 F2 F3 F4 F5 F6"),    # Not canonical.
    ("j10",   "G1 G2 G3 G4 G5 G6 G7 G8"), # Canonical but not named pmod*.
]

def platform(pmods=None):
    p = Xilinx7SeriesPlatform("xc7a35ticsg324-1L", list(_io), list(_connectors), toolchain="vivado")
    if pmods is not None:
        p.pmods = pmods
    return p

def soc(platform):
    from litex.soc.integration.soc_core import SoCCore
    return SoCCore(platform, clk_freq=100e6, cpu_type=None, uart_name="stub", integrated_rom_size=0)

# Tests --------------------------------------------------------------------------------------------

class TestPmodConnectors(unittest.TestCase):
    def test_list(self):
        self.assertEqual(pmod.get_pmod_connectors(platform()), ["pmoda", "pmodb", "PMODC"])

    def test_list_explicit(self):
        self.assertEqual(pmod.get_pmod_connectors(platform(pmods=["j10", "pmoda"])), ["j10", "pmoda"])

    def test_check(self):
        p = platform()
        for conn in ["pmoda", "PMODC", "j10"]:
            pmod.check_pmod_connector(p, conn)
        with self.assertRaisesRegex(ValueError, "Unknown connector 'pmodz', Pmod connectors: pmoda, pmodb, PMODC"):
            pmod.check_pmod_connector(p, "pmodz")
        with self.assertRaisesRegex(ValueError, "not a canonical Pmod connector \\(8 entries, got 6\\)"):
            pmod.check_pmod_connector(p, "pmodx")

class TestPmodCores(unittest.TestCase):
    def test_cli_modules(self):
        # Modules available from the command line are the ones implementing add_cores().
        self.assertEqual(sorted(pmod._cli_pmods), sorted(["gpio", "usb_uart", "sdcard", "numato_sdcard", "i2c", "can", "dvi"]))
        for name in pmod._cli_pmods:
            self.assertTrue(hasattr({**pmod.pmods, **pmod.multi_pmods}[name], "add_cores"))

    def test_cores(self):
        p = platform()
        s = soc(p)
        pmod.add_pmods(s, ["pmoda=gpio", "pmodb=i2c", "PMODC=i2c", "j10=usb_uart"])
        self.assertTrue(hasattr(s, "pmoda_gpio"))
        self.assertTrue(hasattr(s, "pmodb_i2c"))
        self.assertTrue(hasattr(s, "PMODC_i2c"))
        self.assertTrue(hasattr(s, "j10_usb_uart"))
        # Resources requested by the cores, with numbers incremented per module.
        self.assertIsNotNone(p.lookup_request("pmoda"))
        self.assertIsNotNone(p.lookup_request("i2c", 0))
        self.assertIsNotNone(p.lookup_request("i2c", 1))
        self.assertIsNotNone(p.lookup_request("usb_uart", 0))

    def test_io_only(self):
        p = platform()
        s = soc(p)
        pmod.add_pmods(s, ["pmoda=sdcard", "pmoda+pmodb=dvi"])
        # IOs only: added to the platform but not requested.
        self.assertIsNone(p.lookup_request("sdcard", loose=True))
        self.assertIsNone(p.lookup_request("dvi",    loose=True))
        p.request("sdcard")
        p.request("dvi")

    def test_validation(self):
        with self.assertRaisesRegex(ValueError, "Unknown connector 'pmodz'"):
            pmod.add_pmods(soc(platform()), ["pmodz=gpio"])
        with self.assertRaisesRegex(ValueError, "Unknown connector 'pmodz'"):
            pmod.add_pmods(soc(platform()), ["pmoda+pmodz=dvi"])
        with self.assertRaisesRegex(ValueError, "not a canonical Pmod connector"):
            pmod.add_pmods(soc(platform()), ["pmodx=i2c"])

if __name__ == "__main__":
    unittest.main()
