#
# This file is part of LiteX-Boards.
#
# This file is Copyright (c) 2017-2021 Florent Kermarrec <florent@enjoy-digital.fr>
# This file is Copyright (c) 2019 Tim 'mithro' Ansell <me@mith.ro>
# SPDX-License-Identifier: BSD-2-Clause

import subprocess
import unittest
import importlib
import os
import shutil
import sys

from migen import *

from litex.soc.integration.builder import *

EXCLUSION_CATEGORIES = {
    "external_toolchain",
    "generic_target",
    "known_build_failure",
    "missing_default_clock",
    "not_real_platform",
    "untested",
}

PLATFORM_EXCLUSIONS = {
    "qmtech_daughterboard": {
        "category": "not_real_platform",
        "reason": "Not a real platform.",
    },
    "qmtech_rp2040_daughterboard": {
        "category": "not_real_platform",
        "reason": "Not a real platform.",
    },
    "enclustra_st1": {
        "category": "not_real_platform",
        "reason": "Not a real platform.",
    },
    "quicklogic_quickfeather": {
        "category": "missing_default_clock",
        "reason": "No default clock.",
    },
    "colognechip_gatemate_evb": {
        "category": "external_toolchain",
        "reason": "Toolchain not yet mainlined.",
    },
    "efinix_ti375_c529_dev_kit": {
        "category": "external_toolchain",
        "reason": "Require Efinity toolchain.",
    },
    "efinix_titanium_ti60_f225_dev_kit": {
        "category": "external_toolchain",
        "reason": "Require Efinity toolchain.",
    },
    "efinix_trion_t120_bga576_dev_kit": {
        "category": "external_toolchain",
        "reason": "Require Efinity toolchain.",
    },
    "efinix_trion_t20_bga256_dev_kit": {
        "category": "external_toolchain",
        "reason": "Require Efinity toolchain.",
    },
    "efinix_trion_t20_mipi_dev_kit": {
        "category": "external_toolchain",
        "reason": "Require Efinity toolchain.",
    },
    "efinix_tz170_j484_dev_kit": {
        "category": "external_toolchain",
        "reason": "Require Efinity toolchain.",
    },
    "efinix_xyloni_dev_kit": {
        "category": "external_toolchain",
        "reason": "Require Efinity toolchain.",
    },
    "sipeed_tang_primer": {
        "category": "external_toolchain",
        "reason": "Require Anlogic toolchain.",
    },
    "jungle_electronics_fireant": {
        "category": "external_toolchain",
        "reason": "Require Efinity toolchain.",
    },
    "efinix_t8f81_dev_kit": {
        "category": "external_toolchain",
        "reason": "Require Efinity toolchain.",
    },
    "adi_plutosdr": {
        "category": "missing_default_clock",
        "reason": "No default clock.",
    },
    "newae_cw305": {
        "category": "missing_default_clock",
        "reason": "No default clock.",
    },
    "sipeed_slogic16u3": {
        "category": "missing_default_clock",
        "reason": "No default clock.",
    },
    "modretro_chromatic": {
        "category": "untested",
        "reason": "Not yet tested.",
    },
}

TARGET_EXCLUSIONS = {
    "simple": {
        "category": "generic_target",
        "reason": "Generic target.",
    },
    "quicklogic_quickfeather": {
        "category": "missing_default_clock",
        "reason": "No default clock.",
    },
    "efinix_ti375_c529_dev_kit": {
        "category": "external_toolchain",
        "reason": "Require Efinity toolchain.",
    },
    "efinix_titanium_ti60_f225_dev_kit": {
        "category": "external_toolchain",
        "reason": "Require Efinity toolchain.",
    },
    "efinix_trion_t120_bga576_dev_kit": {
        "category": "external_toolchain",
        "reason": "Require Efinity toolchain.",
    },
    "efinix_trion_t20_bga256_dev_kit": {
        "category": "external_toolchain",
        "reason": "Require Efinity toolchain.",
    },
    "efinix_trion_t20_mipi_dev_kit": {
        "category": "external_toolchain",
        "reason": "Require Efinity toolchain.",
    },
    "efinix_tz170_j484_dev_kit": {
        "category": "external_toolchain",
        "reason": "Require Efinity toolchain.",
    },
    "efinix_xyloni_dev_kit": {
        "category": "external_toolchain",
        "reason": "Require Efinity toolchain.",
    },
    "jungle_electronics_fireant": {
        "category": "external_toolchain",
        "reason": "Require Efinity toolchain.",
    },
    "efinix_t8f81_dev_kit": {
        "category": "external_toolchain",
        "reason": "Require Efinity toolchain.",
    },
}


