#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Nathaniel Lewis <github@nrlewis.dev>
# Copyright (c) 2023 Hans Baier <hansfbaier@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause
from migen import *

from litex.gen import *

from litex.build.io import DDROutput
from litex_boards.platforms import aliexpress_xc7k70t

from litex.soc.interconnect.csr import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

from litex.soc.cores.clock import *
from litex.soc.cores.video import VideoS7HDMIPHY
from litex.soc.cores.led import LedChaser

from litedram.modules import W9812G6JB, SDRModule
from litedram.phy import GENSDRPHY, HalfRateGENSDRPHY

# CRG ----------------------------------------------------------------------------------------------

class CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, sdram_rate="1:1"):
        self.rst       = Signal()
        self.cd_sys    = ClockDomain()
        self.cd_hdmi   = ClockDomain()
        self.cd_hdmi5x = ClockDomain()
        if sdram_rate == "1:2":
            self.cd_sys2x    = ClockDomain()
            self.cd_sys2x_ps = ClockDomain()
        else:
            self.cd_sys_ps = ClockDomain()

        # Clk/Rst
        clk50 = platform.request("clk50")

        # PLL
        self.pll = pll = S7PLL()
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk50, 50e6)
        pll.create_clkout(self.cd_sys,    sys_clk_freq)
        pll.create_clkout(self.cd_hdmi,   25e6,  margin=0)
        pll.create_clkout(self.cd_hdmi5x, 125e6, margin=0)
        if sdram_rate == "1:2":
            pll.create_clkout(self.cd_sys2x,    2*sys_clk_freq)
            pll.create_clkout(self.cd_sys2x_ps, 2*sys_clk_freq, phase=90)
        else:
            pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=90)

# BaseSoC -----------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=100e6, sdram_rate="1:1",
        with_hdmi              = False,
        with_ethernet          = False,
        with_pcie              = False,
        with_sdram             = True,
        with_led_chaser        = True,
        with_video_terminal    = False,
        with_video_framebuffer = False,
        with_video_colorbars   = False,
        **kwargs):
        platform = aliexpress_xc7k70t.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = CRG(platform, sys_clk_freq, sdram_rate)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Alchitry Mojo", **kwargs)

        # Add SDRAM if a shield with RAM has been added
        if not self.integrated_main_ram_size:
            sdram_clk = ClockSignal("sys2x_ps" if sdram_rate == "1:2" else "sys_ps")
            self.crg.specials += DDROutput(1, 0, platform.request("sdram_clock"), sdram_clk)

            sdrphy_cls = HalfRateGENSDRPHY if sdram_rate == "1:2" else GENSDRPHY
            self.sdrphy = sdrphy_cls(platform.request("sdram"), sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.sdrphy,
                module        = W9812G6JB(sys_clk_freq, sdram_rate),
                l2_cache_size = kwargs.get("l2_size", 1 * KILOBYTE)
            )
        
        # HDMI Options -----------------------------------------------------------------------------
        if with_hdmi and (with_video_colorbars or with_video_framebuffer or with_video_terminal):
            self.videophy = VideoS7HDMIPHY(platform.request("hdmi_out"), clock_domain="hdmi")
            if with_video_colorbars:
                self.add_video_colorbars(phy=self.videophy, timings="640x480@60Hz", clock_domain="hdmi")
            if with_video_terminal:
                self.add_video_terminal(phy=self.videophy, timings="640x480@60Hz", clock_domain="hdmi")
            if with_video_framebuffer:
                self.add_video_framebuffer(phy=self.videophy, timings="640x480@60Hz", clock_domain="hdmi")

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet:
            self.ethphy = LiteEthPHYRGMII(
                clock_pads = self.platform.request("eth_clocks", 0),
                pads       = self.platform.request("eth", 0),
                tx_delay = 1.417e-9,
                rx_delay = 1.417e-9,
            )
            self.add_ethernet(phy=self.ethphy)

        # PCIe -------------------------------------------------------------------------------------
        if with_pcie:
            self.pcie_phy = S7PCIEPHY(platform, platform.request("pcie_x4"),
                data_width = 128,
                bar0_size  = 0x20000)
            self.add_pcie(phy=self.pcie_phy, ndmas=1)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=aliexpress_xc7k70t.Platform, description="LiteX SoC on AliExpress XC7K70T PCIe board.")
    parser.add_target_argument("--sys-clk-freq",    default=90e6, type=float,  help="System clock frequency.")
    parser.add_target_argument("--sdram-rate",      default="1:1",             help="SDRAM Rate: (1:1 Full Rate or 1:2 Half Rate).")
    parser.add_argument("--with-ethernet",          action="store_true",       help="Enable ethernet")
    parser.add_argument("--with-pcie",              action="store_true",       help="Enable PCIe")
    parser.add_argument("--with-hdmi",              action="store_true",       help="Enable HDMI")
    viopts = parser.target_group.add_mutually_exclusive_group()
    viopts.add_argument("--with-video-terminal",    action="store_true",       help="Enable Video Terminal (HDMI).")
    viopts.add_argument("--with-video-framebuffer", action="store_true",       help="Enable Video Framebuffer (HDMI).")
    viopts.add_argument("--with-video-colorbars",   action="store_true",       help="Enable Video Colorbars (HDMI).")
    args = parser.parse_args()

    # Note: baudrate is fixed because regardless of USB->TTL baud, the AVR <-> FPGA baudrate is
    #       set to a fixed rate of 500 kilobaud.
    soc = BaseSoC(
        sys_clk_freq           = args.sys_clk_freq,
        sdram_rate             = args.sdram_rate,
        with_ethernet          = args.with_ethernet,
        with_pcie              = args.with_pcie,
        with_hdmi              = args.with_hdmi,
        with_video_terminal    = args.with_video_terminal,
        with_video_framebuffer = args.with_video_framebuffer,
        with_video_colorbars   = args.with_video_colorbars,
        **parser.soc_argdict
    )

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

if __name__ == "__main__":
    main()
