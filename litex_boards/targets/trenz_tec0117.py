#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Pepijn de Vos <pepijndevos@gmail.com>
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex_boards.platforms import trenz_tec0117

from litex.build.io import DDROutput

from litex.soc.cores.clock.gowin_gw1n import  GW1NPLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litedram.modules import MT48LC4M16  # FIXME: use EtronTech reference.
from litedram.phy import GENSDRPHY, HalfRateGENSDRPHY

kB = 1024
mB = 1024*kB

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_sys   = ClockDomain()
        self.clock_domains.cd_sys2x = ClockDomain()

        # # #

        # Clk / Rst
        clk100 = platform.request("clk100")
        rst_n  = platform.request("rst_n")

        # PLL
        self.submodules.pll = pll = GW1NPLL(devicename=platform.devicename, device=platform.device)
        self.comb += pll.reset.eq(~rst_n)
        pll.register_clkin(clk100, 100e6)
        pll.create_clkout(self.cd_sys2x, 2*sys_clk_freq, with_reset=False)
        self.specials += Instance("CLKDIV",
            p_DIV_MODE= "2",
            i_RESETN = rst_n,
            i_HCLKIN = self.cd_sys2x.clk,
            o_CLKOUT = self.cd_sys.clk
        )
        self.specials += AsyncResetSynchronizer(self.cd_sys, ~rst_n)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, bios_flash_offset=0x0000, sys_clk_freq=int(25e6), sdram_rate="1:1",
                 with_led_chaser=True, **kwargs):
        platform = trenz_tec0117.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        # Disable Integrated ROM.
        kwargs["integrated_rom_size"] = 0
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on TEC0117", **kwargs)

        # SPI Flash --------------------------------------------------------------------------------
        from litespi.modules import W74M64FV
        from litespi.opcodes import SpiNorFlashOpCodes as Codes
        self.add_spi_flash(mode="4x", module=W74M64FV(Codes.READ_1_1_4), with_master=False)

        # Add ROM linker region --------------------------------------------------------------------
        self.bus.add_region("rom", SoCRegion(
            origin = self.bus.regions["spiflash"].origin + bios_flash_offset,
            size   = 32*kB,
            linker = True)
        )
        self.cpu.set_reset_address(self.bus.regions["rom"].origin)

        # SDR SDRAM --------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            class SDRAMPads:
                def __init__(self):
                    self.clk   = platform.request("O_sdram_clk")
                    self.cke   = platform.request("O_sdram_cke")
                    self.cs_n  = platform.request("O_sdram_cs_n")
                    self.cas_n = platform.request("O_sdram_cas_n")
                    self.ras_n = platform.request("O_sdram_ras_n")
                    self.we_n  = platform.request("O_sdram_wen_n")
                    self.dm    = platform.request("O_sdram_dqm")
                    self.a     = platform.request("O_sdram_addr")
                    self.ba    = platform.request("O_sdram_ba")
                    self.dq    = platform.request("IO_sdram_dq")
            sdram_pads = SDRAMPads()

            sdram_clk = ClockSignal("sys2x" if sdram_rate == "1:2" else "sys") # FIXME: use phase shift from PLL.
            self.specials += DDROutput(0, 1, sdram_pads.clk, sdram_clk)

            sdrphy_cls = HalfRateGENSDRPHY if sdram_rate == "1:2" else GENSDRPHY
            self.submodules.sdrphy = sdrphy_cls(sdram_pads, sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.sdrphy,
                module        = MT48LC4M16(sys_clk_freq, sdram_rate), # FIXME.
                l2_cache_size = 128,
            )

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Flash --------------------------------------------------------------------------------------------

def flash(bios_flash_offset):
    # Create FTDI <--> SPI Flash proxy bitstream and load it.
    # -------------------------------------------------------
    platform = trenz_tec0117.Platform()
    flash    = platform.request("spiflash", 0)
    bus      = platform.request("spiflash", 1)
    module = Module()
    module.comb += [
        flash.clk.eq(bus.clk),
        flash.cs_n.eq(bus.cs_n),
        flash.mosi.eq(bus.mosi),
        bus.miso.eq(flash.miso),
    ]
    platform.build(module)
    prog = platform.create_programmer()
    prog.flash(0, builder.get_bitstream_filename(mode="flash", ext=".fs")) # FIXME

    # Flash Image through proxy Bitstream.
    # ------------------------------------
    from spiflash.serialflash import SerialFlashManager
    dev = SerialFlashManager.get_flash_device("ftdi://ftdi:2232/2")
    dev.TIMINGS["chip"] = (4, 60) # Chip is too slow
    print("Erasing flash...")
    dev.erase(0, -1)
    with open("build/trenz_tec0117/software/bios/bios.bin", "rb") as f:
        bios = f.read()
    print("Programming flash...")
    dev.write(bios_flash_offset, bios)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on TEC0117")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",             action="store_true", help="Build design.")
    target_group.add_argument("--load",              action="store_true", help="Load bitstream.")
    target_group.add_argument("--bios-flash-offset", default="0x0000",    help="BIOS offset in SPI Flash.")
    target_group.add_argument("--flash",             action="store_true", help="Flash Bitstream and BIOS.")
    target_group.add_argument("--sys-clk-freq",      default=25e6,        help="System clock frequency.")
    sdopts = target_group.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-sdcard",     action="store_true", help="Enable SPI-mode SDCard support.")
    sdopts.add_argument("--with-sdcard",         action="store_true", help="Enable SDCard support.")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        bios_flash_offset = int(args.bios_flash_offset, 0),
        sys_clk_freq      = int(float(args.sys_clk_freq)),
        **soc_core_argdict(args)
    )
    soc.platform.add_extension(trenz_tec0117._sdcard_pmod_io)
    if args.with_spi_sdcard:
        soc.add_spi_sdcard()
    if args.with_sdcard:
        soc.add_sdcard()

    builder = Builder(soc, **builder_argdict(args))
    if args.build:
        builder.build()

    if args.load:
        prog = soc.platform.create_programmer()
        prog.flash(0, builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.flash(0, builder.get_bitstream_filename(mode="flash", ext=".fs")) # FIXME
        flash(int(args.bios_flash_offset, 0))

if __name__ == "__main__":
    main()
