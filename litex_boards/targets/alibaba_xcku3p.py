#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 Derek Kozel <dkozel@bitstovolts.com
# SPDX-License-Identifier: BSD-2-Clause

import os

from migen import *

from litex.gen import *

from litex_boards.platforms import alibaba_xcku3p

from litex.soc.integration.soc_core import *
from litex.soc.integration.builder  import *

from litex.soc.cores.clock import *
from litex.soc.cores.led   import LedChaser

from litepcie.phy.usppciephy import USPPCIEPHY
from litepcie.software       import generate_litepcie_software

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()

        # Clk.
        clk100 = platform.request("clk100")

        # PLL.
        self.pll = pll = USPMMCM(speedgrade=-2)
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk100, 100e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=100e6,
        with_led_chaser = True,
        with_pcie       = False,
        **kwargs):
        platform = alibaba_xcku3p.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        if kwargs.get("uart_name", "serial") == "serial":
            kwargs["uart_name"] = "jtag_uart" # Defaults to JTAG UART.
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Alibaba Cloud KU3P Board", **kwargs)

        # PCIe -------------------------------------------------------------------------------------
        if with_pcie:
            # Select default x4 PHY (usable subset of x8)
            self.pcie_phy = USPPCIEPHY(
                platform,
                platform.request("pcie_x4"),
                data_width = 128,
                bar0_size  = 0x20000
            )
            self.add_pcie(phy=self.pcie_phy, ndmas=1)

        # LEDs -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=alibaba_xcku3p.Platform, description="LiteX SoC on Alibaba Cloud KU3P board.")
    parser.add_target_argument("--sys-clk-freq", default=100e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-pcie",    action="store_true",       help="Enable PCIe support.")
    parser.add_target_argument("--driver",       action="store_true",       help="Generate PCIe driver.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq = args.sys_clk_freq,
        with_pcie    = args.with_pcie,
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
