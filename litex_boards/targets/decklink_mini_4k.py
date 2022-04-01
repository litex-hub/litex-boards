#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# Build/Use:
# ./decklink_mini_4k.py --build --load
# litex_term jtag --jtag-config=openocd_xc7_ft232.cfg

import os

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
        self.clock_domains.cd_sys4x     = ClockDomain()
        self.clock_domains.cd_sys4x_dqs = ClockDomain()
        self.clock_domains.cd_idelay    = ClockDomain()
        self.clock_domains.cd_hdmi      = ClockDomain()

        # # #

        # Clk.
        clk100 = platform.request("clk100")
        platform.add_platform_command("set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets clk100_IBUF]")
        platform.add_platform_command("set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets main_s7pll0_clkin]")

        # Main PLL.
        self.submodules.pll = pll = S7PLL(speedgrade=-1)
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk100, 100e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        pll.create_clkout(self.cd_sys4x,     4*sys_clk_freq)
        pll.create_clkout(self.cd_sys4x_dqs, 4*sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_idelay,    200e6, margin=1e-1)   # FIXME: Re-arrange clocking.
        pll.create_clkout(self.cd_hdmi,      148.5e6, margin=2e-2) # FIXME: Use a second PLL or move to clkout0 that has fractional support.
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        # IDELAY Ctrl.
        self.submodules.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

        # SATA PLL.
        self.clock_domains.cd_sata_refclk = ClockDomain()
        self.submodules.sata_pll = sata_pll = S7PLL(speedgrade=-1)
        self.comb += sata_pll.reset.eq(self.rst)
        sata_pll.register_clkin(clk100, 100e6)
        sata_pll.create_clkout(self.cd_sata_refclk, 150e6)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCMini):
    def __init__(self, sys_clk_freq=int(100e6), with_pcie=False, with_sata=False, with_video_terminal=False, with_video_framebuffer=False, **kwargs):
        if with_video_terminal or with_video_framebuffer:
            sys_clk_freq = int(148.5e6) # FIXME: For now requires sys_clk >= video_clk.
        platform = mini_4k.Platform()

        # SoCCore ----------------------------------------------------------------------------------
        kwargs["uart_name"] = "jtag_uart"
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident = "LiteX SoC on Blackmagic Decklink Mini 4K",
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

        # SATA -------------------------------------------------------------------------------------
        if with_sata:
            from litex.build.generic_platform import Subsignal, Pins
            from litesata.phy import LiteSATAPHY

            # IOs
            _sata_io = [
                 # PCIe 2 SATA Custom Adapter (With PCIe Riser / SATA cable mod).
                ("pcie2sata", 0,
                    Subsignal("tx_p",  Pins("B7")),
                    Subsignal("tx_n",  Pins("A7")),
                    Subsignal("rx_p",  Pins("B11")),
                    Subsignal("rx_n",  Pins("A11")),
                ),
            ]
            platform.add_extension(_sata_io)

            # RefClk, Generate 150MHz from PLL.
            platform.add_platform_command("set_property SEVERITY {{Warning}} [get_drc_checks REQP-49]")

            # PHY
            self.submodules.sata_phy = LiteSATAPHY(platform.device,
                refclk     = ClockSignal("sata_refclk"),
                pads       = platform.request("pcie2sata"),
                gen        = "gen2",
                clk_freq   = sys_clk_freq,
                data_width = 16)

            # Core
            self.add_sata(phy=self.sata_phy, mode="read+write")
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
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC Blackmagic Decklink Mini 4K")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",                  action="store_true", help="Build bitstream.")
    target_group.add_argument("--load",                   action="store_true", help="Load bitstream.")
    target_group.add_argument("--sys-clk-freq",           default=148.5e6,     help="System clock frequency.")
    pcieopts = target_group.add_mutually_exclusive_group()
    pcieopts.add_argument("--with-pcie",            action="store_true", help="Enable PCIe support.")
    target_group.add_argument("--driver",                 action="store_true", help="Generate PCIe driver.")
    viopts = target_group.add_mutually_exclusive_group()
    viopts.add_argument("--with-video-terminal",    action="store_true", help="Enable Video Terminal (HDMI).")
    viopts.add_argument("--with-video-framebuffer", action="store_true", help="Enable Video Framebuffer (HDMI).")
    pcieopts.add_argument("--with-sata",            action="store_true", help="Enable SATA support (over PCIe2SATA).")
    builder_args(parser)
    soc_core_args(parser)
    vivado_build_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq           = int(float(args.sys_clk_freq)),
        with_pcie              = args.with_pcie,
        with_sata              = args.with_sata,
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
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
