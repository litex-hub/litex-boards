#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Greg Davill <greg.davill@gmail.com>
# Copyright (c) 2022 Goran Mahovlic <goran.mahovlic@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

# Build/Use:
# ./radiona_ulx4m_ld_v3.py  --uart-name=uart --uart-baudrate=115200 --sdram-device MT41K64M16 --csr-csv=csr.csv --build

# Note:
# 1) Ethernet PHY oscillator is not populated. The solution is to uses a GPIO from RPI Header (pin 37).
# 2) Ethernet is not working. No answer with mdio_dump command
# 3) DDR3 DM IOs, for PCB complexity, are not in the required group. The solution mentioned in
#    this issue must be used: https://github.com/enjoy-digital/litedram/issues/299


from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *
from litex_boards.platforms import radiona_ulx4m_ld_v2

from litex.soc.cores.clock import *
from litex.soc.integration.soc import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.video import VideoHDMIPHY

from litedram.common import PHYPadsReducer
from litedram.modules import MT41K64M16, MT41K128M16, MT41K256M16, MT41K512M16
from litedram.phy import ECP5DDRPHY

from liteeth.phy.ecp5rgmii import LiteEthPHYRGMII

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_video_pll=True, with_usb_pll=False, sdram_rate="1:2"):
        self.rst        = Signal()
        self.cd_init    = ClockDomain()
        self.cd_por     = ClockDomain(reset_less=True)
        self.cd_sys     = ClockDomain()
        self.cd_sys2x   = ClockDomain()
        self.cd_sys2x_i = ClockDomain(reset_less=True)
        if sdram_rate == "1:4":
            self.cd_sys4x   = ClockDomain()
            self.cd_sys4x_i = ClockDomain(reset_less=True)

        # # #

        self.stop  = Signal()
        self.reset = Signal()

        # Clk / Rst
        clk25 = platform.request("clk25")
        rst_n = platform.request("rst_n", 0)

        # Power on reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += self.cd_por.clk.eq(clk25)
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # Video PLL
        if with_video_pll:
            self.video_pll = video_pll = ECP5PLL()
            self.comb += video_pll.reset.eq(rst_n | self.rst)
            video_pll.register_clkin(clk25, 25e6)
            self.cd_hdmi   = ClockDomain()
            self.cd_hdmi5x = ClockDomain()
            video_pll.create_clkout(self.cd_hdmi,    25e6, margin=0)
            video_pll.create_clkout(self.cd_hdmi5x, 125e6, margin=0)

        # PLL
        self.pll = pll = ECP5PLL()
        self.comb += pll.reset.eq(~por_done | rst_n | self.rst)
        pll.register_clkin(clk25, 25e6)
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
                AsyncResetSynchronizer(self.cd_sys,    ~pll.locked | self.reset),
                AsyncResetSynchronizer(self.cd_sys2x,  ~pll.locked | self.reset),
            ]
        else:
            # sys4x: DDR edge clock (ECLKSYNCB), sys2x = sys4x/2 (CLKDIVF, PHY clock). sys
            # (controller clock) must be phase aligned with sys2x (DFI rate converter): generated
            # through the second edge clock synchronizer/divider of the DDR bank (bank 3) from a 2x sys
            # PLL output (same structural path as sys2x, both realigned by the PHY init stop/reset
            # sequence).
            eclksync1_bel, clkdiv1_bel = {
                "25F": ("X72/Y26/ECLKSYNC1_BK3", "X72/Y25/CLKDIV1"),
                "45F": ("X90/Y35/ECLKSYNC1_BK3", "X90/Y34/CLKDIV1"),
                "85F": ("X126/Y47/ECLKSYNC1_BK3", "X126/Y46/CLKDIV1"),
            }[platform.device.split("-")[1][:2] + "F"]
            pll.create_clkout(self.cd_sys4x_i, 4*sys_clk_freq)
            pll.create_clkout(self.cd_sys2x_i, 2*sys_clk_freq)
            pll.create_clkout(self.cd_init, 25e6)
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

        if with_usb_pll:
            self.cd_usb_12 = ClockDomain()
            self.cd_usb_48 = ClockDomain()
            usb_12         = Signal()
            self.specials += Instance("OSCG",
                p_DIV = 26, # ~12MHz
                o_OSC = usb_12
            )
            self.usb_pll = usb_pll = ECP5PLL()
            self.comb += usb_pll.reset.eq(~por_done | rst_n | self.rst)
            usb_pll.register_clkin(usb_12, 12e6)
            usb_pll.create_clkout(self.cd_usb_12, 12e6, margin=0)
            usb_pll.create_clkout(self.cd_usb_48, 48e6, margin=0)

        self.comb += platform.request("eth_phy_ref_clk").eq(clk25)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, revision="0.3", device="85F", toolchain="trellis", sys_clk_freq=int(75e6),
        sdram_device           = "MT41K512M16",
        sdram_rate             = "1:2",
        with_ethernet          = False,
        with_etherbone         = False,
        with_video_colorbars   = False,
        with_video_terminal    = False,
        with_video_framebuffer = False,
        eth_ip                 = "192.168.1.50",
        remote_ip              = "",
        eth_dynamic_ip         = False,
        with_spi_flash         = False,
        with_led_chaser        = True,
        **kwargs)       :
        platform = radiona_ulx4m_ld_v2.Platform(revision=revision, device=device, toolchain=toolchain)

        # CRG --------------------------------------------------------------------------------------
        uart_name      = kwargs.get("uart_name", "serial")
        with_video_pll = with_video_terminal or with_video_framebuffer or with_video_colorbars
        with_usb_pll   = uart_name == "usb_acm"
        self.submodules.crg = _CRG(platform, sys_clk_freq, with_video_pll, with_usb_pll, sdram_rate=sdram_rate)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on ULX4M-LD-V2", **kwargs)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            available_sdram_modules = {
                "MT41K64M16":  MT41K64M16,
                "MT41K128M16": MT41K128M16,
                "MT41K256M16": MT41K256M16,
                "MT41K512M16": MT41K512M16,
            }
            sdram_module = available_sdram_modules.get(sdram_device)
            l2_cache_size = kwargs.get("l2_size", 8192)
            if not l2_cache_size:
                raise ValueError("ULX4M-LD DDR3 requires an L2 cache when DM is disabled.")

            # 1:2: DDR3 at 2x sys. 1:4: DDR3 at 4x sys (DDR3-600 at 75MHz).
            if sdram_rate == "1:2":
                phy_cls = ECP5DDRPHY
            else:
                from litedram.phy.ecp5ddrphy import ecp5ddrphy_with_ratio
                phy_cls = ecp5ddrphy_with_ratio(2)
            self.submodules.ddrphy = phy_cls(
                pads         = PHYPadsReducer(platform.request("ddram"), [0, 1]),
                sys_clk_freq = sys_clk_freq,
                with_dm      = False,
            )
            self.comb += self.crg.stop.eq(self.ddrphy.init.stop)
            self.comb += self.crg.reset.eq(self.ddrphy.init.reset)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = sdram_module(sys_clk_freq, sdram_rate),
                l2_cache_size = l2_cache_size,
            )

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            self.submodules.ethphy = LiteEthPHYRGMII(
                clock_pads = self.platform.request("eth_clocks"),
                pads       = self.platform.request("eth"),
                rx_delay   = 0e-9, # KSZ9031RNX phy adds a 1.2ns RX delay
            )
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, ip_address=eth_ip, with_ethmac=with_ethernet)
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy, dynamic_ip=eth_dynamic_ip, local_ip=eth_ip, remote_ip=remote_ip, software_debug=False)

        # SPI Flash --------------------------------------------------------------------------------
        if with_spi_flash:
            from litespi.modules import IS25LP128
            from litespi.opcodes import SpiNorFlashOpCodes as Codes
            self.add_spi_flash(mode="4x", module=IS25LP128(Codes.READ_1_1_4))

        # Video ------------------------------------------------------------------------------------
        if with_video_terminal or with_video_framebuffer or with_video_colorbars:
            self.submodules.videophy = VideoHDMIPHY(platform.request("gpdi"), clock_domain="hdmi")
            if with_video_colorbars:
                self.add_video_colorbars(phy=self.videophy, timings="640x480@60Hz", clock_domain="hdmi")
            if with_video_terminal:
                self.add_video_terminal(phy=self.videophy, timings="640x480@75Hz", clock_domain="hdmi")
            if with_video_framebuffer:
                self.add_video_framebuffer(phy=self.videophy, timings="640x480@75Hz", clock_domain="hdmi")

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=radiona_ulx4m_ld_v2.Platform, description="LiteX SoC on ULX4M-LD-V2")
    parser.add_target_argument("--sys-clk-freq", default=75e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--revision",     default="0.3",            help="Board revision (0.3).")
    parser.add_target_argument("--device",       default="85F",            help="ECP5 device (25F, 45F, or 85F).")

    # RAM.
    parser.add_target_argument("--sdram-device", default="MT41K512M16",
        help="SDRAM device (MT41K64M16, MT41K128M16, MT41K256M16, or MT41K512M16).")
    parser.add_target_argument("--sdram-rate",   default="1:2", choices=["1:2", "1:4"], help="SDRAM controller:DRAM clock ratio.")

    # Ethernet.
    ethopts = parser.target_group.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",  action="store_true", help="Enable Ethernet support.")
    ethopts.add_argument("--with-etherbone", action="store_true", help="Enable Etherbone support.")
    parser.add_target_argument("--eth-ip", "--local-ip", dest="eth_ip", default="192.168.1.50", help="Ethernet/Etherbone IP address.")
    parser.add_target_argument("--remote-ip",      default="192.168.1.100", help="Remote IP address of TFTP server.")
    parser.add_target_argument("--eth-dynamic-ip", action="store_true",     help="Enable dynamic Ethernet IP assignment.")

    # SPI Flash.
    parser.add_target_argument("--with-spi-flash",      action="store_true",        help="Enable memory-mapped SPI flash.")
    sdopts = parser.target_group.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-sdcard", action="store_true", help="Enable SPI-mode SDCard support.")
    sdopts.add_argument("--with-sdcard",     action="store_true", help="Enable SDCard support.")

    # Video.
    viopts = parser.target_group.add_mutually_exclusive_group()
    viopts.add_argument("--with-video-colorbars",   action="store_true", help="Enable video color bars (HDMI).")
    viopts.add_argument("--with-video-terminal",    action="store_true", help="Enable Video Terminal (HDMI).")
    viopts.add_argument("--with-video-framebuffer", action="store_true", help="Enable Video Framebuffer (HDMI).")

    parser.set_defaults(uart_name="usb_acm")

    args = parser.parse_args()

    assert not (args.with_etherbone and args.eth_dynamic_ip)

    soc = BaseSoC(
        toolchain              = args.toolchain,
        revision               = args.revision,
        device                 = args.device,
        sdram_device           = args.sdram_device,
        sdram_rate             = args.sdram_rate,
        sys_clk_freq           = args.sys_clk_freq,
        with_ethernet          = args.with_ethernet,
        with_etherbone         = args.with_etherbone,
        eth_ip                 = args.eth_ip,
        remote_ip              = args.remote_ip,
        eth_dynamic_ip         = args.eth_dynamic_ip,
        with_spi_flash         = args.with_spi_flash,
        with_video_colorbars   = args.with_video_colorbars,
        with_video_terminal    = args.with_video_terminal,
        with_video_framebuffer = args.with_video_framebuffer,
        **parser.soc_argdict)

    if args.with_spi_sdcard:
        soc.add_spi_sdcard()
    if args.with_sdcard:
        soc.add_sdcard()

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
