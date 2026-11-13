#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# SPDX-License-Identifier: BSD-2-Clause

from pathlib import Path

from migen import Cat, ClockDomain, Signal

from litex.gen import LiteXModule

from litex_boards.platforms import terasic_c5g

from litex.soc.cores.clock import CycloneVPLL
from litex.soc.cores.gpio import GPIOIn
from litex.soc.cores.led import LedChaser
from litex.soc.integration.builder import Builder
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.soc_core import SoCCore

from litex_boards.targets.terasic_c5g_memory import C5GLPDDR2, C5GSRAM, generate_lpddr2_ip

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_lpddr2):
        self.rst    = Signal()
        self.cd_sys = ClockDomain("sys")

        self.pll = pll = CycloneVPLL(speedgrade="-C7")
        self.reset_n = platform.request("cpu_reset_n")
        self.ref_clk = platform.request("clk50")
        self.comb += pll.reset.eq(self.rst | ~self.reset_n)
        # Keep the PLL at R20 available for the LPDDR2 hard controller.
        pll.register_clkin(platform.request("clk50", 1) if with_lpddr2 else self.ref_clk, 50e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=50e6, with_led_chaser=True, with_buttons=False, with_switches=False,
        with_sram=False, with_lpddr2=False, **kwargs):
        platform = terasic_c5g.Platform()

        self.crg = _CRG(platform, sys_clk_freq, with_lpddr2)

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

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=terasic_c5g.Platform, description="LiteX SoC on Terasic C5G.")
    parser.add_target_argument("--sys-clk-freq",  default=50e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-buttons",  action="store_true",      help="Enable buttons.")
    parser.add_target_argument("--with-switches", action="store_true",      help="Enable switches.")
    parser.add_target_argument("--with-sram",     action="store_true",      help="Enable the onboard asynchronous SRAM.")
    parser.add_target_argument("--with-lpddr2",   action="store_true",      help="Enable the onboard LPDDR2 using the Quartus hard memory controller.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq  = args.sys_clk_freq,
        with_buttons  = args.with_buttons,
        with_switches = args.with_switches,
        with_sram     = args.with_sram,
        with_lpddr2   = args.with_lpddr2,
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
