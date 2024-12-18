#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2024 Jiaxun Yang <jiaxun.yang@flygoat.com>
# SPDX-License-Identifier: BSD-2-Clause

import os
import re

from migen import *

from litex.gen import *

from litex_boards.platforms import alibaba_vu13p

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

from litex.soc.cores.led import LedChaser
from litedram.modules import MT40A512M16
from litedram.phy import usddrphy

from liteeth.phy.usp_gty_1000basex import USP_GTY_1000BASEX

from litepcie.phy.usppciephy import USPPCIEPHY
from litepcie.software import generate_litepcie_software

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, ddram_channel=0):
        self.rst       = Signal()
        self.cd_sys    = ClockDomain()
        self.cd_sys4x  = ClockDomain()
        self.cd_pll4x  = ClockDomain()
        self.cd_eth    = ClockDomain()
        self.cd_idelay = ClockDomain()

        self.pll = pll = USMMCM(speedgrade=-2)
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(platform.request("clk400", 0), 400e6)
        pll.create_clkout(self.cd_pll4x, sys_clk_freq*4, buf=None, with_reset=False)
        pll.create_clkout(self.cd_eth, 200e6, margin=0)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        self.specials += [
            Instance("BUFGCE_DIV",
                p_BUFGCE_DIVIDE=4,
                i_CE=1, i_I=self.cd_pll4x.clk, o_O=self.cd_sys.clk),
            Instance("BUFGCE",
                i_CE=1, i_I=self.cd_pll4x.clk, o_O=self.cd_sys4x.clk),
        ]

        ddr_pad = platform.request("ddram_refclk", ddram_channel)
        self.specials += [Instance("IBUFDS",
            i_I   = ddr_pad.p,
            i_IB  = ddr_pad.n,
            o_O   = self.cd_idelay.clk,
        )]

        self.idelayctrl = USIDELAYCTRL(cd_ref=self.cd_idelay, cd_sys=self.cd_sys)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=125e6,
                ddram_channel          = 0,
                with_led_chaser        = True,
                with_ethernet          = False,
                with_etherbone         = False,
                ethernet_port          = "qsfp0_sfp0",
                etherbone_port         = "qsfp0_sfp0", 
                ethernet_ip            = "192.168.1.50",
                eth_dynamic_ip         = True,
                remote_ip              = None,
                etherbone_ip           = "192.168.1.50",
                with_pcie              = False,
                **kwargs):
        platform = alibaba_vu13p.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, ddram_channel)

        kwargs["uart_name"]     = "crossover"
        kwargs["with_jtagbone"] = True

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Alibaba VU13P", **kwargs)

        # Running LED
        self.comb += platform.request("run_led").eq(~ResetSignal("sys"))

        # DDR4 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.ddrphy = usddrphy.USPDDRPHY(platform.request("ddram", ddram_channel),
                memtype          = "DDR4",
                sys_clk_freq     = sys_clk_freq,
                iodelay_clk_freq = 400e6)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT40A512M16(sys_clk_freq, "1:4"),
                size          = 0x40000000,
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # PCIe -------------------------------------------------------------------------------------
        if with_pcie:
            self.pcie_phy = USPPCIEPHY(platform, platform.request("pcie_x4"),
                data_width = 128,
                bar0_size  = 0x20000)
            self.add_pcie(phy=self.pcie_phy, ndmas=1)

        # Ethernet / Etherbone ---------------------------------------------------------------------
        def parse_qsfp_port(port_string):
            match = re.match(r"qsfp(\d+)_sfp(\d+)", port_string)
            qsfp_id = int(match.group(1))
            sfp_lane = int(match.group(2))
            return (qsfp_id, sfp_lane)
        
        qsfp_in_use = [False, False]

        if with_ethernet:
            qsfp_id, sfp_lane = parse_qsfp_port(ethernet_port)
            self.ethphy = USP_GTY_1000BASEX(self.crg.cd_eth.clk,
                data_pads    = self.platform.request("qsfp{}_sfp".format(qsfp_id), sfp_lane),
                sys_clk_freq = self.clk_freq,
                refclk_from_fabric = True)
            self.add_ethernet(phy=self.ethphy, local_ip=ethernet_ip if not eth_dynamic_ip else None, dynamic_ip=eth_dynamic_ip, remote_ip=remote_ip)
            qsfp_in_use[qsfp_id] = True

        if with_etherbone:
            qsfp_id, sfp_lane = parse_qsfp_port(etherbone_port)
            self.bonephy = USP_GTY_1000BASEX(self.crg.cd_eth.clk,
                data_pads    = self.platform.request("qsfp{}_sfp".format(qsfp_id), sfp_lane),
                sys_clk_freq = self.clk_freq,
                refclk_from_fabric = True)
            self.add_etherbone(phy=self.bonephy, ip_address=etherbone_ip)
            qsfp_in_use[qsfp_id] = True


        for qsfp_id, in_use in enumerate(qsfp_in_use):
            if in_use:
                resetl = platform.request("qsfp_resetl", qsfp_id)
                lpmode = platform.request("qsfp_lpmode", qsfp_id)

                reset_cycles = int(sys_clk_freq * 10e-3)  # 1ms as tested with multiple SFP modules
                reset_count = Signal(max=reset_cycles+1, reset=reset_cycles)
                self.sync += [
                    If(ResetSignal("sys"),
                        reset_count.eq(reset_cycles)
                    ).Elif(reset_count != 0,
                        reset_count.eq(reset_count - 1)
                    )
                ]

                self.comb += resetl.eq(~(ResetSignal("sys") | (reset_count != 0)))
                self.comb += lpmode.eq(0)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser

    sfp_list = []
    for qsfp in range(2):
        for sfp in range(4):
            sfp_list.append("qsfp{}_{}".format(qsfp, sfp))

    parser = LiteXArgumentParser(platform=alibaba_vu13p.Platform, description="LiteX SoC on Alibaba VU13P.")
    parser.add_target_argument("--flash",          action="store_true",       help="Write FPGA bitstream into spi flash.")
    parser.add_target_argument("--sys-clk-freq",   default=125e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--ddram-channel",  default=0, type=int, choices=range(4), help="DDRAM channel.")
    parser.add_target_argument("--with-ethernet",  action="store_true",       help="Enable Ethernet support.")
    parser.add_target_argument("--with-etherbone", action="store_true",       help="Enable Etherbone support.")
    parser.add_target_argument("--ethernet-port",  default="qsfp0_sfp0", choices=sfp_list, help="Ethernet SFP port.")
    parser.add_target_argument("--etherbone-port", default="qsfp0_sfp0", choices=sfp_list, help="Etherbone SFP port.")
    parser.add_target_argument("--ethernet-ip",    default="192.168.1.50",    help="Ethernet IP address.")
    parser.add_target_argument("--remote-ip",      default="192.168.1.100",   help="Remote IP address of TFTP server.")
    parser.add_target_argument("--eth-dynamic-ip", action="store_true",     help="Enable dynamic Ethernet IP addresses setting.")
    parser.add_target_argument("--etherbone-ip",   default="192.168.1.50",    help="Ethernet IP address.")
    parser.add_target_argument("--with-pcie",      action="store_true",       help="Enable PCIe support.")
    parser.add_target_argument("--driver",         action="store_true",       help="Generate PCIe driver.")
    args = parser.parse_args()

    if args.with_ethernet and args.with_etherbone:
        if args.ethernet_port == args.etherbone_port:
            parser.error("Ethernet and Etherbone SFP ports must be different.")

    soc = BaseSoC(
        sys_clk_freq = args.sys_clk_freq,
        ddram_channel = args.ddram_channel,
        with_ethernet = args.with_ethernet,
        with_etherbone = args.with_etherbone,
        ethernet_port  = args.ethernet_port,
        etherbone_port  = args.etherbone_port,
        ethernet_ip    = args.ethernet_ip,
        remote_ip      = args.remote_ip,
        eth_dynamic_ip = args.eth_dynamic_ip,
        etherbone_ip  = args.etherbone_ip,
        with_pcie    = args.with_pcie,
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
