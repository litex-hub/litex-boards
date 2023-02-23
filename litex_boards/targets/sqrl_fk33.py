#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020-2022 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# Build/Use:
# python3 -m litex_boards.targets.sqrl_fk33 --with-hbm --sys-clk-freq=250e6 --csr-csv=csr.csv --build --load
# litex_server --jtag --jtag-config=openocd_xc7_ft2232.cfg --jtag-chain=2
# litex_term crossover

import os

from migen import *

from litex.gen import *

from litex_boards.platforms import sqrl_fk33

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.interconnect.axi import *
from litex.soc.cores.ram.xilinx_usp_hbm2 import USPHBM2
from litex.soc.cores.led import LedChaser

from litepcie.phy.usppciephy import USPHBMPCIEPHY
from litepcie.core import LitePCIeEndpoint, LitePCIeMSI
from litepcie.frontend.dma import LitePCIeDMA
from litepcie.frontend.wishbone import LitePCIeWishboneBridge
from litepcie.software import generate_litepcie_software

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_hbm):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()
        if with_hbm:
            self.cd_hbm_ref = ClockDomain()
            self.cd_apb     = ClockDomain()

        # # #

        self.pll = pll = USPMMCM(speedgrade=-2)
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(platform.request("clk200"), 200e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        if with_hbm:
            pll.create_clkout(self.cd_hbm_ref, 100e6)
            pll.create_clkout(self.cd_apb,     100e6)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=125e6,
        with_led_chaser = True,
        with_pcie       = False,
        with_hbm        = False,
        **kwargs):
        platform = sqrl_fk33.Platform()
        if with_hbm:
            assert 225e6 <= sys_clk_freq <= 450e6

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, with_hbm)

        # SoCCore ----------------------------------------------------------------------------------
        if kwargs.get("uart_name", "serial") == "serial":
            kwargs["uart_name"] = "crossover" # Defaults to Crossover-UART.
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on FK33", **kwargs)

        # JTAGBone --------------------------------------------------------------------------------
        self.add_jtagbone(chain=2) # Chain 1 already used by HBM2 debug probes.

        # HBM --------------------------------------------------------------------------------------
        if with_hbm:
            # Add HBM Core.
            self.hbm = hbm = ClockDomainsRenamer({"axi": "sys"})(USPHBM2(platform))

            # Get HBM .xci.
            os.system("wget https://github.com/litex-hub/litex-boards/files/8178874/hbm_0.xci.txt")
            os.makedirs("ip/hbm", exist_ok=True)
            os.system("mv hbm_0.xci.txt ip/hbm/hbm_0.xci")

            # Connect four of the HBM's AXI interfaces to the main bus of the SoC.
            for i in range(4):
                axi_hbm      = hbm.axi[i]
                axi_lite_hbm = AXILiteInterface(data_width=256, address_width=33)
                self.submodules += AXILite2AXI(axi_lite_hbm, axi_hbm)
                self.bus.add_slave(f"hbm{i}", axi_lite_hbm, SoCRegion(origin=0x4000_0000 + 0x1000_0000*i, size=0x1000_0000)) # 256MB.
            # Link HBM2 channel 0 as main RAM
            self.bus.add_region("main_ram", SoCRegion(origin=0x4000_0000, size=0x1000_0000, linker=True)) # 256MB.

        # PCIe -------------------------------------------------------------------------------------
        if with_pcie:
            assert self.csr_data_width == 32
            # PHY
            self.pcie_phy = USPHBMPCIEPHY(platform, platform.request("pcie_x4"),
                data_width = 128,
                bar0_size  = 0x20000)

            # Endpoint
            self.pcie_endpoint = LitePCIeEndpoint(self.pcie_phy, max_pending_requests=8)

            # Wishbone bridge
            self.pcie_bridge = LitePCIeWishboneBridge(self.pcie_endpoint,
                base_address = self.mem_map["csr"])
            self.bus.add_master(master=self.pcie_bridge.wishbone)

            # DMA0
            self.pcie_dma0 = LitePCIeDMA(self.pcie_phy, self.pcie_endpoint,
                with_buffering = True, buffering_depth=1024,
                with_loopback  = True)

            self.add_constant("DMA_CHANNELS", 1)

            # MSI
            self.pcie_msi = LitePCIeMSI()
            self.comb += self.pcie_msi.source.connect(self.pcie_phy.msi)
            self.interrupts = {
                "PCIE_DMA0_WRITER":    self.pcie_dma0.writer.irq,
                "PCIE_DMA0_READER":    self.pcie_dma0.reader.irq,
            }
            for i, (k, v) in enumerate(sorted(self.interrupts.items())):
                self.comb += self.pcie_msi.irqs[i].eq(v)
                self.add_constant(k + "_INTERRUPT", i)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=sqrl_fk33.Platform, description="LiteX SoC on FK33.")
    parser.add_target_argument("--sys-clk-freq", default=125e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-pcie",    action="store_true",       help="Enable PCIe support.")
    parser.add_target_argument("--with-hbm",     action="store_true",       help="Use HBM2.")
    parser.add_target_argument("--driver",       action="store_true",       help="Generate PCIe driver.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq = args.sys_clk_freq,
        with_pcie    = args.with_pcie,
        with_hbm     = args.with_hbm,
        **parser.soc_argdict
    )
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.driver:
        generate_litepcie_software(soc, os.path.join(builder.output_dir, "driver"))

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
