#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Fei Gao <feig@princeton.edu>
# Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2020 David Shah <dave@ds0.me>
# SPDX-License-Identifier: BSD-2-Clause

import os

from migen import *

from litex.gen import *

from litex_boards.platforms import xilinx_alveo_u250
from litex_boards.targets.usp_gty_10g import (
    LiteEthPHYUSPGTY10G,
    USP_GTY_10GBASE_R_REFCLK_FREQ,
    gty_data_pads_lane,
    gty_refclk_from_pads,
)

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

from litex.soc.cores.led import LedChaser
from litedram.modules import MTA18ASF2G72PZ
from litedram.phy import usddrphy

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
    def __init__(self, platform, sys_clk_freq):
        self.rst       = Signal()
        self.cd_sys    = ClockDomain()
        self.cd_sys4x  = ClockDomain()
        self.cd_pll4x  = ClockDomain()
        self.cd_idelay = ClockDomain()

        # # #

        self.pll = pll = USMMCM(speedgrade=-2)
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(platform.request("clk300", 0), 300e6)
        pll.create_clkout(self.cd_pll4x, sys_clk_freq*4, buf=None, with_reset=False)
        pll.create_clkout(self.cd_idelay, 500e6)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        self.specials += [
            Instance("BUFGCE_DIV",
                p_BUFGCE_DIVIDE=4,
                i_CE=1, i_I=self.cd_pll4x.clk, o_O=self.cd_sys.clk),
            Instance("BUFGCE",
                i_CE=1, i_I=self.cd_pll4x.clk, o_O=self.cd_sys4x.clk),
        ]

        self.idelayctrl = USIDELAYCTRL(cd_ref=self.cd_idelay, cd_sys=self.cd_sys)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=125e6, with_led_chaser=True,
        with_ethernet         = False,
        ethernet_port         = "qsfp0_sfp0",
        eth_ip                = "192.168.1.50",
        eth_dynamic_ip        = False,
        remote_ip             = None,
        with_pcie             = False,
        pcie_lanes            = 4,
        pcie_ndmas            = 1,
        pcie_address_width    = 32,
        with_pcie_dma_status  = False,
        with_pcie_dma_monitor = False,
        **kwargs):
        platform = xilinx_alveo_u250.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Alveo U250", **kwargs)

        # DDR4 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.ddrphy = usddrphy.USPDDRPHY(platform.request("ddram"),
                memtype          = "DDR4",
                sys_clk_freq     = sys_clk_freq,
                cmd_latency      = 1,
                iodelay_clk_freq = 500e6,
                is_rdimm         = True)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MTA18ASF2G72PZ(sys_clk_freq, "1:4"),
                size          = 0x40000000,
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Firmware RAM (To ease initial LiteDRAM calibration support) ------------------------------
        self.add_ram("firmware_ram", 0x20000000, 0x8000)

        # PCIe -------------------------------------------------------------------------------------
        if with_pcie:
            self.pcie_phy = USPPCIEPHY(platform, platform.request(f"pcie_x{pcie_lanes}"),
                data_width = {4: 128, 16: 512}[pcie_lanes],
                bar0_size  = 0x20000)
            self.add_pcie(
                phy              = self.pcie_phy,
                ndmas            = pcie_ndmas,
                address_width    = pcie_address_width,
                with_dma_status  = with_pcie_dma_status,
                with_dma_monitor = with_pcie_dma_monitor)

        # Ethernet ---------------------------------------------------------------------------------
        if with_ethernet:
            qsfp_id, sfp_lane = parse_qsfp_port(ethernet_port)
            qsfp_pads = platform.request("qsfp28", qsfp_id)
            self.ethphy = LiteEthPHYUSPGTY10G(
                platform     = platform,
                refclk       = gty_refclk_from_pads(self, qsfp_pads),
                data_pads    = gty_data_pads_lane(self, qsfp_pads, sfp_lane),
                sys_clk_freq = self.clk_freq,
                refclk_freq  = USP_GTY_10GBASE_R_REFCLK_FREQ)
            self.add_ethernet(
                phy        = self.ethphy,
                data_width = 32,
                dynamic_ip = eth_dynamic_ip,
                local_ip   = eth_ip if not eth_dynamic_ip else None,
                remote_ip  = remote_ip)

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
                qsfp_pads.resetl.eq(~(ResetSignal("sys") | (reset_count != 0))),
                qsfp_pads.lpmode.eq(0),
                qsfp_pads.refclk_reset.eq(0),
                qsfp_pads.fs0.eq(1),
                qsfp_pads.fs1.eq(0),
            ]

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=xilinx_alveo_u250.Platform, description="LiteX SoC on Alveo U250.")
    parser.add_target_argument("--sys-clk-freq",        default=125e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-ethernet",       action="store_true",       help="Enable 10G Ethernet support.")
    parser.add_target_argument("--ethernet-port",       default="qsfp0_sfp0",      choices=QSFP_PORTS, help="Ethernet QSFP port.")
    parser.add_target_argument("--ethernet-ip",         default="192.168.1.50",    help="Ethernet IP address.")
    parser.add_target_argument("--eth-dynamic-ip",      action="store_true",       help="Enable dynamic Ethernet IP assignment.")
    parser.add_target_argument("--remote-ip",           default="192.168.1.100",   help="Remote IP address of TFTP server.")
    parser.add_target_argument("--with-pcie",           action="store_true",       help="Enable PCIe support.")
    parser.add_target_argument("--pcie-lanes",          default=4, type=int,       choices=[4, 16], help="PCIe lane count.")
    parser.add_target_argument("--pcie-ndmas",          default=1, type=int,       help="Number of PCIe DMA channels.")
    parser.add_target_argument("--pcie-address-width", default=32, type=int, choices=[32, 64], help="PCIe address width.")
    parser.add_target_argument("--pcie-with-dma-status",  action="store_true",        help="Enable PCIe DMA status CSRs.")
    parser.add_target_argument("--pcie-with-dma-monitor", action="store_true",        help="Enable PCIe DMA monitor CSRs.")
    parser.add_target_argument("--driver",                action="store_true",        help="Generate PCIe driver.")
    args = parser.parse_args()
    if args.pcie_ndmas < 0:
        parser.error("--pcie-ndmas must be >= 0")

    soc = BaseSoC(
        sys_clk_freq          = args.sys_clk_freq,
        with_ethernet         = args.with_ethernet,
        ethernet_port         = args.ethernet_port,
        eth_ip                = args.ethernet_ip,
        eth_dynamic_ip        = args.eth_dynamic_ip,
        remote_ip             = args.remote_ip,
        with_pcie             = args.with_pcie,
        pcie_lanes            = args.pcie_lanes,
        pcie_ndmas            = args.pcie_ndmas,
        pcie_address_width    = args.pcie_address_width,
        with_pcie_dma_status  = args.pcie_with_dma_status,
        with_pcie_dma_monitor = args.pcie_with_dma_monitor,
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
