#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import *

from litex_boards.platforms import sipeed_tang_nano_4k

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
    def __init__(self, sys_clk_freq=27e6,
        with_hyperram       = False,
        with_led_chaser     = True,
        with_video_terminal = True,
        **kwargs):
        platform = sipeed_tang_nano_4k.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, with_video_pll=with_video_terminal)

        # SoCCore ----------------------------------------------------------------------------------
        if "cpu_type" in kwargs and kwargs["cpu_type"] == "gowin_emcu":
            kwargs["with_uart"]            = False # CPU has own UART
            kwargs["integrated_sram_size"] = 0     # SRAM is directly attached to CPU
            kwargs["integrated_rom_size"]  = 0     # boot flash directly attached to CPU
        else:
            # Disable Integrated ROM
            kwargs["integrated_rom_size"] = 0
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Tang Nano 4K", **kwargs)

        if self.cpu_type == 'vexriscv':
            assert self.cpu_variant == 'minimal', 'use --cpu-variant=minimal to fit into number of BSRAMs'

        # Gowin EMCU Integration -------------------------------------------------------------------
        if self.cpu_type == "gowin_emcu":
            self.cpu.connect_uart(platform.request("serial"))
            self.bus.add_region("sram", SoCRegion(
                origin=self.cpu.mem_map["sram"],
                size=16 * kB)
            )
            self.bus.add_region("rom", SoCRegion(
                origin=self.cpu.mem_map["rom"],
                size=32 * kB,
                linker=True)
            )
        else:
            # SPI Flash ----------------------------------------------------------------------------
            from litespi.modules import W25Q32
            from litespi.opcodes import SpiNorFlashOpCodes as Codes
            self.add_spi_flash(mode="1x", module=W25Q32(Codes.READ_1_1_1), with_master=False)
            # Add ROM linker region ----------------------------------------------------------------
            self.bus.add_region("rom", SoCRegion(
                origin = self.bus.regions["spiflash"].origin,
                size   = 32*kB,
                linker = True)
            )
            self.cpu.set_reset_address(self.bus.regions["rom"].origin)

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
            self.hyperram = HyperRAM(hyperram_pads, sys_clk_freq=sys_clk_freq)
            self.bus.add_slave("main_ram", slave=self.hyperram.bus, region=SoCRegion(origin=0x40000000, size=8*mB))

        # Video ------------------------------------------------------------------------------------
        if with_video_terminal:
            self.videophy = VideoGowinHDMIPHY(platform.request("hdmi"), clock_domain="hdmi")
            self.add_video_colorbars(phy=self.videophy, timings="640x480@75Hz", clock_domain="hdmi")
            #self.add_video_terminal(phy=self.videophy, timings="640x480@75Hz", clock_domain="hdmi") # FIXME: Free up BRAMs.

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=sipeed_tang_nano_4k.Platform, description="LiteX SoC on Tang Nano 4K.")
    parser.add_target_argument("--flash",       action="store_true",        help="Flash Bitstream.")
    parser.add_target_argument("--sys-clk-freq",default=27e6, type=float,   help="System clock frequency.")
    parser.add_target_argument("--with-video-terminal",action="store_true", help="System clock frequency.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq        = args.sys_clk_freq,
        with_video_terminal = args.with_video_terminal,
        **parser.soc_argdict
    )

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.flash(0, builder.get_bitstream_filename(mode="flash", ext=".fs")) # FIXME
        prog.flash(0, builder.get_bios_filename(), external=True)


if __name__ == "__main__":
    main()
