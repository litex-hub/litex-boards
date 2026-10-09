#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) Greg Davill <greg.davill@gmail.com>
# Copyright (c) Lone Dynamics Corporation <info@lonedynamics.com>
#
# SPDX-License-Identifier: BSD-2-Clause
#


from migen import *

from litex.gen import *

from litex_boards.platforms import machdyne_kopflos


from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.soc.cores.clock import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.gpio import GPIOIn
from litex.soc.cores.usb_ohci import USBOHCI

from litex.soc.integration.soc import *
from litex.soc.integration.builder import *
from litex.soc.interconnect.csr_eventmanager import *

from litedram.modules import MT41K64M16, MT41K128M16, MT41K256M16, MT41K512M16
from litedram.phy import ECP5DDRPHY


from litex.soc.integration.soc import SoCRegion

# CRG ---------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, sdram_rate):
        self.rst        = Signal()
        self.cd_por     = ClockDomain()
        self.cd_sys     = ClockDomain()
        self.cd_sys2x   = ClockDomain()
        self.cd_sys2x_i = ClockDomain()
        self.cd_init    = ClockDomain()
        if sdram_rate == "1:4":
            self.cd_sys4x   = ClockDomain()
            self.cd_sys4x_i = ClockDomain()

        self.stop  = Signal()
        self.reset = Signal()

        # Clk / Rst
        clk48 = platform.request("clk48")

        # Power on reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += self.cd_por.clk.eq(clk48)
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # PLL
        sys2x_clk_ecsout = Signal()
        self.pll = pll = ECP5PLL()
        self.comb += pll.reset.eq(~por_done | self.rst)
        pll.register_clkin(clk48, 48e6)
        if sdram_rate == "1:2":
            # sys2x: DDR edge clock (ECLKBRIDGECS + ECLKSYNCB), sys = sys2x/2 (CLKDIVF).
            pll.create_clkout(self.cd_sys2x_i, 2*sys_clk_freq)
            pll.create_clkout(self.cd_init, 24e6)
            self.specials += [
                Instance("ECLKBRIDGECS",
                    i_CLK0   = self.cd_sys2x_i.clk,
                    i_SEL    = 0,
                    o_ECSOUT = sys2x_clk_ecsout),
                Instance("ECLKSYNCB",
                    i_ECLKI = sys2x_clk_ecsout,
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
            # through the second edge clock synchronizer/divider of the DDR side (bank 2) from a 2x sys
            # PLL output (same structural path as sys2x, both realigned by the PHY init stop/reset
            # sequence).
            eclksync1_bel, clkdiv1_bel = ("X72/Y25/ECLKSYNC1_BK2", "X72/Y25/CLKDIV1")
            pll.create_clkout(self.cd_sys4x_i, 4*sys_clk_freq)
            pll.create_clkout(self.cd_sys2x_i, 2*sys_clk_freq)
            pll.create_clkout(self.cd_init, 24e6)
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

        pll2 = ECP5PLL()
        self.pll2 = pll2
        pll2.register_clkin(clk48, 48e6)

        self.cd_usb_12 = ClockDomain()
        self.cd_usb    = ClockDomain()
        self.cd_usb_48 = ClockDomain()
        self.cd_usb_48 = self.cd_usb
        pll2.create_clkout(self.cd_usb, 48e6)
        pll2.create_clkout(self.cd_usb_12, 12e6)
        self.comb += pll2.reset.eq(~por_done)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    mem_map = {**SoCCore.mem_map, **{
        "usb_ohci":     0xc0000000,
    }}
    def __init__(self, revision="v0", device="12F", sdram_device="MT41K128M16", sdram_rate="1:2", sys_clk_freq=int(40e6), toolchain="trellis",
        with_led_chaser = True,
        with_usb_host   = False,
        with_ethernet   = False,
        eth_ip          = "192.168.1.50",
        remote_ip       = None,
        eth_dynamic_ip  = False,
        with_button     = False,
        **kwargs):

        platform = machdyne_kopflos.Platform(revision=revision, device=device ,toolchain=toolchain)

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, sdram_rate=sdram_rate)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Schoko", **kwargs)

        # DDR3L ----------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            available_sdram_modules = {
                "MT41K64M16":  MT41K64M16,
                "MT41K128M16": MT41K128M16,
                "MT41K256M16": MT41K256M16,
                "MT41K512M16": MT41K512M16,
            }
            sdram_module = available_sdram_modules.get(sdram_device)

            ddram_pads = platform.request("ddram")
            # 1:2: DDR3 at 2x sys. 1:4: DDR3 at 4x sys.
            if sdram_rate == "1:2":
                phy_cls = ECP5DDRPHY
            else:
                from litedram.phy.ecp5ddrphy import ecp5ddrphy_with_ratio
                phy_cls = ecp5ddrphy_with_ratio(2)
            self.ddrphy = phy_cls(
                pads         = ddram_pads,
                sys_clk_freq = sys_clk_freq,
                cmd_delay    = 0 if sys_clk_freq > 64e6 else 100)
            self.ddrphy.settings.rtt_nom = "disabled"
            self.comb += self.crg.stop.eq(self.ddrphy.init.stop)
            self.comb += self.crg.reset.eq(self.ddrphy.init.reset)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = sdram_module(sys_clk_freq, sdram_rate),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # USB Host ---------------------------------------------------------------------------------
        if with_usb_host:
            self.usb_ohci = USBOHCI(platform, platform.request("usb_host"), usb_clk_freq=int(48e6))
            self.bus.add_slave("usb_ohci_ctrl", self.usb_ohci.wb_ctrl, region=SoCRegion(origin=self.mem_map["usb_ohci"], size=0x100000, cached=False))
            dma_bus = getattr(self, "dma_bus", self.bus)
            dma_bus.add_master("usb_ohci_dma", master=self.usb_ohci.wb_dma)
            self.comb += self.cpu.interrupt[16].eq(self.usb_ohci.interrupt)

        if with_ethernet:
            from liteeth.phy.rmii import LiteEthPHYRMII
            self.ethphy = LiteEthPHYRMII(
                clock_pads = platform.request("eth_clocks"),
                pads = platform.request("eth"),
                with_hw_init_reset=True,
                refclk_cd=None)
            self.add_ethernet(phy=self.ethphy, dynamic_ip=eth_dynamic_ip, local_ip=eth_ip, remote_ip=remote_ip)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

        # Button ----------------------------------------------------------------------------------
        if with_button:
            self.button = GPIOIn(platform.request("user_btn"))

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser           import LiteXArgumentParser
    from litex_boards.extensions.pmod import add_pmod_args, add_pmods
    parser = LiteXArgumentParser(platform=machdyne_kopflos.Platform, description="LiteX SoC on Schoko")
    parser.add_target_argument("--sys-clk-freq",    default=40e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--revision",        default="v0",             help="Board Revision (v0).")
    parser.add_target_argument("--device",          default="12F",            help="ECP5 device (12F, 25F, 45F or 85F).")
    parser.add_target_argument("--cable",           default="dirtyJtag",      help="Specify an openFPGALoader cable.")
    parser.add_target_argument("--with-sdcard",     action="store_true",      help="Enable SDCard support.")
    parser.add_target_argument("--with-spi-sdcard", action="store_true",      help="Enable SPI-mode SDCard support.")
    parser.add_target_argument("--with-button",     action="store_true",      help="Enable User Button.")
    parser.add_target_argument("--with-usb-host",   action="store_true",      help="Enable USB host support.")
    parser.add_target_argument("--with-ethernet",   action="store_true",      help="Enable Ethernet support.")
    parser.add_target_argument("--eth-ip",          default="192.168.1.50",   help="Ethernet/Etherbone IP address.")
    parser.add_target_argument("--remote-ip",       default="192.168.1.100",  help="Remote IP address of TFTP server.")
    parser.add_target_argument("--eth-dynamic-ip",  action="store_true",      help="Enable dynamic Ethernet IP assignment.")
    parser.add_target_argument("--sdram-device",    default="MT41K128M16",    help="SDRAM device.")
    parser.add_target_argument("--sdram-rate",      default="1:2", choices=["1:2", "1:4"], help="SDRAM controller:DRAM clock ratio.")

    add_pmod_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        toolchain      = args.toolchain,
        revision       = args.revision,
        device         = args.device,
        sys_clk_freq   = int(float(args.sys_clk_freq)),
        sdram_device   = args.sdram_device,
        sdram_rate     = args.sdram_rate,
        with_usb_host  = args.with_usb_host,
        with_ethernet  = args.with_ethernet,
        eth_ip         = args.eth_ip,
        eth_dynamic_ip = args.eth_dynamic_ip,
        remote_ip      = args.remote_ip,
        with_button    = args.with_button,
        **parser.soc_argdict)
    add_pmods(soc, args.pmod)

    if args.with_sdcard:
        soc.add_sdcard()

    if args.with_spi_sdcard:
        soc.add_spi_sdcard()

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
