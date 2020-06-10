#!/usr/bin/env python3

# This file is Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# License: BSD

# Build/Use ----------------------------------------------------------------------------------------
#
# 1) SoC with regular UART and optional Ethernet connected to the CPU:
# Connect a USB/UART to J19: TX of the FPGA is DATA_LED-, RX of the FPGA is KEY+.
# ./colorlight_5a_75x.py --revision=7.0 (or 6.1) (--with-ethernet to add Ethernet capability)
# Note: on revision 6.1, add --uart-baudrate=9600 to lower the baudrate.
# ./colorlight_5a_75x.py --load
# You should see the LiteX BIOS and be able to interact with it.
#
# 2) SoC with UART in crossover mode over Etherbone:
# ./colorlight_5a_75x.py --revision=7.0 (or 6.1) --uart-name=crossover --with-etherbone --csr-csv=csr.csv
# ./colorlight_5a_75x.py --load
# ping 192.168.1.50
# Get and install wishbone tool from: https://github.com/litex-hub/wishbone-utils/releases
# wishbone-tool --ethernet-host 192.168.1.50 --server terminal --csr-csv csr.csv
# You should see the LiteX BIOS and be able to interact with it.
#
# 3) SoC with USB-ACM UART (on V7.0):
# - Replace U23 with a SN74CBT3245APWR or remove U23 and place jumper wires to make the ports bi-directional.
# - Place a 15K resistor between J4 pin 2 and J4 pin 4.
# - Place a 15K resistor between J4 pin 3 and J4 pin 4.
# - Place a 1.5K resistor between J4 pin 1 and J4 pin 3.
# - Connect USB DP (Green) to J4 pin 3, USB DN (White) to J4 pin 2.
# ./colorlight_5a_75x.py --revision=7.0 --uart-name=usb_acm
# ./colorlight_5a_75x.py --load
# You should see the LiteX BIOS and be able to interact with it.
#
# Note that you can also use a 5A-75E board:
# ./colorlight_5a_75x.py --board=5a-75e --revision=7.1
#
# Disclaimer: SoC 2) is still a Proof of Concept with large timings violations on the IP/UDP and
# Etherbone stack that need to be optimized. It was initially just used to validate the reversed
# pinout but happens to work on hardware...

import os
import argparse
import sys

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.build.io import DDROutput

from litex_boards.platforms import colorlight_5a_75b, colorlight_5a_75e

from litex.build.lattice.trellis import trellis_args, trellis_argdict

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

from litedram.modules import M12L16161A
from litedram.phy import GENSDRPHY

from liteeth.phy.ecp5rgmii import LiteEthPHYRGMII

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq, with_usb_pll=False, with_rst=True):
        self.clock_domains.cd_sys    = ClockDomain()
        self.clock_domains.cd_sys_ps = ClockDomain()

        # # #

        # Clk / Rst
        clk25 = platform.request("clk25")
        rst_n = 1 if not with_rst else platform.request("user_btn_n", 0)

        # PLL
        self.submodules.pll = pll = ECP5PLL()

        pll.register_clkin(clk25, 25e6)
        pll.create_clkout(self.cd_sys,    sys_clk_freq)
        pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=180) # Idealy 90° but needs to be increased.
        self.specials += AsyncResetSynchronizer(self.cd_sys, ~pll.locked | ~rst_n)

        # USB PLL
        if with_usb_pll:
            self.submodules.usb_pll = usb_pll = ECP5PLL()
            usb_pll.register_clkin(clk25, 25e6)
            self.clock_domains.cd_usb_12 = ClockDomain()
            self.clock_domains.cd_usb_48 = ClockDomain()
            usb_pll.create_clkout(self.cd_usb_12, 12e6, margin=0)
            usb_pll.create_clkout(self.cd_usb_48, 48e6, margin=0)

        # SDRAM clock
        self.specials += DDROutput(1, 0, platform.request("sdram_clock"), ClockSignal("sys_ps"))

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, board, revision, with_ethernet=False, with_etherbone=False, sys_clk_freq=60e6, **kwargs):
        board = board.lower()
        assert board in ["5a-75b", "5a-75e"]
        if board == "5a-75b":
            platform = colorlight_5a_75b.Platform(revision=revision)
        elif board == "5a-75e":
            platform = colorlight_5a_75e.Platform(revision=revision)

        if with_etherbone:
            sys_clk_freq = int(125e6)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, clk_freq=sys_clk_freq, **kwargs)

        # CRG --------------------------------------------------------------------------------------
        with_rst = kwargs["uart_name"] not in ["serial", "bridge"] # serial_rx shared with user_btn_n.
        with_usb_pll = kwargs.get("uart_name", None) == "usb_acm"
        self.submodules.crg = _CRG(platform, sys_clk_freq, with_usb_pll=with_usb_pll,with_rst=with_rst)

        # SDR SDRAM --------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.submodules.sdrphy = GENSDRPHY(platform.request("sdram"))
            self.add_sdram("sdram",
                phy                     = self.sdrphy,
                module                  = M12L16161A(sys_clk_freq, "1:1"),
                origin                  = self.mem_map["main_ram"],
                size                    = kwargs.get("max_sdram_size", 0x40000000),
                l2_cache_size           = kwargs.get("l2_size", 8192),
                l2_cache_min_data_width = kwargs.get("min_l2_data_width", 128),
                l2_cache_reverse        = True
            )

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            self.submodules.ethphy = LiteEthPHYRGMII(
                clock_pads = self.platform.request("eth_clocks"),
                pads       = self.platform.request("eth"))
            self.add_csr("ethphy")
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy)
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy)

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on Colorlight 5A-75B")
    builder_args(parser)
    soc_core_args(parser)
    trellis_args(parser)
    parser.add_argument("--build",          action="store_true",     help="Build bitstream")
    parser.add_argument("--load",           action="store_true",     help="Load bitstream")
    parser.add_argument("--board",          default="5a-75b",        help="Board type: 5a-75b (default) or 5a-75e")
    parser.add_argument("--revision",       default="7.0", type=str, help="Board revision 7.0 (default) or 6.1")
    parser.add_argument("--with-ethernet",  action="store_true",     help="Enable Ethernet support")
    parser.add_argument("--with-etherbone", action="store_true",     help="Enable Etherbone support")
    parser.add_argument("--eth-phy",        default=0, type=int,     help="Ethernet PHY 0 or 1 (default=0)")
    parser.add_argument("--sys-clk-freq",   default=60e6,            help="System clock frequency (default=60MHz)")
    args = parser.parse_args()

    assert not (args.with_ethernet and args.with_etherbone)
    soc = BaseSoC(board=args.board, revision=args.revision,
        with_ethernet  = args.with_ethernet,
        with_etherbone = args.with_etherbone,
        sys_clk_freq   = args.sys_clk_freq,
        **soc_core_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder.build(**trellis_argdict(args), run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".svf"))

if __name__ == "__main__":
    main()
