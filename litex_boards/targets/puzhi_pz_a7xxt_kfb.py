#!/usr/bin/env python3
#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 Denis Bodor <lefinnois@lefinnois.net>
# SPDX-License-Identifier: BSD-2-Clause
#
# PZ-A775T-KFB : https://www.puzhi.com/en/detail/442.html
# Also available with XC7A35T, XC7A75T, XC7A100T, or XC7A200T core module, the PCIe card is always the same.

from migen import *
from litex.gen import *

from litex_boards.platforms import puzhi_pz_a7xxt_kfb

from litex.soc.cores.clock import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.video import VideoS7HDMIPHY
from litex.soc.cores.led import LedChaser

from litedram.modules import MT41K256M16
from litedram.phy import s7ddrphy

from liteeth.phy.a7_gtp import QPLLSettings, QPLL
from liteeth.phy.s7rgmii import LiteEthPHYRGMII

from litepcie.phy.s7pciephy import S7PCIEPHY
from litepcie.software import generate_litepcie_software

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, toolchain="vivado"):
        self.rst          = Signal()
        self.cd_sys       = ClockDomain()
        self.cd_sys4x     = ClockDomain()
        self.cd_sys4x_dqs = ClockDomain()
        self.cd_idelay    = ClockDomain()
        self.cd_hdmi      = ClockDomain()
        self.cd_hdmi5x    = ClockDomain()

        # Clk/Rst
        clk200 = platform.request("clk200")
        rst    = ~platform.request("cpu_reset")

        # PLL
        if toolchain == "vivado":
            self.pll = pll = S7MMCM(speedgrade=-2)
        else:
            self.pll = pll = S7PLL(speedgrade=-2)
        self.comb += pll.reset.eq(rst | self.rst)
        pll.register_clkin(clk200,           200e6)
        pll.create_clkout(self.cd_sys,       sys_clk_freq)
        pll.create_clkout(self.cd_sys4x,     4*sys_clk_freq)
        pll.create_clkout(self.cd_sys4x_dqs, 4*sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_idelay,    200e6)
        pll.create_clkout(self.cd_hdmi,      40e6)
        pll.create_clkout(self.cd_hdmi5x,    5*40e6)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst

        self.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, toolchain="vivado", kgates=75, sys_clk_freq=100e6,
        with_led_chaser        = True,
        with_pcie              = False,
        pcie_lanes             = 2,
        with_i2c               = False,
        with_ethernet          = False,
        with_etherbone         = False,
        eth_phy                = 0,
        eth_ip                 = "192.168.1.50",
        remote_ip              = None,
        eth_dynamic_ip         = False,
        with_hdmi              = False,
        hdmi_port              = 0,
        with_video_terminal    = False,
        with_video_framebuffer = False,
        with_video_colorbars   = False,
        **kwargs):
        platform = puzhi_pz_a7xxt_kfb.Platform(kgates=kgates, toolchain=toolchain)

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, toolchain)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Puzhi PZ-A7{kgates}T-KFB", **kwargs)

        # PCIe -------------------------------------------------------------------------------------  targets/ocp_tap_timecard
        if with_pcie:
            if pcie_lanes == 2:
                self.pcie_phy = S7PCIEPHY(platform, platform.request("pcie_x2"),
                    data_width = 64,
                    bar0_size  = 0x20000)
                platform.toolchain.pre_placement_commands.append("reset_property LOC [get_cells -hierarchical -filter {{NAME=~*gtp_channel.gtpe2_channel_i}}]")
                platform.toolchain.pre_placement_commands.append("set_property LOC GTPE2_CHANNEL_X0Y5 [get_cells -hierarchical -filter {{NAME=~pcie_s7/*pipe_lane[0].gt_wrapper_i/gtp_channel.gtpe2_channel_i}}]")
                platform.toolchain.pre_placement_commands.append("set_property LOC GTPE2_CHANNEL_X0Y6 [get_cells -hierarchical -filter {{NAME=~pcie_s7/*pipe_lane[1].gt_wrapper_i/gtp_channel.gtpe2_channel_i}}]")
            else:
                self.pcie_phy = S7PCIEPHY(platform, platform.request("pcie_x1"),
                    data_width = 64,
                    bar0_size  = 0x20000)
                platform.toolchain.pre_placement_commands.append("reset_property LOC [get_cells -hierarchical -filter {{NAME=~*gtp_channel.gtpe2_channel_i}}]")
                platform.toolchain.pre_placement_commands.append("set_property LOC GTPE2_CHANNEL_X0Y5 [get_cells -hierarchical -filter {{NAME=~*gtp_channel.gtpe2_channel_i}}]")

            self.add_pcie(phy=self.pcie_phy, ndmas=1)

            # ICAP (For FPGA reload over PCIe).
            from litex.soc.cores.icap import ICAP
            self.icap = ICAP()
            self.icap.add_reload()
            self.icap.add_timing_constraints(platform, sys_clk_freq, self.crg.cd_sys.clk)

            # Flash (For SPIFlash update over PCIe).
            from litex.soc.cores.gpio import GPIOOut
            from litex.soc.cores.spi_flash import S7SPIFlash
            self.flash_cs_n = GPIOOut(platform.request("flash_cs_n"))
            self.flash      = S7SPIFlash(platform.request("flash"), sys_clk_freq, 25e6)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.ddrphy = s7ddrphy.A7DDRPHY(
                platform.request("ddram"),
                memtype        = "DDR3",
                nphases        = 4,
                sys_clk_freq   = sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT41K256M16(sys_clk_freq, "1:4"),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

        # I2C / AT24C64 ----------------------------------------------------------------------------
        if with_i2c:
            from litex.soc.cores.bitbang import I2CMaster
            self.i2c = I2CMaster(platform.request("i2c"))
            self.add_csr("i2c")

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            self.ethphy = LiteEthPHYRGMII(
                clock_pads = self.platform.request("eth_clocks", eth_phy),
                pads       = self.platform.request("eth", eth_phy),
                tx_delay   = 1.417e-9,
                rx_delay   = 1.417e-9,
            )
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, ip_address=eth_ip, with_ethmac=with_ethernet)
            elif with_ethernet:
                self.add_ethernet(phy=self.ethphy, dynamic_ip=eth_dynamic_ip, local_ip=eth_ip, remote_ip=remote_ip)

        # HDMI -------------------------------------------------------------------------------------
        if with_hdmi and (with_video_colorbars or with_video_framebuffer or with_video_terminal):
            self.videophy = VideoS7HDMIPHY(platform.request("hdmi_out", hdmi_port), clock_domain="hdmi")
            if with_video_colorbars:
                self.add_video_colorbars(phy=self.videophy, timings="640x480@60Hz", clock_domain="hdmi")
            if with_video_terminal:
                self.add_video_terminal(phy=self.videophy, timings="640x480@60Hz", clock_domain="hdmi")
            if with_video_framebuffer:
                self.add_video_framebuffer(phy=self.videophy, timings="640x480@60Hz", clock_domain="hdmi")

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=puzhi_pz_a7xxt_kfb.Platform, description="LiteX SoC on Puzhi PZ-A7xxT-KFB")
    parser.add_target_argument("--kgates",          default=75,   type=int,    help="Number of kgates. Allowed values: 35, 75, 100, 200, representing XC7A35T, XC7A75T, XC7A100T and XC7A200T")
    parser.add_target_argument("--flash",           action="store_true",       help="Flash bitstream.")
    parser.add_target_argument("--sys-clk-freq",    default=100e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-pcie",       action="store_true",       help="Enable PCIe support.")
    parser.add_target_argument("--pcie-lanes",      default=2, type=int,       help="Number of PCIe lanes (1 or 2).")
    parser.add_target_argument("--driver",          action="store_true",       help="Generate PCIe driver.")
    sdopts = parser.target_group.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-sdcard",        action="store_true",       help="Enable SPI-mode SDCard support.")
    sdopts.add_argument("--with-sdcard",            action="store_true",       help="Enable SDCard support.")
    parser.add_target_argument("--with-i2c",        action="store_true",       help="Enable I2C support.")
    parser.add_target_argument("--with-ethernet",   action="store_true",       help="Enable Ethernet support.")
    parser.add_target_argument("--with-etherbone",  action="store_true",       help="Enable Etherbone support.")
    parser.add_target_argument("--eth-phy",         default=0, type=int,       help="Ethernet PHY (0 or 1).")
    parser.add_target_argument("--eth-ip",          default="192.168.1.50",    help="Ethernet/Etherbone IP address.")
    parser.add_target_argument("--remote-ip",       default="192.168.1.100",   help="Remote IP address of TFTP server.")
    parser.add_target_argument("--eth-dynamic-ip",  action="store_true",       help="Enable dynamic Ethernet IP addresses setting.")
    parser.add_argument("--with-hdmi",              action="store_true",       help="Enable HDMI")
    parser.add_target_argument("--hdmi-port",       default=0, type=int,       help="Ethernet PHY (0 or 1).")
    viopts = parser.target_group.add_mutually_exclusive_group()
    viopts.add_argument("--with-video-terminal",    action="store_true",       help="Enable Video Terminal (HDMI).")
    viopts.add_argument("--with-video-framebuffer", action="store_true",       help="Enable Video Framebuffer (HDMI).")
    viopts.add_argument("--with-video-colorbars",   action="store_true",       help="Enable Video Colorbars (HDMI).")
    args = parser.parse_args()

    soc = BaseSoC(
        toolchain              = args.toolchain,
        kgates                 = args.kgates,
        sys_clk_freq           = args.sys_clk_freq,
        with_pcie              = args.with_pcie,
        pcie_lanes             = args.pcie_lanes,
        with_i2c               = args.with_i2c,
        with_ethernet          = args.with_ethernet,
        with_etherbone         = args.with_etherbone,
        eth_ip                 = args.eth_ip,
        remote_ip              = args.remote_ip,
        eth_dynamic_ip         = args.eth_dynamic_ip,
        eth_phy                = args.eth_phy,
        with_hdmi              = args.with_hdmi,
        hdmi_port              = args.hdmi_port,
        with_video_terminal    = args.with_video_terminal,
        with_video_framebuffer = args.with_video_framebuffer,
        with_video_colorbars   = args.with_video_colorbars,
        **parser.soc_argdict
    )

    if args.with_spi_sdcard:
        soc.add_spi_sdcard()
    if args.with_sdcard:
        soc.add_sdcard()

    builder  = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.driver:
        generate_litepcie_software(soc, os.path.join(builder.output_dir, "driver"))

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram", ext=".bit"))

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.flash(address=0, data_file=builder.get_bitstream_filename(mode="flash", ext=".bit"), unprotect_flash=True)

if __name__ == "__main__":
    main()
