#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

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
# ./colorlight_5a_75x.py --board=5a-75e --revision=7.1 (or 6.0)
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

from litedram.modules import M12L16161A, M12L64322A
from litedram.phy import GENSDRPHY, HalfRateGENSDRPHY

from liteeth.phy.ecp5rgmii import LiteEthPHYRGMII

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq, use_internal_osc=False, with_usb_pll=False, with_rst=True, sdram_rate="1:1"):
        self.clock_domains.cd_sys    = ClockDomain()
        if sdram_rate == "1:2":
            self.clock_domains.cd_sys2x    = ClockDomain()
            self.clock_domains.cd_sys2x_ps = ClockDomain(reset_less=True)
        else:
            self.clock_domains.cd_sys_ps = ClockDomain(reset_less=True)

        # # #

        # Clk / Rst
        if not use_internal_osc:
            clk = platform.request("clk25")
            clk_freq = 25e6
        else:
            clk = Signal()
            div = 5
            self.specials += Instance("OSCG",
                                p_DIV = div,
                                o_OSC = clk)
            clk_freq = 310e6/div

        rst_n = 1 if not with_rst else platform.request("user_btn_n", 0)

        # PLL
        self.submodules.pll = pll = ECP5PLL()
        self.comb += pll.reset.eq(~rst_n)
        pll.register_clkin(clk, clk_freq)
        pll.create_clkout(self.cd_sys,    sys_clk_freq)
        if sdram_rate == "1:2":
            pll.create_clkout(self.cd_sys2x,    2*sys_clk_freq)
            pll.create_clkout(self.cd_sys2x_ps, 2*sys_clk_freq, phase=180) # Idealy 90° but needs to be increased.
        else:
           pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=180) # Idealy 90° but needs to be increased.

        # USB PLL
        if with_usb_pll:
            self.submodules.usb_pll = usb_pll = ECP5PLL()
            self.comb += usb_pll.reset.eq(~rst_n)
            usb_pll.register_clkin(clk, clk_freq)
            self.clock_domains.cd_usb_12 = ClockDomain()
            self.clock_domains.cd_usb_48 = ClockDomain()
            usb_pll.create_clkout(self.cd_usb_12, 12e6, margin=0)
            usb_pll.create_clkout(self.cd_usb_48, 48e6, margin=0)

        # SDRAM clock
        sdram_clk = ClockSignal("sys2x_ps" if sdram_rate == "1:2" else "sys_ps")
        self.specials += DDROutput(1, 0, platform.request("sdram_clock"), sdram_clk)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, board, revision, with_ethernet=False, with_etherbone=False, eth_phy=0, sys_clk_freq=60e6, use_internal_osc=False, sdram_rate="1:1", **kwargs):
        board = board.lower()
        assert board in ["5a-75b", "5a-75e"]
        if board == "5a-75b":
            platform = colorlight_5a_75b.Platform(revision=revision)
        elif board == "5a-75e":
            platform = colorlight_5a_75e.Platform(revision=revision)

        if board == "5a-75e" and revision == "6.0" and (with_etherbone or with_ethernet):
            assert use_internal_osc, "You cannot use the 25MHz clock as system clock since it is provided by the Ethernet PHY and will stop during PHY reset."

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, int(sys_clk_freq),
            ident          = "LiteX SoC on Colorlight " + board.upper(),
            ident_version  = True,
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        with_rst = kwargs["uart_name"] not in ["serial", "bridge"] # serial_rx shared with user_btn_n.
        with_usb_pll = kwargs.get("uart_name", None) == "usb_acm"
        self.submodules.crg = _CRG(platform, sys_clk_freq, use_internal_osc=use_internal_osc, with_usb_pll=with_usb_pll,with_rst=with_rst, sdram_rate=sdram_rate)

        # SDR SDRAM --------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            sdrphy_cls = HalfRateGENSDRPHY if sdram_rate == "1:2" else GENSDRPHY
            self.submodules.sdrphy = sdrphy_cls(platform.request("sdram"))
            if board == "5a-75e" and revision == "6.0":
                sdram_cls  = M12L64322A
                sdram_size = 0x80000000
            else:
                sdram_cls  = M12L16161A
                sdram_size = 0x40000000
            self.add_sdram("sdram",
                phy                     = self.sdrphy,
                module                  = sdram_cls(sys_clk_freq, sdram_rate),
                origin                  = self.mem_map["main_ram"],
                size                    = kwargs.get("max_sdram_size", sdram_size),
                l2_cache_size           = kwargs.get("l2_size", 8192),
                l2_cache_min_data_width = kwargs.get("min_l2_data_width", 128),
                l2_cache_reverse        = True
            )

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            self.submodules.ethphy = LiteEthPHYRGMII(
                clock_pads = self.platform.request("eth_clocks", eth_phy),
                pads       = self.platform.request("eth", eth_phy))
            self.add_csr("ethphy")
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy)
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy)

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on Colorlight 5A-75X")
    builder_args(parser)
    soc_core_args(parser)
    trellis_args(parser)
    parser.add_argument("--build",            action="store_true",      help="Build bitstream")
    parser.add_argument("--load",             action="store_true",      help="Load bitstream")
    parser.add_argument("--board",            default="5a-75b",         help="Board type: 5a-75b (default) or 5a-75e")
    parser.add_argument("--revision",         default="7.0", type=str,  help="Board revision 7.0 (default), 6.0 or 6.1")
    parser.add_argument("--with-ethernet",    action="store_true",      help="Enable Ethernet support")
    parser.add_argument("--with-etherbone",   action="store_true",      help="Enable Etherbone support")
    parser.add_argument("--eth-phy",          default=0, type=int,      help="Ethernet PHY 0 or 1 (default=0)")
    parser.add_argument("--sys-clk-freq",     default=60e6, type=float, help="System clock frequency (default=60MHz)")
    parser.add_argument("--use-internal-osc", action="store_true",      help="Use internal oscillator")
    parser.add_argument("--sdram-rate",       default="1:1",            help="SDRAM Rate 1:1 Full Rate (default), 1:2 Half Rate")
    args = parser.parse_args()

    assert not (args.with_ethernet and args.with_etherbone)
    soc = BaseSoC(board=args.board, revision=args.revision,
        with_ethernet    = args.with_ethernet,
        with_etherbone   = args.with_etherbone,
        eth_phy          = args.eth_phy,
        sys_clk_freq     = args.sys_clk_freq,
        use_internal_osc = args.use_internal_osc,
        sdram_rate       = args.sdram_rate,
        **soc_core_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder.build(**trellis_argdict(args), run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".svf"))

if __name__ == "__main__":
    main()
