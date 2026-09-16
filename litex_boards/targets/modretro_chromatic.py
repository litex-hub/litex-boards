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
from litex.soc.cores.gpio import GPIOIn, GPIOOut
from litex.soc.cores.video import VideoLCDPHY

from litex_boards.platforms import modretro_chromatic

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_lcd=False):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()
        self.cd_por = ClockDomain()

        # # #

        clk_fpga = platform.request("clk_fpga")
        self.clk_24 = platform.request("clk_24")
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

        if with_lcd:
            self.cd_lcd = ClockDomain()
            self.comb += self.cd_lcd.clk.eq(self.clk_24)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, toolchain="gowin", sys_clk_freq=33.55432e6,
        with_buttons = True,
        with_rgb_led = True,
        with_lcd_terminal   = False,
        with_lcd_colorbars  = False,
        with_cart_gpio      = False,
        with_link_gpio      = False,
        with_ir             = False,
        **kwargs):
        platform = modretro_chromatic.Platform(toolchain=toolchain)

        # CRG --------------------------------------------------------------------------------------
        with_lcd = with_lcd_terminal or with_lcd_colorbars
        self.crg = _CRG(platform, sys_clk_freq, with_lcd=with_lcd)

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

        # LCD -------------------------------------------------------------------------------------
        if with_lcd:
            lcd = platform.request("lcd")
            class LCDPads:
                pass
            lcd_pads = LCDPads()
            lcd_pads.clk    = lcd.dotclk
            lcd_pads.de     = lcd.enable
            lcd_pads.hsync  = lcd.hsync
            lcd_pads.vsync  = lcd.vsync
            lcd_pads.r = Signal(2)
            lcd_pads.g = Signal(2)
            lcd_pads.b = Signal(2)
            self.comb += [
                lcd_pads.r.eq(Cat(lcd.db[5], lcd.db[4])),
                lcd_pads.g.eq(Cat(lcd.db[3], lcd.db[2])),
                lcd_pads.b.eq(Cat(lcd.db[1], lcd.db[0])),
            ]
            self.lcdphy = VideoLCDPHY(lcd_pads, clock_domain="lcd", with_clk_ddr_output=False)
            if with_lcd_terminal:
                self.add_video_terminal(phy=self.lcdphy, timings="640x480@60Hz", clock_domain="lcd")
            if with_lcd_colorbars:
                self.add_video_colorbars(phy=self.lcdphy, timings="640x480@60Hz", clock_domain="lcd")
            self.comb += [
                lcd.pwm.eq(1),
                lcd.reset.eq(0),
            ]

        # Cartridge GPIO --------------------------------------------------------------------------
        if with_cart_gpio:
            cart = platform.request("cart")
            self.cart_in = GPIOIn(Cat(cart.det, cart.audin))
            self.cart_out = GPIOOut(Cat(
                cart.a,
                cart.clk,
                cart.cs,
                cart.rd,
                cart.wr,
                cart.rst,
                cart.data_dir_e,
            ))

        # Link GPIO -------------------------------------------------------------------------------
        if with_link_gpio:
            link = platform.request("link")
            self.link_in = GPIOIn(getattr(link, "in"))
            self.link_out = GPIOOut(Cat(link.clk, link.out, link.sd))

        # IR --------------------------------------------------------------------------------------
        if with_ir:
            ir = platform.request("ir")
            self.ir_in = GPIOIn(ir.rx)
            self.ir_out = GPIOOut(ir.led)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=modretro_chromatic.Platform, description="LiteX SoC on ModRetro Chromatic.")
    parser.add_target_argument("--flash",        action="store_true",      help="Flash bitstream.")
    parser.add_target_argument("--sys-clk-freq", default=33.55432e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-buttons", action="store_true",       help="Enable Buttons.")
    parser.add_target_argument("--with-rgb-led", action="store_true",       help="Enable RGB Led.")
    parser.add_target_argument("--with-lcd-terminal", action="store_true",  help="Enable LCD Video Terminal.")
    parser.add_target_argument("--with-lcd-colorbars", action="store_true", help="Enable LCD Video Colorbars.")
    parser.add_target_argument("--with-cart-gpio", action="store_true",     help="Enable cartridge GPIO controls.")
    parser.add_target_argument("--with-link-gpio", action="store_true",     help="Enable link-port GPIO controls.")
    parser.add_target_argument("--with-ir",        action="store_true",     help="Enable IR receiver/LED.")
    args = parser.parse_args()

    soc = BaseSoC(
        toolchain    = args.toolchain,
        sys_clk_freq = args.sys_clk_freq,
        with_buttons = args.with_buttons,
        with_rgb_led = args.with_rgb_led,
        with_lcd_terminal  = args.with_lcd_terminal,
        with_lcd_colorbars = args.with_lcd_colorbars,
        with_cart_gpio     = args.with_cart_gpio,
        with_link_gpio     = args.with_link_gpio,
        with_ir            = args.with_ir,
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
