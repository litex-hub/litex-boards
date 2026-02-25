#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Franck Jullien <franck.jullien@collshade.fr>
# SPDX-License-Identifier: BSD-2-Clause

from math import log2
from textwrap import dedent
from typing import Counter, List, Mapping
import xml.etree.ElementTree as et

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex_boards.platforms import efinix_titanium_ti180_m484_dev_kit

from litex.build.generic_platform import *

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.interconnect import axi
from litex.soc.interconnect import wishbone

from litex.soc.cores.hyperbus import HyperRAM
from liteeth.phy.trionrgmii import LiteEthPHYRGMII

from litex.build.efinix import InterfaceWriterBlock, InterfaceWriterXMLBlock

from litex.soc.integration.soc import SoCBusHandler


# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.clock_domains.cd_sys = ClockDomain()

        # # #

        clk50 = platform.request("clk50")
        rst_n = platform.request("user_btn", 0)

        # PLL
        self.submodules.pll = pll = TITANIUMPLL(platform)
        # self.comb += pll.reset.eq(~rst_n)
        pll.register_clkin(clk50, 50e6)
        # You can use CLKOUT0 only for clocks with a maximum frequency of 4x
        # (integer) of the reference clock. If all your system clocks do not fall within
        # this range, you should dedicate one unused clock for CLKOUT0.
        pll.create_clkout(None, 50e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq, with_reset=False, name="axi_clk")

        # Do reset here so we can also wait for DDR other than PLL locked
        dram_pll_locked = platform.add_iface_io("dram_pll_locked")
        dram_pll_rstn = platform.add_iface_io("dram_pll_rstn")

        cfg_done = platform.add_iface_io("cfg_done")
        cfg_reset = platform.add_iface_io("cfg_reset")
        cfg_sel = platform.add_iface_io("cfg_sel")
        cfg_start = platform.add_iface_io("cfg_start")

        axi_rstn = platform.add_iface_io("axi_rstn")

        cfg_ok = Signal()
        counter = Signal(8, reset_less=True)

        # Use a separate clock domain since we are generating the sys_rst here; Also we can choose to use reset-less here
        cd_por = ClockDomain() 
        self.clock_domains += cd_por
        # fsm = ResetInserter()(fsm)
        fsm = ClockDomainsRenamer("por")(FSM(reset_state="IDLE"))
        fsm.act("IDLE", If(counter == 255, NextState("START")))
        fsm.act("START", If(cfg_done, NextState("DONE")))
        # Use rst_n from push botton (async) as a sync reset for this domain; Not the best practice, but works fine
        self.comb += cd_por.clk.eq(ClockSignal())
        self.comb += cd_por.rst.eq(~rst_n) 
        self.submodules += fsm

        self.sync += If(fsm.ongoing("IDLE"), counter.eq(counter + 1)).Else(counter.eq(0))

        self.comb += [
            pll.reset.eq(0),
            # dram_pll_rstn.eq(rst_n),
            dram_pll_rstn.eq(1),
            cfg_sel.eq(0),
            cfg_reset.eq(fsm.ongoing("IDLE")),
            cfg_start.eq(~fsm.ongoing("IDLE")),
            cfg_ok.eq(fsm.ongoing("DONE")),
            axi_rstn.eq(cfg_ok),
        ]
        self.specials += AsyncResetSynchronizer(self.cd_sys, ~(rst_n & pll.locked & dram_pll_locked & cfg_ok))

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(200e6),
        with_spi_flash = False,
        with_ethernet  = False,
        with_etherbone = False,
        eth_phy        = 0,
        eth_ip         = "192.168.1.50",
        # with_debug     = True, 
        **kwargs):
        platform = efinix_titanium_ti180_m484_dev_kit.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)


        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Efinix Titanium Ti180 M484 Dev Kit", **kwargs)

        # SPI Flash --------------------------------------------------------------------------------
        if with_spi_flash:
            # from litespi.modules import W25Q64JW
            from litespi.modules import MX25U25635F # actual model is MX25U25645GZ4I00 on Ti180; this seems to work ok
            from litespi.opcodes import SpiNorFlashOpCodes as Codes
            # self.add_spi_flash(mode="1x", module=W25Q64JW(Codes.READ_1_1_1), with_master=True)
            self.add_spi_flash(mode="1x", module=MX25U25635F(Codes.READ_1_1_1), with_master=True)

        # HyperRAM ---------------------------------------------------------------------------------
        # if with_hyperram:
        #     self.submodules.hyperram = HyperRAM(platform.request("hyperram"), latency=7)
        #     self.bus.add_slave("main_ram", slave=self.hyperram.bus, region=SoCRegion(origin=0x80000000, size=32*1024*1024))

        # LPDDR4 SDRAM -----------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            # DRAM / PLL Blocks.
            # ------------------
            dram_pll_refclk = platform.request("clk33")
            platform.toolchain.excluded_ios.append(dram_pll_refclk)
            self.platform.toolchain.additional_sdc_commands.append(f"create_clock -period {1e9/33.33e6} clk33")
            platform.toolchain.ifacewriter.blocks.append(PLLDRAMBlock())
            platform.toolchain.ifacewriter.xml_blocks.append(DRAMXMLBlock())

            # DRAM Rst.
            # ---------
            # dram_pll_rst_n = platform.add_iface_io("dram_pll_rst_n")
            # self.comb += dram_pll_rst_n.eq(platform.request("user_btn", 1))

            self.add_sdram(platform, l2_cache_size=0)

        # Ethernet / Etherbone ---------------------------------------------------------------------
        # if with_ethernet or with_etherbone:
        #     platform.add_extension(efinix_titanium_ti60_f225_dev_kit.rgmii_ethernet_qse_ios("P1"))
        #     pads = platform.request("eth", eth_phy)
        #     self.submodules.ethphy = LiteEthPHYRGMII(
        #         platform           = platform,
        #         clock_pads         = platform.request("eth_clocks", eth_phy),
        #         pads               = pads,
        #         with_hw_init_reset = False)
        #     if with_ethernet:
        #         self.add_ethernet(phy=self.ethphy, software_debug=True)
        #     if with_etherbone:
        #         self.add_etherbone(phy=self.ethphy)

        #     # FIXME: Avoid this.
        #     platform.toolchain.excluded_ios.append(platform.lookup_request("eth_clocks").tx)
        #     platform.toolchain.excluded_ios.append(platform.lookup_request("eth_clocks").rx)
        #     platform.toolchain.excluded_ios.append(platform.lookup_request("eth").tx_data)
        #     platform.toolchain.excluded_ios.append(platform.lookup_request("eth").tx_ctl)
        #     platform.toolchain.excluded_ios.append(platform.lookup_request("eth").rx_data)
        #     platform.toolchain.excluded_ios.append(platform.lookup_request("eth").mdio)

        #     # Extension board on P2 + External Logic Analyzer.
        #     _pmod_ios = [
        #         ("debug", 0, Pins(
        #             "L11", # GPIOR_P_15
        #             "K11", # GPIOR_N_15
        #             "N10", # GPIOR_P_12
        #             "M10", # GPIOR_N_12
        #             ),
        #             IOStandard("1.8_V_LVCMOS")
        #         ),
        #     ]
        #     platform.add_extension(_pmod_ios)
        #     debug = platform.request("debug")
        #     self.comb += debug[0].eq(self.ethphy.tx.sink.valid)
        #     self.comb += debug[1].eq(self.ethphy.tx.sink.data[0])
        #     self.comb += debug[2].eq(self.ethphy.tx.sink.data[1])
    
    def add_sdram(self, platform, name="sdram", origin=None, 
        # with_bist=False, 
        with_soc_interconnect = True,
        l2_cache_size           = 8192,
        l2_cache_min_data_width = 128,
        l2_cache_reverse        = False,
        l2_cache_full_memory_we = True):
        from litedram.frontend.bist import  LiteDRAMBISTGenerator, LiteDRAMBISTChecker

        sdram_size = 1024 * 1024 * 1024
        ddr_axi_data_width = 512

        self.check_if_exists(name)
        # sdram = LiteDRAMCore()
        # setattr(self.submodules, name, sdram)

        # LiteDRAM BIST.
        # if with_bist:
        #     sdram_generator = LiteDRAMBISTGenerator(sdram.crossbar.get_port())
        #     sdram_checker   = LiteDRAMBISTChecker(  sdram.crossbar.get_port())
        #     setattr(self.submodules, f"{name}_generator", sdram_generator)
        #     setattr(self.submodules, f"{name}_checker",   sdram_checker)

        if not with_soc_interconnect: return

        # Add SDRAM region.
        main_ram_region = SoCRegion(
            origin = self.mem_map.get("main_ram", origin),
            size   = sdram_size,
            mode   = "rwx")
        self.bus.add_region("main_ram", main_ram_region)

        # Add CPU's direct memory buses (if not already declared) ----------------------------------
        if hasattr(self.cpu, "add_memory_buses"):
            self.cpu.add_memory_buses(
                address_width = 32,
                data_width    = ddr_axi_data_width # sdram.crossbar.controller.data_width
            )

        # In place of sdram.crossbar.get_port()
        xbar_masters = []
        # xbar = SoCBusHandler(standard="axi", data_width=ddr_axi_data_width, address_width=33)
        # self.submodules += xbar

        # Connect CPU's direct memory buses to LiteDRAM --------------------------------------------
        if len(self.cpu.memory_buses):
            # When CPU has at least a direct memory bus, connect them directly to LiteDRAM.
            for mem_bus in self.cpu.memory_buses:
                # Request a LiteDRAM native port.
                # port = sdram.crossbar.get_port()
                # port.data_width = 2**int(log2(port.data_width)) # Round to nearest power of 2.

                # Check if bus is an AXI bus and connect it.
                if isinstance(mem_bus, axi.AXIInterface):
                    # data_width_ratio = int(port.data_width/mem_bus.data_width)
                    data_width_ratio = int(ddr_axi_data_width / mem_bus.data_width)
                    # If same data_width, connect it directly.
                    if data_width_ratio == 1:
                        # self.submodules += LiteDRAMAXI2Native(
                        #     axi          = mem_bus,
                        #     port         = port,
                        #     base_address = self.bus.regions["main_ram"].origin
                        # )
                        xbar_masters += [mem_bus]
                        # xbar.add_master(master=mem_bus)
                    # UpConvert.
                    # elif data_width_ratio > 1:
                    else:
                        axi_port = axi.AXIInterface(
                            # data_width = port.data_width,
                            data_width = ddr_axi_data_width,
                            id_width   = len(mem_bus.aw.id),
                        )
                        # self.submodules += axi.AXIUpConverter(
                        #     axi_from = mem_bus,
                        #     axi_to   = axi_port,
                        # )
                        self.submodules += axi.AXIConverter(mem_bus, axi_port)
                        # self.submodules += LiteDRAMAXI2Native(
                        #     axi          = axi_port,
                        #     port         = port,
                        #     base_address = self.bus.regions["main_ram"].origin
                        # )
                        xbar_masters += [axi_port]
                        # xbar.add_master(master=axi_port)
                    # DownConvert. FIXME: Pass through Wishbone for now, create/use native AXI converter.
                    # else:
                        # mem_wb  = wishbone.Interface(
                        #     data_width = self.cpu.mem_axi.data_width,
                        #     adr_width  = 32-log2_int(mem_bus.data_width//8))
                        # mem_a2w = axi.AXI2Wishbone(
                        #     axi          = mem_bus,
                        #     wishbone     = mem_wb,
                        #     base_address = 0)
                        # self.submodules += mem_a2w
                        # litedram_wb = wishbone.Interface(port.data_width)
                        # self.submodules += LiteDRAMWishbone2Native(
                        #     wishbone     = litedram_wb,
                        #     port         = port,
                        #     base_address = self.bus.regions["main_ram"].origin)
                        # self.submodules += wishbone.Converter(mem_wb, litedram_wb)

        # Connect Main bus to LiteDRAM (with optional L2 Cache) ------------------------------------
        connect_main_bus_to_dram = (
            # No memory buses.
            (not len(self.cpu.memory_buses)) or
            # Memory buses but no DMA bus.
            (len(self.cpu.memory_buses) and not hasattr(self.cpu, "dma_bus"))
        )
        print(f'connect_main_bus_to_dram is {connect_main_bus_to_dram}')
        if connect_main_bus_to_dram:
            # Request a LiteDRAM native port.
            # port = sdram.crossbar.get_port()
            # port.data_width = 2**int(log2(port.data_width)) # Round to nearest power of 2.

            # Create Wishbone Slave.
            wb_sdram = wishbone.Interface(32, adr_width=30)
            self.bus.add_slave("main_ram", wb_sdram)
            print(f'wb_sdram.data_width={wb_sdram.data_width}')
            print(f'wb_sdram.adr_width={wb_sdram.adr_width}')

            # L2 Cache
            if l2_cache_size != 0:
                # Insert L2 cache inbetween Wishbone bus and LiteDRAM
                # l2_cache_size = max(l2_cache_size, int(2*port.data_width/8)) # Use minimal size if lower
                l2_cache_size = max(l2_cache_size, int(2 * ddr_axi_data_width / 8)) # Use minimal size if lower
                l2_cache_size = 2 ** int(log2(l2_cache_size))                  # Round to nearest power of 2
                # l2_cache_data_width = max(port.data_width, l2_cache_min_data_width)
                l2_cache_data_width = max(ddr_axi_data_width, l2_cache_min_data_width)
                l2_cache = wishbone.Cache(
                    cachesize = l2_cache_size//4,
                    master    = wb_sdram,
                    slave     = wishbone.Interface(l2_cache_data_width, adr_width=26),
                    reverse   = l2_cache_reverse)
                if l2_cache_full_memory_we:
                    l2_cache = FullMemoryWE()(l2_cache)
                self.submodules.l2_cache = l2_cache
                litedram_wb = self.l2_cache.slave
                self.add_config("L2_SIZE", l2_cache_size)
            else:
                # litedram_wb = wishbone.Interface(port.data_width)
                litedram_wb = wishbone.Interface(ddr_axi_data_width, adr_width=26)
                self.submodules += wishbone.Converter(wb_sdram, litedram_wb)

            # Wishbone Slave <--> LiteDRAM bridge.
            # self.submodules.wishbone_bridge = LiteDRAMWishbone2Native(
            #     wishbone     = litedram_wb,
            #     port         = port,
            #     base_address = self.bus.regions["main_ram"].origin
            # )
            axi_port = axi.AXIInterface(data_width = ddr_axi_data_width, address_width=32)
            self.submodules += axi.Wishbone2AXI(litedram_wb, axi_port, base_address=self.bus.regions['main_ram'].origin)
            xbar_masters += [axi_port]
            # xbar.add_master(axi_port)

        xbar_slaves = self.add_sdram_io(platform)
        if len(xbar_slaves) == 1 and len(xbar_masters) == 1:
            self.submodules += axi.AXIInterconnectPointToPoint(xbar_masters[0], xbar_slaves['main_ram'])
        else:
            f = self.bus.regions['main_ram'].decoder(self.bus)
            import inspect
            print(f'self.bus.regions[n].decoder(self.bus) is {inspect.getsource(f)}')
            self.submodules += axi.AXICrossbar(xbar_masters, [(self.bus.regions[n].decoder(self.bus), s) for n, s in xbar_slaves.items()])
            # self.submodules += axi.AXIInterconnectShared(xbar_masters, [(self.bus.regions[n].decoder(self.bus), s) for n, s in xbar_slaves.items()])


    def add_sdram_io(self, platform) -> Mapping[str, axi.AXIInterface]:
        # platform = efinix_titanium_ti180_m484_dev_kit.Platform()
        # DRAM AXI-Ports.
        # --------------
        # target0: 512-bit. # target1: 512-bit
        # targets = { 0: 512, 1: 512 }.items()
        targets = [(0, 512)]
        ports = {}
        for n, data_width in targets:
            axi_port = axi.AXIInterface(data_width=data_width, address_width=32, id_width=6) # 1GB.
            ports['main_ram'] = axi_port
            # xbar.add_slave(slave=axi_port)
            ios = [(f"axi{n}", 0,
                Subsignal("araddr",  Pins(33)),
                Subsignal("arburst", Pins(2)),
                Subsignal("arid",    Pins(6)),
                Subsignal("arlen",   Pins(8)),
                Subsignal("arlock",  Pins(1)),
                Subsignal("arsize",  Pins(3)),
                Subsignal("arqos",   Pins(1)),
                Subsignal("arapcmd", Pins(1)),
                Subsignal("arvalid", Pins(1)),
                Subsignal("arready", Pins(1)),

                Subsignal("awaddr",    Pins(33)),
                Subsignal("awburst",   Pins(2)),
                Subsignal("awcache",   Pins(4)),
                Subsignal("awid",      Pins(6)),
                Subsignal("awlen",     Pins(8)),
                Subsignal("awlock",    Pins(1)),
                Subsignal("awsize",    Pins(3)),
                Subsignal("awqos",     Pins(1)),
                Subsignal("awallstrb", Pins(1)),
                Subsignal("awapcmd",   Pins(1)),
                Subsignal("awcobuf",   Pins(1)),
                Subsignal("awvalid",   Pins(1)),
                Subsignal("awready",   Pins(1)),

                Subsignal("rdata",   Pins(data_width)),
                Subsignal("rid",     Pins(6)),
                Subsignal("rlast",   Pins(1)),
                Subsignal("rresp",   Pins(2)),
                Subsignal("rvalid",  Pins(1)),
                Subsignal("rready",  Pins(1)),

                Subsignal("wdata",   Pins(data_width)),
                Subsignal("wid",     Pins(6)),
                Subsignal("wlast",   Pins(1)),
                Subsignal("wstrb",   Pins(data_width//8)),
                Subsignal("wvalid",  Pins(1)),
                Subsignal("wready",  Pins(1)),

                Subsignal("bid",     Pins(6)),
                Subsignal("bresp",   Pins(2)),
                Subsignal("bready",  Pins(1)),
                Subsignal("bvalid",  Pins(1)),
            )]
            io = platform.add_iface_ios(ios)

            self.comb += [
                # AR Channels
                io.araddr.eq(axi_port.ar.addr),
                io.arburst.eq(axi_port.ar.burst),
                io.arid.eq(axi_port.ar.id),
                io.arlen.eq(axi_port.ar.len),
                io.arlock.eq(axi_port.ar.lock),
                io.arsize.eq(axi_port.ar.size),
                io.arqos.eq(axi_port.ar.qos),
                io.arapcmd.eq(0),
                io.arvalid.eq(axi_port.ar.valid),
                axi_port.ar.ready.eq(io.arready),

                # AW Channels
                io.awaddr.eq(axi_port.aw.addr),
                io.awburst.eq(axi_port.aw.burst),
                io.awcache.eq(axi_port.aw.cache),
                io.awid.eq(axi_port.aw.id),
                io.awlen.eq(axi_port.aw.len),
                io.awlock.eq(axi_port.aw.lock),
                io.awsize.eq(axi_port.aw.size),
                io.awqos.eq(axi_port.aw.qos),
                io.awallstrb.eq(0),
                io.awapcmd.eq(0),
                io.awcobuf.eq(1),
                io.awvalid.eq(axi_port.aw.valid),
                axi_port.aw.ready.eq(io.awready),

                # R Channel.
                axi_port.r.data.eq(io.rdata),
                axi_port.r.id.eq(io.rid),
                axi_port.r.last.eq(io.rlast),
                axi_port.r.resp.eq(io.rresp),
                axi_port.r.valid.eq(io.rvalid),
                io.rready.eq(axi_port.r.ready),

                # W Channel.
                io.wdata.eq(axi_port.w.data),
                io.wid.eq(axi_port.w.id),
                io.wlast.eq(axi_port.w.last),
                io.wstrb.eq(axi_port.w.strb),
                io.wvalid.eq(axi_port.w.valid),
                axi_port.w.ready.eq(io.wready),

                # B Channel.
                axi_port.b.id.eq(io.bid),
                axi_port.b.resp.eq(io.bresp),
                axi_port.b.valid.eq(io.bvalid),
                io.bready.eq(axi_port.b.ready),
            ]

        return ports

        #     # Connect AXI interface to the main bus of the SoC.
        #     axi_lite_port = axi.AXILiteInterface(data_width=data_width, address_width=30)
        #     self.submodules += axi.AXILite2AXI(axi_lite_port, axi_port)
        #     self.bus.add_slave(f"target{n}", axi_lite_port, SoCRegion(origin=0x4000_0000 + 0x4000_0000*n, size=0x4000_0000)) # 1GB.

        # # Use DRAM's target0 port as Main Ram  -----------------------------------------------------
        # self.bus.add_region("main_ram", SoCRegion( origin = 0x4000_0000, size   = 0x4000_0000, linker = True)) # 1GB.

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on Efinix Titanium Ti60 F225 Dev Kit")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",          action="store_true", help="Build design.")
    target_group.add_argument("--load",           action="store_true", help="Load bitstream.")
    target_group.add_argument("--flash",          action="store_true", help="Flash bitstream.")
    target_group.add_argument("--sys-clk-freq",   default=200e6,       help="System clock frequency.")
    target_group.add_argument("--with-spi-flash", action="store_true", help="Enable SPI Flash (MMAPed).")
    # target_group.add_argument("--with-hyperram",  action="store_true", help="Enable HyperRAM.")
    sdopts = target_group.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-sdcard",      action="store_true", help="Enable SPI-mode SDCard support.")
    sdopts.add_argument("--with-sdcard",          action="store_true", help="Enable SDCard support.")
    ethopts = target_group.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",        action="store_true",              help="Enable Ethernet support.")
    ethopts.add_argument("--with-etherbone",       action="store_true",              help="Enable Etherbone support.")
    target_group.add_argument("--eth-ip",          default="192.168.1.50", type=str, help="Ethernet/Etherbone IP address.")
    target_group.add_argument("--eth-phy",         default=0, type=int,              help="Ethernet PHY: 0 (default) or 1.")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq   = int(float(args.sys_clk_freq)),
        with_spi_flash = args.with_spi_flash,
        # with_hyperram  = args.with_hyperram,
        with_ethernet  = args.with_ethernet,
        with_etherbone = args.with_etherbone,
        eth_ip         = args.eth_ip,
        eth_phy        = args.eth_phy,
         **soc_core_argdict(args))
    if args.with_spi_sdcard:
        soc.add_spi_sdcard()
    if args.with_sdcard:
        soc.add_sdcard()
    builder = Builder(soc, **builder_argdict(args))
    if args.build:
        builder.build()

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        from litex.build.openfpgaloader import OpenFPGALoader
        prog = OpenFPGALoader("titanium_ti180_m484")
        prog.flash(0, builder.get_bitstream_filename(mode="flash", ext=".hex")) # FIXME

