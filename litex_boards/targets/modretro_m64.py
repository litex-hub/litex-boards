#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause
#
# Uses the independent 50MHz oscillator, 64KiB ROM and 128KiB main RAM in block RAM.
# Build/load: python3 -m litex_boards.targets.modretro_m64 --build --load
# Hardware operation has not yet been tested. See the platform for schematics and JTAG wiring.
#
# JTAG UART uses USER1. For an OpenOCD-compatible 1.8V adapter, add this TAP definition
# to the adapter's configuration (m64.cfg), then run: litex_term jtag --jtag-config=m64.cfg
#   transport select jtag
#   adapter speed 10000
#   jtag newtap xcau15p tap -irlen 6 -ignore-version -expected-id 0x04ac2093
# --with-jtagbone uses USER1 for JTAGBone and selects a crossover UART.
# --uart-name=serial selects the 3.3V debug UART on J18.
#
# --with-psram enables all four devices in x16 mode at sys_clk_freq/8 (12.5MHz by default).
# The BIOS stays in block RAM. psram0..3 are uncached regions at 0xa0000000, 0xa4000000,
# 0xa8000000 and 0xac000000, with sizes 32, 32, 32 and 64MiB. Each psramN_status CSR reports
# ready (bit 0), initialization error (bit 1) and read timeout (bit 2); psramN_identification
# contains MR1/MR2. Initial BIOS tests can use:
#   mem_test 0xa0000000 0x1000
#   mem_test 0xa4000000 0x1000
#   mem_test 0xa8000000 0x1000
#   mem_test 0xac000000 0x1000
#
# --with-video-terminal / --with-video-colorbars generates 720p60 DVI-compatible video.
# Video needs LiteICLink and an already configured 8T49N241 Q2 GTH reference clock.
# Pass its actual frequency with --video-refclk-freq; the schematic does not specify it.
# For example, with Q2 configured to 148.5MHz:
#   python3 -m litex_boards.targets.modretro_m64 --with-psram --with-video-colorbars \
#       --video-refclk-freq=148.5e6 --build
# The target does not program the clock generator; clkgen_i2c (0x7c) and hdmi_i2c (0x5e)
# are exposed for bring-up. Pixel and GTH clocks share Q2 to avoid FIFO drift.
# SN75DP159: https://www.ti.com/lit/ds/symlink/sn75dp159.pdf

import math

from migen import *
from migen.genlib.misc import WaitTimer

from litex.gen import *

from litex_boards.platforms import modretro_m64

