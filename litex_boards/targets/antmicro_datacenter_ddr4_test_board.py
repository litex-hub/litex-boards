#!/usr/bin/env python3
#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Antmicro <www.antmicro.com>
# SPDX-License-Identifier: BSD-2-Clause

import os
import math
import json

from migen import *

from litex.gen import *

from litex_boards.platforms import antmicro_datacenter_ddr4_test_board

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.bitbang import I2CMaster
from litex.soc.cores.video import VideoS7HDMIPHY

from litedram.modules import MTA18ASF2G72PZ
from litedram.phy.s7ddrphy import A7DDRPHY
from litedram.init import get_sdram_phy_py_header
from litedram.core.controller import ControllerSettings
from litedram.common import PhySettings, GeomSettings, TimingSettings

from liteeth.phy import LiteEthS7PHYRGMII
from litex.soc.cores.hyperbus import HyperRAM

from litespi.modules import S25FL128S0
from litespi.opcodes import SpiNorFlashOpCodes as Codes

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, iodelay_clk_freq, with_video_pll=False):
        self.rst          = Signal()
        self.cd_sys       = ClockDomain()
        self.cd_sys2x     = ClockDomain()
        self.cd_sys4x     = ClockDomain()
        self.cd_sys4x_dqs = ClockDomain()
        self.cd_idelay    = ClockDomain()

        self.cd_hdmi      = ClockDomain()
        self.cd_hdmi5x    = ClockDomain()

        # # #

        # Clk.
        clk100 = platform.request("clk100")

        self.pll = pll = S7PLL(speedgrade=-1)
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk100, 100e6)
        pll.create_clkout(self.cd_sys,       sys_clk_freq)
        pll.create_clkout(self.cd_sys2x,     2 * sys_clk_freq)
        pll.create_clkout(self.cd_sys4x,     4 * sys_clk_freq)
        pll.create_clkout(self.cd_sys4x_dqs, 4 * sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_idelay,    iodelay_clk_freq)

        self.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

        # Video PLL.
        if with_video_pll:
            self.video_pll = video_pll = S7MMCM(speedgrade=-1)
            self.comb += video_pll.reset.eq(self.rst)
            video_pll.register_clkin(clk100, 100e6)
            video_pll.create_clkout(self.cd_hdmi,   40e6)
            video_pll.create_clkout(self.cd_hdmi5x, 5*40e6)


# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, *, sys_clk_freq=100e6, iodelay_clk_freq=200e6,
            with_ethernet          = False,
            with_etherbone         = False,
            eth_ip                 = "192.168.1.50",
            eth_reset_time         = "10e-3",
            eth_dynamic_ip         = False,
            with_hyperram          = False,
            with_sdcard            = False,
            with_jtagbone          = True,
            with_uartbone          = False,
            with_spi_flash         = False,
            with_led_chaser        = True,
            with_video_terminal    = False,
            with_video_framebuffer = False,
            **kwargs):
        platform = antmicro_datacenter_ddr4_test_board.Platform()

        # CRG --------------------------------------------------------------------------------------
        with_video_pll = (with_video_terminal or with_video_framebuffer)
        self.crg = _CRG(platform, sys_clk_freq, iodelay_clk_freq=iodelay_clk_freq, with_video_pll=with_video_pll)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on data center test board", **kwargs)

        # DDR4 SDRAM RDIMM -------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.ddrphy = A7DDRPHY(platform.request("ddr4"),
                memtype         = "DDR4",
                iodelay_clk_freq = iodelay_clk_freq,
                sys_clk_freq     = sys_clk_freq,
                is_rdimm         = True,
            )
            self.add_sdram("sdram",
                phy                     = self.ddrphy,
                module                  = MTA18ASF2G72PZ(sys_clk_freq, "1:4"),
                l2_cache_size           = kwargs.get("l2_size", 8192),
                l2_cache_min_data_width = 256,
                size                    = 0x40000000,
            )

        # HyperRAM ---------------------------------------------------------------------------------
        if with_hyperram:
            self.hyperram = HyperRAM(platform.request("hyperram"), sys_clk_freq=sys_clk_freq)
            self.bus.add_slave("hyperram", slave=self.hyperram.bus, region=SoCRegion(origin=0x20000000, size=8*1024*1024))

        # SD Card ----------------------------------------------------------------------------------
        if with_sdcard:
            self.add_sdcard()

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            # Traces between PHY and FPGA introduce ignorable delays of ~0.165ns +/- 0.015ns.
            # PHY chip does not introduce delays on TX (FPGA->PHY), however it includes 1.2ns
            # delay for RX CLK so we only need 0.8ns to match the desired 2ns.
            self.ethphy = LiteEthS7PHYRGMII(
                clock_pads = self.platform.request("eth_clocks"),
                pads       = self.platform.request("eth"),
                rx_delay   = 0.8e-9,
                hw_reset_cycles = math.ceil(float(eth_reset_time) * self.sys_clk_freq)
            )
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy, dynamic_ip=eth_dynamic_ip)
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, ip_address=eth_ip)

        # UartBone ---------------------------------------------------------------------------------
        if with_uartbone:
            self.add_uartbone(baudrate=1e6)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

        # Video ------------------------------------------------------------------------------------
        if with_video_terminal or with_video_framebuffer:
            self.videophy = VideoS7HDMIPHY(platform.request("hdmi_out"), clock_domain="hdmi")
            if with_video_terminal:
                self.add_video_terminal(phy=self.videophy, timings="800x600@60Hz", clock_domain="hdmi")
            if with_video_framebuffer:
                self.add_video_framebuffer(phy=self.videophy, timings="800x600@60Hz", clock_domain="hdmi")

        # SPI Flash --------------------------------------------------------------------------------
        if with_spi_flash:
            self.add_spi_flash(mode="4x", module=S25FL128S0(Codes.READ_1_1_4), with_master=True)

        # System I2C (behing multiplexer) ----------------------------------------------------------
        i2c_pads = platform.request('i2c')
        self.i2c = I2CMaster(i2c_pads)

    def generate_sdram_phy_py_header(self, output_file):
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        f = open(output_file, "w")
        f.write(get_sdram_phy_py_header(
            self.sdram.controller.settings.phy,
            self.sdram.controller.settings.timing))
        f.close()


