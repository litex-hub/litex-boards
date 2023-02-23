#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2021 Greg Davill <greg.davill@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

# Build/Use:
# ./gsd_butterstick.py --uart-name=crossover --with-etherbone --csr-csv=csr.csv --build --load --programmer (jtag / dfu)
# litex_server --udp
# litex_term crossover

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from litex_boards.platforms import gsd_butterstick

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.gpio import GPIOTristate

from litedram.modules import MT41K64M16,MT41K128M16,MT41K256M16,MT41K512M16
from litedram.phy import ECP5DDRPHY

from liteeth.phy.ecp5rgmii import LiteEthPHYRGMII

# CRG ---------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst        = Signal()
        self.cd_init    = ClockDomain()
        self.cd_por     = ClockDomain()
        self.cd_sys     = ClockDomain()
        self.cd_sys2x   = ClockDomain()
        self.cd_sys2x_i = ClockDomain()

        # # #

        self.stop  = Signal()
        self.reset = Signal()

        # Clk / Rst
        clk30 = platform.request("clk30")
        rst_n = platform.request("user_btn", 0)

        # Power on reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += self.cd_por.clk.eq(clk30)
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # PLL
        self.pll = pll = ECP5PLL()
        self.comb += pll.reset.eq(~por_done | ~rst_n | self.rst)
        pll.register_clkin(clk30, 30e6)
        pll.create_clkout(self.cd_sys2x_i, 2*sys_clk_freq)
        pll.create_clkout(self.cd_init,   25e6)
        self.specials += [
            Instance("ECLKSYNCB",
                i_ECLKI = self.cd_sys2x_i.clk,
                i_STOP  = self.stop,
                o_ECLKO = self.cd_sys2x.clk),
            Instance("CLKDIVF",
                p_DIV     = "2.0",
                i_ALIGNWD = 0,
                i_CLKI    = self.cd_sys2x.clk,
                i_RST     = self.reset,
                o_CDIVX   = self.cd_sys.clk),
            AsyncResetSynchronizer(self.cd_sys, ~pll.locked | self.reset),
        ]

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, revision="1.0", device="85F", sys_clk_freq=60e6, toolchain="trellis",
        sdram_device     = "MT41K64M16",
        with_ethernet    = False,
        with_etherbone   = False,
        eth_ip           = "192.168.1.50",
        eth_dynamic_ip   = False,
        with_spi_flash   = False,
        with_led_chaser  = True,
        with_syzygy_gpio = True,
        **kwargs)       :
        platform = gsd_butterstick.Platform(revision=revision, device=device ,toolchain=toolchain)

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        if kwargs["uart_name"] == "serial":
            kwargs["uart_name"] = "crossover"
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on ButterStick", **kwargs)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            available_sdram_modules = {
                "MT41K64M16":  MT41K64M16,
                "MT41K128M16": MT41K128M16,
                "MT41K256M16": MT41K256M16,
                "MT41K512M16": MT41K512M16,
            }
            sdram_module = available_sdram_modules.get(sdram_device)

            self.ddrphy = ECP5DDRPHY(
                platform.request("ddram"),
                sys_clk_freq=sys_clk_freq)
            self.comb += self.crg.stop.eq(self.ddrphy.init.stop)
            self.comb += self.crg.reset.eq(self.ddrphy.init.reset)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = sdram_module(sys_clk_freq, "1:2"),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            self.ethphy = LiteEthPHYRGMII(
                clock_pads = self.platform.request("eth_clocks"),
                pads       = self.platform.request("eth"),
                rx_delay   = 0e-9, # KSZ9031RNX phy adds a 1.2ns RX delay
                )
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy, dynamic_ip=eth_dynamic_ip)
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, ip_address=eth_ip)

        # SPI Flash --------------------------------------------------------------------------------
        if with_spi_flash:
            from litespi.modules import W25Q128JV
            from litespi.opcodes import SpiNorFlashOpCodes as Codes
            self.add_spi_flash(mode="4x", module=W25Q128JV(Codes.READ_1_1_4), with_master=False)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.comb += platform.request("user_led_color").eq(0b010) # Blue.
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

        # GPIOs ------------------------------------------------------------------------------------
        if with_syzygy_gpio:
            platform.add_extension(gsd_butterstick.raw_syzygy_io("SYZYGY0"))
            self.gpio = GPIOTristate(platform.request("SYZYGY0"))

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=gsd_butterstick.Platform, description="LiteX SoC on ButterStick.")
    parser.add_target_argument("--programmer",   default="jtag",           help="Programming interface (jtag or dfu).")
    parser.add_target_argument("--sys-clk-freq", default=75e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--revision",     default="1.0",            help="Board Revision (1.0).")
    parser.add_target_argument("--device",       default="85F",            help="ECP5 device (25F, 45F, 85F).")
    parser.add_target_argument("--sdram-device", default="MT41K64M16",     help="SDRAM device (MT41K64M16, MT41K128M16, MT41K256M16 or MT41K512M16).")
    ethopts = parser.target_group.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",  action="store_true",    help="Add Ethernet.")
    ethopts.add_argument("--with-etherbone", action="store_true",    help="Add EtherBone.")
    parser.add_target_argument("--eth-ip",         default="192.168.1.50", help="Ethernet/Etherbone IP address.")
    parser.add_target_argument("--eth-dynamic-ip", action="store_true",    help="Enable dynamic Ethernet IP addresses setting.")
    parser.add_target_argument("--with-spi-flash", action="store_true",    help="Enable SPI Flash (MMAPed).")
    sdopts = parser.target_group.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-sdcard", action="store_true", help="Enable SPI-mode SDCard support.")
    sdopts.add_argument("--with-sdcard",     action="store_true", help="Enable SDCard support.")
    parser.add_target_argument("--with-syzygy-gpio",action="store_true", help="Enable GPIOs through SYZYGY Breakout on Port-A.")
    args = parser.parse_args()

    assert not (args.with_etherbone and args.eth_dynamic_ip)

    soc = BaseSoC(
        toolchain        = args.toolchain,
        revision         = args.revision,
        device           = args.device,
        sdram_device     = args.sdram_device,
        sys_clk_freq     = args.sys_clk_freq,
        with_ethernet    = args.with_ethernet,
        with_etherbone   = args.with_etherbone,
        eth_ip           = args.eth_ip,
        eth_dynamic_ip   = args.eth_dynamic_ip,
        with_spi_flash   = args.with_spi_flash,
        with_syzygy_gpio = args.with_syzygy_gpio,
        **parser.soc_argdict)
    if args.with_spi_sdcard:
        soc.add_spi_sdcard()
    if args.with_sdcard:
        soc.add_sdcard()
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer(args.programmer)
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
