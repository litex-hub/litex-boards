#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2015 Robert Jordens <jordens@gmail.com>
# Copyright (c) 2015 Sebastien Bourdeauducq <sb@m-labs.hk>
# Copyright (c) 2015 Yann Sionneau <yann.sionneau@gmail.com>
# Copyright (c) 2016-2017 Tim 'mithro' Ansell <mithro@mithis.com>
# Copyright (c) 2019 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from fractions import Fraction

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from litex_boards.platforms import digilent_atlys

from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litedram.modules import MT47H64M16
from litedram.phy import s6ddrphy

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.cd_sys           = ClockDomain()
        self.cd_sdram_half    = ClockDomain()
        self.cd_sdram_full_wr = ClockDomain()
        self.cd_sdram_full_rd = ClockDomain()

        self.reset = Signal()

        # # #

        # Input clock ------------------------------------------------------------------------------
        clk100_freq = int(100e6)
        clk100      = platform.request("clk100")
        clk100b     = Signal()
        self.specials += Instance("BUFIO2",
            p_DIVIDE=1, p_DIVIDE_BYPASS="TRUE",
            p_I_INVERT="FALSE",
            i_I=clk100, o_DIVCLK=clk100b)

        # PLL --------------------------------------------------------------------------------------
        pll_lckd         = Signal()
        pll_fb           = Signal()
        pll_sdram_full   = Signal()
        pll_sdram_half_a = Signal()
        pll_sdram_half_b = Signal()
        pll_unused       = Signal()
        pll_sys          = Signal()
        pll_periph       = Signal()

        f0 = clk100_freq
        f = Fraction(int(sys_clk_freq), int(f0))
        n, m = f.denominator, f.numerator
        assert f0 / n * m == sys_clk_freq
        p = 8

        self.specials.pll = Instance(
            "PLL_ADV",
            name="crg_pll_adv",
            p_SIM_DEVICE="SPARTAN6", p_BANDWIDTH="OPTIMIZED", p_COMPENSATION="INTERNAL",
            p_REF_JITTER=.01,
            i_DADDR=0, i_DCLK=0, i_DEN=0, i_DI=0, i_DWE=0, i_RST=0, i_REL=0,
            p_DIVCLK_DIVIDE=1,
            # Input Clocks (100MHz)
            i_CLKIN1=clk100b,
            p_CLKIN1_PERIOD=1e9/f0,
            i_CLKIN2=0,
            p_CLKIN2_PERIOD=0.,
            i_CLKINSEL=1,
            # Feedback
            i_CLKFBIN=pll_fb, o_CLKFBOUT=pll_fb, o_LOCKED=pll_lckd,
            p_CLK_FEEDBACK="CLKFBOUT",
            p_CLKFBOUT_MULT=m*p//n, p_CLKFBOUT_PHASE=0.,
            # (300MHz) sdram wr rd
            o_CLKOUT0=pll_sdram_full, p_CLKOUT0_DUTY_CYCLE=.5,
            p_CLKOUT0_PHASE=0., p_CLKOUT0_DIVIDE=p//4,
            # unused?
            o_CLKOUT1=pll_unused, p_CLKOUT1_DUTY_CYCLE=.5,
            p_CLKOUT1_PHASE=0., p_CLKOUT1_DIVIDE=15,
            # (150MHz) sdram_half - sdram dqs adr ctrl
            o_CLKOUT2=pll_sdram_half_a, p_CLKOUT2_DUTY_CYCLE=.5,
            p_CLKOUT2_PHASE=270., p_CLKOUT2_DIVIDE=p//2,
            # (150Mhz) off-chip ddr
            o_CLKOUT3=pll_sdram_half_b, p_CLKOUT3_DUTY_CYCLE=.5,
            p_CLKOUT3_PHASE=250., p_CLKOUT3_DIVIDE=p//2,
            # ( 50MHz) periph
            o_CLKOUT4=pll_periph, p_CLKOUT4_DUTY_CYCLE=.5,
            p_CLKOUT4_PHASE=0., p_CLKOUT4_DIVIDE=20,
            # ( 75MHz) sysclk
            o_CLKOUT5=pll_sys, p_CLKOUT5_DUTY_CYCLE=.5,
            p_CLKOUT5_PHASE=0., p_CLKOUT5_DIVIDE=p//1,
        )

        # Power on reset
        reset = ~platform.request("cpu_reset") | self.reset
        self.cd_por = ClockDomain()
        por = Signal(max=1 << 11, reset=(1 << 11) - 1)
        self.sync.por += If(por != 0, por.eq(por - 1))
        self.specials += AsyncResetSynchronizer(self.cd_por, reset)

        # System clock
        self.specials += Instance("BUFG", i_I=pll_sys, o_O=self.cd_sys.clk)
        self.comb += self.cd_por.clk.eq(self.cd_sys.clk)
        self.specials += AsyncResetSynchronizer(self.cd_sys, ~pll_lckd | (por > 0))
        platform.add_period_constraint(self.cd_sys.clk, 1e9/sys_clk_freq)

        # SDRAM clocks -----------------------------------------------------------------------------
        self.clk4x_wr_strb = Signal()
        self.clk4x_rd_strb = Signal()

        # SDRAM full clock
        self.specials += Instance("BUFPLL", name="sdram_full_bufpll",
            p_DIVIDE       = 4,
            i_PLLIN        = pll_sdram_full, i_GCLK=self.cd_sys.clk,
            i_LOCKED       = pll_lckd,
            o_IOCLK        = self.cd_sdram_full_wr.clk,
            o_SERDESSTROBE = self.clk4x_wr_strb)
        self.comb += [
            self.cd_sdram_full_rd.clk.eq(self.cd_sdram_full_wr.clk),
            self.clk4x_rd_strb.eq(self.clk4x_wr_strb),
        ]
        # SDRAM_half clock
        self.specials += Instance("BUFG", name="sdram_half_a_bufpll",
            i_I=pll_sdram_half_a, o_O=self.cd_sdram_half.clk)
        clk_sdram_half_shifted = Signal()
        self.specials += Instance("BUFG", name="sdram_half_b_bufpll",
            i_I=pll_sdram_half_b, o_O=clk_sdram_half_shifted)

        output_clk = Signal()
        clk = platform.request("ddram_clock")
        self.specials += Instance("ODDR2", p_DDR_ALIGNMENT="NONE",
            p_INIT=0, p_SRTYPE="SYNC",
            i_D0=1, i_D1=0, i_S=0, i_R=0, i_CE=1,
            i_C0=clk_sdram_half_shifted,
            i_C1=~clk_sdram_half_shifted,
            o_Q=output_clk)
        self.specials += Instance("OBUFDS", i_I=output_clk, o_O=clk.p, o_OB=clk.n)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=75e6,
        with_ethernet  = True,
        with_etherbone = False,
        eth_phy        = 0,
        **kwargs):
        platform = digilent_atlys.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Atlys", **kwargs)

        # DDR2 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.ddrphy = s6ddrphy.S6HalfRateDDRPHY(platform.request("ddram"),
                memtype           = "DDR2",
                rd_bitslip        = 0,
                wr_bitslip        = 4,
                dqs_ddr_alignment = "C0")
            self.comb += [
                self.ddrphy.clk4x_wr_strb.eq(self.crg.clk4x_wr_strb),
                self.ddrphy.clk4x_rd_strb.eq(self.crg.clk4x_rd_strb),
            ]
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT47H64M16(sys_clk_freq, "1:2"),
                l2_cache_size = kwargs.get("l2_size", 8192),
            )

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            from liteeth.phy import LiteEthPHYGMIIMII
            self.ethphy = LiteEthPHYGMIIMII(
                clock_pads = self.platform.request("eth_clocks", eth_phy),
                pads       = self.platform.request("eth", eth_phy),
                clk_freq   = int(self.sys_clk_freq))
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy)
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy)
            self.ethphy.crg.cd_eth_rx.clk.attr.add("keep")
            self.ethphy.crg.cd_eth_tx.clk.attr.add("keep")
            self.platform.add_platform_command("""
NET "{eth_clocks_rx}" CLOCK_DEDICATED_ROUTE = FALSE;
NET "{eth_clocks_tx}" CLOCK_DEDICATED_ROUTE = FALSE;
""",
            eth_clocks_rx=platform.lookup_request("eth_clocks").rx,
            eth_clocks_tx=platform.lookup_request("eth_clocks").tx,
            )

        # Leds -------------------------------------------------------------------------------------
        self.leds = LedChaser(
            pads         = platform.request_all("user_led"),
            sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=digilent_atlys.Platform, description="LiteX SoC on Atlys.")
    parser.add_target_argument("--with-ethernet",  action="store_true", help="Enable Ethernet support.")
    parser.add_target_argument("--with-etherbone", action="store_true", help="Enable Etherbone support.")

    args = parser.parse_args()

    soc = BaseSoC(
        with_ethernet  = args.with_ethernet,
        with_etherbone = args.with_etherbone,
        **parser.soc_argdict)
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
