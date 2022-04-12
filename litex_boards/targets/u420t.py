#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020-2021 Xuanyu Hu <xuanyu.hu@whu.edu.cn>
# SPDX-License-Identifier: BSD-2-Clause
# ported by Alex Petrov aka sysman
# Kintex7-420T aliexpress
# Part xc7k420tiffg901-2L v0.2

from migen import *

from litex_boards.platforms import u420t
from litex.soc.interconnect import wishbone
from litex.soc.cores.clock import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_sys    = ClockDomain()
        self.clock_domains.cd_sys4x  = ClockDomain(reset_less=True)
        self.clock_domains.cd_idelay = ClockDomain()

        # board is grade 2, but to fix halts use -1
        self.submodules.pll = pll = S7MMCM(speedgrade=-2)
        ##self.submodules.pll = pll = S7MMCM(speedgrade=-1)
        self.comb += pll.reset.eq(~platform.request("user_btn_k3") | self.rst)
        pll.register_clkin(platform.request("clk100"), 100e6)
        #workaround to bypass for clk100 error: No nets matched 'clk100'
        #line:940 litex/litex/build/xilinx/vivado.py " [get_ports {clk}]", clk=clk)
        ## platform.add_platform_command("create_clock -name clk100 -period 10.0 [get_ports clk100]")
        pll.create_clkout(self.cd_sys,    sys_clk_freq)
        pll.create_clkout(self.cd_sys4x,  4*sys_clk_freq)
        pll.create_clkout(self.cd_idelay, 200e6)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.
        # platform.add_platform_command("set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets clk100]")
        # Reduce programming time
        #self.add_platform_command("set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]")
        self.submodules.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(100e6), with_led_chaser=True, with_spi_flash=False, **kwargs):
        platform = u420t.Platform()

        # --- add more sram for riscv comfort
        # xc7k420t BRAMs: 1670 (col length: RAMB18 160 RAMB36 80)
        kwargs["integrated_rom_size"]  = 0x8000 # 8kb
        kwargs["integrated_sram_size"] = 0x10000 # 64kb
        kwargs["integrated_main_ram_size"] = 0x40000 # 256kb ## change if needed

        # SoCCore ----------------------------------_-----------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident = "LiteX SoC on u420t",
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # Video ------------------------------------------------------------------------------------
        # no video
        # no ram
	# SPI Flash --------------------------------------------------------------------------------
        if with_spi_flash:
            from litespi.modules import N25Q256
            from litespi.opcodes import SpiNorFlashOpCodes as Codes
            self.add_spi_flash(mode="4x", module=W25Q256(Codes.READ_1_1_4))


        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

        # Add ROM linker region --------------------------------------------------------------------
        #self.bus.add_region("rom", SoCRegion(
        #    origin = self.bus.regions["spiflash"].origin + bios_flash_offset,
        #    size   = 32*kB,
        #    linker = True)
        #)
        #self.cpu.set_reset_address(self.bus.regions["rom"].origin)


# Build --------------------------------------------------------------------------------------------  
def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on u420t")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",               action="store_true", help="Build bitstream.")
    target_group.add_argument("--load",                action="store_true", help="Load bitstream.")
    target_group.add_argument("--sys-clk-freq",        default=100e6,        help="System clock frequency.")
#    sdopts = target_group.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-flash",     action="store_true", help="Enable SPI-mode flash support.")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq           = int(float(args.sys_clk_freq)),
        **soc_core_argdict(args)
    )
#    soc.platform.add_extension(u420t._sdcard_pmod_io)
    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(obuilder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
