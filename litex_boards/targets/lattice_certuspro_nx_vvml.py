#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2024 Enjoy-Digital <enjoy-digital.fr>
#
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from litex_boards.platforms import lattice_certuspro_nx_vvml

from litex.build.generic_platform import *

from litex.soc.cores.clock import *
from litex.soc.integration.soc import *
from litex.soc.integration.builder import *

from litex.soc.cores.led import LedChaser
from litex.soc.cores.gpio import GPIOIn

from litedram.modules import EM6GA16L
from litedram.phy.rpc.nxphy import NXRPCPHY

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_rpcdram=False):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()
        self.cd_por = ClockDomain()
        if with_rpcdram:
            self.cd_init    = ClockDomain()
            self.cd_sys4x   = ClockDomain()
            self.cd_sys4x_i = ClockDomain()

        # # #

        self.stop  = Signal()
        self.reset = Signal()

        # Clk / Rst
        self.clk24 = platform.request("clk24")
        self.rst_n = platform.request("gsrn")

        # Built in OSC
        self.hf_clk = NXOSCA(platform)
        hf_clk_freq = 25e6
        self.hf_clk.create_hf_clk(self.cd_por, hf_clk_freq)

        # Power on reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))
        self.specials += AsyncResetSynchronizer(self.cd_por, ~self.rst_n)

        # PLL
        self.sys_pll = sys_pll = NXPLL(platform=platform, create_output_port_clocks=True)
        self.comb += sys_pll.reset.eq(self.rst | ~por_done)
        sys_pll.register_clkin(self.clk24, 24e6)
        if with_rpcdram:
            # Edge clock (sys4x) for the RPC DRAM PHY, sys from the edge clock divider.
            sys_pll.create_clkout(self.cd_sys4x_i, 4*sys_clk_freq)
            self.comb += self.cd_init.clk.eq(self.clk24)
            self.specials += [
                Instance("ECLKSYNC",
                    p_STOP_EN = "ENABLE",
                    i_ECLKIN  = self.cd_sys4x_i.clk,
                    i_STOP    = self.stop,
                    o_ECLKOUT = self.cd_sys4x.clk),
                Instance("ECLKDIV",
                    p_ECLK_DIV = "4",
                    i_SLIP     = 0,
                    i_ECLKIN   = self.cd_sys4x.clk,
                    i_DIVRST   = self.reset,
                    o_DIVOUT   = self.cd_sys.clk),
                AsyncResetSynchronizer(self.cd_init, ~sys_pll.locked),
                AsyncResetSynchronizer(self.cd_sys,  ~sys_pll.locked | self.reset),
            ]
            platform.add_period_constraint(self.cd_sys.clk, 1e9/sys_clk_freq)
        else:
            sys_pll.create_clkout(self.cd_sys, sys_clk_freq)
            self.specials += AsyncResetSynchronizer(self.cd_sys, ~self.sys_pll.locked)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=75e6, toolchain="radiant",
        with_led_chaser = True,
        with_rpcdram    = False,
        with_buttons    = False,
        **kwargs):
        platform = lattice_certuspro_nx_vvml.Platform(toolchain=toolchain)

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, with_rpcdram=with_rpcdram)

        # SoCCore -----------------------------------------_----------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on CertusPro-NX VVML Eval Board", **kwargs)

        # RPC DRAM ---------------------------------------------------------------------------------
        if with_rpcdram and not self.integrated_main_ram_size:
            # First DRAM only for now (STB/CS# of the second one are held high by the PHY).
            self.ddrphy = NXRPCPHY(
                pads         = platform.request("rpcdram"),
                sys_clk_freq = sys_clk_freq)
            self.comb += [
                self.crg.stop.eq(self.ddrphy.init.stop),
                self.crg.reset.eq(self.ddrphy.init.reset),
            ]
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = EM6GA16L(sys_clk_freq, "1:4"),
                l2_cache_size = kwargs.get("l2_size", 8192))

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

        # Buttons ---------------------------------------------------------------------------------
        if with_buttons:
            self.buttons = GPIOIn(Cat(platform.request_all("user_btn")))

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser           import LiteXArgumentParser
    from litex_boards.extensions.pmod import add_pmod_args, add_pmods
    parser = LiteXArgumentParser(platform=lattice_certuspro_nx_vvml.Platform, description="LiteX SoC on CertusPro-NX VVML EVN Board.")
    parser.add_target_argument("--sys-clk-freq", default=75e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--flash",        action="store_true",      help="Flash bitstream to SPI Flash.")
    parser.add_target_argument("--with-rpcdram", action="store_true",      help="Enable RPC DRAM.")
    parser.add_target_argument("--with-buttons", action="store_true",      help="Enable Buttons.")
    add_pmod_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq = args.sys_clk_freq,
        with_rpcdram = args.with_rpcdram,
        with_buttons = args.with_buttons,
        **parser.soc_argdict
    )
    add_pmods(soc, args.pmod)

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.flash(0, builder.get_bitstream_filename(mode="flash"))

if __name__ == "__main__":
    main()
