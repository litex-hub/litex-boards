#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2024 Enjoy-Digital <enjoy-digital.fr>
#
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from litex_boards.platforms import lattice_certuspro_nx_vvml

from litex.build.io import CRG
from litex.build.generic_platform import *

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *

from litex.soc.cores.led import LedChaser

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()
        self.cd_por = ClockDomain()

        # # #

        # Clk / Rst
        self.clk24 = platform.request("clk24")
        self.rst_n = platform.request("gsrn")

        # Built in OSC
        self.hf_clk = NXOSCA(platform)
        hf_clk_freq = 25e6
        self.hf_clk.create_hf_clk(self.cd_por, hf_clk_freq)

        # Power on reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))
        self.specials += AsyncResetSynchronizer(self.cd_por, ~self.rst_n)

        # PLL
        self.sys_pll = sys_pll = NXPLL(platform=platform, create_output_port_clocks=True)
        self.comb += sys_pll.reset.eq(self.rst | ~por_done)
        sys_pll.register_clkin(self.clk24, 24e6)
        sys_pll.create_clkout(self.cd_sys, sys_clk_freq)
        self.specials += AsyncResetSynchronizer(self.cd_sys, ~self.sys_pll.locked)


# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=75e6, toolchain="radiant",
        with_led_chaser = True,
        **kwargs):
        platform = lattice_certuspro_nx_vvml.Platform(toolchain=toolchain)

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore -----------------------------------------_----------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on CertusPro-NX VVML Eval Board", **kwargs)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=lattice_certuspro_nx_vvml.Platform, description="LiteX SoC on CertusPro-NX VVML EVN Board.")
    parser.add_target_argument("--sys-clk-freq", default=75e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--flash",        action="store_true",      help="Flash bitstream to SPI Flash.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq = args.sys_clk_freq,
        **parser.soc_argdict
    )

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer(args.prog_target)
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer(args.prog_target)
        prog.load_bitstream(0, builder.get_bitstream_filename(mode="flash"))

if __name__ == "__main__":
    main()
