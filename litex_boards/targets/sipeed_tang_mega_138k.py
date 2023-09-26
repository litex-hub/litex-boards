#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022-2023 Icenowy Zheng <uwu@icenowy.me>
# Copyright (c) 2022 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from litex.soc.cores.clock.gowin_gw5a import GW5APLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser, WS2812

from liteeth.phy.gw5rgmii import LiteEthPHYRGMII

from litedram.modules import AS4C32M16
from litedram.phy import GENSDRPHY, HalfRateGENSDRPHY
from litex.build.io import DDROutput

from litex_boards.platforms import sipeed_tang_mega_138k

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_sdram=False):
        self.rst      = Signal()
        self.cd_sys   = ClockDomain()
        self.cd_por   = ClockDomain()
        if with_sdram:
            self.cd_sys_ps = ClockDomain()

        # Clk
        self.clk50 = platform.request("clk50")
        rst = platform.request("rst")

        # Power on reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += self.cd_por.clk.eq(self.clk50)
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # PLL
        self.pll = pll = GW5APLL(devicename=platform.devicename, device=platform.device)
        self.comb += pll.reset.eq(~por_done | self.rst | rst)
        pll.register_clkin(self.clk50, 50e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        if with_sdram:
            pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=90)

        # SDRAM clock
        if with_sdram:
            sdram_clk = ClockSignal("sys_ps")
            self.specials += DDROutput(1, 0, platform.request("sdram_clock"), sdram_clk)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=50e6,
        with_ethernet       = True,
        with_etherbone      = False,
        local_ip            = "192.168.1.50",
        remote_ip           = "",
        eth_dynamic_ip      = False,
        with_sdram          = False,
        with_led_chaser     = True,
        with_rgb_led        = False,
        with_buttons        = True,
        **kwargs):

        platform = sipeed_tang_mega_138k.Platform(toolchain="gowin")

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, with_sdram=with_sdram)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Tang Mega 138K", **kwargs)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("led_n"),
                sys_clk_freq = sys_clk_freq
            )

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            self.ethphy = LiteEthPHYRGMII(
                clock_pads = self.platform.request("eth_clocks"),
                pads       = self.platform.request("eth"),
                tx_delay   = 2e-9,
                rx_delay   = 2e-9)
            self.clk50_half = Signal()
            self.specials += Instance("CLKDIV",
                p_DIV_MODE = "2",
                i_HCLKIN   = self.crg.clk50,
                i_RESETN   = 1,
                i_CALIB    = 0,
                o_CLKOUT   = self.clk50_half)
            self.specials += DDROutput(1, 0, platform.request("ephy_clk"), self.clk50_half)
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy, dynamic_ip=eth_dynamic_ip, data_width=32, software_debug=True)
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, data_width=32)

        if local_ip:
            local_ip = local_ip.split(".")
            self.add_constant("LOCALIP1", int(local_ip[0]))
            self.add_constant("LOCALIP2", int(local_ip[1]))
            self.add_constant("LOCALIP3", int(local_ip[2]))
            self.add_constant("LOCALIP4", int(local_ip[3]))

        if remote_ip:
            remote_ip = remote_ip.split(".")
            self.add_constant("REMOTEIP1", int(remote_ip[0]))
            self.add_constant("REMOTEIP2", int(remote_ip[1]))
            self.add_constant("REMOTEIP3", int(remote_ip[2]))
            self.add_constant("REMOTEIP4", int(remote_ip[3]))

        # SDR SDRAM --------------------------------------------------------------------------------
        if with_sdram and not self.integrated_main_ram_size:
            self.sdrphy = GENSDRPHY(platform.request("sdram"), sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.sdrphy,
                module        = AS4C32M16(sys_clk_freq, "1:1"),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=sipeed_tang_mega_138k.Platform, description="LiteX SoC on Tang Mega 138K.")
    parser.add_target_argument("--flash",           action="store_true",      help="Flash Bitstream.")
    parser.add_target_argument("--sys-clk-freq",    default=50e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-sdram",      action="store_true",      help="Enable optional SDRAM module.")
    ethopts = parser.target_group.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",         action="store_true",      help="Enable Ethernet support.")
    ethopts.add_argument("--with-etherbone",        action="store_true",      help="Enable Etherbone support.")
    parser.add_target_argument("--eth-dynamic-ip",  action="store_true",      help="Enable dynamic Ethernet IP addresses setting.")
    parser.add_target_argument("--remote-ip",       default="192.168.1.100",  help="Remote IP address of TFTP server.")
    parser.add_target_argument("--local-ip",        default="192.168.1.50",   help="Local IP address.")
    args = parser.parse_args()

    assert not (args.with_etherbone and args.eth_dynamic_ip)

    soc = BaseSoC(
        sys_clk_freq        = args.sys_clk_freq,
        with_sdram          = args.with_sdram,
        with_ethernet       = args.with_ethernet,
        with_etherbone      = args.with_etherbone,
        local_ip            = args.local_ip,
        remote_ip           = args.remote_ip,
        eth_dynamic_ip      = args.eth_dynamic_ip,
        **parser.soc_argdict
    )

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.flash(0, builder.get_bitstream_filename(mode="flash", ext=".fs"), external=True)

if __name__ == "__main__":
    main()
