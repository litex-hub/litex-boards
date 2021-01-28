#!/usr/bin/env python3
#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Hans Baier <hansfbaier@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

import os
import argparse

from migen.fhdl.module      import Module
from migen.fhdl.structure   import Signal, ClockDomain
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.soc.cores.clock           import CycloneVPLL
from litex.soc.integration.builder   import Builder, builder_args, builder_argdict
from litex.soc.integration.soc_core  import SoCCore
from litex.soc.integration.soc_sdram import soc_sdram_argdict, soc_sdram_args
from litex.soc.cores.led             import LedChaser

from litex_boards.platforms import arrow_sockit

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_sys    = ClockDomain()
        self.clock_domains.cd_sys_ps = ClockDomain(reset_less=True)

        # Clk / Rst
        clk50 = platform.request("clk50")

        # PLL
        self.submodules.pll = pll = CycloneVPLL(speedgrade="-C6")
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk50, 50e6)
        pll.create_clkout(self.cd_sys,    sys_clk_freq)
        pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=90)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(50e6), revision="revd", **kwargs):
        platform = arrow_sockit.Platform(revision)

        # Defaults to Crossover UART because serial is attached to the HPS and cannot be used.
        if kwargs["uart_name"] == "serial":
            kwargs["uart_name"] = "crossover"

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident          = "LiteX SoC on the Arrow SoCKit",
            ident_version  = True,
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # Leds -------------------------------------------------------------------------------------
        self.submodules.leds = LedChaser(
            pads         = platform.request_all("user_led"),
            sys_clk_freq = sys_clk_freq)
        self.add_csr("leds")


# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on SoCKit")
    parser.add_argument("--build",        action="store_true", help="Build bitstream")
    parser.add_argument("--load",         action="store_true", help="Load bitstream")
    parser.add_argument("--revision",     default="revd",      help="Board revision: revb (default), revc or revd")
    parser.add_argument("--sys-clk-freq", default=50e6,        help="System clock frequency (default: 50MHz)")
    builder_args(parser)
    soc_sdram_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq = int(float(args.sys_clk_freq)),
        revision     = args.revision,
        **soc_sdram_argdict(args)
    )
    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".sof"))

if __name__ == "__main__":
    main()
