#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019-2020 Florent Kermarrec <florent@enjoy-digital.fr>,
# SPDX-License-Identifier: BSD-2-Clause

import os
import argparse

from migen import *

from litex_boards.platforms import zybo_z7
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
        self.clock_domains.cd_sys = ClockDomain()

        # # #

        if use_ps7_clk:
            assert sys_clk_freq == 100e6
            self.comb += ClockSignal("sys").eq(ClockSignal("ps7"))
            self.comb += ResetSignal("sys").eq(ResetSignal("ps7"))
        else:
            self.submodules.pll = pll = S7PLL(speedgrade=-1)
            pll.register_clkin(platform.request("clk125"), 125e6)
            pll.create_clkout(self.cd_sys,       sys_clk_freq)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(100e6), **kwargs):
        platform = zybo_z7.Platform()

        if kwargs["uart_name"] == "serial": kwargs["uart_name"] = "usb_uart" # Use USB-UART Pmod on JB.

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident          = "LiteX SoC on Zybo Z7",
            ident_version  = True,
            **kwargs)

        # Zynq7000 Integration ---------------------------------------------------------------------
        if kwargs.get("cpu_type", None) == "zynq7000":
            # Get and set the pre-generated .xci FIXME: change location? add it to the repository?
            os.system("wget https://github.com/litex-hub/litex-boards/files/4967144/zybo_z7_ps7.txt")
            os.makedirs("xci", exist_ok=True)
            os.system("mv zybo_z7_ps7.txt xci/zybo_z7_ps7.xci")
            self.cpu.set_ps7_xci("xci/zybo_z7_ps7.xci")

            # Connect AXI GP0 to the SoC with base address of 0x43c00000 (default one)
            wb_gp0  = wishbone.Interface()
            self.submodules += axi.AXI2Wishbone(
                axi          = self.cpu.add_axi_gp_master(),
                wishbone     = wb_gp0,
                base_address = 0x43c00000)
            self.add_wb_master(wb_gp0)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # Leds -------------------------------------------------------------------------------------
        self.submodules.leds = LedChaser(
            pads         = platform.request_all("user_led"),
            sys_clk_freq = sys_clk_freq)
        self.add_csr("leds")

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on Zybo Z7")
    parser.add_argument("--build", action="store_true", help="Build bitstream")
    parser.add_argument("--load",  action="store_true", help="Load bitstream")
    builder_args(parser)
    soc_core_args(parser)
    vivado_build_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(**soc_core_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder.build(**vivado_build_argdict(args), run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".bit"), device=1)

if __name__ == "__main__":
    main()
