#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

import os
import argparse

from migen import *

from litex_boards.platforms import fk33

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser


from litepcie.phy.usppciephy import USPHBMPCIEPHY
from litepcie.core import LitePCIeEndpoint, LitePCIeMSI
from litepcie.frontend.dma import LitePCIeDMA
from litepcie.frontend.wishbone import LitePCIeWishboneBridge
from litepcie.software import generate_litepcie_software

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.clock_domains.cd_sys    = ClockDomain()

        # # #

        self.submodules.pll = pll = USPMMCM(speedgrade=-2)
        pll.register_clkin(platform.request("clk200"), 200e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(125e6), with_pcie=False, **kwargs):
        platform = fk33.Platform()

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident          = "LiteX SoC on FK33",
            ident_version  = True,
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # PCIe -------------------------------------------------------------------------------------
        if with_pcie:
            # PHY
            self.submodules.pcie_phy = USPHBMPCIEPHY(platform, platform.request("pcie_x4"),
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
    parser = argparse.ArgumentParser(description="LiteX SoC on FK33")
    parser.add_argument("--build", action="store_true", help="Build bitstream")
    parser.add_argument("--with-pcie", action="store_true", help="Enable PCIe support")
    parser.add_argument("--driver",    action="store_true", help="Generate PCIe driver")
    parser.add_argument("--load",      action="store_true", help="Load bitstream")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    # Enforce arguments
    args.csr_data_width = 32

    soc =  BaseSoC(with_pcie=args.with_pcie, **soc_core_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.driver:
        generate_litepcie_software(soc, os.path.join(builder.output_dir, "driver"))

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".bit"))

if __name__ == "__main__":
    main()
