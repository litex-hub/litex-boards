#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019 Arnaud Durand <arnaud.durand@unifr.ch>
# Copyright (c) 2022 Martin Hubacek @hubmartin (Twitter)
# Copyright (c) 2022 Raptor Engineering, LLC
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from litex_boards.platforms import rcs_arctic_tern_bmc_card

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.integration.soc import SoCRegion

from litedram.modules import MT41J256M16
from litedram.phy import ECP5DDRPHY
from liteeth.phy.ecp5rgmii import LiteEthPHYRGMII
from litex.soc.cores.video import VideoGenericPHY

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst         = Signal()
        self.cd_init     = ClockDomain()
        self.cd_por      = ClockDomain()
        self.cd_sys      = ClockDomain()
        self.cd_sys2x    = ClockDomain()
        self.cd_sys2x_i  = ClockDomain()
        self.cd_sys2x_eb = ClockDomain()
        self.cd_dvo      = ClockDomain()

        # # #
        self.stop  = Signal()
        self.reset = Signal()

        # Clk / Rst
        clk125 = platform.request("clk125")
        rst_n  = platform.request("rst_n")

        self.clk_inv_alignwd = Signal()
        self.sys_inv_clk_bridge = Signal()
        self.sys_inv_clk_syncb = Signal()

        # Power on reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # PLL
        sys2x_clk_ecsout = Signal()
        self.pll = pll = ECP5PLL()
        self.comb += pll.reset.eq(~por_done | ~rst_n | self.rst)
        pll.register_clkin(clk125, 125e6)
        pll.create_clkout(self.cd_sys2x_i, 2*sys_clk_freq)
        pll.create_clkout(self.cd_init, 24e6)
        self.specials += [
            Instance("OSCG",
                p_DIV = 128,                # 2.4MHz
                o_OSC = self.cd_por.clk),
            Instance("ECLKBRIDGECS",
                i_CLK0   = self.cd_sys2x_i.clk,
                i_SEL    = 0,
                o_ECSOUT = sys2x_clk_ecsout),
            Instance("ECLKSYNCB",
                i_ECLKI = sys2x_clk_ecsout,
                i_STOP  = self.stop,
                o_ECLKO = self.cd_sys2x.clk),
            Instance("CLKDIVF",
                p_DIV     = "2.0",
                i_ALIGNWD = 0,
                i_CLKI    = self.cd_sys2x.clk,
                i_RST     = self.reset,
                o_CDIVX   = self.cd_sys.clk),
            AsyncResetSynchronizer(self.cd_sys, ~pll.locked | self.reset),
        ]

        # Generate DVO clock
        pll.create_clkout(self.cd_dvo, 40e6)            # 800x600@60
        #pll.create_clkout(self.cd_dvo, 148.35e6)       # 1920x1080@60
        #pll.create_clkout(self.cd_dvo, 148.2e6)        # 1920x1200@60


# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=50e6, toolchain="trellis",
        with_video_colorbars   = False,
        with_video_terminal    = True,
        with_video_framebuffer = False,
        with_ethernet          = False,
        with_etherbone         = False,
        eth_ip                 = "192.168.1.50",
        **kwargs):
        platform = rcs_arctic_tern_bmc_card.Platform(toolchain=toolchain)

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, irq_n_irqs=16, clk_freq=sys_clk_freq,
            ident = "LiteX SoC on Arctic Tern (BMC card carrier)",
            **kwargs
        )

        # DDR3 SDRAM -------------------------------------------------------------------------------
        self.ddrphy = ECP5DDRPHY(
            platform.request("ddram"),
            sys_clk_freq=sys_clk_freq)
        self.comb += self.crg.stop.eq(self.ddrphy.init.stop)
        self.comb += self.crg.reset.eq(self.ddrphy.init.reset)
        self.add_sdram("sdram",
            phy           = self.ddrphy,
            module        = MT41J256M16(sys_clk_freq, "1:2"), # Not MT41J256M16, but the AS4C256M16D3C in use has similar specifications
            l2_cache_size = kwargs.get("l2_size", 8192),
        )

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            self.ethphy = LiteEthPHYRGMII(
                clock_pads = self.platform.request("eth_clocks", 0),
                pads       = self.platform.request("eth", 0),
                tx_delay   = 0e-9,
                rx_delay   = 0e-9)
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy)
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, ip_address=eth_ip)

        # Video Output -----------------------------------------------------------------------------
        if with_video_colorbars or with_video_terminal or with_video_framebuffer:
            dvo_pads = platform.request("dvo")
            self.videophy = VideoGenericPHY(dvo_pads, clock_domain="dvo", with_clk_ddr_output=False)
            if with_video_terminal:
                #self.add_video_terminal(phy=self.videophy, timings="1920x1080@60Hz", clock_domain="dvo")
                #self.add_video_terminal(phy=self.videophy, timings="1920x1200@60Hz", clock_domain="dvo")
                self.add_video_terminal(phy=self.videophy, timings="800x600@60Hz", clock_domain="dvo")
            elif with_video_framebuffer:
                #self.add_video_framebuffer(phy=self.videophy, timings="1920x1080@60Hz", clock_domain="dvo")
                #self.add_video_framebuffer(phy=self.videophy, timings="1920x1200@60Hz", clock_domain="dvo")
                self.add_video_framebuffer(phy=self.videophy, timings="800x600@60Hz", clock_domain="dvo")
            else:
                self.add_video_colorbars(phy=self.videophy, timings="800x600@60Hz", clock_domain="dvo")

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=rcs_arctic_tern_bmc_card.Platform, description="LiteX SoC on Arctic Tern (BMC card carrier).")
    parser.add_target_argument("--sys-clk-freq", default=60e6, type=float, help="System clock frequency (default: 60MHz).")
    ethopts = parser.target_group.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",  action="store_true",    help="Enable Ethernet support.")
    ethopts.add_argument("--with-etherbone", action="store_true",    help="Enable Etherbone support.")
    parser.add_target_argument("--eth-ip",   default="192.168.1.50", help="Ethernet/Etherbone IP address.")
    args = parser.parse_args()

    soc = BaseSoC(
        toolchain      = args.toolchain,
        sys_clk_freq   = args.sys_clk_freq,
        with_ethernet  = args.with_ethernet,
        with_etherbone = args.with_etherbone,
        eth_ip         = args.eth_ip,
        **parser.soc_argdict)
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram", ext=".svf")) # FIXME

if __name__ == "__main__":
    main()
