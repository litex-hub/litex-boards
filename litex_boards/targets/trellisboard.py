#!/usr/bin/env python3

# This file is Copyright (c) 2019 David Shah <dave@ds0.me>
# License: BSD

import argparse

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex_boards.platforms import trellisboard

from litex.build.lattice.trellis import trellis_args, trellis_argdict

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc_sdram import *
from litex.soc.integration.builder import *

from litedram.modules import MT41J256M16
from litedram.phy import ECP5DDRPHY

from liteeth.phy.ecp5rgmii import LiteEthPHYRGMII

from litesdcard.phy import SDPHY
from litesdcard.core import SDCore
from litesdcard.bist import BISTBlockGenerator, BISTBlockChecker
from litex.soc.cores.timer import Timer

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.clock_domains.cd_init    = ClockDomain()
        self.clock_domains.cd_por     = ClockDomain(reset_less=True)
        self.clock_domains.cd_sys     = ClockDomain()
        self.clock_domains.cd_sys2x   = ClockDomain()
        self.clock_domains.cd_sys2x_i = ClockDomain(reset_less=True)
        self.clock_domains.cd_sd      = ClockDomain()
        self.clock_domains.cd_sd_fb   = ClockDomain()

        # # #

        self.stop = Signal()

        # Clk / Rst
        clk12 = platform.request("clk12")
        rst   = platform.request("user_btn", 0)
        platform.add_period_constraint(clk12, 1e9/12e6)

        # Power on reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += self.cd_por.clk.eq(ClockSignal())
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # PLL
        sys2x_clk_ecsout = Signal()
        self.submodules.pll = pll = ECP5PLL()
        pll.register_clkin(clk12, 12e6)
        pll.create_clkout(self.cd_sys2x_i, 2*sys_clk_freq)
        pll.create_clkout(self.cd_init, 25e6)
        pll.create_clkout(self.cd_sd, 10e6)
        self.specials += [
            Instance("ECLKBRIDGECS",
                i_CLK0   = self.cd_sys2x_i.clk,
                i_SEL    = 0,
                o_ECSOUT = sys2x_clk_ecsout,
            ),
            Instance("ECLKSYNCB",
                i_ECLKI = sys2x_clk_ecsout,
                i_STOP  = self.stop,
                o_ECLKO = self.cd_sys2x.clk),
            Instance("CLKDIVF",
                p_DIV     = "2.0",
                i_ALIGNWD = 0,
                i_CLKI    = self.cd_sys2x.clk,
                i_RST     = self.cd_sys2x.rst,
                o_CDIVX   = self.cd_sys.clk),
            AsyncResetSynchronizer(self.cd_init, ~por_done | ~pll.locked | rst),
            AsyncResetSynchronizer(self.cd_sys,  ~por_done | ~pll.locked | rst)
        ]

        self.comb += platform.request("dram_vtt_en").eq(1)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(75e6), toolchain="trellis", with_ethernet=False, **kwargs):
        platform = trellisboard.Platform(toolchain=toolchain)

        # SoCCore -----------------------------------------------------------------_----------------
        SoCCore.__init__(self, platform, clk_freq=sys_clk_freq, **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.submodules.ddrphy = ECP5DDRPHY(
                platform.request("ddram"),
                sys_clk_freq=sys_clk_freq)
            self.add_csr("ddrphy")
            self.add_constant("ECP5DDRPHY")
            self.add_sdram("sdram",
                phy                     = self.ddrphy,
                module                  = MT41J256M16(sys_clk_freq, "1:2"),
                origin                  = self.mem_map["main_ram"],
                size                    = kwargs.get("max_sdram_size", 0x40000000),
                l2_cache_size           = kwargs.get("l2_size", 8192),
                l2_cache_min_data_width = kwargs.get("min_l2_data_width", 128),
                l2_cache_reverse        = True
            )

        # Ethernet ---------------------------------------------------------------------------------
        if with_ethernet:
            self.submodules.ethphy = LiteEthPHYRGMII(
                clock_pads = self.platform.request("eth_clocks"),
                pads       = self.platform.request("eth"))
            self.add_csr("ethphy")
            self.add_ethernet(phy=self.ethphy)

    def add_sdcard(self):
        sdcard_pads = self.platform.request("sdcard")
        if hasattr(sdcard_pads, "rst"):
            self.comb += sdcard_pads.rst.eq(0)
        self.submodules.sdphy = SDPHY(sdcard_pads, self.platform.device)
        self.submodules.sdcore = SDCore(self.sdphy)
        self.submodules.sdtimer = Timer()
        self.add_csr("sdphy")
        self.add_csr("sdcore")
        self.add_csr("sdtimer")

        self.submodules.bist_generator = BISTBlockGenerator(random=True)
        self.submodules.bist_checker = BISTBlockChecker(random=True)
        self.add_csr("bist_generator")
        self.add_csr("bist_checker")
        self.comb += [
            self.sdcore.source.connect(self.bist_checker.sink),
            self.bist_generator.source.connect(self.sdcore.sink)
        ]
        self.platform.add_period_constraint(self.crg.cd_sd.clk, period_ns(self.sys_clk_freq))
        self.platform.add_period_constraint(self.crg.cd_sd_fb.clk, period_ns(self.sys_clk_freq))
        self.platform.add_false_path_constraints(
            self.crg.cd_sys.clk,
            self.crg.cd_sd.clk,
            self.crg.cd_sd_fb.clk)

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on Trellis Board")
    parser.add_argument("--gateware-toolchain", dest="toolchain", default="trellis",
        help="gateware toolchain to use, trellis (default) or diamond")
    builder_args(parser)
    soc_sdram_args(parser)
    trellis_args(parser)
    parser.add_argument("--sys-clk-freq", default=75e6,
                        help="system clock frequency (default=75MHz)")
    parser.add_argument("--with-ethernet", action="store_true",
                        help="enable Ethernet support")
    parser.add_argument("--with-spi-sdcard", action="store_true",
                        help="enable SPI-mode SDCard support")
    parser.add_argument("--with-sdcard", action="store_true",
                        help="enable SDCard support")
    args = parser.parse_args()

    soc = BaseSoC(sys_clk_freq=int(float(args.sys_clk_freq)),
        with_ethernet=args.with_ethernet,
        **soc_sdram_argdict(args))
    if args.with_spi_sdcard:
        soc.add_spi_sdcard()
    if args.with_sdcard:
        if args.with_spi_sdcard:
            raise ValueError("'--with-spi-sdcard' and '--with-sdcard' are mutually exclusive!")
        soc.add_sdcard()
    builder = Builder(soc, **builder_argdict(args))
    builder_kargs = trellis_argdict(args) if args.toolchain == "trellis" else {}
    builder.build(**builder_kargs)

if __name__ == "__main__":
    main()
