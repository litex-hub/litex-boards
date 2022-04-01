#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Paul Sajna <sajattack@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.build.io import DDROutput

from litex_boards.platforms import de10nano

from litex.soc.cores.clock import CycloneVPLL
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.video import VideoVGAPHY
from litex.soc.cores.led import LedChaser

from litedram.modules import AS4C32M16
from litedram.phy import GENSDRPHY, HalfRateGENSDRPHY

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq, with_sdram=False, sdram_rate="1:1"):
        self.rst = Signal()
        self.clock_domains.cd_sys    = ClockDomain()
        if sdram_rate == "1:2":
            self.clock_domains.cd_sys2x    = ClockDomain()
            self.clock_domains.cd_sys2x_ps = ClockDomain()
        else:
            self.clock_domains.cd_sys_ps = ClockDomain()
        self.clock_domains.cd_vga    = ClockDomain()

        # # #

        # Clk / Rst
        clk50 = platform.request("clk50")

        # PLL
        self.submodules.pll = pll = CycloneVPLL(speedgrade="-I7")
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk50, 50e6)
        pll.create_clkout(self.cd_sys,    sys_clk_freq)
        if sdram_rate == "1:2":
            pll.create_clkout(self.cd_sys2x,    2*sys_clk_freq)
            pll.create_clkout(self.cd_sys2x_ps, 2*sys_clk_freq, phase=90)
        else:
            pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_vga, 40e6)

        # SDRAM clock
        if with_sdram:
            sdram_clk = ClockSignal("sys2x_ps" if sdram_rate == "1:2" else "sys_ps")
            self.specials += DDROutput(1, 0, platform.request("sdram_clock"), sdram_clk)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(50e6), with_led_chaser=True, with_mister_sdram=True,
                 with_mister_video_terminal=False, sdram_rate="1:1", **kwargs):
        platform = de10nano.Platform()

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident = "LiteX SoC on DE10-Nano",
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq, with_sdram=with_mister_sdram, sdram_rate=sdram_rate)

        # SDR SDRAM --------------------------------------------------------------------------------
        if with_mister_sdram and not self.integrated_main_ram_size:
            sdrphy_cls = HalfRateGENSDRPHY if sdram_rate == "1:2" else GENSDRPHY
            self.submodules.sdrphy = sdrphy_cls(platform.request("sdram"), sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.sdrphy,
                module        = AS4C32M16(sys_clk_freq, sdram_rate),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Video Terminal ---------------------------------------------------------------------------
        if with_mister_video_terminal:
            self.submodules.videophy = VideoVGAPHY(platform.request("vga"), clock_domain="vga")
            self.add_video_terminal(phy=self.videophy, timings="800x600@60Hz", clock_domain="vga")

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on DE10-Nano")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",                      action="store_true", help="Build bitstream.")
    target_group.add_argument("--load",                       action="store_true", help="Load bitstream.")
    target_group.add_argument("--sys-clk-freq",               default=50e6,        help="System clock frequency.")
    target_group.add_argument("--with-mister-sdram",          action="store_true", help="Enable SDRAM with MiSTer expansion board.")
    target_group.add_argument("--with-mister-video-terminal", action="store_true", help="Enable Video Terminal with Mister expansion board.")
    target_group.add_argument("--sdram-rate",                 default="1:1",       help="SDRAM Rate (1:1 Full Rate or 1:2 Half Rate).")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq               = int(float(args.sys_clk_freq)),
        with_mister_sdram          = args.with_mister_sdram,
        with_mister_video_terminal = args.with_mister_video_terminal,
        sdram_rate                 = args.sdram_rate,
        **soc_core_argdict(args)
    )
    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
