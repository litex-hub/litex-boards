#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from litex.build.io import DDROutput
from litex.build.generic_platform import Pins, IOStandard, Misc, Subsignal

from litex.soc.cores.clock.gowin_gw5a import GW5APLL
from litex.soc.integration.soc import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser, WS2812
from litex.soc.cores.gpio import GPIOIn
from litex.soc.cores.video import VideoGowinHDMIPHY

from litedram.modules import AS4C32M16, H5TQ4G63EFR, W9825G6KH6
from litedram.phy import GENSDRPHY, HalfRateGENSDRPHY
from litedram.phy import GW5DDRPHY

from litex_boards.platforms import sipeed_tang_mega_60k

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq,
        with_sdram     = False,
        sdram_rate     = "1:2",
        with_ddr3      = False,
        ddr3_rate      = "1:2",
        with_video_pll = False):
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
            self.cd_init = ClockDomain()

            ddr3_nphases = int(ddr3_rate[-1])
            cd_ddr       = ClockDomain(f"sys{ddr3_nphases}x")
            cd_ddr_i     = ClockDomain(f"sys{ddr3_nphases}x_i")
            setattr(self, f"cd_sys{ddr3_nphases}x",   cd_ddr)
            setattr(self, f"cd_sys{ddr3_nphases}x_i", cd_ddr_i)

            self.stop  = Signal()
            self.reset = Signal()

        # Clk / Rst.
        clk50 = platform.request("sys_clk")
        rst_n = platform.request("sys_rst_n")

        # Power-on reset.
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += self.cd_por.clk.eq(clk50)
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # PLL.
        self.pll = pll = GW5APLL(devicename=platform.devicename, device=platform.device)
        self.comb += pll.reset.eq(~por_done | ~rst_n)
        pll.register_clkin(clk50, 50e6)
        if with_ddr3:
            pll.create_clkout(cd_ddr_i, ddr3_nphases*sys_clk_freq)
        else:
            pll.create_clkout(self.cd_sys, sys_clk_freq)

        # SDRAM clock.
        if with_sdram:
            if sdram_rate == "1:2":
                pll.create_clkout(self.cd_sys2x,    2*sys_clk_freq)
                pll.create_clkout(self.cd_sys2x_ps, 2*sys_clk_freq, phase=180)
                sdram_clk = ClockSignal("sys2x_ps")
            else:
                pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=90)
                sdram_clk = ClockSignal("sys_ps")
            self.specials += DDROutput(1, 0, platform.request("sdram").clk, sdram_clk)

        # DDR3 clock.
        if with_ddr3:
            self.specials += [
                Instance("DHCE",
                    i_CLKIN  = cd_ddr_i.clk,
                    i_CEN    = self.stop,
                    o_CLKOUT = cd_ddr.clk
                ),
                Instance("CLKDIV",
                    p_DIV_MODE = str(ddr3_nphases),
                    i_CALIB    = 0,
                    i_HCLKIN   = cd_ddr.clk,
                    i_RESETN   = ~self.reset,
                    o_CLKOUT   = self.cd_sys.clk
                ),
                AsyncResetSynchronizer(self.cd_sys, ~pll.locked | self.reset),
            ]
            self.comb += [
                self.cd_init.clk.eq(clk50),
                self.cd_init.rst.eq(pll.reset),
            ]

        # Video PLL.
        if with_video_pll:
            self.cd_hdmi   = ClockDomain()
            self.cd_hdmi5x = ClockDomain()
            pll.create_clkout(self.cd_hdmi5x, 125e6, margin=1e-3)
            self.specials += Instance("CLKDIV",
                p_DIV_MODE = "5",
                i_RESETN   = 1,
                i_CALIB    = 0,
                i_HCLKIN   = self.cd_hdmi5x.clk,
                o_CLKOUT   = self.cd_hdmi.clk
            )

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, toolchain="gowin", sys_clk_freq=50e6,
        with_ddr3         = True,
        ddr3_rate         = "1:2",
        with_sdram        = False,
        sdram_model       = "sipeed",
        sdram_rate        = "1:1",
        with_hdmi         = False,
        with_spi_sdcard   = False,
        with_led_chaser   = True,
        with_buttons      = True,
        with_ws2812       = False,
        **kwargs):
        assert ddr3_rate in ("1:2", "1:4")
        assert not with_sdram or (sdram_model in ["sipeed", "mister"])

        platform = sipeed_tang_mega_60k.Platform(toolchain=toolchain)

        with_ddr3 = with_ddr3 and not (with_sdram or kwargs.get("integrated_main_ram_size", 0))
        with_sdram = with_sdram and not kwargs.get("integrated_main_ram_size", 0)

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq,
            with_sdram     = with_sdram,
            sdram_rate     = sdram_rate,
            with_ddr3      = with_ddr3,
            ddr3_rate      = ddr3_rate,
            with_video_pll = with_hdmi,
        )

        # SoCCore ----------------------------------------------------------------------------------
        kwargs["uart_name"] = "stub"
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Tang Mega 60K", **kwargs)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if with_ddr3:
            ddr3_nphases = int(ddr3_rate[-1])
            self.ddrphy = GW5DDRPHY(
                pads         = platform.request("ddram"),
                sys_clk_freq = sys_clk_freq,
                dll_off      = (ddr3_nphases*sys_clk_freq <= 125e6),
                nphases      = ddr3_nphases,
            )
            self.ddrphy.settings.rtt_nom = "disabled"
            self.comb += self.crg.stop.eq(self.ddrphy.init.stop)
            self.comb += self.crg.reset.eq(self.ddrphy.init.reset)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = H5TQ4G63EFR(sys_clk_freq, ddr3_rate),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # SDR SDRAM --------------------------------------------------------------------------------
        if with_sdram:
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

        # HDMI -------------------------------------------------------------------------------------
        if with_hdmi:
            self.videophy = VideoGowinHDMIPHY(platform.request("hdmi_out"), clock_domain="hdmi")
            self.add_video_terminal(phy=self.videophy, timings="640x480@60Hz", clock_domain="hdmi")

        # SD Card ----------------------------------------------------------------------------------
        if with_spi_sdcard:
            platform.add_extension([
                ("spisdcard", 0,
                    Subsignal("clk",  Pins("V15"),  Misc("DRIVE=8")),
                    Subsignal("cs_n", Pins("W15"),  Misc("DRIVE=8")),
                    Subsignal("mosi", Pins("Y16"),  Misc("DRIVE=8")),
                    Subsignal("miso", Pins("AA15"), Misc("DRIVE=OFF")),
                    IOStandard("LVCMOS33"),
                    Misc("PULL_MODE=NONE")
                ),
            ])
            self.add_spi_sdcard()

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("led"),
                sys_clk_freq = sys_clk_freq
            )

        # Buttons ----------------------------------------------------------------------------------
        if with_buttons:
            self.buttons = GPIOIn(Cat(platform.request_all("btn")))

        # WS2812 -----------------------------------------------------------------------------------
        if with_ws2812:
            self.ws2812 = WS2812(platform.request("ws2812"), nleds=1, sys_clk_freq=sys_clk_freq)
            self.bus.add_slave(name="ws2812", slave=self.ws2812.bus, region=SoCRegion(
                origin = 0x2000_0000,
                size   = 4,
            ))

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=sipeed_tang_mega_60k.Platform, description="LiteX SoC on Tang Mega 60K.")
    parser.add_target_argument("--flash",         action="store_true",      help="Flash bitstream.")
    parser.add_target_argument("--sys-clk-freq",  default=50e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--ddr3-rate",     default="1:2", choices=["1:2", "1:4"], help="DDR3 PHY clock ratio.")
    parser.add_target_argument("--with-sdram",    action="store_true",      help="Use SDRAM instead of DDR3.")
    parser.add_target_argument("--sdram-model",   default="sipeed", choices=["sipeed", "mister"], help="SDRAM module model.")
    parser.add_target_argument("--sdram-rate",    default="1:1", choices=["1:1", "1:2"],          help="SDRAM clock ratio.")
    parser.add_target_argument("--with-hdmi",     action="store_true",      help="Enable HDMI Video Terminal.")
    parser.add_target_argument("--with-spi-sdcard", action="store_true",    help="Enable SPI-mode SDCard support.")
    parser.add_target_argument("--with-ws2812",   action="store_true",      help="Enable WS2812 LED.")
    parser.add_target_argument("--without-ddr3",  action="store_true",      help="Disable DDR3 SDRAM.")
    parser.add_target_argument("--without-buttons", action="store_true",    help="Disable Buttons.")
    parser.add_target_argument("--without-leds",  action="store_true",      help="Disable LED Chaser.")
    args = parser.parse_args()

    soc = BaseSoC(
        toolchain        = args.toolchain,
        sys_clk_freq     = args.sys_clk_freq,
        with_ddr3        = not args.without_ddr3,
        ddr3_rate        = args.ddr3_rate,
        with_sdram       = args.with_sdram,
        sdram_model      = args.sdram_model,
        sdram_rate       = args.sdram_rate,
        with_hdmi        = args.with_hdmi,
        with_spi_sdcard  = args.with_spi_sdcard,
        with_led_chaser  = not args.without_leds,
        with_buttons     = not args.without_buttons,
        with_ws2812      = args.with_ws2812,
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
        prog.flash(0, builder.get_bitstream_filename(mode="flash", ext=".fs"))

if __name__ == "__main__":
    main()
