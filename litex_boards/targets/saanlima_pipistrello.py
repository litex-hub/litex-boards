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

from litex_boards.platforms import pipistrello

from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litedram.modules import MT46H32M16
from litedram.phy import s6ddrphy

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_sys           = ClockDomain()
        self.clock_domains.cd_sdram_half    = ClockDomain()
        self.clock_domains.cd_sdram_full_wr = ClockDomain()
        self.clock_domains.cd_sdram_full_rd = ClockDomain()

        self.reset = Signal()

        # # #

        # Input clock ------------------------------------------------------------------------------
        clk50_freq = int(50e6)
        clk50      = platform.request("clk50")
        clk50b     = Signal()
        self.specials += Instance("BUFIO2",
            p_DIVIDE=1, p_DIVIDE_BYPASS="TRUE",
            p_I_INVERT="FALSE",
            i_I=clk50, o_DIVCLK=clk50b)

        # PLL --------------------------------------------------------------------------------------
        pll_lckd           = Signal()
        pll_fb             = Signal()
        pll_sdram_full   = Signal()
        pll_sdram_half_a = Signal()
        pll_sdram_half_b = Signal()
        pll_unused       = Signal()
        pll_sys          = Signal()
        pll_periph       = Signal()

        p = 12
        f = Fraction(sys_clk_freq*p, clk50_freq)
        n, d = f.numerator, f.denominator
        assert 19e6 <= clk50_freq/d <= 500e6  # pfd
        assert 400e6 <= clk50_freq*n/d <= 1080e6  # vco

        self.specials.pll = Instance(
            "PLL_ADV",
            name="crg_pll_adv",
            p_SIM_DEVICE="SPARTAN6", p_BANDWIDTH="OPTIMIZED", p_COMPENSATION="INTERNAL",
            p_REF_JITTER=.01,
            i_DADDR=0, i_DCLK=0, i_DEN=0, i_DI=0, i_DWE=0, i_RST=0, i_REL=0,
            p_DIVCLK_DIVIDE=d,
            # Input Clocks (50MHz)
            i_CLKIN1=clk50b,
            p_CLKIN1_PERIOD=1e9/clk50_freq,
            i_CLKIN2=0,
            p_CLKIN2_PERIOD=0.,
            i_CLKINSEL=1,
            # Feedback
            i_CLKFBIN=pll_fb, o_CLKFBOUT=pll_fb, o_LOCKED=pll_lckd,
            p_CLK_FEEDBACK="CLKFBOUT",
            p_CLKFBOUT_MULT=n, p_CLKFBOUT_PHASE=0.,
            # (333MHz) sdram wr rd
            o_CLKOUT0=pll_sdram_full, p_CLKOUT0_DUTY_CYCLE=.5,
            p_CLKOUT0_PHASE=0., p_CLKOUT0_DIVIDE=p//4,
            # unused?
            o_CLKOUT1=pll_unused, p_CLKOUT1_DUTY_CYCLE=.5,
            p_CLKOUT1_PHASE=0., p_CLKOUT1_DIVIDE=15,
            # (166MHz) sdram_half - sdram dqs adr ctrl
            o_CLKOUT2=pll_sdram_half_a, p_CLKOUT2_DUTY_CYCLE=.5,
            p_CLKOUT2_PHASE=270., p_CLKOUT2_DIVIDE=p//2,
            # (166MHz) off-chip ddr
            o_CLKOUT3=pll_sdram_half_b, p_CLKOUT3_DUTY_CYCLE=.5,
            p_CLKOUT3_PHASE=250., p_CLKOUT3_DIVIDE=p//2,
            # ( 50MHz) periph
            o_CLKOUT4=pll_periph, p_CLKOUT4_DUTY_CYCLE=.5,
            p_CLKOUT4_PHASE=0., p_CLKOUT4_DIVIDE=20,
            # ( 83MHz) sysclk
            o_CLKOUT5=pll_sys, p_CLKOUT5_DUTY_CYCLE=.5,
            p_CLKOUT5_PHASE=0., p_CLKOUT5_DIVIDE=p//1,
        )

        # Power on reset
        reset = platform.request("user_btn") | self.reset | self.rst
        self.clock_domains.cd_por = ClockDomain()
        por = Signal(max=1 << 11, reset=(1 << 11) - 1)
        self.sync.por += If(por != 0, por.eq(por - 1))
        self.specials += AsyncResetSynchronizer(self.cd_por, reset)

        # System clock
        self.specials += Instance("BUFG", i_I=pll_sys, o_O=self.cd_sys.clk)
        self.comb += self.cd_por.clk.eq(self.cd_sys.clk)
        self.specials += AsyncResetSynchronizer(self.cd_sys, ~pll_lckd | (por > 0))

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
        clk = platform.request("ddram_clock")
        self.specials += Instance("ODDR2", p_DDR_ALIGNMENT="NONE",
            p_INIT=0, p_SRTYPE="SYNC",
            i_D0=1, i_D1=0, i_S=0, i_R=0, i_CE=1,
            i_C0=clk_sdram_half_shifted,
            i_C1=~clk_sdram_half_shifted,
            o_Q=clk.p)
        self.specials += Instance("ODDR2", p_DDR_ALIGNMENT="NONE",
            p_INIT=0, p_SRTYPE="SYNC",
            i_D0=0, i_D1=1, i_S=0, i_R=0, i_CE=1,
            i_C0=clk_sdram_half_shifted,
            i_C1=~clk_sdram_half_shifted,
            o_Q=clk.n)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, with_led_chaser=True, **kwargs):
        sys_clk_freq = (83 + Fraction(1, 3))*1000*1000
        platform     = pipistrello.Platform()

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident = "LiteX SoC on Pipistrello",
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)
        self.platform.add_period_constraint(self.crg.cd_sys.clk, 1e9/sys_clk_freq)

        # LPDDR SDRAM ------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.submodules.ddrphy = s6ddrphy.S6HalfRateDDRPHY(platform.request("ddram"),
                memtype           = "LPDDR",
                rd_bitslip        = 1,
                wr_bitslip        = 3,
                dqs_ddr_alignment = "C1")
            self.comb += [
                self.ddrphy.clk4x_wr_strb.eq(self.crg.clk4x_wr_strb),
                self.ddrphy.clk4x_rd_strb.eq(self.crg.clk4x_rd_strb),
            ]
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT46H32M16(sys_clk_freq, "1:2"),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on Pipistrello")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",        action="store_true", help="Build bitstream.")
    target_group.add_argument("--load",         action="store_true", help="Load bitstream.")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(**soc_core_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
