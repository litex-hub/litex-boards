#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019 Antti Lukats <antti.lukats@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import *
from litex.soc.interconnect import wishbone


class OnChipOscillator(LiteXModule):
    def __init__(self, device):
        self.clkout = Signal()

        if device.startswith("10CL"):
            self.specials += Instance("cyclone10lp_oscillator",
                i_oscena = Constant(1),
                o_clkout = self.clkout
            )
        elif device.startswith("10M"):
            self.specials += Instance("fiftyfivenm_oscillator",
                p_device_id        = "08",
                p_clock_frequency  = "116",
                i_oscena           = Constant(1),
                o_clkout           = self.clkout
            )
        elif device.startswith("5C") or device.startswith("EP5"):
            self.specials += Instance("cyclonev_oscillator",
                i_oscena = Constant(1),
                o_clkout = self.clkout
            )
        else:
            raise ValueError(f"Unsupported on-chip oscillator device: {device}")


class MFIOBasic(LiteXModule):
    def __init__(self, pads):
        self.bus = wishbone.Interface()

        # # #

        mfio_width = len(pads)
        mfio_o     = Signal(mfio_width)
        mfio_oe    = Signal(mfio_width)
        mfio_i     = Signal(mfio_width)

        for n in range(mfio_width):
            io = TSTriple()
            self.specials += io.get_tristate(pads[n])
            self.comb += [
                mfio_i[n].eq(io.i),
                io.o.eq(mfio_o[n]),
                io.oe.eq(mfio_oe[n]),
            ]

        index_width = max(1, bits_for(mfio_width - 1))
        index       = self.bus.adr[:index_width]
        input_bits  = Array(mfio_i[n] for n in range(mfio_width))
        selected    = Signal()

        self.comb += [
            selected.eq(input_bits[index]),
            self.bus.ack.eq(self.bus.cyc & self.bus.stb),
            self.bus.dat_r.eq(selected),
        ]

        for n in range(mfio_width):
            self.sync += If(self.bus.cyc & self.bus.stb & self.bus.we & (index == n),
                mfio_o[n].eq(self.bus.dat_w[0]),
                mfio_oe[n].eq(~self.bus.dat_w[1])
            )
