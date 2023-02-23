#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019 Antti Lukats <antti.lukats@gmail.com>
# Copyright (c) 2019 msloniewski <marcin.sloniewski@gmail.com>
# Copyright (c) 2019 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import *

from litex_boards.platforms import trenz_c10lprefkit

from litex.soc.cores.clock import Cyclone10LPPLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litedram.modules import MT48LC16M16
from litedram.phy import GENSDRPHY

from liteeth.phy.mii import LiteEthPHYMII

from litex.soc.cores.hyperbus import HyperRAM

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst       = Signal()
        self.cd_sys    = ClockDomain()
        self.cd_sys_ps = ClockDomain()

        # # #

        # Clk / Rst
        clk12 = platform.request("clk12")

        # PLL
        self.pll = pll = Cyclone10LPPLL(speedgrade="-A7")
        self.comb += pll.reset.eq(~platform.request("cpu_reset") | self.rst)
        pll.register_clkin(clk12, 12e6)
        pll.create_clkout(self.cd_sys,    sys_clk_freq)
        pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=90)

        # SDRAM clock
        self.comb += platform.request("sdram_clock").eq(self.cd_sys_ps.clk)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    mem_map = {
        "hyperram": 0x20000000,
    }
    mem_map.update(SoCCore.mem_map)

    def __init__(self, sys_clk_freq=50e6,
        with_led_chaser = True,
        with_ethernet   = False,
        with_etherbone  = False,
        **kwargs):
        platform = trenz_c10lprefkit.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on C10 LP RefKit", **kwargs)

        # HyperRam ---------------------------------------------------------------------------------
        self.hyperram = HyperRAM(platform.request("hyperram"), sys_clk_freq=sys_clk_freq)
        self.bus.add_slave("hyperram", slave=self.hyperram.bus, region=SoCRegion(origin=0x20000000, size=8*1024*1024))

        # SDR SDRAM --------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.sdrphy = GENSDRPHY(platform.request("sdram"), sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.sdrphy,
                module        = MT48LC16M16(sys_clk_freq, "1:1"),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            self.ethphy = LiteEthPHYMII(
                clock_pads = self.platform.request("eth_clocks"),
                pads       = self.platform.request("eth"))
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy)
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=trenz_c10lprefkit.Platform, description="LiteX SoC on C10 LP RefKit.")
    parser.add_target_argument("--sys-clk-freq",   default=50e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-ethernet",  action="store_true",      help="Enable Ethernet support.")
    parser.add_target_argument("--with-etherbone", action="store_true",      help="Enable Etherbone support.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq   = args.sys_clk_freq,
        with_ethernet  = args.with_ethernet,
        with_etherbone = args.with_etherbone,
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
