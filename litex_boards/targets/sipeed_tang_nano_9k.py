#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Icenowy Zheng <icenowy@aosc.io>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

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

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq, with_video_pll=False):
        self.rst = Signal()
        self.clock_domains.cd_sys = ClockDomain()

        # # #

        # Clk / Rst
        clk27 = platform.request("clk27")
        rst_n = platform.request("user_btn", 0)

        # PLL
        self.submodules.pll = pll = GW1NPLL(devicename=platform.devicename, device=platform.device)
        self.comb += pll.reset.eq(~rst_n)
        pll.register_clkin(clk27, 27e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(27e6), bios_flash_offset=0x0,
                 with_led_chaser=True, **kwargs):
        platform = sipeed_tang_nano_9k.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        # Disable Integrated ROM
        kwargs["integrated_rom_size"] = 0
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident = "LiteX SoC on Tang Nano 9K",
            **kwargs
        )

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
            self.submodules.hyperram = HyperRAM(hyperram_pads, sys_clk_freq=sys_clk_freq)
            self.bus.add_slave("main_ram", slave=self.hyperram.bus, region=SoCRegion(origin=self.mem_map["main_ram"], size=4*mB))

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on Tang Nano 9K")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",       action="store_true", help="Build design.")
    target_group.add_argument("--load",        action="store_true", help="Load bitstream.")
    target_group.add_argument("--flash",       action="store_true", help="Flash Bitstream.")
    target_group.add_argument("--sys-clk-freq",default=27e6,        help="System clock frequency.")
    target_group.add_argument("--bios-flash-offset", default="0x0", help="BIOS offset in SPI Flash.")
    target_group.add_argument("--with-spi-sdcard", action="store_true", help="Enable SPI-mode SDCard support.")
    target_group.add_argument("--prog-kit", default="openfpgaloader", help="Programmer select from Gowin/openFPGALoader.")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq=int(float(args.sys_clk_freq)),
        bios_flash_offset=int(args.bios_flash_offset, 0),
        **soc_core_argdict(args)
    )

    if args.with_spi_sdcard:
        soc.add_spi_sdcard()

    builder = Builder(soc, **builder_argdict(args))
    if args.build:
        builder.build()

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
