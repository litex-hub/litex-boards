#!/usr/bin/env python3

# This file is Copyright (c) 2019 Antti Lukats <antti.lukats@gmail.com>
# This file is Copyright (c) 2019 msloniewski <marcin.sloniewski@gmail.com>
# This file is Copyright (c) 2019 Florent Kermarrec <florent@enjoy-digital.fr>
# License: BSD

import argparse

from migen import *

from litex_boards.platforms import c10lprefkit

from litex.soc.integration.soc_core import *
from litex.soc.integration.soc_sdram import *
from litex.soc.integration.builder import *

from litedram.modules import MT48LC16M16
from litedram.phy import GENSDRPHY

from liteeth.phy.mii import LiteEthPHYMII
from liteeth.mac import LiteEthMAC

from litex.soc.cores.hyperbus import HyperRAM

# CRG ----------------------------------------------------------------------------------------------
class _CRG(Module):
    def __init__(self, platform):
        self.clock_domains.cd_sys = ClockDomain()
        self.clock_domains.cd_sys_ps = ClockDomain()
        self.clock_domains.cd_por = ClockDomain(reset_less=True)

        # # #

        self.cd_sys.clk.attr.add("keep")
        self.cd_sys_ps.clk.attr.add("keep")
        self.cd_por.clk.attr.add("keep")

        clk12 = platform.request("clk12")

        # power on rst
        rst_n = Signal()
        self.sync.por += rst_n.eq(platform.request("cpu_reset"))
        self.comb += [
            self.cd_por.clk.eq(clk12),
            self.cd_sys.rst.eq(~rst_n),
            self.cd_sys_ps.rst.eq(~rst_n)
        ]

        # sys clk / sdram clk
        clk_outs = Signal(5)
        self.specials += \
            Instance("ALTPLL",
                p_BANDWIDTH_TYPE="AUTO",
                p_CLK0_DIVIDE_BY=6,
                p_CLK0_DUTY_CYCLE=50,
                p_CLK0_MULTIPLY_BY=25,
                p_CLK0_PHASE_SHIFT="0",
                p_CLK1_DIVIDE_BY=6,
                p_CLK1_DUTY_CYCLE=50,
                p_CLK1_MULTIPLY_BY=25,
                p_CLK1_PHASE_SHIFT="-10000",
                p_COMPENSATE_CLOCK="CLK0",
                p_INCLK0_INPUT_FREQUENCY=83000,
                p_INTENDED_DEVICE_FAMILY="MAX 10",
                p_LPM_TYPE="altpll",
                p_OPERATION_MODE="NORMAL",
                i_INCLK=clk12,
                o_CLK=clk_outs,
                i_ARESET=0,
                i_CLKENA=0x3f,
                i_EXTCLKENA=0xf,
                i_FBIN=1,
                i_PFDENA=1,
                i_PLLENA=1,
            )
        self.comb += self.cd_sys.clk.eq(clk_outs[0])
        self.comb += self.cd_sys_ps.clk.eq(clk_outs[1])
        self.comb += platform.request("sdram_clock").eq(self.cd_sys_ps.clk)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCSDRAM):
    mem_map = {
        "hyperram": 0x20000000,
    }
    mem_map.update(SoCCore.mem_map)


    def __init__(self, sys_clk_freq=int(50e6), **kwargs):
        assert sys_clk_freq == int(50e6)
        platform = c10lprefkit.Platform()
        SoCSDRAM.__init__(self, platform, clk_freq=sys_clk_freq,
            integrated_rom_size=0x8000,
            **kwargs)

        self.submodules.crg = _CRG(platform)

        self.submodules.hyperram = HyperRAM(platform.request("hyperram"))
        self.add_wb_slave(mem_decoder(self.mem_map["hyperram"]), self.hyperram.bus)
        self.add_memory_region("hyperram", self.mem_map["hyperram"], 8*1024*1024)

        if not self.integrated_main_ram_size:
            self.submodules.sdrphy = GENSDRPHY(platform.request("sdram"))
            sdram_module = MT48LC16M16(self.clk_freq, "1:1")
            self.register_sdram(self.sdrphy,
                                sdram_module.geom_settings,
                                sdram_module.timing_settings)


class EthernetSoC(BaseSoC):
    mem_map = {
        "ethmac": 0x30000000,  # (shadow @0xb0000000)
    }
    mem_map.update(BaseSoC.mem_map)

    def __init__(self, eth_port=0, **kwargs):
        BaseSoC.__init__(self, **kwargs)

        self.submodules.ethphy = LiteEthPHYMII(self.platform.request("eth_clocks", eth_port),
                                               self.platform.request("eth", eth_port))
        self.add_csr("ethphy")
        self.submodules.ethmac = LiteEthMAC(phy=self.ethphy, dw=32,
            interface="wishbone", endianness=self.cpu.endianness)
        self.add_wb_slave(self.mem_map["ethmac"], self.ethmac.bus, 0x2000)
        self.add_memory_region("ethmac", self.mem_map["ethmac"] | self.shadow_base, 0x2000)
        self.add_csr("ethmac")
        self.add_interrupt("ethmac")

        self.platform.add_period_constraint(self.platform.lookup_request("eth_clocks").tx, 1e9/12.5e6)
        self.platform.add_period_constraint(self.platform.lookup_request("eth_clocks").rx, 1e9/12.5e6)
        self.platform.add_false_path_constraints(
            self.platform.lookup_request("clk12"),
            self.platform.lookup_request("eth_clocks").tx,
            self.platform.lookup_request("eth_clocks").rx
        )

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on C10 LP RefKit")
    builder_args(parser)
    soc_sdram_args(parser)
    parser.add_argument("--with-ethernet", action="store_true",
                        help="enable Ethernet support")
    args = parser.parse_args()

    cls = EthernetSoC if args.with_ethernet else BaseSoC
    soc = cls(**soc_sdram_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder.build()


if __name__ == "__main__":
    main()
