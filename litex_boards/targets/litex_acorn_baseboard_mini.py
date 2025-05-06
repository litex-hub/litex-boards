#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021-2024 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

import subprocess

from migen import *

from litex.gen import *

from litex.build.generic_platform import Subsignal, Pins
from litex.build.io import DifferentialInput
from litex.build.openocd import OpenOCD

from litex_boards.platforms import sqrl_acorn

from litex.soc.interconnect.csr import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

from litex.soc.cores.clock import *
from litex.soc.cores.led import LedChaser

from litex.build.generic_platform import IOStandard, Subsignal, Pins

from litepcie.phy.s7pciephy import S7PCIEPHY
from litepcie.software import generate_litepcie_software

from litedram.modules import MT41K512M16
from litedram.phy import s7ddrphy

from liteeth.phy.a7_gtp import QPLLSettings, QPLL
from liteeth.phy.a7_1000basex import A7_1000BASEX

from litesata.phy import LiteSATAPHY

# CRG ----------------------------------------------------------------------------------------------

class CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_dram=False, with_eth=False, with_sata=False):
        self.rst          = Signal()
        self.cd_sys       = ClockDomain()
        self.cd_sys4x     = ClockDomain()
        self.cd_sys4x_dqs = ClockDomain()
        self.cd_idelay    = ClockDomain()

        # Clk/Rst.
        clk200    = platform.request("clk200")
        clk200_se = Signal()
        self.specials += DifferentialInput(clk200.p, clk200.n, clk200_se)

        # PLL.
        self.pll = pll = S7PLL()
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk200_se, 200e6)
        pll.create_clkout(self.cd_sys,       sys_clk_freq)
        if with_dram:
            pll.create_clkout(self.cd_sys4x,     4*sys_clk_freq)
            pll.create_clkout(self.cd_sys4x_dqs, 4*sys_clk_freq, phase=90)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        # IDelayCtrl.
        if with_dram:
            self.specials += Instance("BUFG", i_I=clk200_se, o_O=self.cd_idelay.clk)
            self.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

        # Eth PLL.
        if with_eth:
            self.cd_eth_ref = ClockDomain()
            self.eth_pll = eth_pll = S7PLL()
            self.comb += eth_pll.reset.eq(self.rst)
            eth_pll.register_clkin(clk200_se, 200e6)
            eth_pll.create_clkout(self.cd_eth_ref, 156.25e6, margin=0)

        # SATA PLL.
        if with_sata:
            self.cd_sata_ref = ClockDomain()
            self.sata_pll = sata_pll = S7PLL()
            self.comb += sata_pll.reset.eq(self.rst)
            sata_pll.register_clkin(clk200_se, 200e6)
            sata_pll.create_clkout(self.cd_sata_ref, 150e6, margin=0)

