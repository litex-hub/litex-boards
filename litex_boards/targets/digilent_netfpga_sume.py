#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019-2024 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2024 Gustavo Bastos <gustavocerq7gmail.com> 
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import *

from litex_boards.platforms import digilent_netfpga_sume

from litex.soc.cores.clock import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.bitbang import I2CMaster

from litedram.modules import MT8KTF51264
from litedram.phy import s7ddrphy

from litedram.common import PHYPadsReducer

from liteeth.phy.s7rgmii import LiteEthPHYRGMII
from liteeth.phy.v7_1000basex import V7_1000BASEX
from liteeth.phy import LiteEthPHY

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst          = Signal()
        self.cd_sys       = ClockDomain()
        self.cd_sys4x     = ClockDomain()
        self.cd_idelay = ClockDomain()
        self.cd_sfp   = ClockDomain()
   
        self.pll = pll = S7PLL(speedgrade = -2)
        self.comb += pll.reset.eq(platform.request("cpu_reset_n") | self.rst)
        pll.register_clkin(platform.request("clk200"), 200e6)
        pll.create_clkout(self.cd_sys,       sys_clk_freq)
        pll.create_clkout(self.cd_sys4x,     4*sys_clk_freq)
        pll.create_clkout(self.cd_idelay,    200e6)
        pll.create_clkout(self.cd_sfp,    200e6)
        
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        self.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=125e6,
        with_ethernet          = False,
        with_etherbone         = False,
        with_led_chaser        = True,
        with_i2c               = False,
        **kwargs):
        platform = digilent_netfpga_sume.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------_-----------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on NetFPGA-Sume", **kwargs)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
             self.ddrphy = s7ddrphy.V7DDRPHY(platform.request("ddram"),
                memtype          = "DDR3",
                nphases          = 4,
                sys_clk_freq     = sys_clk_freq
            )
             self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT8KTF51264(sys_clk_freq, "1:4"),
                size          = 0x40000000,
                l2_cache_size = kwargs.get("l2_size", 8192),
            )
            
        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            self.ethphy = V7_1000BASEX(
                refclk_or_clk_pads = self.crg.cd_sfp.clk,
                data_pads          = self.platform.request("sfp"),
                sys_clk_freq       = sys_clk_freq,
                with_csr           = True
            )                    
            self.comb += self.platform.request("sfp_tx_disable_n").eq(1)
            platform.add_platform_command("set_property SEVERITY {{Warning}} [get_drc_checks UCIO-1]")
            platform.add_platform_command("set_property SEVERITY {{Warning}} [get_drc_checks REQP-44]")
        if with_ethernet:
                self.add_ethernet(phy=self.ethphy)
        if with_etherbone:
                self.add_etherbone(phy=self.ethphy)
                
        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)
                
        # I2C Bus ----------------------------------------------------------------------------------
        if with_i2c:
            self.i2c = I2CMaster(platform.request("i2c"))
            self.add_csr("i2c")
# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=digilent_netfpga_sume.Platform, description="LiteX SoC on NetFPGA-Sume.")
    parser.add_target_argument("--sys-clk-freq", default=125e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-i2c",             action="store_true",     help="Enable I2C support.")
    ethopts = parser.target_group.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",  action="store_true", help="Enable Ethernet support.")
    ethopts.add_argument("--with-etherbone", action="store_true", help="Enable Etherbone support.")
    sdopts = parser.target_group.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-sdcard",        action="store_true", help="Enable SPI-mode SDCard support.")
    sdopts.add_argument("--with-sdcard",            action="store_true", help="Enable SDCard support.")
    
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq           = args.sys_clk_freq,
        with_ethernet          = args.with_ethernet,
        with_etherbone         = args.with_etherbone,
        with_i2c               = args.with_i2c,
        **parser.soc_argdict
    )
    
    if args.with_spi_sdcard:
        soc.add_spi_sdcard()
    if args.with_sdcard:
        soc.add_sdcard()
        
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