# PLLDRAMBlock ----------------------------------------------------------------------------------------------

class PLLDRAMBlock(InterfaceWriterBlock):
    @staticmethod
    def generate():
        return dedent("""\
        design.create_block("dram_pll", block_type="PLL")
        design.set_property("dram_pll", {"REFCLK_FREQ": "33.33"}, block_type="PLL")
        design.gen_pll_ref_clock("dram_pll", pll_res="PLL_TL2", refclk_src="EXTERNAL", refclk_name="dram_pll_clkin", ext_refclk_no="1")
        design.set_property("dram_pll", "LOCKED_PIN", "dram_pll_locked", block_type="PLL")
        design.set_property("dram_pll", "RSTN_PIN", "dram_pll_rstn", block_type="PLL")
        design.set_property("dram_pll", "CLKOUT3_EN", "1", block_type="PLL")
        design.set_property("dram_pll", "CLKOUT4_EN", "1", block_type="PLL")
        design.set_property("dram_pll", "CLKOUT0_PIN", "dram_pll_CLKOUT0", block_type="PLL")
        design.set_property("dram_pll", "CLKOUT3_PIN", "dram_pll_CLKOUT3", block_type="PLL")
        design.set_property("dram_pll", "CLKOUT4_PIN", "dram_pll_CLKOUT4", block_type="PLL")
        calc_result = design.auto_calc_pll_clock("dram_pll", {"CLKOUT0_FREQ": "33.33", "CLKOUT3_FREQ": "1066.66", "CLKOUT4_FREQ": "533.33"})
        """)


