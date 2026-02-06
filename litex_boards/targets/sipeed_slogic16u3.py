#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import *

from litex.soc.integration.soc_core import *
from litex.soc.integration.builder  import *

from litex_boards.platforms.sipeed_slogic16u3 import Platform

# CRG ----------------------------------------------------------------------------------------------

def osca_div(sys_clk_freq, fosc_hz=207.32e6):
    div = int(round(fosc_hz / sys_clk_freq))
    div = max(2, min(126, div))
    if div == 3:
        return 3
    if div & 1:
        div += 1
        if div > 126:
            div -= 2
    return div


class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.cd_sys = ClockDomain()

        # # #

        self.specials += Instance("OSCA",
            p_FREQ_DIV = osca_div(sys_clk_freq),
            i_OSCEN    = 1,
            o_OSCOUT   = self.cd_sys.clk
        )

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=20.732e6, **kwargs):
        platform = Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Sipeed Slogic16U3", **kwargs)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=Platform, description="LiteX SoC on Sipeed Slogic16U3.")
    parser.add_target_argument("--flash",        action="store_true",          help="Flash Bitstream.")
    parser.add_target_argument("--sys-clk-freq", default=20.732e6, type=float, help="System clock frequency.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq = args.sys_clk_freq,
        **parser.soc_argdict
    )

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.flash(0, builder.get_bitstream_filename(mode="flash", ext=".fs"), external=True)

if __name__ == "__main__":
    main()
