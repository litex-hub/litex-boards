#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Derek Mulcahy <derekmulcahy@gmail.com>
# Copyright (c) 2019-2020 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

import os

from migen import *

from litex_boards.platforms import snickerdoodle
from litex.build.xilinx.vivado import vivado_build_args, vivado_build_argdict

from litex.soc.interconnect import axi
from litex.soc.interconnect import wishbone

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

# UTILS ---------------------------------------------------------------------------------------------

def load_ps7(soc, xci_file):
    odir = os.path.join("build", "snickerdoodle", "gateware", "xci")
    os.makedirs(odir, exist_ok=True)
    file = "snickerdoodle_ps7.xci"
    dst = os.path.join(odir, file)
    if xci_file is None:
        src = "https://technicaltoys-support.s3.amazonaws.com/xci/" + file
        os.system("wget " + src + " -O " + dst)
    else:
        os.system("cp -p  " + xci_file + " " + dst)
    soc.cpu.set_ps7_xci(dst)

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq, use_ps7_clk=False):
        self.rst = Signal()
        self.clock_domains.cd_sys = ClockDomain()

        # # #

        if use_ps7_clk:
            assert sys_clk_freq == 100e6
            self.comb += ClockSignal("sys").eq(ClockSignal("ps7"))
            self.comb += ResetSignal("sys").eq(ResetSignal("ps7") | self.rst)
        else:
            self.submodules.pll = pll = S7MMCM(speedgrade=-1)
            self.comb += pll.reset.eq(self.rst)
            pll.register_clkin(platform.request(platform.default_clk_name),
                               platform.default_clk_freq)
            pll.create_clkout(self.cd_sys, sys_clk_freq)
            # Ignore sys_clk to pll.clkin path created by SoC's rst.
            platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):

    def __init__(self, variant="z7-10", sys_clk_freq=int(100e6), with_led_chaser=True,
        ext_clk_freq = None,
        xci_file     = None,
        **kwargs):

        platform = snickerdoodle.Platform(variant=variant)

        if ext_clk_freq:
            platform.default_clk_freq = ext_clk_freq
            platform.default_clk_period = 1e9 / ext_clk_freq

        if kwargs.get("cpu_type", None) == "zynq7000":
            kwargs["integrated_sram_size"] = 0
            kwargs["with_uart"]            = False
            self.mem_map = {"csr": 0x4000_0000}  # Zynq GP0 default

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident = "LiteX SoC on Snickerdoodle",
            **kwargs)

        # Zynq7000 Integration ---------------------------------------------------------------------
        if kwargs.get("cpu_type", None) == "zynq7000":
            load_ps7(self, xci_file)

            # Connect AXI GP0 to the SoC with base address of 0x43c00000 (default one)
            wb_gp0  = wishbone.Interface()
            self.submodules += axi.AXI2Wishbone(
                axi          = self.cpu.add_axi_gp_master(),
                wishbone     = wb_gp0,
                base_address = self.mem_map['csr'])
            self.add_wb_master(wb_gp0)

            use_ps7_clk = True
        else:
            use_ps7_clk = False

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq, use_ps7_clk)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on Snickerdoodle")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",        action="store_true", help="Build bitstream.")
    target_group.add_argument("--load",         action="store_true", help="Load bitstream.")
    target_group.add_argument("--variant",      default="z7-10",     help="Board variant (z7-10 or z7-20).")
    target_group.add_argument("--ext-clk-freq", default=10e6,  type=float, help="External Clock Frequency.")
    target_group.add_argument("--sys-clk-freq", default=100e6, type=float, help="System clock frequency.")
    target_group.add_argument("--xci-file",     help="XCI file for PS7 configuration.")
    target_group.add_argument("--target",       help="Vivado programmer target.")
    builder_args(parser)
    soc_core_args(parser)
    vivado_build_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        variant      = args.variant,
        sys_clk_freq = args.sys_clk_freq,
        ext_clk_freq = args.ext_clk_freq,
        xci_file     = args.xci_file,
        **soc_core_argdict(args)
    )
    builder = Builder(soc, **builder_argdict(args))
    builder.build(**vivado_build_argdict(args), run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"), target=args.target, device=1)

if __name__ == "__main__":
    main()
