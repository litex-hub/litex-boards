#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 Derek Kozel <dkozel@bitstovolts.com
# SPDX-License-Identifier: BSD-2-Clause

# Ex Use:
# LiteX SoC with UART over JTAG:
# - python3 -m litex_boards.targets.alibaba_xcku3p --uart-name=jtag_uart --build --load
# - litex_term jtag --jtag-config=openocd_xc7_ft232.cfg
#
# LiteX/LitePCIe SoC:
# - python3 -m litex_boards.targets.alibaba_xcku3p --with-pcie --build --load
# - reboot computer
# - lspci -> board should be seen as Memory controller: Xilinx Corporation Device 9034

import os

from migen import *

from litex.gen import *

from litex_boards.platforms import alibaba_xcku3p

from litex.soc.integration.soc_core import *
from litex.soc.integration.builder  import *

from litex.soc.cores.clock import *
from litex.soc.cores.led   import LedChaser

from liteeth.phy.usp_gty_1000basex import USP_GTY_1000BASEX

from litepcie.phy.usppciephy import USPPCIEPHY
from litepcie.software       import generate_litepcie_software

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()
        self.cd_eth = ClockDomain()

        # Clk.
        clk100 = platform.request("clk100")

        # PLL.
        self.pll = pll = USPMMCM(speedgrade=-2)
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk100, 100e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        pll.create_clkout(self.cd_eth, 200e6)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=100e6,
        with_ethernet   = False,
        with_etherbone  = False,
        eth_sfp         = 0,
        eth_ip          = "192.168.1.50",
        remote_ip       = None,
        eth_dynamic_ip  = False,
        with_led_chaser = True,
        with_pcie       = False,
        **kwargs):
        platform = alibaba_xcku3p.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        if kwargs.get("uart_name", "serial") == "serial":
            kwargs["uart_name"] = "jtag_uart" # Defaults to JTAG UART.
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Alibaba Cloud KU3P Board", **kwargs)

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            self.ethphy = USP_GTY_1000BASEX(self.crg.cd_eth.clk,
                data_pads    = self.platform.request("sfp", eth_sfp),
                sys_clk_freq = self.clk_freq,
                refclk_from_fabric = True)
            platform.add_platform_command("set_property SEVERITY {{Warning}} [get_drc_checks REQP-1753]")
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, ip_address=eth_ip, with_ethmac=with_ethernet)
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy, dynamic_ip=eth_dynamic_ip, local_ip=eth_ip, remote_ip=remote_ip)

        # PCIe -------------------------------------------------------------------------------------
        if with_pcie:
            self.pcie_phy = USPPCIEPHY(
                platform,
                platform.request("pcie_x4"),
                data_width = 128,
                bar0_size  = 0x20000
            )
            self.pcie_phy.update_config({
                "mode_selection"   : "Advanced",
                "en_gt_selection"  : "true",
                "select_quad"      : "GTY_Quad_225",
                "pcie_blk_locn"    : "X0Y0",
                "gen_x0y0"         : "true",
                "gen_x1y0"         : "false",
            })
            self.add_pcie(phy=self.pcie_phy, ndmas=1)

        # LEDs -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=alibaba_xcku3p.Platform, description="LiteX SoC on Alibaba Cloud KU3P board.")
    parser.add_target_argument("--sys-clk-freq", default=100e6, type=float, help="System clock frequency.")
    ethopts = parser.target_group.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",        action="store_true",    help="Enable Ethernet support.")
    ethopts.add_argument("--with-etherbone",       action="store_true",    help="Enable Etherbone support.")
    parser.add_argument("--eth-sfp",               default=0, type=int,    help="Ethernet SFP.", choices=[0, 1])
    parser.add_target_argument("--eth-ip",         default="192.168.1.50", help="Ethernet/Etherbone IP address.")
    parser.add_target_argument("--eth-dynamic-ip", action="store_true",    help="Enable dynamic Ethernet IP addresses setting.")
    parser.add_target_argument("--remote-ip",      default=None,           help="Remote IP address of TFTP server.")
    parser.add_target_argument("--with-pcie",      action="store_true",    help="Enable PCIe support.")
    parser.add_target_argument("--driver",         action="store_true",    help="Generate PCIe driver.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq   = args.sys_clk_freq,
        with_ethernet  = args.with_ethernet,
        with_etherbone = args.with_etherbone,
        eth_sfp        = args.eth_sfp,
        eth_ip         = args.eth_ip,
        eth_dynamic_ip = args.eth_dynamic_ip,
        remote_ip      = args.remote_ip,
        with_pcie      = args.with_pcie,
        **parser.soc_argdict
    )

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.driver:
        generate_litepcie_software(soc, os.path.join(builder.output_dir, "driver"))

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
