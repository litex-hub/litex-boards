#!/usr/bin/env python3

# This file is Copyright (c) 2019 Sean Cross <sean@xobs.io>
# License: BSD

from litex_boards.partner.platforms import netv2

from migen import Module, Signal, Instance, ClockDomain, If
from migen.genlib.resetsync import AsyncResetSynchronizer

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, use_pll=True):
        clk48_raw = platform.request("clk48")
        clk12_raw = Signal()
        clk48 = Signal()
        clk12 = Signal()

        reset_delay = Signal(13, reset=4095)
        self.clock_domains.cd_por = ClockDomain()
        self.reset = Signal()

        self.clock_domains.cd_sys = ClockDomain()
        self.clock_domains.cd_usb_12 = ClockDomain()
        self.clock_domains.cd_usb_48 = ClockDomain()

        platform.add_period_constraint(self.cd_usb_48.clk, 1e9/48e6)
        platform.add_period_constraint(self.cd_sys.clk, 1e9/12e6)
        platform.add_period_constraint(self.cd_usb_12.clk, 1e9/12e6)
        platform.add_period_constraint(clk48, 1e9/48e6)
        platform.add_period_constraint(clk48_raw, 1e9/48e6)
        platform.add_period_constraint(clk12_raw, 1e9/12e6)

        # POR reset logic- POR generated from sys clk, POR logic feeds sys clk
        # reset.
        self.comb += [
            self.cd_por.clk.eq(self.cd_sys.clk),
            self.cd_sys.rst.eq(reset_delay != 0),
            self.cd_usb_12.rst.eq(reset_delay != 0),
        ]

        if use_pll:

            # Divide clk48 down to clk12, to ensure they're synchronized.
            # By doing this, we avoid needing clock-domain crossing.
            clk12_counter = Signal(2)

            self.clock_domains.cd_usb_48_raw = ClockDomain()

            platform.add_period_constraint(self.cd_usb_48_raw.clk, 1e9/48e6)

            # POR reset logic- POR generated from sys clk, POR logic feeds sys clk
            # reset.
            self.comb += [
                self.cd_usb_48.rst.eq(reset_delay != 0),
            ]

            self.comb += self.cd_usb_48_raw.clk.eq(clk48_raw)
            self.comb += self.cd_usb_48.clk.eq(clk48)

            self.sync.usb_48_raw += clk12_counter.eq(clk12_counter + 1)

            self.comb += clk12_raw.eq(clk12_counter[1])
            self.specials += Instance(
                "SB_GB",
                i_USER_SIGNAL_TO_GLOBAL_BUFFER=clk12_raw,
                o_GLOBAL_BUFFER_OUTPUT=clk12,
            )

            self.specials += Instance(
                "SB_PLL40_CORE",
                # Parameters
                p_DIVR = 0,
                p_DIVF = 3,
                p_DIVQ = 2,
                p_FILTER_RANGE = 1,
                p_FEEDBACK_PATH = "PHASE_AND_DELAY",
                p_DELAY_ADJUSTMENT_MODE_FEEDBACK = "FIXED",
                p_FDA_FEEDBACK = 15,
                p_DELAY_ADJUSTMENT_MODE_RELATIVE = "FIXED",
                p_FDA_RELATIVE = 0,
                p_SHIFTREG_DIV_MODE = 1,
                p_PLLOUT_SELECT = "SHIFTREG_0deg",
                p_ENABLE_ICEGATE = 0,
                # IO
                i_REFERENCECLK = clk12,
                o_PLLOUTGLOBAL = clk48,
                i_BYPASS = 0,
                i_RESETB = 1,
            )
        else:
            self.specials += Instance(
                "SB_GB",
                i_USER_SIGNAL_TO_GLOBAL_BUFFER=clk48_raw,
                o_GLOBAL_BUFFER_OUTPUT=clk48,
            )
            self.comb += self.cd_usb_48.clk.eq(clk48)

            clk12_counter = Signal(2)
            self.sync.usb_48 += clk12_counter.eq(clk12_counter + 1)

            self.comb += clk12_raw.eq(clk12_counter[1])
            self.specials += Instance(
                "SB_GB",
                i_USER_SIGNAL_TO_GLOBAL_BUFFER=clk12_raw,
                o_GLOBAL_BUFFER_OUTPUT=clk12,
            )

        self.comb += self.cd_sys.clk.eq(clk12)
        self.comb += self.cd_usb_12.clk.eq(clk12)

        self.sync.por += \
            If(reset_delay != 0,
                reset_delay.eq(reset_delay - 1)
            )
        self.specials += AsyncResetSynchronizer(self.cd_por, self.reset)
