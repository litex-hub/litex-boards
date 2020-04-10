#!/usr/bin/env python3

# This file is Copyright (c) 2019 msloniewski <marcin.sloniewski@gmail.com>
# License: BSD

import argparse

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.build.io import DDROutput

from litex_boards.platforms import de10lite

from litex.soc.cores.clock import Max10PLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc_sdram import *
from litex.soc.integration.builder import *

from litedram.modules import IS42S16320
from litedram.phy import GENSDRPHY

from litevideo.terminal.core import Terminal

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.clock_domains.cd_sys    = ClockDomain()
        self.clock_domains.cd_sys_ps = ClockDomain(reset_less=True)
        self.clock_domains.cd_vga    = ClockDomain(reset_less=True)

        # # #

        # Clk / Rst
        clk50 = platform.request("clk50")
        platform.add_period_constraint(clk50, 1e9/50e6)

        # PLL
        self.submodules.pll = pll = Max10PLL(speedgrade="-7")
        pll.register_clkin(clk50, 50e6)
        pll.create_clkout(self.cd_sys,    sys_clk_freq)
        pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_vga,    25e6)

        # SDRAM clock
        self.specials += DDROutput(1, 0, platform.request("sdram_clock"), ClockSignal("sys_ps"))

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(50e6), **kwargs):
        platform = de10lite.Platform()

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, clk_freq=sys_clk_freq, **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # SDR SDRAM --------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.submodules.sdrphy = GENSDRPHY(platform.request("sdram"))
            self.add_sdram("sdram",
                phy                     = self.sdrphy,
                module                  = IS42S16320(sys_clk_freq, "1:1"),
                origin                  = self.mem_map["main_ram"],
                size                    = kwargs.get("max_sdram_size", 0x40000000),
                l2_cache_size           = kwargs.get("l2_size", 8192),
                l2_cache_min_data_width = kwargs.get("min_l2_data_width", 128),
                l2_cache_reverse        = True
            )

# VGASoC -------------------------------------------------------------------------------------------

class VGASoC(BaseSoC):
    mem_map = {
        "terminal": 0x30000000,
    }
    mem_map.update(BaseSoC.mem_map)

    def __init__(self, **kwargs):
        BaseSoC.__init__(self, **kwargs)

        # create VGA terminal
        self.submodules.terminal = terminal = Terminal()
        self.add_wb_slave(self.mem_map["terminal"], self.terminal.bus)
        self.add_memory_region("terminal", self.mem_map["terminal"], 0x10000)

        # connect VGA pins
        vga = self.platform.request('vga_out', 0)
        self.comb += [
            vga.vsync_n.eq(terminal.vsync),
            vga.hsync_n.eq(terminal.hsync),
            vga.r.eq(terminal.red[4:8]),
            vga.g.eq(terminal.green[4:8]),
            vga.b.eq(terminal.blue[4:8])
        ]

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on DE10 Lite")
    builder_args(parser)
    soc_sdram_args(parser)
    parser.add_argument("--with-vga", action="store_true", help="enable VGA support")
    args = parser.parse_args()

    cls = VGASoC if args.with_vga else BaseSoC
    soc = cls(**soc_sdram_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder.build()


if __name__ == "__main__":
    main()
