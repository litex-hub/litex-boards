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
from litex_boards.extensions.syzygy import SyzygyGPIO

from litex.soc.cores.clock import *
from litex.soc.integration.soc import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.gpio import GPIOIn
from litex.soc.cores.gpio import GPIOTristate

from litedram.modules import MT41K64M16,MT41K128M16,MT41K256M16,MT41K512M16
from litedram.phy import ECP5DDRPHY

from liteeth.phy.ecp5rgmii import LiteEthPHYRGMII

# CRG ---------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, sdram_rate="1:2"):
        self.rst        = Signal()
        self.cd_init    = ClockDomain()
        self.cd_por     = ClockDomain()
        self.cd_sys     = ClockDomain()
        self.cd_sys2x   = ClockDomain()
        self.cd_sys2x_i = ClockDomain()
        if sdram_rate == "1:4":
            self.cd_sys4x   = ClockDomain()
            self.cd_sys4x_i = ClockDomain()

        # # #

        self.stop  = Signal()
        self.reset = Signal()

        # Clk / Rst
        clk30 = platform.request("clk30")
        rst_n = platform.request("user_btn_n", 0)

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
        if sdram_rate == "1:2":
            # sys2x: DDR edge clock (ECLKSYNCB), sys = sys2x/2 (CLKDIVF).
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
        else:
            # sys4x: DDR edge clock (ECLKSYNCB), sys2x = sys4x/2 (CLKDIVF, PHY clock). sys
            # (controller clock) must be phase aligned with sys2x (DFI rate converter): generated
            # through the second edge clock synchronizer/divider of the DDR side from a 2x sys PLL
            # output (same structural path as sys2x, both realigned by the PHY init stop/reset
            # sequence).
            eclksync1_bel, clkdiv1_bel = {
                "25F": ("X72/Y25/ECLKSYNC1_BK2",  "X72/Y25/CLKDIV1"),
                "45F": ("X90/Y34/ECLKSYNC1_BK2",  "X90/Y34/CLKDIV1"),
                "85F": ("X126/Y46/ECLKSYNC1_BK2", "X126/Y46/CLKDIV1"),
            }[{"25": "25F", "45": "45F", "85": "85F"}[platform.device.split("-")[1][:2]]]
            pll.create_clkout(self.cd_sys4x_i, 4*sys_clk_freq)
            pll.create_clkout(self.cd_sys2x_i, 2*sys_clk_freq)
            pll.create_clkout(self.cd_init,   25e6)
            sys2x_e = Signal()
            self.specials += [
                Instance("ECLKSYNCB",
                    i_ECLKI = self.cd_sys4x_i.clk,
                    i_STOP  = self.stop,
                    o_ECLKO = self.cd_sys4x.clk),
                Instance("CLKDIVF",
                    p_DIV     = "2.0",
                    i_ALIGNWD = 0,
                    i_CLKI    = self.cd_sys4x.clk,
                    i_RST     = self.reset,
                    o_CDIVX   = self.cd_sys2x.clk),
                Instance("ECLKSYNCB",
                    i_ECLKI = self.cd_sys2x_i.clk,
                    i_STOP  = self.stop,
                    o_ECLKO = sys2x_e,
                    attr    = {("BEL", eclksync1_bel)}),
                Instance("CLKDIVF",
                    p_DIV     = "2.0",
                    i_ALIGNWD = 0,
                    i_CLKI    = sys2x_e,
                    i_RST     = self.reset,
                    o_CDIVX   = self.cd_sys.clk,
                    attr      = {("BEL", clkdiv1_bel)}),
                AsyncResetSynchronizer(self.cd_sys4x, ~pll.locked | self.reset),
                AsyncResetSynchronizer(self.cd_sys,   ~pll.locked | self.reset),
            ]
            # sys2x reset released from sys (deterministic phase of the DFI rate converter).
            sys2x_rst = Signal(reset=1, reset_less=True)
            self.sync.sys2x += sys2x_rst.eq(ResetSignal("sys"))
            self.comb += self.cd_sys2x.rst.eq(sys2x_rst)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, revision="1.0", device="85F", sys_clk_freq=60e6, toolchain="trellis",
        sdram_device     = "MT41K64M16",
        sdram_rate       = "1:2",
        with_ethernet    = False,
        with_etherbone   = False,
        eth_ip           = "192.168.1.50",
        remote_ip        = None,
        eth_dynamic_ip   = False,
        with_spi_flash   = False,
        with_led_chaser  = True,
        with_syzygy_gpio = True,
        with_buttons     = False,
        **kwargs)       :
        platform = gsd_butterstick.Platform(revision=revision, device=device ,toolchain=toolchain)

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, sdram_rate=sdram_rate)

        # SoCCore ----------------------------------------------------------------------------------
        if kwargs["uart_name"] == "serial":
            if kwargs.get("uart_name", "serial") == "serial": kwargs["uart_name"] = "crossover"
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

            # 1:2: DDR3 at 2x sys. 1:4: DDR3 at 4x sys (DDR3-600 at 75MHz).
            if sdram_rate == "1:2":
                phy_cls = ECP5DDRPHY
            else:
                from litedram.phy.ecp5ddrphy import ecp5ddrphy_with_ratio
                phy_cls = ecp5ddrphy_with_ratio(2)
            self.ddrphy = phy_cls(
                platform.request("ddram"),
                sys_clk_freq=sys_clk_freq)
            self.comb += self.crg.stop.eq(self.ddrphy.init.stop)
            self.comb += self.crg.reset.eq(self.ddrphy.init.reset)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = sdram_module(sys_clk_freq, sdram_rate),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            self.ethphy = LiteEthPHYRGMII(
                clock_pads = self.platform.request("eth_clocks"),
                pads       = self.platform.request("eth"),
                rx_delay   = 0e-9, # KSZ9031RNX phy adds a 1.2ns RX delay
                )
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, ip_address=eth_ip, with_ethmac=with_ethernet)
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy, dynamic_ip=eth_dynamic_ip, local_ip=eth_ip, remote_ip=remote_ip)

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

        # Buttons ---------------------------------------------------------------------------------
        if with_buttons:
            self.buttons = GPIOIn(Cat(platform.request_all("user_btn_n")[1:]))

        # GPIOs ------------------------------------------------------------------------------------
        if with_syzygy_gpio:
            platform.add_extension(SyzygyGPIO("SYZYGY0", signals=32))
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
    parser.add_target_argument("--sdram-rate",   default="1:2", choices=["1:2", "1:4"], help="SDRAM controller:DRAM clock ratio.")
    ethopts = parser.target_group.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",  action="store_true", help="Enable Ethernet support.")
    ethopts.add_argument("--with-etherbone", action="store_true", help="Enable Etherbone support.")
    parser.add_target_argument("--eth-ip",         default="192.168.1.50",  help="Ethernet/Etherbone IP address.")
    parser.add_target_argument("--remote-ip",      default="192.168.1.100", help="Remote IP address of TFTP server.")
    parser.add_target_argument("--eth-dynamic-ip", action="store_true",     help="Enable dynamic Ethernet IP assignment.")
    parser.add_target_argument("--with-spi-flash", action="store_true",     help="Enable memory-mapped SPI flash.")
    sdopts = parser.target_group.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-sdcard", action="store_true", help="Enable SPI-mode SDCard support.")
    sdopts.add_argument("--with-sdcard",     action="store_true", help="Enable SDCard support.")
    parser.add_target_argument("--with-syzygy-gpio",    action="store_true",        help="Enable GPIOs through SYZYGY Breakout on Port-A.")
    parser.add_target_argument("--with-buttons",        action="store_true",        help="Enable Buttons.")
    args = parser.parse_args()

    assert not (args.with_etherbone and args.eth_dynamic_ip)

    soc = BaseSoC(
        toolchain        = args.toolchain,
        revision         = args.revision,
        device           = args.device,
        sdram_device     = args.sdram_device,
        sdram_rate       = args.sdram_rate,
        sys_clk_freq     = args.sys_clk_freq,
        with_ethernet    = args.with_ethernet,
        with_etherbone   = args.with_etherbone,
        eth_ip           = args.eth_ip,
        remote_ip        = args.remote_ip,
        eth_dynamic_ip   = args.eth_dynamic_ip,
        with_spi_flash   = args.with_spi_flash,
        with_syzygy_gpio = args.with_syzygy_gpio,
        with_buttons     = args.with_buttons,
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
