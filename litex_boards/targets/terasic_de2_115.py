#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2015-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from litex.build.io import DDROutput

from litex_boards.platforms import terasic_de2_115

from litex.soc.cores.clock import CycloneIVPLL
from litex.soc.cores.led import LedChaser
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

from litedram.modules import IS42S16320
from litedram.phy import GENSDRPHY

from liteeth.phy.mii import LiteEthPHYMII

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst       = Signal()
        self.cd_sys    = ClockDomain()
        self.cd_sys_ps = ClockDomain()

        # # #

        # Clk / Rst
        clk50 = platform.request("clk50")

        # PLL
        self.pll = pll = CycloneIVPLL(speedgrade="-7")
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk50, 50e6)
        pll.create_clkout(self.cd_sys,    sys_clk_freq)
        pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=90)

        # SDRAM clock
        self.specials += DDROutput(1, 0, platform.request("sdram_clock"), ClockSignal("sys_ps"))

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=50e6,
        with_ethernet   = False,
        with_etherbone  = False,
        with_sdcard     = False,
        with_led_chaser = True,
        ethernet_phy    = 0,
        etherbone_ip    = "192.168.1.50",
        etherbone_phy   = 1,
        **kwargs,
    ):
        platform = terasic_de2_115.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on DE2-115", **kwargs)

        # SDR SDRAM --------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.sdrphy = GENSDRPHY(platform.request("sdram"), sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.sdrphy,
                module        = IS42S16320(self.clk_freq, "1:1"),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Add debug interface if the CPU has one ---------------------------------------------------
        if hasattr(self.cpu, "debug_bus"):
            self.register_mem(
                name      = "vexriscv_debug",
                address   = 0xF00F0000,
                interface = self.cpu.debug_bus,
                size      = 0x100,
            )

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads = platform.request_all("user_led"), sys_clk_freq=sys_clk_freq
            )
            self.leds.add_pwm()

        # SD Card ----------------------------------------------------------------------------------
        if with_sdcard:
            self.add_sdcard()

        # Ethernet ---------------------------------------------------------------------------------
        if with_ethernet:
            # Ethernet PHY
            self.submodules.ethphy = LiteEthPHYMII(
                clock_pads = platform.request("eth_clocks", ethernet_phy),
                pads       = platform.request("eth", ethernet_phy),
            )
            self.add_ethernet(
                phy        = self.ethphy,
                phy_cd     = "ethphy_eth" if with_etherbone else "eth",
                dynamic_ip = True,
            )
        if with_etherbone:
            # Ethernet PHY
            self.submodules.ethbphy = LiteEthPHYMII(
                clock_pads = platform.request("eth_clocks", etherbone_phy),
                pads       = platform.request("eth", etherbone_phy),
            )
            self.add_etherbone(
                phy        = self.ethbphy,
                phy_cd     = "ethbphy_eth" if with_ethernet else "eth",
                ip_address = etherbone_ip,
            )

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=terasic_de2_115.Platform, description="LiteX SoC on DE2-115.")

    parser.add_target_argument("--sys-clk-freq",    default=50e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-led-chaser", action="store_true",      help="Enable LED chaser.")
    parser.add_target_argument("--with-sdcard",     action="store_true",      help="Enable SD card support.")
    parser.add_target_argument("--with-ethernet",   action="store_true",      help="Enable Ethernet support.")
    parser.add_target_argument("--with-etherbone",  action="store_true",      help="Enable Etherbone support.")
    parser.add_target_argument("--etherbone-ip",    default="192.168.48.100", help="Etherbone IP address.")
    parser.add_target_argument("--etherbone-phy",   default=1, type=int,      help="Etherbone PHY (0 or 1).")
    parser.add_target_argument("--ethernet-phy",    default=0, type=int,      help="Ethernet  PHY (0 or 1).")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq    = args.sys_clk_freq,
        with_sdcard     = args.with_sdcard,
        with_ethernet   = args.with_ethernet,
        with_etherbone  = args.with_etherbone,
        with_led_chaser = args.with_led_chaser,
        etherbone_ip    = args.etherbone_ip,
        etherbone_phy   = args.etherbone_phy,
        ethernet_phy    = args.ethernet_phy,
        **parser.soc_argdict,
    )

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
