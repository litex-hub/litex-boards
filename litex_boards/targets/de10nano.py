#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Paul Sajna <sajattack@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

import os
import argparse

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.build.io import DDROutput

from litex_boards.platforms import de10nano

from litex.soc.cores.clock import CycloneVPLL
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc_sdram import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litedram.modules import AS4C32M16
from litedram.phy import GENSDRPHY, HalfRateGENSDRPHY

from litevideo.terminal.core import Terminal

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq, with_sdram=False, sdram_rate="1:1"):
        self.clock_domains.cd_sys    = ClockDomain()
        if sdram_rate == "1:2":
            self.clock_domains.cd_sys2x    = ClockDomain()
            self.clock_domains.cd_sys2x_ps = ClockDomain(reset_less=True)
        else:
            self.clock_domains.cd_sys_ps = ClockDomain(reset_less=True)
        self.clock_domains.cd_vga    = ClockDomain(reset_less=True)

        # # #

        # Clk / Rst
        clk50 = platform.request("clk50")

        # PLL
        self.submodules.pll = pll = CycloneVPLL(speedgrade="-I7")
        pll.register_clkin(clk50, 50e6)
        pll.create_clkout(self.cd_sys,    sys_clk_freq)
        if sdram_rate == "1:2":
            pll.create_clkout(self.cd_sys2x,    2*sys_clk_freq)
            pll.create_clkout(self.cd_sys2x_ps, 2*sys_clk_freq, phase=90)
        else:
            pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_vga,    25e6)

        # SDRAM clock
        if with_sdram:
            sdram_clk = ClockSignal("sys2x_ps" if sdram_rate == "1:2" else "sys_ps")
            self.specials += DDROutput(1, 0, platform.request("sdram_clock"), sdram_clk)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(50e6), with_mister_sdram=True, with_mister_vga=False, sdram_rate="1:1", **kwargs):
        platform = de10nano.Platform()

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident          = "LiteX SoC on DE10-Nano",
            ident_version  = True,
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq, with_sdram=with_mister_sdram, sdram_rate=sdram_rate)

        # SDR SDRAM --------------------------------------------------------------------------------
        if with_mister_sdram and not self.integrated_main_ram_size:
            sdrphy_cls = HalfRateGENSDRPHY if sdram_rate == "1:2" else GENSDRPHY
            self.submodules.sdrphy = sdrphy_cls(platform.request("sdram"))
            self.add_sdram("sdram",
                phy                     = self.sdrphy,
                module                  = AS4C32M16(sys_clk_freq, sdram_rate),
                origin                  = self.mem_map["main_ram"],
                size                    = kwargs.get("max_sdram_size", 0x40000000),
                l2_cache_size           = kwargs.get("l2_size", 8192),
                l2_cache_min_data_width = kwargs.get("min_l2_data_width", 128),
                l2_cache_reverse        = True
            )

        # VGA terminal -----------------------------------------------------------------------------
        if with_mister_vga:
            self.submodules.terminal = terminal = Terminal()
            self.bus.add_slave("terminal", self.terminal.bus, region=SoCRegion(origin=0x30000000, size=0x10000))
            vga_pads = platform.request("vga")
            self.comb += [
                vga_pads.vsync.eq(terminal.vsync),
                vga_pads.hsync.eq(terminal.hsync),
                vga_pads.red.eq(terminal.red[2:8]),
                vga_pads.green.eq(terminal.green[2:8]),
                vga_pads.blue.eq(terminal.blue[2:8])
            ]

        # Leds -------------------------------------------------------------------------------------
        self.submodules.leds = LedChaser(
            pads         = platform.request_all("user_led"),
            sys_clk_freq = sys_clk_freq)
        self.add_csr("leds")

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on DE10-Nano")
    parser.add_argument("--build", action="store_true", help="Build bitstream")
    parser.add_argument("--load",  action="store_true", help="Load bitstream")
    builder_args(parser)
    soc_sdram_args(parser)
    parser.add_argument("--with-mister-sdram", action="store_true", help="Enable SDRAM with MiSTer expansion board")
    parser.add_argument("--with-mister-vga",   action="store_true", help="Enable VGA with Mister expansion board")
    parser.add_argument("--sdram-rate",  default="1:1", help="SDRAM Rate 1:1 Full Rate (default), 1:2 Half Rate")
    args = parser.parse_args()
    soc = BaseSoC(
        with_mister_sdram = args.with_mister_sdram,
        with_mister_vga   = args.with_mister_vga,
        sdram_rate        = args.sdram_rate,
        **soc_sdram_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".sof"))

if __name__ == "__main__":
    main()