from litex.soc.cores.clock import USPMMCM
from litex.soc.cores.gpio import GPIOIn, GPIOOut, GPIOTristate
from litex.soc.cores.bitbang import I2CMaster
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.soc_core import SoCCore
from litex.soc.integration.builder import Builder

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, video_refclk_freq=None):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()

        # Clk / Rst.
        clk50       = platform.request("clk50")
        cpu_reset_n = platform.request("cpu_reset_n")

        # Buffer the MMCM input, which also clocks its reset delay registers.
        clk50_buf = Signal()
        self.specials += Instance("BUFG", i_I=clk50, o_O=clk50_buf)

        # PLL.
        self.pll = pll = USPMMCM(speedgrade=-2)
        self.comb += pll.reset.eq(~cpu_reset_n | self.rst)
        pll.register_clkin(clk50_buf, 50e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.
        platform.add_platform_command("set_false_path -from [get_ports {cpu_reset_n}]", cpu_reset_n=cpu_reset_n)

        # HDMI clocking. Pixel and serial clocks must share the external GTH reference.
        if video_refclk_freq is not None:
            self.cd_hdmi      = ClockDomain()
            self.video_refclk = Signal()
            refclk_pads = platform.request("clk_gth")
            refclk_div2 = Signal()
            refclk_buf  = Signal()
            self.specials += [
                Instance("IBUFDS_GTE4",
                    p_REFCLK_HROW_CK_SEL = 0b01, # ODIV2 = O/2.

                    i_CEB   = 0,
                    i_I     = refclk_pads.p,
                    i_IB    = refclk_pads.n,
                    o_O     = self.video_refclk,
                    o_ODIV2 = refclk_div2,
                ),
                Instance("BUFG_GT", i_I=refclk_div2, o_O=refclk_buf),
            ]
            self.video_pll = video_pll = USPMMCM(speedgrade=-2)
            self.comb += video_pll.reset.eq(~cpu_reset_n | self.rst)
            video_pll.register_clkin(refclk_buf, video_refclk_freq/2)
            video_pll.create_clkout(self.cd_hdmi, 74.25e6, margin=0)
            platform.add_period_constraint(refclk_pads.p, 1e9/video_refclk_freq)
            platform.add_false_path_constraints(self.cd_sys.clk, self.cd_hdmi.clk, video_pll.clkin)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=100e6, with_gpio=False, with_psram=False,
        with_video_terminal=False, with_video_colorbars=False, video_refclk_freq=None, **kwargs):
        with_video = with_video_terminal or with_video_colorbars
        if with_video_terminal and with_video_colorbars:
            raise ValueError("Select either the video terminal or colorbars.")
        if with_video and (video_refclk_freq is None or video_refclk_freq <= 0):
            raise ValueError("Video requires --video-refclk-freq matching the 8T49N241 Q2 output.")
        platform = modretro_m64.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, video_refclk_freq if with_video else None)

        # SoCCore ----------------------------------------------------------------------------------
        kwargs.setdefault("integrated_rom_size",      0x10000)
        kwargs.setdefault("integrated_main_ram_size", 0x20000)
        if kwargs.get("uart_name") is None:
            kwargs["uart_name"] = "crossover" if kwargs.get("with_jtagbone", False) else "jtag_uart"
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on ModRetro M64", **kwargs)

        # JTAG UART / JTAGBone ---------------------------------------------------------------------
        for phy_name in ["uart_phy", "jtagbone_phy"]:
            phy = getattr(self, phy_name, None)
            if hasattr(phy, "cd_jtag"):
                # Include the BSCAN TDO register in JTAG timing analysis.
                platform.add_platform_command(
                    "create_clock -name jtag_clk -period 100 "
                    "[get_pins -hierarchical -filter {{REF_PIN_NAME == INTERNAL_TCK}}]")
                platform.add_false_path_constraints(phy.cd_jtag.clk, self.crg.cd_sys.clk)

        # GPIO -------------------------------------------------------------------------------------
        if with_gpio:
            self.gpio = GPIOTristate(platform.request("gpio"))

        # PSRAM ------------------------------------------------------------------------------------
        if with_psram:
            from litex.soc.cores.ram.apmemory import APMemory
            for n, size in enumerate([32*1024*1024]*3 + [64*1024*1024]):
                pads = platform.request("psram", n)
                psram = APMemory(pads, sys_clk_freq, size=size)
                setattr(self, f"psram{n}", psram)
                self.bus.add_slave(f"psram{n}", psram.bus,
                    SoCRegion(origin=0xa0000000 + n*0x04000000, size=size, cached=False))
                # Bound pad-to-sampler and output-register-to-pad delays for the sys/8 PHY.
                platform.add_platform_command(
                    "set_max_delay -datapath_only 5 -from [get_ports {{{dq}[*] {dqs}[*]}}]",
                    dq=pads.dq, dqs=pads.dqs)
                platform.add_platform_command(
                    "set_max_delay -datapath_only 5 -from [all_registers] "
                    "-to [get_ports {{{clk} {cs_n}}}]", clk=pads.clk, cs_n=pads.cs_n)
                # DQ/DM have two sys cycles of setup/hold, including tristate enable delays.
                platform.add_platform_command(
                    "set_max_delay -datapath_only 8 -from [all_registers] "
                    "-to [get_ports {{{dq}[*] {dqs}[*]}}]", dq=pads.dq, dqs=pads.dqs)

        # Video ------------------------------------------------------------------------------------
        if with_video:
            from litex.soc.cores.video import VideoUSPGTHHDMIPHY
            self.videophy = VideoUSPGTHHDMIPHY(platform.request("hdmi"), sys_clk_freq,
                refclk       = self.crg.video_refclk,
                refclk_freq  = video_refclk_freq,
                clock_domain = "hdmi",
                clk_freq     = 74.25e6,
            )
            if with_video_terminal:
                self.add_video_terminal(phy=self.videophy, timings="1280x720@60Hz", clock_domain="hdmi")
            if with_video_colorbars:
                self.add_video_colorbars(phy=self.videophy, timings="1280x720@60Hz", clock_domain="hdmi")
            platform.add_false_path_constraints(self.crg.cd_sys.clk, self.videophy.gthclk.cd_tx.clk)

            # Clock generator controls; leave its programmed output frequencies unchanged.
            clkgen_pads = platform.request("clkgen")
            self.clkgen_i2c    = I2CMaster(platform.request("clkgen_i2c"))
            self.clkgen_reset  = GPIOOut(clkgen_pads.rst_n, reset=1)
            self.clkgen_status = GPIOIn(Cat(clkgen_pads.int_n, clkgen_pads.lol))

            # SN75DP159: normal lane mapping, I2C control at 0x5e (schematic sheet 7).
            # OE must remain low for at least 100us before enabling the retimer (datasheet 9.3.1).
            hdmi_pads = platform.request("hdmi_ctrl")
            self.hdmi_i2c = I2CMaster(platform.request("hdmi_i2c"))
            self.hdmi_hpd = GPIOIn(hdmi_pads.hpd)
            self.hdmi_reset_timer = WaitTimer(math.ceil(100e-6*sys_clk_freq))
            self.comb += [
                hdmi_pads.pwr_en.eq(1),
                self.hdmi_reset_timer.wait.eq(self.videophy.ready),
                hdmi_pads.oe.eq(self.hdmi_reset_timer.done),
            ]

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=modretro_m64.Platform, description="LiteX SoC on ModRetro M64.")
    parser.add_target_argument("--sys-clk-freq", default=100e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-gpio",    action="store_true",       help="Enable GPIO on the 1.8V J25 expansion connector.")
    parser.add_target_argument("--with-psram",   action="store_true",       help="Enable all four x16 PSRAMs (160MiB total, sys/8 clock).")
    video_group = parser.target_group.add_mutually_exclusive_group()
    video_group.add_argument("--with-video-terminal",  action="store_true", help="Enable the 720p60 video terminal.")
    video_group.add_argument("--with-video-colorbars", action="store_true", help="Enable the 720p60 colorbars pattern.")
    parser.add_target_argument("--video-refclk-freq", type=float, help="Configured 8T49N241 Q2 GTH reference frequency in Hz.")
    parser.set_defaults(uart_name=None, integrated_rom_size=0x10000, integrated_main_ram_size=0x20000)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq         = args.sys_clk_freq,
        with_gpio            = args.with_gpio,
        with_psram           = args.with_psram,
        with_video_terminal  = args.with_video_terminal,
        with_video_colorbars = args.with_video_colorbars,
        video_refclk_freq    = args.video_refclk_freq,
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
