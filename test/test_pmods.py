#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

import io
import os
import re
import unittest
import importlib
import contextlib

from litex.build.generic_platform import *
from litex.build.extension import Extension
from litex.build.xilinx import Xilinx7SeriesPlatform

from litex_boards.extensions import pmod

# Helpers (synthetic hosts) ------------------------------------------------------------------------

_io = [("clk", 0, Pins("A1"), IOStandard("LVCMOS33"))]

_connectors = [
    ("pmoda", "B1 B2 B3 B4 B5 B6 B7 B8"),
    ("pmodb", "C1 C2 C3 C4 C5 C6 C7 C8"),
    ("pmodr", "E1 E2 E3 E4"), # Single-row.
    ("J1",    {1: "D1", 2: "D2", 3: "D3", 4: "D4", 5: "D5", 6: "D6", 7: "D7", 8: "D8", 9: "D9"}),
]

def xilinx_platform():
    return Xilinx7SeriesPlatform("xc7a35ticsg324-1L", list(_io), list(_connectors), toolchain="vivado")

def resolved(platform):
    """Return {(resource, number, subsignal): (pins, others)} with connectors resolved."""
    r = {}
    for sig, pins, others, (name, number, sub) in platform.constraint_manager.get_sig_constraints():
        r[(name, number, sub)] = (pins, others)
    return r

def misc(others):
    return sorted(c.misc for c in others if isinstance(c, Misc))

def iostd(others):
    return [c.name for c in others if isinstance(c, IOStandard)]

# Carrier test extension ---------------------------------------------------------------------------

class _Carrier(Extension):
    slots = {"J1": "J1"}
    def define_io(self, platform):
        return [("user_led", 0, Pins("J1:9"), *self.iostandard(platform))]
    def define_connectors(self, platform):
        return [
            ("pmodc", "J1:1 J1:2 J1:3 J1:4 J1:5 J1:6 J1:7 J1:8"),
            ("hdr",   {"a": "J1:1", "b": "None"}),
        ]

