#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2023 Hans Baier <hansfbaier@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

# Board product page: https://www.alientek.com/productinfo/945752.html
# Taobao item: https://item.taobao.com/item.htm?id=641238123452
# The Taobao agent I used: https://www.basetao.com/?ejATJf+gGuEbpa8IBg

from migen import *

from litex.gen import *

from litex_boards.platforms import alientek_davincipro

from litex.soc.cores.clock import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.gpio import GPIOIn, GPIOTristate
from litex.soc.cores.xadc import XADC
from litex.soc.cores.dna  import DNA
from litex.soc.cores.video import VideoS7HDMIPHY

from litedram.modules import IS43TR16128B
from litedram.phy import s7ddrphy

from liteeth.phy.s7rgmii import LiteEthPHYRGMII
from litepcie.phy.s7pciephy import S7PCIEPHY


# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_dram=True, with_rst=True, with_hdmi=False):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()
        self.cd_eth = ClockDomain()
        if with_hdmi:
            self.cd_hdmi   = ClockDomain()
            self.cd_hdmi5x = ClockDomain()
        if with_dram:
            self.cd_sys4x     = ClockDomain()
            self.cd_sys4x_dqs = ClockDomain()
            self.cd_idelay    = ClockDomain()

        # # #

        # Clk/Rst.
        clk50 = platform.request("clk50")
        rst   = ~platform.request("cpu_reset") if with_rst else 0

        # PLL.
        self.pll = pll = S7PLL(speedgrade=-2)
        self.comb += pll.reset.eq(rst | self.rst)
        pll.register_clkin(clk50, 50e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        pll.create_clkout(self.cd_eth, 25e6)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.
        if with_dram:
            pll.create_clkout(self.cd_sys4x,     4*sys_clk_freq)
            pll.create_clkout(self.cd_sys4x_dqs, 4*sys_clk_freq, phase=90)
            pll.create_clkout(self.cd_idelay,    200e6)

        # IdelayCtrl.
        if with_dram:
            self.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

        if with_hdmi:
            self.submodules.pll2 = pll2 = S7MMCM(speedgrade=-2)
            self.comb += pll2.reset.eq(rst | self.rst)
            pll2.register_clkin(clk50, 50e6)
            pll2.create_clkout(self.cd_hdmi,   25e6,  margin=0)
            pll2.create_clkout(self.cd_hdmi5x, 125e6, margin=0)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, variant="a7-35", toolchain="vivado", sys_clk_freq=100e6,
        with_xadc       = False,
        with_dna        = False,
        with_ethernet   = False,
        with_etherbone  = False,
        eth_phy         = "rgmii",
        eth_ip          = "192.168.1.50",
        remote_ip       = None,
        eth_dynamic_ip  = False,
        with_pcie       = False,
        with_led_chaser = True,
        with_buttons    = True,
        with_gpio       = False,
        with_video_colorbars   = False,
        with_video_framebuffer = False,
        with_video_terminal    = False,
        **kwargs):
        platform = alientek_davincipro.Platform(variant=variant, toolchain=toolchain)

        with_hdmi = with_video_colorbars or with_video_framebuffer or with_video_terminal

        # CRG --------------------------------------------------------------------------------------
        with_dram = (kwargs.get("integrated_main_ram_size", 0) == 0)
        self.crg  = _CRG(platform, sys_clk_freq, with_dram, with_rst=True, with_hdmi=with_hdmi)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident=f"LiteX SoC on Alientek DaVinci Pro ({variant}t)", **kwargs)

        # XADC -------------------------------------------------------------------------------------
        if with_xadc:
            self.xadc = XADC()

        # DNA --------------------------------------------------------------------------------------
        if with_dna:
            self.dna = DNA()
            self.dna.add_timing_constraints(platform, sys_clk_freq, self.crg.cd_sys.clk)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.ddrphy = s7ddrphy.A7DDRPHY(platform.request("ddram"),
                memtype        = "DDR3",
                nphases        = 4,
                sys_clk_freq   = sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = IS43TR16128B(sys_clk_freq, "1:4"),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

       # Ethernet ---------------------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            # RGMII Ethernet PHY -------------------------------------------------------------------
            if eth_phy == "rgmii":
                # phy
                self.ethphy = LiteEthPHYRGMII(
                    clock_pads = self.platform.request("eth_clocks"),
                    pads       = self.platform.request("eth"))

            # 1000BaseX Ethernet PHY ---------------------------------------------------------------
            if eth_phy == "1000basex":
                # phy
                self.comb += self.platform.request("sfp_tx_disable_n", 0).eq(0)
                qpll_settings = QPLLSettings(
                    refclksel  = 0b001,
                    fbdiv      = 4,
                    fbdiv_45   = 5,
                    refclk_div = 1)
                refclk125 = self.platform.request("gtp_refclk")
                refclk125_se = Signal()
                self.specials += \
                    Instance("IBUFDS_GTE2",
                        i_CEB = 0,
                        i_I   = refclk125.p,
                        i_IB  = refclk125.n,
                        o_O   = refclk125_se)
                qpll = QPLL(refclk125_se, qpll_settings)
                self.submodules += qpll
                self.ethphy = A7_1000BASEX(
                    qpll_channel = qpll.channels[0],
                    data_pads    = self.platform.request("sfp", 0),
                    sys_clk_freq = self.clk_freq)

            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, ip_address=eth_ip, with_ethmac=with_ethernet)
            elif with_ethernet:
                self.add_ethernet(phy=self.ethphy, dynamic_ip=eth_dynamic_ip, local_ip=eth_ip if not eth_dynamic_ip else None, remote_ip=remote_ip)

        # PCIe -------------------------------------------------------------------------------------
        if with_pcie:
            self.pcie_phy = S7PCIEPHY(platform, platform.request("pcie_x2"),
                data_width = 64,
                bar0_size  = 0x20000)
            self.add_pcie(phy=self.pcie_phy, ndmas=1)

        # HDMI Options -----------------------------------------------------------------------------
        if with_hdmi:
            self.submodules.videophy = VideoS7HDMIPHY(platform.request("hdmi_out"), clock_domain="hdmi")
            if with_video_colorbars:
                self.add_video_colorbars(phy=self.videophy, timings="640x480@60Hz", clock_domain="hdmi")
            if with_video_terminal:
                self.add_video_terminal(phy=self.videophy, timings="640x480@60Hz", clock_domain="hdmi")
            if with_video_framebuffer:
                self.add_video_framebuffer(phy=self.videophy, timings="640x480@60Hz", clock_domain="hdmi")

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq,
            )

        # Buttons ----------------------------------------------------------------------------------
        if with_buttons:
            self.buttons = GPIOIn(
                pads     = platform.request_all("user_btn"),
                with_irq = self.irq.enabled
            )

        # GPIOs ------------------------------------------------------------------------------------
        if with_gpio:
            platform.add_extension(alientek_davincipro.raw_j3())
            self.gpio = GPIOTristate(
                pads     = platform.request("J3"),
                with_irq = self.irq.enabled
            )

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=alientek_davincipro.Platform, decription="LiteX SoC on Alientek Davinci Pro.")
    parser.add_target_argument("--flash",          action="store_true",       help="Flash bitstream.")
    parser.add_target_argument("--variant",        default="a7-35",           help="Board variant (a7-35 or a7-100).")
    parser.add_target_argument("--sys-clk-freq",   default=100e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-xadc",      action="store_true",       help="Enable 7-Series XADC.")
    parser.add_target_argument("--with-dna",       action="store_true",       help="Enable 7-Series DNA.")
    parser.add_target_argument("--with-ethernet",  action="store_true",       help="Enable Ethernet support.")
    parser.add_target_argument("--with-etherbone", action="store_true",       help="Enable Etherbone support.")
    parser.add_target_argument("--eth-ip",         default="192.168.1.50",    help="Ethernet/Etherbone IP address.")
    parser.add_target_argument("--remote-ip",      default="192.168.1.100",   help="Remote IP address of TFTP server.")
    parser.add_target_argument("--eth-dynamic-ip", action="store_true",       help="Enable dynamic Ethernet IP addresses setting.")
    parser.add_target_argument("--with-pcie",      action="store_true",        help="Enable PCIe support.")
    viopts = parser.target_group.add_mutually_exclusive_group()
    viopts.add_argument("--with-video-terminal",    action="store_true", help="Enable Video Terminal (HDMI).")
    viopts.add_argument("--with-video-framebuffer", action="store_true", help="Enable Video Framebuffer (HDMI).")
    viopts.add_argument("--with-video-colorbars",   action="store_true", help="Enable Video Colorbars (HDMI).")
    sdopts = parser.target_group.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-sdcard",       action="store_true",       help="Enable SPI-mode SDCard support.")
    sdopts.add_argument("--with-sdcard",           action="store_true",       help="Enable SDCard support.")
    parser.add_target_argument("--with-gpio",      action="store_true",       help="Enable GPIOs through PMOD.") # FIXME: Temporary test.
    args = parser.parse_args()

    assert not (args.with_etherbone and args.eth_dynamic_ip)

    soc = BaseSoC(
        variant        = args.variant,
        toolchain      = args.toolchain,
        sys_clk_freq   = args.sys_clk_freq,
        with_xadc      = args.with_xadc,
        with_dna       = args.with_dna,
        with_ethernet  = args.with_ethernet,
        with_etherbone = args.with_etherbone,
        eth_ip         = args.eth_ip,
        remote_ip      = args.remote_ip,
        eth_dynamic_ip = args.eth_dynamic_ip,
        with_buttons   = True,
        with_gpio      = args.with_gpio,
        with_pcie      = args.with_pcie,
        with_video_colorbars   = args.with_video_colorbars,
        with_video_framebuffer = args.with_video_framebuffer,
        with_video_terminal    = args.with_video_terminal,
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
        prog.flash(0, builder.get_bitstream_filename(mode="flash"))

if __name__ == "__main__":
    main()
