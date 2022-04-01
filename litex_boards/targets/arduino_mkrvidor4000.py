#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 John Simons <jammsimons@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

import os
import argparse

from migen import *

from litex_boards.platforms import arduino_mkrvidor4000

from litex.soc.cores.clock import Cyclone10LPPLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

from litedram.modules import AS4C4M16
from litedram.phy import GENSDRPHY, HalfRateGENSDRPHY

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_sys    = ClockDomain()
        self.clock_domains.cd_sys_ps = ClockDomain()

        # # #

        # Clk / Rst
        clk48 = platform.request("clk48")

        # PLL
        self.submodules.pll = pll = Cyclone10LPPLL(speedgrade="-C8")
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk48, 48e6)
        pll.create_clkout(self.cd_sys,    sys_clk_freq)
        pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=90)

        # SDRAM clock
        self.comb += platform.request("sdram_clock").eq(self.cd_sys_ps.clk)


# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(48e6), **kwargs):
        platform = arduino_mkrvidor4000.Platform()

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident = "LiteX SoC on MKR Vidor 4000",
            **kwargs)

        self.add_jtagbone() # TODO: untested

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # SDR SDRAM --------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.submodules.sdrphy = GENSDRPHY(platform.request("sdram"), sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.sdrphy,
                module        = AS4C4M16(sys_clk_freq, "1:1"), # Alliance Memory AS4C4M16
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on MKR Vidor 4000")
    parser.add_argument("--build",         action="store_true", help="Build bitstream.")
    parser.add_argument("--load",          action="store_true", help="Load bitstream.")
    parser.add_argument("--sys-clk-freq",  default=48e6,        help="System clock frequency.")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq  = int(float(args.sys_clk_freq)),
        **soc_core_argdict(args)
    )
    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".sof"))

if __name__ == "__main__":
    main()