# Helpers (boards) ---------------------------------------------------------------------------------

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
# Single-row (6-pin) Pmods (4 entries) are accepted.
_non_canonical_pmods = {
    "alinx_ax7010"       : ["pmodj10", "pmodj11"],                # 2x20 J10/J11 headers (aliases of j10/j11), not Pmods.
    "lattice_ecp5_evn"   : ["PMOD"],                              # Physical numbering, see pmoda.
    "microphase_a7_lite" : ["pmoda", "pmodb", "pmodc", "pmodd"],  # 2x20 headers, not Pmods.
    "trellisboard"       : ["pmodx"],                             # Extra middle pins of the dual Pmod connector.
    "trenz_smf2000"      : ["pmod"],                              # GND/VCC placeholders, see pmoda.
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

# Tests (library, on synthetic hosts) --------------------------------------------------------------

class TestPmodExtension(unittest.TestCase):
    def test_binding(self):
        with self.assertRaises(ValueError):
            pmod.PmodSDCard()                  # Unbound slot.
        with self.assertRaises(ValueError):
            pmod.PmodSDCard("pmoda", "pmodb")  # Too many connectors.
        with self.assertRaises(ValueError):
            pmod.PmodSDCard(foo="pmoda")       # Unknown slot.
        self.assertEqual(pmod.PmodDVI(a="pmoda", b="pmodb").bindings, {"a": "pmoda", "b": "pmodb"})

    def test_pmod_sdcard_xilinx(self):
        platform = xilinx_platform()
        platform.add_extension(pmod.PmodSDCard("pmoda"))
        platform.request("sdcard")
        r = resolved(platform)
        pins, others = r[("sdcard", 0, "data")]
        self.assertEqual(pins, ["B3", "B5", "B6", "B1"])
        self.assertEqual(misc(others), ["PULLUP True", "SLEW=FAST"])
        self.assertEqual(iostd(others), ["LVCMOS33"])
        self.assertEqual(r[("sdcard", 0, "cd")][0], ["B7"])

    def test_pmod_sdcard_slew(self):
        # sdcard_slew_fast=False only removes the fast slew rate on the native SDCard resource.
        platform = xilinx_platform()
        platform.add_extension(pmod.PmodSDCard("pmoda", sdcard_slew_fast=False))
        platform.request("sdcard")
        platform.request("spisdcard")
        r = resolved(platform)
        self.assertEqual(misc(r[("sdcard",    0, "data")][1]), ["PULLUP True"])
        self.assertEqual(misc(r[("spisdcard", 0, "mosi")][1]), ["PULLUP True", "SLEW=FAST"])

    def test_pmod_options(self):
        platform = xilinx_platform()
        platform.add_extension(pmod.PmodCAN("pmoda", number=1, iostandard="LVCMOS18"))
        platform.add_extension(pmod.PmodGPIO("pmodb"))
        platform.request("can", 1)
        platform.request("pmodb")
        r = resolved(platform)
        self.assertEqual(iostd(r[("can", 1, "tx")][1]), ["LVCMOS18"])
        self.assertEqual(r[("pmodb", 0, None)][0], [f"C{i}" for i in range(1, 9)])

    def test_pmod_dvi(self):
        platform = xilinx_platform()
        platform.add_extension(pmod.PmodDVI(a="pmoda", b="pmodb"))
        platform.request("dvi")
        r = resolved(platform)
        self.assertEqual(r[("dvi", 0, "r")][0], ["B6", "B2", "B5", "B1"])
        self.assertEqual(r[("dvi", 0, "clk")][0], ["C2"])

    def test_stacking(self):
        # Pmod plugged on a connector exposed by a carrier.
        platform = xilinx_platform()
        platform.add_extension(_Carrier())
        platform.add_extension(pmod.PmodUSBUART("pmodc"))
        platform.request("user_led")
        platform.request("usb_uart")
        r = resolved(platform)
        self.assertEqual(r[("user_led", 0, None)][0], ["D9"])
        self.assertEqual(r[("usb_uart", 0, "tx")][0], ["D2"])

class TestPmodOptions(unittest.TestCase):
    def test_name(self):
        platform = xilinx_platform()
        io = pmod.PmodUSBUART("pmoda", name="serial").get_io(platform)
        self.assertEqual(io[0][0], "serial")
        io = pmod.PmodSDCard("pmoda", name={"sdcard": "sdcard_pmod"}).get_io(platform)
        self.assertEqual(sorted(r[0] for r in io), ["sdcard_pmod", "spisdcard"])
        with self.assertRaises(ValueError):
            pmod.PmodSDCard("pmoda", name="foo").get_io(platform) # Several resource names.

    def test_number_offset(self):
        io = pmod.PmodUSBHostDual("pmoda", number=2).get_io(xilinx_platform())
        self.assertEqual([r[1] for r in io], [2, 3])

    def test_misc(self):
        io = pmod.PmodGPIO("pmoda", misc=Misc("DRIVE=8")).get_io(xilinx_platform())
        self.assertEqual(misc(io[0][2:]), ["DRIVE=8"])

class TestPmodModules(unittest.TestCase):
    def test_uart(self):
        platform = xilinx_platform()
        platform.add_extension(pmod.PmodUART("pmoda", tx=1, rx=0))
        platform.request("serial")
        r = resolved(platform)
        self.assertEqual((r[("serial", 0, "tx")][0], r[("serial", 0, "rx")][0]), (["B2"], ["B1"]))
        self.assertEqual(pmod.PmodUSBUART("pmoda").get_io(platform)[0][0], "usb_uart")

    def test_usb_host(self):
        platform = xilinx_platform()
        platform.add_extension(pmod.PmodUSBHostDual("pmoda", bundled=True))
        platform.add_extension(pmod.PmodUSBHostQuad("pmodb", number=1))
        platform.request("usb_host", 0)
        platform.request("usb_host", 1)
        r = resolved(platform)
        self.assertEqual(r[("usb_host", 0, "dp")][0], ["B1", "B3"])
        self.assertEqual(r[("usb_host", 1, "dm")][0], ["C5", "C6", "C7", "C8"])

    def test_leds_buttons(self):
        platform = xilinx_platform()
        platform.add_extension(pmod.PmodLED("pmoda", order=[4, 5, 6, 7, 0, 1, 2, 3], name="user_led_n"))
        platform.add_extension(pmod.Pmod1BitSquaredBreakOff("pmodb"))
        platform.add_extension(pmod.PmodWS2812("pmodb", pin=7))
        platform.request("user_led_n", 0)
        platform.request("user_btn", 0)
        platform.request("ws2812")
        r = resolved(platform)
        self.assertEqual(r[("user_led_n", 0, None)][0], ["B5"])
        self.assertEqual(r[("user_btn", 0, None)][0], ["C7"])
        self.assertEqual(r[("ws2812", 0, None)][0], ["C8"])

class TestPmodCLI(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(pmod.parse_pmod_args(["pmoda=gpio", "pmodb=sdcard"]), [("pmoda", "gpio"), ("pmodb", "sdcard")])
        with self.assertRaises(ValueError):
            pmod.parse_pmod_args(["pmoda"])
        with self.assertRaises(ValueError):
            pmod.parse_pmod_args(["pmoda=foo"])
        self.assertEqual(pmod.parse_pmod_args(["pmoda+pmodb=dvi"]), [(("pmoda", "pmodb"), "dvi")])
        with self.assertRaises(ValueError):
            pmod.parse_pmod_args(["pmoda=dvi"])       # Missing connector.
        with self.assertRaises(ValueError):
            pmod.parse_pmod_args(["pmoda+pmodb=gpio"]) # Too many connectors.

    def test_args(self):
        import argparse
        parser = argparse.ArgumentParser()
        pmod.add_pmod_args(parser)
        self.assertEqual(parser.parse_args(["--pmod", "pmoda=gpio", "--pmod", "pmodb=can"]).pmod, ["pmoda=gpio", "pmodb=can"])
        with self.assertRaises(SystemExit):
            parser.parse_args(["--pmod", "pmoda"])

    def test_add_pmods(self):
        from litex.soc.integration.soc_core import SoCCore
        platform = xilinx_platform()
        soc = SoCCore(platform, clk_freq=100e6, cpu_type=None, uart_name="stub", integrated_rom_size=0)
        pmod.add_pmods(soc, ["pmoda=gpio", "pmodb=i2c", "pmoda+pmodb=dvi"])
        self.assertEqual(platform.lookup_request("dvi", loose=True), None) # IOs only, not requested.
        platform.request("dvi")
        self.assertTrue(hasattr(soc, "pmoda_gpio"))
        self.assertTrue(hasattr(soc, "pmodb_i2c"))

    def test_add_pmods_connector_check(self):
        from litex.soc.integration.soc_core import SoCCore
        for arg, error in [
            ("pmodz=gpio",      "Unknown connector 'pmodz', Pmod connectors: pmoda, pmodb, pmodr."),
            ("J1=gpio",         "Connector 'J1' is not a Pmod connector \\(8 entries, or 4 for single-row Pmods, got 9\\)"),
            ("pmodr=gpio",      "PmodGPIO requires a dual-row \\(12-pin\\) Pmod, 'pmodr' is a single-row"),
            ("pmoda+pmodz=dvi", "Unknown connector 'pmodz'"),
        ]:
            with self.subTest(arg=arg):
                soc = SoCCore(xilinx_platform(), clk_freq=100e6, cpu_type=None, uart_name="stub", integrated_rom_size=0)
                with self.assertRaisesRegex(ValueError, error):
                    pmod.add_pmods(soc, [arg])

    def test_add_pmods_already_requested(self):
        # IOs-only Pmods can't replace resources already requested by the target.
        from litex.soc.integration.soc_core import SoCCore
        for arg, resource in [("pmoda=sdcard", "spisdcard"), ("pmoda+pmodb=dvi", "dvi")]:
            with self.subTest(arg=arg):
                platform = xilinx_platform()
                platform.add_extension(pmod.PmodSDCard("pmodb"))       # "On-board" resources.
                platform.add_extension(pmod.PmodDVI(a="pmoda", b="pmodb"))
                soc = SoCCore(platform, clk_freq=100e6, cpu_type=None, uart_name="stub", integrated_rom_size=0)
                platform.request(resource)
                with self.assertRaisesRegex(ValueError, re.escape(f"--pmod {arg}: '{resource}' is already used")):
                    pmod.add_pmods(soc, [arg])
                # Not requested yet: the Pmod takes precedence.
                soc = SoCCore(xilinx_platform(), clk_freq=100e6, cpu_type=None, uart_name="stub", integrated_rom_size=0)
                pmod.add_pmods(soc, [arg])

    def test_add_pmods_single_row(self):
        # Modules only using indexes 0-3 can be plugged on single-row (6-pin) Pmods.
        from litex.soc.integration.soc_core import SoCCore
        platform = xilinx_platform()
        soc = SoCCore(platform, clk_freq=100e6, cpu_type=None, uart_name="stub", integrated_rom_size=0)
        pmod.add_pmods(soc, ["pmodr=i2c"])
        self.assertTrue(hasattr(soc, "pmodr_i2c"))
        self.assertEqual(resolved(platform)[("i2c", 0, "scl")][0], ["E2"])

# Tests (boards) -----------------------------------------------------------------------------------

class TestPmodBoards(unittest.TestCase):
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
                    self.assertIn(len(pins), [4, 8])

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
            "digilent_arty"            : ["PULLUP True",  "SLEW=FAST"],
            "colorlight_i5"            : ["PULLMODE=UP",  "SLEWRATE=FAST"],
            "trenz_tec0117"            : ["PULL_MODE=UP"],
            "colognechip_gatemate_evb" : ["PULLUP=true"],
        }
        for host, conn in _hosts:
            if host not in expected:
                continue
            with self.subTest(host=host):
                r = _resolve(_platform(host), pmod.PmodSDCard(conn), "spisdcard")
                self.assertEqual(misc(r["mosi"][1]), sorted(expected[host]))

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
        from litex_boards.platforms import colorlight_i5
        from litex.build.lattice import LatticeECP5Platform
        with self.assertWarns(FutureWarning):
            io = colorlight_i5._sdcard_pmod_io
        self.assertEqual(repr(io), repr(pmod.PmodSDCard("pmode", sdcard_slew_fast=False).get_io(LatticeECP5Platform)))
        with self.assertRaises(AttributeError):
            digilent_arty.does_not_exist

    def test_deprecated_target_args(self):
        from litex_boards.compat import DEPRECATION_RELEASE, warn_deprecated_arg
        with self.assertWarnsRegex(FutureWarning, f"--with-pmod-gpio .* {DEPRECATION_RELEASE} .* --pmod pmoda=gpio") as cm:
            warn_deprecated_arg("--with-pmod-gpio", "--pmod pmoda=gpio")
        self.assertEqual(cm.filename, __file__) # Warning points to the target.

if __name__ == "__main__":
    unittest.main()
