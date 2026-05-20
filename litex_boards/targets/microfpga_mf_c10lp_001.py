#!/usr/bin/env python3

# This file is Copyright (c) 2019 Antti Lukats <antti.lukats@gmail.com>
# This file is Copyright (c) 2019 Florent Kermarrec <florent@enjoy-digital.fr>
# License: BSD

import argparse

from migen import *

from litex_boards.platforms import mf_c10lp_001

from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

from onchip_osc import *
from mfio import *

# CRG ----------------------------------------------------------------------------------------------
class _CRG(Module):
    def __init__(self, platform):
        self.clock_domains.cd_sys = ClockDomain()
        self.clock_domains.cd_por = ClockDomain(reset_less=True)

        # kick off onchip oscillator


        self.submodules.osc = osc = onchip_osc(device=platform.device)

        # # #

        self.cd_sys.clk.attr.add("keep")
        self.cd_por.clk.attr.add("keep")

        # power on rst
        rst_n = Signal()
        self.sync.por += rst_n.eq(1)
        self.comb += [
            self.cd_por.clk.eq(osc.clkout),
            self.cd_sys.clk.eq(osc.clkout),
            self.cd_sys.rst.eq(~rst_n)
        ]

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    mem_map = {
        "mfio": 0x20000000
    }
    mem_map.update(SoCCore.mem_map)

    def __init__(self, sys_clk_freq=int(80e6), **kwargs):
        assert sys_clk_freq == int(80e6)
        platform = mf_c10lp_001.Platform()
        SoCCore.__init__(self, platform, clk_freq=sys_clk_freq,
            integrated_rom_size=0x8000,
            integrated_main_ram_size=0x8000,
            uart_name="jtag_atlantic",
            **kwargs)

        self.submodules.crg = _CRG(platform)

        self.counter = counter = Signal(32)
        self.sync += counter.eq(counter + 1)
      
        led0 = platform.request("user_led", 0)
        self.comb += led0.eq(counter[23])

        mfio_pads = platform.request("mfio")
        self.submodules.mfio = mfioBasic(mfio_pads)
        self.add_wb_slave(mem_decoder(self.mem_map["mfio"]), self.mfio.bus)
        self.add_memory_region("mfio", self.mem_map["mfio"], 8*1024*1024)


# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX MicroFPGA SoC on Intel Cyclone 10LP")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    cls = BaseSoC
    soc = cls(**soc_core_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder.build()


if __name__ == "__main__":
    main()
