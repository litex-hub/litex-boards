#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2021 Gwenhael Goavec-Merou <gwenhael.goavec-merou@trabucayre.com>
# SPDX-License-Identifier: BSD-2-Clause

import os
import argparse

from migen import *

from litex_boards.platforms import quicklogic_quickfeather

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.gpio import *

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, is_eoss3_cpu=False):
        self.rst = Signal()
        self.clock_domains.cd_sys = ClockDomain()

        # # #

        class Open(Signal): pass

        if is_eoss3_cpu:
            self.comb += ClockSignal("sys").eq(ClockSignal("Sys_Clk0"))
            self.comb += ResetSignal("sys").eq(ResetSignal("Sys_Clk0") | self.rst)
        else:
            self.specials += Instance("qlal4s3b_cell_macro",
                o_Sys_Clk0     = self.cd_sys.clk,
                o_Sys_Clk0_Rst = self.cd_sys.rst,
                o_Sys_Clk1     = Open(),
                o_Sys_Clk1_Rst = Open(),
            )

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(10e6), with_led_chaser=True, with_gpioin=True, **kwargs):
        platform = quicklogic_quickfeather.Platform()

        # SoCCore ----------------------------------------------------------------------------------
        if kwargs.get("cpu_type", None) == "eos-s3":
            is_eoss3_cpu = True
        else:
            is_eoss3_cpu = False
            kwargs["cpu_type"]  = None
        kwargs["with_uart"] = False
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident          = "LiteX SoC on QuickLogic QuickFeather",
            ident_version  = True,
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, is_eoss3_cpu)

        # GPIOIn -> interrupt test
        if with_gpioin:
            self.submodules.gpio = GPIOIn(
                pads         = platform.request_all("user_btn_n"), with_irq=True)
            self.add_csr("gpio")
            self.irq.add("gpio", use_loc_if_exists=True)
        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)
            if is_eoss3_cpu:
                self.add_csr("leds")

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on Quicklogic QuickFeather")
    parser.add_argument("--build", action="store_true", help="Build bitstream")
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(**soc_core_argdict(args))
    builder = Builder(soc, compile_software=False)
    builder.build(run=args.build)

if __name__ == "__main__":
    main()
