#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2015-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2020 Antmicro <www.antmicro.com>
# SPDX-License-Identifier: BSD-2-Clause

import os
import argparse

from migen import *

from litex_boards.platforms import arty
from litex.build.xilinx.vivado import vivado_build_args, vivado_build_argdict

from litex.soc.cores.clock import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.gpio import GPIOTristate

from litedram.modules import MT41K128M16
from litedram.phy import s7ddrphy

from liteeth.phy.mii import LiteEthPHYMII

from litespi.modules import S25FL128L
from litespi.opcodes import SpiNorFlashOpCodes as Codes
from litespi.phy.generic import LiteSPIPHY
from litespi import LiteSPI

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq, with_mapped_flash=False):
        self.rst = Signal()
        self.clock_domains.cd_sys       = ClockDomain()
        self.clock_domains.cd_sys4x     = ClockDomain(reset_less=True)
        self.clock_domains.cd_sys4x_dqs = ClockDomain(reset_less=True)
        self.clock_domains.cd_idelay    = ClockDomain()
        self.clock_domains.cd_eth       = ClockDomain()

        # # #

        self.submodules.pll = pll = S7PLL(speedgrade=-1)
        self.comb += pll.reset.eq(~platform.request("cpu_reset") | self.rst)
        pll.register_clkin(platform.request("clk100"), 100e6)
        pll.create_clkout(self.cd_sys,       sys_clk_freq)
        pll.create_clkout(self.cd_sys4x,     4*sys_clk_freq)
        pll.create_clkout(self.cd_sys4x_dqs, 4*sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_idelay,    200e6)
        pll.create_clkout(self.cd_eth,       25e6)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        self.submodules.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

        self.comb += platform.request("eth_ref_clk").eq(self.cd_eth.clk)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, variant="a7-35", toolchain="vivado", sys_clk_freq=int(100e6),
                 with_ethernet=False, with_etherbone=False, eth_ip="192.168.1.50",
                 eth_dynamic_ip=False, ident_version=True, with_led_chaser=True, with_jtagbone=True,
                 with_mapped_flash=False, with_pmod_gpio=False, **kwargs):
        platform = arty.Platform(variant=variant, toolchain=toolchain)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident          = "LiteX SoC on Arty A7",
            ident_version  = ident_version,
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq, with_mapped_flash)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.submodules.ddrphy = s7ddrphy.A7DDRPHY(platform.request("ddram"),
                memtype        = "DDR3",
                nphases        = 4,
                sys_clk_freq   = sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT41K128M16(sys_clk_freq, "1:4"),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            self.submodules.ethphy = LiteEthPHYMII(
                clock_pads = self.platform.request("eth_clocks"),
                pads       = self.platform.request("eth"))
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy, dynamic_ip=eth_dynamic_ip)
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, ip_address=eth_ip)

        # Jtagbone ---------------------------------------------------------------------------------
        if with_jtagbone:
            self.add_jtagbone()

        # Flash (through LiteSPI, experimental).
        if with_mapped_flash:
            self.submodules.spiflash_phy  = LiteSPIPHY(platform.request("spiflash4x"), S25FL128L(Codes.READ_1_1_4))
            self.submodules.spiflash_mmap = LiteSPI(self.spiflash_phy, clk_freq=sys_clk_freq, mmap_endianness=self.cpu.endianness)
            spiflash_region = SoCRegion(origin=self.mem_map.get("spiflash", None), size=S25FL128L.total_size, cached=False)
            self.bus.add_slave(name="spiflash", slave=self.spiflash_mmap.bus, region=spiflash_region)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

        # GPIOs ------------------------------------------------------------------------------------
        if with_pmod_gpio:
            platform.add_extension(arty.raw_pmod_io("pmoda"))
            self.submodules.gpio = GPIOTristate(platform.request("pmoda"))

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on Arty A7")
    parser.add_argument("--toolchain",           default="vivado",                 help="Toolchain use to build (default: vivado)")
    parser.add_argument("--build",               action="store_true",              help="Build bitstream")
    parser.add_argument("--load",                action="store_true",              help="Load bitstream")
    parser.add_argument("--variant",             default="a7-35",                  help="Board variant: a7-35 (default) or a7-100")
    parser.add_argument("--sys-clk-freq",        default=100e6,                    help="System clock frequency (default: 100MHz)")
    ethopts = parser.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",      action="store_true",              help="Enable Ethernet support")
    ethopts.add_argument("--with-etherbone",     action="store_true",              help="Enable Etherbone support")
    parser.add_argument("--eth-ip",              default="192.168.1.50", type=str, help="Ethernet/Etherbone IP address")
    parser.add_argument("--eth-dynamic-ip",      action="store_true",              help="Enable dynamic Ethernet IP addresses setting")
    sdopts = parser.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-sdcard",     action="store_true",              help="Enable SPI-mode SDCard support")
    sdopts.add_argument("--with-sdcard",         action="store_true",              help="Enable SDCard support")
    parser.add_argument("--sdcard-adapter",      type=str,                         help="SDCard PMOD adapter: digilent (default) or numato")
    parser.add_argument("--no-ident-version",    action="store_false",             help="Disable build time output")
    parser.add_argument("--with-jtagbone",       action="store_true",              help="Enable Jtagbone support")
    parser.add_argument("--with-mapped-flash",   action="store_true",              help="Enable Memory Mapped Flash")
    parser.add_argument("--with-pmod-gpio",      action="store_true",              help="Enable GPIOs through PMOD") # FIXME: Temporary test.
    builder_args(parser)
    soc_core_args(parser)
    vivado_build_args(parser)
    args = parser.parse_args()

    assert not (args.with_etherbone and args.eth_dynamic_ip)

    soc = BaseSoC(
        variant           = args.variant,
        toolchain         = args.toolchain,
        sys_clk_freq      = int(float(args.sys_clk_freq)),
        with_ethernet     = args.with_ethernet,
        with_etherbone    = args.with_etherbone,
        eth_ip            = args.eth_ip,
        eth_dynamic_ip    = args.eth_dynamic_ip,
        ident_version     = args.no_ident_version,
        with_jtagbone     = args.with_jtagbone,
        with_mapped_flash = args.with_mapped_flash,
        with_pmod_gpio    = args.with_pmod_gpio,
        **soc_core_argdict(args)
    )
    if args.sdcard_adapter == "numato":
        soc.platform.add_extension(arty._numato_sdcard_pmod_io)
    else:
        soc.platform.add_extension(arty._sdcard_pmod_io)
    if args.with_spi_sdcard:
        soc.add_spi_sdcard()
    if args.with_sdcard:
        soc.add_sdcard()
    builder = Builder(soc, **builder_argdict(args))
    builder_kwargs = vivado_build_argdict(args) if args.toolchain == "vivado" else {}
    builder.build(**builder_kwargs, run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".bit"))

if __name__ == "__main__":
    main()
