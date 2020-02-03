# This file is Copyright (c) 2017-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# This file is Copyright (c) 2019 Tim 'mithro' Ansell <me@mith.ro>
# License: BSD

import subprocess
import unittest
import os

from migen import *

from litex.soc.integration.builder import *


RUNNING_ON_TRAVIS = (os.getenv('TRAVIS', 'false').lower() == 'true')


def build_test(socs):
    errors = 0
    for soc in socs:
        os.system("rm -rf build")
        builder = Builder(soc, output_dir="./build", compile_software=False, compile_gateware=False)
        builder.build()
        errors += not os.path.isfile("./build/gateware/top.v")
    os.system("rm -rf build")
    return errors


class TestTargets(unittest.TestCase):
    # Build simple design for all platforms
    def test_simple(self):
        platforms = []

        # Xilinx Spartan6
        platforms.append("minispartan6")
        platforms.append("sp605")

        # Xilinx Artix7
        platforms.append("arty")
        platforms.append("nexys4ddr")
        platforms.append("nexys_video")
        platforms.append("netv2")
        platforms.append("ac701")

        # Xilinx Kintex7
        platforms.append("kc705")
        platforms.append("genesys2")
        platforms.append("kx2")

        # Xilinx Kintex Ultrascale
        platforms.append("kcu105")

        # Intel Cyclone4
        platforms.append("de0nano")
        platforms.append("de2_115")

        # Intel Cyclone5
        platforms.append("de1soc")

        # Intel Max10
        platforms.append("de10lite")

        # Lattice iCE40
        platforms.append("tinyfpga_bx")
        platforms.append("fomu_evt")
        platforms.append("fomu_hacker")
        platforms.append("fomu_pvt")

        # Lattice MachXO2
        platforms.append("machxo3")

        # Lattice ECP3
        platforms.append("versa_ecp3")

        # Lattice ECP5
        platforms.append("versa_ecp5")
        platforms.append("ulx3s")
        platforms.append("trellisboard")
        platforms.append("ecp5_evn")

        # Microsemi PolarFire
        platforms.append("avalanche")

        for name in platforms:
            with self.subTest(platform=name):
                cmd = """\
litex_boards/targets/simple.py litex_boards.platforms.{} \
    --no-compile-software   \
    --no-compile-gateware   \
    --uart-name="stub"      \
""".format(name)
                subprocess.check_call(cmd, shell=True)
