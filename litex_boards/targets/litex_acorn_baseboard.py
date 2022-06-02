#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex_boards.platforms import litex_acorn_baseboard

from litex.build.lattice.trellis import trellis_args, trellis_argdict

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.video import VideoHDMIPHY
from litex.soc.cores.bitbang import I2CMaster

from liteeth.phy.ecp5rgmii import LiteEthPHYRGMII

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq, with_video_pll=False):
        self.rst = Signal()
        self.clock_domains.cd_por = ClockDomain()
        self.clock_domains.cd_sys = ClockDomain()

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
        self.submodules.pll = pll = ECP5PLL()
        self.comb += pll.reset.eq(~por_done | self.rst)
        pll.register_clkin(clk50, 50e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)

        # Video PLL
        if with_video_pll:
            self.submodules.video_pll = video_pll = ECP5PLL()
            self.comb += pll.reset.eq(~por_done | self.rst)
            video_pll.register_clkin(clk50, 50e6)
            self.clock_domains.cd_hdmi   = ClockDomain()
            self.clock_domains.cd_hdmi5x = ClockDomain()
            video_pll.create_clkout(self.cd_hdmi,    40e6, margin=0)
            video_pll.create_clkout(self.cd_hdmi5x, 200e6, margin=0)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(75e6),
        with_spi_flash      = False,
        with_ethernet       = False,
        with_etherbone      = False,
        with_video_terminal = False,
        with_lcd            = False,
        with_ws2812         = False,
        **kwargs):
        platform = litex_acorn_baseboard.Platform(toolchain="trellis")

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq, with_video_pll=with_video_terminal)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on LiteX M2 Baseboard", **kwargs)

        # SPI Flash --------------------------------------------------------------------------------
        if with_spi_flash:
            from litespi.modules import W25Q128JV
            from litespi.opcodes import SpiNorFlashOpCodes as Codes
            self.add_spi_flash(mode="4x", module=W25Q128JV(Codes.READ_1_1_4), with_master=True)

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            self.submodules.ethphy = LiteEthPHYRGMII(
                clock_pads = self.platform.request("eth_clocks"),
                pads       = self.platform.request("eth"),
                rx_delay   = 0e-9)
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy)
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy)

        # Video ------------------------------------------------------------------------------------
        if with_video_terminal:
            self.submodules.videophy = VideoHDMIPHY(platform.request("hdmi"), clock_domain="hdmi", pn_swap=["g", "b"])
            self.add_video_terminal(phy=self.videophy, timings="800x600@60Hz", clock_domain="hdmi")

        # LCD --------------------------------------------------------------------------------------
        if with_lcd:
            self.submodules.i2c = I2CMaster(platform.request("lcd"))

        # M2 --------------------------------------------------------------------------------------
        self.comb += platform.request("m2_devslp").eq(0) # Enable SATA M2.

        # WS2812 ----------------------------------------------------------------------------------
        if with_ws2812:
            from litex.build.generic_platform import Pins, IOStandard
            from litex.soc.integration.soc import SoCRegion
            from litex.soc.cores.led import WS2812
            platform.add_extension([("ws2812", 0, Pins("pmod1:0"), IOStandard("LVCMOS33"))])
            self.submodules.ws2812 = WS2812(platform.request("ws2812"), nleds=64, sys_clk_freq=sys_clk_freq)
            self.bus.add_slave(name="ws2812", slave=self.ws2812.bus, region=SoCRegion(
                origin = 0x2000_0000,
                size   = 64*4,
            ))

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on LiteX Acorn Baseboard")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",        action="store_true", help="Build design.")
    target_group.add_argument("--load",         action="store_true", help="Load bitstream.")
    target_group.add_argument("--flash",        action="store_true", help="Flash bitstream to SPI Flash.")
    target_group.add_argument("--sys-clk-freq", default=75e6,        help="System clock frequency.")
    ethopts = target_group.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",  action="store_true", help="Enable Ethernet support.")
    ethopts.add_argument("--with-etherbone", action="store_true", help="Enable Etherbone support.")
    sdopts = target_group.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-sdcard", action="store_true", help="Enable SPI-mode SDCard support.")
    sdopts.add_argument("--with-sdcard",     action="store_true", help="Enable SDCard support.")
    viopts = target_group.add_mutually_exclusive_group()
    viopts.add_argument("--with-video-terminal", action="store_true", help="Enable Video Terminal (HDMI).")
    target_group.add_argument("--with-spi-flash", action="store_true",      help="Enable SPI Flash (MMAPed).")
    target_group.add_argument("--with-lcd",       action="store_true",      help="Enable OLED LCD support.")
    target_group.add_argument("--with-ws2812",    action="store_true",      help="Enable WS2812 on PMOD1:0.")

    builder_args(parser)
    soc_core_args(parser)
    trellis_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq        = int(float(args.sys_clk_freq)),
        with_spi_flash      = args.with_spi_flash,
        with_ethernet       = args.with_ethernet,
        with_etherbone      = args.with_etherbone,
        with_video_terminal = args.with_video_terminal,
        with_lcd            = args.with_lcd,
        with_ws2812         = args.with_ws2812,
        **soc_core_argdict(args)
    )
    if args.with_spi_sdcard:
        soc.add_spi_sdcard()
    if args.with_sdcard:
        soc.add_sdcard()
    builder = Builder(soc, **builder_argdict(args))
    if args.build:
        builder.build(**trellis_argdict(args))

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.flash(None, prog.load_bitstream(builder.get_bitstream_filename(mode="flash")))

if __name__ == "__main__":
    main()
