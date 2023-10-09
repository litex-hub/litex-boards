#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2023 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2020 Paul Sajna <sajattack@gmail.com>
# Copyright (c) 2022 Thomas Watson <twatson52@icloud.com>
# SPDX-License-Identifier: BSD-2-Clause

# ./analog_pocket.py --sdram-rate=1:2 --uart-name=jtag_uart --build --load
# litex_term jtag --jtag-config=openocd_usb_blaster.cfg

from migen import *

from litex.gen import *

from litex_boards.platforms import analog_pocket

from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

from litex.build.io import DDROutput

from litex.soc.cores.clock import CycloneVPLL

from litedram.modules import AS4C32M16
from litedram.phy import GENSDRPHY, HalfRateGENSDRPHY

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, sdram_rate="1:1"):
        self.rst         = Signal()
        self.cd_sys      = ClockDomain()
        self.cd_video    = ClockDomain()
        self.cd_video_90 = ClockDomain()
        if sdram_rate == "1:2":
            self.cd_sys2x    = ClockDomain()
            self.cd_sys2x_ps = ClockDomain()
        else:
            self.cd_sys_ps = ClockDomain()

        # # #

        # Clk / Rst
        clk74 = platform.request("clk74a")

        # PLL
        self.pll = pll = CycloneVPLL()
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk74, 74.25e6)
        pll.create_clkout(self.cd_sys,    sys_clk_freq)
        if sdram_rate == "1:2":
            pll.create_clkout(self.cd_sys2x,    2*sys_clk_freq)
            pll.create_clkout(self.cd_sys2x_ps, 2*sys_clk_freq, phase=180)  # Idealy 90° but needs to be increased.
        else:
            pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_video,    25e6)
        pll.create_clkout(self.cd_video_90, 25e6, phase=90)

        # SDRAM clock
        sdram_clk = ClockSignal("sys2x_ps" if sdram_rate == "1:2" else "sys_ps")
        self.specials += DDROutput(1, 0, platform.request("sdram_clock"), sdram_clk)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=50e6, sdram_rate="1:1",
        with_video_terminal    = False,
        with_video_framebuffer = False,
        with_video_colorbars   = False,
        **kwargs):
        platform = analog_pocket.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, sdram_rate)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Analog Pocket", **kwargs)

        # SDR SDRAM --------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            sdrphy_cls = HalfRateGENSDRPHY if sdram_rate == "1:2" else GENSDRPHY
            self.sdrphy = sdrphy_cls(platform.request("sdram"), sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.sdrphy,
                module        = AS4C32M16(sys_clk_freq, sdram_rate),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Video ------------------------------------------------------------------------------------

        if with_video_colorbars or with_video_framebuffer or with_video_terminal:

            from litex.soc.interconnect import stream
            from litex.soc.cores.video import video_data_layout
            from litex.build.io import SDROutput, DDROutput

            class VideoDDRPHY(Module):
                def __init__(self, pads, clock_domain="sys"):
                    self.sink = sink = stream.Endpoint(video_data_layout)

                    # # #

                    # Always ack Sink, no backpressure.
                    self.comb += sink.ready.eq(1)

                    # Drive Clk.
                    self.specials += DDROutput(i1=1, i2=0, o=pads.clk, clk=ClockSignal(clock_domain+"_90"))

                    # Drive Controls.
                    self.specials += SDROutput(i=sink.de,     o=pads.de,    clk=ClockSignal(clock_domain))
                    self.specials += SDROutput(i=sink.hsync,  o=pads.hsync, clk=ClockSignal(clock_domain))
                    self.specials += SDROutput(i=sink.vsync,  o=pads.vsync, clk=ClockSignal(clock_domain))
                    self.specials += SDROutput(i=Constant(0), o=pads.skip,  clk=ClockSignal(clock_domain))

                    # Drive Datas.
                    data = Signal(24)
                    for i in range(8):
                        self.comb += data[ 0+i].eq(sink.b[i] & sink.de)
                        self.comb += data[ 8+i].eq(sink.g[i] & sink.de)
                        self.comb += data[16+i].eq(sink.r[i] & sink.de)
                    for i in range(12):
                        self.specials += DDROutput(
                            i1  = data[12 + i],
                            i2  = data[ 0 + i],
                            o   = pads.data[i],
                            clk = ClockSignal(clock_domain)
                        )

            self.videophy = VideoDDRPHY(platform.request("video"), clock_domain="video")
            if with_video_colorbars:
                self.add_video_colorbars(phy=self.videophy, timings="640x480@60Hz", clock_domain="video")
            if with_video_terminal:
                self.add_video_terminal(phy=self.videophy, timings="640x480@60Hz", clock_domain="video")
            if with_video_framebuffer:
                self.add_video_framebuffer(phy=self.videophy, timings="640x480@60Hz", clock_domain="video")

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=analog_pocket.Platform, description="LiteX SoC on Analog Pocket.")
    parser.add_target_argument("--sys-clk-freq", default=50e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--sdram-rate",   default="1:1",            help="SDRAM Rate (1:1 Full Rate or 1:2 Half Rate).")
    viopts = parser.target_group.add_mutually_exclusive_group()
    viopts.add_argument("--with-video-terminal",    action="store_true", help="Enable Video Terminal.")
    viopts.add_argument("--with-video-framebuffer", action="store_true", help="Enable Video Framebuffer.")
    viopts.add_argument("--with-video-colorbars",   action="store_true", help="Enable Video Colorbars.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq           = args.sys_clk_freq,
        sdram_rate             = args.sdram_rate,
        with_video_terminal    = args.with_video_terminal,
        with_video_framebuffer = args.with_video_framebuffer,
        with_video_colorbars   = args.with_video_colorbars,
        **parser.soc_argdict
    )
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram").replace(".sof", ".rbf"))

if __name__ == "__main__":
    main()
