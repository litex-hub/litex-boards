#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019-2020 Florent Kermarrec <florent@enjoy-digital.fr>,
# Copyright (c) 2021 Derek Mulcahy <derekmulcahy@gmail.com>,
# SPDX-License-Identifier: BSD-2-Clause

import os
import argparse

from migen import *

from litex_boards.platforms import snickerdoodle
from litex.build.xilinx.vivado import vivado_build_args, vivado_build_argdict

from litex.soc.interconnect import axi
from litex.soc.interconnect import wishbone

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq, use_ps7_clk=True):
        self.rst = Signal()
        self.clock_domains.cd_sys = ClockDomain()

        # # #

        if use_ps7_clk:
            assert sys_clk_freq == 100e6
            self.comb += ClockSignal("sys").eq(ClockSignal("ps7"))
            self.comb += ResetSignal("sys").eq(ResetSignal("ps7") | self.rst)
        else:
            raise NotImplementedError

# BaseSoC ------------------------------------------------------------------------------------------

def load_ps7(soc, xci_file):
    odir = os.path.join("build", "snickerdoodle", "gateware", "xci")
    os.makedirs(odir, exist_ok=True)
    file = "snickerdoodle_ps7.xci"
    dst = os.path.join(odir, file)
    if xci_file is None:
        src = "https://technicaltoys-support.s3.amazonaws.com/xci/" + file
        os.system("wget " + src + " -O " + dst)
    else:
        os.system("cp -p  " + xci_file + " " + dst)
    soc.cpu.set_ps7_xci(dst)

def blinky(soc, platform):
    from litex.build.generic_platform import Pins, IOStandard
    platform.add_extension([("blinky_led", 0, Pins("ja1:3"), IOStandard("LVCMOS33"))])
    led = platform.request("blinky_led")
    soc.submodules.blinky = blinky = Module()
    counter = Signal(27)
    blinky.comb += led.eq(counter[counter.nbits-1])
    blinky.sync += counter.eq(counter + 1)

class BaseSoC(SoCCore):

    def __init__(self, sys_clk_freq=int(100e6),
        with_blinky = False,
        blinky_led = "ja1:3",
        xci_file = None,
        **kwargs):

        platform = snickerdoodle.Platform()

        kwargs["with_uart"] = False
        kwargs["cpu_type"] = "zynq7000"

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident          = "Snickerdoodle",
            ident_version  = True,
            **kwargs)

        # Zynq7000 Integration ---------------------------------------------------------------------
        if kwargs.get("cpu_type", None) == "zynq7000":
            load_ps7(self, xci_file)

            # Connect AXI GP0 to the SoC with base address of 0x43c00000 (default one)
            wb_gp0  = wishbone.Interface()
            self.submodules += axi.AXI2Wishbone(
                axi          = self.cpu.add_axi_gp_master(),
                wishbone     = wb_gp0,
                base_address = 0x43c00000)
            self.add_wb_master(wb_gp0)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        platform.add_platform_command("set_property BITSTREAM.GENERAL.COMPRESS True [current_design]")

        if with_blinky:
            blinky(self, platform)

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on Snickerdoodle")
    parser.add_argument("--build",       action="store_true", help="Build bitstream")
    parser.add_argument("--load",        action="store_true", help="Load bitstream")
    parser.add_argument("--with-blinky", action="store_true", help="Enable Blinky")
    parser.add_argument("--blinky-led",  default="ja1:3", help="Blinky LED")
    parser.add_argument("--xci-file",    help="XCI for PS7 configuration")
    parser.add_argument("--target",      help="Programmer target")
    builder_args(parser)
    soc_core_args(parser)
    vivado_build_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        with_blinky = args.with_blinky,
        blinky_led = args.blinky_led,
        xci_file = args.xci_file,
        **soc_core_argdict(args)
    )
    builder = Builder(soc, **builder_argdict(args))
    builder.build(**vivado_build_argdict(args), run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        bitstream = os.path.join(builder.gateware_dir, soc.build_name + ".bit")
        prog.load_bitstream(bitstream, target=args.target, device=1)

if __name__ == "__main__":
    main()
