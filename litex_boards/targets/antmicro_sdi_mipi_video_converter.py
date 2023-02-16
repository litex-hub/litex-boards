#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2023 Antmicro <www.antmicro.com>
# SPDX-License-Identifier: BSD-2-Clause

import os

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

import litex_boards.platforms.antmicro_sdi_mipi_video_converter

from litex.soc.cores.ram import NXLRAM
from litex.soc.cores.clock import NXPLL
from litex.build.generic_platform import *

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litex.build.lattice.oxide import oxide_args, oxide_argdict
from litex.build.lattice.radiant import radiant_build_argdict, radiant_build_args

kB = 1024
mB = 1024*kB


# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.clock_domains.cd_por = ClockDomain()
        self.clock_domains.cd_sys = ClockDomain()

        # Built in OSC
        self.submodules.hf_clk = NXOSCA()
        hf_clk_freq = 25e6
        self.hf_clk.create_hf_clk(self.cd_por, hf_clk_freq)

        # Power on reset
        por_count = Signal(16, reset=2**16-1)
        por_done = Signal()
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # PLL
        self.submodules.sys_pll = sys_pll = NXPLL(platform=platform, create_output_port_clocks=True)
        sys_pll.register_clkin(self.cd_por.clk, hf_clk_freq)
        sys_pll.create_clkout(self.cd_sys, sys_clk_freq)
        self.specials += AsyncResetSynchronizer(self.cd_sys, ~self.sys_pll.locked | ~por_done)


# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    mem_map = {
        "rom": 0x00000000,
        "sram": 0x40000000,
        "main_ram": 0x60000000,
        "csr": 0xf0000000,
    }

    def __init__(self, sys_clk_freq=int(75e6), device="LIFCL-40-9BG256C", toolchain="radiant", with_led_chaser=True, **kwargs):
        platform = litex_boards.platforms.antmicro_sdi_mipi_video_converter.Platform(
            device=device, toolchain=toolchain)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # SoCCore -----------------------------------------_----------------------------------------

        # Disable Integrated SRAM since we want to instantiate LRAM specifically for it
        kwargs["integrated_sram_size"] = 0
        SoCCore.__init__(self, platform, sys_clk_freq,
                         ident="LiteX SoC on Crosslink-NX Evaluation Board", **kwargs)

        # 128KB LRAM (used as SRAM) ---------------------------------------------------------------

        self.submodules.spram = NXLRAM(32, 64*kB)
        self.bus.add_slave("sram", self.spram.bus, SoCRegion(origin=self.mem_map["sram"], size=16*kB))

        self.submodules.main_ram = NXLRAM(32, 64*kB)
        self.bus.add_slave("main_ram", self.main_ram.bus, SoCRegion(origin=self.mem_map["main_ram"], size=64*kB))

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads=Cat(*[platform.request("user_led", i) for i in range(2)]),
                sys_clk_freq=sys_clk_freq)

# Build --------------------------------------------------------------------------------------------


def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on Crosslink-NX Eval Board")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",         action="store_true",        help="Build design.")
    target_group.add_argument("--load",          action="store_true",        help="Load bitstream.")
    target_group.add_argument("--toolchain",     default="radiant",          help="FPGA toolchain (radiant or prjoxide).")
    target_group.add_argument("--device",        default="LIFCL-40-9BG256C", help="FPGA device (LIFCL-40-9BG400C, LIFCL-40-8BG400CES, or LIFCL-40-8BG400CES2).")
    target_group.add_argument("--sys-clk-freq",  default=75e6,               help="System clock frequency.")
    target_group.add_argument("--programmer",    default="radiant",          help="Programmer (radiant or ecpprog).")
    target_group.add_argument("--prog-target",   default="direct",           help="Programming Target (direct or flash).")

    builder_args(parser)
    soc_core_args(parser)
    oxide_args(parser)
    radiant_build_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq=int(float(args.sys_clk_freq)),
        device=args.device,
        toolchain=args.toolchain,
        **soc_core_argdict(args)
    )

    builder = Builder(soc, **builder_argdict(args))
    builder_kargs = oxide_argdict(args) if args.toolchain == "oxide" else radiant_build_argdict(args)
    if args.build:
        builder.build(**builder_kargs)

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
