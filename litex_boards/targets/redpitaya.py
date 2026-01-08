#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Gwenhael Goavec-Merou <gwenhael.goavec-merou@trabucayre.com>
# SPDX-License-Identifier: BSD-2-Clause

import os

from migen import *

from litex.gen import *

from litex_boards.platforms import redpitaya

from litex.soc.interconnect import axi
from litex.soc.interconnect import wishbone

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

# CRG ----------------------------------------------------------------------------------------------


class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, use_ps7_clk=False):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()

        # # #

        if use_ps7_clk:
            assert sys_clk_freq == 125e6
            self.comb += ClockSignal("sys").eq(ClockSignal("ps7"))
            self.comb += ResetSignal("sys").eq(ResetSignal("ps7") | self.rst)
        else:
            self.pll = pll = S7PLL(speedgrade=-1)
            self.comb += pll.reset.eq(self.rst)
            pll.register_clkin(platform.request(platform.default_clk_name), platform.default_clk_freq)
            pll.create_clkout(self.cd_sys,      sys_clk_freq)
            platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

# BaseSoC ------------------------------------------------------------------------------------------


class BaseSoC(SoCCore):
    def __init__(self, board, sys_clk_freq=100e6, with_led_chaser=True, **kwargs):
        platform = redpitaya.Platform(board)

        # CRG --------------------------------------------------------------------------------------
        use_ps7_clk  = (kwargs.get("cpu_type", None) == "zynq7000")
        sys_clk_freq = 125e6 if use_ps7_clk else sys_clk_freq
        self.crg = _CRG(platform, sys_clk_freq, use_ps7_clk)

        # SoCCore ----------------------------------------------------------------------------------
        if kwargs["uart_name"] == "serial":
            kwargs["uart_name"] = "usb_uart"
        if kwargs.get("cpu_type", None) == "zynq7000":
            kwargs["integrated_sram_size"] = 0
            kwargs["with_uart"]            = False
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Redpitaya", **kwargs)

        # Zynq7000 Integration ---------------------------------------------------------------------
        if kwargs.get("cpu_type", None) == "zynq7000":
            self.cpu.set_ps7(name="Zynq",
                config={
                    **platform.ps7_config,
                    "PCW_FPGA0_PERIPHERAL_FREQMHZ"     : sys_clk_freq / 1e6,
                    "PCW_SDIO_PERIPHERAL_FREQMHZ"      : "125",
                    "PCW_ACT_ENET0_PERIPHERAL_FREQMHZ" : "125.000000",
                    "PCW_ENET0_RESET_ENABLE"           : "0",
                })

            self.bus.add_region("sram", SoCRegion(
                origin = self.cpu.mem_map["sram"],
                size   = 512 * MEGABYTE - self.cpu.mem_map["sram"])
            )
            self.bus.add_region("rom", SoCRegion(
                origin = self.cpu.mem_map["rom"],
                size   = 256 * MEGABYTE // 8,
                linker = True)
            )
            self.constants["CONFIG_CLOCK_FREQUENCY"] = 666666687
            self.bus.add_region("flash", SoCRegion(origin=0xFC00_0000, size=0x4_0000, mode="rwx"))

            # Enable UART0.
            self.cpu.add_uart(0, "MIO 14 .. 15")

            # Enable SDIO.
            self.cpu.add_sdio(0, "MIO 40 .. 45", None, None, None)

            # Enable Ethernet.
            self.cpu.add_ethernet(0, "MIO 16 .. 27", "MIO 52 .. 53")

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------


def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=redpitaya.Platform, description="LiteX SoC on Zedboard.")
    parser.add_target_argument("--sys-clk-freq", default=100e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--board",        default="redpitaya14",     help="Board type (redpitaya14 or redpitaya16).")
    parser.set_defaults(cpu_type="zynq7000")
    parser.set_defaults(no_uart=True)
    args = parser.parse_args()

    if args.cpu_type == "zynq7000":
        args.no_compile_software = True # otherwise fails

    soc = BaseSoC(
        board        = args.board,
        sys_clk_freq = args.sys_clk_freq,
        **parser.soc_argdict
    )
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"), device=1)

if __name__ == "__main__":
    main()
