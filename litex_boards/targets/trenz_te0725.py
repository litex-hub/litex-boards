#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Shinken Sanada <sanadashinken@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex_boards.platforms import trenz_te0725
from litex.build.xilinx.vivado import vivado_build_args, vivado_build_argdict

from litex.soc.cores.clock import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litex.soc.cores.hyperbus import HyperRAM

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_sys       = ClockDomain()

        self.submodules.pll = pll = S7PLL(speedgrade=-1)
        self.comb += pll.reset.eq(~platform.request("cpu_reset") | self.rst)
        pll.register_clkin(platform.request("clk100"), 100e6)
        pll.create_clkout(self.cd_sys,       sys_clk_freq)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(100e6), with_led_chaser=True, **kwargs):
        platform = trenz_te0725.Platform()

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident = "LiteX SoC on Trenz TE0725 Board",
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # Use HyperRAM generic PHY as SRAM ---------------------------------------------------------
        size = int((64*1024*1024) / 8)
        hr_pads = platform.request("hyperram", 0)
        self.submodules.hyperram = HyperRAM(hr_pads)
        self.bus.add_slave("hyperram", slave=self.hyperram.bus, region=SoCRegion(origin=0x20000000, size=size))

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)
            self.add_csr("leds")

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on Trenz TE0725")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",           action="store_true", help="Build bitstream.")
    target_group.add_argument("--load",            action="store_true", help="Load bitstream.")
    target_group.add_argument("--flash",           action="store_true", help="Flash bitstream.")
    target_group.add_argument("--sys-clk-freq",    default=100e6,       help="System clock frequency.")

    builder_args(parser)
    soc_core_args(parser)
    vivado_build_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq   = int(float(args.sys_clk_freq)),
        **soc_core_argdict(args)
    )

    builder = Builder(soc, **builder_argdict(args))

    builder.build(**vivado_build_argdict(args), run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="flash"))

if __name__ == "__main__":
    main()

