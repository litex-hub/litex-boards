#!/usr/bin/env python3

# This file is Copyright (c) 2019 Antti Lukats <antti.lukats@gmail.com>
# This file is Copyright (c) 2015-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# License: BSD

import argparse

from migen import *

from litex_boards.partner.platforms import tem0006

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.clock_domains.cd_sys = ClockDomain()
        self.clock_domains.cd_por = ClockDomain(reset_less=True)

        clk12 = platform.request("clk12")

        btn = platform.request("user_btn", 0)

        rst_n = Signal()
        self.sync.por += rst_n.eq(btn)
        self.comb += [
            self.cd_por.clk.eq(clk12),
            self.cd_sys.clk.eq(clk12),
            self.cd_sys.rst.eq(~rst_n)
        ]


# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):

    def __init__(self, sys_clk_freq=int(12e6), **kwargs):
        platform = tem0006.Platform()

        SoCCore.__init__(self, platform, clk_freq=sys_clk_freq,
            integrated_rom_size=0x6000,
            integrated_main_ram_size=0x1000,
            **kwargs)

	# can we just use the clock without PLL ?

        self.submodules.crg = _CRG(platform, sys_clk_freq)
        self.counter = counter = Signal(32)
        self.sync += counter.eq(counter + 1)
 
	#
        led_red = platform.request("user_led", 0)
        self.comb += led_red.eq(counter[23])

#        led_green = platform.request("user_led_green")
#        self.comb += led_green.eq(counter[25])


# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX on TEM0006")
    builder_args(parser)
#    soc_sdram_args(parser)
    soc_core_args(parser)

    args = parser.parse_args()

    cls = BaseSoC

    soc = cls(**soc_core_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder.build()


if __name__ == "__main__":
    main()
