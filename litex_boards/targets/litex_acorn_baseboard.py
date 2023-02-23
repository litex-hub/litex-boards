#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import *

from litex_boards.platforms import litex_acorn_baseboard

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.video import VideoHDMIPHY
from litex.soc.cores.bitbang import I2CMaster

from liteeth.phy.ecp5rgmii import LiteEthPHYRGMII

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_video_pll=False):
        self.rst    = Signal()
        self.cd_por = ClockDomain()
        self.cd_sys = ClockDomain()

        # # #

        # Clk / Rst
        clk50 = platform.request("clk50")

        # Power on reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += self.cd_por.clk.eq(clk50)
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # PLL
        self.pll = pll = ECP5PLL()
        self.comb += pll.reset.eq(~por_done | self.rst)
        pll.register_clkin(clk50, 50e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)

        # Video PLL
        if with_video_pll:
            self.video_pll = video_pll = ECP5PLL()
            self.comb += pll.reset.eq(~por_done | self.rst)
            video_pll.register_clkin(clk50, 50e6)
            self.cd_hdmi   = ClockDomain()
            self.cd_hdmi5x = ClockDomain()
            video_pll.create_clkout(self.cd_hdmi,    40e6, margin=0)
            video_pll.create_clkout(self.cd_hdmi5x, 200e6, margin=0)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=75e6, toolchain="trellis",
        with_spi_flash      = False,
        with_ethernet       = False,
        with_etherbone      = False,
        with_video_terminal = False,
        with_lcd            = False,
        with_ws2812         = False,
        **kwargs):
        platform = litex_acorn_baseboard.Platform(toolchain=toolchain)

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, with_video_pll=with_video_terminal)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on LiteX M2 Baseboard", **kwargs)

        # SPI Flash --------------------------------------------------------------------------------
        if with_spi_flash:
            from litespi.modules import W25Q128JV
            from litespi.opcodes import SpiNorFlashOpCodes as Codes
            self.add_spi_flash(mode="4x", module=W25Q128JV(Codes.READ_1_1_4), with_master=True)

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            self.ethphy = LiteEthPHYRGMII(
                clock_pads = self.platform.request("eth_clocks"),
                pads       = self.platform.request("eth"),
                rx_delay   = 0e-9)
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy)
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy)

        # Video ------------------------------------------------------------------------------------
        if with_video_terminal:
            self.videophy = VideoHDMIPHY(platform.request("hdmi"), clock_domain="hdmi", pn_swap=["g", "r"])
            self.add_video_terminal(phy=self.videophy, timings="800x600@60Hz", clock_domain="hdmi")

        # LCD --------------------------------------------------------------------------------------
        if with_lcd:
            self.i2c = I2CMaster(platform.request("lcd"))

        # M2 --------------------------------------------------------------------------------------
        self.comb += platform.request("m2_devslp").eq(0) # Enable SATA M2.

        # WS2812 ----------------------------------------------------------------------------------
        if with_ws2812:
            from litex.build.generic_platform import Pins, IOStandard
            from litex.soc.integration.soc import SoCRegion
            from litex.soc.cores.led import WS2812
            platform.add_extension([("ws2812", 0, Pins("pmod1:0"), IOStandard("LVCMOS33"))])
            self.ws2812 = WS2812(platform.request("ws2812"), nleds=64, sys_clk_freq=sys_clk_freq)
            self.bus.add_slave(name="ws2812", slave=self.ws2812.bus, region=SoCRegion(
                origin = 0x2000_0000,
                size   = 64*4,
            ))

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=litex_acorn_baseboard.Platform, description="LiteX SoC on LiteX Acorn Baseboard.")
    parser.add_target_argument("--flash",        action="store_true",      help="Flash bitstream to SPI Flash.")
    parser.add_target_argument("--sys-clk-freq", default=75e6, type=float, help="System clock frequency.")
    ethopts = parser.target_group.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",  action="store_true", help="Enable Ethernet support.")
    ethopts.add_argument("--with-etherbone", action="store_true", help="Enable Etherbone support.")
    sdopts = parser.target_group.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-sdcard", action="store_true", help="Enable SPI-mode SDCard support.")
    sdopts.add_argument("--with-sdcard",     action="store_true", help="Enable SDCard support.")
    viopts = parser.target_group.add_mutually_exclusive_group()
    viopts.add_argument("--with-video-terminal", action="store_true", help="Enable Video Terminal (HDMI).")
    parser.add_target_argument("--with-spi-flash", action="store_true",      help="Enable SPI Flash (MMAPed).")
    parser.add_target_argument("--with-lcd",       action="store_true",      help="Enable OLED LCD support.")
    parser.add_target_argument("--with-ws2812",    action="store_true",      help="Enable WS2812 on PMOD1:0.")

    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq        = args.sys_clk_freq,
        toolchain           = args.toolchain,
        with_spi_flash      = args.with_spi_flash,
        with_ethernet       = args.with_ethernet,
        with_etherbone      = args.with_etherbone,
        with_video_terminal = args.with_video_terminal,
        with_lcd            = args.with_lcd,
        with_ws2812         = args.with_ws2812,
        **parser.soc_argdict
    )
    if args.with_spi_sdcard:
        soc.add_spi_sdcard()
    if args.with_sdcard:
        soc.add_sdcard()
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.flash(None, prog.load_bitstream(builder.get_bitstream_filename(mode="flash")))

if __name__ == "__main__":
    main()
