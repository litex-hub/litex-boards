#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2018-2020 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

import os

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from litex_boards.platforms import xilinx_kcu105

from litex.soc.cores.clock import *
from litex.soc.integration.soc import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.gpio import GPIOIn

from litedram.modules import EDY4016A
from litedram.phy import usddrphy

from liteeth.phy.ku_1000basex      import KU_1000BASEX
from liteeth.phy.us_lvds_1000basex import US_LVDS_1000BASEX

from litepcie.phy.uspciephy import USPCIEPHY
from litepcie.software import generate_litepcie_software

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst       = Signal()
        self.cd_sys    = ClockDomain()
        self.cd_sys4x  = ClockDomain()
        self.cd_pll4x  = ClockDomain()
        self.cd_idelay = ClockDomain()
        self.cd_eth    = ClockDomain()
        self.iodelay_clk_freq = 200e6
        self.serdes_locked    = Signal(reset=1) # Holds the IDELAYCTRL until a SerDes locks.

        # # #

        self.pll = pll = USMMCM(speedgrade=-2)
        self.comb += pll.reset.eq(platform.request("cpu_reset") | self.rst)
        pll.register_clkin(platform.request("clk125"), 125e6)
        pll.create_clkout(self.cd_pll4x, sys_clk_freq*4, buf=None, with_reset=False)
        pll.create_clkout(self.cd_idelay, self.iodelay_clk_freq, with_reset=False)
        pll.create_clkout(self.cd_eth,    200e6)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        self.specials += [
            Instance("BUFGCE_DIV",
                p_BUFGCE_DIVIDE=4,
                i_CE=1, i_I=self.cd_pll4x.clk, o_O=self.cd_sys.clk),
            Instance("BUFGCE",
                i_CE=1, i_I=self.cd_pll4x.clk, o_O=self.cd_sys4x.clk),
            # UG571 reset order: IDELAYCTRL and the IDELAYE3s it serves are released together.
            AsyncResetSynchronizer(self.cd_idelay, ~pll.locked | ~self.serdes_locked),
        ]

        self.idelayctrl = USIDELAYCTRL(cd_ref=self.cd_idelay, cd_sys=self.cd_sys)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=125e6,
        with_ethernet   = False,
        with_etherbone  = False,
        eth_phy         = "sfp",
        eth_ip          = "192.168.1.50",
        remote_ip       = None,
        eth_dynamic_ip  = False,
        with_led_chaser = True,
        with_pcie       = False,
        pcie_lanes      = 4,
        with_sata       = False,
        with_sdcard     = False,
        with_buttons    = False,
        with_switches   = False,
        **kwargs):
        platform = xilinx_kcu105.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on KCU105", **kwargs)

        # DDR4 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.ddrphy = usddrphy.USDDRPHY(platform.request("ddram"),
                memtype          = "DDR4",
                sys_clk_freq     = sys_clk_freq,
                iodelay_clk_freq = self.crg.iodelay_clk_freq)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = EDY4016A(sys_clk_freq, "1:4"),
                size          = 0x40000000,
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            # SFP0: 1000BASE-X on a GTH transceiver.
            eth_timing_constraints = True
            if eth_phy == "sfp":
                self.ethphy = KU_1000BASEX(self.crg.cd_eth.clk,
                    data_pads    = self.platform.request("sfp", 0),
                    sys_clk_freq = self.clk_freq)
                self.comb += self.platform.request("sfp_tx_disable_n", 0).eq(1)
                self.platform.add_platform_command(
                    "set_property SEVERITY {{Warning}} [get_drc_checks REQP-1753]")
            # RJ45: SGMII over LVDS SelectIO to the on-board PHY, clocked by its 625MHz SGMII clock.
            elif eth_phy == "rj45":
                self.ethphy = US_LVDS_1000BASEX(
                    pads               = self.platform.request("eth"),
                    refclk_or_clk_pads = self.platform.request("eth_clocks"),
                    sys_clk_freq       = self.clk_freq,
                    speedgrade         = -2,
                    iodelay_clk_freq   = self.crg.iodelay_clk_freq,
                    pcs_kwargs         = {"sgmii": True}) # The on-board PHY is strapped for SGMII.
                self.comb += self.crg.serdes_locked.eq(self.ethphy.crg.locked)
                # The eth_rx/eth_tx clocks are MMCM outputs Vivado derives from the 625MHz
                # reference; a create_clock on their nets is redundant and fails at synthesis.
                eth_timing_constraints = False
                self.platform.add_false_path_constraints(self.crg.cd_sys.clk,
                    self.ethphy.crg.cd_eth_rx.clk, self.ethphy.crg.cd_eth_tx.clk)
            else:
                raise ValueError(f"Unsupported eth_phy: {eth_phy}")
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, ip_address=eth_ip, with_ethmac=with_ethernet,
                    with_timing_constraints = eth_timing_constraints)
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy,
                    dynamic_ip              = eth_dynamic_ip,
                    local_ip                = None if eth_dynamic_ip else eth_ip,
                    remote_ip               = remote_ip,
                    with_timing_constraints = eth_timing_constraints)

        # PCIe -------------------------------------------------------------------------------------
        if with_pcie:
            self.pcie_phy = USPCIEPHY(platform, platform.request(f"pcie_x{pcie_lanes}"),
                data_width = {4: 128, 8: 256}[pcie_lanes],
                bar0_size  = 0x20000)
            self.add_pcie(phy=self.pcie_phy, ndmas=1)

        # SATA -------------------------------------------------------------------------------------
        if with_sata:
            from litex.build.generic_platform import Subsignal, Pins
            from litesata.phy import LiteSATAPHY

            # IOs
            _sata_io = [
                # SFP 2 SATA Adapter / https://shop.trenz-electronic.de/en/TE0424-01-SFP-2-SATA-Adapter
                ("sfp2sata", 0,
                    Subsignal("tx_p", Pins("U4")),
                    Subsignal("tx_n", Pins("U3")),
                    Subsignal("rx_p", Pins("T2")),
                    Subsignal("rx_n", Pins("T1")),
                ),
            ]
            platform.add_extension(_sata_io)

            # RefClk, Generate 150MHz from PLL.
            self.cd_sata_refclk = ClockDomain()
            self.crg.pll.create_clkout(self.cd_sata_refclk, 150e6)
            sata_refclk = ClockSignal("sata_refclk")
            platform.add_platform_command("set_property SEVERITY {{Warning}} [get_drc_checks REQP-1753]")

            # PHY
            self.sata_phy = LiteSATAPHY(platform.device,
                refclk     = sata_refclk,
                pads       = platform.request("sfp2sata"),
                gen        = "gen2",
                clk_freq   = sys_clk_freq,
                data_width = 16)

            # Core
            self.add_sata(phy=self.sata_phy, mode="read+write")

        # SD Card ----------------------------------------------------------------------------------
        if with_sdcard:
            self.add_sdcard()

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

        # Buttons / Switches -----------------------------------------------------------------------
        if with_buttons:
            self.buttons = GPIOIn(Cat(
                platform.request("user_btn_c"),
                platform.request("user_btn_e"),
                platform.request("user_btn_n"),
                platform.request("user_btn_s"),
                platform.request("user_btn_w"),
            ))
        if with_switches:
            self.switches = GPIOIn(Cat(platform.request_all("user_dip_btn")))

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=xilinx_kcu105.Platform, description="LiteX SoC on KCU105.")
    parser.add_target_argument("--sys-clk-freq",        default=125e6, type=float, help="System clock frequency.")
    ethopts = parser.target_group.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",  action="store_true", help="Enable Ethernet support.")
    ethopts.add_argument("--with-etherbone", action="store_true", help="Enable Etherbone support.")
    parser.add_target_argument("--eth-phy",        default="sfp", choices=["sfp", "rj45"],
        help="Ethernet PHY: sfp (SFP0, 1000BASE-X) or rj45 (on-board SGMII PHY).")
    parser.add_target_argument("--eth-ip",         default="192.168.1.50",  help="Ethernet/Etherbone IP address.")
    parser.add_target_argument("--eth-dynamic-ip", action="store_true",     help="Enable dynamic Ethernet IP assignment.")
    parser.add_target_argument("--remote-ip",      default="192.168.1.100", help="Remote IP address of TFTP server.")
    parser.add_target_argument("--with-pcie",      action="store_true",     help="Enable PCIe support.")
    parser.add_target_argument("--pcie-lanes",     default=4, type=int,     choices=[4, 8], help="PCIe lane count.")
    parser.add_target_argument("--driver",         action="store_true",     help="Generate PCIe driver.")
    parser.add_target_argument("--with-sata",      action="store_true",     help="Enable SATA support (over SFP2SATA).")
    parser.add_target_argument("--with-sdcard",    action="store_true",     help="Enable SDCard support.")
    parser.add_target_argument("--with-buttons",   action="store_true",     help="Enable Buttons.")
    parser.add_target_argument("--with-switches",  action="store_true",     help="Enable Switches.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq   = args.sys_clk_freq,
        with_ethernet  = args.with_ethernet,
        with_etherbone = args.with_etherbone,
        eth_phy        = args.eth_phy,
        eth_ip         = args.eth_ip,
        remote_ip      = args.remote_ip,
        eth_dynamic_ip = args.eth_dynamic_ip,
        with_pcie      = args.with_pcie,
        pcie_lanes     = args.pcie_lanes,
        with_sata      = args.with_sata,
        with_sdcard    = args.with_sdcard,
        with_buttons   = args.with_buttons,
        with_switches  = args.with_switches,
        **parser.soc_argdict
    )
    builder = Builder(soc, **parser.builder_argdict)
    if args.build or args.driver:
        if not args.build:
            builder.compile_software = False
            builder.compile_gateware = False
        builder.build(**parser.toolchain_argdict)

    if args.driver:
        generate_litepcie_software(soc, os.path.join(builder.output_dir, "driver"))

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
