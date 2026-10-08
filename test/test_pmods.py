#
# This file is part of LiteX-Boards.
#
# SPDX-License-Identifier: BSD-2-Clause

import io
import os
import re
import unittest
import importlib
import contextlib

from litex.build.generic_platform import Misc, IOStandard
from litex.build import pmod

# Helpers ------------------------------------------------------------------------------------------

_platforms_dir = os.path.join(os.path.dirname(__file__), "..", "litex_boards", "platforms")

def _platform(name, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return importlib.import_module(f"litex_boards.platforms.{name}").Platform(**kwargs)

def _resolve(platform, extension, resource):
    platform.add_extension(extension)
    platform.request(resource)
    r = {}
    for sig, pins, others, (name, number, sub) in platform.constraint_manager.get_sig_constraints():
        r[sub] = (pins, others)
    return r

# Connectors named pmod* that are not canonical 8-pin Pmods (index 0-3: pins 1-4, 4-7: pins 7-10).
_non_canonical_pmods = {
    "alinx_ax7010"       : ["pmodj10", "pmodj11"],                     # Headers named pmod.
    "kosagi_fomu_evt"    : ["pmoda_n", "pmodb_n"],                      # 4-pin.
    "lattice_ecp5_evn"   : ["PMOD"],                                    # Physical numbering, see pmoda.
    "machdyne_krote"     : ["PMODC", "PMODD"],                          # 7-pin.
    "microphase_a7_lite" : ["pmoda", "pmodb", "pmodc", "pmodd"],        # Headers named pmod.
    "trellisboard"       : ["pmodx"],                                   # 6-pin.
    "trenz_smf2000"      : ["pmod"],                                    # GND/VCC placeholders, see pmoda.
    "xilinx_ac701"       : ["pmod"],                                    # 4-pin.
}

# Hosts from different vendors, with a Pmod connector.
_hosts = [
    ("digilent_arty",            "pmoda"),  # Xilinx.
    ("colorlight_i5",            "pmode"),  # Lattice ECP5.
    ("trenz_tec0117",            "pmod"),   # Gowin.
    ("colognechip_gatemate_evb", "PMODA"),  # CologneChip.
    ("efinix_t120_f576_dev_kit", "pmod_a"), # Efinix.
    ("lattice_ecp5_evn",         "pmoda"),  # Lattice ECP5 (alias on physical numbering).
]

# Tests --------------------------------------------------------------------------------------------

class TestPmods(unittest.TestCase):
    def test_pmod_connectors_are_canonical(self):
        for f in sorted(os.listdir(_platforms_dir)):
            if not f.endswith(".py") or f.startswith("_"):
                continue
            name = f[:-3]
            try:
                platform = _platform(name)
            except Exception:
                continue # Platforms requiring arguments/tools.
            for conn, pins in platform.constraint_manager.connector_manager.connector_table.items():
                if not re.match(r"pmod", conn, re.I) or isinstance(pins, dict):
                    continue
                if conn in _non_canonical_pmods.get(name, []):
                    continue
                with self.subTest(platform=name, connector=conn):
                    self.assertEqual(len(pins), 8)

    def test_pmods_on_hosts(self):
        for host, conn in _hosts:
            for module, cls in pmod.pmods.items():
                with self.subTest(host=host, module=module):
                    try:
                        platform = _platform(host)
                    except OSError as e:
                        # Some vendor platforms (ex: Efinix) require their toolchain to be created.
                        self.skipTest(f"{host}: {e}".splitlines()[0])
                    extension = cls(conn)
                    platform.add_extension(extension)
                    for name, number, *_ in extension.get_io(platform):
                        platform.request(name, number)
                    for sig, pins, others, resource in platform.constraint_manager.get_sig_constraints():
                        for p in pins:
                            self.assertNotIn(":", p) # Fully resolved to FPGA pins.

    def test_sdcard_vendor_attributes(self):
        expected = {
            "digilent_arty"            : "PULLUP True",
            "colorlight_i5"            : "PULLMODE=UP",
            "trenz_tec0117"            : "PULL_MODE=UP",
            "colognechip_gatemate_evb" : "PULLUP=true",
        }
        for host, conn in _hosts:
            if host not in expected:
                continue
            with self.subTest(host=host):
                r = _resolve(_platform(host), pmod.PmodSDCard(conn), "spisdcard")
                self.assertIn(expected[host], [c.misc for c in r["mosi"][1] if isinstance(c, Misc)])

    def test_deprecated_board_helpers(self):
        # Deprecated board helpers warn and still generate the same IOs as the library.
        from litex_boards.platforms import digilent_arty, icebreaker
        from litex.build.lattice import LatticeiCE40Platform
        with self.assertWarns(FutureWarning):
            io = digilent_arty.sdcard_pmod_io("pmodd")
        self.assertEqual(repr(io), repr(pmod.PmodSDCard("pmodd").get_io(_platform("digilent_arty"))))
        with self.assertWarns(FutureWarning):
            io = icebreaker.break_off_pmod
        self.assertEqual(repr(io), repr(pmod.Pmod1BitSquaredBreakOff("PMOD2").get_io(LatticeiCE40Platform)))
        with self.assertRaises(AttributeError):
            digilent_arty.does_not_exist

if __name__ == "__main__":
    unittest.main()
