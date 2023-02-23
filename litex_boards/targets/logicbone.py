#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Owen Kirby <oskirby@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

import os
import sys

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from litex_boards.platforms import logicbone

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litedram.modules import MT41K512M16
from litedram.phy import ECP5DDRPHY
from liteeth.phy.ecp5rgmii import LiteEthPHYRGMII

# _CRG ---------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_usb_pll=False):
        self.rst        = Signal()
        self.cd_init    = ClockDomain()
        self.cd_por     = ClockDomain()
        self.cd_sys     = ClockDomain()
        self.cd_sys2x   = ClockDomain()
        self.cd_sys2x_i = ClockDomain()

        # # #

        self.stop  = Signal()
        self.reset = Signal()

        # Clk / Rst
        clk25 = platform.request("clk25")

        # Power on reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += self.cd_por.clk.eq(clk25)
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # PLL
        sys2x_clk_ecsout = Signal()
        self.pll = pll = ECP5PLL()
        self.comb += pll.reset.eq(~por_done | self.rst)
        pll.register_clkin(clk25, 25e6)
        pll.create_clkout(self.cd_sys2x_i, 2*sys_clk_freq)
        pll.create_clkout(self.cd_init, 24e6)
        self.specials += [
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

        # USB PLL
        if with_usb_pll:
            self.cd_usb_12 = ClockDomain()
            self.cd_usb_48 = ClockDomain()
            usb_pll = ECP5PLL()
            self.submodules += usb_pll
            self.comb += usb_pll.reset.eq(~por_done | self.rst)
            usb_pll.register_clkin(clk25, 25e6)
            usb_pll.create_clkout(self.cd_usb_48, 48e6)
            usb_pll.create_clkout(self.cd_usb_12, 12e6)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, revision="rev0", device="45F", sdram_device="MT41K512M16",
        sys_clk_freq    = 75e6,
        with_ethernet   = False,
        with_led_chaser = True,
        toolchain       = "trellis",
        **kwargs):
        platform = logicbone.Platform(revision=revision, device=device ,toolchain=toolchain)

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, with_usb_pll=True)

        # SoCCore ----------------------------------------------------------------------------------
        # Defaults to USB ACM through ValentyUSB.
        kwargs["uart_name"] = "usb_acm"
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Logicbone", **kwargs)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            available_sdram_modules = {
                "MT41K512M16":  MT41K512M16,
                #"AS4C1GM8":    AS4C1GM8, ## Too many rows, seems to break things.
            }
            sdram_module = available_sdram_modules.get(sdram_device)

            self.ddrphy = ECP5DDRPHY(
                platform.request("ddram"),
                sys_clk_freq=sys_clk_freq)
            self.comb += self.crg.stop.eq(self.ddrphy.init.stop)
            self.comb += self.crg.reset.eq(self.ddrphy.init.reset)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = sdram_module(sys_clk_freq, "1:2"),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Ethernet ---------------------------------------------------------------------------------
        if with_ethernet:
            self.ethphy = LiteEthPHYRGMII(
                clock_pads = self.platform.request("eth_clocks"),
                pads       = self.platform.request("eth"))
            self.add_ethernet(phy=self.ethphy)


        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=logicbone.Platform, description="LiteX SoC on Logicbone.")
    parser.add_target_argument("--sys-clk-freq",   default=75e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--device",         default="45F",            help="FPGA device (45F or 85F).")
    parser.add_target_argument("--sdram-device",   default="MT41K512M16",    help="SDRAM device (MT41K512M16).")
    parser.add_target_argument("--with-ethernet",  action="store_true",      help="Enable Ethernet support.")
    parser.add_target_argument("--with-sdcard",    action="store_true",      help="Enable SDCard support.")
    args = parser.parse_args()

    soc = BaseSoC(
        toolchain     = args.toolchain,
        device        = args.device,
        sys_clk_freq  = args.sys_clk_freq,
        sdram_device  = args.sdram_device,
        with_ethernet = args.with_ethernet,
        **parser.soc_argdict
    )
    if args.with_sdcard:
        soc.add_sdcard()
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
