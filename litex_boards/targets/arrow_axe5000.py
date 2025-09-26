#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 Gwenhael Goavec-merou<gwenhael.goavec-merou@trabucayre.com>
#
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import *

from litex_boards.platforms import arrow_axe5000

from litex.soc.interconnect import wishbone

from litex.soc.integration.soc      import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder  import *

from litex.soc.cores.clock    import Agilex5PLL
from litex.soc.cores.hyperbus import HyperRAM
from litex.soc.cores.led      import LedChaser


# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst      = Signal()
        self.cd_sys   = ClockDomain()
        self.cd_sys2x = ClockDomain()

        # # #

        # Clk / Rst
        clk25 = platform.request("clk25")
        rst_n = platform.request("user_btn", 0)

        # Power on reset
        ninit_done = Signal()
        self.specials += Instance("altera_agilex_config_reset_release_endpoint", o_conf_reset = ninit_done)

        # PLL
        self.pll = pll = Agilex5PLL(platform, speedgrade="-6S")
        self.comb += pll.reset.eq(ninit_done | ~rst_n)
        pll.register_clkin(clk25, 25e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)

        # HyperRAM
        pll.create_clkout(self.cd_sys2x, 2*sys_clk_freq)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=100e6,
        with_l2_cache   = False,
        with_led_chaser = True,
        **kwargs):
        platform = arrow_axe5000.Platform()

        # Select 1.3V, for HSIO on CRUVI-HS
        self.comb += platform.request("vsel_1v3").eq(0b1)

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Arrow AXE5000", **kwargs)

        # HyperRAM ---------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            # HyperRAM Parameters.
            hyperram_size       = 16 * MEGABYTE
            hyperram_cache_size = 16 * KILOBYTE

            # HyperRAM Bus/Slave Interface.
            hyperram_bus = wishbone.Interface(data_width=32, address_width=32, addressing="word")
            self.bus.add_slave(
                name   = "main_ram",
                slave  = hyperram_bus,
                region = SoCRegion(origin=self.mem_map["main_ram"], size=hyperram_size, mode="rwx")
            )

            # HyperRAM L2 Cache.
            if with_l2_cache:
                hyperram_cache = wishbone.Cache(
                    cachesize = hyperram_cache_size // 4,
                    master    = hyperram_bus,
                    slave     = wishbone.Interface(data_width=32, address_width=32, addressing="word")
                )
                self.hyperram_cache = FullMemoryWE()(hyperram_cache)
                self.add_config("L2_SIZE", hyperram_cache_size)

            # HyperRAM Core.
            self.hyperram = HyperRAM(
                pads         = platform.request("hyperram"),
                latency      = 7,
                latency_mode = "variable",
                sys_clk_freq = sys_clk_freq,
                clk_ratio    = "2:1", # Not working with 4:1
            )

            if with_l2_cache:
                self.comb += self.hyperram_cache.slave.connect(self.hyperram.bus)
            else:
                self.comb += hyperram_bus.connect(self.hyperram.bus)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            led_pads     = platform.request_all("user_led")
            rgb_led_pads = platform.request("rgb_led", 0)
            self.comb += [getattr(rgb_led_pads, n).eq(1) for n in "gb"] # Disable Green/Blue Leds.
            self.leds = LedChaser(
                pads         = Cat(led_pads, rgb_led_pads.r),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=arrow_axe5000.Platform, description="LiteX SoC on Arrow AXE5000.")
    parser.add_target_argument("--sys-clk-freq",  default=100e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-l2-cache", action="store_true",       help="Enable Main RAM L2 cache.")

    # Overrides defaults synth/conv tools.
    parser.set_defaults(synth_tool = "quartus_syn")
    parser.set_defaults(conv_tool  = "quartus_pfg")

    # soc.json default path
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq  = args.sys_clk_freq,
        with_l2_cache = args.with_l2_cache,
        **parser.soc_argdict
    )

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
