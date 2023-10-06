#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2023 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# ./analog_pocket.py --sdram-rate=1:2 --uart-name=jtag_uart --build --load
# litex_term jtag --jtag-config=openocd_usb_blaster.cfg

from migen import *

from litex.gen import *

from litex_boards.platforms import analog_pocket

from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

from litex.build.io import DDROutput

from litex.soc.cores.clock import CycloneVPLL

from litedram.modules import AS4C32M16
from litedram.phy import GENSDRPHY, HalfRateGENSDRPHY

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, sdram_rate="1:1"):
        self.rst       = Signal()
        self.cd_sys    = ClockDomain()
        if sdram_rate == "1:2":
            self.cd_sys2x    = ClockDomain()
            self.cd_sys2x_ps = ClockDomain()
        else:
            self.cd_sys_ps = ClockDomain()

        # # #

        # Clk / Rst
        clk74 = platform.request("clk74a")

        # PLL
        self.pll = pll = CycloneVPLL()
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk74, 74.25e6)
        pll.create_clkout(self.cd_sys,    sys_clk_freq)
        if sdram_rate == "1:2":
            pll.create_clkout(self.cd_sys2x,    2*sys_clk_freq)
            pll.create_clkout(self.cd_sys2x_ps, 2*sys_clk_freq, phase=180)  # Idealy 90° but needs to be increased.
        else:
            pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=90)

        # SDRAM clock
        sdram_clk = ClockSignal("sys2x_ps" if sdram_rate == "1:2" else "sys_ps")
        self.specials += DDROutput(1, 0, platform.request("sdram_clock"), sdram_clk)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=50e6, sdram_rate="1:1", **kwargs):
        platform = analog_pocket.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, sdram_rate)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Analog Pocket", **kwargs)

        # SDR SDRAM --------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            sdrphy_cls = HalfRateGENSDRPHY if sdram_rate == "1:2" else GENSDRPHY
            self.sdrphy = sdrphy_cls(platform.request("sdram"), sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.sdrphy,
                module        = AS4C32M16(sys_clk_freq, sdram_rate),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=analog_pocket.Platform, description="LiteX SoC on Analog Pocket.")
    parser.add_target_argument("--sys-clk-freq", default=50e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--sdram-rate",   default="1:1",            help="SDRAM Rate (1:1 Full Rate or 1:2 Half Rate).")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq = args.sys_clk_freq,
        sdram_rate   = args.sdram_rate,
        **parser.soc_argdict
    )
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram").replace(".sof", ".rbf"))

if __name__ == "__main__":
    main()
