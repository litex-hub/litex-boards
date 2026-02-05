#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 Icenowy Zheng <uwu@icenowy.me>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from litex_boards.platforms import microsoft_catapult_v3

from litex.gen import *

from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.bitbang import I2CMaster

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst     = Signal()
        self.cd_sys  = ClockDomain()
        self.cd_por  = ClockDomain()

        # # #

        # Clk
        clk100 = platform.request("clk100")
        self.comb += ClockSignal("sys").eq(clk100)
        assert sys_clk_freq == 100e6

        # Power on reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += self.cd_por.clk.eq(clk100)
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))
        self.comb += ResetSignal("sys").eq(~por_done | self.rst)


# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=100e6,
        with_led_chaser = True,
        **kwargs):
        self.platform = platform = microsoft_catapult_v3.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        # Defaults to JTAG-UART since no hardware UART.
        real_uart_name = kwargs["uart_name"]
        if real_uart_name == "serial":
            if kwargs["with_jtagbone"]:
                kwargs["uart_name"] = "crossover"
            else:
                kwargs["uart_name"] = "jtag_uart"
        if kwargs["with_uartbone"]:
            kwargs["uart_name"] = "crossover"
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Microsoft Catapult v3 SmartNIC", **kwargs)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

        # I2C --------------------------------------------------------------------------------------
        self.i2c0 = I2CMaster(platform.request("i2c", 0))
        self.i2c1 = I2CMaster(platform.request("i2c", 1))

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=microsoft_catapult_v3.Platform, description="LiteX SoC on Microsoft Catapult v3 SmartNIC.")
    parser.add_target_argument("--variant",         default="pcie",                    help="Board variant (pcie or ocp).")
    parser.add_target_argument("--sys-clk-freq",    default=100e6, type=float,         help="System clock frequency.")
    parser.add_target_argument("--with-led-chaser", default=True, action="store_true", help="Enable LED Chaser.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq    = args.sys_clk_freq,
        with_led_chaser = args.with_led_chaser,
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
