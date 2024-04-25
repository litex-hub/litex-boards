#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2024 Gwenhael Goavec-Merou <gwenhael@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# Build/use
# Build/Load bitstream:
# ./xilinx_zc7006.py --with-etherbone --uart-name=crossover --csr-csv=csr.csv --build --load
#
# Test Ethernet:
# ping 192.168.1.50
#
# Test Console:
# litex_server --udp
# litex_term crossover
#
#
# Build/Load bitstream:
# ./xilinx_zc706.py --with-jtagbone --uart-name=crossover --csr-csv=csr.csv --build --load
#
# litex_server --jtag --jtag-config openocd_xc7z_smt2-nc.cfg
#
# In a second terminal:
# litex_cli --regs # to dump all registers
# Or
# litex_term crossover # to have access to LiteX bios
#
# --------------------------------------------------------------------------------------------------

from migen import *

from litex.gen import *

from litex_boards.platforms import xilinx_zc706

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litedram.modules import MT8JTF12864
from litedram.phy import s7ddrphy

from liteeth.phy.k7_1000basex import K7_1000BASEX

from litepcie.phy.s7pciephy import S7PCIEPHY
from litepcie.software import generate_litepcie_software

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst       = Signal()
        self.cd_sys    = ClockDomain()
        self.cd_sys4x  = ClockDomain()
        self.cd_idelay = ClockDomain()
        self.cd_eth    = ClockDomain()

        # # #

        # Clk/Rst.
        clk200 = platform.request("clk200")

        # PLL.
        self.pll = pll = S7PLL(speedgrade=-1)
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk200, 200e6)
        pll.create_clkout(self.cd_sys,    sys_clk_freq)
        pll.create_clkout(self.cd_sys4x,  4*sys_clk_freq)
        pll.create_clkout(self.cd_idelay, 200e6)
        pll.create_clkout(self.cd_eth,    200e6)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        # IDelayCtrl.
        self.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=125e6,
        with_ethernet   = False,
        with_etherbone  = False,
        eth_ip          = "192.168.1.50",
        remote_ip       = None,
        eth_dynamic_ip  = False,
        with_led_chaser = True,
        with_pcie       = False,
        **kwargs):
        platform = xilinx_zc706.Platform()

        # When nor jtagbone, nor etherbone are set forces jtagbone.
        kwargs["uart_name"]     = "crossover"
        if not (kwargs["with_jtagbone"] or with_etherbone):
            kwargs["with_jtagbone"] = True

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on ZC706", **kwargs)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.ddrphy = s7ddrphy.K7DDRPHY(platform.request("ddram"),
                memtype      = "DDR3",
                nphases      = 4,
                sys_clk_freq = sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT8JTF12864(sys_clk_freq, "1:4"),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            self.ethphy = K7_1000BASEX(
                refclk_or_clk_pads = self.crg.cd_eth.clk,
                data_pads          = self.platform.request("sfp", 0),
                sys_clk_freq       = self.clk_freq,
                with_csr           = False
            )
            self.comb += self.platform.request("sfp_tx_disable_n", 0).eq(1)
            platform.add_platform_command("set_property SEVERITY {{Warning}} [get_drc_checks REQP-52]")
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, ip_address=eth_ip, with_ethmac=with_ethernet)
            elif with_ethernet:
                self.add_ethernet(phy=self.ethphy, dynamic_ip=eth_dynamic_ip, local_ip=eth_ip, remote_ip=remote_ip)

        # PCIe -------------------------------------------------------------------------------------
        if with_pcie:
            self.pcie_phy = S7PCIEPHY(platform, platform.request("pcie_x4"),
                data_width = 128,
                bar0_size  = 0x20000)
            self.add_pcie(phy=self.pcie_phy, ndmas=1)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq
            )

# Build --------------------------------------------------------------------------------------------
def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=xilinx_zc706.Platform, description="LiteX SoC on ZC706.")
    parser.add_target_argument("--sys-clk-freq",   default=125e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--programmer",     default="vivado",          help="Programmer select from Vivado/openFPGALoader.")
    parser.add_target_argument("--with-ethernet",  action="store_true",       help="Enable Ethernet support.")
    parser.add_target_argument("--with-etherbone", action="store_true",       help="Enable Etherbone support.")
    parser.add_target_argument("--eth-ip",         default="192.168.1.50",    help="Ethernet/Etherbone IP address.")
    parser.add_target_argument("--remote-ip",      default="192.168.1.100",   help="Remote IP address of TFTP server.")
    parser.add_target_argument("--eth-dynamic-ip", action="store_true",       help="Enable dynamic Ethernet IP addresses setting.")
    parser.add_target_argument("--with-pcie",      action="store_true",       help="Enable PCIe support.")
    parser.add_target_argument("--driver",         action="store_true",       help="Generate PCIe driver.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq   = args.sys_clk_freq,
        with_ethernet  = args.with_ethernet,
        with_etherbone = args.with_etherbone,
        eth_ip         = args.eth_ip,
        remote_ip      = args.remote_ip,
        eth_dynamic_ip = args.eth_dynamic_ip,
        with_pcie      = args.with_pcie,
        **parser.soc_argdict
    )
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.driver:
        generate_litepcie_software(soc, os.path.join(builder.output_dir, "driver"))

    if args.load:
        prog = soc.platform.create_programmer(args.programmer)
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"), device=1)

if __name__ == "__main__":
    main()
