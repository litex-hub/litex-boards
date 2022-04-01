#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2015-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex_boards.platforms import nexys_video
from litex.build.xilinx.vivado import vivado_build_args, vivado_build_argdict

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.video import VideoS7HDMIPHY
from litex.soc.cores.led import LedChaser

from litedram.modules import MT41K256M16
from litedram.phy import s7ddrphy

from liteeth.phy.s7rgmii import LiteEthPHYRGMII

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq, toolchain="vivado", with_sata_pll_refclk=False, with_video_pll=False):
        self.rst = Signal()
        self.clock_domains.cd_sys       = ClockDomain()
        self.clock_domains.cd_sys4x     = ClockDomain()
        self.clock_domains.cd_sys4x_dqs = ClockDomain()
        self.clock_domains.cd_idelay    = ClockDomain()
        self.clock_domains.cd_hdmi      = ClockDomain()
        self.clock_domains.cd_hdmi5x    = ClockDomain()
        self.clock_domains.cd_clk100    = ClockDomain()

        # # #

        # Clk / Rst.
        clk100 = platform.request("clk100")
        rst_n  = platform.request("cpu_reset")

        # PLL.
        if toolchain == "vivado":
            self.submodules.pll = pll = S7MMCM(speedgrade=-1)
        else:
            self.submodules.pll = pll = S7PLL(speedgrade=-1)
        self.comb += pll.reset.eq(~rst_n | self.rst)
        pll.register_clkin(clk100, 100e6)
        pll.create_clkout(self.cd_sys,       sys_clk_freq)
        pll.create_clkout(self.cd_sys4x,     4*sys_clk_freq)
        pll.create_clkout(self.cd_sys4x_dqs, 4*sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_idelay,    200e6)
        pll.create_clkout(self.cd_clk100,    100e6)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        self.submodules.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

        # SATA PLL.
        if with_sata_pll_refclk:
            self.clock_domains.cd_sata_refclk = ClockDomain()
            pll.create_clkout(self.cd_sata_refclk, 150e6)
            platform.add_platform_command("set_property SEVERITY {{WARNING}} [get_drc_checks REQP-49]")

        # Video PLL.
        if with_video_pll:
            self.submodules.video_pll = video_pll = S7MMCM(speedgrade=-1)
            video_pll.reset.eq(~rst_n | self.rst)
            video_pll.register_clkin(clk100, 100e6)
            video_pll.create_clkout(self.cd_hdmi,   40e6)
            video_pll.create_clkout(self.cd_hdmi5x, 5*40e6)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, toolchain="vivado", sys_clk_freq=int(100e6), with_ethernet=False,
                 with_led_chaser=True, with_sata=False, sata_gen="gen2", with_sata_pll_refclk=False, vadj="1.2V", with_video_terminal=False,
                 with_video_framebuffer=False, **kwargs):
        platform = nexys_video.Platform(toolchain=toolchain)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident = "LiteX SoC on Nexys Video",
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        with_video_pll = (with_video_terminal or with_video_framebuffer)
        self.submodules.crg = _CRG(platform, sys_clk_freq, toolchain, with_sata_pll_refclk=with_sata_pll_refclk, with_video_pll=with_video_pll)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.submodules.ddrphy = s7ddrphy.A7DDRPHY(platform.request("ddram"),
                memtype      = "DDR3",
                nphases      = 4,
                sys_clk_freq = sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT41K256M16(sys_clk_freq, "1:4"),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Ethernet ---------------------------------------------------------------------------------
        if with_ethernet:
            self.submodules.ethphy = LiteEthPHYRGMII(
                clock_pads = self.platform.request("eth_clocks"),
                pads       = self.platform.request("eth"))
            self.add_ethernet(phy=self.ethphy)

        # SATA -------------------------------------------------------------------------------------
        if with_sata:
            from litex.build.generic_platform import Subsignal, Pins
            from litesata.phy import LiteSATAPHY

            # IOs
            _sata_io = [
                # AB09-FMCRAID / https://www.dgway.com/AB09-FMCRAID_E.html
                ("fmc2sata", 0,
                    Subsignal("clk_p", Pins("LPC:GBTCLK0_M2C_P")),
                    Subsignal("clk_n", Pins("LPC:GBTCLK0_M2C_N")),
                    Subsignal("tx_p",  Pins("LPC:DP0_C2M_P")),
                    Subsignal("tx_n",  Pins("LPC:DP0_C2M_N")),
                    Subsignal("rx_p",  Pins("LPC:DP0_M2C_P")),
                    Subsignal("rx_n",  Pins("LPC:DP0_M2C_N"))
                ),
            ]
            platform.add_extension(_sata_io)

            # PHY
            self.submodules.sata_phy = LiteSATAPHY(platform.device,
                refclk     = None if not with_sata_pll_refclk else self.crg.cd_sata_refclk.clk,
                pads       = platform.request("fmc2sata"),
                gen        = sata_gen,
                clk_freq   = sys_clk_freq,
                data_width = 16)

            # Core
            self.add_sata(phy=self.sata_phy, mode="read+write")

        # Video ------------------------------------------------------------------------------------
        if with_video_terminal or with_video_framebuffer:
            self.submodules.videophy = VideoS7HDMIPHY(platform.request("hdmi_out"), clock_domain="hdmi")
            if with_video_terminal:
                self.add_video_terminal(phy=self.videophy, timings="800x600@60Hz", clock_domain="hdmi")
            if with_video_framebuffer:
                self.add_video_framebuffer(phy=self.videophy, timings="800x600@60Hz", clock_domain="hdmi")

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

        # VADJ -------------------------------------------------------------------------------------
        vadj_map = {"1.2V": 0b00, "1.8V": 0b01, "2.5V": 0b10, "3.3V": 0b11}
        platform.request_all("vadj").eq(vadj_map[vadj])

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on Nexys Video")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--toolchain",              default="vivado",    help="FPGA toolchain (vivado or symbiflow).")
    target_group.add_argument("--build",                  action="store_true", help="Build bitstream.")
    target_group.add_argument("--load",                   action="store_true", help="Load bitstream.")
    target_group.add_argument("--sys-clk-freq",           default=100e6,       help="System clock frequency.")
    target_group.add_argument("--with-ethernet",          action="store_true", help="Enable Ethernet support.")
    sdopts = target_group.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-sdcard",        action="store_true", help="Enable SPI-mode SDCard support.")
    sdopts.add_argument("--with-sdcard",            action="store_true", help="Enable SDCard support.")
    target_group.add_argument("--with-sata",              action="store_true", help="Enable SATA support (over FMCRAID).")
    target_group.add_argument("--sata-gen",               default="2",         help="SATA Gen.", choices=["1", "2"])
    target_group.add_argument("--with-sata-pll-refclk",   action="store_true", help="Generate SATA RefClk from PLL.")
    target_group.add_argument("--vadj",                   default="1.2V",      help="FMC VADJ value.", choices=["1.2V", "1.8V", "2.5V", "3.3V"])
    viopts = target_group.add_mutually_exclusive_group()
    viopts.add_argument("--with-video-terminal",    action="store_true", help="Enable Video Terminal (HDMI).")
    viopts.add_argument("--with-video-framebuffer", action="store_true", help="Enable Video Framebuffer (HDMI).")
    builder_args(parser)
    soc_core_args(parser)
    vivado_build_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        toolchain              = args.toolchain,
        sys_clk_freq           = int(float(args.sys_clk_freq)),
        with_ethernet          = args.with_ethernet,
        with_sata              = args.with_sata,
        sata_gen               = "gen" + args.sata_gen,
        with_sata_pll_refclk   = args.with_sata_pll_refclk,
        vadj                   = args.vadj,
        with_video_terminal    = args.with_video_terminal,
        with_video_framebuffer = args.with_video_framebuffer,
        **soc_core_argdict(args)
    )
    if args.with_spi_sdcard:
        soc.add_spi_sdcard()
    if args.with_sdcard:
        soc.add_sdcard()
    builder = Builder(soc, **builder_argdict(args))
    builder_kwargs = vivado_build_argdict(args) if args.toolchain == "vivado" else {}
    builder.build(**builder_kwargs, run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
