#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019 David Shah <dave@ds0.me>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex_boards.platforms import trellisboard

from litex.build.lattice.trellis import trellis_args, trellis_argdict

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.gpio import GPIOTristate
from litex.soc.cores.video import VideoDVIPHY
from litex.soc.cores.bitbang import I2CMaster

from litedram.modules import MT41J256M16
from litedram.phy import ECP5DDRPHY

from liteeth.phy.ecp5rgmii import LiteEthPHYRGMII

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_por = ClockDomain()
        self.clock_domains.cd_sys = ClockDomain()

        # # #

        # Clk / Rst
        clk12 = platform.request("clk12")
        rst   = platform.request("user_btn", 0)

        # Power on reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += self.cd_por.clk.eq(clk12)
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # PLL
        self.submodules.pll = pll = ECP5PLL()
        self.comb += pll.reset.eq(~por_done | rst | self.rst)
        pll.register_clkin(clk12, 12e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)


class _CRGSDRAM(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_init    = ClockDomain()
        self.clock_domains.cd_por     = ClockDomain()
        self.clock_domains.cd_sys     = ClockDomain()
        self.clock_domains.cd_sys2x   = ClockDomain()
        self.clock_domains.cd_sys2x_i = ClockDomain()

        # # #

        self.stop  = Signal()
        self.reset = Signal()

        # Clk / Rst
        clk12 = platform.request("clk12")
        rst   = platform.request("user_btn", 0)

        # Power on reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += self.cd_por.clk.eq(clk12)
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # PLL
        sys2x_clk_ecsout = Signal()
        self.submodules.pll = pll = ECP5PLL()
        self.comb += pll.reset.eq(~por_done | rst | self.rst)
        pll.register_clkin(clk12, 12e6)
        pll.create_clkout(self.cd_sys2x_i, 2*sys_clk_freq)
        pll.create_clkout(self.cd_init,   25e6)
        self.specials += [
            Instance("ECLKBRIDGECS",
                i_CLK0   = self.cd_sys2x_i.clk,
                i_SEL    = 0,
                o_ECSOUT = sys2x_clk_ecsout,
            ),
            Instance("ECLKSYNCB",
                i_ECLKI = sys2x_clk_ecsout,
                i_STOP  = self.stop,
                o_ECLKO = self.cd_sys2x.clk),
            Instance("CLKDIVF",
                p_DIV     = "2.0",
                i_ALIGNWD = 0,
                i_CLKI    = self.cd_sys2x.clk,
                i_RST     = self.reset,
                o_CDIVX   = self.cd_sys.clk),
            AsyncResetSynchronizer(self.cd_sys, ~pll.locked | self.reset),
        ]

        self.comb += platform.request("dram_vtt_en").eq(1)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(75e6), toolchain="trellis",
        with_ethernet          = False,
        with_video_terminal    = False,
        with_video_framebuffer = False,
        with_led_chaser        = True,
        with_pmod_gpio         = False,
        **kwargs):
        platform = trellisboard.Platform(toolchain=toolchain)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident = "LiteX SoC on Trellis Board",
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        crg_cls = _CRGSDRAM if not self.integrated_main_ram_size else _CRG
        self.submodules.crg = crg_cls(platform, sys_clk_freq)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.submodules.ddrphy = ECP5DDRPHY(
                platform.request("ddram"),
                sys_clk_freq=sys_clk_freq)
            self.comb += self.crg.stop.eq(self.ddrphy.init.stop)
            self.comb += self.crg.reset.eq(self.ddrphy.init.reset)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT41J256M16(sys_clk_freq, "1:2"),
                l2_cache_size = kwargs.get("l2_size", 8192),
            )

        # Ethernet ---------------------------------------------------------------------------------
        if with_ethernet:
            self.submodules.ethphy = LiteEthPHYRGMII(
                clock_pads = self.platform.request("eth_clocks"),
                pads       = self.platform.request("eth"))
            self.add_ethernet(phy=self.ethphy)

        # HDMI -------------------------------------------------------------------------------------
        if with_video_terminal or with_video_framebuffer:
            # PHY + TP410 I2C initialization.
            hdmi_pads = platform.request("hdmi")
            self.submodules.videophy = VideoDVIPHY(hdmi_pads, clock_domain="init")
            self.submodules.videoi2c = I2CMaster(hdmi_pads)
            self.videoi2c.add_init(addr=0x38, init=[
                (0x08, 0x35) # CTL_1_MODE: Normal operation, 24-bit, HSYNC/VSYNC.
            ])

            # Video Terminal/Framebuffer.
            if with_video_terminal:
                self.add_video_terminal(phy=self.videophy, timings="640x480@75Hz", clock_domain="init")
            if with_video_framebuffer:
                self.add_video_framebuffer(phy=self.videophy, timings="640x480@75Hz", clock_domain="init")

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

        # GPIOs ------------------------------------------------------------------------------------
        if with_pmod_gpio:
            platform.add_extension(trellisboard.raw_pmod_io("pmoda"))
            self.submodules.gpio = GPIOTristate(platform.request("pmoda"))

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on Trellis Board")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",           action="store_true", help="Build bitstream.")
    target_group.add_argument("--load",            action="store_true", help="Load bitstream.")
    target_group.add_argument("--toolchain",       default="trellis",   help="FPGA toolchain (trellis or diamond).")
    target_group.add_argument("--sys-clk-freq",    default=75e6,        help="System clock frequency.")
    target_group.add_argument("--with-ethernet",   action="store_true", help="Enable Ethernet support.")
    viopts = target_group.add_mutually_exclusive_group()
    viopts.add_argument("--with-video-terminal",    action="store_true", help="Enable Video Terminal (HDMI).")
    viopts.add_argument("--with-video-framebuffer", action="store_true", help="Enable Video Framebuffer (HDMI).")
    sdopts = target_group.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-sdcard", action="store_true", help="Enable SPI-mode SDCard support.")
    sdopts.add_argument("--with-sdcard",     action="store_true", help="Enable SDCard support.")
    target_group.add_argument("--with-pmod-gpio",  action="store_true", help="Enable GPIOs through PMOD.") # FIXME: Temporary test.
    builder_args(parser)
    soc_core_args(parser)
    trellis_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq           = int(float(args.sys_clk_freq)),
        with_ethernet          = args.with_ethernet,
        with_video_terminal    = args.with_video_terminal,
        with_video_framebuffer = args.with_video_framebuffer,
        with_pmod_gpio         = args.with_pmod_gpio,
        **soc_core_argdict(args)
    )
    if args.with_spi_sdcard:
        soc.add_spi_sdcard()
    if args.with_sdcard:
        soc.add_sdcard()
    builder = Builder(soc, **builder_argdict(args))
    builder_kargs = trellis_argdict(args) if args.toolchain == "trellis" else {}
    builder.build(**builder_kargs, run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram", ext=".svf")) # FIXME

if __name__ == "__main__":
    main()
