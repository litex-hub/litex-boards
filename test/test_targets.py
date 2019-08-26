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
        platforms += [("official",  "minispartan6")]
        platforms += [("community", "sp605")]

        # Xilinx Artix7
        platforms += [("official",  "arty")]
        platforms += [("official",  "nexys4ddr")]
        platforms += [("official",  "nexys_video")]
        platforms += [("partner",   "netv2")]
        platforms += [("community", "ac701")]

        # Xilinx Kintex7
        platforms += [("official",  "kc705")]
        platforms += [("official",  "genesys2")]

        # Xilinx Kintex Ultrascale
        platforms += [("official",  "kcu105")]

        # Intel Cyclone4
        platforms += [("official",  "de0nano")]
        platforms += [("community", "de2_115")]

        # Intel Cyclone5
        platforms += [("community", "de1soc")]

        # Intel Max10
        platforms += [("community", "de10lite")]

        # Lattice iCE40
        platforms += [("partner",   "tinyfpga_bx")]
        platforms += [("partner",   "fomu_evt")]
        platforms += [("partner",   "fomu_hacker")]
        platforms += [("partner",   "fomu_pvt")]

        # Lattice MachXO2
        platforms += [("official",  "machxo3")]

        # Lattice ECP3
        platforms += [("official",  "versa_ecp3")]

        # Lattice ECP5
        platforms += [("official",  "versa_ecp5")]
        platforms += [("partner",   "ulx3s")]
        platforms += [("partner",   "trellisboard")]
        platforms += [("community", "ecp5_evn")]

        # Microsemi PolarFire
        platforms += [("official",  "avalanche")]

        for s, p in platforms:
            with self.subTest(platform=p):
                cmd = """\
litex_boards/official/targets/simple.py litex_boards.{s}.platforms.{p} \
    --cpu-type=vexriscv     \
    --no-compile-software   \
    --no-compile-gateware   \
    --uart-stub=True        \
""".format(s=s, p=p)
                subprocess.check_call(cmd, shell=True)
