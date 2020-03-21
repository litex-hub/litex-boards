#!/usr/bin/env python3

# This file is Copyright (c) 2018-2019 Rohit Singh <rohit@rohitksingh.in>
# This file is Copyright (c) 2019 Florent Kermarrec <florent@enjoy-digital.fr>
# License: BSD

import argparse
import sys

from migen import *

from litex.build.generic_platform import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc_sdram import *
from litex.soc.integration.builder import *
from litex.soc.cores.clock import *
from litex.soc.cores import dna, xadc
from litex.soc.cores.uart import *
from litex.soc.integration.cpu_interface import get_csr_header

from litedram.modules import MT41J128M16
from litedram.phy import s7ddrphy

from litepcie.phy.s7pciephy import S7PCIEPHY
from litepcie.core import LitePCIeEndpoint, LitePCIeMSI
from litepcie.frontend.dma import LitePCIeDMA
from litepcie.frontend.wishbone import LitePCIeWishboneBridge

from litex_boards.platforms import aller

# CRG ----------------------------------------------------------------------------------------------

class CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.clock_domains.cd_sys       = ClockDomain()
        self.clock_domains.cd_sys4x     = ClockDomain(reset_less=True)
        self.clock_domains.cd_sys4x_dqs = ClockDomain(reset_less=True)
        self.clock_domains.cd_clk200    = ClockDomain()

        clk100 = platform.request("clk100")

        self.submodules.pll = pll = S7PLL()
        pll.register_clkin(clk100, 100e6)
        pll.create_clkout(self.cd_sys,       sys_clk_freq)
        pll.create_clkout(self.cd_sys4x,     4*sys_clk_freq)
        pll.create_clkout(self.cd_sys4x_dqs, 4*sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_clk200,    200e6)

        self.submodules.idelayctrl = S7IDELAYCTRL(self.cd_clk200)

# PCIeSoC -----------------------------------------------------------------------------------------

class PCIeSoC(SoCCore):
    SoCCore.mem_map["csr"] = 0x80000000
    SoCCore.mem_map["rom"] = 0x20000000

    def __init__(self, platform, **kwargs):
        sys_clk_freq = int(100e6)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident = "LiteX SoC on Tagus", ident_version=True,
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = CRG(platform, sys_clk_freq)
        self.add_csr("crg")

        # DNA --------------------------------------------------------------------------------------
        self.submodules.dna = dna.DNA()
        self.add_csr("dna")

        # XADC -------------------------------------------------------------------------------------
        self.submodules.xadc = xadc.XADC()
        self.add_csr("xadc")

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.submodules.ddrphy = s7ddrphy.A7DDRPHY(platform.request("ddram"),
                memtype          = "DDR3",
                nphases          = 4,
                sys_clk_freq     = sys_clk_freq,
                iodelay_clk_freq = 200e6)
            self.add_csr("ddrphy")
            self.add_sdram("sdram",
                phy                     = self.ddrphy,
                module                  = MT41J128M16(sys_clk_freq, "1:4"),
                origin                  = self.mem_map["main_ram"],
                size                    = kwargs.get("max_sdram_size", 0x40000000),
                l2_cache_size           = kwargs.get("l2_size", 8192),
                l2_cache_min_data_width = kwargs.get("min_l2_data_width", 128),
                l2_cache_reverse        = True
            )

        # PCIe -------------------------------------------------------------------------------------
        # pcie phy
        self.submodules.pcie_phy = S7PCIEPHY(platform, platform.request("pcie_x1"), bar0_size=0x20000)
        platform.add_false_path_constraints(self.crg.cd_sys.clk, self.pcie_phy.cd_pcie.clk)
        self.add_csr("pcie_phy")

        # pcie endpoint
        self.submodules.pcie_endpoint = LitePCIeEndpoint(self.pcie_phy)

        # pcie wishbone bridge
        self.submodules.pcie_wishbone = LitePCIeWishboneBridge(self.pcie_endpoint,
            lambda a: 1, base_address=self.mem_map["csr"])
        self.add_wb_master(self.pcie_wishbone.wishbone)

        # pcie dma
        self.submodules.pcie_dma = LitePCIeDMA(self.pcie_phy, self.pcie_endpoint,
            with_buffering=True, buffering_depth=1024, with_loopback=True)
        self.add_csr("pcie_dma")

        # pcie msi
        self.submodules.pcie_msi = LitePCIeMSI()
        self.add_csr("pcie_msi")
        self.comb += self.pcie_msi.source.connect(self.pcie_phy.msi)
        self.msis = {
            "DMA_WRITER": self.pcie_dma.writer.irq,
            "DMA_READER": self.pcie_dma.reader.irq
        }
        for i, (k, v) in enumerate(sorted(self.msis.items())):
            self.comb += self.pcie_msi.irqs[i].eq(v)
            self.add_constant(k + "_INTERRUPT", i)

    def generate_software_header(self, filename):
        csr_header = get_csr_header(self.csr_regions,
                                    self.constants,
                                    with_access_functions=False)
        tools.write_to_file(filename, csr_header)


# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on Tagus")
    builder_args(parser)
    soc_sdram_args(parser)
    args = parser.parse_args()

    args.uart_name = "crossover"
    args.csr_data_width = 32

    platform = aller.Platform()
    soc      = PCIeSoC(platform, **soc_sdram_argdict(args))
    builder  = Builder(soc, **builder_argdict(args))
    vns = builder.build()
    soc.generate_software_header("csr.h")

if __name__ == "__main__":
    main()
