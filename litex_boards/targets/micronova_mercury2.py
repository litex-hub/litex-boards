#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Michael T. Mayers <michael@tweakoz.com>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import *

from litex.build.io import CRG

from litex_boards.platforms import micronova_mercury2

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.interconnect import wishbone

from litex.soc.integration.soc import colorer

kB = 1024
mB = 1024*kB

# _CRG ---------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst          = Signal()
        self.cd_sys       = ClockDomain()
        self.cd_sys4x     = ClockDomain()
        self.cd_sys4x_dqs = ClockDomain()

        # # #

        pll_clk50 = platform.request("clk50")

        self.pll = pll = S7MMCM(speedgrade=-1)
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(pll_clk50, 50e6)
        pll.create_clkout(self.cd_sys,       sys_clk_freq)
        pll.create_clkout(self.cd_sys4x,     4*sys_clk_freq)
        pll.create_clkout(self.cd_sys4x_dqs, 4*sys_clk_freq, phase=90)

        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

# AsyncSRAM ------------------------------------------------------------------------------------------

class AsyncSRAM(LiteXModule):
    def __init__(self, platform, size):
        addr_width = size//8
        data_width = 8
        self.bus = wishbone.Interface(data_width=data_width,adr_width=addr_width)
        issiram = platform.request("issiram")
        addr = issiram.addr
        data = issiram.data
        wen = issiram.wen
        cen = issiram.cen
        ########################
        tristate_data = TSTriple(data_width)
        self.specials += tristate_data.get_tristate(data)
        ########################
        chip_ena = self.bus.cyc & self.bus.stb & self.bus.sel[0]
        write_ena = (chip_ena & self.bus.we)
        ########################
        # external write enable, 
        # external chip enable, 
        # internal tristate write enable
        ########################
        self.comb += [
            cen.eq(~chip_ena),
            wen.eq(~write_ena),
            tristate_data.oe.eq(write_ena)
        ]
        ########################
        # address and data
        ########################
        self.comb += [
            addr.eq(self.bus.adr[:addr_width]),
            self.bus.dat_r.eq(tristate_data.i[:data_width]),
            tristate_data.o.eq(self.bus.dat_w[:data_width])
        ]
        ########################
        # generate ack
        ########################
        self.sync += [
            self.bus.ack.eq(self.bus.cyc & self.bus.stb & ~self.bus.ack),
        ]
        ########################

def addAsyncSram(soc, platform, name, origin, size):
    ram_bus = wishbone.Interface(data_width=soc.bus.data_width)
    ram     = AsyncSRAM(platform,size)
    soc.bus.add_slave(name, ram.bus, SoCRegion(origin=origin, size=size, mode="rw"))
    soc.check_if_exists(name)
    soc.logger.info("ISSIRAM {} {} {}.".format(
        colorer(name),
        colorer("added", color="green"),
        soc.bus.regions[name]))
    setattr(soc.submodules, name, ram)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, 
        variant         = "a7-35",
        toolchain       = "vivado",
        sys_clk_freq    = 100e6,
        with_led_chaser = True,
        **kwargs):
        platform = micronova_mercury2.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on MicroNova Mercury2", **kwargs)

        # Async RAM --------------------------------------------------------------------------------
        addAsyncSram(self,platform,"main_ram", 0x40000000, 512*1024)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=micronova_mercury2.Platform, description="LiteX SoC on MicroNova Mercury2.")
    parser.add_target_argument("--variant",      default="a7-35",          help="Board variant (a7-35 or a7-100).")
    parser.add_target_argument("--sys-clk-freq", default=50e6, type=float, help="System clock frequency.")

    args = parser.parse_args()

    soc = BaseSoC(
        variant      = args.variant,
        toolchain    = args.toolchain,
        sys_clk_freq = args.sys_clk_freq,
        **parser.soc_argdict
    )

    builder_argd = parser.builder_argdict

    builder = Builder(soc, **builder_argd)
    if args.build:
        builder.build(**parser.toolchain_argdict)

if __name__ == "__main__":
    main()

