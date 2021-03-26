#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019 msloniewski <marcin.sloniewski@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

import os
import argparse

from migen import *
from litex_boards.platforms          import deca

from litex.soc.cores.clock           import Max10PLL
from litex.soc.integration.soc_core  import *
from litex.soc.integration.builder   import *
from litex.soc.cores.video           import VideoDVIPHY
from litex.soc.cores.led             import LedChaser
from litex.soc.cores.bitbang         import I2CMaster

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_sys    = ClockDomain()
        self.clock_domains.cd_hdmi   = ClockDomain()
        self.clock_domains.cd_usb    = ClockDomain()

        # # #

        # PLL
        ulpi    = platform.request("ulpi", 0)
        clk1_50 = platform.request("clk1_50")

        self.submodules.pll = pll = Max10PLL(speedgrade="-6")
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk1_50, 50e6)
        pll.create_clkout(self.cd_sys,  sys_clk_freq)
        pll.create_clkout(self.cd_hdmi, 40e6)

        self.submodules.usb_pll = pll = Max10PLL(speedgrade="-6")
        self.comb += [
            pll.reset.eq(self.rst),
            ulpi.cs.eq(1) # enable ULPI chip, which enables the ULPI clock
        ]
        pll.register_clkin(ulpi.clk, 60e6)
        # the working example from the DECA kit uses -120 degrees for the USB core's
        # and it works with the LUNA core too
        pll.create_clkout(self.cd_usb,  60e6, phase=-120)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(50e6), with_video_terminal=False, **kwargs):
        self.platform = platform = deca.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = self.crg = _CRG(platform, sys_clk_freq)

        # Leds -------------------------------------------------------------------------------------
        self.submodules.leds = LedChaser(
            pads         = platform.request_all("user_led"),
            sys_clk_freq = sys_clk_freq)

        # Defaults to UART over JTAG because no hardware uart is on the board
        if kwargs["uart_name"] == "serial":
            kwargs["uart_name"] = "jtag_atlantic"

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident               = "LiteX SoC on Terasic DECA",
            ident_version       = True,
            **kwargs)

        # Video ------------------------------------------------------------------------------------
        if with_video_terminal:
            self.submodules.videophy = VideoDVIPHY(platform.request("hdmi"), clock_domain="hdmi")
            self.add_video_terminal(phy=self.videophy, timings="800x600@60Hz", clock_domain="hdmi")

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on DECA")
    parser.add_argument("--build",               action="store_true", help="Build bitstream")
    parser.add_argument("--load",                action="store_true", help="Load bitstream")
    parser.add_argument("--debug",               action="store_true", help="generate cpu debug interface")
    parser.add_argument("--sys-clk-freq",        default=50e6,        help="System clock frequency (default: 50MHz)")
    parser.add_argument("--with-video-terminal", action="store_true", help="Enable Video Terminal (VGA)")
    parser.add_argument("--integrated-ram-size", default=0x4000,      help="Use FPGA block RAM as main RAM. Interim measure until we have DDR3 support.")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq             = int(float(args.sys_clk_freq)),
        with_video_terminal      = args.with_video_terminal,
        integrated_main_ram_size = args.integrated_ram_size,
        # use compressed instructions to save ROM
        cpu_variant              = "imac+debug" if args.debug else "imac",
        **soc_core_argdict(args)
    )
    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".sof"))

if __name__ == "__main__":
    main()
