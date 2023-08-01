#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019 Arnaud Durand <arnaud.durand@unifr.ch>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from litex_boards.platforms import lattice_ecp5_evn

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, x5_clk_freq):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()

        # # #

        # Clk / Rst.
        clk = clk12 = platform.request("clk12")
        rst_n = platform.request("rst_n")
        if x5_clk_freq is not None:
            clk = clk50 = platform.request("ext_clk50")
            self.comb += platform.request("ext_clk50_en").eq(1)
            platform.add_period_constraint(clk50, 1e9/x5_clk_freq)

        # PLL.
        self.pll = pll = ECP5PLL()
        self.comb += pll.reset.eq(~rst_n | self.rst)
        pll.register_clkin(clk, x5_clk_freq or 12e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=50e6, toolchain="trellis", x5_clk_freq=None,
        with_led_chaser = True,
        with_jtagbone   = True,
        **kwargs):
        platform = lattice_ecp5_evn.Platform(toolchain=toolchain)

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, x5_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on ECP5 Evaluation Board", **kwargs)

        # JtagBone ---------------------------------------------------------------------------------
        if with_jtagbone:
            self.add_jtagbone()

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=lattice_ecp5_evn.Platform, description="LiteX SoC on ECP5 Evaluation Board.")
    parser.add_target_argument("--sys-clk-freq", default=60e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--x5-clk-freq",  type=int,                 help="Use X5 oscillator as system clock at the specified frequency.")
    parser.add_target_argument("--with-jtagbone", action="store_true",     help="Add JTAGBone.")
    args = parser.parse_args()

    soc = BaseSoC(
        toolchain    = args.toolchain,
        sys_clk_freq = args.sys_clk_freq,
        x5_clk_freq  = args.x5_clk_freq,
        with_jtagbone = args.with_jtagbone,
        **parser.soc_argdict)
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram", ext=".svf")) # FIXME

if __name__ == "__main__":
    main()
