#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# SPDX-License-Identifier: BSD-2-Clause

from pathlib import Path
from types import SimpleNamespace

from migen import Cat, ClockDomain, ClockSignal, Signal

from litex.build.io import DDROutput
from litex.gen import LiteXModule

from litex_boards.platforms import terasic_c5g

from litex.soc.cores.bitbang import I2CMaster
from litex.soc.cores.clock import CycloneVPLL
from litex.soc.cores.gpio import GPIOIn
from litex.soc.cores.led import LedChaser
from litex.soc.cores.video import VideoDVIPHY, video_timings
from litex.soc.integration.builder import Builder
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.soc_core import SoCCore

from litex_boards.targets.terasic_c5g_memory import C5GLPDDR2, C5GSRAM, generate_lpddr2_ip

_hdmi_timing = "1280x720@60Hz"

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_lpddr2, with_video_terminal):
        self.rst    = Signal()
        self.cd_sys = ClockDomain("sys")

        self.pll = pll = CycloneVPLL(speedgrade="-C7")
        self.reset_n = platform.request("cpu_reset_n")
        self.ref_clk = platform.request("clk50")
        self.comb += pll.reset.eq(self.rst | ~self.reset_n)
        # Keep the PLL at R20 available for the LPDDR2 hard controller.
        pll.register_clkin(platform.request("clk50", 1) if with_lpddr2 else self.ref_clk, 50e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)

        if with_video_terminal:
            # The UART mirror crosses into the independent pixel domain through an async FIFO.
            sys_ref = "clk501" if with_lpddr2 else "clk50"
            platform.toolchain.additional_sdc_commands.append(
                "set_clock_groups -asynchronous "
                f"-group [get_clocks {{{sys_ref} altpll:ALTPLL|*}}] "
                "-group [get_clocks {clk502 altpll:ALTPLL_1|*}]"
            )
            self.cd_hdmi = ClockDomain("hdmi")
            self.hdmi_pll = hdmi_pll = CycloneVPLL(speedgrade="-C7")
            self.comb += hdmi_pll.reset.eq(self.rst | ~self.reset_n)
            hdmi_pll.register_clkin(platform.request("clk50", 2), 50e6)
            hdmi_pll.create_clkout(self.cd_hdmi, video_timings[_hdmi_timing]["pix_clk"], margin=0)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=50e6, with_led_chaser=True, with_buttons=False, with_switches=False,
        with_sram=False, with_lpddr2=False, with_video_terminal=False, **kwargs):
        platform = terasic_c5g.Platform()

        self.crg = _CRG(platform, sys_clk_freq, with_lpddr2, with_video_terminal)

        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Terasic C5G", **kwargs)

        if with_sram:
            self.ext_sram = C5GSRAM(platform.request("sram"), sys_clk_freq)
            self.bus.add_slave("ext_sram", self.ext_sram.bus,
                SoCRegion(origin=0x80000000, size=self.ext_sram.size, cached=False), strip_origin=True)
        if with_lpddr2:
            self.lpddr2 = C5GLPDDR2(platform, self.crg.ref_clk, self.crg.reset_n)
            self.bus.add_slave("lpddr2", self.lpddr2.bus,
                SoCRegion(origin=0xa0000000, size=self.lpddr2.size, cached=False), strip_origin=True)

        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq,
            )
        if with_buttons:
            self.buttons = GPIOIn(~Cat(platform.request_all("user_btn")))
        if with_switches:
            self.switches = GPIOIn(Cat(platform.request_all("user_sw")))

        if with_video_terminal:
            self.i2c = I2CMaster(platform.request("i2c"))
            # ADV7513, RGB888 input ID 0 with separate sync and data enable.
            # Use a fixed video mode so the transmitter can start before a sink is plugged in.
            self.i2c.add_init(0x39, [
                (0xd6, 0xc0), # Keep configuration across hot-plug events.
                (0x41, 0x10), # Power up.
                (0x98, 0x03), (0x9a, 0xe0), (0x9c, 0x30), (0x9d, 0x61),
                (0xa2, 0xa4), (0xa3, 0xa4), (0xe0, 0xd0), (0xf9, 0x00), # Required fixed settings.
                (0x15, 0x00), (0x16, 0x30), # RGB, 8 bits per component.
                (0x18, 0x46), # Disable color-space conversion.
                (0xaf, 0x16), # HDMI mode, HDCP disabled.
            ])
            pads = platform.request("hdmi")
            rgb = SimpleNamespace(r=pads.d[16:24], g=pads.d[8:16], b=pads.d[:8],
                de=pads.de, hsync=pads.hsync, vsync=pads.vsync)
            self.videophy = VideoDVIPHY(rgb, clock_domain="hdmi")
            # Forward the inverted pixel clock so the transmitter samples
            # midway through the cycle after the registered data changes.
            self.specials += DDROutput(i1=0, i2=1, o=pads.clk, clk=ClockSignal("hdmi"))
            self.add_video_terminal(phy=self.videophy, timings=_hdmi_timing, clock_domain="hdmi")

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=terasic_c5g.Platform, description="LiteX SoC on Terasic C5G.")
    parser.add_target_argument("--sys-clk-freq",        default=50e6, type=float,    help="System clock frequency.")
    parser.add_target_argument("--with-buttons",        action="store_true",         help="Enable buttons.")
    parser.add_target_argument("--with-switches",       action="store_true",         help="Enable switches.")
    parser.add_target_argument("--with-sram",           action="store_true",         help="Enable the onboard asynchronous SRAM.")
    parser.add_target_argument("--with-lpddr2",         action="store_true",         help="Enable the onboard LPDDR2 using the Quartus hard memory controller.")
    parser.add_target_argument("--with-video-terminal", action="store_true",         help="Mirror the BIOS UART output on HDMI at 720p60.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq        = args.sys_clk_freq,
        with_buttons        = args.with_buttons,
        with_switches       = args.with_switches,
        with_sram           = args.with_sram,
        with_lpddr2         = args.with_lpddr2,
        with_video_terminal = args.with_video_terminal,
        **parser.soc_argdict,
    )
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        if args.with_lpddr2 and builder.compile_gateware:
            ip = generate_lpddr2_ip(soc.platform, Path(builder.gateware_dir) / "lpddr2")
            soc.platform.add_ip(str(ip))
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
