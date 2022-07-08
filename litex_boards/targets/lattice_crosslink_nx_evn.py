#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 David Corrigan <davidcorrigan714@gmail.com>
# Copyright (c) 2020 Alan Green <avg@google.com>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex_boards.platforms import lattice_crosslink_nx_evn

from litex.soc.cores.ram import NXLRAM
from litex.soc.cores.clock import NXPLL
from litex.build.io import CRG
from litex.build.generic_platform import *

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litex.build.lattice.oxide import oxide_args, oxide_argdict

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
        por_done  = Signal()
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        self.rst_n = platform.request("gsrn")
        self.specials += AsyncResetSynchronizer(self.cd_por, ~self.rst_n)

        # PLL
        self.submodules.sys_pll = sys_pll = NXPLL(platform=platform, create_output_port_clocks=True)
        sys_pll.register_clkin(self.cd_por.clk, hf_clk_freq)
        sys_pll.create_clkout(self.cd_sys, sys_clk_freq)
        self.specials += AsyncResetSynchronizer(self.cd_sys, ~self.sys_pll.locked | ~por_done )


# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    mem_map = {
        "rom"  : 0x00000000,
        "sram" : 0x40000000,
        "csr"  : 0xf0000000,
    }
    def __init__(self, sys_clk_freq=int(75e6), device="LIFCL-40-9BG400C", toolchain="radiant", with_led_chaser=True, **kwargs):
        platform = lattice_crosslink_nx_evn.Platform(device=device, toolchain=toolchain)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # SoCCore -----------------------------------------_----------------------------------------
        # Disable Integrated SRAM since we want to instantiate LRAM specifically for it
        kwargs["integrated_sram_size"] = 0
        # Make serial_pmods available
        platform.add_extension(lattice_crosslink_nx_evn.serial_pmods)
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Crosslink-NX Evaluation Board", **kwargs)

        # 128KB LRAM (used as SRAM) ---------------------------------------------------------------
        size = 128*kB
        self.submodules.spram = NXLRAM(32, size)
        self.register_mem("sram", self.mem_map["sram"], self.spram.bus, size)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = Cat(*[platform.request("user_led", i) for i in range(14)]),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on Crosslink-NX Eval Board")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",         action="store_true",        help="Build design.")
    target_group.add_argument("--load",          action="store_true",        help="Load bitstream.")
    target_group.add_argument("--toolchain",     default="radiant",          help="FPGA toolchain (radiant or prjoxide).")
    target_group.add_argument("--device",        default="LIFCL-40-9BG400C", help="FPGA device (LIFCL-40-9BG400C or LIFCL-40-8BG400CES).")
    target_group.add_argument("--sys-clk-freq",  default=75e6,               help="System clock frequency.")
    target_group.add_argument("--serial",        default="serial",           help="UART Pins (serial (requires R15 and R17 to be soldered) or serial_pmod[0-2]).")
    target_group.add_argument("--prog-target",   default="direct",           help="Programming Target (direct or flash).")
    builder_args(parser)
    soc_core_args(parser)
    oxide_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq = int(float(args.sys_clk_freq)),
        device       = args.device,
        toolchain    = args.toolchain,
        **soc_core_argdict(args)
    )
    builder = Builder(soc, **builder_argdict(args))
    builder_kargs = oxide_argdict(args) if args.toolchain == "oxide" else {}
    if args.build:
        builder.build(**builder_kargs)

    if args.load:
        prog = soc.platform.create_programmer(args.prog_target)
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
