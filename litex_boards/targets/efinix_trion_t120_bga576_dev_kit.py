#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Franck Jullien <franck.jullien@collshade.fr>
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

import argparse

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex_boards.platforms import efinix_trion_t120_bga576_dev_kit

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.interconnect import axi

from liteeth.phy.trionrgmii import LiteEthPHYRGMII

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.clock_domains.cd_sys = ClockDomain()

        # # #

        clk40 = platform.request("clk40")
        rst_n = platform.request("user_btn", 0)


        # PLL
        self.submodules.pll = pll = TRIONPLL(platform)
        self.comb += pll.reset.eq(~rst_n)
        pll.register_clkin(clk40, 40e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq, with_reset=True)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(50e6),
        with_spi_flash  = False,
        with_ethernet   = False,
        with_etherbone  = False,
        eth_phy         = 0,
        eth_ip          = "192.168.1.50",
        with_led_chaser = True,
        **kwargs):
        platform = efinix_trion_t120_bga576_dev_kit.Platform()

        # USBUART PMOD as Serial--------------------------------------------------------------------
        platform.add_extension(efinix_trion_t120_bga576_dev_kit.usb_pmod_io("pmod_e"))
        kwargs["uart_name"] = "usb_uart"

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident         = "LiteX SoC on Efinix Trion T120 BGA576 Dev Kit",
            ident_version = True,
            **kwargs
        )

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # SPI Flash --------------------------------------------------------------------------------
        if with_spi_flash:
            from litespi.modules import W25Q128JV
            from litespi.opcodes import SpiNorFlashOpCodes as Codes
            self.add_spi_flash(mode="4x", module=W25Q128JV(Codes.READ_1_1_4), with_master=True)
            platform.toolchain.excluded_ios.append(platform.lookup_request("spiflash4x").dq)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

        # Tristate Test ----------------------------------------------------------------------------
        from litex.build.generic_platform import Subsignal, Pins, Misc, IOStandard
        from litex.soc.cores.bitbang import I2CMaster
        platform.add_extension([("i2c", 0,
            Subsignal("sda",   Pins("T12")),
            Subsignal("scl",   Pins("V11")),
            IOStandard("3.3_V_LVTTL_/_LVCMOS"),
        )])
        self.submodules.i2c = I2CMaster(pads=platform.request("i2c"))

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            self.submodules.ethphy = LiteEthPHYRGMII(
                platform           = platform,
                clock_pads         = platform.request("eth_clocks", eth_phy),
                pads               = platform.request("eth", eth_phy),
                with_hw_init_reset = False)
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy, software_debug=True)
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy)

            # FIXME: Avoid this.
            platform.toolchain.excluded_ios.append(platform.lookup_request("eth_clocks").tx)
            platform.toolchain.excluded_ios.append(platform.lookup_request("eth_clocks").rx)
            platform.toolchain.excluded_ios.append(platform.lookup_request("eth").tx_data)
            platform.toolchain.excluded_ios.append(platform.lookup_request("eth").rx_data)
            platform.toolchain.excluded_ios.append(platform.lookup_request("eth").mdio)

        # LPDDR3 SDRAM -----------------------------------------------------------------------------
        if False:
            block = {"type" : "DRAM"}
            platform.toolchain.ifacewriter.xml_blocks.append(block)
            axi_port = axi.AXIInterface(data_width=256, address_width=32, id_width=8)
            ios = [("axi", 0,
                Subsignal("wdata",   Pins(256)),
                Subsignal("wready",  Pins(1)),
                Subsignal("wid",     Pins(8)),
                Subsignal("bready",  Pins(1)),
                Subsignal("rdata",   Pins(256)),
                Subsignal("aid",     Pins(8)),
                Subsignal("bvalid",  Pins(1)),
                Subsignal("rlast",   Pins(1)),
                Subsignal("bid",     Pins(8)),
                Subsignal("asize",   Pins(3)),
                Subsignal("atype",   Pins(1)),
                Subsignal("aburst",  Pins(2)),
                Subsignal("wvalid",  Pins(1)),
                Subsignal("aaddr",   Pins(32)),
                Subsignal("rid",     Pins(8)),
                Subsignal("avalid",  Pins(1)),
                Subsignal("rvalid",  Pins(1)),
                Subsignal("alock",   Pins(2)),
                Subsignal("rready",  Pins(1)),
                Subsignal("rresp",   Pins(2)),
                Subsignal("wstrb",   Pins(32)),
                Subsignal("aready",  Pins(1)),
                Subsignal("alen",    Pins(8)),
                Subsignal("wlast",   Pins(1)),
            )]
            io   = platform.add_iface_ios(ios)
            rw_n = Signal()
            self.comb += rw_n.eq(axi_port.ar.valid)
            self.comb += [
                # Pseudo AW/AR Channels.
                io.atype.eq(~rw_n),
                io.aaddr.eq(  Mux(rw_n,      axi_port.ar.addr,      axi_port.aw.addr)),
                io.aid.eq(    Mux(rw_n,        axi_port.ar.id,        axi_port.aw.id)),
                io.alen.eq(   Mux(rw_n,       axi_port.ar.len,       axi_port.aw.len)),
                io.asize.eq(  Mux(rw_n, axi_port.ar.size[0:4], axi_port.aw.size[0:4])), # CHECKME.
                io.aburst.eq( Mux(rw_n,     axi_port.ar.burst,     axi_port.aw.burst)),
                io.alock.eq(  Mux(rw_n,      axi_port.ar.lock,      axi_port.aw.lock)),
                io.avalid.eq( Mux(rw_n,     axi_port.ar.valid,     axi_port.aw.valid)),
                axi_port.aw.ready.eq(~rw_n & io.aready),
                axi_port.ar.ready.eq( rw_n & io.aready),

                # R Channel.
                axi_port.r.id.eq(io.rid),
                axi_port.r.data.eq(io.rdata),
                axi_port.r.last.eq(io.rlast),
                axi_port.r.resp.eq(io.rresp),
                axi_port.r.valid.eq(io.rvalid),
                io.rready.eq(axi_port.r.ready),

                # W Channel.
                io.wid.eq(axi_port.w.id),
                io.wstrb.eq(axi_port.w.strb),
                io.wdata.eq(axi_port.w.data),
                io.wlast.eq(axi_port.w.last),
                io.wvalid.eq(axi_port.w.valid),
                axi_port.w.ready.eq(io.wready),

                # B Channel.
                axi_port.b.id.eq(io.bid),
                axi_port.b.valid.eq(io.bvalid),
                io.bready.eq(axi_port.b.ready),
                # axi_port.b.resp ??
            ]

            # Connect AXI interface to the main bus of the SoC.
            axi_lite_port = axi.AXILiteInterface(data_width=256, address_width=32)
            self.submodules += axi.AXILite2AXI(axi_lite_port, axi_port)
            self.bus.add_slave("main_ram", axi_lite_port, SoCRegion(origin=0x4000_0000, size=0x1000_0000)) # 256MB.

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on Efinix Trion T120 BGA576 Dev Kit")
    parser.add_argument("--build",          action="store_true", help="Build bitstream")
    parser.add_argument("--load",           action="store_true", help="Load bitstream")
    parser.add_argument("--flash",          action="store_true", help="Flash bitstream")
    parser.add_argument("--sys-clk-freq",   default=50e6,        help="System clock frequency (default: 50MHz)")
    parser.add_argument("--with-spi-flash", action="store_true", help="Enable SPI Flash (MMAPed)")
    ethopts = parser.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",  action="store_true",              help="Enable Ethernet support")
    ethopts.add_argument("--with-etherbone", action="store_true",              help="Enable Etherbone support")
    parser.add_argument("--eth-ip",          default="192.168.1.50", type=str, help="Ethernet/Etherbone IP address")
    parser.add_argument("--eth-phy",         default=0, type=int,              help="Ethernet PHY: 0 (default) or 1")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq   = int(float(args.sys_clk_freq)),
        with_spi_flash = args.with_spi_flash,
        with_ethernet  = args.with_ethernet,
        with_etherbone = args.with_etherbone,
        eth_ip         = args.eth_ip,
        eth_phy        = args.eth_phy,
        **soc_core_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, f"outflow/{soc.build_name}.bit"))

    if args.flash:
        from litex.build.openfpgaloader import OpenFPGALoader
        prog = OpenFPGALoader("trion_t120_bga576")
        prog.flash(0, os.path.join(builder.gateware_dir, f"outflow/{soc.build_name}.hex"))

if __name__ == "__main__":
    main()
