#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Andrew Elbert Wilson <Andrew.E.Wilson@ieee.org>
# SPDX-License-Identifier: BSD-2-Clause

import os

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex_boards.platforms import opalkelly_xem8320

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.video import VideoDVIPHY
from litedram.modules import MT40A512M16
from litedram.phy import usddrphy



# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_sys    = ClockDomain()
        self.clock_domains.cd_sys4x  = ClockDomain()
        self.clock_domains.cd_idelay = ClockDomain()
        self.clock_domains.cd_hdmi      = ClockDomain()
        self.clock_domains.cd_hdmi5x    = ClockDomain()

        # # #
        clk100 = platform.request("ddr_clk100")

        self.submodules.pll = pll = USMMCM(speedgrade=-2)
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk100, 100e6)
        pll.create_clkout(self.cd_sys,       sys_clk_freq, with_reset=False)
        pll.create_clkout(self.cd_sys4x,     4*sys_clk_freq) #500
        pll.create_clkout(self.cd_hdmi,   25e6)
        pll.create_clkout(self.cd_hdmi5x, 5*25e6)

        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        # #option for second MMCM for video clocks
        # self.submodules.video_pll = video_pll = USMMCM(speedgrade=-2)
        # video_pll.reset.eq(self.rst)
        # video_pll.register_clkin(self.cd_sys.clk, sys_clk_freq)
        # video_pll.create_clkout(self.cd_hdmi,   25e6)
        # video_pll.create_clkout(self.cd_hdmi5x, 5*25e6)

        self.submodules.idelayctrl = USIDELAYCTRL(cd_ref=self.cd_sys4x, cd_sys=self.cd_sys)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(125e6), with_ethernet=False, with_etherbone=False,
                 eth_ip="192.168.1.50", with_led_chaser=True,
                 **kwargs):
        platform = opalkelly_xem8320.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        kwargs["uart_name"] = "jtag_uart"

        # TODO: add okHost FrontPanel API for UART, Data streaing, and Debug

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on xem8320", **kwargs)

        # DDR4 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.submodules.ddrphy = usddrphy.USPDDRPHY(platform.request("ddram"),
                memtype          = "DDR4",
                sys_clk_freq     = sys_clk_freq,
                iodelay_clk_freq = 500e6)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT40A512M16(sys_clk_freq, "1:4"),
                size          = 0x40000000,
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # TODO: add SFP+ cages for ethernet
        # Ethernet / Etherbone ---------------------------------------------------------------------
        # if with_ethernet or with_etherbone:
        #     self.submodules.ethphy = KU_1000BASEX(self.crg.cd_eth.clk,
        #         data_pads    = self.platform.request("sfp", 0),
        #         sys_clk_freq = self.clk_freq)
        #     self.comb += self.platform.request("sfp_tx_disable_n", 0).eq(1)
        #     self.platform.add_platform_command("set_property SEVERITY {{Warning}} [get_drc_checks REQP-1753]")
        #     if with_ethernet:
        #         self.add_ethernet(phy=self.ethphy)
        #     if with_etherbone:
        #         self.add_etherbone(phy=self.ethphy, ip_address=eth_ip)

        platform.add_extension(opalkelly_xem8320._dvi_pmod_io)
        self.submodules.videophy = VideoDVIPHY(platform.request("dvi"), clock_domain="hdmi")
        self.add_video_framebuffer(phy=self.videophy, timings="640x480@75Hz", clock_domain="hdmi")
      

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on XEM8320")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",           action="store_true",    help="Build design.")
    target_group.add_argument("--load",            action="store_true",    help="Load bitstream.")
    target_group.add_argument("--sys-clk-freq",    default=125e6,          help="System clock frequency.")
    #ethopts = target_group.add_mutually_exclusive_group()
    #ethopts.add_argument("--with-ethernet",  action="store_true",          help="Enable Ethernet support.")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq   = int(float(args.sys_clk_freq)),
        #with_ethernet  = args.with_ethernet,
        #with_etherbone = args.with_etherbone,
        #eth_ip         = args.eth_ip,
        #with_pcie      = args.with_pcie,
        #with_sata      = args.with_sata,
        **soc_core_argdict(args)
	)

    soc.platform.add_extension(opalkelly_xem8320._sdcard_pmod_io)
    soc.add_spi_sdcard()

    builder = Builder(soc, **builder_argdict(args))
    if args.build:
        builder.build()

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))
        # TODO: add option for FrontPanel Programming

if __name__ == "__main__":
    main()
