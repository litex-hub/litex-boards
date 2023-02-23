#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Icenowy Zheng <icenowy@aosc.io>
# SPDX-License-Identifier: BSD-2-Clause

import os
from migen import *

from litex.gen import *

from litex_boards.platforms import sipeed_tang_nano_9k

from litex.soc.cores.clock.gowin_gw1n import GW1NPLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.video import *

from litex.soc.cores.hyperbus import HyperRAM

kB = 1024
mB = 1024*kB

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_video_pll=False):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()

        # # #

        # Clk / Rst
        clk27 = platform.request("clk27")
        rst_n = platform.request("user_btn", 0)

        # PLL
        self.pll = pll = GW1NPLL(devicename=platform.devicename, device=platform.device)
        self.comb += pll.reset.eq(~rst_n)
        pll.register_clkin(clk27, 27e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)

        # Video PLL
        if with_video_pll:
            self.video_pll = video_pll = GW1NPLL(devicename=platform.devicename, device=platform.device)
            self.comb += video_pll.reset.eq(~rst_n)
            video_pll.register_clkin(clk27, 27e6)
            self.cd_hdmi   = ClockDomain()
            self.cd_hdmi5x = ClockDomain()
            video_pll.create_clkout(self.cd_hdmi5x, 125e6)
            self.specials += Instance("CLKDIV",
                p_DIV_MODE= "5",
                i_RESETN = rst_n,
                i_HCLKIN = self.cd_hdmi5x.clk,
                o_CLKOUT = self.cd_hdmi.clk
            )

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=27e6, bios_flash_offset=0x0,
        with_led_chaser     = True,
        with_video_terminal = False,
        **kwargs):
        platform = sipeed_tang_nano_9k.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, with_video_pll=with_video_terminal)

        # SoCCore ----------------------------------------------------------------------------------
        # Disable Integrated ROM
        kwargs["integrated_rom_size"] = 0
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Tang Nano 9K", **kwargs)

        # SPI Flash --------------------------------------------------------------------------------
        from litespi.modules import W25Q32
        from litespi.opcodes import SpiNorFlashOpCodes as Codes
        self.add_spi_flash(mode="1x", module=W25Q32(Codes.READ_1_1_1), with_master=False)

        # Add ROM linker region --------------------------------------------------------------------
        self.bus.add_region("rom", SoCRegion(
            origin = self.bus.regions["spiflash"].origin + bios_flash_offset,
            size   = 64*kB,
            linker = True)
        )
        self.cpu.set_reset_address(self.bus.regions["rom"].origin)

        # HyperRAM ---------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            # TODO: Use second 32Mbit PSRAM chip.
            dq      = platform.request("IO_psram_dq")
            rwds    = platform.request("IO_psram_rwds")
            reset_n = platform.request("O_psram_reset_n")
            cs_n    = platform.request("O_psram_cs_n")
            ck      = platform.request("O_psram_ck")
            ck_n    = platform.request("O_psram_ck_n")
            class HyperRAMPads:
                def __init__(self, n):
                    self.clk   = Signal()
                    self.rst_n = reset_n[n]
                    self.dq    = dq[8*n:8*(n+1)]
                    self.cs_n  = cs_n[n]
                    self.rwds  = rwds[n]

            hyperram_pads = HyperRAMPads(0)
            self.comb += ck[0].eq(hyperram_pads.clk)
            self.comb += ck_n[0].eq(~hyperram_pads.clk)
            # FIXME: Issue with upstream HyperRAM core, so use old one. Need to investigate.
            if not os.path.exists("hyperbus.py"):
                os.system("wget https://github.com/litex-hub/litex-boards/files/8831568/hyperbus.py.txt")
                os.system("mv hyperbus.py.txt hyperbus.py")
            from hyperbus import HyperRAM
            self.hyperram = HyperRAM(hyperram_pads)
            self.bus.add_slave("main_ram", slave=self.hyperram.bus, region=SoCRegion(origin=self.mem_map["main_ram"], size=4*mB))

        # Video ------------------------------------------------------------------------------------
        if with_video_terminal:
            self.videophy = VideoGowinHDMIPHY(platform.request("hdmi"), clock_domain="hdmi")
            self.add_video_colorbars(phy=self.videophy, timings="640x480@60Hz", clock_domain="hdmi")
            #self.add_video_terminal(phy=self.videophy, timings="640x480@75Hz", clock_domain="hdmi") # FIXME: Free up BRAMs.


        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=sipeed_tang_nano_9k.Platform, description="LiteX SoC on Tang Nano 9K.")
    parser.add_target_argument("--flash",                action="store_true",      help="Flash Bitstream.")
    parser.add_target_argument("--sys-clk-freq",         default=27e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--bios-flash-offset",    default="0x0",            help="BIOS offset in SPI Flash.")
    parser.add_target_argument("--with-spi-sdcard",      action="store_true",      help="Enable SPI-mode SDCard support.")
    parser.add_target_argument("--with-video-terminal",  action="store_true",      help="Enable Video Terminal (HDMI).")
    parser.add_target_argument("--prog-kit",             default="openfpgaloader", help="Programmer select from Gowin/openFPGALoader.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq        = args.sys_clk_freq,
        bios_flash_offset   = int(args.bios_flash_offset, 0),
        with_video_terminal = args.with_video_terminal,
        **parser.soc_argdict
    )

    if args.with_spi_sdcard:
        soc.add_spi_sdcard()

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer(kit=args.prog_kit)
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer(kit=args.prog_kit)
        prog.flash(0, builder.get_bitstream_filename(mode="flash", ext=".fs")) # FIXME
        # Axternal SPI programming not supported by gowin 'programmer_cli' now!
        # if needed, use openFPGALoader or Gowin programmer GUI
        if args.prog_kit == "openfpgaloader":
            prog.flash(int(args.bios_flash_offset, 0), builder.get_bios_filename(), external=True)

if __name__ == "__main__":
    main()
