#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019 Arnaud Durand <arnaud.durand@unifr.ch>
# Copyright (c) 2022 Martin Hubacek @hubmartin (Twitter)
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from litex_boards.platforms import lattice_ecp5_vip

from litex.soc.cores.clock import *
from litex.soc.integration.soc import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litedram.modules import MT41K64M16
from litedram.phy import ECP5DDRPHY
from litex.soc.cores.video import VideoVGAPHY
from litex.soc.cores.bitbang import I2CMaster

# CRG ----------------------------------------------------------------------------------------------

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
        clk100 = platform.request("clk100")
        rst_n  = platform.request("rst_n")

        # Power on reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += self.cd_por.clk.eq(clk100)
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # PLL
        self.pll = pll = ECP5PLL()
        self.comb += pll.reset.eq(~por_done | ~rst_n | self.rst)
        pll.register_clkin(clk100, 100e6)
        if sdram_rate == "1:2":
            # sys2x: DDR edge clock (ECLKSYNCB), sys = sys2x/2 (CLKDIVF).
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
        else:
            # sys4x: DDR edge clock (ECLKSYNCB), sys2x = sys4x/2 (CLKDIVF, PHY clock). sys
            # (controller clock) must be phase aligned with sys2x (DFI rate converter): generated
            # through the second edge clock synchronizer/divider of the DDR bank (bank 6) from a 2x sys
            # PLL output (same structural path as sys2x, both realigned by the PHY init stop/reset
            # sequence).
            eclksync1_bel, clkdiv1_bel = ("X0/Y47/ECLKSYNC1_BK6", "X0/Y46/CLKDIV1")
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

        # HDMI (1:4: from a second PLL, the DRAM PLL outputs are used and its internal feedback
        # must be kept on a dedicated output).
        self.cd_hdmi   = ClockDomain()
        hdmi_pll = pll
        if sdram_rate == "1:4":
            self.hdmi_pll = hdmi_pll = ECP5PLL()
            self.comb += hdmi_pll.reset.eq(~por_done | ~rst_n | self.rst)
            hdmi_pll.register_clkin(clk100, 100e6)
        #hdmi_pll.create_clkout(self.cd_hdmi, 148.5e6) # for terminal "1920x1080@60Hz"
        #hdmi_pll.create_clkout(self.cd_hdmi, 160e6) # for terminal "1920x1080@60Hz"
        #hdmi_pll.create_clkout(self.cd_hdmi, 80e6) # for terminal "1920x1080@30Hz"
        hdmi_pll.create_clkout(self.cd_hdmi, 40e6) # for terminal "800x600@60Hz"

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=50e6, toolchain="trellis",
        sdram_rate             = "1:2",
        with_led_chaser        = True,
        with_video_terminal    = True,
        with_video_framebuffer = False,
        **kwargs):
        platform = lattice_ecp5_vip.Platform(toolchain=toolchain)

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, sdram_rate=sdram_rate)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on ECP5 Evaluation Board", **kwargs)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        # 1:2: DDR3 at 2x sys. 1:4: DDR3 at 4x sys.
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
            module        = MT41K64M16(sys_clk_freq, sdram_rate), # Not entirely MT41J64M16 but similar and works(c)
            l2_cache_size = kwargs.get("l2_size", 8192),
        )

        # Video ------------------------------------------------------------------------------------
        if with_video_terminal or with_video_framebuffer:
            pads = platform.request("hdmi")
            self.videophy = VideoVGAPHY(pads, clock_domain="hdmi")
            self.videoi2c = I2CMaster(pads)

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
            self.leds = LedChaser(
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
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=lattice_ecp5_vip.Platform, description="LiteX SoC on ECP5 Evaluation Board.")
    parser.add_target_argument("--sys-clk-freq",        default=60e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--sdram-rate",          default="1:2", choices=["1:2", "1:4"], help="SDRAM controller:DRAM clock ratio.")
    args = parser.parse_args()

    soc = BaseSoC(
        toolchain    = args.toolchain,
        sys_clk_freq = args.sys_clk_freq,
        sdram_rate   = args.sdram_rate,
        **parser.soc_argdict)
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
