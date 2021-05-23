#
# This file is part of LiteX-Boards.
#
# This file is Copyright (c) 2017-2020 Florent Kermarrec <florent@enjoy-digital.fr>
# This file is Copyright (c) 2019 Tim 'mithro' Ansell <me@mith.ro>
# SPDX-License-Identifier: BSD-2-Clause

import subprocess
import unittest
import os

from migen import *

from litex.soc.integration.builder import *

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
        platforms.append("linsn_rv901t")
        platforms.append("minispartan6")
        platforms.append("pipistrello")
        platforms.append("sp605")
        platforms.append("pano_logic_g2")

        # Xilinx Spartan7
        platforms.append("arty_s7")

        # Xilinx Artix7
        platforms.append("ac701")
        platforms.append("aller")
        platforms.append("arty")
        platforms.append("basys3")
        platforms.append("mimas_a7")
        platforms.append("netv2")
        platforms.append("nexys4ddr")
        platforms.append("nexys_video")
        platforms.append("tagus")
        platforms.append("acorn")
        platforms.append("marblemini")
        platforms.append("qmtech_wukong")
        platforms.append("qmtech_xc7a35t")

        # Xilinx Kintex7
        platforms.append("genesys2")
        platforms.append("kc705")
        platforms.append("mercury_kx2")
        platforms.append("nereid")

        # Xilinx Virtex7
        platforms.append("vc707")

        # Xilinx Kintex Ultrascale
        platforms.append("kcu105")

        # Xilinx Zynq-7000
        platforms.append("zedboard")
        platforms.append("zybo_z7")

        # Xilinx Zynq Ultrascale+
        platforms.append("zcu104")
        platforms.append("mercury_xu5")

        # Xilinx Virtex Ultrascale+
        platforms.append("vcu118")

        # Intel Cyclone3
        platforms.append("mist")

        # Intel Cyclone4
        platforms.append("de0nano")
        platforms.append("de2_115")
        platforms.append("qmtech_ep4ce15")

        # Intel Cyclone5
        platforms.append("de1soc")
        platforms.append("de10nano")
        platforms.append("sockit")

        # Intel Cyclone10
        platforms.append("c10lprefkit")
        platforms.append("cyc1000")

        # Intel Max10
        platforms.append("de10lite")
        platforms.append("deca")

        # Lattice iCE40
        platforms.append("fomu_evt")
        platforms.append("fomu_hacker")
        platforms.append("fomu_pvt")
        platforms.append("tinyfpga_bx")
        platforms.append("icebreaker")
        platforms.append("icesugar")

        # Lattice MachXO2
        platforms.append("machxo3")

        # Lattice ECP5
        platforms.append("ecp5_evn")
        platforms.append("hadbadge")
        platforms.append("orangecrab")
        platforms.append("trellisboard")
        platforms.append("ulx3s")
        platforms.append("versa_ecp5")
        platforms.append("colorlight_5a_75b")
        platforms.append("colorlight_5a_75e")
        platforms.append("camlink_4k")

        # Lattice Crosslink NX
        platforms.append("crosslink_nx_evn")
        platforms.append("crosslink_nx_vip")

        # Gowin
        platforms.append("tec0117")

        # Microsemi PolarFire
        platforms.append("avalanche")

        # LPDDR4 Test Board
        platforms.append("lpddr4_test_board")

        for name in platforms:
            with self.subTest(platform=name):
                cmd = """\
litex_boards/targets/simple.py litex_boards.platforms.{} \
    --no-compile-software   \
    --no-compile-gateware   \
    --uart-name="stub"      \
""".format(name)
                subprocess.check_call(cmd, shell=True)
