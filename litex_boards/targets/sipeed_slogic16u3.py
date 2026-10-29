#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025-2026 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from litex.soc.cores.led import LedChaser

from litex.soc.integration.soc_core import *
from litex.soc.integration.builder  import *

from litex_boards.platforms.sipeed_slogic16u3 import Platform

# OSCA ---------------------------------------------------------------------------------------------

OSCA_FREQ = 207.32e6 # Nominal GW5AT OSCA base frequency (~51.7MHz measured with FREQ_DIV=4).

def osca_div(freq, fosc=OSCA_FREQ):
    """OSCA FREQ_DIV for freq: 2-126, even values (and 3)."""
    div = int(round(fosc/freq))
    div = max(2, min(126, div))
    if div == 3:
        return div
    if div & 1:
        div = div + 1 if div < 126 else div - 1
    return div

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()
        self.cd_por = ClockDomain(reset_less=True)

        # # #

        # Internal Oscillator (no fabric clock input on the board, the 125MHz oscillator only feeds
        # the GTR12 reference clock).
        osc = Signal()
        self.specials += Instance("OSCA",
            p_FREQ_DIV = osca_div(sys_clk_freq),
            i_OSCEN    = 1,
            o_OSCOUT   = osc,
        )
        self.comb += [
            self.cd_por.clk.eq(osc),
            self.cd_sys.clk.eq(osc),
        ]

        # Power-On Reset.
        por_count = Signal(16, reset=2**16 - 1)
        por_done  = Signal()
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))
        self.specials += AsyncResetSynchronizer(self.cd_sys, ~por_done | self.rst)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=OSCA_FREQ/4, device_version="B", with_led_chaser=True, **kwargs):
        platform = Platform(device_version=device_version)

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)
        sys_clk_freq = OSCA_FREQ/osca_div(sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        # GW5AT has no pROM resource: boot memory implemented as RAM (initialized BSRAMs: Gowin >= 1.9.12,
        # device version B).
        kwargs["integrated_rom_size"] = 32 * KILOBYTE
        kwargs["integrated_rom_mode"] = "rwx"
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Sipeed SLogic16U3", **kwargs)

        # 125MHz Oscillator / USB2 Pull-up ---------------------------------------------------------
        self.comb += [
            platform.request("clk125_oe").eq(1),  # GTR12 Q0 reference clock enabled.
            platform.request("usb_pullup").eq(0), # SuperSpeed only.
        ]

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq,
            )

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=Platform, description="LiteX SoC on Sipeed SLogic16U3.")
    parser.add_target_argument("--flash",          action="store_true",             help="Flash bitstream.")
    parser.add_target_argument("--prog-kit",       default="openfpgaloader",        help="Programmer select from Gowin/openFPGALoader.")
    parser.add_target_argument("--sys-clk-freq",   default=OSCA_FREQ/4, type=float, help="System clock frequency (OSCA: 207.32MHz/2-126).")
    parser.add_target_argument("--device-version", default="B", choices=["A", "B"], help="GW5AT-15 device version (A: Gowin 1.9.10).")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq   = args.sys_clk_freq,
        device_version = args.device_version,
        **parser.soc_argdict
    )

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer(kit=args.prog_kit)
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer(kit=args.prog_kit)
        prog.flash(0, builder.get_bitstream_filename(mode="flash", ext=".fs"), external=True)

if __name__ == "__main__":
    main()
