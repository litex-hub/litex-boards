#!/usr/bin/env python3
#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Antmicro <www.antmicro.com>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import *

from litex_boards.platforms import antmicro_lpddr4_test_board

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litedram.modules import MT53E256M16D1
from litedram.phy import lpddr4

from liteeth.phy import LiteEthS7PHYRGMII
from litex.soc.cores.hyperbus import HyperRAM

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, iodelay_clk_freq):
        self.rst       = Signal()
        self.cd_sys    = ClockDomain()
        self.cd_sys2x  = ClockDomain()
        self.cd_sys8x  = ClockDomain()
        self.cd_idelay = ClockDomain()

        # # #

        self.pll = pll = S7PLL(speedgrade=-1)
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(platform.request("clk100"), 100e6)
        pll.create_clkout(self.cd_sys,    sys_clk_freq)
        pll.create_clkout(self.cd_sys2x,  2 * sys_clk_freq)
        pll.create_clkout(self.cd_sys8x,  8 * sys_clk_freq)
        pll.create_clkout(self.cd_idelay, iodelay_clk_freq)

        self.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, *, sys_clk_freq=50e6, iodelay_clk_freq=200e6,
            with_ethernet   = False,
            with_etherbone  = False,
            eth_ip          = "192.168.1.50",
            eth_dynamic_ip  = False,
            with_hyperram   = False,
            with_sdcard     = False,
            with_jtagbone   = True,
            with_uartbone   = False,
            with_led_chaser = True,
            **kwargs):
        platform = antmicro_lpddr4_test_board.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, iodelay_clk_freq=iodelay_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on LPDDR4 Test Board", **kwargs)

        # LDDR4 SDRAM ------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.ddrphy = lpddr4.K7LPDDR4PHY(platform.request("lpddr4"),
                iodelay_clk_freq = iodelay_clk_freq,
                sys_clk_freq     = sys_clk_freq,
            )
            self.add_sdram("sdram",
                phy                     = self.ddrphy,
                module                  = MT53E256M16D1(sys_clk_freq, "1:8"),
                l2_cache_size           = kwargs.get("l2_size", 8192),
                l2_cache_min_data_width = 256,
            )

        # HyperRAM ---------------------------------------------------------------------------------
        if with_hyperram:
            self.hyperram = HyperRAM(platform.request("hyperram"), sys_clk_freq=sys_clk_freq)
            self.bus.add_slave("hyperram", slave=self.hyperram.bus, region=SoCRegion(origin=0x20000000, size=8*1024*1024))

        # SD Card ----------------------------------------------------------------------------------
        if with_sdcard:
            self.add_sdcard()

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            # Traces between PHY and FPGA introduce ignorable delays of ~0.165ns +/- 0.015ns.
            # PHY chip does not introduce delays on TX (FPGA->PHY), however it includes 1.2ns
            # delay for RX CLK so we only need 0.8ns to match the desired 2ns.
            self.ethphy = LiteEthS7PHYRGMII(
                clock_pads = self.platform.request("eth_clocks"),
                pads       = self.platform.request("eth"),
                rx_delay   = 0.8e-9,
            )
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy, dynamic_ip=eth_dynamic_ip)
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, ip_address=eth_ip)

        # Jtagbone ---------------------------------------------------------------------------------
        if with_jtagbone:
            self.add_jtagbone()

        # UartBone ---------------------------------------------------------------------------------
        if with_uartbone:
            self.add_uartbone(baudrate=1e6)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=antmicro_lpddr4_test_board.Platform, description="LiteX SoC on LPDDR4 Test Board.")
    parser.add_target_argument("--flash",            action="store_true", help="Flash bitstream.")
    parser.add_target_argument("--sys-clk-freq",     default=50e6,  type=float, help="System clock frequency.")
    parser.add_target_argument("--iodelay-clk-freq", default=200e6, type=float, help="IODELAYCTRL frequency.")
    ethopts = parser.target_group.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",          action="store_true",    help="Add Ethernet.")
    ethopts.add_argument("--with-etherbone",         action="store_true",    help="Add EtherBone.")
    parser.add_target_argument("--eth-ip",           default="192.168.1.50", help="Ethernet/Etherbone IP address.")
    parser.add_target_argument("--eth-dynamic-ip",   action="store_true",    help="Enable dynamic Ethernet IP addresses setting.")
    parser.add_target_argument("--with-hyperram",    action="store_true",    help="Add HyperRAM.")
    parser.add_target_argument("--with-sdcard",      action="store_true",    help="Add SDCard.")
    parser.add_target_argument("--with-jtagbone",    action="store_true",    help="Add JTAGBone.")
    parser.add_target_argument("--with-uartbone",    action="store_true",    help="Add UartBone on 2nd serial.")
    args = parser.parse_args()

    assert not (args.with_etherbone and args.eth_dynamic_ip)

    soc = BaseSoC(
        sys_clk_freq      = args.sys_clk_freq,
        iodelay_clk_freq  = args.iodelay_clk_freq,
        with_ethernet     = args.with_ethernet,
        with_etherbone    = args.with_etherbone,
        eth_ip            = args.eth_ip,
        eth_dynamic_ip    = args.eth_dynamic_ip,
        with_hyperram     = args.with_hyperram,
        with_sdcard       = args.with_sdcard,
        with_jtagbone     = args.with_jtagbone,
        with_uartbone     = args.with_uartbone,
        **parser.soc_argdict)
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.flash(0, builder.get_bitstream_filename(mode="flash"))

if __name__ == "__main__":
    main()
