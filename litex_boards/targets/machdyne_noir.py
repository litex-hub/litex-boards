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

from litex_boards.platforms import machdyne_noir


from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.soc.cores.clock import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.pwm import PWM
from litex.soc.cores.usb_ohci import USBOHCI
from litex.soc.cores.video import VideoHDMIPHY

from litex.soc.integration.soc import *
from litex.soc.integration.builder import *

from litedram.modules import MT41K64M16, MT41K128M16, MT41K256M16, MT41K512M16
from litedram.phy import ECP5DDRPHY

from litex.soc.integration.soc import SoCRegion

# CRG ---------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, sdram_rate="1:2"):
        self.rst        = Signal()
        self.cd_por     = ClockDomain()
        self.cd_sys     = ClockDomain()
        self.cd_sys2x   = ClockDomain()
        self.cd_sys2x_i = ClockDomain()
        self.cd_init    = ClockDomain()
        self.cd_video   = ClockDomain()
        self.cd_video5x = ClockDomain()
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
            eclksync1_bel, clkdiv1_bel = ("X90/Y34/ECLKSYNC1_BK2", "X90/Y34/CLKDIV1")
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
        pll2.create_clkout(self.cd_video, 25e6)
        pll2.create_clkout(self.cd_video5x, 125e6)

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
    def __init__(self, revision="v0", device="45F", sdram_device="MT41K128M16", sdram_rate="1:2", sys_clk_freq=int(50e6), toolchain="trellis", with_led_chaser=True, with_usb_host=False, with_ethernet=False, with_audio_pwm=False, **kwargs):

        platform = machdyne_noir.Platform(revision=revision, device=device, toolchain=toolchain)

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, sdram_rate=sdram_rate)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Noir", **kwargs)

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

        # DDMI Framebuffer -------------------------------------------------------------------------------------
        self.videophy = VideoHDMIPHY(platform.request("ddmi"),
            clock_domain="video")
        self.add_video_framebuffer(phy=self.videophy, timings="640x480@60Hz",
            clock_domain="video", format="rgb565")

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

        # Audio PWM -------------------------------------------------------------------------------
        if with_audio_pwm:
            audio = platform.request("audio_pwm")
            self.audio_left  = PWM(pwm=audio.left,  with_csr=True)
            self.audio_right = PWM(pwm=audio.right, with_csr=True)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=machdyne_noir.Platform, description="LiteX SoC on Noir")
    parser.add_target_argument("--sys-clk-freq",    default=50e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--revision",        default="v0",             help="Board Revision (v0).")
    parser.add_target_argument("--device",          default="45F",            help="ECP5 device (25F, 45F or 85F).")
    parser.add_target_argument("--cable",           default="usb-blaster",    help="Specify an openFPGALoader cable.")
    parser.add_target_argument("--with-sdcard",     action="store_true",      help="Enable SDCard support.")
    parser.add_target_argument("--with-spi-sdcard", action="store_true",      help="Enable SPI-mode SDCard support.")
    parser.add_target_argument("--with-usb-host",   action="store_true",      help="Enable USB host support.")
    parser.add_target_argument("--with-audio-pwm",  action="store_true",      help="Enable Audio PWM output.")
    parser.add_target_argument("--with-ethernet",   action="store_true",      help="Enable Ethernet support.")
    parser.add_target_argument("--boot-from-flash", action="store_true",      help="Boot from flash MMOD.")
    parser.add_target_argument("--sdram-device",    default="MT41K128M16",    help="SDRAM device.")
    parser.add_target_argument("--sdram-rate",      default="1:2", choices=["1:2", "1:4"], help="SDRAM controller:DRAM clock ratio.")

    args = parser.parse_args()

    soc = BaseSoC(
        revision      = args.revision,
        device        = args.device,
        sys_clk_freq  = int(float(args.sys_clk_freq)),
        sdram_device  = args.sdram_device,
        sdram_rate    = args.sdram_rate,
        with_usb_host = args.with_usb_host,
        with_ethernet = args.with_ethernet,
        with_audio_pwm = args.with_audio_pwm,
        **parser.soc_argdict)

    if args.with_sdcard:
        soc.add_sdcard()

    if args.with_spi_sdcard:
        soc.add_spi_sdcard()

    builder = Builder(soc, **parser.builder_argdict)

    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer(cable=args.cable)
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