class DRAMXMLBlock(InterfaceWriterXMLBlock):
    @staticmethod
    def generate(root, namespaces):
        # CHECKME: Switch to DDRDesignService?
        ddr_info = root.find("efxpt:ddr_info", namespaces)

        ddr = et.SubElement(ddr_info, "efxpt:adv_ddr",
            name            = "ddr_inst1",
            ddr_def         = "DDR_0",
            clkin_sel       = "2",
            data_width      = "32",
            physical_rank   = "1",
            mem_type        = "LPDDR4x",
            mem_density     = "8G",
        )

        axi_target0 = et.SubElement(ddr, "efxpt:axi_target0", is_axi_width_256="false", is_axi_enable="true")
        gen_pin_target0 = et.SubElement(axi_target0, "efxpt:gen_pin_axi")
        et.SubElement(gen_pin_target0, "efxpt:pin", name="axi_clk",        type_name=f"ACLK_0",       is_bus="false", is_clk="true", is_clk_invert="false")
        et.SubElement(gen_pin_target0, "efxpt:pin", name="axi_rstn",       type_name=f"ARST_0",       is_bus="false")

        et.SubElement(gen_pin_target0, "efxpt:pin", name="axi0_araddr",    type_name=f"ARADDR_0",     is_bus="true")
        et.SubElement(gen_pin_target0, "efxpt:pin", name="axi0_arburst",   type_name=f"ARBURST_0",    is_bus="true")
        et.SubElement(gen_pin_target0, "efxpt:pin", name="axi0_arid",      type_name=f"ARID_0",       is_bus="true")
        et.SubElement(gen_pin_target0, "efxpt:pin", name="axi0_arlen",     type_name=f"ARLEN_0",      is_bus="true")
        et.SubElement(gen_pin_target0, "efxpt:pin", name="axi0_arlock",    type_name=f"ARLOCK_0",     is_bus="false")
        et.SubElement(gen_pin_target0, "efxpt:pin", name="axi0_arqos",     type_name=f"ARQOS_0",      is_bus="false")
        et.SubElement(gen_pin_target0, "efxpt:pin", name="axi0_arsize",    type_name=f"ARSIZE_0",     is_bus="true")
        et.SubElement(gen_pin_target0, "efxpt:pin", name="axi0_arapcmd",   type_name=f"ARAPCMD_0",    is_bus="false")
        et.SubElement(gen_pin_target0, "efxpt:pin", name="axi0_arvalid",   type_name=f"ARVALID_0",    is_bus="false")
        et.SubElement(gen_pin_target0, "efxpt:pin", name="axi0_arready",   type_name=f"ARREADY_0",    is_bus="false")

        et.SubElement(gen_pin_target0, "efxpt:pin", name="axi0_awaddr",    type_name=f"AWADDR_0",     is_bus="true")
        et.SubElement(gen_pin_target0, "efxpt:pin", name="axi0_awburst",   type_name=f"AWBURST_0",    is_bus="true")
        et.SubElement(gen_pin_target0, "efxpt:pin", name="axi0_awcache",   type_name=f"AWCACHE_0",    is_bus="true")
        et.SubElement(gen_pin_target0, "efxpt:pin", name="axi0_awid",      type_name=f"AWID_0",       is_bus="true")
        et.SubElement(gen_pin_target0, "efxpt:pin", name="axi0_awlen",     type_name=f"AWLEN_0",      is_bus="true")
        et.SubElement(gen_pin_target0, "efxpt:pin", name="axi0_awlock",    type_name=f"AWLOCK_0",     is_bus="false")
        et.SubElement(gen_pin_target0, "efxpt:pin", name="axi0_awqos",     type_name=f"AWQOS_0",      is_bus="false")
        et.SubElement(gen_pin_target0, "efxpt:pin", name="axi0_awsize",    type_name=f"AWSIZE_0",     is_bus="true")
        et.SubElement(gen_pin_target0, "efxpt:pin", name="axi0_awallstrb", type_name=f"AWALLSTRB_0",  is_bus="false")
        et.SubElement(gen_pin_target0, "efxpt:pin", name="axi0_awapcmd",   type_name=f"AWAPCMD_0",    is_bus="false")
        et.SubElement(gen_pin_target0, "efxpt:pin", name="axi0_awcobuf",   type_name=f"AWCOBUF_0",    is_bus="false")
        et.SubElement(gen_pin_target0, "efxpt:pin", name="axi0_awvalid",   type_name=f"AWVALID_0",    is_bus="false")
        et.SubElement(gen_pin_target0, "efxpt:pin", name="axi0_awready",   type_name=f"AWREADY_0",    is_bus="false")

        et.SubElement(gen_pin_target0, "efxpt:pin", name="axi0_rdata",     type_name=f"RDATA_0",      is_bus="true")
        et.SubElement(gen_pin_target0, "efxpt:pin", name="axi0_rid",       type_name=f"RID_0",        is_bus="true")
        et.SubElement(gen_pin_target0, "efxpt:pin", name="axi0_rlast",     type_name=f"RLAST_0",      is_bus="false")
        et.SubElement(gen_pin_target0, "efxpt:pin", name="axi0_rresp",     type_name=f"RRESP_0",      is_bus="true")
        et.SubElement(gen_pin_target0, "efxpt:pin", name="axi0_rvalid",    type_name=f"RVALID_0",     is_bus="false")
        et.SubElement(gen_pin_target0, "efxpt:pin", name="axi0_rready",    type_name=f"RREADY_0",     is_bus="false")

        et.SubElement(gen_pin_target0, "efxpt:pin", name="axi0_wdata",     type_name=f"WDATA_0",      is_bus="true")
        et.SubElement(gen_pin_target0, "efxpt:pin", name="axi0_wlast",     type_name=f"WLAST_0",      is_bus="false")
        et.SubElement(gen_pin_target0, "efxpt:pin", name="axi0_wstrb",     type_name=f"WSTRB_0",      is_bus="true")
        et.SubElement(gen_pin_target0, "efxpt:pin", name="axi0_wvalid",    type_name=f"WVALID_0",     is_bus="false")
        et.SubElement(gen_pin_target0, "efxpt:pin", name="axi0_wready",    type_name=f"WREADY_0",     is_bus="false")

        et.SubElement(gen_pin_target0, "efxpt:pin", name="axi0_bid",       type_name=f"BID_0",        is_bus="true")
        et.SubElement(gen_pin_target0, "efxpt:pin", name="axi0_bresp",     type_name=f"BRESP_0",      is_bus="true")
        et.SubElement(gen_pin_target0, "efxpt:pin", name="axi0_bvalid",    type_name=f"BVALID_0",     is_bus="false")
        et.SubElement(gen_pin_target0, "efxpt:pin", name="axi0_bready",    type_name=f"BREADY_0",     is_bus="false")

        axi_target1 = et.SubElement(ddr, "efxpt:axi_target1", is_axi_width_256="false", is_axi_enable="false")
        gen_pin_target1 = et.SubElement(axi_target1, "efxpt:gen_pin_axi")
        et.SubElement(gen_pin_target1, "efxpt:pin", name="", type_name=f"ACLK_1",       is_bus="false", is_clk="true", is_clk_invert="false")
        et.SubElement(gen_pin_target1, "efxpt:pin", name="", type_name=f"ARST_1",       is_bus="false")

        et.SubElement(gen_pin_target1, "efxpt:pin", name="", type_name=f"ARADDR_1",     is_bus="true")
        et.SubElement(gen_pin_target1, "efxpt:pin", name="", type_name=f"ARAPCMD_1",    is_bus="false")
        et.SubElement(gen_pin_target1, "efxpt:pin", name="", type_name=f"ARBURST_1",    is_bus="true")
        et.SubElement(gen_pin_target1, "efxpt:pin", name="", type_name=f"ARID_1",       is_bus="true")
        et.SubElement(gen_pin_target1, "efxpt:pin", name="", type_name=f"ARLEN_1",      is_bus="true")
        et.SubElement(gen_pin_target1, "efxpt:pin", name="", type_name=f"ARLOCK_1",     is_bus="false")
        et.SubElement(gen_pin_target1, "efxpt:pin", name="", type_name=f"ARQOS_1",      is_bus="false")
        et.SubElement(gen_pin_target1, "efxpt:pin", name="", type_name=f"ARSIZE_1",     is_bus="true")
        et.SubElement(gen_pin_target1, "efxpt:pin", name="", type_name=f"ARVALID_1",    is_bus="false")
        et.SubElement(gen_pin_target1, "efxpt:pin", name="", type_name=f"ARREADY_1",    is_bus="false")

        et.SubElement(gen_pin_target1, "efxpt:pin", name="", type_name=f"AWADDR_1",     is_bus="true")
        et.SubElement(gen_pin_target1, "efxpt:pin", name="", type_name=f"AWAPCMD_1",    is_bus="false")
        et.SubElement(gen_pin_target1, "efxpt:pin", name="", type_name=f"AWALLSTRB_1",  is_bus="false")
        et.SubElement(gen_pin_target1, "efxpt:pin", name="", type_name=f"AWCACHE_1",    is_bus="true")
        et.SubElement(gen_pin_target1, "efxpt:pin", name="", type_name=f"AWCOBUF_1",    is_bus="false")
        et.SubElement(gen_pin_target1, "efxpt:pin", name="", type_name=f"AWBURST_1",    is_bus="true")
        et.SubElement(gen_pin_target1, "efxpt:pin", name="", type_name=f"AWID_1",       is_bus="true")
        et.SubElement(gen_pin_target1, "efxpt:pin", name="", type_name=f"AWLEN_1",      is_bus="true")
        et.SubElement(gen_pin_target1, "efxpt:pin", name="", type_name=f"AWLOCK_1",     is_bus="false")
        et.SubElement(gen_pin_target1, "efxpt:pin", name="", type_name=f"AWQOS_1",      is_bus="false")
        et.SubElement(gen_pin_target1, "efxpt:pin", name="", type_name=f"AWSIZE_1",     is_bus="true")
        et.SubElement(gen_pin_target1, "efxpt:pin", name="", type_name=f"AWVALID_1",    is_bus="false")
        et.SubElement(gen_pin_target1, "efxpt:pin", name="", type_name=f"AWREADY_1",    is_bus="false")

        et.SubElement(gen_pin_target1, "efxpt:pin", name="", type_name=f"RDATA_1",      is_bus="true")
        et.SubElement(gen_pin_target1, "efxpt:pin", name="", type_name=f"RID_1",        is_bus="true")
        et.SubElement(gen_pin_target1, "efxpt:pin", name="", type_name=f"RLAST_1",      is_bus="false")
        et.SubElement(gen_pin_target1, "efxpt:pin", name="", type_name=f"RRESP_1",      is_bus="true")
        et.SubElement(gen_pin_target1, "efxpt:pin", name="", type_name=f"RVALID_1",     is_bus="false")
        et.SubElement(gen_pin_target1, "efxpt:pin", name="", type_name=f"RREADY_1",     is_bus="false")

        et.SubElement(gen_pin_target1, "efxpt:pin", name="", type_name=f"BID_1",        is_bus="true")
        et.SubElement(gen_pin_target1, "efxpt:pin", name="", type_name=f"BRESP_1",      is_bus="true")
        et.SubElement(gen_pin_target1, "efxpt:pin", name="", type_name=f"BVALID_1",     is_bus="false")
        et.SubElement(gen_pin_target1, "efxpt:pin", name="", type_name=f"BREADY_1",     is_bus="false")

        et.SubElement(gen_pin_target1, "efxpt:pin", name="", type_name=f"WDATA_1",      is_bus="true")
        et.SubElement(gen_pin_target1, "efxpt:pin", name="", type_name=f"WLAST_1",      is_bus="false")
        et.SubElement(gen_pin_target1, "efxpt:pin", name="", type_name=f"WSTRB_1",      is_bus="true")
        et.SubElement(gen_pin_target1, "efxpt:pin", name="", type_name=f"WVALID_1",     is_bus="false")
        et.SubElement(gen_pin_target1, "efxpt:pin", name="", type_name=f"WREADY_1",     is_bus="false")

        gen_pin_controller = et.SubElement(ddr, "efxpt:gen_pin_controller")
        et.SubElement(gen_pin_controller, "efxpt:pin", name="", type_name="CTRL_CLK",               is_bus="false", is_clk="true", is_clk_invert="false")
        et.SubElement(gen_pin_controller, "efxpt:pin", name="", type_name="CTRL_INT",               is_bus="false")
        et.SubElement(gen_pin_controller, "efxpt:pin", name="", type_name="CTRL_MEM_RST_VALID",     is_bus="false")
        et.SubElement(gen_pin_controller, "efxpt:pin", name="", type_name="CTRL_REFRESH",           is_bus="false")
        et.SubElement(gen_pin_controller, "efxpt:pin", name="", type_name="CTRL_BUSY",              is_bus="false")
        et.SubElement(gen_pin_controller, "efxpt:pin", name="", type_name="CTRL_CMD_Q_ALMOST_FULL", is_bus="false")
        et.SubElement(gen_pin_controller, "efxpt:pin", name="", type_name="CTRL_DP_IDLE",           is_bus="false")
        et.SubElement(gen_pin_controller, "efxpt:pin", name="", type_name="CTRL_CKE",               is_bus="true")
        et.SubElement(gen_pin_controller, "efxpt:pin", name="", type_name="CTRL_PORT_BUSY",         is_bus="true")

        gen_pin_config = et.SubElement(ddr, "efxpt:gen_pin_cfg_ctrl")
        et.SubElement(gen_pin_config, "efxpt:pin", name="cfg_done",  type_name="CFG_DONE",  is_bus="false")
        et.SubElement(gen_pin_config, "efxpt:pin", name="cfg_reset", type_name="CFG_RESET", is_bus="false")
        et.SubElement(gen_pin_config, "efxpt:pin", name="cfg_sel",   type_name="CFG_SEL",   is_bus="false")
        et.SubElement(gen_pin_config, "efxpt:pin", name="cfg_start", type_name="CFG_START", is_bus="false")

        ctrl_reg_inf = et.SubElement(ddr, "efxpt:ctrl_reg_inf", is_reg_ena="false")
        gen_pin_ctrl_reg_inf = et.SubElement(ctrl_reg_inf, "efxpt:gen_pin_ctrl_reg_inf")
        et.SubElement(gen_pin_ctrl_reg_inf, "efxpt:pin", name="axi_clk", type_name="CR_ACLK", is_bus="false", is_clk="true", is_clk_invert="false")
        et.SubElement(gen_pin_ctrl_reg_inf, "efxpt:pin", name="regARESETn", type_name="CR_ARESETN", is_bus="false")
        et.SubElement(gen_pin_ctrl_reg_inf, "efxpt:pin", name="regARVALID", type_name="CR_ARVALID", is_bus="false")
        et.SubElement(gen_pin_ctrl_reg_inf, "efxpt:pin", name="regARREADY", type_name="CR_ARREADY", is_bus="false")
        et.SubElement(gen_pin_ctrl_reg_inf, "efxpt:pin", name="regAWVALID", type_name="CR_AWVALID", is_bus="false")
        et.SubElement(gen_pin_ctrl_reg_inf, "efxpt:pin", name="regAWREADY", type_name="CR_AWREADY", is_bus="false")
        et.SubElement(gen_pin_ctrl_reg_inf, "efxpt:pin", name="regBVALID",  type_name="CR_BVALID",  is_bus="false")
        et.SubElement(gen_pin_ctrl_reg_inf, "efxpt:pin", name="regBREADY",  type_name="CR_BREADY",  is_bus="false")
        et.SubElement(gen_pin_ctrl_reg_inf, "efxpt:pin", name="regRLAST",   type_name="CR_RLAST",   is_bus="false")
        et.SubElement(gen_pin_ctrl_reg_inf, "efxpt:pin", name="regRVALID",  type_name="CR_RVALID",  is_bus="false")
        et.SubElement(gen_pin_ctrl_reg_inf, "efxpt:pin", name="regRREADY",  type_name="CR_RREADY",  is_bus="false")
        et.SubElement(gen_pin_ctrl_reg_inf, "efxpt:pin", name="regWLAST",   type_name="CR_WLAST",   is_bus="false")
        et.SubElement(gen_pin_ctrl_reg_inf, "efxpt:pin", name="regWVALID",  type_name="CR_WVALID",  is_bus="false")
        et.SubElement(gen_pin_ctrl_reg_inf, "efxpt:pin", name="regWREADY",  type_name="CR_WREADY",  is_bus="false")
        et.SubElement(gen_pin_ctrl_reg_inf, "efxpt:pin", name="regARADDR",  type_name="CR_ARADDR",  is_bus="true")
        et.SubElement(gen_pin_ctrl_reg_inf, "efxpt:pin", name="regARID",    type_name="CR_ARID",    is_bus="true")
        et.SubElement(gen_pin_ctrl_reg_inf, "efxpt:pin", name="regARLEN",   type_name="CR_ARLEN",   is_bus="true")
        et.SubElement(gen_pin_ctrl_reg_inf, "efxpt:pin", name="regARSIZE",  type_name="CR_ARSIZE",  is_bus="true")
        et.SubElement(gen_pin_ctrl_reg_inf, "efxpt:pin", name="regARBURST", type_name="CR_ARBURST", is_bus="true")
        et.SubElement(gen_pin_ctrl_reg_inf, "efxpt:pin", name="regAWADDR",  type_name="CR_AWADDR",  is_bus="true")
        et.SubElement(gen_pin_ctrl_reg_inf, "efxpt:pin", name="regAWID",    type_name="CR_AWID",    is_bus="true")
        et.SubElement(gen_pin_ctrl_reg_inf, "efxpt:pin", name="regAWLEN",   type_name="CR_AWLEN",   is_bus="true")
        et.SubElement(gen_pin_ctrl_reg_inf, "efxpt:pin", name="regAWSIZE",  type_name="CR_AWSIZE",  is_bus="true")
        et.SubElement(gen_pin_ctrl_reg_inf, "efxpt:pin", name="regAWBURST", type_name="CR_AWBURST", is_bus="true")
        et.SubElement(gen_pin_ctrl_reg_inf, "efxpt:pin", name="regBID",     type_name="CR_BID",     is_bus="true")
        et.SubElement(gen_pin_ctrl_reg_inf, "efxpt:pin", name="regBRESP",   type_name="CR_BRESP",   is_bus="true")
        et.SubElement(gen_pin_ctrl_reg_inf, "efxpt:pin", name="regRDATA",   type_name="CR_RDATA",   is_bus="true")
        et.SubElement(gen_pin_ctrl_reg_inf, "efxpt:pin", name="regRID",     type_name="CR_RID",     is_bus="true")
        et.SubElement(gen_pin_ctrl_reg_inf, "efxpt:pin", name="regRRESP",   type_name="CR_RRESP",   is_bus="true")
        et.SubElement(gen_pin_ctrl_reg_inf, "efxpt:pin", name="regWDATA",   type_name="CR_WDATA",   is_bus="true")
        et.SubElement(gen_pin_ctrl_reg_inf, "efxpt:pin", name="regWSTRB",   type_name="CR_WSTRB",   is_bus="true")
        et.SubElement(gen_pin_ctrl_reg_inf, "efxpt:pin", name="",           type_name="CFG_PHY_RSTN", is_bus="false")
        et.SubElement(gen_pin_ctrl_reg_inf, "efxpt:pin", name="",           type_name="CTRL_RSTN",  is_bus="false")

        cs_fpga = et.SubElement(ddr, "efxpt:cs_fpga")
        et.SubElement(cs_fpga, "efxpt:param", name="DQ_PULLDOWN_DRV", value="40", value_type="str")
        et.SubElement(cs_fpga, "efxpt:param", name="DQ_PULLDOWN_ODT", value="80", value_type="str")
        et.SubElement(cs_fpga, "efxpt:param", name="DQ_PULLUP_DRV",   value="40",   value_type="str")
        et.SubElement(cs_fpga, "efxpt:param", name="DQ_PULLUP_ODT",   value="Hi-Z", value_type="str")
        # et.SubElement(cs_fpga, "efxpt:param", name="FPGA_VREF_RANGE0", value="21.780", value_type="float")
        et.SubElement(cs_fpga, "efxpt:param", name="FPGA_VREF_RANGE0", value="23.000", value_type="float")
        et.SubElement(cs_fpga, "efxpt:param", name="FPGA_VREF_RANGE1", value="23.000", value_type="float")
        et.SubElement(cs_fpga, "efxpt:param", name="MEM_FPGA_VREF_RANGE", value="Range 1", value_type="str")

        cs_memory = et.SubElement(ddr, "efxpt:cs_memory")
        et.SubElement(cs_memory, "efxpt:param", name="BLEN",       value="BL=16 Sequential", value_type="str")
        et.SubElement(cs_memory, "efxpt:param", name="CA_ODT_CS0", value="RZQ/6",   value_type="str")
        et.SubElement(cs_memory, "efxpt:param", name="CA_ODT_CS1", value="Disable", value_type="str")
        # et.SubElement(cs_memory, "efxpt:param", name="CA_VREF_RANGE0", value="27.200", value_type="float")
        # et.SubElement(cs_memory, "efxpt:param", name="CA_VREF_RANGE1", value="22.000", value_type="float")
        et.SubElement(cs_memory, "efxpt:param", name="CA_VREF_RANGE0", value="22.000", value_type="float")
        et.SubElement(cs_memory, "efxpt:param", name="CA_VREF_RANGE1", value="22.400", value_type="float")
        et.SubElement(cs_memory, "efxpt:param", name="DQ_ODT_CS0", value="RZQ/4",   value_type="str")
        et.SubElement(cs_memory, "efxpt:param", name="DQ_ODT_CS1", value="Disable", value_type="str")
        # et.SubElement(cs_memory, "efxpt:param", name="DQ_VREF_RANGE0", value="27.200", value_type="float")
        et.SubElement(cs_memory, "efxpt:param", name="DQ_VREF_RANGE0", value="20.000", value_type="float")
        et.SubElement(cs_memory, "efxpt:param", name="DQ_VREF_RANGE1", value="22.000", value_type="float")
        # et.SubElement(cs_memory, "efxpt:param", name="MEM_CA_RANGE", value="RANGE[1]", value_type="str")
        # et.SubElement(cs_memory, "efxpt:param", name="MEM_DQ_RANGE", value="RANGE[1]", value_type="str")
        et.SubElement(cs_memory, "efxpt:param", name="MEM_CA_RANGE", value="RANGE[0]", value_type="str")
        et.SubElement(cs_memory, "efxpt:param", name="MEM_DQ_RANGE", value="RANGE[0]", value_type="str")
        et.SubElement(cs_memory, "efxpt:param", name="NWR",          value="nWR=6", value_type="str")
        et.SubElement(cs_memory, "efxpt:param", name="ODTD_CA_CS0", value="Obeys ODT_CA Bond Pad", value_type="str")
        et.SubElement(cs_memory, "efxpt:param", name="ODTD_CA_CS1", value="Obeys ODT_CA Bond Pad", value_type="str")
        et.SubElement(cs_memory, "efxpt:param", name="ODTE_CK_CS0", value="Override Disabled", value_type="str")
        et.SubElement(cs_memory, "efxpt:param", name="ODTE_CK_CS1", value="Override Disabled", value_type="str")
        et.SubElement(cs_memory, "efxpt:param", name="ODTE_CS_CS0", value="Override Disabled", value_type="str")
        et.SubElement(cs_memory, "efxpt:param", name="ODTE_CS_CS1", value="Override Disabled", value_type="str")
        et.SubElement(cs_memory, "efxpt:param", name="PDDS_CS0", value="RZQ/6", value_type="str")
        et.SubElement(cs_memory, "efxpt:param", name="PDDS_CS1", value="RFU", value_type="str")
        et.SubElement(cs_memory, "efxpt:param", name="RL_DBI_READ", value="No", value_type="str")
        et.SubElement(cs_memory, "efxpt:param", name="RL_DBI_READ_DISABLED", value="RL=6,nRTP=8", value_type="str")
        et.SubElement(cs_memory, "efxpt:param", name="RL_DBI_READ_ENABLED",  value="RL=6,nRTP=8", value_type="str")
        et.SubElement(cs_memory, "efxpt:param", name="RL_DBI_WRITE", value="No", value_type="str")
        et.SubElement(cs_memory, "efxpt:param", name="WL_SET", value="Set A", value_type="str")
        et.SubElement(cs_memory, "efxpt:param", name="WL_SET_A", value="WL=4", value_type="str")
        et.SubElement(cs_memory, "efxpt:param", name="WL_SET_B", value="WL=4", value_type="str")

        timing = et.SubElement(ddr, "efxpt:cs_memory_timing")
        et.SubElement(timing, "efxpt:param", name="tCCD",   value="8",       value_type="int")
        et.SubElement(timing, "efxpt:param", name="tCCDMW", value="32",      value_type="int")
        et.SubElement(timing, "efxpt:param", name="tFAW",   value="40.000",  value_type="float")
        et.SubElement(timing, "efxpt:param", name="tPPD",   value="4",       value_type="int")
        et.SubElement(timing, "efxpt:param", name="tRAS",   value="42.000",  value_type="float")
        et.SubElement(timing, "efxpt:param", name="tRCD",   value="18.000",  value_type="float")
        et.SubElement(timing, "efxpt:param", name="tRPab",  value="21.000",  value_type="float")
        et.SubElement(timing, "efxpt:param", name="tRPpb",  value="18.000",  value_type="float")
        et.SubElement(timing, "efxpt:param", name="tRRD",   value="10.000",  value_type="float")
        et.SubElement(timing, "efxpt:param", name="tRTP",   value="7.500",   value_type="float")
        et.SubElement(timing, "efxpt:param", name="tSR",    value="15.000",  value_type="float")
        et.SubElement(timing, "efxpt:param", name="tWR",    value="18.000",  value_type="float")
        et.SubElement(timing, "efxpt:param", name="tWTR",   value="10.000",  value_type="float")


if __name__ == "__main__":
    main()
