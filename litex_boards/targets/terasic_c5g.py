#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 Matt Thompson <matt@boondocker.io>
# SPDX-License-Identifier: BSD-2-Clause

# Build/Use:
# ./terasic_c5g.py --build --load
# ./terasic_c5g.py --with-sram --with-lpddr2 --build --load
# ./terasic_c5g.py --with-audio --with-audio-dma --integrated-sram-size=65536 --build --load
# The LPDDR2 UniPHY IP is generated with Quartus (ip-generate) during the build.

import os
import math

from migen import *

from litex.gen import *

from litex_boards.platforms import terasic_c5g

from litex.soc.cores.bitbang import I2CMaster
from litex.soc.cores.clock import CycloneVPLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import *
from litex.soc.integration.builder import *
from litex.soc.interconnect import wishbone
from litex.soc.cores.led import LedChaser
from litex.soc.cores.gpio import GPIOIn
from litex.soc.cores.ram.async_sram import AsyncSRAM
from litex.soc.cores.ram.intel_cyclone5_lpddr2 import CycloneVLPDDR2

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_lpddr2=False, with_audio=False):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()

        # # #

        # Clk / Rst.
        self.rst_n = rst_n = platform.request("cpu_reset_n")
        self.clk50 = clk50 = platform.request("clk50")

        # PLL (On clk50 1 with LPDDR2: clk50 0 and its PLL are kept for the Hard Memory Controller).
        self.pll = pll = CycloneVPLL(speedgrade="-C7")
        self.comb += pll.reset.eq(self.rst | ~rst_n)
        pll.register_clkin(platform.request("clk50", 1) if with_lpddr2 else clk50, 50e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)

        # Audio Clk (12.288MHz: 256 x 48kHz).
        if with_audio:
            self.cd_audio = ClockDomain()
            pll.create_clkout(self.cd_audio, 12.288e6, margin=3e-3)
            # sys <-> audio through the PCM FIFOs and synchronizers.
            platform.toolchain.additional_sdc_commands.append(
                r"set_clock_groups -asynchronous "
                r"-group [get_clocks {altpll:ALTPLL|*clk\[0\]}] "
                r"-group [get_clocks {altpll:ALTPLL|*clk\[1\]}]")

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=50e6,
        with_led_chaser     = True,
        with_sram           = False,
        with_lpddr2         = False,
        with_audio          = False,
        with_audio_dma      = False,
        with_buttons        = False,
        with_switches       = False,
        **kwargs):
        if with_audio_dma and not with_audio:
            raise ValueError("Audio DMA requires audio to be enabled.")
        platform = terasic_c5g.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, with_lpddr2=with_lpddr2, with_audio=with_audio)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Terasic C5G", **kwargs)

        # SRAM -------------------------------------------------------------------------------------
        if with_sram:
            # IS61WV25616 (512KiB, 16-bit): a 32-bit access is done as two 16-bit accesses, each
            # with a setup, an access and a hold phase of at least 20ns.
            sram_cycles   = math.ceil(20e-9*sys_clk_freq)
            self.ext_sram = AsyncSRAM(platform.request("sram"),
                read_cycles  = sram_cycles,
                write_cycles = sram_cycles,
                setup_cycles = sram_cycles,
                hold_cycles  = sram_cycles,
            )
            self.bus.add_slave("ext_sram", self.ext_sram.bus, strip_origin=True, region=SoCRegion(
                origin = 0x8000_0000,
                size   = 512*1024,
                cached = False,
            ))

        # LPDDR2 -----------------------------------------------------------------------------------
        if with_lpddr2:
            # 512MiB (32-bit, 1 rank) at 300MHz from the 50MHz reference, parameters from the
            # Terasic C5G System CD reference design.
            self.lpddr2 = CycloneVLPDDR2(platform,
                pads          = platform.request("lpddr2"),
                rzq           = platform.request("lpddr2_rzq"),
                ref_clk       = self.crg.clk50,
                ref_clk_freq  = 50e6,
                mem_clk_freq  = 300e6,
                speedgrade    = 7,
                row_bits      = 14,
                col_bits      = 10,
                bank_bits     = 3,
                reset_n       = self.crg.rst_n,
                ip_name       = "c5g_lpddr2",
                ip_parameters = {
                    "MEM_TCL"      : 7,
                    "MEM_TRFC_NS"  : 130.0,
                    "MEM_TREFI_US" : 3.9,
                },
            )
            # The Wishbone bus is crossed to the Hard Memory Controller clock with asynchronous FIFOs.
            platform.toolchain.additional_sdc_commands.append(
                "set_clock_groups -asynchronous -group [get_clocks {clk501 *ALTPLL*}]")
            self.bus.add_slave("lpddr2", self.lpddr2.bus, strip_origin=True, region=SoCRegion(
                origin = 0xa000_0000,
                size   = self.lpddr2.size,
                cached = False,
            ))

        # Audio (SSM2603) --------------------------------------------------------------------------
        if with_audio:
            from litex.soc.cores.audio import SSM2603, SSM2603PCM # LiteX #2801.

            sample_width = 32

            # I2C / Codec (Initialized by the BIOS).
            self.i2c   = I2CMaster(platform.request("i2c"))
            self.codec = SSM2603(self, "i2c", sample_width=sample_width)

            # DMA (64-bit Wishbone masters).
            playback_bus = None
            capture_bus  = None
            if with_audio_dma:
                playback_bus = wishbone.Interface(data_width=64, mode="r")
                capture_bus  = wishbone.Interface(data_width=64, mode="w")
                self.bus.add_master("audio_playback", playback_bus)
                self.bus.add_master("audio_capture",  capture_bus)

            # PCM.
            self.audio = SSM2603PCM(platform.request("audio"), self.crg.cd_audio.clk,
                sample_width = sample_width,
                playback_bus = playback_bus,
                capture_bus  = capture_bus,
            )
            self.add_config("AUDIO_PCM_RATE", self.audio.sample_rate)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

        # Buttons / Switches -----------------------------------------------------------------------
        if with_buttons:
            self.buttons = GPIOIn(~Cat(platform.request_all("user_btn")))
        if with_switches:
            self.switches = GPIOIn(Cat(platform.request_all("user_sw")))

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=terasic_c5g.Platform, description="LiteX SoC on Terasic C5G.")
    parser.add_target_argument("--sys-clk-freq",        default=50e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-sram",           action="store_true",      help="Enable SRAM (IS61WV25616, 512KiB).")
    parser.add_target_argument("--with-lpddr2",         action="store_true",      help="Enable LPDDR2 (512MiB, Cyclone V Hard Memory Controller).")
    parser.add_target_argument("--with-audio",          action="store_true",      help="Enable Audio (SSM2603 stereo playback and capture).")
    parser.add_target_argument("--with-audio-dma",      action="store_true",      help="Enable Audio DMA (Wishbone masters for playback and capture).")
    parser.add_target_argument("--with-buttons",        action="store_true",      help="Enable Buttons.")
    parser.add_target_argument("--with-switches",       action="store_true",      help="Enable Switches.")
    args = parser.parse_args()
    if args.with_audio_dma and not args.with_audio:
        parser.error("--with-audio-dma requires --with-audio")

    soc = BaseSoC(
        sys_clk_freq        = args.sys_clk_freq,
        with_sram           = args.with_sram,
        with_lpddr2         = args.with_lpddr2,
        with_audio          = args.with_audio,
        with_audio_dma      = args.with_audio_dma,
        with_buttons        = args.with_buttons,
        with_switches       = args.with_switches,
        **parser.soc_argdict
    )
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        # Generate the LPDDR2 UniPHY IP with Quartus.
        if args.with_lpddr2 and builder.compile_gateware:
            soc.lpddr2.generate_ip(os.path.join(builder.gateware_dir, "lpddr2"))
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
