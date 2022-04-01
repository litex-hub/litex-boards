#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

import os

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex_boards.platforms import xcu1525

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litedram.modules import MT40A512M8
from litedram.phy import usddrphy

from litepcie.phy.usppciephy import USPPCIEPHY
from litepcie.software import generate_litepcie_software

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq, ddram_channel):
        self.rst = Signal()
        self.clock_domains.cd_sys    = ClockDomain()
        self.clock_domains.cd_sys4x  = ClockDomain()
        self.clock_domains.cd_pll4x  = ClockDomain()
        self.clock_domains.cd_idelay = ClockDomain()

        # # #

        self.submodules.pll = pll = USPMMCM(speedgrade=-2)
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(platform.request("clk300", ddram_channel), 300e6)
        pll.create_clkout(self.cd_pll4x, sys_clk_freq*4, buf=None, with_reset=False)
        pll.create_clkout(self.cd_idelay, 500e6)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        self.specials += [
            Instance("BUFGCE_DIV", name="main_bufgce_div",
                p_BUFGCE_DIVIDE=4,
                i_CE=1, i_I=self.cd_pll4x.clk, o_O=self.cd_sys.clk),
            Instance("BUFGCE", name="main_bufgce",
                i_CE=1, i_I=self.cd_pll4x.clk, o_O=self.cd_sys4x.clk),
        ]

        self.submodules.idelayctrl = USPIDELAYCTRL(cd_ref=self.cd_idelay, cd_sys=self.cd_sys)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(125e6), ddram_channel=0, with_led_chaser=True,
                 with_pcie=False, with_sata=False, **kwargs):
        platform = xcu1525.Platform()

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident = "LiteX SoC on XCU1525",
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq, ddram_channel)

        # DDR4 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.submodules.ddrphy = usddrphy.USPDDRPHY(
                pads             = platform.request("ddram", ddram_channel),
                memtype          = "DDR4",
                sys_clk_freq     = sys_clk_freq,
                iodelay_clk_freq = 500e6)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT40A512M8(sys_clk_freq, "1:4"),
                size          = 0x40000000,
                l2_cache_size = kwargs.get("l2_size", 8192)
            )
            # Workadound for Vivado 2018.2 DRC, can be ignored and probably fixed on newer Vivado versions.
            platform.add_platform_command("set_property SEVERITY {{Warning}} [get_drc_checks PDCN-2736]")

        # PCIe -------------------------------------------------------------------------------------
        if with_pcie:
            self.submodules.pcie_phy = USPPCIEPHY(platform, platform.request("pcie_x4"),
                data_width = 128,
                bar0_size  = 0x20000)
            self.add_pcie(phy=self.pcie_phy, ndmas=1)

        # SATA -------------------------------------------------------------------------------------
        if with_sata:
            from litex.build.generic_platform import Subsignal, Pins
            from litesata.phy import LiteSATAPHY

            # IOs
            _sata_io = [
                # SFP 2 SATA Adapter / https://shop.trenz-electronic.de/en/TE0424-01-SFP-2-SATA-Adapter
                ("qsfp2sata", 0,
                    Subsignal("tx_p", Pins("N9")),
                    Subsignal("tx_n", Pins("N8")),
                    Subsignal("rx_p", Pins("N4")),
                    Subsignal("rx_n", Pins("N3")),
                ),
            ]
            platform.add_extension(_sata_io)

            # RefClk, Generate 150MHz from PLL.
            self.clock_domains.cd_sata_refclk = ClockDomain()
            self.crg.pll.create_clkout(self.cd_sata_refclk, 150e6)
            sata_refclk = ClockSignal("sata_refclk")

            # PHY
            self.submodules.sata_phy = LiteSATAPHY(platform.device,
                refclk     = sata_refclk,
                pads       = platform.request("qsfp2sata"),
                gen        = "gen2",
                clk_freq   = sys_clk_freq,
                data_width = 16)

            # Core
            self.add_sata(phy=self.sata_phy, mode="read+write")

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on XCU1525")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",         action="store_true", help="Build bitstream.")
    target_group.add_argument("--load",          action="store_true", help="Load bitstream.")
    target_group.add_argument("--sys-clk-freq",  default=125e6,       help="System clock frequency.")
    target_group.add_argument("--ddram-channel", default="0",         help="DDRAM channel (0, 1, 2 or 3).")
    target_group.add_argument("--with-pcie",     action="store_true", help="Enable PCIe support.")
    target_group.add_argument("--driver",        action="store_true", help="Generate PCIe driver.")
    target_group.add_argument("--with-sata",     action="store_true", help="Enable SATA support (over SFP2SATA).")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq  = int(float(args.sys_clk_freq)),
        ddram_channel = int(args.ddram_channel, 0),
        with_pcie     = args.with_pcie,
        with_sata     = args.with_sata,
        **soc_core_argdict(args)
	)
    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.driver:
        generate_litepcie_software(soc, os.path.join(builder.output_dir, "driver"))

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
