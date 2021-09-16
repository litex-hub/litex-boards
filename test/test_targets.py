#
# This file is part of LiteX-Boards.
#
# This file is Copyright (c) 2017-2021 Florent Kermarrec <florent@enjoy-digital.fr>
# This file is Copyright (c) 2019 Tim 'mithro' Ansell <me@mith.ro>
# SPDX-License-Identifier: BSD-2-Clause

import subprocess
import unittest
import os

from migen import *

from litex.soc.integration.builder import *

class TestTargets(unittest.TestCase):
    # Build simple design for all platforms.
    def test_platforms(self):
        # Collect platforms.
        platforms = []
        for file in os.listdir("./litex_boards/platforms/"):
            if file.endswith(".py"):
                file = file.replace(".py", "")
                if file not in ["__init__", "qmtech_daughterboard"]:
                    platforms.append(file)

        # Test platforms with simple design.
        for name in platforms:
            with self.subTest(platform=name):
                os.system("rm -rf build")
                cmd = """\
python3 -m litex_boards.targets.simple litex_boards.platforms.{} \
    --no-compile-software   \
    --no-compile-gateware   \
    --uart-name="stub"      \
""".format(name)
                subprocess.check_call(cmd, shell=True)

    # Build default configuration for all targets.
    def test_targets(self):
        # Collect targets.
        targets = []
        for file in os.listdir("./litex_boards/targets/"):
            if file.endswith(".py"):
                file = file.replace(".py", "")
                if file not in ["__init__", "simple"]:
                    targets.append(file)

        # Test targets.
        for name in targets:
            with self.subTest(target=name):
                os.system("rm -rf build")
                cmd = """\
python3 -m litex_boards.targets.{} \
    --no-compile-software   \
    --no-compile-gateware   \
""".format(name)
                subprocess.check_call(cmd, shell=True)
