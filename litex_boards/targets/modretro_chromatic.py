#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import *

from litex.soc.cores.clock.gowin_gw5a import GW5APLL
from litex.soc.integration.soc import *
from litex.soc.integration.builder import *
from litex.soc.cores.gpio import GPIOIn

from litex_boards.platforms import modretro_chromatic

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()
        self.cd_por = ClockDomain()

        # # #

        clk_fpga = platform.request("clk_fpga")
        platform.request("clk_24")
        platform.request("clk_27")
        buttons  = platform.request("buttons")
        rst_n    = buttons.a
        self.buttons = buttons

        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += [
            self.cd_por.clk.eq(clk_fpga),
            por_done.eq(por_count == 0),
        ]
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        self.pll = pll = GW5APLL(devicename=platform.devicename, device=platform.device)
        self.comb += pll.reset.eq(~por_done | ~rst_n)
        pll.register_clkin(clk_fpga, 33.55432e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, toolchain="gowin", sys_clk_freq=33.55432e6,
        with_buttons = True,
        with_rgb_led = True,
        **kwargs):
        platform = modretro_chromatic.Platform(toolchain=toolchain)

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on ModRetro Chromatic", **kwargs)

        # Buttons ----------------------------------------------------------------------------------
        if with_buttons:
            buttons = self.crg.buttons
            self.buttons = GPIOIn(Cat(
                buttons.a,
                buttons.b,
                buttons.dpad_down,
                buttons.dpad_left,
                buttons.dpad_right,
                buttons.dpad_up,
                buttons.menu,
                buttons.sel,
                buttons.start,
            ))

        # RGB Led ----------------------------------------------------------------------------------
        if with_rgb_led:
            rgb_led = platform.request("rgb_led")
            self.rgb_led = CSRStorage(3)
            self.comb += Cat(rgb_led.r, rgb_led.g, rgb_led.b).eq(~self.rgb_led.storage)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=modretro_chromatic.Platform, description="LiteX SoC on ModRetro Chromatic.")
    parser.add_target_argument("--flash",        action="store_true",      help="Flash bitstream.")
    parser.add_target_argument("--sys-clk-freq", default=33.55432e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-buttons", action="store_true",      help="Enable Buttons.")
    parser.add_target_argument("--with-rgb-led", action="store_true",      help="Enable RGB Led.")
    args = parser.parse_args()

    soc = BaseSoC(
        toolchain    = args.toolchain,
        sys_clk_freq = args.sys_clk_freq,
        with_buttons = args.with_buttons,
        with_rgb_led = args.with_rgb_led,
        **parser.soc_argdict
    )

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.flash(0, builder.get_bitstream_filename(mode="flash", ext=".fs"))

if __name__ == "__main__":
    main()
