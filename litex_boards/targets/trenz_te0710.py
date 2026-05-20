#!/usr/bin/env python3

# This file is Copyright (c) 2019 Antti Lukats <antti.lukats@gmail.com>
# This file is Copyright (c) 2015-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# License: BSD

import argparse

from migen import *

from litex_boards.partner.platforms import te0710

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.clock_domains.cd_sys = ClockDomain()

        # # #
        self.cd_sys.clk.attr.add("keep")
        self.submodules.pll = pll = S7PLL(speedgrade=-2)
        self.comb += pll.reset.eq(~platform.request("cpu_reset"))

        pll.register_clkin(platform.request("clk100"), 100e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)


# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(100e6), **kwargs):
        platform = te0710.Platform()

#        SoCCore.__init__(self, platform, sys_clk_freq, **kwargs)

        SoCCore.__init__(self, platform, clk_freq=sys_clk_freq,
            integrated_rom_size=0x8000,
            integrated_main_ram_size=0x8000,
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
    parser = argparse.ArgumentParser(description="LiteX on TE0711")
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
