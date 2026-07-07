#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

import os

from migen import *

from litex.gen import *

from litex_boards.platforms import sqrl_xcu1525

from litex.soc.cores.clock import *
from litex.soc.integration.soc import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litedram.modules import MT40A512M8
from litedram.phy import usddrphy

from liteeth.phy.usp_gty_1000basex import USP_GTY_1000BASEX

from litepcie.phy.usppciephy import USPPCIEPHY
from litepcie.software import generate_litepcie_software

# QSFP ---------------------------------------------------------------------------------------------

QSFP_PORTS = tuple(f"qsfp{qsfp}_sfp{sfp}" for qsfp in range(2) for sfp in range(4))

def parse_qsfp_port(port):
    if port not in QSFP_PORTS:
        raise ValueError("QSFP port must be one of: " + ", ".join(QSFP_PORTS))
    qsfp, sfp = port.replace("qsfp", "").split("_sfp")
    return int(qsfp), int(sfp)

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, ddram_channel, with_qsfp=False):
        self.rst       = Signal()
        self.cd_sys    = ClockDomain()
        self.cd_sys4x  = ClockDomain()
        self.cd_pll4x  = ClockDomain()
        self.cd_idelay = ClockDomain()
        if with_qsfp:
            self.cd_eth = ClockDomain()

        # # #

        self.pll = pll = USPMMCM(speedgrade=-2)
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(platform.request("clk300", ddram_channel), 300e6)
        pll.create_clkout(self.cd_pll4x, sys_clk_freq*4, buf=None, with_reset=False)
        pll.create_clkout(self.cd_idelay, 500e6)
        if with_qsfp:
            pll.create_clkout(self.cd_eth, 200e6, margin=0)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        self.specials += [
            Instance("BUFGCE_DIV",
                p_BUFGCE_DIVIDE=4,
                i_CE=1, i_I=self.cd_pll4x.clk, o_O=self.cd_sys.clk),
            Instance("BUFGCE",
                i_CE=1, i_I=self.cd_pll4x.clk, o_O=self.cd_sys4x.clk),
        ]

        self.idelayctrl = USPIDELAYCTRL(cd_ref=self.cd_idelay, cd_sys=self.cd_sys)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=125e6, ddram_channel=0,
        with_led_chaser       = True,
        with_pcie             = False,
        pcie_lanes            = 4,
        pcie_ndmas            = 1,
        pcie_address_width    = 32,
        with_pcie_dma_status  = False,
        with_pcie_dma_monitor = False,
        with_sata             = False,
        with_ethernet         = False,
        with_etherbone        = False,
        ethernet_port         = "qsfp0_sfp0",
        etherbone_port        = "qsfp0_sfp1",
        eth_ip                = "192.168.1.50",
        eth_dynamic_ip        = False,
        remote_ip             = None,
        etherbone_ip          = "192.168.1.50",
        **kwargs):
        platform = sqrl_xcu1525.Platform()
        if ddram_channel not in range(4):
            raise ValueError("DDRAM channel must be 0, 1, 2 or 3")
        if with_ethernet and with_etherbone and ethernet_port == etherbone_port:
            raise ValueError("Ethernet and Etherbone QSFP ports must be different")

        # CRG --------------------------------------------------------------------------------------
        with_qsfp = with_ethernet or with_etherbone
        self.crg = _CRG(platform, sys_clk_freq, ddram_channel, with_qsfp=with_qsfp)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on XCU1525", **kwargs)

        # DDR4 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.ddrphy = usddrphy.USPDDRPHY(
                pads             = platform.request("ddram", ddram_channel),
                memtype          = "DDR4",
                sys_clk_freq     = sys_clk_freq,
                iodelay_clk_freq = 500e6)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT40A512M8(sys_clk_freq, "1:4"),
                size          = 0x40000000,
                l2_cache_size = kwargs.get("l2_size", 8192)
            )
            # Workadound for Vivado 2018.2 DRC, can be ignored and probably fixed on newer Vivado versions.
            platform.add_platform_command("set_property SEVERITY {{Warning}} [get_drc_checks PDCN-2736]")

        # PCIe -------------------------------------------------------------------------------------
        if with_pcie:
            self.pcie_phy = USPPCIEPHY(platform, platform.request(f"pcie_x{pcie_lanes}"),
                data_width = {2: 64, 4: 128, 8: 256, 16: 512}[pcie_lanes],
                bar0_size  = 0x20000)
            self.add_pcie(
                phy              = self.pcie_phy,
                ndmas            = pcie_ndmas,
                address_width    = pcie_address_width,
                with_dma_status  = with_pcie_dma_status,
                with_dma_monitor = with_pcie_dma_monitor)

        # Ethernet / Etherbone ---------------------------------------------------------------------
        qsfp_in_use = [False, False]

        if with_ethernet:
            qsfp_id, sfp_lane = parse_qsfp_port(ethernet_port)
            self.ethphy = USP_GTY_1000BASEX(self.crg.cd_eth.clk,
                data_pads          = platform.request(f"qsfp{qsfp_id}_sfp{sfp_lane}"),
                sys_clk_freq       = self.clk_freq,
                refclk_from_fabric = True)
            self.add_ethernet(
                phy        = self.ethphy,
                local_ip   = eth_ip if not eth_dynamic_ip else None,
                dynamic_ip = eth_dynamic_ip,
                remote_ip  = remote_ip)
            qsfp_in_use[qsfp_id] = True

        if with_etherbone:
            qsfp_id, sfp_lane = parse_qsfp_port(etherbone_port)
            self.bonephy = USP_GTY_1000BASEX(self.crg.cd_eth.clk,
                data_pads          = platform.request(f"qsfp{qsfp_id}_sfp{sfp_lane}"),
                sys_clk_freq       = self.clk_freq,
                refclk_from_fabric = True)
            self.add_etherbone(phy=self.bonephy, ip_address=etherbone_ip)
            qsfp_in_use[qsfp_id] = True

        # SATA -------------------------------------------------------------------------------------
        if with_sata:
            from litex.build.generic_platform import Subsignal, Pins
            from litesata.phy import LiteSATAPHY

            # IOs
            _sata_io = [
                # SFP 2 SATA Adapter / https://shop.trenz-electronic.de/en/TE0424-01-SFP-2-SATA-Adapter
                ("qsfp2sata", 0,
                    Subsignal("tx_p", Pins("N9")),
                    Subsignal("tx_n", Pins("N8")),
                    Subsignal("rx_p", Pins("N4")),
                    Subsignal("rx_n", Pins("N3")),
                ),
            ]
            platform.add_extension(_sata_io)

            # RefClk, Generate 150MHz from PLL.
            self.cd_sata_refclk = ClockDomain()
            self.crg.pll.create_clkout(self.cd_sata_refclk, 150e6)
            sata_refclk = ClockSignal("sata_refclk")

            # PHY
            self.sata_phy = LiteSATAPHY(platform.device,
                refclk     = sata_refclk,
                pads       = platform.request("qsfp2sata"),
                gen        = "gen2",
                clk_freq   = sys_clk_freq,
                data_width = 16)

            # Core
            self.add_sata(phy=self.sata_phy, mode="read+write")
            qsfp_in_use[0] = True

        for qsfp_id, in_use in enumerate(qsfp_in_use):
            if in_use:
                resetl = platform.request(f"qsfp{qsfp_id}_resetl")
                lpmode = platform.request(f"qsfp{qsfp_id}_lpmode")

                reset_cycles = int(sys_clk_freq*10e-3)
                reset_count  = Signal(max=reset_cycles + 1, reset=reset_cycles)
                self.sync += [
                    If(ResetSignal("sys"),
                        reset_count.eq(reset_cycles)
                    ).Elif(reset_count != 0,
                        reset_count.eq(reset_count - 1)
                    )
                ]
                self.comb += [
                    resetl.eq(~(ResetSignal("sys") | (reset_count != 0))),
                    lpmode.eq(0),
                ]

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=sqrl_xcu1525.Platform, description="LiteX SoC on XCU1525.")
    parser.add_target_argument("--sys-clk-freq",  default=125e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--ddram-channel", default=0, type=lambda x: int(x, 0), choices=range(4), help="DDRAM channel (0, 1, 2 or 3).")
    parser.add_target_argument("--with-pcie",     action="store_true",        help="Enable PCIe support.")
    parser.add_target_argument("--pcie-lanes",    default=4, type=int,        choices=[2, 4, 8, 16], help="PCIe lane count.")
    parser.add_target_argument("--pcie-ndmas",    default=1, type=int,        help="Number of PCIe DMA channels.")
    parser.add_target_argument("--pcie-address-width", default=32, type=int, choices=[32, 64], help="PCIe address width.")
    parser.add_target_argument("--pcie-with-dma-status",  action="store_true",       help="Enable PCIe DMA status CSRs.")
    parser.add_target_argument("--pcie-with-dma-monitor", action="store_true",       help="Enable PCIe DMA monitor CSRs.")
    parser.add_target_argument("--with-ethernet",         action="store_true",       help="Enable Ethernet support over QSFP/SFP.")
    parser.add_target_argument("--with-etherbone",        action="store_true",       help="Enable Etherbone support over QSFP/SFP.")
    parser.add_target_argument("--ethernet-port",  default="qsfp0_sfp0", choices=QSFP_PORTS, help="Ethernet QSFP/SFP port.")
    parser.add_target_argument("--etherbone-port", default="qsfp0_sfp1", choices=QSFP_PORTS, help="Etherbone QSFP/SFP port.")
    parser.add_target_argument("--ethernet-ip",    default="192.168.1.50",    help="Ethernet IP address.")
    parser.add_target_argument("--remote-ip",      default="192.168.1.100",   help="Remote IP address of TFTP server.")
    parser.add_target_argument("--eth-dynamic-ip", action="store_true",       help="Enable dynamic Ethernet IP assignment.")
    parser.add_target_argument("--etherbone-ip",   default="192.168.1.50",    help="Etherbone IP address.")
    parser.add_target_argument("--driver",        action="store_true",        help="Generate PCIe driver.")
    parser.add_target_argument("--with-sata",     action="store_true",        help="Enable SATA support (over SFP2SATA on qsfp0_sfp0).")
    args = parser.parse_args()
    if args.with_etherbone and args.eth_dynamic_ip:
        parser.error("--eth-dynamic-ip cannot be used with Etherbone.")
    if args.pcie_ndmas < 0:
        parser.error("--pcie-ndmas must be >= 0")
    if args.with_ethernet and args.with_etherbone and args.ethernet_port == args.etherbone_port:
        parser.error("Ethernet and Etherbone QSFP ports must be different.")
    if args.with_sata:
        for feature, port in [
            ("Ethernet",  args.ethernet_port  if args.with_ethernet  else None),
            ("Etherbone", args.etherbone_port if args.with_etherbone else None),
        ]:
            if port == "qsfp0_sfp0":
                parser.error(f"{feature} on qsfp0_sfp0 conflicts with SATA.")

    soc = BaseSoC(
        sys_clk_freq          = args.sys_clk_freq,
        ddram_channel         = args.ddram_channel,
        with_pcie             = args.with_pcie,
        pcie_lanes            = args.pcie_lanes,
        pcie_ndmas            = args.pcie_ndmas,
        pcie_address_width    = args.pcie_address_width,
        with_pcie_dma_status  = args.pcie_with_dma_status,
        with_pcie_dma_monitor = args.pcie_with_dma_monitor,
        with_sata             = args.with_sata,
        with_ethernet         = args.with_ethernet,
        with_etherbone        = args.with_etherbone,
        ethernet_port         = args.ethernet_port,
        etherbone_port        = args.etherbone_port,
        eth_ip                = args.ethernet_ip,
        eth_dynamic_ip        = args.eth_dynamic_ip,
        remote_ip             = args.remote_ip,
        etherbone_ip          = args.etherbone_ip,
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
