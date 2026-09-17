#
# This file is part of LiteX-Boards.
#
# SPDX-License-Identifier: BSD-2-Clause

"""Validate component/native DDR options before any Vivado device query."""
import unittest
import subprocess
import re
from unittest.mock import patch
from types import SimpleNamespace

from migen import Signal
from litedram.phy import usddrphy
from litex_boards.targets.opalkelly_xem8320 import (
    BaseSoC, _component_idelay_sim_device, _native_post_route_commands)


class TestXEM8320NativeOptions(unittest.TestCase):
    def setUp(self):
        # Elaborations are independent of an installed Vivado executable.
        self.idelay_selector = patch(
            "litex_boards.targets.opalkelly_xem8320._component_idelay_sim_device",
            return_value=("ULTRASCALE", None, None))
        self.idelay_selector.start()

    def tearDown(self):
        self.idelay_selector.stop()

    def test_component_idelay_uses_implementation_vivado_version(self):
        # Windows vivado.BAT returns 1 despite emitting this valid banner.
        completed = SimpleNamespace(returncode=1, stdout="vivado v2026.1 (64-bit)\n")
        with patch("litex_boards.targets.opalkelly_xem8320.shutil.which",
                   return_value="C:/Vivado/bin/vivado"), \
             patch("litex_boards.targets.opalkelly_xem8320.subprocess.run",
                   return_value=completed) as run:
            self.assertEqual(_component_idelay_sim_device(),
                ("ULTRASCALE_PLUS", "2026.1", "C:/Vivado/bin/vivado"))
        run.assert_called_once_with(["C:/Vivado/bin/vivado", "-version"],
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, text=True, timeout=15, check=False)

    def test_component_idelay_uses_portable_enum_before_2026(self):
        completed = SimpleNamespace(returncode=0, stdout="Vivado v2025.2 (64-bit)\n")
        with patch("litex_boards.targets.opalkelly_xem8320.shutil.which",
                   return_value="C:/Vivado/bin/vivado"), \
             patch("litex_boards.targets.opalkelly_xem8320.subprocess.run",
                   return_value=completed):
            self.assertEqual(_component_idelay_sim_device(),
                ("ULTRASCALE", "2025.2", "C:/Vivado/bin/vivado"))

    def test_component_idelay_falls_back_without_vivado(self):
        with patch("litex_boards.targets.opalkelly_xem8320.shutil.which", return_value=None):
            self.assertEqual(_component_idelay_sim_device(), ("ULTRASCALE", None, None))

    def test_component_dma_elaborates_with_software_admission(self):
        soc = BaseSoC(sys_clk_freq=125e6, with_dma=True, dma_data_width=128,
            with_led_chaser=False)
        self.assertTrue(hasattr(soc, "dma_bench"))
        self.assertTrue(hasattr(soc.dma_bench, "_software_ready"))
        self.assertIn("CONFIG_SDRAM_DMA_SOFTWARE_ADMISSION", soc.constants)
        self.assertFalse(soc.sdram.controller.settings.with_registered_row_hit)
        self.assertNotIn("CONFIG_SDRAM_USNATIVE_DMA_CALIBRATION", soc.constants)

    def test_component_stub_or_disabled_uart_needs_no_jtag_constraint(self):
        # CI elaborates targets with a stub UART; users can also omit it.
        for options in ({"uart_name": "stub"}, {"with_uart": False}):
            with self.subTest(options=options):
                soc = BaseSoC(with_led_chaser=False, **options)
                commands = "\n".join(command for command, _ in
                    soc.platform.constraint_manager.platform_commands)
                self.assertNotIn("jtag_tck", commands)

    def test_native_without_dma_elaborates_cpu_crossing(self):
        # Replace the query-dependent PHY with the component PHY's compatible
        # DFI interface. This elaborates the native CPU CDC branch without a
        # Vivado device query or generated native core.
        class USPDDRPHY(usddrphy.USPDDRPHY):
            def __init__(self, pads, platform, native_clock, native_locked,
                native_enable, *, sys_clk_freq, **kwargs):
                super().__init__(pads, memtype="DDR4", sys_clk_freq=sys_clk_freq,
                    cl=24 if sys_clk_freq > 333333334 else (19 if sys_clk_freq > 300e6 else None),
                    cwl=16 if sys_clk_freq > 333333334 else (14 if sys_clk_freq > 300e6 else None),
                    iodelay_clk_freq=500e6)
                self.software_control = Signal()
                self.overclock = False

        with patch("litedram.phy.usnative.USNativeDDRPHY", USPDDRPHY):
            soc = BaseSoC(sys_clk_freq=300e6, with_usnative=True,
                with_dma=False, with_led_chaser=False)
        self.assertTrue(hasattr(soc, "cpu_cdc0"))
        self.assertFalse(hasattr(soc, "dma_bench"))
        self.assertNotIn("CONFIG_SDRAM_USNATIVE_DMA_CALIBRATION", soc.constants)
        self.assertTrue(soc.sdram.controller.settings.with_registered_row_hit)
        self.assertFalse(soc.sdram.controller.settings.with_bank_group_interleaving)
        self.assertFalse(soc.sdram.controller.settings.with_registered_refresh_timers)

        with patch("litedram.phy.usnative.USNativeDDRPHY", USPDDRPHY):
            high_rate = BaseSoC(sys_clk_freq=400e6, with_usnative=True,
                overclock=True, with_dma=False, with_led_chaser=False)
        self.assertTrue(high_rate.sdram.controller.settings.with_registered_refresh_timers)
        self.assertFalse(high_rate.sdram.controller.settings.with_bank_group_interleaving)

        receiver_commands = []
        for debug in (False, True):
            with patch("litedram.phy.usnative.USNativeDDRPHY", USPDDRPHY):
                receiver_soc = BaseSoC(sys_clk_freq=1e9/3, with_usnative=True,
                    usnative_debug=debug, with_dma=False, with_led_chaser=False)
            commands = receiver_soc.platform.toolchain.bitstream_commands
            receiver_commands.append([c for c in commands if "EQUALIZATION" in c])
            self.assertNotIn("PDRC-182", "\n".join(commands))
        self.assertEqual(receiver_commands[0], receiver_commands[1])
        self.assertEqual(len(receiver_commands[0]), 1)

    def test_native_dma_calibration_supports_converted_and_paired_dma(self):
        # Use the component PHY's compatible DFI interface to elaborate the
        # native DMA/configuration path without a Vivado device query.
        class USPDDRPHY(usddrphy.USPDDRPHY):
            def __init__(self, pads, platform, native_clock, native_locked,
                native_enable, *, sys_clk_freq, **kwargs):
                super().__init__(pads, memtype="DDR4", sys_clk_freq=sys_clk_freq,
                    cl=24 if sys_clk_freq > 333333334 else None,
                    cwl=16 if sys_clk_freq > 333333334 else None,
                    iodelay_clk_freq=500e6)
                self.software_control = Signal()
                self.overclock = False
                self._ready = SimpleNamespace(status=Signal())
                self._training_stage = SimpleNamespace(storage=Signal(3))
                self._training_error = SimpleNamespace(storage=Signal())
                self._bisc_only = SimpleNamespace(storage=Signal())
                self._en_vtc = SimpleNamespace(storage=Signal())

        with patch("litedram.phy.usnative.USNativeDDRPHY", USPDDRPHY):
            soc = BaseSoC(sys_clk_freq=300e6, with_usnative=True,
                with_dma=True, dma_data_width=256,
                with_dma_bank_group_interleaving=True,
                with_led_chaser=False)
            converted = BaseSoC(sys_clk_freq=300e6, with_usnative=True,
                with_dma=True, dma_data_width=256,
                with_led_chaser=False)
            explicit = BaseSoC(sys_clk_freq=300e6, with_usnative=True,
                with_dma=True, dma_data_width=256,
                usnative_dma_calibration=True, with_led_chaser=False)
        self.assertIn("CONFIG_SDRAM_USNATIVE_DMA_CALIBRATION", explicit.constants)
        self.assertIn("CONFIG_SDRAM_USNATIVE_DMA_CALIBRATION", converted.constants)
        self.assertFalse(converted.sdram.controller.settings.with_bank_group_interleaving)
        self.assertNotIn("CONFIG_SDRAM_USNATIVE_DEBUG", converted.constants)
        self.assertIn("CONFIG_SDRAM_USNATIVE_DMA_CALIBRATION", soc.constants)
        self.assertNotIn("CONFIG_SDRAM_USNATIVE_DEBUG", soc.constants)
        self.assertIn("CONFIG_SDRAM_DMA_SOFTWARE_ADMISSION", soc.constants)
        # Simulate the production admission expression independently of PLLs
        # and vendor primitives. PHY readiness cannot substitute for memtest.
        from migen import Module, run_simulation
        from migen.fhdl.structure import _Assign
        admission = Module()
        admission.comb += [statement for statement in soc._fragment.comb
            if isinstance(statement, _Assign) and statement.l is soc.dma_bench.allowed]
        self.assertEqual(len(admission._fragment.comb), 1)

        def exercise():
            yield soc.ddrphy._ready.status.eq(1)
            yield soc.ddrphy._training_stage.storage.eq(5)
            yield soc.ddrphy._en_vtc.storage.eq(1)
            yield soc.sdram.dfii._control.fields.sel.eq(1)
            yield
            self.assertEqual((yield soc.dma_bench.allowed), 0)
            yield soc.dma_bench._software_ready.storage.eq(1)
            yield
            self.assertEqual((yield soc.dma_bench.allowed), 1)
            for blocked in (soc.ddrphy._bisc_only.storage,
                            soc.ddrphy._training_error.storage,
                            soc.dma_paired_write.error):
                yield blocked.eq(1)
                yield
                self.assertEqual((yield soc.dma_bench.allowed), 0)
                yield blocked.eq(0)
            yield soc.ddrphy._training_stage.storage.eq(2)
            yield
            self.assertEqual((yield soc.dma_bench.allowed), 0)
        run_simulation(admission, exercise())

    def test_3200_only_downgrades_the_known_pll_drc(self):
        for frequency in (300e6, 1e9/3, 1100e6/3):
            with self.subTest(frequency=frequency):
                self.assertNotIn("PDRC-182", "\n".join(_native_post_route_commands(frequency)))

        commands = _native_post_route_commands(400e6)
        self.assertEqual(commands[0], "set_property SEVERITY Warning [get_drc_checks PDRC-182]")
        self.assertEqual(commands[-1], "report_drc -file opalkelly_xem8320_native_final_drc.rpt")

    def test_dq_equalization_is_profile_specific(self):
        for frequency in (300e6,):
            self.assertNotIn("EQUALIZATION", "\n".join(_native_post_route_commands(frequency)))
        for frequency in (1e9/3, 1100e6/3, 400e6):
            commands = _native_post_route_commands(frequency)
            equalization = [command for command in commands if "EQUALIZATION" in command]
            self.assertEqual(len(equalization), 1)
            self.assertIn("EQ_LEVEL3", equalization[0])
            emitted = equalization[0].format(build_name="opalkelly_xem8320")
            expression = re.search(r"-regexp \{(.+)\}", emitted).group(1)
            ports = ["ddram_dq[{}]".format(i) for i in range(16)]
            ports += ["ddram_dqs_p[0]", "ddram_dqs_n[0]", "ddram_dm_n[0]", "ddram_clk_p"]
            self.assertEqual([p for p in ports if re.search(expression, p)], ports[:16])

    def test_default_target_keeps_125mhz_component_mode(self):
        # Avoid constructing the component PHY here: this checks the target's
        # defaults without requiring Vivado or an external DDR build.
        soc = BaseSoC(integrated_main_ram_size=4096, with_led_chaser=False)
        self.assertEqual(soc.clk_freq, 125e6)
        self.assertNotIn("SDRAM_USNATIVE_XEM8320", soc.constants)

    def test_invalid_options_do_not_query_vivado(self):
        cases = [
            dict(toolchain='yosys+nextpnr'),
            dict(sys_clk_freq=125e6),
            dict(sys_clk_freq=400e6),
            dict(sys_clk_freq=1100e6/3),
            dict(dma_data_width=256),
            dict(with_dma=True, dma_data_width=64),
            dict(with_dma=True, with_dma_bank_group_interleaving=True),
            dict(with_dma=True, dma_data_width=128, with_dma_bank_group_interleaving=True),
            dict(dma_data_width=256, with_dma_bank_group_interleaving=True),
            dict(with_video_framebuffer=True),
            dict(integrated_main_ram_size=4096),
            dict(cpu_type='serv'),
            dict(cpu_variant='minimal'),
            dict(uart_name='crossover'),
            dict(usnative_dma_calibration=True),
            dict(with_dma=True, dma_data_width=128,
                 with_dma_bank_group_interleaving=True, usnative_dma_calibration=True),
        ]
        with patch('litedram.phy.usnative.ddrphy.query_device') as query:
            for options in cases:
                with self.subTest(options=options), self.assertRaises(ValueError):
                    BaseSoC(**dict(dict(with_usnative=True, sys_clk_freq=300e6), **options))
            query.assert_not_called()

    def test_native_only_flags_require_native_phy(self):
        for options in (dict(usnative_debug=True), dict(usnative_dma_calibration=True)):
            with self.subTest(options=options), self.assertRaises(ValueError):
                BaseSoC(**options)

    def test_component_dma_validation_does_not_query_vivado(self):
        cases = [
            dict(dma_data_width=256),
            dict(with_dma_bank_group_interleaving=True),
            dict(with_dma=True, with_dma_bank_group_interleaving=True),
        ]
        with patch('litedram.phy.usnative.ddrphy.query_device') as query:
            for options in cases:
                with self.subTest(options=options), self.assertRaises(ValueError):
                    BaseSoC(**options)
            query.assert_not_called()

    def test_component_2000_requires_explicit_overclock(self):
        with self.assertRaises(ValueError):
            BaseSoC(sys_clk_freq=250e6)

    def test_component_debug_preserves_non_native_selection(self):
        soc = BaseSoC(integrated_main_ram_size=4096, with_led_chaser=False,
            sdram_debug=True)
        self.assertNotIn("SDRAM_USNATIVE_XEM8320", soc.constants)
