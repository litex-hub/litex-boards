#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Sergiu Mosanu <sm7ed@virginia.edu>
# Copyright (c) 2020-2021 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2020 Antmicro <www.antmicro.com>
#
# SPDX-License-Identifier: BSD-2-Clause

# To interface via the serial port use:
#     lxterm /dev/ttyUSBx --speed=115200

import os

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from litex_boards.platforms import xilinx_alveo_u280

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.interconnect.axi import *
from litex.soc.interconnect.csr import *
from litex.soc.cores.ram.xilinx_usp_hbm2 import USPHBM2

from litex.soc.cores.led import LedChaser
from litedram.modules import MTA18ASF2G72PZ
from litedram.phy import usddrphy

from litepcie.phy.usppciephy import USPPCIEPHY
from litepcie.software import generate_litepcie_software

from litedram.common import *
from litedram.frontend.axi import *

from litescope import LiteScopeAnalyzer

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, ddram_channel, with_hbm):
        if with_hbm:
            self.rst        = Signal()
            self.cd_sys     = ClockDomain()
            self.cd_hbm_ref = ClockDomain()
            self.cd_apb     = ClockDomain()
        else: # ddr4
            self.rst = Signal()
            self.cd_sys    = ClockDomain()
            self.cd_sys4x  = ClockDomain()
            self.cd_pll4x  = ClockDomain()
            self.cd_idelay = ClockDomain()

        # # #

        if with_hbm:
            self.pll = pll = USMMCM(speedgrade=-2)
            self.comb += pll.reset.eq(self.rst)
            pll.register_clkin(platform.request("sysclk", ddram_channel), 100e6)
            pll.create_clkout(self.cd_sys,     sys_clk_freq)
            pll.create_clkout(self.cd_hbm_ref, 100e6)
            pll.create_clkout(self.cd_apb,     100e6)
            platform.add_false_path_constraints(self.cd_sys.clk, self.cd_apb.clk)
        else: # ddr4
            self.pll = pll = USMMCM(speedgrade=-2)
            self.comb += pll.reset.eq(self.rst)
            pll.register_clkin(platform.request("sysclk", ddram_channel), 100e6)
            pll.create_clkout(self.cd_pll4x, sys_clk_freq*4, buf=None, with_reset=False)
            pll.create_clkout(self.cd_idelay, 600e6) #, with_reset=False
            platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

            self.specials += [
                Instance("BUFGCE_DIV",
                    p_BUFGCE_DIVIDE=4,
                    i_CE=1, i_I=self.cd_pll4x.clk, o_O=self.cd_sys.clk),
                Instance("BUFGCE",
                    i_CE=1, i_I=self.cd_pll4x.clk, o_O=self.cd_sys4x.clk),
                # AsyncResetSynchronizer(self.cd_idelay, ~pll.locked),
            ]

            self.idelayctrl = USIDELAYCTRL(cd_ref=self.cd_idelay, cd_sys=self.cd_sys)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=150e6, ddram_channel=0,
        with_pcie       = False,
        with_led_chaser = False,
        with_hbm        = False,
        **kwargs):
        platform = xilinx_alveo_u280.Platform()
        if with_hbm:
            assert 225e6 <= sys_clk_freq <= 450e6

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, ddram_channel, with_hbm)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Alveo U280 (ES1)", **kwargs)

        # HBM / DRAM -------------------------------------------------------------------------------
        if with_hbm:
            # JTAGBone -----------------------------------------------------------------------------
            #self.add_jtagbone(chain=2) # Chain 1 already used by HBM2 debug probes.

            # Add HBM Core.
            self.hbm = hbm = ClockDomainsRenamer({"axi": "sys"})(USPHBM2(platform))

            # Get HBM .xci.
            os.system("wget https://github.com/litex-hub/litex-boards/files/6893157/hbm_0.xci.txt")
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

        else:
            # DDR4 SDRAM -------------------------------------------------------------------------------
            if not self.integrated_main_ram_size:
                self.ddrphy = usddrphy.USPDDRPHY(platform.request("ddram", ddram_channel),
                    memtype          = "DDR4",
                    cmd_latency      = 1, # seems to work better with cmd_latency=1
                    sys_clk_freq     = sys_clk_freq,
                    iodelay_clk_freq = 600e6,
                    is_rdimm         = True)
                self.add_sdram("sdram",
                    phy           = self.ddrphy,
                    module        = MTA18ASF2G72PZ(sys_clk_freq, "1:4"),
                    size          = 0x40000000,
                    l2_cache_size = kwargs.get("l2_size", 8192)
                )

            # Firmware RAM (To ease initial LiteDRAM calibration support) --------------------------
            self.add_ram("firmware_ram", 0x20000000, 0x8000)

        # PCIe -------------------------------------------------------------------------------------
        if with_pcie:
            self.pcie_phy = USPPCIEPHY(platform, platform.request("pcie_x4"),
                data_width = 128,
                bar0_size  = 0x20000)
            self.add_pcie(phy=self.pcie_phy, ndmas=1)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("gpio_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=xilinx_alveo_u280.Platform, description="LiteX SoC on Alveo U280.")
    parser.add_target_argument("--sys-clk-freq",    default=150e6, type=float, help="System clock frequency.") # HBM2 with 250MHz, DDR4 with 150MHz (1:4)
    parser.add_target_argument("--ddram-channel",   default="0",               help="DDRAM channel (0, 1, 2 or 3).") # also selects clk 0 or 1
    parser.add_target_argument("--with-pcie",       action="store_true",       help="Enable PCIe support.")
    parser.add_target_argument("--driver",          action="store_true",       help="Generate PCIe driver.")
    parser.add_target_argument("--with-hbm",        action="store_true",       help="Use HBM2.")
    parser.add_target_argument("--with-analyzer",   action="store_true",       help="Enable Analyzer.")
    parser.add_target_argument("--with-led-chaser", action="store_true",       help="Enable LED Chaser.")
    args = parser.parse_args()

    if args.with_hbm:
        args.sys_clk_freq = 250e6

    soc = BaseSoC(
        sys_clk_freq    = args.sys_clk_freq,
        ddram_channel   = int(args.ddram_channel, 0),
        with_pcie       = args.with_pcie,
        with_led_chaser = args.with_led_chaser,
        with_hbm        = args.with_hbm,
        with_analyzer   = args.with_analyzer,
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
