#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

import os
import argparse

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.soc.cores.clock.gowin_gw1nsr import  GW1NSRPLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.video import *

from litex_boards.platforms import tang_nano_4k

from litehyperbus.core.hyperbus import HyperRAM

kB = 1024
mB = 1024*kB

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq, with_video_pll=False):
        self.rst = Signal()
        self.clock_domains.cd_sys = ClockDomain()

        # # #

        # Clk / Rst
        clk27 = platform.request("clk27")
        rst_n = platform.request("user_btn", 0)

        # PLL
        self.submodules.pll = pll = GW1NSRPLL(device="GW1NSR-4C")
        self.comb += pll.reset.eq(~rst_n)
        pll.register_clkin(clk27, 27e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)


        # Video PLL
        if with_video_pll:
            self.submodules.video_pll = video_pll = GW1NSRPLL(device="GW1NSR-4C")
            self.comb += video_pll.reset.eq(~rst_n)
            video_pll.register_clkin(clk27, 27e6)
            self.clock_domains.cd_hdmi   = ClockDomain()
            self.clock_domains.cd_hdmi5x = ClockDomain()
            video_pll.create_clkout(self.cd_hdmi5x, 125e6)
            self.specials += Instance("CLKDIV",
                p_DIV_MODE= "5",
                i_RESETN = rst_n,
                i_HCLKIN = self.cd_hdmi5x.clk,
                o_CLKOUT = self.cd_hdmi.clk
            )

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    mem_map = {**SoCCore.mem_map, **{"spiflash": 0x80000000}}
    def __init__(self, sys_clk_freq=int(27e6), with_hyperram=False, with_led_chaser=True, with_video_terminal=True, **kwargs):
        platform = tang_nano_4k.Platform()

        # Put BIOS in SPIFlash to save BlockRAMs.
        kwargs["integrated_rom_size"] = 0
        kwargs["cpu_reset_address"]   = self.mem_map["spiflash"] + 0

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident         = "LiteX SoC on Tang Nano 4K",
            ident_version = True,
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq, with_video_pll=with_video_terminal)

        # SPI Flash --------------------------------------------------------------------------------
        from litespi.modules import W25Q32
        from litespi.opcodes import SpiNorFlashOpCodes as Codes
        self.add_spi_flash(mode="1x", module=W25Q32(Codes.READ_1_1_1), with_master=False)

        # Add ROM linker region --------------------------------------------------------------------
        self.bus.add_region("rom", SoCRegion(
            origin = self.mem_map["spiflash"] + 0,
            size   = 64*kB,
            linker = True)
        )

        # HyperRAM ---------------------------------------------------------------------------------
        if with_hyperram:
            class HyperRAMPads:
                def __init__(self):
                    self.clk   = Signal()
                    self.rst_n = platform.request("O_hpram_reset_n")
                    self.dq    = platform.request("IO_hpram_dq")
                    self.cs_n  = platform.request("O_hpram_cs_n")
                    self.rwds  = platform.request("IO_hpram_rwds")

            hyperram_pads = HyperRAMPads()
            self.comb += platform.request("O_hpram_ck").eq(hyperram_pads.clk)
            self.comb += platform.request("O_hpram_ck_n").eq(~hyperram_pads.clk)
            self.submodules.hyperram = HyperRAM(hyperram_pads)
            self.bus.add_slave("main_ram", slave=self.hyperram.bus, region=SoCRegion(origin=0x40000000, size=8*1024*1024))

        # Video ------------------------------------------------------------------------------------
        if with_video_terminal:
            self.submodules.videophy = VideoHDMIPHY(platform.request("hdmi"), clock_domain="hdmi")
            self.add_video_colorbars(phy=self.videophy, timings="640x480@75Hz", clock_domain="hdmi")
            #self.add_video_terminal(phy=self.videophy, timings="640x480@75Hz", clock_domain="hdmi") # FIXME: Free up BRAMs.

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on Tang Nano 4K")
    parser.add_argument("--build",       action="store_true", help="Build bitstream")
    parser.add_argument("--load",        action="store_true", help="Load bitstream")
    parser.add_argument("--flash",       action="store_true", help="Flash Bitstream")
    parser.add_argument("--sys-clk-freq",default=27e6,        help="System clock frequency (default: 27MHz)")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq      = int(float(args.sys_clk_freq)),
        **soc_core_argdict(args)
    )

    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, "impl", "pnr", "project.fs"))

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.flash(0, os.path.join(builder.gateware_dir, "impl", "pnr", "project.fs"))
        prog.flash(0, "build/sipeed_tang_nano_4k/software/bios/bios.bin", external=True)

if __name__ == "__main__":
    main()
