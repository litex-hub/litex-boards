#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

import os

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
    def __init__(self, pads, sys_clk_freq, polarity=1, gpio_pads=None):
        n = len(pads)
        self._mode = CSRStorage(3, reset=1, description="LED demo mode: 0 direct PWM, 1 breathe, 2 chase, 3 rainbow, 4 strobe, 5 sparkle.")
        self._rgb = CSRStorage(n, reset=2**n - 1, description="RGB LED mask/control value.")
        self._speed = CSRStorage(8, reset=8, description="Animation speed; larger values slow the demo down.")
        self._pwm_r = CSRStorage(8, reset=0xff, description="Red LED PWM duty cycle.")
        self._pwm_g = CSRStorage(8, reset=0xff, description="Green LED PWM duty cycle.")
        self._pwm_b = CSRStorage(8, reset=0xff, description="Blue LED PWM duty cycle.")
        self._pwm_period = CSRStorage(8, reset=0xff, description="PWM period/top value.")
        self._pattern = CSRStorage(4, reset=0, description="Pattern variant selector.")
        self._trigger = CSRStorage(1, reset=0, description="Write to inject a manual demo event.")
        self._gpio_mask = CSRStorage(18, reset=0, description="Edge connector output override mask.")
        self._gpio_value = CSRStorage(18, reset=0, description="Edge connector output override value.")
        self._counter = CSRStatus(32, description="Free-running demo counter.")
        self._frame_counter = CSRStatus(32, description="Animation frame counter.")
        self._event_counter = CSRStatus(32, description="Frame/manual event counter.")
        self._status = CSRStatus(8, description="Packed demo status.")

        # # #

        self.counter       = counter       = Signal(32, name="demo_counter")
        self.frame_counter = frame_counter = Signal(32, name="demo_frame_counter")
        self.event_counter = event_counter = Signal(32, name="demo_event_counter")
        self.prescaler     = prescaler     = Signal(21, name="demo_prescaler")
        self.step          = step          = Signal(8, name="demo_step")
        self.mode          = mode          = Signal(3, name="demo_mode")
        self.rgb           = rgb           = Signal(n, name="demo_rgb")
        self.pattern       = pattern       = Signal(4, name="demo_pattern")
        self.pwm_counter   = pwm_counter   = Signal(8, name="demo_pwm_counter")
        self.frame_tick    = frame_tick    = Signal(name="demo_frame_tick")
        self.manual_event  = manual_event  = Signal(name="demo_manual_event")
        self.leds          = leds          = Signal(n, name="demo_leds")
        self.gpio_out      = gpio_out      = Signal(18, name="demo_gpio_out")
        self.gpio_sample   = gpio_sample   = Signal(8, name="demo_gpio_out_lsb")

        period        = Signal(21)
        breath        = Signal(8)
        direct        = Signal(n, name="demo_direct_leds")
        breathe       = Signal(n, name="demo_breathe_leds")
        chase         = Signal(n, name="demo_chase_leds")
        rainbow       = Signal(n, name="demo_rainbow_leds")
        strobe        = Signal(n, name="demo_strobe_leds")
        sparkle       = Signal(n, name="demo_sparkle_leds")
        edge_pattern  = Signal(18)
        chase_index   = Signal(2)
        color_index   = Signal(3)
        sparkle_index = Signal(3)

        chase_patterns = Array([1, 2, 4, 2])
        color_patterns = Array([1, 2, 4, 3, 6, 5, 7, 0])
        color          = Signal(n)
        sparkle_patterns = Array([1, 4, 2, 5, 3, 6, 7, 0])

        self.comb += [
            self._counter.status.eq(counter),
            self._frame_counter.status.eq(frame_counter),
            self._event_counter.status.eq(event_counter),
            self._status.status.eq(Cat(self._mode.storage, frame_tick, manual_event, leds)),
            mode.eq(self._mode.storage),
            rgb.eq(self._rgb.storage),
            pattern.eq(self._pattern.storage),
            period.eq((self._speed.storage + 1) << 12),
            chase_index.eq(step[6:8] + pattern[0:2]),
            color_index.eq(step[5:8] + pattern[0:3]),
            sparkle_index.eq(counter[16:19] + pattern[0:3]),
            chase.eq(chase_patterns[chase_index] & self._rgb.storage),
            color.eq(color_patterns[color_index]),
            rainbow.eq(color & self._rgb.storage),
            strobe.eq(Mux(step[7] ^ pattern[0], self._rgb.storage, 0)),
            sparkle.eq(sparkle_patterns[sparkle_index] & self._rgb.storage),
        ]

        self.sync += [
            counter.eq(counter + 1),
            frame_tick.eq(0),
            manual_event.eq(0),
            If(pwm_counter >= self._pwm_period.storage,
                pwm_counter.eq(0)
            ).Else(
                pwm_counter.eq(pwm_counter + 1)
            ),
            If(self._trigger.wr_stb,
                manual_event.eq(1),
                event_counter.eq(event_counter + 1)
            ),
            If(prescaler >= period,
                prescaler.eq(0),
                step.eq(step + 1),
                frame_tick.eq(1),
                frame_counter.eq(frame_counter + 1),
                event_counter.eq(event_counter + 1)
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
            direct[0].eq((pwm_counter < self._pwm_r.storage) & self._rgb.storage[0]),
            direct[1].eq((pwm_counter < self._pwm_g.storage) & self._rgb.storage[1]),
            direct[2].eq((pwm_counter < self._pwm_b.storage) & self._rgb.storage[2]),
            breathe.eq(Replicate(pwm_counter < breath, n) & self._rgb.storage),
            If(self._mode.storage == 0,
                leds.eq(direct)
            ).Elif(self._mode.storage == 1,
                leds.eq(breathe)
            ).Elif(self._mode.storage == 2,
                leds.eq(chase)
            ).Elif(self._mode.storage == 3,
                leds.eq(Mux(pwm_counter < breath, rainbow, 0))
            ).Elif(self._mode.storage == 4,
                leds.eq(strobe)
            ).Else(
                leds.eq(sparkle)
            ),
            edge_pattern.eq(Cat(
                leds,
                frame_tick,
                manual_event,
                pwm_counter[0],
                pwm_counter[7],
                step,
                counter[0:2],
                pattern,
            )[0:18]),
            gpio_out.eq((edge_pattern & ~self._gpio_mask.storage) | (self._gpio_value.storage & self._gpio_mask.storage)),
            gpio_sample.eq(gpio_out[:8]),
            pads.eq(leds ^ (polarity*(2**n - 1))),
        ]
        if gpio_pads is not None:
            self.comb += gpio_pads.eq(gpio_out)

    def get_litescope_groups(self):
        return {
            0: [
                self.frame_tick,
                self.manual_event,
                self.leds,
                self.mode,
                self.rgb,
                self.step,
                self.pattern,
                self.pwm_counter,
                self.gpio_sample,
            ],
        }

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCMini):
    def __init__(self, sys_clk_freq=32e6, with_spibone=False, with_led_chaser=True,
        with_demo_leds=False, with_demo_io=False, with_demo_scope=False,
        demo_scope_depth=512, demo_analyzer_csv="analyzer.csv", **kwargs):
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
        if with_demo_leds or with_demo_io or with_demo_scope:
            gpio_pads = platform.request("user_io") if with_demo_io else None
            self.demo_leds = DemoLEDs(platform.request_all("user_led_n"),
                sys_clk_freq = sys_clk_freq,
                polarity     = 1,
                gpio_pads    = gpio_pads)
        elif with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led_n"),
                sys_clk_freq = sys_clk_freq,
                polarity     = 1)

        # LiteScope Analyzer -----------------------------------------------------------------------
        if with_demo_scope:
            from litescope import LiteScopeAnalyzer
            analyzer_groups = self.demo_leds.get_litescope_groups()
            if with_spibone:
                spibone_bus_adr_lsb   = Signal(14, name="spibone_bus_adr_lsb")
                spibone_bus_dat_w_lsb = Signal(16, name="spibone_bus_dat_w_lsb")
                spibone_bus_dat_r_lsb = Signal(16, name="spibone_bus_dat_r_lsb")
                self.comb += [
                    spibone_bus_adr_lsb.eq(self.spibone.bus.adr[:14]),
                    spibone_bus_dat_w_lsb.eq(self.spibone.bus.dat_w[:16]),
                    spibone_bus_dat_r_lsb.eq(self.spibone.bus.dat_r[:16]),
                ]
                analyzer_groups[1] = [
                    self.spibone.bus.cyc,
                    self.spibone.bus.stb,
                    self.spibone.bus.we,
                    self.spibone.bus.ack,
                    spibone_bus_adr_lsb,
                    spibone_bus_dat_w_lsb,
                    spibone_bus_dat_r_lsb,
                ]
            self.analyzer = LiteScopeAnalyzer(analyzer_groups,
                depth        = demo_scope_depth,
                clock_domain = "sys",
                samplerate   = sys_clk_freq,
                register     = True,
                csr_csv      = demo_analyzer_csv)
            if hasattr(self, "add_csr"):
                self.add_csr("analyzer")
            else:
                self.csr.add("analyzer")

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=adiuvo_forgix.Platform, description="LiteX SoC on Adiuvo Forgix.")
    parser.add_target_argument("--sys-clk-freq", default=32e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-spibone",     action="store_true", help="Add SPIBone on the RP2350 SPI pins.")
    parser.add_target_argument("--with-demo-leds",   action="store_true", help="Add the CSR-controlled RGB LED demo core.")
    parser.add_target_argument("--with-demo-io",     action="store_true", help="Mirror demo signals to the Teensy-style edge connector.")
    parser.add_target_argument("--with-demo-scope",  action="store_true", help="Add LiteScope Analyzer probes for the demo core.")
    parser.add_target_argument("--demo-scope-depth", default=512, type=int, help="LiteScope Analyzer capture depth.")
    parser.add_target_argument("--demo-analyzer-csv", default=None, help="LiteScope Analyzer CSV path.")
    parser.set_defaults(
        cpu_type             = "None",
        integrated_sram_size = 0,
        no_uart              = True,
        no_timer             = True,
        uart_name            = "crossover",
        with_uartbone        = False)
    args = parser.parse_args()

    builder_argdict = parser.builder_argdict
    output_dir = builder_argdict["output_dir"] or "build/adiuvo_forgix"
    demo_analyzer_csv = args.demo_analyzer_csv or os.path.join(output_dir, "analyzer.csv")

    soc = BaseSoC(
        sys_clk_freq       = args.sys_clk_freq,
        with_spibone       = args.with_spibone,
        with_demo_leds     = args.with_demo_leds,
        with_demo_io       = args.with_demo_io,
        with_demo_scope    = args.with_demo_scope,
        demo_scope_depth   = args.demo_scope_depth,
        demo_analyzer_csv  = demo_analyzer_csv,
        **parser.soc_argdict)
    builder = Builder(soc, **builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

if __name__ == "__main__":
    main()
