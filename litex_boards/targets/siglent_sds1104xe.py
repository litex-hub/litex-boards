#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# Build/Use ----------------------------------------------------------------------------------------
# Build/Load bitstream:
# ./siglent_ds1104xe.py --with-etherbone --uart-name=crossover --csr-csv=csr.csv --build --load
#
# Test Ethernet:
# ping 192.168.1.50
#
# Test Console:
# litex_server --udp
# litex_term crossover
# --------------------------------------------------------------------------------------------------

from migen import *

from litex.gen import *

from litex_boards.platforms import siglent_sds1104xe

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.video import VideoVGAPHY

from litedram.common import PHYPadsReducer
from litedram.modules import MT41K64M16
from litedram.phy import s7ddrphy

from liteeth.phy.mii import LiteEthPHYMII

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_ethernet=False):
        self.rst          = Signal()
        self.cd_sys       = ClockDomain()
        self.cd_sys4x     = ClockDomain()
        self.cd_sys4x_dqs = ClockDomain()
        self.cd_idelay    = ClockDomain()
        self.cd_dvi       = ClockDomain()

        # # #

        # Clk / Rst
        clk25 = ClockSignal("eth_tx") if with_ethernet else platform.request("eth_clocks").rx

        # PLL
        self.pll = pll = S7PLL(speedgrade=-1)
        pll.register_clkin(clk25, 25e6)
        pll.create_clkout(self.cd_sys,       sys_clk_freq)
        pll.create_clkout(self.cd_sys4x,     4*sys_clk_freq)
        pll.create_clkout(self.cd_sys4x_dqs, 4*sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_idelay,    200e6)
        pll.create_clkout(self.cd_dvi,       33.3e6)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        self.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=100e6,
        with_etherbone         = True,
        eth_ip                 = "192.168.1.50",
        with_video_terminal    = False,
        with_video_framebuffer = False,
        **kwargs):
        platform = siglent_sds1104xe.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, with_ethernet=with_etherbone)

        # SoCCore ----------------------------------------------------------------------------------
        if kwargs.get("uart_name", "serial") == "serial":
            kwargs["uart_name"] = "crossover" # Defaults to Crossover UART.
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Siglent SDS1104X-E", **kwargs)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.ddrphy = s7ddrphy.A7DDRPHY(
                pads           = PHYPadsReducer(platform.request("ddram"), [0, 1, 2, 3]),
                memtype        = "DDR3",
                nphases        = 4,
                sys_clk_freq   = sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT41K64M16(sys_clk_freq, "1:4"),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Etherbone --------------------------------------------------------------------------------
        if with_etherbone:
            # FIXME: Simplify LiteEth Hybrid MAC integration.
            from liteeth.common import convert_ip
            from liteeth.mac import LiteEthMAC
            from liteeth.core.arp import LiteEthARP
            from liteeth.core.ip import LiteEthIP
            from liteeth.core.udp import LiteEthUDP
            from liteeth.core.icmp import LiteEthICMP
            from liteeth.core import LiteEthUDPIPCore
            from liteeth.frontend.etherbone import LiteEthEtherbone

            # Ethernet PHY
            self.ethphy = LiteEthPHYMII(
                clock_pads = self.platform.request("eth_clocks"),
                pads       = self.platform.request("eth"))
            etherbone_ip_address  = convert_ip("192.168.1.51")
            etherbone_mac_address = 0x10e2d5000001

            # Ethernet MAC
            self.ethmac = LiteEthMAC(phy=self.ethphy, dw=8,
                interface  = "hybrid",
                endianness = self.cpu.endianness,
                hw_mac     = etherbone_mac_address)

            # Software Interface.
            self.add_memory_region("ethmac", getattr(self.mem_map, "ethmac", None), 0x2000, type="io")
            self.add_wb_slave(self.mem_regions["ethmac"].origin, self.ethmac.bus, 0x2000)
            if self.irq.enabled:
                self.irq.add("ethmac", use_loc_if_exists=True)

            # Hardware Interface.
            self.arp  = LiteEthARP(self.ethmac, etherbone_mac_address, etherbone_ip_address, sys_clk_freq, dw=8)
            self.ip   = LiteEthIP(self.ethmac, etherbone_mac_address, etherbone_ip_address, self.arp.table, dw=8)
            self.icmp = LiteEthICMP(self.ip, etherbone_ip_address, dw=8)
            self.udp  = LiteEthUDP(self.ip, etherbone_ip_address, dw=8)
            self.add_constant("ETH_PHY_NO_RESET") # Disable reset from BIOS to avoid disabling Hardware Interface.

            # Etherbone
            self.etherbone = LiteEthEtherbone(self.udp, 1234, mode="master")
            self.bus.add_master(master=self.etherbone.wishbone.bus)

            # Timing constraints
            eth_rx_clk = self.ethphy.crg.cd_eth_rx.clk
            eth_tx_clk = self.ethphy.crg.cd_eth_tx.clk
            self.platform.add_period_constraint(eth_rx_clk, 1e9/self.ethphy.rx_clk_freq)
            self.platform.add_period_constraint(eth_tx_clk, 1e9/self.ethphy.tx_clk_freq)
            self.platform.add_false_path_constraints(self.crg.cd_sys.clk, eth_rx_clk, eth_tx_clk)

        # Video ------------------------------------------------------------------------------------
        video_timings = ("800x480@60Hz", {
            "pix_clk"       : 33.3e6,
            "h_active"      : 800,
            "h_blanking"    : 256,
            "h_sync_offset" : 210,
            "h_sync_width"  : 1,
            "v_active"      : 480,
            "v_blanking"    : 45,
            "v_sync_offset" : 22,
            "v_sync_width"  : 1,
        })
        if with_video_terminal or with_video_framebuffer:
            self.videophy = VideoVGAPHY(platform.request("lcd"), clock_domain="dvi")
            if with_video_terminal:
                self.add_video_terminal(phy=self.videophy, timings=video_timings, clock_domain="dvi")
            if with_video_framebuffer:
                self.add_video_framebuffer(phy=self.videophy, timings=video_timings, clock_domain="dvi")

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=siglent_sds1104xe.Platform, description="LiteX SoC on SDS1104X-E.")
    parser.add_target_argument("--sys-clk-freq",   default=100e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-etherbone", action="store_true",       help="Enable Etherbone support.")
    parser.add_target_argument("--eth-ip",         default="192.168.1.50",     help="Ethernet/Etherbone IP address.")
    viopts = parser.target_group.add_mutually_exclusive_group()
    viopts.add_argument("--with-video-terminal",    action="store_true", help="Enable Video Terminal (HDMI).")
    viopts.add_argument("--with-video-framebuffer", action="store_true", help="Enable Video Framebuffer (HDMI).")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq   = args.sys_clk_freq,
        with_etherbone = args.with_etherbone,
        eth_ip         = args.eth_ip,
        with_video_terminal    = args.with_video_terminal,
        with_video_framebuffer = args.with_video_framebuffer,
        **parser.soc_argdict
    )

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"), device=1)

if __name__ == "__main__":
    main()
