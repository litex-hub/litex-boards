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
from litex.soc.integration.soc import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.gpio import GPIOIn
from litex.soc.cores.video import *

from litex.soc.cores.ram.gowin_hyperram import GowinHyperRAM

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_video_pll=False, with_hyperram=False):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()

        # # #

        # Clk / Rst
        clk27 = platform.request("clk27")
        rst_n = platform.request("user_btn_n", 0)
        self.btn_n0 = rst_n

        # PLL
        self.pll = pll = GW1NPLL(devicename=platform.devicename, device=platform.device)
        self.comb += pll.reset.eq(~rst_n)
        pll.register_clkin(clk27, 27e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)

        # HyperRAM Clock.
        if with_hyperram:
            self.cd_sys4x = ClockDomain()
            pll.create_clkout(self.cd_sys4x, 4*sys_clk_freq)

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
    def __init__(self, toolchain="gowin", sys_clk_freq=27e6, bios_flash_offset=0x0,
        with_led_chaser     = True,
        with_buttons        = False,
        with_video_terminal = False,
        with_video_framebuffer = False,
        with_integrated_rom = False,
        **kwargs):
        platform = sipeed_tang_nano_9k.Platform(toolchain=toolchain)

        # This GW1NR-9 is tight on LUTs, so build Ibex (when selected) with its
        # distributed-RAM register file instead of the default flip-flop one,
        # which overflows the part. Ignored by every other CPU.
        platform.ibex_regfile = "fpga"

        # CRG --------------------------------------------------------------------------------------
        with_hyperram = not kwargs.get("integrated_main_ram_size", 0)
        assert not with_video_framebuffer or with_hyperram
        self.crg = _CRG(platform, sys_clk_freq,
            with_video_pll = with_video_terminal or with_video_framebuffer,
            with_hyperram  = with_hyperram)

        # SoCCore ----------------------------------------------------------------------------------
        # Keep the BIOS in external SPI Flash by default to save GW1N-9 resources.
        # --with-integrated-rom is useful for SRAM-only loading/debug, at the cost of extra BRAMs.
        if with_integrated_rom:
            kwargs.setdefault("integrated_rom_size", 128 * KILOBYTE)
        else:
            kwargs["integrated_rom_size"] = 0
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Tang Nano 9K", **kwargs)

        # SPI Flash --------------------------------------------------------------------------------
        from litespi.modules import W25Q32
        from litespi.opcodes import SpiNorFlashOpCodes as Codes
        self.add_spi_flash(mode="1x", module=W25Q32(Codes.READ_1_1_1), with_master=False)

        # Add ROM linker region --------------------------------------------------------------------
        if not with_integrated_rom:
            self.bus.add_region("rom", SoCRegion(
                origin = self.bus.regions["spiflash"].origin + bios_flash_offset,
                size   = 64 * KILOBYTE,
                linker = True)
            )
            self.cpu.set_reset_address(self.bus.regions["rom"].origin)

        # HyperRAM ---------------------------------------------------------------------------------
        if with_hyperram:
            class HyperRAMPads:
                pass
            hyperram_pads = HyperRAMPads()
            hyperram_pads.clk    = platform.request("O_psram_ck")
            hyperram_pads.clk_n  = platform.request("O_psram_ck_n")
            hyperram_pads.cs_n   = platform.request("O_psram_cs_n")
            hyperram_pads.rst_n  = platform.request("O_psram_reset_n")
            hyperram_pads.dq     = platform.request("IO_psram_dq")
            hyperram_pads.rwds   = platform.request("IO_psram_rwds")
            self.hyperram = GowinHyperRAM(hyperram_pads, sys_clk_freq=sys_clk_freq, clk_ratio="4:1")
            self.bus.add_slave("main_ram", slave=self.hyperram.bus, region=SoCRegion(origin=self.mem_map["main_ram"], size=4 * MEGABYTE, mode="rwx"))

        # Video ------------------------------------------------------------------------------------
        if with_video_terminal:
            self.videophy = VideoGowinHDMIPHY(platform.request("hdmi"), clock_domain="hdmi")
            self.add_video_colorbars(phy=self.videophy, timings="640x480@60Hz", clock_domain="hdmi")
            #self.add_video_terminal(phy=self.videophy, timings="640x480@75Hz", clock_domain="hdmi") # FIXME: Free up BRAMs.
        if with_video_framebuffer:
            self.videophy = VideoGowinHDMIPHY(platform.request("hdmi"), clock_domain="hdmi")
            self.add_video_framebuffer(phy=self.videophy, timings="640x480@60Hz", clock_domain="hdmi")

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

        # Buttons ---------------------------------------------------------------------------------
        if with_buttons:
            self.buttons = GPIOIn(Cat(self.crg.btn_n0, platform.request("user_btn_n", 1)))

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=sipeed_tang_nano_9k.Platform, description="LiteX SoC on Tang Nano 9K.")
    parser.add_target_argument("--flash",               action="store_true",      help="Flash bitstream.")
    parser.add_target_argument("--sys-clk-freq",        default=27e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--bios-flash-offset",   default="0x0",            help="BIOS offset in SPI Flash.")
    parser.add_target_argument("--with-spi-sdcard",     action="store_true",      help="Enable SPI-mode SDCard support.")
    parser.add_target_argument("--with-video-terminal", action="store_true",      help="Enable Video Terminal (HDMI).")
    parser.add_target_argument("--with-video-framebuffer", action="store_true",   help="Enable Video Framebuffer (HDMI, HyperRAM-backed).")
    parser.add_target_argument("--with-buttons",        action="store_true",      help="Enable Buttons.")
    parser.add_target_argument("--with-integrated-rom", action="store_true",      help="Build BIOS into FPGA bitstream for SRAM-only loading/debug.")
    parser.add_target_argument("--prog-kit",            default="openfpgaloader", help="Programmer select from Gowin/openFPGALoader.")
    args = parser.parse_args()

    soc = BaseSoC(
        toolchain           = args.toolchain,
        sys_clk_freq        = args.sys_clk_freq,
        bios_flash_offset   = int(args.bios_flash_offset, 0),
        with_video_terminal = args.with_video_terminal,
        with_video_framebuffer = args.with_video_framebuffer,
        with_buttons        = args.with_buttons,
        with_integrated_rom = args.with_integrated_rom,
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