# BaseSoC -----------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, variant="cle-215+", sys_clk_freq=125e6,
        with_pcie       = False,
        with_ethernet   = False,
        with_etherbone  = False,
        eth_ip          = "192.168.1.50",
        remote_ip       = None,
        eth_dynamic_ip  = False,
        with_led_chaser = True,
        with_sata       = False, sata_gen="gen2",
        **kwargs):
        platform = sqrl_acorn.Platform(variant=variant)
        platform.add_extension(sqrl_acorn._litex_acorn_baseboard_mini_io, prepend=True)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Acorn CLE-101/215(+)", **kwargs)

        # CRG --------------------------------------------------------------------------------------
        with_eth = (with_ethernet or with_etherbone)
        self.crg = CRG(platform, sys_clk_freq,
            with_dram = not self.integrated_main_ram_size,
            with_eth  = with_eth,
            with_sata = with_sata,
        )

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.ddrphy = s7ddrphy.A7DDRPHY(platform.request("ddram"),
                memtype        = "DDR3",
                nphases        = 4,
                sys_clk_freq   = sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT41K512M16(sys_clk_freq, "1:4"),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # PCIe -------------------------------------------------------------------------------------
        if with_pcie:
            assert not with_sata
            self.pcie_phy = S7PCIEPHY(platform, platform.request("pcie_x1"),
                data_width = 64,
                bar0_size  = 0x20000)
            self.add_pcie(phy=self.pcie_phy, ndmas=1)
            platform.toolchain.pre_placement_commands.append("reset_property LOC [get_cells -hierarchical -filter {{NAME=~pcie_s7/*gtp_channel.gtpe2_channel_i}}]")
            platform.toolchain.pre_placement_commands.append("set_property LOC GTPE2_CHANNEL_X0Y7 [get_cells -hierarchical -filter {{NAME=~pcie_s7/*gtp_channel.gtpe2_channel_i}}]")

        # PCIe / Ethernet / SATA / Shared-QPLL -----------------------------------------------------

        if not with_pcie:
            # Ethernet QPLL Settings.
            qpll_eth_settings = QPLLSettings(
                refclksel  = 0b111,
                fbdiv      = 4,
                fbdiv_45   = 4,
                refclk_div = 1,
            )
            platform.add_platform_command("set_property SEVERITY {{Warning}} [get_drc_checks REQP-49]")

            # SATA QPLL Settings.
            qpll_sata_settings = QPLLSettings(
                refclksel  = 0b111,
                fbdiv      = 5,
                fbdiv_45   = 4,
                refclk_div = 1,
            )
            platform.add_platform_command("set_property SEVERITY {{Warning}} [get_drc_checks REQP-49]")

            # Shared QPLL.
            self.qpll = qpll = QPLL(
                gtgrefclk0    = Open() if not with_eth  else self.crg.cd_eth_ref.clk,
                qpllsettings0 = None   if not with_eth  else qpll_eth_settings,
                gtgrefclk1    = Open() if not with_sata else self.crg.cd_sata_ref.clk,
                qpllsettings1 = None   if not with_sata else qpll_sata_settings,
            )

        if with_pcie:
            # PCIe QPLL Settings.
            qpll_pcie_settings = QPLLSettings(
                refclksel  = 0b001,
                fbdiv      = 5,
                fbdiv_45   = 5,
                refclk_div = 1,
            )

            # Ethernet QPLL Settings.
            qpll_eth_settings = QPLLSettings(
                refclksel  = 0b111,
                fbdiv      = 4,
                fbdiv_45   = 4,
                refclk_div = 1,
            )
            platform.add_platform_command("set_property SEVERITY {{Warning}} [get_drc_checks REQP-49]")

            # Shared QPLL.
            self.qpll = qpll = QPLL(
                gtrefclk0     = Open() if not with_pcie else self.pcie_phy.pcie_refclk,
                qpllsettings0 = None   if not with_pcie else qpll_pcie_settings,
                gtgrefclk1    = Open() if not with_eth  else self.crg.cd_eth_ref.clk,
                qpllsettings1 = None   if not with_eth  else qpll_eth_settings,
            )
            self.pcie_phy.use_external_qpll(qpll_channel=qpll.channels[0])

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            self.ethphy = A7_1000BASEX(
                qpll_channel = qpll.channels[1 if with_pcie else 0],
                data_pads    = self.platform.request("sfp"),
                sys_clk_freq = sys_clk_freq,
                rx_polarity  = 1,  # Inverted on Acorn.
                tx_polarity  = 0   # Inverted on Acorn and on baseboard.
            )

            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, ip_address=eth_ip, with_ethmac=with_ethernet)
            elif with_ethernet:
                self.add_ethernet(phy=self.ethphy, dynamic_ip=eth_dynamic_ip, local_ip=eth_ip, remote_ip=remote_ip)

        # SATA -------------------------------------------------------------------------------------
        if with_sata:
            # PHY
            self.sata_phy = LiteSATAPHY(platform.device,
                refclk     = self.crg.cd_sata_ref.clk,
                pads       = platform.request("sata"),
                gen        = sata_gen,
                clk_freq   = sys_clk_freq,
                data_width = 16,
                qpll       = qpll.channels[1],
            )
            platform.add_platform_command("set_property SEVERITY {{WARNING}} [get_drc_checks REQP-49]")

            # Core
            self.add_sata(phy=self.sata_phy, mode="read+write")

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=sqrl_acorn.Platform, description="LiteX SoC on Acorn CLE-101/215(+).")
    parser.add_target_argument("--flash",          action="store_true",          help="Flash bitstream.")
    parser.add_target_argument("--variant",        default="cle-215+",           help="Board variant (cle-215+, cle-215 or cle-101).")
    parser.add_target_argument("--programmer",     default="openocd",            help="Programmer select from OpenOCD/openFPGALoader.",
        choices=[
            "openocd",
            "openfpgaloader"
    ])
    parser.add_target_argument("--sys-clk-freq",   default=125.00e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-pcie",      action="store_true",          help="Enable PCIe support.")
    parser.add_target_argument("--driver",         action="store_true",          help="Generate PCIe driver.")
    parser.add_target_argument("--with-ethernet",  action="store_true",          help="Enable Ethernet support.")
    parser.add_target_argument("--with-etherbone", action="store_true",          help="Enable Etherbone support.")
    parser.add_target_argument("--eth-ip",         default="192.168.1.50",       help="Ethernet/Etherbone IP address.")
    parser.add_target_argument("--remote-ip",      default="192.168.1.100",      help="Remote IP address of TFTP server.")
    parser.add_target_argument("--eth-dynamic-ip", action="store_true",          help="Enable dynamic Ethernet IP addresses setting.")
    parser.add_target_argument("--with-sata",      action="store_true",          help="Enable SATA support (over FMCRAID).")
    parser.add_target_argument("--sata-gen",       default="2",                  help="SATA Gen.", choices=["1", "2"])
    args = parser.parse_args()

    soc = BaseSoC(
        variant        = args.variant,
        sys_clk_freq   = args.sys_clk_freq,
        with_pcie      = args.with_pcie,
        with_ethernet  = args.with_ethernet,
        with_etherbone = args.with_etherbone,
        eth_ip         = args.eth_ip,
        remote_ip      = args.remote_ip,
        eth_dynamic_ip = args.eth_dynamic_ip,
        with_sata      = args.with_sata,
        sata_gen       = "gen" + args.sata_gen,
        **parser.soc_argdict
    )

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.driver:
        generate_litepcie_software(soc, os.path.join(builder.output_dir, "driver"))

    if args.load:
        prog = soc.platform.create_programmer(args.programmer)
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer(args.programmer)
        prog.flash(0, builder.get_bitstream_filename(mode="flash"))

if __name__ == "__main__":
    main()
