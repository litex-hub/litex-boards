#
# This file is part of LiteX-Boards.
#
# SPDX-License-Identifier: BSD-2-Clause

import io
import unittest
import importlib
import contextlib

from litex.build.generic_platform import IOStandard

# Helpers ------------------------------------------------------------------------------------------

def _platform(name, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return importlib.import_module(f"litex_boards.platforms.{name}").Platform(**kwargs)

def _request_all(platform):
    """Request all available resources and check they all resolve to FPGA pins."""
    for name, number, *_ in list(platform.constraint_manager.available):
        platform.request(name, number)
    for sig, pins, others, resource in platform.constraint_manager.get_sig_constraints():
        for pin in pins:
            assert pin is None or ":" not in pin, f"{resource}: {pin} not resolved"

_qmtech_core_boards = [
    "qmtech_xc7a35t",
    "qmtech_xc7k325t",
    "qmtech_artix7_fbg484",
    "qmtech_artix7_fgg676",
    "qmtech_10cl006",
    "qmtech_5cefa2",
    "qmtech_5cefa5",
    "qmtech_ep4cgx150",
    "qmtech_ep4cex5",
]

# Tests --------------------------------------------------------------------------------------------

class TestExtensions(unittest.TestCase):
    def test_qmtech_daughterboards(self):
        for board in _qmtech_core_boards:
            with self.subTest(board=board):
                # Platform can be created several times (no module-level IOs/connectors mutation).
                for i in range(2):
                    _request_all(_platform(board, with_daughterboard=True))
                    _request_all(_platform(board, with_daughterboard=False))
        _request_all(_platform("qmtech_artix7_fgg676", with_rp2040_daughterboard=True))

    def test_qmtech_pmod_on_daughterboard(self):
        # Pmod plugged on a connector exposed by the daughterboard (stacking).
        from litex_boards.extensions.pmod import PmodSDCard
        platform = _platform("qmtech_xc7a35t", with_daughterboard=True)
        platform.add_extension(PmodSDCard("pmoda"), prepend=True)
        platform.request("spisdcard")
        _request_all(platform)

    def test_qmtech_compat(self):
        from litex_boards.platforms.qmtech_daughterboard import QMTechDaughterboard
        db = QMTechDaughterboard(IOStandard("LVCMOS33"))
        with self.assertWarns(FutureWarning):
            self.assertEqual(db.io[0][0], "serial")
        with self.assertWarns(FutureWarning):
            self.assertEqual([c[0] for c in db.connectors], ["pmoda", "pmodb", "J1"])

    def test_enclustra_st1(self):
        from litex_boards.extensions.enclustra import EnclustraST1
        a = _platform("enclustra_mercury_kx2")
        with self.assertWarns(FutureWarning):
            a.add_baseboard(EnclustraST1())
        b = _platform("enclustra_mercury_kx2")
        b.add_extension(EnclustraST1())
        self.assertEqual(repr(a.constraint_manager.available), repr(b.constraint_manager.available))

    def test_sipeed_docks(self):
        for board in ["sipeed_tang_primer_20k", "sipeed_tang_primer_25k", "sipeed_tang_mega_138k",
                      "sipeed_tang_mega_138k_pro", "sipeed_tang_mega_60k"]:
            docks = importlib.import_module(f"litex_boards.platforms.{board}").docks
            for dock in [None, *docks]:
                with self.subTest(board=board, dock=dock):
                    _request_all(_platform(board, dock=dock))
            with self.assertRaises(ValueError):
                _platform(board, dock="unknown")

    def test_enclustra_st1_on_kx2(self):
        # All ST1 IOs resolve on KX2 except the ones not connected on KX2 (C pins below 69).
        from litex_boards.extensions.enclustra import EnclustraST1
        not_connected = {"clk_ref", "clk_ref1", "hdmi", "sfp_tx", "sfp_rx"}
        for name, number, *_ in EnclustraST1().get_io(_platform("enclustra_mercury_kx2")):
            if name in not_connected:
                continue
            with self.subTest(resource=name):
                platform = _platform("enclustra_mercury_kx2")
                platform.add_extension(EnclustraST1(), prepend=True)
                platform.request(name, number)
                platform.constraint_manager.get_sig_constraints()
        # clk_ref0 is on MGTREFCLK0_116 (D6/D5).
        platform = _platform("enclustra_mercury_kx2")
        platform.add_extension(EnclustraST1(), prepend=True)
        platform.request("clk_ref0")
        pins = {res[2]: p for s, p, o, res in platform.constraint_manager.get_sig_constraints()}
        self.assertEqual(pins, {"p": ["D6"], "n": ["D5"]})

    def test_enclustra_xu8_module_connectors(self):
        # XU8 module connectors are described as Mercury+ A/B/C connectors, so baseboard extensions
        # written against them (ex: ST1) can be plugged (ST1's I2C uses A:115, not defined on XU8).
        from litex_boards.extensions.enclustra import EnclustraST1
        platform = _platform("enclustra_mercury_xu8_pe3")
        platform.add_extension(EnclustraST1(), prepend=True)
        for name, number in [("user_led", 0), ("hdmi", 0), ("sfp_tx", 0)]:
            platform.request(name, number)
        platform.constraint_manager.get_sig_constraints()

    def test_sipeed_sdram_modules(self):
        from litex_boards.platforms import sipeed_tang_primer_25k
        for helper in [sipeed_tang_primer_25k.misterSDRAM, sipeed_tang_primer_25k.sipeedSDRAM]:
            with self.subTest(helper=helper.__name__):
                platform = _platform("sipeed_tang_primer_25k")
                platform.add_extension(helper())
                platform.request("sdram")
                platform.constraint_manager.get_sig_constraints()

if __name__ == "__main__":
    unittest.main()
