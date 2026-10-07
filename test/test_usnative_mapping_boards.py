#
# This file is part of LiteX-Boards.
#
# SPDX-License-Identifier: BSD-2-Clause

"""Actual board geometry with synthetic logical ABI resources, not device qualification."""

import unittest
import importlib

from types import SimpleNamespace

from litedram.phy.usnative.mapping import NativeMapping
from litedram.phy.usnative.pins import extract_ddr_pins


BOARDS = (
    "adi_adrv2crr_fmc", "alibaba_vu13p", "aliexpress_rk_xcku5p", "alinx_axau15",
    "avnet_aesku40", "enclustra_mercury_xu5", "enclustra_mercury_xu8_pe3",
    "mlk_cu07_ku15p", "opalkelly_xem8320", "sqrl_xcu1525", "xilinx_kcu105",
    "xilinx_kcu116", "xilinx_vcu118", "xilinx_vcu128", "xilinx_zcu102",
    "xilinx_zcu104", "xilinx_zcu106",
)


class TestUSNativeBoardMapping(unittest.TestCase):
    pass


def geometry_test(board, rate):
    def check(self):
        platform = importlib.import_module("litex_boards.platforms." + board).Platform()
        pads = platform.request("ddram", 0)
        pins = extract_ddr_pins(platform, pads)
        width = len(pads.dq)
        lanes = len(pads.dqs_p)
        self.assertEqual(width, 8*lanes)
        self.assertIn(pins.family, ("ULTRASCALE", "ULTRASCALE_PLUS"))
        # Invented compact resources exercise descriptor geometry only. Actual
        # slice placement and RIU ownership still require a local Vivado query.
        layout = SimpleNamespace(
            slices=tuple(("data", None) for _ in range(10*lanes)) + (("clk_p", None),),
            controls=tuple(range(lanes)),
            lanes=tuple(SimpleNamespace(index=i, dq=tuple(range(10*i, 10*i+8)),
                strobe=10*i+8, mask=10*i+9, controls=(i,)) for i in range(lanes)),
            riu_bytes=tuple((i, i, None) for i in range(lanes)))
        mapping = NativeMapping(layout, profile=dict(family=pins.family, rate_mt_s=rate))
        self.assertEqual(len(mapping.dq_taps), width)
        self.assertEqual(mapping.lane_count, lanes)
        self.assertEqual(mapping.major, 1)
        changed = NativeMapping(layout, profile=dict(family=pins.family, rate_mt_s=rate+1))
        self.assertNotEqual(mapping.config_id, changed.config_id)
        self.assertNotIn(platform.device, str(mapping.logical_descriptor()))
    return check


for board in BOARDS:
    for rate in (2400, 2666.667):
        setattr(TestUSNativeBoardMapping, "test_" + board + "_" + str(rate).replace(".", "p"),
                geometry_test(board, rate))
