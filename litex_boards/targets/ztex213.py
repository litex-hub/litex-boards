#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2015-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2020-2021 Romain Dolbeau <romain@dolbeau.org>
# SPDX-License-Identifier: BSD-2-Clause

# Support for the ZTEX USB-FGPA Module 2.13:https://www.ztex.de/usb-fpga-2/usb-fpga-2.13.e.html.
# With (no-so-optional) expansion, either the ZTEX Debug board:
# https://www.ztex.de/usb-fpga-2/debug.e.html
# Or the SBusFPGA adapter board:
# https://github.com/rdolbeau/SBusFPGA

from migen import *

from litex_boards.platforms import ztex213
from litex.build.xilinx.vivado import vivado_build_args, vivado_build_argdict

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litedram.modules import MT41J128M16
from litedram.phy import s7ddrphy

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.clock_domains.cd_sys       = ClockDomain()
        self.clock_domains.cd_sys4x     = ClockDomain()
        self.clock_domains.cd_sys4x_dqs = ClockDomain()
        self.clock_domains.cd_idelay    = ClockDomain()
        self.clock_domains.cd_por       = ClockDomain()

        # # #
        clk48 = platform.request("clk48")

        self.submodules.pll = pll = S7MMCM(speedgrade=-1)
        pll.register_clkin(clk48, 48e6)
        pll.create_clkout(self.cd_sys,       sys_clk_freq)
        pll.create_clkout(self.cd_sys4x,     4*sys_clk_freq)
        pll.create_clkout(self.cd_sys4x_dqs, 4*sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_idelay,    200e6)

        # Power on reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += self.cd_por.clk.eq(clk48)
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))
        self.comb += pll.reset.eq(~por_done)

        self.submodules.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, variant="ztex2.13a", sys_clk_freq=int(100e6), expansion="debug",
                 with_led_chaser=True, **kwargs):
        platform = ztex213.Platform(variant=variant, expansion=expansion)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident = "LiteX SoC on Ztex 2.13",
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.submodules.ddrphy = s7ddrphy.A7DDRPHY(platform.request("ddram"),
                memtype        = "DDR3",
                nphases        = 4,
                sys_clk_freq   = sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT41J128M16(sys_clk_freq, "1:4"),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on Ztex 2.13")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",           action="store_true", help="Build bitstream.")
    target_group.add_argument("--load",            action="store_true", help="Load bitstream.")
    target_group.add_argument("--expansion",       default="debug",     help="Expansion board (debug or sbus).")
    target_group.add_argument("--sys-clk-freq",    default=100e6,       help="System clock frequency.")
    target_group.add_argument("--with-spi-sdcard", action="store_true", help="Enable SPI-mode SDCard support.")
    target_group.add_argument("--with-sdcard",     action="store_true", help="Enable SDCard support.")
    builder_args(parser)
    soc_core_args(parser)
    vivado_build_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(sys_clk_freq=int(float(args.sys_clk_freq)), expansion=args.expansion, **soc_core_argdict(args))
    assert not (args.with_spi_sdcard and args.with_sdcard)
    if args.with_spi_sdcard:
        soc.add_spi_sdcard() # SBus only
    if args.with_sdcard:
        soc.add_sdcard() # SBus only
    builder = Builder(soc, **builder_argdict(args))
    builder.build(**vivado_build_argdict(args), run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
