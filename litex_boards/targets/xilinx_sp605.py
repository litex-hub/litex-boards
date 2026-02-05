#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 Arif Darmawan <arif.pens@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

import argparse

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *
from litex.build.io import DDROutput

from litex_boards.platforms import xilinx_sp605

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.video import *
from litex.soc.cores.clock import S6PLL
from litex.soc.cores.led import LedChaser

from litedram.modules import MT41K64M16
from litedram.phy import s6ddrphy, GENSDRPHY
from litex.soc.cores.bitbang import I2CMaster

kB = 1024
mB = 1024*kB

XTAL_VAL = 27e6

# CH7301 PHY ----------------------------------------------------------------------------------------------

class VideoCH7301phy(LiteXModule):
    def __init__(self, pads, clock_domain="sys"):
        self.sink = sink = stream.Endpoint(video_data_layout)

        # Always ack Sink, no backpressure.
        self.comb += sink.ready.eq(1)

        # Drive differential clock
        if hasattr(pads, "clk_p") and hasattr(pads, "clk_n"):
            self.specials += DDROutput(i1=1, i2=0, o=pads.clk_p, clk=ClockSignal(clock_domain))
            self.specials += DDROutput(i1=0, i2=1, o=pads.clk_n, clk=ClockSignal(clock_domain))

        # Drive Controls.
        if hasattr(pads, "de"):
            self.specials += SDROutput(i=sink.de, o=pads.de, clk=ClockSignal(clock_domain))
        if hasattr(pads, "hsync_n") and hasattr(pads, "vsync_n"):
            self.specials += SDROutput(i=~sink.hsync, o=pads.hsync_n, clk=ClockSignal(clock_domain))
            self.specials += SDROutput(i=~sink.vsync, o=pads.vsync_n, clk=ClockSignal(clock_domain))
        else:
            self.specials += SDROutput(i=sink.hsync,  o=pads.hsync,   clk=ClockSignal(clock_domain))
            self.specials += SDROutput(i=sink.vsync,  o=pads.vsync,   clk=ClockSignal(clock_domain))

        # Drive Datas.
        dvi_data_a = Signal(12, name="dvi_data_a")
        dvi_data_b = Signal(12, name="dvi_data_b")
        dvi_data_a_delay = Signal(12, name="dvi_data_a_delay")
        dvi_data_b_delay = Signal(12, name="dvi_data_b_delay")
        # Build the two DDR data words
        self.comb += [
            dvi_data_a.eq(Cat(sink.b, sink.g[0:4])),   # {g[3:0], b[7:0]}
            dvi_data_b.eq(Cat(sink.g[4:8], sink.r))    # {r[7:0], g[7:4]}
        ]

        # fix last pixel not shown
        self.specials += [
            MultiReg(dvi_data_a, dvi_data_a_delay, odomain=clock_domain),
            MultiReg(dvi_data_b, dvi_data_b_delay, odomain=clock_domain)
        ]

        for i in range(12):
            self.specials += DDROutput(i1=dvi_data_a_delay[i], i2=dvi_data_b_delay[i], o=pads.d[i], clk=ClockSignal(clock_domain))


# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        # Clock domains for the system (soft CPU and related components run at).
        self.cd_sys   = ClockDomain()
        self.cd_sys2x = ClockDomain()

        # Clo the DDR interface.
        self.cd_sdram_half      = ClockDomain()
        self.cd_sdram_full_wr   = ClockDomain()
        self.cd_sdram_full_rd   = ClockDomain()
        self.unbuf_sdram_full   = ClockDomain()
        self.unbuf_sdram_half_a = ClockDomain()
        self.unbuf_sdram_half_b = ClockDomain()

        # DVI clock domain
        self.cd_dvi = ClockDomain()
        self.cd_dvi90 = ClockDomain()

        # PLL signals
        clk27 = platform.request("clk27")
        self.pll = pll = S6PLL(speedgrade=-3)
        pll.register_clkin(clk27, XTAL_VAL)
        pll.create_clkout(self.unbuf_sdram_full, sys_clk_freq*8, with_reset=False, buf=None)
        pll.create_clkout(self.unbuf_sdram_half_a, sys_clk_freq*4, phase=230, with_reset=False, buf=None)
        pll.create_clkout(self.unbuf_sdram_half_b, sys_clk_freq*4, phase=210, with_reset=False, buf=None)
        pll.create_clkout(self.cd_sys2x, sys_clk_freq*2, with_reset=False)
        pll.create_clkout(self.cd_sys, sys_clk_freq, with_reset=False)

        # power on reset?
        self.reset = Signal()
        reset = platform.request("cpu_reset") | self.reset
        self.comb += pll.reset.eq(reset)
        self.clock_domains.cd_por = ClockDomain()
        por = Signal(max=1 << 11, reset=(1 << 11) - 1)
        self.sync.por += If(por != 0, por.eq(por - 1))
        self.specials += AsyncResetSynchronizer(self.cd_por, reset)

        # System clock
        self.comb += self.cd_por.clk.eq(self.cd_sys.clk)
        self.specials += AsyncResetSynchronizer(self.cd_sys, ~pll.locked | (por > 0))
        self.specials += AsyncResetSynchronizer(self.cd_sys2x, ~pll.locked | (por > 0))

        # SDRAM clocks
        # ------------------------------------------------------------------------------
        self.clk8x_wr_strb = Signal()
        self.clk8x_rd_strb = Signal()

        # sdram_full
        self.specials += Instance("BUFPLL",
                                  p_DIVIDE=4,
                                  i_PLLIN=self.unbuf_sdram_full.clk, i_GCLK=self.cd_sys2x.clk,
                                  i_LOCKED=pll.locked,
                                  o_IOCLK=self.cd_sdram_full_wr.clk,
                                  o_SERDESSTROBE=self.clk8x_wr_strb
                                  )
        self.comb += [
            self.cd_sdram_full_rd.clk.eq(self.cd_sdram_full_wr.clk),
            self.clk8x_rd_strb.eq(self.clk8x_wr_strb),
        ]

        # sdram_half
        self.specials += Instance("BUFG",
                                  i_I=self.unbuf_sdram_half_a.clk, 
                                  o_O=self.cd_sdram_half.clk
                                  )
        clk_sdram_half_shifted = Signal()
        self.specials += Instance("BUFG", 
                                  i_I=self.unbuf_sdram_half_b.clk, 
                                  o_O=clk_sdram_half_shifted
                                  )

        # sdram differential clock output
        output_clk = Signal()
        clk = platform.request("ddram_clock")
        self.specials += DDROutput(1, 0, output_clk, clk_sdram_half_shifted)
        self.specials += Instance("OBUFDS", i_I=output_clk, o_O=clk.p, o_OB=clk.n)

        # DVI clock
        self.pll2 = pll2 = S6PLL(speedgrade=-3)
        pll2.register_clkin(clk27, XTAL_VAL)
        pll2.create_clkout(self.cd_dvi, 148.5e6, with_reset=False)


# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=54e6,
        with_led_chaser        = True,
        with_video_colorbars   = False,
        with_video_framebuffer = False,
        with_video_terminal    = False,
        **kwargs):
        platform = xilinx_sp605.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on SPARTAN6", **kwargs)

        # SDR DDRAM --------------------------------------------------------------------------------
        self.ddrphy = s6ddrphy.S6QuarterRateDDRPHY(
            pads                = platform.request("ddram"),
            rd_bitslip          = 0,
            wr_bitslip          = 4,
            dqs_ddr_alignment   = "C0" 
        )

        self.comb += [
            self.ddrphy.clk8x_wr_strb.eq(self.crg.clk8x_wr_strb),
            self.ddrphy.clk8x_rd_strb.eq(self.crg.clk8x_rd_strb),
        ]

        self.add_sdram(
            name    = "sdram",
            phy     = self.ddrphy,
            module  = MT41K64M16(sys_clk_freq, "1:4"),
        )

        # Leds -------------------------------------------------------------------------------------
        self.leds = LedChaser(
            pads         = platform.request_all("user_led"),
            sys_clk_freq = sys_clk_freq)

        # Video Terminal ---------------------------------------------------------------------------
        if with_video_colorbars or with_video_framebuffer or with_video_terminal:
            pads = platform.request("dvi")
            self.videophy = VideoCH7301phy(pads, clock_domain="dvi")
            self.videoi2c = I2CMaster(pads)

            self.videoi2c.add_init(addr=0x76, init=[
                (0x49, 0xC0), 
                (0x21, 0x09), 

                # if under 65 Mhz
                # (0x33, 0x08), 
                # (0x34, 0x16), 
                # (0x36, 0x60)

                # 65 Mhz and above
                (0x33, 0x06), 
                (0x34, 0x26), 
                (0x36, 0xA0)
            ])
            if with_video_colorbars:
                self.add_video_colorbars(phy=self.videophy, timings="1920x1080@60Hz", clock_domain="dvi")
            if with_video_terminal:
                self.add_video_terminal(phy=self.videophy, timings="1920x1080@60Hz", clock_domain="dvi")
            if with_video_framebuffer:
                self.add_video_framebuffer(phy=self.videophy, timings="1920x1080@60Hz", clock_domain="dvi")

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=xilinx_sp605.Platform, description="LiteX SoC on Papilio Pro.")
    parser.add_target_argument("--sys-clk-freq",        default=54e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-video-terminal",    action="store_true",       help="Enable Video Terminal (DVI).")
    parser.add_target_argument("--with-video-framebuffer", action="store_true",       help="Enable Video Framebuffer (DVI).")
    parser.add_target_argument("--with-video-colorbars",   action="store_true",       help="Enable Video Colorbars (DVI).")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq           = args.sys_clk_freq,
        with_video_colorbars   = args.with_video_colorbars,
        with_video_terminal    = args.with_video_terminal,
        with_video_framebuffer = args.with_video_framebuffer,
        **parser.soc_argdict
    )

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
