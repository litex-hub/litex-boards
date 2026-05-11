#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020-2022 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# Build/Use:
# python3 -m litex_boards.targets.sqrl_fk33 --with-hbm --sys-clk-freq=250e6 --csr-csv=csr.csv --build --load
# litex_server --jtag --jtag-config=openocd_xc7_ft2232.cfg --jtag-chain=2
# litex_term crossover

import os

from migen import *

from litex.gen import *

from litex_boards.platforms import sqrl_fk33

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.interconnect.axi import *
from litex.soc.cores.ram.xilinx_usp_hbm2 import USPHBM2
from litex.soc.cores.led import LedChaser

from litepcie.phy.usppciephy import USPHBMPCIEPHY
from litepcie.software import generate_litepcie_software

# HBM ----------------------------------------------------------------------------------------------

HBM_NCHANNELS     = 32
HBM_CHANNEL_SIZE  = 0x1000_0000 # 256MB.
HBM_DEFAULT_BASE  = 0x4000_0000
HBM_HIGH_BASE     = 0x1_0000_0000

def parse_hbm_channels(channels):
    if isinstance(channels, str):
        channels = channels.strip().lower()
        if channels == "all":
            parsed_channels = list(range(HBM_NCHANNELS))
        else:
            parsed_channels = []
            for item in channels.split(","):
                item = item.strip()
                if not item:
                    raise ValueError("empty HBM channel entry")
                if "-" in item:
                    start, end = [int(v, 0) for v in item.split("-", 1)]
                    if end < start:
                        raise ValueError("HBM channel ranges must be increasing")
                    parsed_channels.extend(range(start, end + 1))
                else:
                    parsed_channels.append(int(item, 0))
    else:
        parsed_channels = list(channels)

    if not parsed_channels:
        raise ValueError("at least one HBM channel must be selected")
    if len(parsed_channels) != len(set(parsed_channels)):
        raise ValueError("HBM channels must be unique")
    for channel in parsed_channels:
        if not 0 <= channel < HBM_NCHANNELS:
            raise ValueError(f"HBM channel {channel} outside 0-{HBM_NCHANNELS - 1}")
    return tuple(parsed_channels)

def hbm_channel_origin(channel, hbm_base=HBM_DEFAULT_BASE, hbm_high_base=HBM_HIGH_BASE):
    origin = hbm_base + HBM_CHANNEL_SIZE*channel
    if hbm_base == HBM_DEFAULT_BASE and origin >= 0x8000_0000:
        origin = hbm_high_base + HBM_CHANNEL_SIZE*(channel - 4)
    return origin

