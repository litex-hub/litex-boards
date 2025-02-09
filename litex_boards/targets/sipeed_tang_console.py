#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022-2023 Icenowy Zheng <uwu@icenowy.me>
# Copyright (c) 2022-2024 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2025 Gwenhael Goavec-Merou <gwenhael@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from litex_boards.platforms import sipeed_tang_console

from litex.soc.cores.clock.gowin_gw5a import GW5APLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.video import *

from litedram.modules import AS4C32M16, MT41J128M16, W9825G6KH6
from litedram.phy import GENSDRPHY, HalfRateGENSDRPHY
from litedram.phy import GW5DDRPHY
from litex.build.io import DDROutput

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_sdram=False, sdram_rate="1:2", with_ddr3=False, with_video_pll=False):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()
        self.cd_por = ClockDomain()
        if with_sdram:
            if sdram_rate == "1:2":
                self.cd_sys2x    = ClockDomain()
                self.cd_sys2x_ps = ClockDomain()
            else:
                self.cd_sys_ps = ClockDomain()

        if with_ddr3:
            self.cd_init    = ClockDomain()
            self.cd_sys2x   = ClockDomain()
            self.cd_sys2x_i = ClockDomain()
            self.stop       = Signal()
            self.reset      = Signal()

        # Clk
        clk50 = platform.request("clk50")
        rst   = platform.request("rst")

        # Power on reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += self.cd_por.clk.eq(clk50)
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # PLL
        self.pll = pll = GW5APLL(devicename=platform.devicename, device=platform.device)
        self.comb += pll.reset.eq(~por_done | rst)
        pll.register_clkin(clk50, 50e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq, with_reset=not with_ddr3)

        # SDRAM clock
        if with_sdram:
            if sdram_rate == "1:2":
                pll.create_clkout(self.cd_sys2x,    2*sys_clk_freq)
                pll.create_clkout(self.cd_sys2x_ps, 2*sys_clk_freq, phase=180)
                sdram_clk = ClockSignal("sys2x_ps")
            else:
                pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=90)
                sdram_clk = ClockSignal("sys_ps")
            self.specials += DDROutput(1, 0, platform.request("sdram_clock"), sdram_clk)

        # DDR3 clock
        if with_ddr3:
            pll.create_clkout(self.cd_sys2x_i, 2*sys_clk_freq)
            self.specials += [
                Instance("DHCE",
                    i_CLKIN  = self.cd_sys2x_i.clk,
                    i_CEN    = self.stop,
                    o_CLKOUT = self.cd_sys2x.clk
                ),
                AsyncResetSynchronizer(self.cd_sys, ~pll.locked | self.reset),
            ]
            # Init clock domain
            self.comb += self.cd_init.clk.eq(clk50)
            self.comb += self.cd_init.rst.eq(pll.reset)

        if with_video_pll:
            self.cd_hdmi   = ClockDomain()
            self.cd_hdmi5x = ClockDomain()
            pll.create_clkout(self.cd_hdmi5x, 125e6, margin=1e-3)
            self.specials += Instance("CLKDIV",
                p_DIV_MODE = "5",
                i_HCLKIN   = self.cd_hdmi5x.clk,
                i_RESETN   = 1, # Disable reset signal.
                i_CALIB    = 0, # No calibration.
                o_CLKOUT   = self.cd_hdmi.clk
            )

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, toolchain="gowin", sys_clk_freq=50e6,
        with_video_terminal = False,
        with_ddr3           = False,
        with_sdram          = False,
        sdram_model         = "sipeed",
        sdram_rate          = "1:1",
        with_spi_flash      = False,
        with_sdcard         = False,
        with_spi_sdcard     = False,
        with_led_chaser     = True,
        with_buttons        = True,
        **kwargs):
        platform = sipeed_tang_console.Platform(toolchain=toolchain)

        assert not with_sdram or (sdram_model in ["sipeed", "mister"])

        if with_sdram:
            platform.add_extension({
                "sipeed": sipeed_tang_console.sipeedSDRAM(),
                "mister": sipeed_tang_console.misterSDRAM}[sdram_model]
            )

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq,
            with_sdram     = with_sdram,
            sdram_rate     = sdram_rate,
            with_ddr3      = with_ddr3,
            with_video_pll = with_video_terminal,
        )
        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Tang Console", **kwargs)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if with_ddr3 and not self.integrated_main_ram_size:
            self.ddrphy = GW5DDRPHY(
                pads         = platform.request("ddram"),
                sys_clk_freq = sys_clk_freq
            )
            self.ddrphy.settings.rtt_nom = "disabled"
            self.comb += self.crg.stop.eq(self.ddrphy.init.stop)
            self.comb += self.crg.reset.eq(self.ddrphy.init.reset)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT41J128M16(sys_clk_freq, "1:2"),
                l2_cache_size = 0#kwargs.get("l2_size", 8192)
            )

        # SDR SDRAM --------------------------------------------------------------------------------
        if with_sdram and not self.integrated_main_ram_size:
            module_cls = {
                "sipeed": W9825G6KH6,
                "mister": AS4C32M16}[sdram_model]
            if sdram_rate == "1:2":
                sdrphy_cls = HalfRateGENSDRPHY
            else:
                sdrphy_cls = GENSDRPHY
            self.sdrphy = sdrphy_cls(platform.request("sdram"), sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.sdrphy,
                module        = module_cls(sys_clk_freq, sdram_rate),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Video ------------------------------------------------------------------------------------
        if with_video_terminal:
            hdmi_pads = platform.request("hdmi")
            self.comb += hdmi_pads.hdp.eq(1)
            self.comb += hdmi_pads.pwr_sav.eq(0)
            self.videophy = VideoGowinHDMIPHY(hdmi_pads, clock_domain="hdmi")
            #self.add_video_colorbars(phy=self.videophy, timings="640x480@60Hz", clock_domain="hdmi")
            self.add_video_terminal(phy=self.videophy, timings="640x480@75Hz", clock_domain="hdmi")

        # SPI Flash --------------------------------------------------------------------------------
        if with_spi_flash:
            from litespi.modules import W25Q64JV
            from litespi.opcodes import SpiNorFlashOpCodes as Codes
            #self.add_spi_flash(mode="1x", module=W25Q64JV(Codes.READ_1_1_1))
            self.add_spi_flash(mode="4x", module=W25Q64JV(Codes.READ_1_1_4))

        # SD Card ----------------------------------------------------------------------------------
        if with_sdcard:
            self.add_sdcard(software_debug=False)
        if with_spi_sdcard:
            self.add_spi_sdcard()

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("led"),
                sys_clk_freq = sys_clk_freq
            )

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=sipeed_tang_console.Platform, description="LiteX SoC on Tang Console.")
    parser.add_target_argument("--flash",           action="store_true",      help="Flash Bitstream.")
    parser.add_target_argument("--sys-clk-freq",    default=50e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-spi-flash",  action="store_true",      help="Enable SPI Flash (MMAPed).")
    parser.add_target_argument("--with-sdcard",     action="store_true",      help="Enable SDCard support.")
    parser.add_target_argument("--with-spi-sdcard", action="store_true",      help="Enable SPI-mode SDCard support.")
    parser.add_target_argument("--with-sdram",      action="store_true",      help="Enable optional SDRAM module.")
    parser.add_target_argument("--sdram-model",     default="sipeed",         help="SDRAM module model.",
        choices=[
            "sipeed",
            "mister"
    ])
    parser.add_target_argument("--with-ddr3",       action="store_true",      help="Enable optional DDR3 module.")
    parser.add_target_argument("--with-video-terminal", action="store_true",  help="Enable Video Terminal (HDMI).")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq        = args.sys_clk_freq,
        with_video_terminal = args.with_video_terminal,
        with_ddr3           = args.with_ddr3,
        with_sdram          = args.with_sdram,
        sdram_model         = args.sdram_model,
        with_spi_flash      = args.with_spi_flash,
        with_sdcard         = args.with_sdcard,
        with_spi_sdcard     = args.with_spi_sdcard,
        **parser.soc_argdict
    )

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.flash(0, builder.get_bitstream_filename(mode="flash", ext=".fs"), external=True)

if __name__ == "__main__":
    main()
