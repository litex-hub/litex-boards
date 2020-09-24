#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2018-2019 Rohit Singh <rohit@rohitksingh.in>
# Copyright (c) 2019 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

import os
import argparse
import sys

from migen import *

from litex_boards.platforms import aller

from litex.soc.interconnect.csr import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc_sdram import *
from litex.soc.integration.builder import *

from litex.soc.cores.clock import *
from litex.soc.cores.led import LedChaser

from litedram.modules import MT41J128M16
from litedram.phy import s7ddrphy

from litepcie.phy.s7pciephy import S7PCIEPHY
from litepcie.core import LitePCIeEndpoint, LitePCIeMSI
from litepcie.frontend.dma import LitePCIeDMA
from litepcie.frontend.wishbone import LitePCIeWishboneBridge
from litepcie.software import generate_litepcie_software

# CRG ----------------------------------------------------------------------------------------------

class CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.clock_domains.cd_sys       = ClockDomain()
        self.clock_domains.cd_sys4x     = ClockDomain(reset_less=True)
        self.clock_domains.cd_sys4x_dqs = ClockDomain(reset_less=True)
        self.clock_domains.cd_clk200    = ClockDomain()

        # Clk/Rst
        clk100 = platform.request("clk100")

        # PLL
        self.submodules.pll = pll = S7PLL()
        pll.register_clkin(clk100, 100e6)
        pll.create_clkout(self.cd_sys,       sys_clk_freq)
        pll.create_clkout(self.cd_sys4x,     4*sys_clk_freq)
        pll.create_clkout(self.cd_sys4x_dqs, 4*sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_clk200,    200e6)

        self.submodules.idelayctrl = S7IDELAYCTRL(self.cd_clk200)

# BaseSoC -----------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, platform, with_pcie=False, **kwargs):
        sys_clk_freq = int(100e6)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident          = "LiteX SoC on Aller",
            ident_version  = True,
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = CRG(platform, sys_clk_freq)
        self.add_csr("crg")

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
        if with_pcie:
            # PHY
            self.submodules.pcie_phy = S7PCIEPHY(platform, platform.request("pcie_x4"),
                data_width = 128,
                bar0_size  = 0x20000)
            platform.add_false_path_constraints(self.crg.cd_sys.clk, self.pcie_phy.cd_pcie.clk)
            self.add_csr("pcie_phy")

            # Endpoint
            self.submodules.pcie_endpoint = LitePCIeEndpoint(self.pcie_phy, max_pending_requests=8)

            # Wishbone bridge
            self.submodules.pcie_bridge = LitePCIeWishboneBridge(self.pcie_endpoint,
                base_address = self.mem_map["csr"])
            self.add_wb_master(self.pcie_bridge.wishbone)

            # DMA0
            self.submodules.pcie_dma0 = LitePCIeDMA(self.pcie_phy, self.pcie_endpoint,
                with_buffering = True, buffering_depth=1024,
                with_loopback  = True)
            self.add_csr("pcie_dma0")

            self.add_constant("DMA_CHANNELS", 1)

            # MSI
            self.submodules.pcie_msi = LitePCIeMSI()
            self.add_csr("pcie_msi")
            self.comb += self.pcie_msi.source.connect(self.pcie_phy.msi)
            self.interrupts = {
                "PCIE_DMA0_WRITER":    self.pcie_dma0.writer.irq,
                "PCIE_DMA0_READER":    self.pcie_dma0.reader.irq,
            }
            for i, (k, v) in enumerate(sorted(self.interrupts.items())):
                self.comb += self.pcie_msi.irqs[i].eq(v)
                self.add_constant(k + "_INTERRUPT", i)

        # Leds -------------------------------------------------------------------------------------
        self.submodules.leds = LedChaser(
            pads         = platform.request_all("user_led"),
            sys_clk_freq = sys_clk_freq)
        self.add_csr("leds")

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on Aller")
    parser.add_argument("--build",     action="store_true", help="Build bitstream")
    parser.add_argument("--with-pcie", action="store_true", help="Enable PCIe support")
    parser.add_argument("--driver",    action="store_true", help="Generate LitePCIe driver")
    parser.add_argument("--load",      action="store_true", help="Load bitstream")
    builder_args(parser)
    soc_sdram_args(parser)
    args = parser.parse_args()

    # Enforce arguments
    args.csr_data_width = 32

    platform = aller.Platform()
    soc      = BaseSoC(platform, with_pcie=args.with_pcie, **soc_sdram_argdict(args))
    builder  = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.driver:
        generate_litepcie_software(soc, os.path.join(builder.output_dir, "driver"))

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".bit"))

if __name__ == "__main__":
    main()
