#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2021 Greg Davill <greg.davill@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

# Build/Use:
# ./gsd_butterstick.py --uart-name=crossover --with-etherbone --csr-csv=csr.csv --build --load
# litex_server --udp
# litex_term bridge

import os
import sys
import argparse

from migen import *
from litex_boards.platforms import butterstick

from litex.build.lattice.trellis import trellis_args, trellis_argdict

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from liteeth.phy.ecp5rgmii import LiteEthPHYRGMII

# CRG ---------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_por = ClockDomain(reset_less=True)
        self.clock_domains.cd_sys = ClockDomain()

        # # #

        # Clk / Rst
        clk30 = platform.request("clk30")
        rst_n = platform.request("user_btn", 0)

        # Power on reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += self.cd_por.clk.eq(clk30)
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # PLL
        self.submodules.pll = pll = ECP5PLL()
        self.comb += pll.reset.eq(~por_done | ~rst_n | self.rst)
        pll.register_clkin(clk30, 30e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, revision="1.0", device="25F", sys_clk_freq=int(60e6), toolchain="trellis",
        with_ethernet=False, with_etherbone=False, eth_ip="192.168.1.50", eth_dynamic_ip=False,
        with_led_chaser=True,
        **kwargs)       :
        platform = butterstick.Platform(revision=revision, device=device ,toolchain=toolchain)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident          = "LiteX SoC on ButterStick",
            ident_version  = True,
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            self.submodules.ethphy = LiteEthPHYRGMII(
                clock_pads = self.platform.request("eth_clocks"),
                pads       = self.platform.request("eth"))
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy, dynamic_ip=eth_dynamic_ip)
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, ip_address=eth_ip)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.comb += platform.request("user_led_color").eq(0b010) # Blue.
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)


# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on ButterStick")
    parser.add_argument("--build",           action="store_true",    help="Build bitstream")
    parser.add_argument("--load",            action="store_true",    help="Load bitstream")
    parser.add_argument("--toolchain",       default="trellis",      help="FPGA  use, trellis (default) or diamond")
    parser.add_argument("--sys-clk-freq",    default=125e6,           help="System clock frequency (default: 125MHz)")
    parser.add_argument("--revision",        default="1.0",          help="Board Revision: 1.0 (default)")
    parser.add_argument("--device",          default="85F",          help="ECP5 device (default: 85F)")
    ethopts = parser.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",  action="store_true",    help="Add Ethernet")
    ethopts.add_argument("--with-etherbone", action="store_true",    help="Add EtherBone")
    parser.add_argument("--eth-ip",          default="192.168.1.50", help="Ethernet/Etherbone IP address")
    parser.add_argument("--eth-dynamic-ip",  action="store_true",    help="Enable dynamic Ethernet IP addresses setting")
    builder_args(parser)
    soc_core_args(parser)
    trellis_args(parser)
    args = parser.parse_args()

    assert not (args.with_etherbone and args.eth_dynamic_ip)

    soc = BaseSoC(
        toolchain      = args.toolchain,
        revision       = args.revision,
        device         = args.device,
        sys_clk_freq   = int(float(args.sys_clk_freq)),
        with_ethernet  = args.with_ethernet,
        with_etherbone = args.with_etherbone,
        eth_ip         = args.eth_ip,
        eth_dynamic_ip = args.eth_dynamic_ip,
        **soc_core_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder_kargs = trellis_argdict(args) if args.toolchain == "trellis" else {}
    builder.build(**builder_kargs, run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".bit"))

if __name__ == "__main__":
    main()
