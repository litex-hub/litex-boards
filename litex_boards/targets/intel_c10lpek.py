#!/usr/bin/env python3

# This file is Copyright (c) 2019 Antti Lukats <antti.lukats@gmail.com>
# This file is Copyright (c) 2019 msloniewski <marcin.sloniewski@gmail.com>
# License: BSD

import argparse

from migen import *

#
# Intel Cyclone 10 LP Eval Kit
#
from litex_boards.partner.platforms import c10lpek

from litex.soc.integration.soc_core import *
from litex.soc.integration.soc_sdram import *

from litex.soc.interconnect import wishbone
#from litex.soc.integration.soc_core import mem_decoder

from litex.soc.integration.builder import *

from litex.soc.cores import gpio

from hyper_memory import *

from atlantic import *

#class ClassicLed(gpio.GPIOOut):
#    def __init__(self, pads):
#        gpio.GPIOOut.__init__(self, pads)

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

        # clock input always available
        clk50 = platform.request("clk50")

        noreset = Signal()
        self.comb += noreset.eq(0)

        # power on rst
        rst = Signal()
        self.sync.por += rst.eq(~platform.request("cpu_reset"))
        self.comb += [
            self.cd_por.clk.eq(clk50),
            self.cd_sys.rst.eq(rst),
            self.cd_sys_ps.rst.eq(rst)
        ]

        clk_outs = Signal(5)

#        self.comb += self.cd_sys.clk.eq(clk_outs[0]) # C0
#        self.comb += self.cd_sys_ps.clk.eq(clk_outs[1]) # C1

        self.comb += self.cd_sys.clk.eq(clk50)

        #
        # PLL we need 2 clocks one system one for SDRAM phase shifter
        # 
        self.specials += \
            Instance("ALTPLL",
                p_BANDWIDTH_TYPE="AUTO",
                p_CLK0_DIVIDE_BY=1,
                p_CLK0_DUTY_CYCLE=50,
                p_CLK0_MULTIPLY_BY=1,
                p_CLK0_PHASE_SHIFT="0",
                p_CLK1_DIVIDE_BY=1,
                p_CLK1_DUTY_CYCLE=50,
                p_CLK1_MULTIPLY_BY=1, 
                p_CLK1_PHASE_SHIFT="-10000",
                p_COMPENSATE_CLOCK="CLK0",
                p_INCLK0_INPUT_FREQUENCY=20000,
                p_INTENDED_DEVICE_FAMILY="Cyclone 10 LP",
                p_LPM_TYPE = "altpll",
                p_OPERATION_MODE = "NORMAL",
                i_INCLK=clk50,
                o_CLK=clk_outs, # we have total max 5 Cx clocks
                i_ARESET = noreset, #~rst_n,
                i_CLKENA=0x3f,
                i_EXTCLKENA=0xf,
                i_FBIN=1,
                i_PFDENA=1,
                i_PLLENA=1,
            )

#        self.specials += \
#            Instance("ALTPLL",
#                p_BANDWIDTH_TYPE="AUTO",
#                p_CLK0_DIVIDE_BY=1, #6,
#                p_CLK0_DUTY_CYCLE=50,
#                p_CLK0_MULTIPLY_BY=2, #25,
#                p_CLK0_PHASE_SHIFT="0",
#                p_CLK1_DIVIDE_BY=1, #6,
#                p_CLK1_DUTY_CYCLE=50,
#                p_CLK1_MULTIPLY_BY=2, #25, 
#                p_CLK1_PHASE_SHIFT="-10000",
#                p_COMPENSATE_CLOCK="CLK0",
#                p_INCLK0_INPUT_FREQUENCY=40000, #83000,
#                p_INTENDED_DEVICE_FAMILY="MAX 10",
#                p_LPM_TYPE = "altpll",
#                p_OPERATION_MODE = "NORMAL",
#                i_INCLK=clk25, #clk12,
#                o_CLK=clk_outs, # we have total max 5 Cx clocks
#                i_ARESET = noreset, #~rst_n,
#                i_CLKENA=0x3f,
#                i_EXTCLKENA=0xf,
#                i_FBIN=1,
#                i_PFDENA=1,
#                i_PLLENA=1,
#            )




# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore, AutoCSR):
    mem_map = {
        "hyperram": 0x20000000,
    }
    mem_map.update(SoCCore.mem_map)

    def __init__(self, sys_clk_freq=int(50e6), **kwargs):
        assert sys_clk_freq == int(50e6)

        platform = c10lpek.Platform()

        SoCSDRAM.__init__(self, platform, clk_freq=sys_clk_freq,
            integrated_rom_size=0x8000,
            with_uart=False, 
#            integrated_main_ram_size=0x4000,
            **kwargs)
 
        self.submodules.crg = _CRG(platform)

        self.add_csr("hyperram", allow_user_defined=True)

        hyperram_pads = platform.request("hyperram")
        self.submodules.hyperram = HyperRAM(hyperram_pads)

        self.add_wb_slave(mem_decoder(self.mem_map["hyperram"]), self.hyperram.bus)
        self.add_memory_region(
            "hyperram", self.mem_map["hyperram"] | self.shadow_base, 8*1024*1024)


        #
        # insert JTAG uart always if with_uart=False ?
        # 
        if not self.with_uart:
            self.submodules.uart = UART_atlantic(platform)
            self.add_csr("uart", allow_user_defined=True)
            self.add_interrupt("uart", allow_user_defined=True)


        self.counter = counter = Signal(32)
        self.sync += counter.eq(counter + 1)
      
        led0 = platform.request("user_led", 0)
        self.comb += led0.eq(counter[23])

#        led1 = platform.request("user_led", 1)
#        self.comb += led1.eq(1)

#        led2 = platform.request("user_led", 2)
#        self.comb += led2.eq(0)

#        led3 = platform.request("user_led", 3)
#        self.comb += led3.eq(1)




class EthernetSoC(BaseSoC):
    mem_map = {
        "ethmac": 0x30000000,  # (shadow @0xb0000000)
    }
    mem_map.update(BaseSoC.mem_map)

    def __init__(self, **kwargs):
        BaseSoC.__init__(self, **kwargs)

        self.submodules.ethphy = LiteEthPHYMII(self.platform.request("eth_clocks"),
                                               self.platform.request("eth"))

#        self.submodules.ethphy = LiteEthPHYMII(self.platform.request("eth2_clocks"),
#                                               self.platform.request("eth2"))

        self.add_csr("ethphy")
        self.submodules.ethmac = LiteEthMAC(phy=self.ethphy, dw=32,
            interface="wishbone", endianness=self.cpu.endianness)
        self.add_wb_slave(self.mem_map["ethmac"], self.ethmac.bus, 0x2000)
        self.add_memory_region("ethmac", self.mem_map["ethmac"] | self.shadow_base, 0x2000)
        self.add_csr("ethmac")
        self.add_interrupt("ethmac")

        self.ethphy.crg.cd_eth_rx.clk.attr.add("keep")
        self.ethphy.crg.cd_eth_tx.clk.attr.add("keep")

#        self.platform.add_period_constraint(self.ethphy.crg.cd_eth_rx.clk, 1e9/12.5e6)
#        self.platform.add_period_constraint(self.ethphy.crg.cd_eth_tx.clk, 1e9/12.5e6)
#        self.platform.add_false_path_constraints(
#            self.crg.cd_sys.clk,
#            self.ethphy.crg.cd_eth_rx.clk,
#            self.ethphy.crg.cd_eth_tx.clk)


        self.platform.add_period_constraint(self.platform.lookup_request("eth_clocks").tx, 1e9/12.5e6)
        self.platform.add_period_constraint(self.platform.lookup_request("eth_clocks").rx, 1e9/12.5e6)
        self.platform.add_false_path_constraints(
            self.platform.lookup_request("clk50"),
            self.platform.lookup_request("eth_clocks").tx,
            self.platform.lookup_request("eth_clocks").rx
        )


        # ila
#        self.platform.add_source("ila.qsys")
#        probe0 = Signal(6)
#        self.comb += probe0.eq(Cat(spi_pads.clk, spi_pads.cs_n, spi_pads.wp, spi_pads.hold, spi_pads.miso, spi_pads.mosi))
#        self.specials += [
#            Instance("ila_0", i_clk=self.crg.cd_sys.clk, i_probe0=probe0),
#            ]
#        platform.toolchain.additional_commands +=  [
#            "write_debug_probes -force {build_name}.ltx",
#        ]


# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on C10 Eval Kit")
    builder_args(parser)
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
