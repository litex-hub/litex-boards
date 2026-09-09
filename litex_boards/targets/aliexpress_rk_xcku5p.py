#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 Aria Węgrzyn <git@ariac.at>
# SPDX-License-Identifier: BSD-2-Clause

# Documentation and photos of the board can be found here:
# https://github.com/tommythorn/rk-xcku5p-f-v1.2/

import os

from migen import *

from litex.gen import *

from litex_boards.platforms import aliexpress_rk_xcku5p

from litex.soc.integration.soc_core import *
from litex.soc.integration.builder  import *

from litex.soc.cores.clock import *
from litex.soc.cores.led   import LedChaser

from litedram.modules import MT40A512M16
from litedram.phy import usddrphy

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()
        self.cd_eth = ClockDomain()
        # DDR4
        self.cd_sys4x  = ClockDomain()
        self.cd_pll4x  = ClockDomain()
        self.cd_idelay = ClockDomain()

        # Clk.
        clk200 = platform.request("clk200")

        # PLL.
        self.pll = pll = USPMMCM(speedgrade=-2)
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk200, 200e6)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        # DDR4
        pll.create_clkout(self.cd_pll4x, sys_clk_freq*4, buf=None, with_reset=False)
        pll.create_clkout(self.cd_idelay, 500e6)

        self.specials += [
            Instance("BUFGCE_DIV",
                p_BUFGCE_DIVIDE=4,
                i_CE=1, i_I=self.cd_pll4x.clk, o_O=self.cd_sys.clk),
            Instance("BUFGCE",
                i_CE=1, i_I=self.cd_pll4x.clk, o_O=self.cd_sys4x.clk),
        ]

        self.idelayctrl = USIDELAYCTRL(cd_ref=self.cd_idelay, cd_sys=self.cd_sys)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=200e6,
        with_led_chaser = True,
        **kwargs):
        platform = aliexpress_rk_xcku5p.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on RK-XCKU5P Board", **kwargs)
        
        # DDR4 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.ddrphy = usddrphy.USPDDRPHY(
                pads             = platform.request("ddram"),
                memtype          = "DDR4",
                sys_clk_freq     = sys_clk_freq,
                iodelay_clk_freq = 500e6)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT40A512M16(sys_clk_freq, "1:4"),
                # there is 0x80000000 of main ram but we don't want to take all of the upper address space
                # for default configurations. All targets use smaller sizes.
                size          = 0x40000000,
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # LEDs -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=aliexpress_rk_xcku5p.Platform, description="LiteX SoC on RK-XCKU5P board.")
    parser.add_target_argument("--sys-clk-freq",        default=100e6, type=float, help="System clock frequency.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq   = args.sys_clk_freq,
        **parser.soc_argdict
    )

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
