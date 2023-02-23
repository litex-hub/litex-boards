#!/usr/bin/env python3
#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Antmicro <www.antmicro.com>
# Copyright (c) 2022 IBM Corp.
# SPDX-License-Identifier: BSD-2-Clause


import os
import math

from migen import *

from litex.gen import *

from litex_boards.platforms import antmicro_artix_dc_scm

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litedram.modules import MT41K128M16
from litedram.phy import s7ddrphy

from liteeth.phy import LiteEthS7PHYRGMII

from litepcie.phy.s7pciephy import S7PCIEPHY

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst          = Signal()
        self.cd_sys       = ClockDomain()
        self.cd_sys4x     = ClockDomain(reset_less=True)
        self.cd_sys4x_dqs = ClockDomain(reset_less=True)
        self.cd_idelay    = ClockDomain()

        self.cd_ulpi0     = ClockDomain()
        self.cd_ulpi1     = ClockDomain()

        # ulpi0 clock domain (60MHz from ulpi0)
        self.comb += self.cd_ulpi0.clk.eq(platform.request("ulpi_clock", 0))
        # ulpi1 clock domain (60MHz from ulpi1)
        self.comb += self.cd_ulpi1.clk.eq(platform.request("ulpi_clock", 1))

        # # #

        self.pll = pll = S7PLL(speedgrade=-1)
        # self.comb += pll.reset.eq(~platform.request("cpu_reset") | self.rst)
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(platform.request("clk100"), 100e6)
        pll.create_clkout(self.cd_sys,       sys_clk_freq)
        pll.create_clkout(self.cd_sys4x,     4 * sys_clk_freq)
        pll.create_clkout(self.cd_sys4x_dqs, 4 * sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_idelay,    200e6)

        self.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, *, device, toolchain="vivado", sys_clk_freq=100e6,
        with_pcie      = False,
        with_etherbone = False,
        with_ethernet  = False,
        eth_dynamic_ip = False,
        eth_reset_time = "10e-3",
        eth_ip         = "192.168.1.120",
        **kwargs):
        platform = antmicro_artix_dc_scm.Platform(device=device, toolchain=toolchain)

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident = "LiteX SoC on Artix DC-SCM", **kwargs)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.ddrphy = s7ddrphy.A7DDRPHY(platform.request("ddram"),
                memtype      = "DDR3",
                nphases      = 4,
                sys_clk_freq = sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT41K128M16(sys_clk_freq, "1:4"),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            self.ethphy = LiteEthS7PHYRGMII(
                clock_pads = self.platform.request("eth_clocks"),
                pads       = self.platform.request("eth"),
                hw_reset_cycles = math.ceil(float(eth_reset_time) * self.sys_clk_freq)
            )
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy, dynamic_ip=eth_dynamic_ip)
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, ip_address=eth_ip)

            platform.add_platform_command("set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets main_ethphy_eth_rx_clk_ibuf]")

        # PCIe -------------------------------------------------------------------------------------
        if with_pcie:
            self.pcie_phy = S7PCIEPHY(platform, platform.request("pcie_x1"),
                data_width = 128,
                bar0_size  = 0x20000)
            self.add_pcie(phy=self.pcie_phy, ndmas=1)

        # Leds -------------------------------------------------------------------------------------
        self.leds = LedChaser(
            pads         = platform.request_all("user_led"),
            sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=antmicro_artix_dc_scm.Platform, description="LiteX SoC on Artix DC-SCM.")
    parser.add_target_argument("--flash",        action="store_true",       help="Flash bitstream.")
    parser.add_target_argument("--sys-clk-freq", default=100e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--device",       default="xc7a100tfgg484-1", choices=["xc7a100tfgg484-1", "xc7a15tfgg484-1"])
    parser.add_target_argument("--with-pcie",    action="store_true",      help="Add PCIe.")
    ethopts = parser.target_group.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",        action="store_true",    help="Add Ethernet.")
    ethopts.add_argument("--with-etherbone",       action="store_true",    help="Add EtherBone.")
    parser.add_target_argument("--eth-ip",         default="192.168.1.50", help="Ethernet/Etherbone IP address.")
    parser.add_target_argument("--eth-dynamic-ip", action="store_true",    help="Enable dynamic Ethernet IP addresses setting.")
    parser.add_target_argument("--eth-reset-time", default="10e-3",        help="Duration of Ethernet PHY reset.")
    parser.add_target_argument("--with-sdram",     action="store_true",    help="Add SDRAM.")
    parser.add_target_argument("--with-emmc",      action="store_true",    help="Add eMMC.")
    args = parser.parse_args()

    assert not (args.with_etherbone and args.eth_dynamic_ip)

    soc = BaseSoC(
        toolchain              = args.toolchain,
        device                 = args.device,
        sys_clk_freq           = args.sys_clk_freq,
        with_pcie              = args.with_pcie,
        with_ethernet          = args.with_ethernet,
        with_etherbone         = args.with_etherbone,
        eth_ip                 = args.eth_ip,
        eth_dynamic_ip         = args.eth_dynamic_ip,
        eth_reset_time         = args.eth_reset_time,
        **parser.soc_argdict
    )

    if args.with_emmc:
        soc.add_sdcard(software_debug=False)

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.flash(0, builder.get_bitstream_filename(mode="flash"))

if __name__ == "__main__":
    main()
