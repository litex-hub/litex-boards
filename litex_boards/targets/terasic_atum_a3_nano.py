#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 Gwenhael Goavec-merou<gwenhael.goavec-merou@trabucayre.com>
#
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import *

from litex.build.io import DDROutput

from litex_boards.platforms import terasic_atum_a3_nano

from litex.soc.integration.soc      import *
from litex.soc.integration.soc      import *
from litex.soc.integration.builder  import *

from litex.soc.cores.bitbang import I2CMaster
from litex.soc.cores.clock   import Agilex3PLL
from litex.soc.cores.led     import LedChaser
from litex.soc.cores.video   import VideoDVIPHY

from litedram.modules import IS42VM32160G
from litedram.phy     import GENSDRPHY, HalfRateGENSDRPHY

from liteeth.phy import LiteEthAgilexPHYRGMII

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, sdram_rate="1:1", with_hdmi=False, with_eth=False):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()
        if sdram_rate == "1:2":
            self.cd_sys2x    = ClockDomain()
            self.cd_sys2x_ps = ClockDomain()
        else:
            self.cd_sys_ps = ClockDomain()

        if with_eth:
            self.cd_eth = ClockDomain()

        if with_hdmi:
            self.cd_init = ClockDomain()

        # # #

        # Clk / Rst
        clk50 = platform.request("clk50_1")
        rst_n = platform.request("user_btn", 0)

        # Power on reset
        ninit_done = Signal()
        self.specials += Instance("altera_agilex_config_reset_release_endpoint", o_conf_reset = ninit_done)

        # PLL
        self.pll = pll = Agilex3PLL(platform, speedgrade="-7S")
        self.comb += pll.reset.eq(ninit_done | ~rst_n)
        pll.register_clkin(clk50, 50e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)

        # Ethernet
        if with_eth:
            pll.create_clkout(self.cd_eth, 125e6, with_reset=False)

        # HDMI
        if with_hdmi:
            pll.create_clkout(self.cd_init, 50e6) # Yes: for 800x600@75Hz 49.5e6 but can't find valid configuration

        # SDRAM clock
        if sdram_rate == "1:2":
            pll.create_clkout(self.cd_sys2x,    2*sys_clk_freq)
            pll.create_clkout(self.cd_sys2x_ps, 2*sys_clk_freq, phase=90)
        else:
            pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=90)
        sdram_clk = ClockSignal("sys2x_ps" if sdram_rate == "1:2" else "sys_ps")
        self.specials += DDROutput(1, 0, platform.request("sdram_clock"), sdram_clk)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=50e6,
        sdram_rate             = "1:1",
        with_video_colorbars   = False,
        with_video_terminal    = False,
        with_video_framebuffer = False,
        with_ethernet          = False,
        with_etherbone         = False,
        eth_ip                 = "192.168.1.50",
        remote_ip              = None,
        eth_dynamic_ip         = False,
        with_led_chaser        = True,
        **kwargs):
        platform = terasic_atum_a3_nano.Platform()

        with_hdmi = with_video_colorbars or with_video_terminal or with_video_framebuffer
        with_eth  = with_ethernet or with_etherbone

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, sdram_rate=sdram_rate, with_hdmi=with_hdmi, with_eth=with_eth)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Terasic Atum A3-NANO", **kwargs)

        # HDMI -------------------------------------------------------------------------------------
        if with_hdmi:
            # PHY + TFP410 I2C initialization.
            hdmi_pads     = platform.request("hdmi")
            self.videophy = VideoDVIPHY(hdmi_pads, clock_domain="init")
            self.videoi2c = I2CMaster(hdmi_pads)
            REG_CTL_1_MODE = 0x08
            CTL1_VAL       = 0xbf
            REG_CTL_2_MODE = 0x09
            CTL2_VAL       = 0x01

            self.videoi2c.add_init(addr=0x3C, init=[
                (REG_CTL_1_MODE, CTL1_VAL),
                (REG_CTL_2_MODE, CTL2_VAL),
            ])

            self.comb += [
                hdmi_pads.isel.eq(1),
                hdmi_pads.pdn.eq(1),
            ]

            if with_video_colorbars:
                self.add_video_colorbars(phy=self.videophy,   timings="800x600@75Hz", clock_domain="init")
            elif with_video_terminal:
                self.add_video_terminal(phy=self.videophy,    timings="800x600@75Hz", clock_domain="init")
            elif with_video_framebuffer:
                self.add_video_framebuffer(phy=self.videophy, timings="800x600@75Hz", clock_domain="init")

        # SDR SDRAM --------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            sdrphy_cls = HalfRateGENSDRPHY if sdram_rate == "1:2" else GENSDRPHY
            self.sdrphy = sdrphy_cls(platform.request("sdram"), sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.sdrphy,
                module        = IS42VM32160G(sys_clk_freq, sdram_rate),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_eth:
            self.ethphy = LiteEthAgilexPHYRGMII(
                platform       = platform,
                clock_pads     = platform.request("eth_clocks"),
                pads           = platform.request("eth"),
                ref_tx_clk     = ClockSignal("eth"),
                with_phy_reset = False,
            )

            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, ip_address=eth_ip, with_ethmac=with_ethernet)
            elif with_ethernet:
                self.add_ethernet(phy=self.ethphy, dynamic_ip=eth_dynamic_ip, local_ip=eth_ip, remote_ip=remote_ip)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=terasic_atum_a3_nano.Platform, description="LiteX SoC on Terasic Atum A3-NANO.")
    parser.add_target_argument("--sys-clk-freq", default=50e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--sdram-rate",   default="1:1",            help="SDRAM Rate (1:1 Full Rate or 1:2 Half Rate).")

    # HDMI.
    viopts = parser.target_group.add_mutually_exclusive_group()
    viopts.add_argument("--with-video-colorbars",   action="store_true", help="Enable Video Colorbars (DVI).")
    viopts.add_argument("--with-video-terminal",    action="store_true", help="Enable Video Terminal (HDMI).")
    viopts.add_argument("--with-video-framebuffer", action="store_true", help="Enable Video Framebuffer (HDMI).")

    # SDCard.
    sdopts = parser.target_group.add_mutually_exclusive_group()
    sdopts.add_argument("--with-sdcard",     action="store_true", help="Enable SDCard support.")
    sdopts.add_argument("--with-spi-sdcard", action="store_true", help="Enable SPI-mode SDCard support.")

    # Ethernet.
    parser.add_target_argument("--with-ethernet",  action="store_true",     help="Enable Ethernet support.")
    parser.add_target_argument("--with-etherbone", action="store_true",     help="Enable Etherbone support.")
    parser.add_target_argument("--eth-ip",         default="192.168.1.50",  help="Ethernet/Etherbone IP address.")
    parser.add_target_argument("--remote-ip",      default="192.168.1.100", help="Remote IP address of TFTP server.")
    parser.add_target_argument("--eth-dynamic-ip", action="store_true",     help="Enable dynamic Ethernet IP assignment.")

    # Overrides defaults synth/conv tools.
    parser.set_defaults(synth_tool="quartus_syn")
    parser.set_defaults(conv_tool="quartus_pfg")

    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq           = args.sys_clk_freq,
        sdram_rate             = args.sdram_rate,
        with_video_colorbars   = args.with_video_colorbars,
        with_video_terminal    = args.with_video_terminal,
        with_video_framebuffer = args.with_video_framebuffer,
        with_ethernet          = args.with_ethernet,
        with_etherbone         = args.with_etherbone,
        eth_ip                 = args.eth_ip,
        remote_ip              = args.remote_ip,
        eth_dynamic_ip         = args.eth_dynamic_ip,
        **parser.soc_argdict
    )

    if args.with_sdcard:
        soc.add_sdcard()

    if args.with_spi_sdcard:
        soc.add_spi_sdcard()

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram", ext=".rbf"))

if __name__ == "__main__":
    main()
