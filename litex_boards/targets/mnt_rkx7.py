#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2022 Lukas F. Hartmann, MNT Research GmbH <lukas@mntre.com>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from migen.fhdl.specials import Tristate

from litex.gen import *

from litex_boards.platforms import mnt_rkx7


from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.interconnect.csr import *
from litex.soc.interconnect.axi import *
from litex.soc.interconnect.wishbone import *

from litex.soc.cores.clock import *
from litex.soc.cores.bitbang import I2CMaster
from litex.soc.cores.gpio import GPIOOut
from litex.soc.cores.video import VideoDVIPHY
from litex.soc.cores.usb_ohci import USBOHCI

from litedram.modules import IS43TR16512B
from litedram.phy import s7ddrphy

from liteeth.phy.s7rgmii import LiteEthPHYRGMII

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst       = Signal()
        self.cd_sys    = ClockDomain()
        self.cd_sys4x  = ClockDomain()
        self.cd_idelay = ClockDomain()
        self.cd_dvi    = ClockDomain(reset_less=True)
        self.cd_usb    = ClockDomain()
        self.cd_hdmi   = ClockDomain(reset_less=True)

        clkin = platform.request("clk100")

        self.pll = pll = S7MMCM(speedgrade=-2)
        self.comb += pll.reset.eq(self.rst)
        # Main clock input (100MHz)
        pll.register_clkin(clkin, 100e6)
        pll.create_clkout(self.cd_sys,    sys_clk_freq)
        pll.create_clkout(self.cd_sys4x,  4*sys_clk_freq)
        pll.create_clkout(self.cd_idelay, 200e6)
        # Ignore sys_clk to pll.clkin path created by SoC's rst.
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin)

        # USB clock
        pll.create_clkout(self.cd_usb, int(48e6))

        # HDMI 640x480 clock
        pll.create_clkout(self.cd_hdmi, int(25e6))

        self.pll2 = pll2 = S7MMCM(speedgrade=-2)
        self.comb += pll2.reset.eq(self.rst)
        pll2.register_clkin(clkin, 100e6)
        # DVI pixel clock
        pll2.create_clkout(self.cd_dvi, 80e6) # display wants 162e6, but we can underclock
        platform.add_false_path_constraints(self.cd_sys.clk, pll2.clkin)

        self.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    mem_map = {**SoCCore.mem_map, **{
        # FIXME: ends up as 0x7f000000 in linux
        "video_framebuffer": 0x3f000000,
        "usb_ohci"         : 0xc0000000,
    }}

    def __init__(self, sys_clk_freq=100e6,
        with_ethernet  = True,
        with_etherbone = False,
        with_spi_flash = True,
        with_usb_host  = True,
        with_analyzer  = False,
        **kwargs):
        platform = mnt_rkx7.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on MNT-RKX7", **kwargs)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.ddrphy = s7ddrphy.K7DDRPHY(platform.request("ddram"),
                memtype      = "DDR3",
                nphases      = 4,
                sys_clk_freq = sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = IS43TR16512B(sys_clk_freq, "1:4"),
                size          = 0x40000000,
                l2_cache_size = kwargs.get("l2_size", 8192), # TBD: is L2 really necessary?
            )

        # SPI Flash --------------------------------------------------------------------------------
        if with_spi_flash:
            from litespi.modules import W25Q128JV
            from litespi.opcodes import SpiNorFlashOpCodes as Codes
            self.add_spi_flash(mode="4x", module=W25Q128JV(Codes.READ_1_1_4), rate="1:1", with_master=True)

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            self.ethphy = LiteEthPHYRGMII(
                clock_pads = self.platform.request("eth_clocks"),
                pads       = self.platform.request("eth"))
            platform.add_platform_command("set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets {{main_ethphy_eth_rx_clk_ibuf}}]")
            platform.add_platform_command("set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets {{soclinux_ethphy_eth_rx_clk_ibuf}}]")
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy, dynamic_ip=True, software_debug=False)
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy)

        # GPIO -------------------------------------------------------------------------------------
        # Controllable as faux "leds"
        # These are reset pins of various chips
        # We toggle them in LiteX BIOS
        reset_signals = platform.request("resets")
        self.comb += reset_signals.eq(Signal(6, reset=0b111111))

        gpio_signals = platform.request("gpio")
        self.leds = GPIOOut(gpio_signals)

        # Additional I2C Ports ---------------------------------------------------------------------
        self.i2c0 = I2CMaster(platform.request("i2c", 0))
        self.i2c1 = I2CMaster(platform.request("i2c", 1))
        self.i2c2 = I2CMaster(platform.request("i2c", 2))

        # JTAG -------------------------------------------------------------------------------------
        #self.add_jtagbone()

        # Backlight --------------------------------------------------------------------------------
        # Motherboard display connector backlight, currently unused (the new backlight signals
        # are on the 50pin RGB->eDP connector)
        backlight = platform.request("backlight")
        self.comb += backlight.en.eq(Signal(reset=1))
        self.comb += backlight.pwm.eq(Signal(reset=1))

        # eDP --------------------------------------------------------------------------------------
        video_timings = ("1920x1080@rkx7", {
            "pix_clk"       : 162e6,
            "h_active"      : 1920,
            "h_blanking"    : 159, # off by one in vtg
            "h_sync_offset" : 40,
            "h_sync_width"  : 40,
            "v_active"      : 1080,
            "v_blanking"    : 32,
            "v_sync_offset" : 4,
            "v_sync_width"  : 4,
        })
        self.videophy = VideoDVIPHY(platform.request("edp"), clock_domain="dvi")
        self.add_video_framebuffer(phy=self.videophy, timings=video_timings, clock_domain="dvi")

        # HDMI -------------------------------------------------------------------------------------
        # Untested: 2x framebuffers in parallel
        self.videophy_hdmi = VideoDVIPHY(platform.request("hdmi"), clock_domain="hdmi")
        self.add_video_terminal(phy=self.videophy_hdmi, timings="640x480@75Hz", clock_domain="hdmi")

        # USB Host ---------------------------------------------------------------------------------
        if with_usb_host:
            self.usb_ohci = USBOHCI(platform, platform.request("usb"))
            self.bus.add_slave("usb_ohci_ctrl", self.usb_ohci.wb_ctrl, region=SoCRegion(origin=self.mem_map["usb_ohci"], size=0x100000, cached=False))
            dma_bus = getattr(self, "dma_bus", self.bus)
            dma_bus.add_master("usb_ohci_dma", master=self.usb_ohci.wb_dma)
            self.comb += self.cpu.interrupt[16].eq(self.usb_ohci.interrupt)

        # LiteScope Analyzer -----------------------------------------------------------------------
        if with_analyzer:
            from litescope import LiteScopeAnalyzer
            self.add_uartbone(uart_name="debug_serial")
            analyzer_signals = [
                ulpi_data.din,
                utmi.linestate,
                utmi.txvalid,
                utmi.rxerror,
                utmi.rxvalid,
                usb_ulpi.dir,
                usb_ulpi.stp,
                usb_ulpi.nxt,
                usbh_dbg_state,
                ulpi_dbg_state,
                usb_host_intr,
                usb_host_dbg_intr,
            ]
            self.analyzer = LiteScopeAnalyzer(analyzer_signals,
                depth        = 256,
                clock_domain = "ulpi",
                csr_csv      = "analyzer.csv"
            )

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=mnt_rkx7.Platform, description="LiteX SoC on MNT-RKX7.")
    parser.add_target_argument("--sys-clk-freq",    default=100e6,  type=float,         help="System clock frequency.")
    parser.add_target_argument("--with-spi-flash",  action="store_true", default=True,  help="Enable SPI Flash (MMAPed).")
    parser.add_target_argument("--with-usb-host",   action="store_true", default=True, help="Enable USB host support.")
    sdopts = parser.target_group.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-sdcard",     action="store_true",               help="Enable SPI-mode SDCard support.")
    sdopts.add_argument("--with-sdcard",         action="store_true", default=True, help="Enable SDCard support.")
    ethopts = parser.target_group.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",  action="store_true", default=True, help="Enable Ethernet support.")
    ethopts.add_argument("--with-etherbone", action="store_true",               help="Enable Etherbone support.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq   = args.sys_clk_freq,
        with_ethernet  = args.with_ethernet,
        with_etherbone = args.with_etherbone,
        with_spi_flash = args.with_spi_flash,
        with_usb_host  = args.with_usb_host,
        **parser.soc_argdict
    )
    if args.with_spi_sdcard:
        soc.add_spi_sdcard()
    if args.with_sdcard:
        soc.add_sdcard()

    args.csr_csv="csr.csv"

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
