#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Sergiu Mosanu <sm7ed@virginia.edu>
# Copyright (c) 2020-2021 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2020 Antmicro <www.antmicro.com>
#
# SPDX-License-Identifier: BSD-2-Clause

# To interface via the serial port use:
#     lxterm /dev/ttyUSBx --speed=115200

import argparse, os

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex_boards.platforms import alveo_u280

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.interconnect.axi import *
from litex.soc.interconnect.csr import *

from litex.soc.cores.led import LedChaser
from litedram.modules import MTA18ASF2G72PZ
from litedram.phy import usddrphy

from litepcie.phy.usppciephy import USPPCIEPHY
from litepcie.software import generate_litepcie_software

from litedram.common import *
from litedram.frontend.axi import *

from litescope import LiteScopeAnalyzer

# HBM IP

class HBMIP(Module, AutoCSR):
    """Xilinx Virtex US+ High Bandwidth Memory 2 IP wrapper"""
    def __init__(self, platform, hbm_ip_name="hbm_0"):
        self.platform = platform
        self.hbm_name = hbm_ip_name

        self.axi = []
        self.apb = []

        self.hbm_params = {}

        self.init_done = CSRStatus()

        # # #

        class Open(Signal): pass

        # Clocks -----------------------------------------------------------------------------------
        # Ref = 100 MHz (HBM: 900 (225-900) MHz), drives internal PLL (1 per stack).
        for i in range(2):
            self.hbm_params[f"i_HBM_REF_CLK_{i:1d}"] = ClockSignal("hbm_ref")

        # APB: 100 (50-100) MHz
        for i in range(2):
            self.hbm_params[f"i_APB_{i:1d}_PCLK"]     = ClockSignal("apb")
            self.hbm_params[f"i_APB_{i:1d}_PRESET_N"] = ~ResetSignal("apb")

        # AXI: 450 (225-450) MHz
        for i in range(32):
            self.hbm_params[f"i_AXI_{i:02d}_ACLK"]     = ClockSignal("axi")
            self.hbm_params[f"i_AXI_{i:02d}_ARESET_N"] = ~ResetSignal("apb")

        # AXI --------------------------------------------------------------------------------------
        for i in range(32):
            axi = AXIInterface(data_width=256, address_width=33, id_width=6)
            self.axi.append(axi)

            # AW Channel.
            self.hbm_params[f"i_AXI_{i :02d}_AWADDR"]      = axi.aw.addr
            self.hbm_params[f"i_AXI_{i :02d}_AWBURST"]     = axi.aw.burst
            self.hbm_params[f"i_AXI_{i :02d}_AWID"]        = axi.aw.id
            self.hbm_params[f"i_AXI_{i :02d}_AWLEN"]       = axi.aw.len
            self.hbm_params[f"i_AXI_{i :02d}_AWSIZE"]      = axi.aw.size
            self.hbm_params[f"i_AXI_{i :02d}_AWVALID"]     = axi.aw.valid
            self.hbm_params[f"o_AXI_{i :02d}_AWREADY"]     = axi.aw.ready

            # W Channel.
            self.hbm_params[f"i_AXI_{i:02d}_WDATA"]        = axi.w.data
            self.hbm_params[f"i_AXI_{i:02d}_WLAST"]        = axi.w.last
            self.hbm_params[f"i_AXI_{i:02d}_WSTRB"]        = axi.w.strb
            self.hbm_params[f"i_AXI_{i:02d}_WDATA_PARITY"] = 0 # FIXME: Manage parity?
            self.hbm_params[f"i_AXI_{i:02d}_WVALID"]       = axi.w.valid
            self.hbm_params[f"o_AXI_{i:02d}_WREADY"]       = axi.w.ready

            # B Channel.
            self.hbm_params[f"o_AXI_{i:02d}_BID"]          = axi.b.id
            self.hbm_params[f"o_AXI_{i:02d}_BRESP"]        = axi.b.resp
            self.hbm_params[f"o_AXI_{i:02d}_BVALID"]       = axi.b.valid
            self.hbm_params[f"i_AXI_{i:02d}_BREADY"]       = axi.b.ready

            # AR Channel.
            self.hbm_params[f"i_AXI_{i:02d}_ARADDR"]       = axi.ar.addr
            self.hbm_params[f"i_AXI_{i:02d}_ARBURST"]      = axi.ar.burst
            self.hbm_params[f"i_AXI_{i:02d}_ARID"]         = axi.ar.id
            self.hbm_params[f"i_AXI_{i:02d}_ARLEN"]        = axi.ar.len
            self.hbm_params[f"i_AXI_{i:02d}_ARSIZE"]       = axi.ar.size
            self.hbm_params[f"i_AXI_{i:02d}_ARVALID"]      = axi.ar.valid
            self.hbm_params[f"o_AXI_{i:02d}_ARREADY"]      = axi.ar.ready

            # R Channel.
            self.hbm_params[f"o_AXI_{i:02d}_RDATA_PARITY"] = Open() # FIXME: Manage parity?
            self.hbm_params[f"o_AXI_{i:02d}_RDATA"]        = axi.r.data
            self.hbm_params[f"o_AXI_{i:02d}_RID"]          = axi.r.id
            self.hbm_params[f"o_AXI_{i:02d}_RLAST"]        = axi.r.last
            self.hbm_params[f"o_AXI_{i:02d}_RRESP"]        = axi.r.resp
            self.hbm_params[f"o_AXI_{i:02d}_RVALID"]       = axi.r.valid
            self.hbm_params[f"i_AXI_{i:02d}_RREADY"]       = axi.r.ready

        # APB --------------------------------------------------------------------------------------
        # FIXME: Connect to CSR or Wishbone.
        apb_complete = Signal(2)
        for i in range(2):
            self.hbm_params[f"i_APB_{i:1d}_PWDATA"]  = 0
            self.hbm_params[f"i_APB_{i:1d}_PADDR"]   = 0
            self.hbm_params[f"i_APB_{i:1d}_PENABLE"] = 0
            self.hbm_params[f"i_APB_{i:1d}_PSEL"]    = 0
            self.hbm_params[f"i_APB_{i:1d}_PWRITE"]  = 0

            self.hbm_params[f"o_APB_{i:1d}_PRDATA"]  = Open()
            self.hbm_params[f"o_APB_{i:1d}_PREADY"]  = Open()
            self.hbm_params[f"o_APB_{i:1d}_PSLVERR"] = Open()

            self.hbm_params[f"o_apb_complete_{i:1d}"] = apb_complete[i]
        self.comb += self.init_done.status.eq(apb_complete == 0b11)

        # Temperature ------------------------------------------------------------------------------
        for i in range(2):
            self.hbm_params[f"o_DRAM_{i:1d}_STAT_CATTRIP"] = Open()
            self.hbm_params[f"o_DRAM_{i:1d}_STAT_TEMP"]    = Open()

    def add_sources(self, platform):
        this_dir = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
        os.system("wget https://github.com/litex-hub/litex-boards/files/6893157/hbm_0.xci.txt")
        os.makedirs("ip/hbm", exist_ok=True)
        os.system("mv hbm_0.xci.txt ip/hbm/hbm_0.xci")
        platform.add_ip(os.path.join(this_dir, "ip", "hbm", self.hbm_name + ".xci"))

    def do_finalize(self):
        self.add_sources(self.platform)
        self.specials += Instance(self.hbm_name, **self.hbm_params)

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq, ddram_channel, with_hbm):
        if with_hbm:
            self.clock_domains.cd_sys     = ClockDomain()
            self.clock_domains.cd_hbm_ref = ClockDomain()
            self.clock_domains.cd_apb     = ClockDomain()
        else: # ddr4
            self.rst = Signal()
            self.clock_domains.cd_sys    = ClockDomain()
            self.clock_domains.cd_sys4x  = ClockDomain(reset_less=True)
            self.clock_domains.cd_pll4x  = ClockDomain(reset_less=True)
            self.clock_domains.cd_idelay = ClockDomain()

        # # #

        if with_hbm:
            self.submodules.pll = pll = USMMCM(speedgrade=-2)
            pll.register_clkin(platform.request("sysclk", ddram_channel), 100e6)
            pll.create_clkout(self.cd_sys,     sys_clk_freq)
            pll.create_clkout(self.cd_hbm_ref, 100e6)
            pll.create_clkout(self.cd_apb,     100e6)
            platform.add_false_path_constraints(self.cd_sys.clk, self.cd_apb.clk)
        else: # ddr4
            self.submodules.pll = pll = USMMCM(speedgrade=-2)
            self.comb += pll.reset.eq(self.rst)
            pll.register_clkin(platform.request("sysclk", ddram_channel), 100e6)
            pll.create_clkout(self.cd_pll4x, sys_clk_freq*4, buf=None, with_reset=False)
            pll.create_clkout(self.cd_idelay, 600e6) #, with_reset=False
            platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

            self.specials += [
                Instance("BUFGCE_DIV", name="main_bufgce_div",
                    p_BUFGCE_DIVIDE=4,
                    i_CE=1, i_I=self.cd_pll4x.clk, o_O=self.cd_sys.clk),
                Instance("BUFGCE", name="main_bufgce",
                    i_CE=1, i_I=self.cd_pll4x.clk, o_O=self.cd_sys4x.clk),
                # AsyncResetSynchronizer(self.cd_idelay, ~pll.locked),
            ]

            self.submodules.idelayctrl = USIDELAYCTRL(cd_ref=self.cd_idelay, cd_sys=self.cd_sys)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(150e6), ddram_channel=0, with_pcie=False, with_led_chaser=False, with_hbm=False, **kwargs):
        platform = alveo_u280.Platform()
        if with_hbm:
            assert 225e6 <= sys_clk_freq <= 450e6

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident = "LiteX SoC on Alveo U280 (ES1)",
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq, ddram_channel, with_hbm)

        if with_hbm:
            # JTAGBone --------------------------------------------------------------------------------
            #self.add_jtagbone(chain=2) # Chain 1 already used by HBM2 debug probes.

            # Add HBM Core.
            self.submodules.hbm = hbm = ClockDomainsRenamer({"axi": "sys"})(HBMIP(platform))

            # Connect four of the HBM's AXI interfaces to the main bus of the SoC.
            for i in range(4):
                axi_hbm      = hbm.axi[i]
                axi_lite_hbm = AXILiteInterface(data_width=256, address_width=33)
                self.submodules += AXILite2AXI(axi_lite_hbm, axi_hbm)
                self.bus.add_slave(f"hbm{i}", axi_lite_hbm, SoCRegion(origin=0x4000_0000 + 0x1000_0000*i, size=0x1000_0000)) # 256MB.
            # Link HBM2 channel 0 as main RAM
            self.bus.add_region("main_ram", SoCRegion(origin=0x4000_0000, size=0x1000_0000, linker=True)) # 256MB.

        else:
            # DDR4 SDRAM -------------------------------------------------------------------------------
            if not self.integrated_main_ram_size:
                self.submodules.ddrphy = usddrphy.USPDDRPHY(platform.request("ddram", ddram_channel),
                    memtype          = "DDR4",
                    cmd_latency      = 1, # seems to work better with cmd_latency=1
                    sys_clk_freq     = sys_clk_freq,
                    iodelay_clk_freq = 600e6,
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
            self.submodules.pcie_phy = USPPCIEPHY(platform, platform.request("pcie_x4"),
                data_width = 128,
                bar0_size  = 0x20000)
            self.add_pcie(phy=self.pcie_phy, ndmas=1)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("gpio_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on Alveo U280")
    parser.add_argument("--build",           action="store_true", help="Build bitstream.")
    parser.add_argument("--load",            action="store_true", help="Load bitstream.")
    parser.add_argument("--sys-clk-freq",    default=150e6,       help="System clock frequency.") # HBM2 with 250MHz, DDR4 with 150MHz (1:4)
    parser.add_argument("--ddram-channel",   default="0",         help="DDRAM channel (0, 1, 2 or 3).") # also selects clk 0 or 1
    parser.add_argument("--with-pcie",       action="store_true", help="Enable PCIe support.")
    parser.add_argument("--driver",          action="store_true", help="Generate PCIe driver.")
    parser.add_argument("--with-hbm",        action="store_true", help="Use HBM2.")
    parser.add_argument("--with-analyzer",   action="store_true", help="Enable Analyzer.")
    parser.add_argument("--with-led-chaser", action="store_true", help="Enable LED Chaser.")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    if args.with_hbm:
        args.sys_clk_freq = 250e6

    soc = BaseSoC(
        sys_clk_freq    = int(float(args.sys_clk_freq)),
        ddram_channel   = int(args.ddram_channel, 0),
        with_pcie       = args.with_pcie,
        with_led_chaser = args.with_led_chaser,
        with_hbm        = args.with_hbm,
        with_analyzer   = args.with_analyzer,
        **soc_core_argdict(args)
	)
    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.driver:
        generate_litepcie_software(soc, os.path.join(builder.output_dir, "driver"))

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".bit"))

if __name__ == "__main__":
    main()
