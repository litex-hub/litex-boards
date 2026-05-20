#!/usr/bin/env python3

# This file is Copyright (c) 2019 Antti Lukats <antti.lukats@gmail.com>
# This file is Copyright (c) 2015-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# License: BSD

import argparse

from migen import *

from litex_boards.partner.platforms import mega65

from litex.soc.interconnect import wishbone

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

from litex.soc.cores.hyperbus import HyperRAM

from liteeth.phy.rmii import LiteEthPHYRMII
from liteeth.mac import LiteEthMAC


#from hyper_memory import *
#self.submodules.hyperram = HyperRAM(platform.request("hyperram"))
#self.add_wb_slave(mem_decoder(self.mem_map["hyperram"]), self.hyperram.bus)
#self.add_memory_region("hyperram", self.mem_map["hyperram"], 8*1024*1024)


# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.clock_domains.cd_sys = ClockDomain()
        self.clock_domains.cd_eth = ClockDomain()

        # # #
        self.cd_sys.clk.attr.add("keep")
        self.submodules.pll = pll = S7PLL(speedgrade=-1)
        self.comb += pll.reset.eq(platform.request("cpu_reset"))

        pll.register_clkin(platform.request("clk100"), 100e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        pll.create_clkout(self.cd_eth, 50e6)


# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    mem_map = {
#        "spiflash": 0x20000000,
        "hyperram": 0x20000000,
    }
    mem_map.update(SoCCore.mem_map)

    def __init__(self, sys_clk_freq=int(100e6), **kwargs):
        platform = mega65.Platform()

        SoCCore.__init__(self, platform, clk_freq=sys_clk_freq,
            ident="MEGA65", ident_version=True,
            integrated_rom_size=0x8000,
            integrated_main_ram_size=0x10000,
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


#        hyperram_pads = platform.request("hyperram")
#        self.submodules.hyperram = HyperRAM(hyperram_pads)
#        self.add_wb_slave(mem_decoder(self.mem_map["hyperram"]), self.hyperram.bus)
#        self.add_memory_region("hyperram", self.mem_map["hyperram"] | self.shadow_base, 8*1024*1024)

        self.submodules.hyperram = HyperRAM(platform.request("hyperram"))
        self.add_wb_slave(mem_decoder(self.mem_map["hyperram"]), self.hyperram.bus)
        self.add_memory_region("hyperram", self.mem_map["hyperram"], 8*1024*1024)



class EthernetSoC(BaseSoC):
    mem_map = {
        "ethmac": 0x30000000,  # (shadow @0xb0000000)
    }
    mem_map.update(BaseSoC.mem_map)

    def __init__(self, **kwargs):
        BaseSoC.__init__(self, **kwargs)

        self.submodules.ethphy = LiteEthPHYRMII(self.platform.request("eth_clocks"),
                                                self.platform.request("eth"))
        self.add_csr("ethphy")
        self.submodules.ethmac = LiteEthMAC(phy=self.ethphy, dw=32,
            interface="wishbone", endianness=self.cpu.endianness)
        self.add_wb_slave(self.mem_map["ethmac"], self.ethmac.bus, 0x2000)
        self.add_memory_region("ethmac", self.mem_map["ethmac"] | self.shadow_base, 0x2000)
        self.add_csr("ethmac")
        self.add_interrupt("ethmac")

        self.ethphy.crg.cd_eth_rx.clk.attr.add("keep")
        self.ethphy.crg.cd_eth_tx.clk.attr.add("keep")
        self.platform.add_period_constraint(self.ethphy.crg.cd_eth_rx.clk, 1e9/12.5e6)
        self.platform.add_period_constraint(self.ethphy.crg.cd_eth_tx.clk, 1e9/12.5e6)
        self.platform.add_false_path_constraints(
            self.crg.cd_sys.clk,
            self.ethphy.crg.cd_eth_rx.clk,
            self.ethphy.crg.cd_eth_tx.clk)


# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX on MEGA65")
    builder_args(parser)
#    soc_sdram_args(parser)
    soc_core_args(parser)

    parser.add_argument("--with-ethernet", action="store_true",
                        help="enable Ethernet support")

    args = parser.parse_args()

    cls = EthernetSoC if args.with_ethernet else BaseSoC
    soc = cls(**soc_core_argdict(args))

    builder = Builder(soc, **builder_argdict(args))
    builder.build()


if __name__ == "__main__":
    main()
