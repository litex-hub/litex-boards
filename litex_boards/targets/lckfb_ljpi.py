#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2024 Andelf <andelf@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from litex.soc.cores.clock.gowin_gw2a import GW2APLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.gpio import GPIOIn
from litex.soc.cores.video import *

from litex_boards.platforms import lckfb_ljpi

from litedram.modules import MT41J128M16
from litedram.phy import GW2DDRPHY

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_hdmi=False, with_dram=False):
        self.rst            = Signal()
        self.cd_sys         = ClockDomain()
        self.cd_por         = ClockDomain()
        if with_dram:
            self.cd_init    = ClockDomain()
            self.cd_sys2x   = ClockDomain()
            self.cd_sys2x_i = ClockDomain()
        if with_hdmi:
            self.cd_hdmi    = ClockDomain()
            self.cd_hdmi5x  = ClockDomain()

        # # #

        self.stop  = Signal()
        self.reset = Signal()

        # Clk / Rst
        clk50 = platform.request("clk50")
        rst_n  = platform.request("rst_n")

        # Power on reset (the onboard POR is not aware of reprogramming)
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += self.cd_por.clk.eq(clk50)
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # PLL
        self.pll = pll = GW2APLL(devicename=platform.devicename, device=platform.device)
        self.comb += pll.reset.eq(~por_done | ~rst_n)
        pll.register_clkin(clk50, 50e6)
        if with_dram:
            # 2:1 clock needed for DDR
            pll.create_clkout(self.cd_sys2x_i, 2*sys_clk_freq)
            self.specials += [
                Instance("DHCEN",
                    i_CLKIN  = self.cd_sys2x_i.clk,
                    i_CE     = self.stop,
                    o_CLKOUT = self.cd_sys2x.clk),
                Instance("CLKDIV",
                    p_DIV_MODE = "2",
                    i_CALIB    = 0,
                    i_HCLKIN   = self.cd_sys2x.clk,
                    i_RESETN   = ~self.reset,
                    o_CLKOUT   = self.cd_sys.clk),
            ]

            # Init clock domain
            self.comb += self.cd_init.clk.eq(clk50)
            self.comb += self.cd_init.rst.eq(pll.reset)
        else:
            pll.create_clkout(self.cd_sys, sys_clk_freq)

        self.specials += AsyncResetSynchronizer(self.cd_sys, ~pll.locked | self.rst | self.reset)

        # Video PLL
        if with_hdmi:
            self.video_pll = video_pll = GW2APLL(devicename=platform.devicename, device=platform.device)
            video_pll.register_clkin(clk50, 50e6)
            video_pll.create_clkout(self.cd_hdmi5x, 125e6, margin=1e-3)
            self.specials += Instance("CLKDIV",
                p_DIV_MODE = "5",
                i_RESETN   = 1, # Disable reset signal.
                i_CALIB    = 0, # No calibration.
                i_HCLKIN   = self.cd_hdmi5x.clk,
                o_CLKOUT   = self.cd_hdmi.clk
            )

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, toolchain="gowin", sys_clk_freq=50e6,
        with_spi_flash      = False,
        with_led_chaser     = True,
        with_buttons        = True,
        with_video_terminal = False,
        with_video_colorbars = False,
        **kwargs):

        platform = lckfb_ljpi.Platform(toolchain=toolchain)

        with_hdmi = with_video_terminal or with_video_colorbars

        # CRG --------------------------------------------------------------------------------------
        with_dram = (kwargs.get("integrated_main_ram_size", 0) == 0)
        assert not (toolchain == "apicula" and with_dram)
        self.crg  = _CRG(platform, sys_clk_freq, with_hdmi=with_hdmi, with_dram=with_dram)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on LCKFB LJPI", **kwargs)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        # if not self.integrated_main_ram_size:
        if with_dram:
            self.ddrphy = GW2DDRPHY(
                pads         = platform.request("ddram"),
                sys_clk_freq = sys_clk_freq
            )
            self.ddrphy.settings.rtt_nom = "disabled"
            self.comb += self.crg.stop.eq(self.ddrphy.init.stop)
            self.comb += self.crg.reset.eq(self.ddrphy.init.reset)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT41J128M16(sys_clk_freq, "1:4"),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # SPI Flash --------------------------------------------------------------------------------
        if with_spi_flash:
            from litespi.modules import W25Q64JV as SpiFlashModule
            from litespi.opcodes import SpiNorFlashOpCodes as Codes
            self.add_spi_flash(mode="1x", module=SpiFlashModule(Codes.READ_1_1_1))

        # Video ------------------------------------------------------------------------------------
        if with_hdmi:
            hdmi_pads = platform.request("hdmi")
            self.videophy = VideoHDMIPHY(hdmi_pads, clock_domain="hdmi")
            if with_video_terminal:
                # self.add_video_terminal(phy=self.videophy, timings="640x480@75Hz", clock_domain="hdmi")
                self.add_video_terminal(phy=self.videophy, timings="800x600@75Hz", clock_domain="hdmi")
            if with_video_colorbars:
                # self.add_video_colorbars(phy=self.videophy, timings="640x480@60Hz", clock_domain="hdmi")
                # self.add_video_colorbars(phy=self.videophy, timings="800x600@75Hz", clock_domain="hdmi")
                self.add_video_colorbars(phy=self.videophy, timings="1024x768@60Hz", clock_domain="hdmi")

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("led"),
                sys_clk_freq = sys_clk_freq
            )

        # Buttons ----------------------------------------------------------------------------------
        if with_buttons:
            self.buttons = GPIOIn(pads=~platform.request_all("btn_n"))


# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=lckfb_ljpi.Platform, description="LiteX SoC on LCKFB LJPI.")
    parser.add_target_argument("--flash",          action="store_true",      help="Flash Bitstream.")
    parser.add_target_argument("--sys-clk-freq",   default=50e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-spi-flash", action="store_true", help="Enable SPI Flash (MMAPed).")
    viopts = parser.target_group.add_mutually_exclusive_group()
    viopts.add_argument("--with-video-terminal",   action="store_true", help="Enable Video Terminal (HDMI).")
    viopts.add_argument("--with-video-colorbars",  action="store_true", help="Enable Video Colorbars (HDMI).")
    parser.add_target_argument("--prog-kit",       default="gpwin", help="Programmer select from Gowin/openFPGALoader.")

    args = parser.parse_args()

    soc = BaseSoC(
        toolchain            = args.toolchain,
        sys_clk_freq         = args.sys_clk_freq,
        with_spi_flash       = args.with_spi_flash,
        with_video_terminal  = args.with_video_terminal,
        with_video_colorbars = args.with_video_colorbars,
        **parser.soc_argdict
    )

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer(kit=args.prog_kit)
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer(kit=args.prog_kit)
        prog.flash(0, builder.get_bitstream_filename(mode="flash", ext=".fs"))

if __name__ == "__main__":
    main()