# Build --------------------------------------------------------------------------------------------

class LiteDRAMSettingsEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (ControllerSettings, GeomSettings, PhySettings, TimingSettings)):
            ignored = ["self", "refresh_cls"]
            return {k: v for k, v in vars(o).items() if k not in ignored}
        elif isinstance(o, Signal) and isinstance(o.reset, Constant):
            return o.reset
        elif isinstance(o, Constant):
            return o.value
        print('o', end=' = '); __import__('pprint').pprint(o)
        return super().default(o)

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=antmicro_datacenter_ddr4_test_board.Platform, description="LiteX SoC on DDR4 Datacenter Test Board.")
    parser.add_target_argument("--flash",            action="store_true",       help="Flash bitstream.")
    parser.add_target_argument("--sys-clk-freq",     default=100e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--iodelay-clk-freq", default=200e6, type=float, help="IODELAYCTRL frequency.")
    ethopts = parser.target_group.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",                action="store_true",    help="Add Ethernet.")
    ethopts.add_argument("--with-etherbone",               action="store_true",    help="Add EtherBone.")
    parser.add_target_argument("--eth-ip",                 default="192.168.1.50", help="Ethernet/Etherbone IP address.")
    parser.add_target_argument("--eth-dynamic-ip",         action="store_true",    help="Enable dynamic Ethernet IP addresses setting.")
    parser.add_target_argument("--eth-reset-time",         default="10e-3",        help="Duration of Ethernet PHY reset.")
    parser.add_target_argument("--with-hyperram",          action="store_true",    help="Add HyperRAM.")
    parser.add_target_argument("--with-sdcard",            action="store_true",    help="Add SDCard.")
    parser.add_target_argument("--with-jtagbone",          action="store_true",    help="Add JTAGBone.")
    parser.add_target_argument("--with-uartbone",          action="store_true",    help="Add UartBone on 2nd serial.")
    parser.add_target_argument("--with-video-terminal",    action="store_true",    help="Enable Video Terminal (HDMI).")
    parser.add_target_argument("--with-video-framebuffer", action="store_true",    help="Enable Video Framebuffer (HDMI).")
    parser.add_target_argument("--with-spi-flash",         action="store_true",    help="Enable SPI Flash (MMAPed).")
    args = parser.parse_args()

    assert not (args.with_etherbone and args.eth_dynamic_ip)

    soc = BaseSoC(
        sys_clk_freq           = args.sys_clk_freq,
        iodelay_clk_freq       = args.iodelay_clk_freq,
        with_ethernet          = args.with_ethernet,
        with_etherbone         = args.with_etherbone,
        eth_ip                 = args.eth_ip,
        eth_dynamic_ip         = args.eth_dynamic_ip,
        with_hyperram          = args.with_hyperram,
        with_sdcard            = args.with_sdcard,
        with_jtagbone          = args.with_jtagbone,
        with_uartbone          = args.with_uartbone,
        with_spi_flash         = args.with_spi_flash,
        with_video_terminal    = args.with_video_terminal,
        with_video_framebuffer = args.with_video_framebuffer,
        **parser.soc_argdict)
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)
        builder.soc.generate_sdram_phy_py_header(os.path.join(builder.output_dir, "sdram_init.py"))
        # LiteDRAM settings (controller, phy, geom, timing)
        with open(os.path.join(builder.output_dir, 'litedram_settings.json'), 'w') as f:
            json.dump(builder.soc.sdram.controller.settings, f, cls=LiteDRAMSettingsEncoder, indent=4)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.flash(0, builder.get_bitstream_filename(mode="flash"))

if __name__ == "__main__":
    main()