class AXILiteAddressRemapper(LiteXModule):
    def __init__(self, master, slave, origin=0):
        self.comb += [
            slave.aw.valid.eq(master.aw.valid),
            master.aw.ready.eq(slave.aw.ready),
            slave.aw.first.eq(master.aw.first),
            slave.aw.last.eq(master.aw.last),
            slave.aw.addr.eq(master.aw.addr - origin),
            slave.aw.prot.eq(master.aw.prot),

            slave.w.valid.eq(master.w.valid),
            master.w.ready.eq(slave.w.ready),
            slave.w.first.eq(master.w.first),
            slave.w.last.eq(master.w.last),
            slave.w.data.eq(master.w.data),
            slave.w.strb.eq(master.w.strb),

            master.b.valid.eq(slave.b.valid),
            slave.b.ready.eq(master.b.ready),
            master.b.first.eq(slave.b.first),
            master.b.last.eq(slave.b.last),
            master.b.resp.eq(slave.b.resp),

            slave.ar.valid.eq(master.ar.valid),
            master.ar.ready.eq(slave.ar.ready),
            slave.ar.first.eq(master.ar.first),
            slave.ar.last.eq(master.ar.last),
            slave.ar.addr.eq(master.ar.addr - origin),
            slave.ar.prot.eq(master.ar.prot),

            master.r.valid.eq(slave.r.valid),
            slave.r.ready.eq(master.r.ready),
            master.r.first.eq(slave.r.first),
            master.r.last.eq(slave.r.last),
            master.r.data.eq(slave.r.data),
            master.r.resp.eq(slave.r.resp),
        ]

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_hbm):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()
        if with_hbm:
            self.cd_hbm_ref = ClockDomain()
            self.cd_apb     = ClockDomain()

        # # #

        self.pll = pll = USPMMCM(speedgrade=-2)
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(platform.request("clk200"), 200e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        if with_hbm:
            pll.create_clkout(self.cd_hbm_ref, 100e6)
            pll.create_clkout(self.cd_apb,     100e6)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=125e6,
        with_led_chaser = True,
        with_pcie       = False,
        pcie_lanes      = 4,
        pcie_ndmas      = 1,
        pcie_address_width = 32,
        with_pcie_dma_status  = False,
        with_pcie_dma_monitor = False,
        with_hbm        = False,
        hbm_channels    = (0, 1, 2, 3),
        hbm_main_channel= 0,
        hbm_base        = HBM_DEFAULT_BASE,
        hbm_high_base   = HBM_HIGH_BASE,
        hbm_strip_origin= False,
        **kwargs):
        platform = sqrl_fk33.Platform()
        if with_hbm:
            assert 225e6 <= sys_clk_freq <= 450e6
            hbm_channels = parse_hbm_channels(hbm_channels)
            if hbm_main_channel not in hbm_channels:
                raise ValueError("HBM main channel must be one of the mapped HBM channels")
            hbm_origins = {
                channel: hbm_channel_origin(channel, hbm_base, hbm_high_base)
                for channel in hbm_channels
            }
            hbm_window_end = max(origin + HBM_CHANNEL_SIZE for origin in hbm_origins.values())
            if hbm_window_end > 2**kwargs.get("bus_address_width", 32):
                kwargs["bus_address_width"] = 64
            if hbm_window_end > 2**pcie_address_width:
                pcie_address_width = 64
            if hbm_window_end > 2**33:
                hbm_strip_origin = True

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, with_hbm)

        # SoCCore ----------------------------------------------------------------------------------
        if kwargs.get("uart_name", "serial") == "serial":
            if kwargs.get("uart_name", "serial") == "serial": kwargs["uart_name"] = "crossover" # Defaults to Crossover-UART.
        kwargs["with_jtagbone"]  = True
        kwargs["jtagbone_chain"] = 2 # Chain 1 already used by HBM2 debug probes.
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on FK33", **kwargs)

        # HBM --------------------------------------------------------------------------------------
        if with_hbm:
            # Add HBM Core.
            self.hbm = hbm = ClockDomainsRenamer({"axi": "sys"})(USPHBM2(platform))

            # Get HBM .xci.
            hbm_xci = os.path.join("ip", "hbm", "hbm_0.xci")
            if not os.path.exists(hbm_xci):
                os.makedirs(os.path.dirname(hbm_xci), exist_ok=True)
                os.system(f"wget -O {hbm_xci} https://github.com/litex-hub/litex-boards/files/8178874/hbm_0.xci.txt")

            # Connect selected HBM AXI interfaces to the main bus of the SoC.
            hbm_regions = {}
            for channel in hbm_channels:
                axi_hbm      = hbm.axi[channel]
                axi_lite_bus = AXILiteInterface(data_width=256, address_width=self.bus.address_width)
                axi_lite_hbm = AXILiteInterface(data_width=256, address_width=33)
                origin       = hbm_origins[channel]
                self.submodules += AXILiteAddressRemapper(
                    master = axi_lite_bus,
                    slave  = axi_lite_hbm,
                    origin = origin if hbm_strip_origin else 0)
                self.submodules += AXILite2AXI(axi_lite_hbm, axi_hbm)
                hbm_regions[channel] = origin
                self.bus.add_slave(
                    f"hbm{channel}",
                    axi_lite_bus,
                    SoCRegion(
                        origin = origin,
                        size   = HBM_CHANNEL_SIZE,
                        cached = not (0x8000_0000 <= origin < 0x1_0000_0000)))
            self.add_constant("HBM_CHANNELS", len(hbm_channels))
            self.add_constant("HBM_MAIN_CHANNEL", hbm_main_channel)
            self.add_constant("HBM_HIGH_BASE", hbm_high_base)
            # Link selected HBM2 channel as main RAM.
            self.bus.add_region("main_ram", SoCRegion(
                origin = hbm_regions[hbm_main_channel],
                size   = HBM_CHANNEL_SIZE,
                linker = True))

        # PCIe -------------------------------------------------------------------------------------
        if with_pcie:
            assert self.csr_data_width == 32
            self.pcie_phy = USPHBMPCIEPHY(platform, platform.request(f"pcie_x{pcie_lanes}"),
                data_width = {4: 128, 8: 256, 16: 512}[pcie_lanes],
                bar0_size  = 0x20000)
            self.add_pcie(
                phy              = self.pcie_phy,
                ndmas            = pcie_ndmas,
                address_width    = pcie_address_width,
                with_dma_status  = with_pcie_dma_status,
                with_dma_monitor = with_pcie_dma_monitor)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=sqrl_fk33.Platform, description="LiteX SoC on FK33.")
    parser.add_target_argument("--sys-clk-freq", default=125e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-pcie",    action="store_true",       help="Enable PCIe support.")
    parser.add_target_argument("--pcie-lanes",   default=4, type=int,       choices=[4, 8, 16], help="PCIe lane count.")
    parser.add_target_argument("--pcie-ndmas",   default=1, type=int,       help="Number of PCIe DMA channels.")
    parser.add_target_argument("--pcie-address-width", default=32, type=int, choices=[32, 64], help="PCIe address width.")
    parser.add_target_argument("--pcie-with-dma-status",  action="store_true", help="Enable PCIe DMA status CSRs.")
    parser.add_target_argument("--pcie-with-dma-monitor", action="store_true", help="Enable PCIe DMA monitor CSRs.")
    parser.add_target_argument("--with-hbm",     action="store_true",       help="Use HBM2.")
    parser.add_target_argument("--hbm-channels", default="0,1,2,3",         help="HBM channels to map (comma/range list or all).")
    parser.add_target_argument("--hbm-main-channel", default=0, type=int,   help="Mapped HBM channel used as main RAM.")
    parser.add_target_argument("--hbm-base",     default=HBM_DEFAULT_BASE, type=lambda x: int(x, 0), help="HBM bus base address.")
    parser.add_target_argument("--hbm-high-base", default=HBM_HIGH_BASE, type=lambda x: int(x, 0), help="HBM bus base for channels above the low 32-bit cached window.")
    parser.add_target_argument("--hbm-strip-origin", action="store_true",   help="Expose each mapped HBM channel with local AXI addresses.")
    parser.add_target_argument("--driver",       action="store_true",       help="Generate PCIe driver.")
    args = parser.parse_args()
    if args.pcie_ndmas < 0:
        parser.error("--pcie-ndmas must be >= 0")
    try:
        hbm_channels = parse_hbm_channels(args.hbm_channels)
    except ValueError as e:
        parser.error(str(e))

    soc = BaseSoC(
        sys_clk_freq          = args.sys_clk_freq,
        with_pcie             = args.with_pcie,
        pcie_lanes            = args.pcie_lanes,
        pcie_ndmas            = args.pcie_ndmas,
        pcie_address_width    = args.pcie_address_width,
        with_pcie_dma_status  = args.pcie_with_dma_status,
        with_pcie_dma_monitor = args.pcie_with_dma_monitor,
        with_hbm              = args.with_hbm,
        hbm_channels          = hbm_channels,
        hbm_main_channel      = args.hbm_main_channel,
        hbm_base              = args.hbm_base,
        hbm_high_base         = args.hbm_high_base,
        hbm_strip_origin      = args.hbm_strip_origin,
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
