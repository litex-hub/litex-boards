#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 Matt Thompson <matt@boondocker.io>
# SPDX-License-Identifier: BSD-2-Clause

# Build/Use:
# ./terasic_c5g.py --build --load
# ./terasic_c5g.py --with-sram --with-lpddr2 --build --load
# ./terasic_c5g.py --with-video-terminal --build --load
# The LPDDR2 UniPHY IP is generated with Quartus (ip-generate) during the build.

import os
import math

from types import SimpleNamespace

from migen import *

from litex.gen import *

from litex.build.io import DDROutput

from litex_boards.platforms import terasic_c5g

from litex.soc.cores.bitbang import I2CMaster
from litex.soc.cores.clock import CycloneVPLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.gpio import GPIOIn
from litex.soc.cores.ram.async_sram import AsyncSRAM
from litex.soc.cores.ram.intel_cyclone5_lpddr2 import CycloneVLPDDR2
from litex.soc.cores.video import VideoDVIPHY

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_lpddr2=False, with_video_pll=False):
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

        # Video PLL (On clk50 2, 74.25MHz for 1280x720@60Hz).
        if with_video_pll:
            # sys <-> hdmi through an asynchronous FIFO (UART mirror of the Video Terminal).
            sys_clk50 = "clk501" if with_lpddr2 else "clk50"
            platform.toolchain.additional_sdc_commands.append(
                "set_clock_groups -asynchronous "
                f"-group [get_clocks {{{sys_clk50} altpll:ALTPLL|*}}] "
                "-group [get_clocks {clk502 altpll:ALTPLL_1|*}]"
            )
            self.cd_hdmi  = ClockDomain()
            self.hdmi_pll = hdmi_pll = CycloneVPLL(speedgrade="-C7")
            self.comb += hdmi_pll.reset.eq(self.rst | ~rst_n)
            hdmi_pll.register_clkin(platform.request("clk50", 2), 50e6)
            hdmi_pll.create_clkout(self.cd_hdmi, 74.25e6, margin=0)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=50e6,
        with_led_chaser     = True,
        with_sram           = False,
        with_lpddr2         = False,
        with_buttons        = False,
        with_switches       = False,
        with_video_terminal = False,
        **kwargs):
        platform = terasic_c5g.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, with_lpddr2=with_lpddr2, with_video_pll=with_video_terminal)

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

        # Video Terminal (HDMI, ADV7513) -----------------------------------------------------------
        if with_video_terminal:
            # ADV7513 I2C initialization (by the BIOS): RGB888 input (ID 0) with separate syncs and
            # data enable, fixed video mode to start the transmitter before a sink is plugged in.
            self.i2c = I2CMaster(platform.request("i2c"))
            self.i2c.add_init(addr=0x39, init=[
                (0xd6, 0xc0), # Keep configuration across hot-plug events.
                (0x41, 0x10), # Power up.
                (0x98, 0x03), # Required fixed settings.
                (0x9a, 0xe0),
                (0x9c, 0x30),
                (0x9d, 0x61),
                (0xa2, 0xa4),
                (0xa3, 0xa4),
                (0xe0, 0xd0),
                (0xf9, 0x00),
                (0x15, 0x00), # RGB, 8 bits per component.
                (0x16, 0x30),
                (0x18, 0x46), # Disable color-space conversion.
                (0xaf, 0x16), # HDMI mode, HDCP disabled.
            ])

            # PHY (Without the clk pad: forwarded inverted for the transmitter to sample the
            # registered data/syncs at mid-cycle).
            hdmi_pads  = platform.request("hdmi")
            video_pads = SimpleNamespace(
                r     = hdmi_pads.r,
                g     = hdmi_pads.g,
                b     = hdmi_pads.b,
                de    = hdmi_pads.de,
                hsync = hdmi_pads.hsync,
                vsync = hdmi_pads.vsync,
            )
            self.videophy = VideoDVIPHY(video_pads, clock_domain="hdmi")
            self.specials += DDROutput(i1=0, i2=1, o=hdmi_pads.clk, clk=ClockSignal("hdmi"))

            # Terminal.
            self.add_video_terminal(phy=self.videophy, timings="1280x720@60Hz", clock_domain="hdmi")

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=terasic_c5g.Platform, description="LiteX SoC on Terasic C5G.")
    parser.add_target_argument("--sys-clk-freq",        default=50e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-sram",           action="store_true",      help="Enable SRAM (IS61WV25616, 512KiB).")
    parser.add_target_argument("--with-lpddr2",         action="store_true",      help="Enable LPDDR2 (512MiB, Cyclone V Hard Memory Controller).")
    parser.add_target_argument("--with-buttons",        action="store_true",      help="Enable Buttons.")
    parser.add_target_argument("--with-switches",       action="store_true",      help="Enable Switches.")
    parser.add_target_argument("--with-video-terminal", action="store_true",      help="Enable Video Terminal (HDMI, 1280x720@60Hz).")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq        = args.sys_clk_freq,
        with_sram           = args.with_sram,
        with_lpddr2         = args.with_lpddr2,
        with_buttons        = args.with_buttons,
        with_switches       = args.with_switches,
        with_video_terminal = args.with_video_terminal,
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
