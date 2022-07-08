#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Andrew Gillham <gillham@roadsign.com>
# Copyright (c) 2014-2015 Sebastien Bourdeauducq <sb@m-labs.hk>
# Copyright (c) 2014-2020 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2014-2015 Yann Sionneau <ys@m-labs.hk>
# Copyright (c) 2022 Hans Baier <hansfbaier@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

# This is a variant of the aliexpress_stlv7325 board, with different IO voltages
# available here:
# https://www.aliexpress.com/item/1005001275162791.html

import os

from migen import *

from litex_boards.platforms import hpcstore_stlv7325

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.bitbang import I2CMaster
from litex.soc.cores.video import VideoS6HDMIPHY

from litedram.modules import MT8JTF12864
from litedram.phy import s7ddrphy

from liteeth.phy import LiteEthPHY

from litepcie.phy.s7pciephy import S7PCIEPHY
from litepcie.software import generate_litepcie_software

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_sys    = ClockDomain()
        self.clock_domains.cd_sys4x  = ClockDomain()
        self.clock_domains.cd_idelay = ClockDomain()
        self.clock_domains.cd_hdmi   = ClockDomain()
        self.clock_domains.cd_hdmi5x = ClockDomain()

        # # #

        # Clk/Rst.
        clk200 = platform.request("clk200")
        clk100 = platform.request("clk100")
        rst_n  = platform.request("cpu_reset_n")

        # PLL.
        self.submodules.pll = pll = S7MMCM(speedgrade=-2)
        self.comb += pll.reset.eq(~rst_n | self.rst)
        pll.register_clkin(clk200, 200e6)
        pll.create_clkout(self.cd_sys,    sys_clk_freq)
        pll.create_clkout(self.cd_sys4x,  4*sys_clk_freq)
        pll.create_clkout(self.cd_idelay, 200e6)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        self.submodules.pll2 = pll2 = S7MMCM(speedgrade=-2)
        self.comb += pll2.reset.eq(~rst_n | self.rst)
        pll2.register_clkin(clk100, 100e6)
        pll2.create_clkout(self.cd_hdmi,   25e6,  margin=0)
        pll2.create_clkout(self.cd_hdmi5x, 125e6, margin=0)

        self.submodules.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self,
        toolchain="vivado",
        sys_clk_freq=int(100e6),
        with_ethernet   = False, with_etherbone=False, eth_ip="192.168.1.50", eth_dynamic_ip=False,
        with_led_chaser = True,
        with_pcie       = False,
        with_sata       = False,
        with_video_colorbars   = False,
        with_video_framebuffer = False,
        with_video_terminal    = False,
        **kwargs):
        platform = hpcstore_stlv7325.Platform(toolchain=toolchain)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on HPC Store STLV7325", **kwargs)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.submodules.ddrphy = s7ddrphy.K7DDRPHY(platform.request("ddram"),
                memtype      = "DDR3",
                nphases      = 4,
                sys_clk_freq = sys_clk_freq,
            )
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT8JTF12864(sys_clk_freq, "1:4"),
                l2_cache_size = kwargs.get("l2_size", 8192),
            )

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            self.submodules.ethphy = LiteEthPHY(
                clock_pads = self.platform.request("eth_clocks", 0),
                pads       = self.platform.request("eth", 0),
                clk_freq   = self.clk_freq)
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy, dynamic_ip=eth_dynamic_ip)
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, ip_address=eth_ip)

        # PCIe -------------------------------------------------------------------------------------
        if with_pcie:
            self.submodules.pcie_phy = S7PCIEPHY(platform, platform.request("pcie_x4"),
                data_width = 128,
                bar0_size  = 0x20000)
            self.add_pcie(phy=self.pcie_phy, ndmas=1)

        # TODO verify / test
        # SATA -------------------------------------------------------------------------------------
        if with_sata:
            from litex.build.generic_platform import Subsignal, Pins
            from litesata.phy import LiteSATAPHY

            # RefClk, Generate 150MHz from PLL.
            self.clock_domains.cd_sata_refclk = ClockDomain()
            self.crg.pll.create_clkout(self.cd_sata_refclk, 150e6)
            sata_refclk = ClockSignal("sata_refclk")
            platform.add_platform_command("set_property SEVERITY {{Warning}} [get_drc_checks REQP-52]")

            # PHY
            self.submodules.sata_phy = LiteSATAPHY(platform.device,
                refclk     = sata_refclk,
                pads       = platform.request("sata", 0),
                gen        = "gen2",
                clk_freq   = sys_clk_freq,
                data_width = 16)

            # Core
            self.add_sata(phy=self.sata_phy, mode="read+write")

        # HDMI Options -----------------------------------------------------------------------------
        if (with_video_colorbars or with_video_framebuffer or with_video_terminal):
            self.submodules.videophy = VideoS6HDMIPHY(platform.request("hdmi_out"), clock_domain="hdmi")
            if with_video_colorbars:
                self.add_video_colorbars(phy=self.videophy, timings="640x480@60Hz", clock_domain="hdmi")
            if with_video_terminal:
                self.add_video_terminal(phy=self.videophy, timings="640x480@60Hz", clock_domain="hdmi")
            if with_video_framebuffer:
                self.add_video_framebuffer(phy=self.videophy, timings="640x480@60Hz", clock_domain="hdmi")

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led_n"),
                sys_clk_freq = sys_clk_freq)

        # I2C --------------------------------------------------------------------------------------
        self.submodules.i2c = I2CMaster(platform.request("i2c"))

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on HPC Store STLV7325")
    parser.add_argument("--toolchain", default="vivado", help="FPGA toolchain (vivado, symbiflow or yosys+nextpnr).")

    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",         action="store_true", help="Build design.")
    target_group.add_argument("--load",          action="store_true", help="Load bitstream.")
    target_group.add_argument("--sys-clk-freq",  default=100e6,       help="System clock frequency.")
    ethopts = target_group.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",  action="store_true",              help="Enable Ethernet support.")
    ethopts.add_argument("--with-etherbone", action="store_true",              help="Enable Etherbone support.")
    target_group.add_argument("--eth-ip",          default="192.168.1.50", type=str, help="Ethernet/Etherbone IP address.")
    target_group.add_argument("--eth-dynamic-ip",  action="store_true",              help="Enable dynamic Ethernet IP addresses setting.")
    target_group.add_argument("--with-pcie",       action="store_true", help="Enable PCIe support.")
    target_group.add_argument("--driver",          action="store_true", help="Generate PCIe driver.")
    target_group.add_argument("--with-sata",       action="store_true", help="Enable SATA support.")
    sdopts = target_group.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-sdcard", action="store_true", help="Enable SPI-mode SDCard support.")
    sdopts.add_argument("--with-sdcard",     action="store_true", help="Enable SDCard support.")
    viopts = target_group.add_mutually_exclusive_group()
    viopts.add_argument("--with-video-terminal",    action="store_true", help="Enable Video Terminal (HDMI).")
    viopts.add_argument("--with-video-framebuffer", action="store_true", help="Enable Video Framebuffer (HDMI).")
    viopts.add_argument("--with-video-colorbars",   action="store_true", help="Enable Video Colorbars (HDMI).")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        toolchain      = args.toolchain,
        sys_clk_freq   = int(float(args.sys_clk_freq)),
        with_ethernet  = args.with_ethernet,
        with_etherbone = args.with_etherbone,
        eth_ip         = args.eth_ip,
        eth_dynamic_ip = args.eth_dynamic_ip,
        with_pcie      = args.with_pcie,
        with_sata      = args.with_sata,
        with_video_colorbars   = args.with_video_colorbars,
        with_video_framebuffer = args.with_video_framebuffer,
        with_video_terminal    = args.with_video_terminal,
        **soc_core_argdict(args)
    )

    if args.with_spi_sdcard:
        soc.add_spi_sdcard()

    if args.with_sdcard:
        soc.add_sdcard()

    builder = Builder(soc, **builder_argdict(args))
    if args.build:
        builder.build()

    if args.driver:
        generate_litepcie_software(soc, os.path.join(builder.output_dir, "driver"))

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
