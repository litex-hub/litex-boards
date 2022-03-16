#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Joseph FAYE <joseph-wagane.faye@insa-rennes.fr>
# SPDX-License-Identifier: BSD-2-Clause

import os
import argparse
import importlib

from migen import *

from litex_boards.platforms import xilinx_zcu102 as zcu102

from litex.build.io import CRG

from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

from litex.soc.cores.led import LedChaser


# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq, with_ethernet=False, with_led_chaser=True, **kwargs):
        platform = zcu102.Platform()

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
                         ident="LiteX SoC on ZCU102",
                         **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = CRG(sys_clk_freq)

        # Leds -------------------------------------------------------------------------------------
        try:
            if with_led_chaser:
                self.submodules.leds = LedChaser(
                    pads=platform.request_all("user_led"),
                    sys_clk_freq=sys_clk_freq)
        except:
            pass


# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on ZCU102")
    parser.add_argument("--build", action="store_true", help="Build bitstream.")
    parser.add_argument("--load", action="store_true", help="Load bitstream.")
    parser.add_argument("--sys-clk-freq", default=125e6, help="System clock generator.")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(sys_clk_freq=int(float(args.sys_clk_freq)), **soc_core_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".bit"))


if __name__ == "__main__":
    main()