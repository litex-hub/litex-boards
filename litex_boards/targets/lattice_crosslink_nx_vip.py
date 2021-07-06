#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 David Corrigan <davidcorrigan714@gmail.com>
# Copyright (c) 2020 Alan Green <avg@google.com>
# Copyright (c) 2020 David Shah <dave@ds0.me>
#
# SPDX-License-Identifier: BSD-2-Clause

import os
import argparse

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex_boards.platforms import crosslink_nx_vip

from litex_boards.platforms import crosslink_nx_vip

from litehyperbus.core.hyperbus import HyperRAM

from litex.soc.cores.ram import NXLRAM
from litex.soc.cores.spi_flash import SpiFlash
from litex.build.io import CRG
from litex.build.generic_platform import *

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litex.build.lattice.oxide import oxide_args, oxide_argdict

kB = 1024
mB = 1024*kB


# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_sys = ClockDomain()
        self.clock_domains.cd_por = ClockDomain()

        # TODO: replace with PLL
        # Clocking
        self.submodules.sys_clk = sys_osc = NXOSCA()
        sys_osc.create_hf_clk(self.cd_sys, sys_clk_freq)
        platform.add_period_constraint(self.cd_sys.clk, 1e9/sys_clk_freq)
        rst_n = platform.request("gsrn")

        # Power On Reset
        por_cycles  = 4096
        por_counter = Signal(log2_int(por_cycles), reset=por_cycles-1)
        self.comb += self.cd_por.clk.eq(self.cd_sys.clk)
        self.sync.por += If(por_counter != 0, por_counter.eq(por_counter - 1))
        self.specials += AsyncResetSynchronizer(self.cd_por, ~rst_n)
        self.specials += AsyncResetSynchronizer(self.cd_sys, (por_counter != 0) | self.rst)


# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    mem_map = {
        "rom":  0x00000000,
        "sram": 0x40000000,
        "csr":  0xf0000000,
    }
    def __init__(self, sys_clk_freq=int(75e6), hyperram="none", toolchain="radiant",
                 with_led_chaser=True, **kwargs):
        platform = crosslink_nx_vip.Platform(toolchain=toolchain)
        platform.add_platform_command("ldc_set_sysconfig {{MASTER_SPI_PORT=SERIAL}}")

        # Disable Integrated SRAM since we want to instantiate LRAM specifically for it
        kwargs["integrated_sram_size"] = 0

        # SoCCore -----------------------------------------_----------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident          = "LiteX SoC on Crosslink-NX VIP Input Board",
            ident_version  = True,
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        if hyperram == "none":
            # 128KB LRAM (used as SRAM) ------------------------------------------------------------
            size = 128*kB
            self.submodules.spram = NXLRAM(32, size)
            self.register_mem("sram", self.mem_map["sram"], self.spram.bus, size)
        else:
            # Use HyperRAM generic PHY as SRAM -----------------------------------------------------
            size = 8*1024*kB
            hr_pads = platform.request("hyperram", int(hyperram))
            self.submodules.hyperram = HyperRAM(hr_pads)
            self.register_mem("sram", self.mem_map["sram"], self.hyperram.bus, size)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = Cat(*[platform.request("user_led", i) for i in range(4)]),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on Crosslink-NX VIP Board")
    parser.add_argument("--build",         action="store_true", help="Build bitstream")
    parser.add_argument("--load",          action="store_true", help="Load bitstream")
    parser.add_argument("--toolchain",     default="radiant",   help="FPGA toolchain: radiant (default) or prjoxide")
    parser.add_argument("--sys-clk-freq",  default=75e6,        help="System clock frequency (default: 75MHz)")
    parser.add_argument("--with-hyperram", default="none",      help="Enable use of HyperRAM chip: none (default), 0 or 1")
    parser.add_argument("--prog-target",   default="direct",    help="Programming Target: direct (default) or flash")
    builder_args(parser)
    soc_core_args(parser)
    oxide_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq = int(float(args.sys_clk_freq)),
        hyperram     = args.with_hyperram,
        toolchain    = args.toolchain,
        **soc_core_argdict(args)
    )
    builder = Builder(soc, **builder_argdict(args))
    builder_kargs = oxide_argdict(args) if args.toolchain == "oxide" else {}
    builder.build(**builder_kargs, run=args.build)

    if args.load:
        prog = soc.platform.create_programmer(args.prog_target)
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".bit"))

if __name__ == "__main__":
    main()
