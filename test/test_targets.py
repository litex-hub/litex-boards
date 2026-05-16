#
# This file is part of LiteX-Boards.
#
# This file is Copyright (c) 2017-2021 Florent Kermarrec <florent@enjoy-digital.fr>
# This file is Copyright (c) 2019 Tim 'mithro' Ansell <me@mith.ro>
# SPDX-License-Identifier: BSD-2-Clause

import subprocess
import unittest
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
}


class TestTargets(unittest.TestCase):
    excluded_platforms = sorted(PLATFORM_EXCLUSIONS)
    excluded_targets   = sorted(TARGET_EXCLUSIONS)

    # Build simple design for all platforms.
    def test_platforms(self):
        # Collect platforms.
        platforms = []
        for file in os.listdir("./litex_boards/platforms/"):
            if file.endswith(".py"):
                file = file.replace(".py", "")
                if file not in ["__init__"] + self.excluded_platforms:
                    platforms.append(file)

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
        for file in os.listdir("./litex_boards/targets/"):
            if file.endswith(".py"):
                file = file.replace(".py", "")
                if file not in ["__init__"] + self.excluded_targets:
                    targets.append(file)

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
