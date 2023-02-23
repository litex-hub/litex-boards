#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2022 Sylvain Munaut <tnt@246tNt.com>
# SPDX-License-Identifier: BSD-2-Clause

import os

from migen import *

from litex.gen import *

from litex_boards.platforms import adi_adrv2crr_fmc

from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

from litex.soc.cores.clock import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.pwm import PWM
from litex.soc.cores.xadc import ZynqUSPSystemMonitor

from litedram.modules import MT40A512M16
from litedram.phy import usddrphy

from litepcie.phy.usppciephy import USPPCIEPHY
from litepcie.software import generate_litepcie_software

# CRG ----------------------------------------------------------------------------------------------

class CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, ddram_channel):
        self.rst       = Signal()
        self.cd_sys    = ClockDomain()
        self.cd_sys4x  = ClockDomain()
        self.cd_pll4x  = ClockDomain()
        self.cd_idelay = ClockDomain()

        # # #

        self.pll = pll = USPMMCM(speedgrade=-1)
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(platform.request("ddram_refclk", ddram_channel), 300e6)
        pll.create_clkout(self.cd_pll4x, sys_clk_freq*4, buf=None, with_reset=False)
        pll.create_clkout(self.cd_idelay, 400e6)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        self.specials += [
            Instance("BUFGCE_DIV",
                p_BUFGCE_DIVIDE=4,
                i_CE=1, i_I=self.cd_pll4x.clk, o_O=self.cd_sys.clk),
            Instance("BUFGCE",
                i_CE=1, i_I=self.cd_pll4x.clk, o_O=self.cd_sys4x.clk),
        ]

        self.idelayctrl = USPIDELAYCTRL(cd_ref=self.cd_idelay, cd_sys=self.cd_sys)

# BaseSoC -----------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=150e6, ddram_channel=0,
        with_led_chaser = True,
        with_pcie       = False,
        **kwargs):
        platform = adi_adrv2crr_fmc.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = CRG(platform, sys_clk_freq, ddram_channel)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on ADI ADRV2CRR-FMC", **kwargs)

        # DDR4 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.ddrphy = usddrphy.USPDDRPHY(
                pads             = platform.request("ddram", ddram_channel),
                memtype          = "DDR4",
                sys_clk_freq     = sys_clk_freq,
                iodelay_clk_freq = 400e6)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT40A512M16(sys_clk_freq, "1:4"),
                size          = 0x40000000,
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # PCIe -------------------------------------------------------------------------------------
        if with_pcie:
            assert self.csr_data_width == 32

            self.pcie_phy = USPPCIEPHY(platform, platform.request("pcie_x4"),
                speed = "gen3",
                data_width = 128,
                bar0_size  = 0x20000)
            self.add_pcie(phy=self.pcie_phy, ndmas=1)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

        # Fan --------------------------------------------------------------------------------------
            # Full speed is _really_ loud and with this demo bitstream which is almost
            # empty, we can slow it way down and still keep the FPGA < 10C above ambient
        self.fan = PWM(
            default_enable =    1,
            default_period = 2500,
            default_width  =  500
        )

        self.comb += platform.request("fan").pwm_n.eq(~self.fan.pwm)

        # SYSMON -----------------------------------------------------------------------------------
        self.sysmon = ZynqUSPSystemMonitor()

        # JTAG -------------------------------------------------------------------------------------
        self.add_jtagbone()

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=adi_adrv2crr_fmc.Platform, description="LiteX SoC on ADI ADRV2CRR-FMC.")
    parser.add_target_argument("--sys-clk-freq", default=150e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-pcie",    action="store_true",       help="Enable PCIe support.")
    parser.add_target_argument("--driver",       action="store_true",       help="Generate PCIe driver.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq = args.sys_clk_freq,
        with_pcie    = args.with_pcie,
        **parser.soc_argdict
    )

    builder  = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.driver:
        generate_litepcie_software(soc, os.path.join(builder.output_dir, "driver"))

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
