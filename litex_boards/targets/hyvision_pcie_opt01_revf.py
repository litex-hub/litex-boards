#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 Hans Baier <foss@hans-baier.de>
# SPDX-License-Identifier: BSD-2-Clause
# Since this board has no uart, you want to build with JTAG UART:
# python litex_boards/targets/hyvision_pcie_opt01_revf.py --build --uart-name=jtag_uart
#
# JTAG Connectors: j11 or j13
# Pinout:
#
# | Pins |  1  |  2  |  3  |  4  |  5  |  6  |
# |------|-----|-----|-----|-----|-----|-----|
# | Pins | TMS | TDI | TDO | TCK | GND | VCC |

from migen import *

from litex.gen import *

from litex_boards.platforms import hyvision_pcie_opt01_revf

from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

from litex.soc.cores.clock import *
from litex.soc.cores.led import LedChaser

from litedram.common  import PHYPadsReducer
from litedram.modules import K4T1G164QGBCE7
from litedram.phy import s7ddrphy

from liteeth.phy.k7_1000basex import K7_1000BASEX

from litepcie.phy.s7pciephy import S7PCIEPHY
from litepcie.software import generate_litepcie_software

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_eth=False):
        self.rst          = Signal()
        self.cd_sys       = ClockDomain()
        self.cd_sys2x     = ClockDomain()
        self.cd_sys2x_dqs = ClockDomain()
        self.cd_idelay    = ClockDomain()

        # Clk / Rst.
        clk200 = platform.request("clk200")

        # PLL.
        self.pll = pll = S7MMCM(speedgrade=-1)
        pll.register_clkin(clk200, 200e6)
        pll.create_clkout(self.cd_sys,       sys_clk_freq)
        pll.create_clkout(self.cd_sys2x,     2*sys_clk_freq)
        pll.create_clkout(self.cd_sys2x_dqs, 2*sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_idelay,    200e6)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        # Eth Clk.
        if with_eth:
            self.cd_eth  = ClockDomain()
            pll.create_clkout(self.cd_eth, 200e6, margin=0)

        self.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=100e6,
        with_led_chaser = True,
        with_pcie       = False,
        with_ethernet   = False,
        with_etherbone  = False,
        eth_sfp         = 0,
        eth_ip          = "192.168.1.50",
        remote_ip       = None,
        eth_dynamic_ip  = False,
        **kwargs):
        platform = hyvision_pcie_opt01_revf.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, with_eth=(with_ethernet or with_etherbone))

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on HVS HyVision PCIe OPT01 revf", **kwargs)

        # PCIe -------------------------------------------------------------------------------------
        if with_pcie:
            self.pcie_phy = S7PCIEPHY(platform, platform.request("pcie_x4"),
                data_width = 128,
                bar0_size  = 0x20000)
            self.add_pcie(phy=self.pcie_phy, ndmas=1)

        # DDR2 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.ddrphy = s7ddrphy.K7DDRPHY(
                pads         = PHYPadsReducer(platform.request("ddram"), [0, 1]),
                memtype      = "DDR2",
                nphases      = 2,
                sys_clk_freq = sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = K4T1G164QGBCE7(sys_clk_freq, "1:2"),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            self.ethphy = K7_1000BASEX(
                refclk_or_clk_pads = self.crg.cd_eth.clk,
                data_pads          = self.platform.request("sfp", eth_sfp),
                sys_clk_freq       = self.clk_freq,
                with_csr           = False
            )
            self.comb += self.platform.request("sfp_tx_disable", eth_sfp).eq(0)
            self.comb += self.platform.request("sfp_rs0",        eth_sfp).eq(1)
            platform.add_platform_command("set_property SEVERITY {{Warning}} [get_drc_checks REQP-52]")
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, ip_address=eth_ip, with_ethmac=with_ethernet)
            elif with_ethernet:
                self.add_ethernet(phy=self.ethphy, dynamic_ip=eth_dynamic_ip, local_ip=eth_ip, remote_ip=remote_ip)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------
def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=hyvision_pcie_opt01_revf.Platform, description="LiteX SoC on HyVision PCIe OPT01 refv.")
    parser.add_target_argument("--sys-clk-freq",   default=100e6, type=float, help="System clock frequency.")

    # PCIe parameters.
    parser.add_target_argument("--with-pcie",      action="store_true",       help="Enable PCIe support.")
    parser.add_target_argument("--driver",         action="store_true",       help="Generate PCIe driver.")

    # Ethernet parameters.
    parser.add_target_argument("--with-ethernet",  action="store_true",       help="Enable Ethernet support.")
    parser.add_target_argument("--with-etherbone", action="store_true",       help="Enable Etherbone support.")
    parser.add_argument("--eth-sfp",               default=0, type=int,       help="Ethernet SFP.", choices=[0, 1])
    parser.add_target_argument("--eth-ip",         default="192.168.1.50",    help="Ethernet/Etherbone IP address.")
    parser.add_target_argument("--remote-ip",      default="192.168.1.100",   help="Remote IP address of TFTP server.")
    parser.add_target_argument("--eth-dynamic-ip", action="store_true",       help="Enable dynamic Ethernet IP addresses setting.")

    parser.set_defaults(uart_name="jtag_uart")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq   = args.sys_clk_freq,
        with_pcie      = args.with_pcie,
        with_ethernet  = args.with_ethernet,
        with_etherbone = args.with_etherbone,
        eth_sfp        = args.eth_sfp,
        eth_ip         = args.eth_ip,
        remote_ip      = args.remote_ip,
        eth_dynamic_ip = args.eth_dynamic_ip,
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