def python_module_names(directory):
    return sorted(
        file.replace(".py", "")
        for file in os.listdir(directory)
        if file.endswith(".py") and file != "__init__.py"
    )


def subprocess_run_quiet(cmd):
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)


def efinity_available():
    if os.getenv("LITEX_ENV_EFINITY"):
        return True
    return any(shutil.which(tool) for tool in ["efx_map", "efx_pnr", "efx_run.py"])


def efinity_target_names():
    return sorted(
        name for name, record in TARGET_EXCLUSIONS.items()
        if record["category"] == "external_toolchain" and "Efinity" in record["reason"]
    )


class TestTargets(unittest.TestCase):
    excluded_platforms = sorted(PLATFORM_EXCLUSIONS)
    excluded_targets   = sorted(TARGET_EXCLUSIONS)

    # Import and instantiate excluded platforms when no external toolchain discovery is required.
    def test_excluded_platforms_smoke(self):
        for name, record in PLATFORM_EXCLUSIONS.items():
            if record["category"] == "not_real_platform":
                continue
            if record["category"] == "external_toolchain" and "Efinity" in record["reason"] and not efinity_available():
                continue
            with self.subTest(platform=name):
                module = importlib.import_module(f"litex_boards.platforms.{name}")
                platform = getattr(module, "Platform")
                platform()

    # Build Efinix targets when Efinity is available on the runner.
    def test_efinity_targets(self):
        if not efinity_available():
            self.skipTest("Efinity toolchain not available.")

        for name in efinity_target_names():
            with self.subTest(target=name):
                output_dir = os.path.join("build", "test_efinity_targets", name)
                shutil.rmtree(output_dir, ignore_errors=True)
                cmd = [
                    sys.executable,
                    "-m", f"litex_boards.targets.{name}",
                    "--cpu-type=vexriscv",
                    "--cpu-variant=minimal",
                    "--uart-name=stub",
                    "--build",
                    "--no-compile",
                    "--output-dir", output_dir,
                ]
                subprocess.check_call(cmd)

    # Exercise target imports and parser setup for board targets, including no-compile exclusions.
    def test_target_parsers_smoke(self):
        targets = [name for name in python_module_names("./litex_boards/targets/") if name != "simple"]
        for name in targets:
            with self.subTest(target=name):
                cmd = [
                    sys.executable,
                    "-m", f"litex_boards.targets.{name}",
                    "--help",
                ]
                result = subprocess_run_quiet(cmd)
                if result.returncode != 0:
                    self.fail(result.stdout)

    # Build simple design for all platforms.
    def test_platforms(self):
        # Collect platforms.
        platforms = []
        for name in python_module_names("./litex_boards/platforms/"):
            if name not in self.excluded_platforms:
                platforms.append(name)

        # Test platforms with simple design.
        for name in platforms:
            with self.subTest(platform=name):
                shutil.rmtree("build", ignore_errors=True)
                cmd = [
                    sys.executable,
                    "-m", "litex_boards.targets.simple",
                    f"litex_boards.platforms.{name}",
                    "--build",
                    "--no-compile",
                    "--uart-name=stub",
                ]
                subprocess.check_call(cmd)

    # Build default configuration for all targets.
    def test_targets(self):
        # Collect targets.
        targets = []
        for name in python_module_names("./litex_boards/targets/"):
            if name not in self.excluded_targets:
                targets.append(name)

        # Test targets.
        for name in targets:
            with self.subTest(target=name):
                shutil.rmtree("build", ignore_errors=True)
                cmd = [
                    sys.executable,
                    "-m", f"litex_boards.targets.{name}",
                    "--cpu-type=vexriscv",
                    "--cpu-variant=minimal",
                    "--uart-name=stub",
                    "--build",
                    "--no-compile",
                ]
                subprocess.check_call(cmd)
