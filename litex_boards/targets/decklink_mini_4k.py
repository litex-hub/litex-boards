#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

import os
import argparse

from migen import *

from litex_boards.platforms import mini_4k
from litex.build.xilinx.vivado import vivado_build_args, vivado_build_argdict

from litex.soc.cores.clock import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.video import VideoS7GTPHDMIPHY

from litedram.modules import MT41K128M16
from litedram.phy import s7ddrphy

from litepcie.phy.s7pciephy import S7PCIEPHY
from litepcie.software import generate_litepcie_software

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_sys       = ClockDomain()
        self.clock_domains.cd_sys4x     = ClockDomain(reset_less=True)
        self.clock_domains.cd_sys4x_dqs = ClockDomain(reset_less=True)
        self.clock_domains.cd_idelay    = ClockDomain()
        self.clock_domains.cd_hdmi      = ClockDomain()

        # # #

        self.submodules.pll = pll = S7PLL(speedgrade=-1)
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(platform.request("clk100"), 100e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        pll.create_clkout(self.cd_sys4x,     4*sys_clk_freq)
        pll.create_clkout(self.cd_sys4x_dqs, 4*sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_idelay,    200e6, margin=1e-1)   # FIXME: Re-arrange clocking.
        pll.create_clkout(self.cd_hdmi,      148.5e6, margin=2e-2) # FIXME: Use a second PLL or move to clkout0 that has fractional support.
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        self.submodules.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

        platform.add_platform_command("set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets clk100_IBUF]")

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCMini):
    def __init__(self, sys_clk_freq=int(100e6), with_pcie=False, with_video_terminal=False, with_video_framebuffer=False, **kwargs):
        if with_video_terminal or with_video_framebuffer:
            sys_clk_freq = int(148.5e6) # FIXME: For now requires sys_clk >= video_clk.
        platform = mini_4k.Platform()

        # SoCCore ----------------------------------------------------------------------------------
        kwargs["uart_name"] = "jtag_uart"
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident          = "LiteX SoC on Blackmagic Decklink Mini 4K",
            ident_version  = True,
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.submodules.ddrphy = s7ddrphy.A7DDRPHY(platform.request("ddram"),
                memtype        = "DDR3",
                nphases        = 4,
                sys_clk_freq   = sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT41K128M16(sys_clk_freq, "1:4"),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # PCIe -------------------------------------------------------------------------------------
        if with_pcie:
            self.submodules.pcie_phy = S7PCIEPHY(platform, platform.request("pcie_x4"),
                data_width = 128,
                bar0_size  = 0x20000)
            self.add_pcie(phy=self.pcie_phy, ndmas=1)

        # Video ------------------------------------------------------------------------------------
        if with_video_terminal or with_video_framebuffer:
            self.submodules.videophy = VideoS7GTPHDMIPHY(platform.request("hdmi_out"),
                sys_clk_freq = sys_clk_freq,
                clock_domain = "hdmi"
            )
            if with_video_terminal:
                self.add_video_terminal(phy=self.videophy, timings="1920x1080@60Hz", clock_domain="hdmi")
            if with_video_framebuffer:
                self.add_video_framebuffer(phy=self.videophy, timings="1920x1080@60Hz", clock_domain="hdmi")
            platform.add_platform_command("set_property SEVERITY {{Warning}} [get_drc_checks REQP-49]") # FIXME: Use GTP refclk.

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC Blackmagic Decklink Mini 4K.")
    parser.add_argument("--build",                  action="store_true", help="Build bitstream")
    parser.add_argument("--load",                   action="store_true", help="Load bitstream")
    parser.add_argument("--sys-clk-freq",           default=148.5e6,       help="System clock frequency (default: 100MHz)")
    parser.add_argument("--with-pcie",              action="store_true", help="Enable PCIe support")
    parser.add_argument("--driver",                 action="store_true", help="Generate PCIe driver")
    viopts = parser.add_mutually_exclusive_group()
    viopts.add_argument("--with-video-terminal",    action="store_true", help="Enable Video Terminal (HDMI)")
    viopts.add_argument("--with-video-framebuffer", action="store_true", help="Enable Video Framebuffer (HDMI)")
    builder_args(parser)
    soc_core_args(parser)
    vivado_build_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq           = int(float(args.sys_clk_freq)),
        with_pcie              = args.with_pcie,
        with_video_terminal    = args.with_video_terminal,
        with_video_framebuffer = args.with_video_framebuffer,
        **soc_core_argdict(args)
    )
    builder = Builder(soc, **builder_argdict(args))
    builder_kwargs = vivado_build_argdict(args)
    builder.build(**builder_kwargs, run=args.build)

    if args.driver:
        generate_litepcie_software(soc, os.path.join(builder.output_dir, "driver"))

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".bit"))

if __name__ == "__main__":
    main()
