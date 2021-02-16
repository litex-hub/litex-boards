#!/usr/bin/env python3
#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Hans Baier <hansfbaier@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause
"""
    This class provides basic support for the Arrow SoCKit.
    Since the SoCKit has its USB2UART attached to the HPS
    system, it is not available to the FPGA and thus the only
    way to communicate is via JTAG serial which is configured
    by default.
    To access it, you can use the nios2_terminal application
    included in the Intel/Altera quartus distribution.
"""

import os
import argparse

from migen.fhdl.module      import Module
from migen.fhdl.structure   import Signal, ClockDomain, ClockSignal
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.soc.cores.clock           import CycloneVPLL
from litex.soc.integration.builder   import Builder, builder_args, builder_argdict
from litex.soc.integration.soc_core  import SoCCore
from litex.soc.integration.soc_sdram import soc_sdram_argdict, soc_sdram_args
from litex.soc.cores.led             import LedChaser

from litex.build.io import DDROutput
from litex.build.generic_platform  import Pins, IOStandard, Subsignal

from litex_boards.platforms import arrow_sockit

from litedram.modules import _TechnologyTimings, _SpeedgradeTimings, SDRModule, AS4C32M16
from litedram.phy     import HalfRateGENSDRPHY, GENSDRPHY

# DRAM Module for XS board v2.2 ----------------------------------------------------------------------
class W9825G6KH6(SDRModule):
    """
    Winbond W9825G6KH-6 chip on Mister SDRAM XS board v2.2
    This is the smallest and cheapest module.
    running it at 100MHz (1:2 if system clock is 50MHz)
    works well on my SoCKit and all 32MB test error free
    I get a number of data errors if I run it at 50MHz,
    so this defaults to 1:2. If you want to use a higher
    system clock (eg 100MHz), you might want to consider
    using 1:1 clocking, because the -6 speedgrade 
    can be clocked up to 166MHz (CL3) or 133MHz (CL2)
    """
    # geometry
    nbanks = 4
    nrows  = 8192
    ncols  = 512

    @staticmethod
    def clock_cycles_to_ns(cycles, clk_freq, sdram_rate) -> float:
        d = {
            "1:1" : 1,
            "1:2" : 2,
            "1:4" : 4
        }
        return cycles / (d[sdram_rate] * clk_freq) / 1e-9

    def __init__(self, clk_freq, sdram_rate):
        # The datasheet specifies tWr in clock cycles, not in
        # ns but to me it looks like litedram expects
        # ns for these two parameters, so I have to convert them
        # to ns first.
        tWr  = self.clock_cycles_to_ns(2, clk_freq, sdram_rate)
        tRRD = self.clock_cycles_to_ns(2, clk_freq, sdram_rate)
        self.technology_timings = _TechnologyTimings(tREFI=64e6/8000, tWTR=(2, None), tCCD=(1, None), tRRD=(None, tRRD))
        self.speedgrade_timings = {"default": _SpeedgradeTimings(tRP=15, tRCD=15, tWR=tWr, tRFC=(None, 60), tFAW=None, tRAS=42)}
        super().__init__(clk_freq, sdram_rate)

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq, with_sdram=False, sdram_rate="1:2"):
        self.sdram_rate = sdram_rate
        self.rst = Signal()
        self.clock_domains.cd_sys    = ClockDomain()
        if with_sdram:
            if sdram_rate == "1:2":
                self.clock_domains.cd_sys2x    = ClockDomain()
                self.clock_domains.cd_sys2x_ps = ClockDomain(reset_less=True)
            else:
                self.clock_domains.cd_sys_ps = ClockDomain(reset_less=True)

        # Clk / Rst
        clk50 = platform.request("clk50")

        # PLL
        self.submodules.pll = pll = CycloneVPLL(speedgrade="-C6")
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk50, 50e6)
        pll.create_clkout(self.cd_sys,    sys_clk_freq)
        if with_sdram:
            if sdram_rate == "1:2":
                pll.create_clkout(self.cd_sys2x,    2*sys_clk_freq)
                pll.create_clkout(self.cd_sys2x_ps, 2*sys_clk_freq, phase=180)  # Idealy 90° but needs to be increased.
            else:
                pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=90)

        # SDRAM clock
        if with_sdram:
            sdram_clk = ClockSignal("sys2x_ps" if sdram_rate == "1:2" else "sys_ps")
            self.specials += DDROutput(1, 0, platform.request("sdram_clock"), sdram_clk)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(50e6), revision="revd", sdram_rate="1:2", mister_sdram=None, **kwargs):
        platform = arrow_sockit.Platform(revision)

        # Defaults to UART over JTAG because serial is attached to the HPS and cannot be used.
        if kwargs["uart_name"] == "serial":
            kwargs["uart_name"] = "jtag_atlantic"

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident          = "LiteX SoC on the Arrow SoCKit",
            ident_version  = True,
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq, with_sdram=mister_sdram != None, sdram_rate=sdram_rate)

        # Leds -------------------------------------------------------------------------------------
        self.submodules.leds = LedChaser(
            pads         = platform.request_all("user_led"),
            sys_clk_freq = sys_clk_freq)
        self.add_csr("leds")

        if mister_sdram == "xs_v22":
            sdrphy_cls = HalfRateGENSDRPHY if sdram_rate == "1:2" else GENSDRPHY
            self.submodules.sdrphy = sdrphy_cls(platform.request("sdram"), sys_clk_freq)
            self.add_sdram("sdram",
                phy                     = self.sdrphy,
                module                  = W9825G6KH6(sys_clk_freq, sdram_rate),
                origin                  = self.mem_map["main_ram"],
                size                    = kwargs.get("max_sdram_size", 0x40000000),
                l2_cache_size           = kwargs.get("l2_size", 8192),
                l2_cache_min_data_width = kwargs.get("min_l2_data_width", 128),
                l2_cache_reverse        = True
            )

        if mister_sdram == "xs_v24":
            sdrphy_cls = HalfRateGENSDRPHY if sdram_rate == "1:2" else GENSDRPHY
            self.submodules.sdrphy = sdrphy_cls(platform.request("sdram"), sys_clk_freq)
            self.add_sdram("sdram",
                phy                     = self.sdrphy,
                module                  = AS4C32M16(sys_clk_freq, sdram_rate),
                origin                  = self.mem_map["main_ram"],
                size                    = kwargs.get("max_sdram_size", 0x40000000),
                l2_cache_size           = kwargs.get("l2_size", 8192),
                l2_cache_min_data_width = kwargs.get("min_l2_data_width", 128),
                l2_cache_reverse        = True
            )

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on the Arrow/Terasic SoCKit")
    parser.add_argument("--single-rate-sdram",   action="store_true", help="clock SDRAM with 1x the sytem clock (instead of 2x)")
    parser.add_argument("--mister-sdram-xs-v22", action="store_true", help="Use optional MiSTer SDRAM module XS v2.2 on J2 on GPIO daughter card")
    parser.add_argument("--mister-sdram-xs-v24", action="store_true", help="Use optional MiSTer SDRAM module XS v2.4 on J2 on GPIO daughter card")
    parser.add_argument("--build",               action="store_true", help="Build bitstream")
    parser.add_argument("--load",                action="store_true", help="Load bitstream")
    parser.add_argument("--revision",            default="revd",      help="Board revision: revb (default), revc or revd")
    parser.add_argument("--sys-clk-freq",        default=50e6,        help="System clock frequency (default: 50MHz)")
    builder_args(parser)
    soc_sdram_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq        = int(float(args.sys_clk_freq)),
        revision            = args.revision,
        sdram_rate          = "1:1" if args.single_rate_sdram else "1:2",
        mister_sdram        = "xs_v22" if args.mister_sdram_xs_v22 else "xs_v24" if args.mister_sdram_xs_v24 else None,
        **soc_sdram_argdict(args)
    )
    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".sof"))

if __name__ == "__main__":
    main()
