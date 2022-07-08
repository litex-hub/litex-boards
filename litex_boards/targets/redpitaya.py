#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Gwenhael Goavec-Merou <gwenhael.goavec-merou@trabucayre.com>
# SPDX-License-Identifier: BSD-2-Clause

import os

from migen import *

from litex_boards.platforms import redpitaya
from litex.build.xilinx.vivado import vivado_build_args, vivado_build_argdict

from litex.soc.interconnect import axi
from litex.soc.interconnect import wishbone

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

# CRG ----------------------------------------------------------------------------------------------


class _CRG(Module):
    def __init__(self, platform, sys_clk_freq, use_ps7_clk=False):
        self.rst = Signal()
        self.clock_domains.cd_sys = ClockDomain()

        # # #

        if use_ps7_clk:
            assert sys_clk_freq == 125e6
            self.comb += ClockSignal("sys").eq(ClockSignal("ps7"))
            self.comb += ResetSignal("sys").eq(ResetSignal("ps7") | self.rst)
        else:
            self.submodules.pll = pll = S7PLL(speedgrade=-1)
            self.comb += pll.reset.eq(self.rst)
            pll.register_clkin(platform.request(platform.default_clk_name), platform.default_clk_freq)
            pll.create_clkout(self.cd_sys,      sys_clk_freq)
            platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

# BaseSoC ------------------------------------------------------------------------------------------


class BaseSoC(SoCCore):
    def __init__(self, board, sys_clk_freq=int(100e6), with_led_chaser=True, **kwargs):
        platform = redpitaya.Platform(board)

        # CRG --------------------------------------------------------------------------------------
        use_ps7_clk  = (kwargs.get("cpu_type", None) == "zynq7000")
        sys_clk_freq = 125e6 if use_ps7_clk else sys_clk_freq
        self.submodules.crg = _CRG(platform, sys_clk_freq, use_ps7_clk)

        # SoCCore ----------------------------------------------------------------------------------
        if kwargs["uart_name"] == "serial":
            kwargs["uart_name"] = "usb_uart"
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Zebboard", **kwargs)

        # Zynq7000 Integration ---------------------------------------------------------------------
        if kwargs.get("cpu_type", None) == "zynq7000":
            # Get and set the pre-generated .xci FIXME: change location? add it to the repository?
            os.system("wget https://kmf2.trabucayre.com/redpitaya_ps7.txt")
            os.makedirs("xci", exist_ok=True)
            os.system("cp redpitaya_ps7.txt xci/redpitaya_ps7.xci")
            self.cpu.set_ps7_xci("xci/redpitaya_ps7.xci")

            # Connect AXI GP0 to the SoC with base address of 0x43c00000 (default one)
            wb_gp0  = wishbone.Interface()
            self.submodules += axi.AXI2Wishbone(
                axi          = self.cpu.add_axi_gp_master(),
                wishbone     = wb_gp0,
                base_address = 0x43c00000)
            self.bus.add_master(master=wb_gp0)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------


def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on Zedboard")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",        action="store_true",   help="Build design.")
    target_group.add_argument("--load",         action="store_true",   help="Load bitstream.")
    target_group.add_argument("--sys-clk-freq", default=100e6,         help="System clock frequency.")
    target_group.add_argument("--board",        default="redpitaya14", help="Board type (redpitaya14 or redpitaya16).")
    builder_args(parser)
    soc_core_args(parser)
    vivado_build_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        board = args.board,
        sys_clk_freq = int(float(args.sys_clk_freq)),
        **soc_core_argdict(args)
    )
    builder = Builder(soc, **builder_argdict(args))
    if args.build:
        builder.build(**vivado_build_argdict(args))

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"), device=1)

if __name__ == "__main__":
    main()
