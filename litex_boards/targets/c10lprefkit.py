#!/usr/bin/env python3

# This file is Copyright (c) 2019 Antti Lukats <antti.lukats@gmail.com>
# This file is Copyright (c) 2019 msloniewski <marcin.sloniewski@gmail.com>
# This file is Copyright (c) 2019 Florent Kermarrec <florent@enjoy-digital.fr>
# License: BSD

import argparse

from migen import *

from litex_boards.platforms import c10lprefkit

from litex.soc.cores.clock import Cyclone10LPPLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc_sdram import *
from litex.soc.integration.builder import *

from litedram.modules import MT48LC16M16
from litedram.phy import GENSDRPHY

from liteeth.phy.mii import LiteEthPHYMII

from litex.soc.cores.hyperbus import HyperRAM

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.clock_domains.cd_sys    = ClockDomain()
        self.clock_domains.cd_sys_ps = ClockDomain(reset_less=True)

        # # #

        # Clk / Rst
        clk12 = platform.request("clk12")
        platform.add_period_constraint(clk12, 1e9/12e6)

        # PLL
        self.submodules.pll = pll = Cyclone10LPPLL(speedgrade="-A7")
        self.comb += pll.reset.eq(~platform.request("cpu_reset"))
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

    def __init__(self, sys_clk_freq=int(50e6), with_ethernet=False, **kwargs):
        platform = c10lprefkit.Platform()

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, clk_freq=sys_clk_freq, **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # HyperRam ---------------------------------------------------------------------------------
        self.submodules.hyperram = HyperRAM(platform.request("hyperram"))
        self.add_wb_slave(self.mem_map["hyperram"], self.hyperram.bus)
        self.add_memory_region("hyperram", self.mem_map["hyperram"], 8*1024*1024)

        # SDR SDRAM --------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.submodules.sdrphy = GENSDRPHY(platform.request("sdram"))
            self.add_sdram("sdram",
                phy                     = self.sdrphy,
                module                  = MT48LC16M16(sys_clk_freq, "1:1"),
                origin                  = self.mem_map["main_ram"],
                size                    = kwargs.get("max_sdram_size", 0x40000000),
                l2_cache_size           = kwargs.get("l2_size", 8192),
                l2_cache_min_data_width = kwargs.get("min_l2_data_width", 128),
                l2_cache_reverse        = True
            )

        # Ethernet ---------------------------------------------------------------------------------
        if with_ethernet:
            self.submodules.ethphy = LiteEthPHYMII(
                clock_pads = self.platform.request("eth_clocks"),
                pads       = self.platform.request("eth"))
            self.add_csr("ethphy")
            self.add_ethernet(phy=self.ethphy)

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on C10 LP RefKit")
    builder_args(parser)
    soc_sdram_args(parser)
    parser.add_argument("--with-ethernet", action="store_true",
                        help="enable Ethernet support")
    args = parser.parse_args()

    soc = BaseSoC(with_ethernet=args.with_ethernet, **soc_sdram_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder.build()


if __name__ == "__main__":
    main()
