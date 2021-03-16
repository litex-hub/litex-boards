#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# Build/Use ----------------------------------------------------------------------------------------
# Build/Load bitstream:
# ./sds1104xe.py --with-etherbone --uart-name=crossover --csr-csv=csr.csv --build --load
#
# Test Ethernet:
# ping 192.168.1.50
#
# Test Console:
# litex_server --udp
# litex_term crossover
# --------------------------------------------------------------------------------------------------

import os
import argparse

from migen import *

from litex_boards.platforms import sds1104xe
from litex.build.xilinx.vivado import vivado_build_args, vivado_build_argdict

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc_sdram import *
from litex.soc.integration.builder import *

from litedram.modules import MT41K64M16
from litedram.phy import s7ddrphy

from liteeth.phy.mii import LiteEthPHYMII

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_sys       = ClockDomain()
        self.clock_domains.cd_sys4x     = ClockDomain(reset_less=True)
        self.clock_domains.cd_sys4x_dqs = ClockDomain(reset_less=True)
        self.clock_domains.cd_idelay    = ClockDomain()

        # # #

        self.submodules.pll = pll = S7PLL(speedgrade=-1)
        pll.register_clkin(ClockSignal("eth_tx"), 25e6)
        pll.create_clkout(self.cd_sys,       sys_clk_freq)
        pll.create_clkout(self.cd_sys4x,     4*sys_clk_freq)
        pll.create_clkout(self.cd_sys4x_dqs, 4*sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_idelay,    200e6)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        self.submodules.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(100e6), with_etherbone=True, eth_ip="192.168.1.50", **kwargs):
        platform = sds1104xe.Platform()

        # SoCCore ----------------------------------------------------------------------------------
        if kwargs.get("uart_name", "serial") == "serial":
            kwargs["uart_name"] = "crossover" # Defaults to Crossover UART.
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident          = "LiteX SoC on Siglent SDS1104X-E",
            ident_version  = True,
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.submodules.ddrphy = s7ddrphy.A7DDRPHY(platform.request("ddram"),
                memtype        = "DDR3",
                nphases        = 4,
                sys_clk_freq   = sys_clk_freq)
            self.add_csr("ddrphy")
            self.add_sdram("sdram",
                phy                     = self.ddrphy,
                module                  = MT41K64M16(sys_clk_freq, "1:4"),
                origin                  = self.mem_map["main_ram"],
                size                    = kwargs.get("max_sdram_size", 0x40000000),
                l2_cache_size           = kwargs.get("l2_size", 8192),
                l2_cache_min_data_width = kwargs.get("min_l2_data_width", 128),
                l2_cache_reverse        = True
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
            ethphy = LiteEthPHYMII(
                clock_pads = self.platform.request("eth_clocks"),
                pads       = self.platform.request("eth"))
            self.submodules += ethphy
            etherbone_ip_address  = convert_ip("192.168.1.51")
            etherbone_mac_address = 0x10e2d5000001

            # Ethernet MAC
            self.submodules.ethmac = LiteEthMAC(phy=ethphy, dw=8,
                interface  = "hybrid",
                endianness = self.cpu.endianness,
                hw_mac     = etherbone_mac_address)

            # Software Interface.
            self.add_memory_region("ethmac", self.mem_map["ethmac"], 0x2000, type="io")
            self.add_wb_slave(self.mem_regions["ethmac"].origin, self.ethmac.bus, 0x2000)
            self.add_csr("ethmac")
            if self.irq.enabled:
                self.irq.add("ethmac", use_loc_if_exists=True)

            # Hardware Interface.
            self.submodules.arp  = LiteEthARP(self.ethmac, etherbone_mac_address, etherbone_ip_address, sys_clk_freq, dw=8)
            self.submodules.ip   = LiteEthIP(self.ethmac, etherbone_mac_address, etherbone_ip_address, self.arp.table, dw=8)
            self.submodules.icmp = LiteEthICMP(self.ip, etherbone_ip_address, dw=8)
            self.submodules.udp  = LiteEthUDP(self.ip, etherbone_ip_address, dw=8)

            # Etherbone
            self.submodules.etherbone = LiteEthEtherbone(self.udp, 1234, mode="master")
            self.add_wb_master(self.etherbone.wishbone.bus)

            # Timing constraints
            eth_rx_clk = ethphy.crg.cd_eth_rx.clk
            eth_tx_clk = ethphy.crg.cd_eth_tx.clk
            self.platform.add_period_constraint(eth_rx_clk, 1e9/ethphy.rx_clk_freq)
            self.platform.add_period_constraint(eth_tx_clk, 1e9/ethphy.tx_clk_freq)
            self.platform.add_false_path_constraints(self.crg.cd_sys.clk, eth_rx_clk, eth_tx_clk)

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on SDS1104X-E")
    parser.add_argument("--build",          action="store_true",              help="Build bitstream")
    parser.add_argument("--load",           action="store_true",              help="Load bitstream")
    parser.add_argument("--sys-clk-freq",   default=100e6,                    help="System clock frequency (default: 100MHz)")
    parser.add_argument("--with-etherbone", action="store_true",              help="Enable Etherbone support")
    parser.add_argument("--eth-ip",         default="192.168.1.50", type=str, help="Ethernet/Etherbone IP address")
    builder_args(parser)
    soc_sdram_args(parser)
    vivado_build_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq   = int(float(args.sys_clk_freq)),
        with_etherbone = args.with_etherbone,
        eth_ip         = args.eth_ip,
        **soc_sdram_argdict(args)
    )

    builder = Builder(soc, **builder_argdict(args))
    builder.build(**vivado_build_argdict(args), run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".bit"), device=1)

if __name__ == "__main__":
    main()
