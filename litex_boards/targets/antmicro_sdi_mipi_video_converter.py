#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2023 Antmicro <www.antmicro.com>
# SPDX-License-Identifier: BSD-2-Clause

import os

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from litex_boards.platforms import antmicro_sdi_mipi_video_converter

from litex.soc.cores.ram import NXLRAM
from litex.soc.cores.clock import NXPLL
from litex.build.generic_platform import *

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

kB = 1024
mB = 1024*kB

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst    = Signal()
        self.cd_por = ClockDomain()
        self.cd_sys = ClockDomain()

        # Built in OSC
        self.hf_clk = NXOSCA()
        hf_clk_freq = 25e6
        self.hf_clk.create_hf_clk(self.cd_por, hf_clk_freq)

        # Power on reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # PLL
        self.sys_pll = sys_pll = NXPLL(platform=platform, create_output_port_clocks=True)
        self.comb += sys_pll.reset.eq(self.rst)
        sys_pll.register_clkin(self.cd_por.clk, hf_clk_freq)
        sys_pll.create_clkout(self.cd_sys, sys_clk_freq)
        self.specials += AsyncResetSynchronizer(self.cd_sys, ~self.sys_pll.locked | ~por_done)


# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    mem_map = {
        "rom"      : 0x00000000,
        "sram"     : 0x40000000,
        "main_ram" : 0x60000000,
        "csr"      : 0xf0000000,
    }

    def __init__(self, sys_clk_freq=int(75e6), device="LIFCL-40-9BG256C", toolchain="radiant",
        with_led_chaser = True,
        **kwargs):
        platform = antmicro_sdi_mipi_video_converter.Platform(device=device, toolchain=toolchain)

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore -----------------------------------------_----------------------------------------

        # Disable Integrated SRAM since we want to instantiate LRAM specifically for it
        kwargs["integrated_sram_size"] = 0
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Antmicro SDI MIPI Video Converter Board", **kwargs)

        # 128KB LRAM (used as SRAM) ---------------------------------------------------------------
        self.spram = NXLRAM(32, 64*kB)
        self.bus.add_slave("sram", self.spram.bus, SoCRegion(origin=self.mem_map["sram"], size=16*kB))

        self.main_ram = NXLRAM(32, 64*kB)
        self.bus.add_slave("main_ram", self.main_ram.bus, SoCRegion(origin=self.mem_map["main_ram"], size=64*kB))

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------


def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=antmicro_sdi_mipi_video_converter.Platform, description="LiteX SoC on Antmicro SDI MIPI Video Converter Board.")
    parser.add_target_argument("--device",        default="LIFCL-40-9BG256C", help="FPGA device (LIFCL-40-9BG400C, LIFCL-40-8BG400CES, or LIFCL-40-8BG400CES2).")
    parser.add_target_argument("--sys-clk-freq",  default=75e6,               help="System clock frequency.")
    parser.add_target_argument("--programmer",    default="radiant",          help="Programmer (radiant or ecpprog).")
    parser.add_target_argument("--prog-target",   default="direct",           help="Programming Target (direct or flash).")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq = int(float(args.sys_clk_freq)),
        device       = args.device,
        toolchain    = args.toolchain,
        **parser.soc_argdict
    )
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer(args.prog_target, args.programmer)
        if args.programmer == "ecpprog" and args.prog_target == "flash":
            prog.flash(address=args.address,
                       bitstream=builder.get_bitstream_filename(mode="sram"))
        else:
            if args.programmer == "radiant":
                os.system("sudo modprobe -rf ftdi_sio")

            prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

            if args.programmer == "radiant":
                os.system("sudo modprobe ftdi_sio")


if __name__ == "__main__":
    main()
