#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019 msloniewski <marcin.sloniewski@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import *

from litex.build.io import DDROutput

from litex_boards.platforms import terasic_de10lite

from litex.soc.cores.clock import Max10PLL, IntelPLLPhaseStepper
from litex.soc.integration.soc import *
from litex.soc.integration.builder import *
from litex.soc.cores.video import VideoVGAPHY
from litex.soc.cores.led import LedChaser
from litex.soc.cores.gpio import GPIOIn

from litedram.modules import IS42S16320
from litedram.phy import GENSDRPHY, HalfRateGENSDRPHY

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, sdram_clk_phase, sdram_rate="1:1", with_sdram_clk_leveling=False):
        self.rst       = Signal()
        self.cd_sys    = ClockDomain()
        if sdram_rate == "1:2":
            self.cd_sys2x    = ClockDomain()
            self.cd_sys2x_ps = ClockDomain()
        else:
            self.cd_sys_ps = ClockDomain()
        self.cd_vga    = ClockDomain()

        # # #

        # Clk / Rst
        clk50 = platform.request("clk50")

        # PLL
        self.pll = pll = Max10PLL(speedgrade="-7")
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk50, 50e6)
        pll.create_clkout(self.cd_sys,    sys_clk_freq)
        if sdram_rate == "1:2":
            pll.create_clkout(self.cd_sys2x,    2*sys_clk_freq)
            pll.create_clkout(self.cd_sys2x_ps, 2*sys_clk_freq, phase=sdram_clk_phase)
        else:
            pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=sdram_clk_phase)
        if with_sdram_clk_leveling:
            # SDRAM clock phase stepped at run time, leveled by the BIOS (sdram_clk_phase).
            pll.expose_dpa(clkout=pll.nclkouts - 1)
        pll.create_clkout(self.cd_vga,    40e6)
        # The SoC reset (sys) only drives the PLL reset synchronizer (clk50): asynchronous.
        platform.toolchain.additional_sdc_commands.append(
            "set_false_path -from [get_clocks {*ALTPLL*clk[0]}] -to [get_clocks {clk50}]")

        # SDRAM clock
        sdram_clk = ClockSignal("sys2x_ps" if sdram_rate == "1:2" else "sys_ps")
        self.specials += DDROutput(1, 0, platform.request("sdram_clock"), sdram_clk)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=50e6,
        sdram_clk_phase     = 90,
        sdram_rate          = "1:1",
        with_sdram_clk_leveling = False,
        with_led_chaser     = True,
        with_video_terminal = False,
        with_buttons        = False,
        with_switches       = False,
        **kwargs):
        platform = terasic_de10lite.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, sdram_clk_phase, sdram_rate, with_sdram_clk_leveling)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on DE10-Lite", **kwargs)

        # SDR SDRAM --------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            if sdram_rate == "1:2":
                # DFI registered in sys: timing closure at the sys2x IO registers.
                self.sdrphy = HalfRateGENSDRPHY(platform.request("sdram"), sys_clk_freq, with_dfi_reg=True)
            else:
                self.sdrphy = GENSDRPHY(platform.request("sdram"), sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.sdrphy,
                module        = IS42S16320(sys_clk_freq, sdram_rate),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )
            if with_sdram_clk_leveling:
                # BIOS SDRAM clock phase leveling at boot (liblitedram sdram_clk_phase_leveling).
                self.sdram_clk_phase = IntelPLLPhaseStepper(self.crg.pll)

        # Video Terminal ---------------------------------------------------------------------------
        if with_video_terminal:
            self.videophy = VideoVGAPHY(platform.request("vga"), clock_domain="vga")
            self.add_video_terminal(phy=self.videophy, timings="800x600@60Hz", clock_domain="vga")

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

        # Buttons / Switches -----------------------------------------------------------------------
        if with_buttons:
            self.buttons = GPIOIn(Cat(platform.request_all("user_btn")))
        if with_switches:
            self.switches = GPIOIn(Cat(platform.request_all("user_sw")))

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=terasic_de10lite.Platform, description="LiteX SoC on DE10-Lite.")
    parser.add_target_argument("--sys-clk-freq",        default=50e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--sdram-clk-phase",     default=None, type=float, help="SDRAM clock phase (default: 90 at 1:1, 180 at 1:2).")
    parser.add_target_argument("--sdram-rate",          default="1:1",            help="SDRAM Rate (1:1 Full Rate or 1:2 Half Rate).")
    parser.add_target_argument("--with-sdram-clk-leveling", action="store_true",  help="Level the SDRAM clock phase at boot (BIOS), from --sdram-clk-phase.")
    parser.add_target_argument("--with-video-terminal", action="store_true",      help="Enable Video Terminal (VGA).")
    parser.add_target_argument("--with-buttons",        action="store_true",      help="Enable Buttons.")
    parser.add_target_argument("--with-switches",       action="store_true",      help="Enable Switches.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq        = args.sys_clk_freq,
        sdram_clk_phase     = args.sdram_clk_phase if args.sdram_clk_phase is not None else {"1:1": 90, "1:2": 180}[args.sdram_rate],
        sdram_rate          = args.sdram_rate,
        with_sdram_clk_leveling = args.with_sdram_clk_leveling,
        with_video_terminal = args.with_video_terminal,
        with_buttons        = args.with_buttons,
        with_switches       = args.with_switches,
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
