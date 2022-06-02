#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019 Arnaud Durand <arnaud.durand@unifr.ch>
# Copyright (c) 2022 Martin Hubacek @hubmartin (Twitter)
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex_boards.platforms import lattice_ecp5_vip

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.cores.led import LedChaser

from litedram.modules import MT41K64M16
from litedram.phy import ECP5DDRPHY
from litex.soc.cores.video import VideoVGAPHY
from litex.soc.cores.bitbang import I2CMaster


# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_init    = ClockDomain()
        self.clock_domains.cd_por     = ClockDomain()
        self.clock_domains.cd_sys     = ClockDomain()
        self.clock_domains.cd_sys2x   = ClockDomain()
        self.clock_domains.cd_sys2x_i = ClockDomain()

        # # #
        self.stop  = Signal()
        self.reset = Signal()

        # Clk / Rst
        clk100 = platform.request("clk100")
        rst_n  = platform.request("rst_n")

        # Power on reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += self.cd_por.clk.eq(clk100)
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # PLL
        self.submodules.pll = pll = ECP5PLL()
        self.comb += pll.reset.eq(~por_done | ~rst_n | self.rst)
        pll.register_clkin(clk100, 100e6)
        pll.create_clkout(self.cd_sys2x_i, 2*sys_clk_freq)
        pll.create_clkout(self.cd_init, 25e6)
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

        # HDMI
        self.clock_domains.cd_hdmi   = ClockDomain()
        #pll.create_clkout(self.cd_hdmi, 148.5e6) # for terminal "1920x1080@60Hz"
        #pll.create_clkout(self.cd_hdmi, 160e6) # for terminal "1920x1080@60Hz"
        #pll.create_clkout(self.cd_hdmi, 80e6) # for terminal "1920x1080@30Hz"
        pll.create_clkout(self.cd_hdmi, 40e6) # for terminal "800x600@60Hz"


# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(50e6), toolchain="trellis",
        with_led_chaser        = True,
        with_video_terminal    = True,
        with_video_framebuffer = False,
        **kwargs):
        platform = lattice_ecp5_vip.Platform(toolchain=toolchain)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on ECP5 Evaluation Board", **kwargs)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        self.submodules.ddrphy = ECP5DDRPHY(
            platform.request("ddram"),
            sys_clk_freq=sys_clk_freq)
        self.comb += self.crg.stop.eq(self.ddrphy.init.stop)
        self.comb += self.crg.reset.eq(self.ddrphy.init.reset)
        self.add_sdram("sdram",
            phy           = self.ddrphy,
            module        = MT41K64M16(sys_clk_freq, "1:2"), # Not entirely MT41J64M16 but similar and works(c)
            l2_cache_size = kwargs.get("l2_size", 8192),
        )

        # Video ------------------------------------------------------------------------------------
        if with_video_terminal or with_video_framebuffer:
            pads = platform.request("hdmi")
            self.submodules.videophy = VideoVGAPHY(pads, clock_domain="hdmi")
            self.submodules.videoi2c = I2CMaster(pads)

            # # 1920x1080@60Hz
            # pixel_clock_hz = 160e6
            # framerate_hz = 60
            # pixels_horizontal = 2200
            # pixels_vertical = 1125

            # 800x600@60Hz
            pixel_clock_hz = 40e6
            framerate_hz = 60
            pixels_horizontal = 1056
            pixels_vertical = 628

            # # 1920x1080@30Hz
            # pixel_clock_hz = 80e6
            # framerate_hz = 30
            # pixels_horizontal = 2640
            # pixels_vertical = 1125

            self.videoi2c.add_init(addr=0x3B, init=[
                (0xc7, 0x00), # HDMI configuration
                (0xc7, 0x00), # Write twice, the first transfer fails for some reason

                (0x1e, 0x00), # Power up transmitter
                (0x08, 0x60), # Input Bus/Pixel Repetition (default)

                (0x00, int((pixel_clock_hz/1e4) %256)), # Pixel clock in MHz * 100
                (0x01, int((pixel_clock_hz/1e4)//256)), # 

                (0x02, int((framerate_hz*100) %256)), # Framerate * 100
                (0x03, int((framerate_hz*100)//256)), #             

                (0x04, int((pixels_horizontal) %256)), # Pixels horizontal
                (0x05, int((pixels_horizontal)//256)), #  

                (0x06, int((pixels_vertical) %256)), # Pixels vertical
                (0x07, int((pixels_vertical)//256)), #

                (0x1a, 0x00) # end

            ])
            if with_video_terminal:
                #self.add_video_terminal(phy=self.videophy, timings="1920x1080@60Hz", clock_domain="hdmi")
                #self.add_video_terminal(phy=self.videophy, timings="1920x1080@30Hz", clock_domain="hdmi")
                self.add_video_terminal(phy=self.videophy, timings="800x600@60Hz", clock_domain="hdmi")
            if with_video_framebuffer:
                #self.add_video_framebuffer(phy=self.videophy, timings="800x600@60Hz", clock_domain="hdmi")
                self.add_video_framebuffer(phy=self.videophy, timings="640x480@60Hz", clock_domain="hdmi")
                
        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

        # Running code from SPI flash had some side effects on BIOS with enabled DDR3 memory
        # So I reverted to the FPGA BRAM for BIOS.

        # # SPI Flash --------------------------------------------------------------------------------
        # from litespi.modules import MX25L12835F
        # from litespi.opcodes import SpiNorFlashOpCodes as Codes
        # self.add_spi_flash(mode="1x", module=MX25L12835F(Codes.READ_1_1_1), with_master=False)

        # # Add ROM linker region --------------------------------------------------------------------
        # self.bus.add_region("rom", SoCRegion(
        #     origin = self.bus.regions["spiflash"].origin + bios_flash_offset,
        #     size   = (16-4)*1024*1024,
        #     linker = True)
        # )

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on ECP5 Evaluation Board")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",        action="store_true", help="Build design")
    target_group.add_argument("--load",         action="store_true", help="Load bitstream")
    target_group.add_argument("--toolchain",    default="trellis",   help="FPGA toolchain: trellis (default) or diamond")
    target_group.add_argument("--sys-clk-freq", default=60e6,        help="System clock frequency (default: 60MHz)")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        toolchain    = args.toolchain,
        sys_clk_freq = int(float(args.sys_clk_freq)),
        **soc_core_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    if args.build:
        builder.build()

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram", ext=".svf")) # FIXME

if __name__ == "__main__":
    main()
