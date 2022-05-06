#!/usr/bin/env python3
#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Hans Baier <hansfbaier@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from litex_boards.platforms import terasic_sockit

from litex.soc.cores.clock import CycloneVPLL
from litex.soc.integration.soc_core  import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.video import VideoVGAPHY

from litex.build.io import DDROutput

from litedram.modules import W9825G6KH6, AS4C32M16
from litedram.phy import HalfRateGENSDRPHY, GENSDRPHY

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq, with_sdram=False, sdram_rate="1:2", with_video_terminal=False):
        self.sdram_rate = sdram_rate
        self.rst = Signal()
        self.clock_domains.cd_sys = ClockDomain()
        if with_video_terminal:
            self.clock_domains.cd_vga = ClockDomain()
        if with_sdram:
            if sdram_rate == "1:2":
                self.clock_domains.cd_sys2x    = ClockDomain()
                self.clock_domains.cd_sys2x_ps = ClockDomain()
            else:
                self.clock_domains.cd_sys_ps = ClockDomain()

        # Clk / Rst
        clk50 = platform.request("clk50")

        # PLL
        self.submodules.pll = pll = CycloneVPLL(speedgrade="-C6")
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk50, 50e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)

        if with_video_terminal:
            pll.create_clkout(self.cd_vga, 65e6)

        if with_sdram:
            if sdram_rate == "1:2":
                pll.create_clkout(self.cd_sys2x,    2*sys_clk_freq)
                pll.create_clkout(self.cd_sys2x_ps, 2*sys_clk_freq, phase=180)  # Idealy 90° but needs to be increased.
            else:
                pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=90)

        # SDRAM clock
        if with_sdram:
            sdram_clk = ClockSignal("sys2x_ps" if sdram_rate == "1:2" else "sys_ps")
            self.specials += DDROutput(1, 0, platform.request("sdram_clock"), sdram_clk)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(50e6), revision="revd", sdram_rate="1:2", mister_sdram=None,
                 with_led_chaser=True, with_video_terminal=False, **kwargs):
        platform = terasic_sockit.Platform(revision)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq,
            with_sdram          = mister_sdram != None,
            sdram_rate          = sdram_rate,
            with_video_terminal = with_video_terminal
        )

        # SoCCore ----------------------------------------------------------------------------------
        if kwargs.get("uart_name", "serial") == "serial":
            kwargs["uart_name"] = "jtag_uart" # Defaults to JTAG-UART.
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on the Terasic SoCKit", **kwargs)

        # SDR SDRAM --------------------------------------------------------------------------------
        if mister_sdram is not None:
            sdrphy_cls = HalfRateGENSDRPHY if sdram_rate == "1:2" else GENSDRPHY
            sdrphy_mod = {"xs_v22": W9825G6KH6, "xs_v24": AS4C32M16}[mister_sdram]
            self.submodules.sdrphy = sdrphy_cls(platform.request("sdram"), sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.sdrphy,
                module        = sdrphy_mod(sys_clk_freq, sdram_rate),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Video Terminal ---------------------------------------------------------------------------
        if with_video_terminal:
            vga_pads = platform.request("vga")
            self.comb += [ vga_pads.sync_n.eq(0), vga_pads.blank_n.eq(1) ]
            self.specials += DDROutput(i1=1, i2=0, o=vga_pads.clk, clk=ClockSignal("vga"))
            self.submodules.videophy = VideoVGAPHY(vga_pads, clock_domain="vga")
            self.add_video_terminal(phy=self.videophy, timings="1024x768@60Hz", clock_domain="vga")

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on the Terasic SoCKit")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--single-rate-sdram",   action="store_true", help="Clock SDRAM with 1x the sytem clock (instead of 2x).")
    target_group.add_argument("--mister-sdram-xs-v22", action="store_true", help="Use optional MiSTer SDRAM module XS v2.2 on J2 on GPIO daughter card.")
    target_group.add_argument("--mister-sdram-xs-v24", action="store_true", help="Use optional MiSTer SDRAM module XS v2.4 on J2 on GPIO daughter card.")
    target_group.add_argument("--build",               action="store_true", help="Build design.")
    target_group.add_argument("--load",                action="store_true", help="Load bitstream.")
    target_group.add_argument("--revision",            default="revd",      help="Board revision (revb, revc or revd).")
    target_group.add_argument("--sys-clk-freq",        default=50e6,        help="System clock frequency.")
    target_group.add_argument("--with-video-terminal", action="store_true", help="Enable Video Terminal (VGA).")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq        = int(float(args.sys_clk_freq)),
        revision            = args.revision,
        sdram_rate          = "1:1" if args.single_rate_sdram else "1:2",
        mister_sdram        = "xs_v22" if args.mister_sdram_xs_v22 else "xs_v24" if args.mister_sdram_xs_v24 else None,
        with_video_terminal = args.with_video_terminal,
        **soc_core_argdict(args)
    )
    builder = Builder(soc, **builder_argdict(args))
    if args.build:
        builder.build()

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
