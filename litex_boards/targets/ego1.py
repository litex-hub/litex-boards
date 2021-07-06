#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Shinken Sanada <sanadashinken@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

import os
import argparse

from migen import *

from litex_boards.platforms import ego1
from litex.build.xilinx.vivado import vivado_build_args, vivado_build_argdict

from litex.soc.cores.clock import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litevideo.terminal.core import Terminal

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_sys       = ClockDomain()
        self.clock_domains.cd_vga       = ClockDomain(reset_less=True)

        self.submodules.pll = pll = S7PLL(speedgrade=-1)
        self.comb += pll.reset.eq(~platform.request("cpu_reset") | self.rst)
        pll.register_clkin(platform.request("clk100"), 100e6)
        pll.create_clkout(self.cd_sys,       sys_clk_freq)
        pll.create_clkout(self.cd_vga,       25e6)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(100e6), with_led_chaser=True, with_vga=False, **kwargs):
        platform = ego1.Platform()

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident          = "LiteX SoC on EGO1 Board",
            ident_version  = True,
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # VGA terminal -----------------------------------------------------------------------------
        if with_vga:
            self.submodules.terminal = terminal = Terminal()
            self.bus.add_slave("terminal", self.terminal.bus, region=SoCRegion(origin=0x30000000, size=0x10000))
            vga_pads = platform.request("vga")
            self.comb += [
                vga_pads.vsync.eq(terminal.vsync),
                vga_pads.hsync.eq(terminal.hsync),
                vga_pads.red.eq(terminal.red[4:8]),
                vga_pads.green.eq(terminal.green[4:8]),
                vga_pads.blue.eq(terminal.blue[4:8])
            ]

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)
            self.add_csr("leds")

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on EGO1")
    parser.add_argument("--build",           action="store_true", help="Build bitstream")
    parser.add_argument("--load",            action="store_true", help="Load bitstream")
    parser.add_argument("--flash",           action="store_true", help="Flash bitstream")
    parser.add_argument("--with-vga",        action="store_true", help="Enagle VGA Terminal")
    parser.add_argument("--sys-clk-freq",    default=100e6,       help="System clock frequency (default: 100MHz)")

    builder_args(parser)
    soc_core_args(parser)
    vivado_build_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq   = int(float(args.sys_clk_freq)),
        with_vga       = args.with_vga,
        **soc_core_argdict(args)
    )

    builder = Builder(soc, **builder_argdict(args))

    builder.build(**vivado_build_argdict(args), run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".bit"))

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".bin"))

if __name__ == "__main__":
    main()

