#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Derek Mulcahy <derekmulcahy@gmail.com>
# Copyright (c) 2019-2020 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

import os

from migen import *

from litex.gen import *

from litex_boards.platforms import krtkl_snickerdoodle

from litex.soc.interconnect import axi
from litex.soc.interconnect import wishbone

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

# UTILS ---------------------------------------------------------------------------------------------

def load_ps7(soc, xci_file):
    odir = os.path.join("build", "krtkl_snickerdoodle", "gateware", "xci")
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

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, use_ps7_clk=False):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()

        # # #

        if use_ps7_clk:
            assert sys_clk_freq == 100e6
            self.comb += ClockSignal("sys").eq(ClockSignal("ps7"))
            self.comb += ResetSignal("sys").eq(ResetSignal("ps7") | self.rst)
        else:
            self.pll = pll = S7MMCM(speedgrade=-1)
            self.comb += pll.reset.eq(self.rst)
            pll.register_clkin(platform.request(platform.default_clk_name),
                               platform.default_clk_freq)
            pll.create_clkout(self.cd_sys, sys_clk_freq)
            # Ignore sys_clk to pll.clkin path created by SoC's rst.
            platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):

    def __init__(self, variant="z7-10", sys_clk_freq=100e6,
        with_led_chaser = True,
        ext_clk_freq    = None,
        xci_file        = None,
        **kwargs):
        platform = krtkl_snickerdoodle.Platform(variant=variant)

        # CRG --------------------------------------------------------------------------------------
        if ext_clk_freq:
            platform.default_clk_freq   = ext_clk_freq
            platform.default_clk_period = 1e9 / ext_clk_freq
        use_ps7_clk = (kwargs.get("cpu_type", None) == "zynq7000")
        self.crg = _CRG(platform, sys_clk_freq, use_ps7_clk)

        # SoCCore ----------------------------------------------------------------------------------
        if kwargs.get("cpu_type", None) == "zynq7000":
            kwargs["integrated_sram_size"] = 0
            kwargs["with_uart"]            = False
            self.mem_map = {"csr": 0x4000_0000}  # Zynq GP0 default
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Snickerdoodle", **kwargs)

        # Zynq7000 Integration ---------------------------------------------------------------------
        if kwargs.get("cpu_type", None) == "zynq7000":
            load_ps7(self, xci_file)

            # Connect AXI GP0 to the SoC with base address of 0x43c00000 (default one)
            wb_gp0  = wishbone.Interface()
            self.submodules += axi.AXI2Wishbone(
                axi          = self.cpu.add_axi_gp_master(),
                wishbone     = wb_gp0,
                base_address = self.mem_map["csr"])
            self.bus.add_master(master=wb_gp0)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=krtkl_snickerdoodle.Platform, description="LiteX SoC on Snickerdoodle.")
    parser.add_target_argument("--variant",      default="z7-10",           help="Board variant (z7-10 or z7-20).")
    parser.add_target_argument("--ext-clk-freq", default=10e6,  type=float, help="External Clock Frequency.")
    parser.add_target_argument("--sys-clk-freq", default=100e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--xci-file",     help="XCI file for PS7 configuration.")
    parser.add_target_argument("--target",       help="Vivado programmer target.")
    args = parser.parse_args()

    soc = BaseSoC(
        variant      = args.variant,
        sys_clk_freq = args.sys_clk_freq,
        ext_clk_freq = args.ext_clk_freq,
        xci_file     = args.xci_file,
        **parser.soc_argdict
    )
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"), target=args.target, device=1)

if __name__ == "__main__":
    main()
