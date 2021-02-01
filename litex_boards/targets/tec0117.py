#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Pepijn de Vos <pepijndevos@gmail.com>
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

import os
import argparse
import importlib

from migen import *

from litex.build.io import CRG

from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litex_boards.platforms import tec0117

from litedram.modules import MT48LC4M16  # FIXME: use EtronTech reference.
from litedram.phy import GENSDRPHY, HalfRateGENSDRPHY

kB = 1024
mB = 1024*kB

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_sys = ClockDomain()

        # # #

        # Clk / Rst
        clk100 = platform.request("clk100")
        rst_n  = platform.request("rst_n")

        # Generate 25Mhz sys_clk_freq clock from 100MHz input clock, FIXME: use PLL.
        assert sys_clk_freq == 25e6
        self.clock_domains.cd_clk100 = ClockDomain()
        self.comb += self.cd_clk100.clk.eq(clk100)
        count = Signal(2)
        self.sync.clk100 += count.eq(count + 1)
        clk50 = count[0]
        clk25 = count[1]
        self.comb += self.cd_sys.clk.eq(clk25)
        self.comb += self.cd_sys.rst.eq(~rst_n | self.rst) # FIXME: use AsyncResetSynchronizer

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    mem_map = {**SoCCore.mem_map, **{"spiflash": 0x80000000}}
    def __init__(self, bios_flash_offset, sys_clk_freq=int(25e6), sdram_rate="1:1", **kwargs):
        platform = tec0117.Platform()

        # Use custom default configuration to fit in LittleBee.
        kwargs["integrated_sram_size"] = 0x1000
        kwargs["integrated_rom_size"]  = 0x6000
        kwargs["cpu_type"]     = "vexriscv"
        kwargs["cpu_variant"]  = "lite"

        # Set CPU variant / reset address
        kwargs["cpu_reset_address"] = self.mem_map["spiflash"] + bios_flash_offset

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident          = "LiteX SoC on TEC0117",
            ident_version  = True,
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # SPI Flash --------------------------------------------------------------------------------
        self.add_spi_flash(mode="1x", dummy_cycles=8)

        # Add ROM linker region --------------------------------------------------------------------
        # FIXME: SPI Flash does not seem responding, power down set after loading bitstream?
        #self.bus.add_region("rom", SoCRegion(
        #    origin = self.mem_map["spiflash"] + bios_flash_offset,
        #    size   = 32*kB,
        #    linker = True)
        #)

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

            self.comb += sdram_pads.clk.eq(~ClockSignal("sys")) # FIXME: use phase shift from PLL.

            sdrphy_cls = HalfRateGENSDRPHY if sdram_rate == "1:2" else GENSDRPHY
            self.submodules.sdrphy = sdrphy_cls(sdram_pads, sys_clk_freq)
            self.add_sdram("sdram",
                phy                     = self.sdrphy,
                module                  = MT48LC4M16(sys_clk_freq, sdram_rate), # FIXME.
                origin                  = self.mem_map["main_ram"],
                l2_cache_size           = 128,
                l2_cache_min_data_width = 256,
            )

        # Leds -------------------------------------------------------------------------------------
        self.submodules.leds = LedChaser(
            pads         = platform.request_all("user_led"),
            sys_clk_freq = sys_clk_freq)
        self.add_csr("leds")

# Flash --------------------------------------------------------------------------------------------

def flash(bios_flash_offset):
    # Prepare Flash image.
    # --------------------
    bitstream  = open("build/tec0117/gateware/impl/pnr/project.bin",  "rb")
    bios       = open("build/tec0117/software/bios/bios.bin", "rb")
    image      = open("build/tec0117/image.bin", "wb")
    # Copy Bitstream at 0.
    blength = 0
    while True:
        b = bitstream.read(1)
        if not b:
            break
        else:
           image.write(b)
           blength += 1
    # Check Bitstream/BIOS overlap.
    if blength > bios_flash_offset:
        raise ValueError(f"Bitstream/BIOS overlap 0x{blength:08x} vs 0x{bios_flash_offset:08x}, increase BIOS Flash offset.")
    # Fill Gap between Bitstream/BIOS with zeroes.
    for i in range(bios_flash_offset - blength):
         image.write(0x00.to_bytes(1, "big"))
    # Copy BIOS at bios_flash_offset
    while True:
        b = bios.read(1)
        if not b:
            break
        else:
           image.write(b)

    # Create FTDI <--> SPI Flash proxy bitstream and load it.
    # -------------------------------------------------------
    platform = tec0117.Platform()
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
    prog.load_bitstream("build/impl/pnr/project.fs")

    # Flash Image through proxy Bitstream.
    # ------------------------------------
    from spiflash.serialflash import SerialFlashManager
    dev = SerialFlashManager.get_flash_device("ftdi://ftdi:2232/2")
    dev.TIMINGS["chip"] = (4, 60) # Chip is too slow
    print("Erasing flash...")
    dev.erase(0, -1)
    with open("build/tec0117/image.bin", "rb") as f:
        image = f.read()
    print("Programming flash...")
    dev.write(0, image)

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on TEC0117")
    parser.add_argument("--build",             action="store_true", help="Build bitstream")
    parser.add_argument("--load",              action="store_true", help="Load bitstream")
    parser.add_argument("--bios-flash-offset", default=0x80000,     help="BIOS offset in SPI Flash (0x00000 default)")
    parser.add_argument("--flash",             action="store_true", help="Flash Bitstream and BIOS")
    parser.add_argument("--sys-clk-freq",      default=25e6,        help="System clock frequency (default: 12MHz)")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        bios_flash_offset = args.bios_flash_offset,
        sys_clk_freq      = int(float(args.sys_clk_freq)),
        **soc_core_argdict(args)
    )
    builder = Builder(soc, **builder_argdict(args), bios_options=["TERM_MINI"])
    builder.build(run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, "impl", "pnr", "project.fs"))

    if args.flash:
        # flash(args.bios_flash_offset) FIXME.
        prog = soc.platform.create_programmer()
        prog.flash(0, os.path.join(builder.gateware_dir, "impl", "pnr", "project.fs"))

if __name__ == "__main__":
    main()
