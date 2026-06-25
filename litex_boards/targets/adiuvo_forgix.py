#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import *

from litex_boards.platforms import adiuvo_forgix

from litex.soc.integration.soc import *
from litex.soc.integration.builder import *
from litex.soc.interconnect.csr import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.spi.spi_bone import SPIBone

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        assert sys_clk_freq == platform.default_clk_freq

        self.rst    = Signal()
        self.cd_sys = ClockDomain()

        # # #

        clk32 = platform.request("clk32")

        self.comb += [
            self.cd_sys.clk.eq(clk32),
            self.cd_sys.rst.eq(self.rst),
        ]

# DemoLEDs -----------------------------------------------------------------------------------------

class DemoLEDs(LiteXModule):
    def __init__(self, pads, sys_clk_freq, polarity=1):
        n = len(pads)
        self._mode = CSRStorage(2, reset=1, description="LED demo mode: 0 fixed, 1 breathe, 2 chase, 3 rainbow.")
        self._rgb = CSRStorage(n, reset=2**n - 1, description="RGB LED mask/control value.")
        self._speed = CSRStorage(8, reset=8, description="Animation speed; larger values slow the demo down.")
        self._counter = CSRStatus(32, description="Free-running demo counter.")

        # # #

        counter     = Signal(32)
        prescaler   = Signal(21)
        step        = Signal(8)
        pwm_counter = Signal(8)
        period      = Signal(21)
        breath      = Signal(8)
        leds        = Signal(n)

        chase_patterns = Array([1, 2, 4, 2])
        color_patterns = Array([1, 2, 4, 3, 6, 5, 7, 0])
        chase          = Signal(n)
        color          = Signal(n)

        self.comb += [
            self._counter.status.eq(counter),
            period.eq((self._speed.storage + 1) << 12),
            chase.eq(chase_patterns[step[6:8]]),
            color.eq(color_patterns[step[5:8]]),
        ]

        self.sync += [
            counter.eq(counter + 1),
            pwm_counter.eq(pwm_counter + 1),
            If(prescaler >= period,
                prescaler.eq(0),
                step.eq(step + 1)
            ).Else(
                prescaler.eq(prescaler + 1)
            )
        ]

        self.comb += [
            If(step[7],
                breath.eq(~step)
            ).Else(
                breath.eq(step)
            ),
            If(self._mode.storage == 0,
                leds.eq(self._rgb.storage)
            ).Elif(self._mode.storage == 1,
                leds.eq(Mux(pwm_counter < breath, self._rgb.storage, 0))
            ).Elif(self._mode.storage == 2,
                leds.eq(chase & self._rgb.storage)
            ).Else(
                leds.eq(Mux(pwm_counter < breath, color, 0))
            ),
            pads.eq(leds ^ (polarity*(2**n - 1))),
        ]

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCMini):
    def __init__(self, sys_clk_freq=32e6, with_spibone=False, with_led_chaser=True, with_demo_leds=False, **kwargs):
        platform = adiuvo_forgix.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCMini ----------------------------------------------------------------------------------
        kwargs["cpu_type"]             = "None"
        kwargs["integrated_sram_size"] = 0
        kwargs["integrated_rom_size"]  = 0
        kwargs["with_uart"]            = False
        kwargs["with_timer"]           = False
        kwargs["uart_name"]            = "crossover"
        kwargs["with_uartbone"]        = kwargs.get("with_uartbone", False) or not with_spibone
        SoCMini.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Adiuvo Forgix", **kwargs)

        # RP2350 <-> MMAP over 3-wire SPIBone. See the RP-side USB/SPI bridge approach:
        # https://github.com/enjoy-digital/litex_rp2040_pmod_test
        if with_spibone:
            self.spibone = SPIBone(platform.request("spibone"), wires=3)
            self.bus.add_master(name="spibone", master=self.spibone.bus)

        # Leds -------------------------------------------------------------------------------------
        if with_demo_leds:
            self.demo_leds = DemoLEDs(platform.request_all("user_led_n"), sys_clk_freq=sys_clk_freq, polarity=1)
        elif with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led_n"),
                sys_clk_freq = sys_clk_freq,
                polarity     = 1)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=adiuvo_forgix.Platform, description="LiteX SoC on Adiuvo Forgix.")
    parser.add_target_argument("--sys-clk-freq", default=32e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-spibone", action="store_true", help="Add SPIBone on the RP2350 SPI pins.")
    parser.add_target_argument("--with-demo-leds", action="store_true", help="Add the CSR-controlled RGB LED demo core.")
    parser.set_defaults(
        cpu_type             = "None",
        integrated_sram_size = 0,
        no_uart              = True,
        no_timer             = True,
        uart_name            = "crossover",
        with_uartbone        = False)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq = args.sys_clk_freq,
        with_spibone = args.with_spibone,
        with_demo_leds = args.with_demo_leds,
        **parser.soc_argdict)
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

if __name__ == "__main__":
    main()
