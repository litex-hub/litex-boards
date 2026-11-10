#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026
# SPDX-License-Identifier: BSD-2-Clause

import os
import shutil

from migen import *

from litex.gen import *

from litex_boards.platforms import xilinx_kr260
from litex.build.tools import write_to_file

from litex.soc.cores.clock import *
from litex.soc.integration.soc import *
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
            self.comb += [
                ClockSignal("sys").eq(ClockSignal("ps")),
                ResetSignal("sys").eq(ResetSignal("ps") | self.rst),
            ]
        else:
            self.pll = pll = S7PLL(speedgrade=-1)
            self.comb += pll.reset.eq(self.rst)
            pll.register_clkin(platform.request(platform.default_clk_name), platform.default_clk_freq)
            pll.create_clkout(self.cd_sys, sys_clk_freq)
            # Ignore sys_clk to pll.clkin path created by SoC's rst.
            platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=100e6, with_led_chaser=True, **kwargs):
        platform = xilinx_kr260.Platform()

        # CRG --------------------------------------------------------------------------------------
        use_ps7_clk = (kwargs.get("cpu_type", None) == "zynqmp")
        self.crg    = _CRG(platform, sys_clk_freq, use_ps7_clk)

        # SoCCore ----------------------------------------------------------------------------------
        if kwargs.get("cpu_type", None) == "zynqmp":
            kwargs["integrated_sram_size"] = 0
            kwargs["with_uart"]            = False
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on KR260", **kwargs)

        # ZynqMP Integration -----------------------------------------------------------------------
        if kwargs.get("cpu_type", None) == "zynqmp":
            #self.cpu.config.update({
            #    "PSU_MIO_36_DIRECTION"                   : "out",
            #    "PSU_MIO_37_DIRECTION"                   : "in",
            #    "PSU__UART1__BAUD_RATE"                  : 115200,
            #    "PSU__CRL_APB__UART1_REF_CTRL__DIVISOR0" : 10,
            #})
            self.cpu.config.update(platform.psu_config)

            self.cpu.add_uart(1, "MIO 36 .. 37", "IOPLL", 100)
            self.cpu.add_i2c(1, "MIO 24 .. 25", "IOPLL", 100)
            self.cpu.add_ethernet(0,
                eth_pads_or_mio_group  = "GT Lane0",
                mdio_pads_or_mio_group = "MIO 50 .. 51",
                clock_pads             = "Ref Clk0",
                clock_pads_freq        = "125",
                ref_ctrl_clk_sel       = "IOPLL",
                ref_ctrl_clk_freq      = "125",
            )
            self.cpu.add_ethernet(1,
                eth_pads_or_mio_group  = "MIO 38 .. 49",
                mdio_pads_or_mio_group = "MIO 50 .. 51",
                ref_ctrl_clk_sel       = "IOPLL",
                ref_ctrl_clk_freq      = "125",
            )

            self.bus.add_region("sram", SoCRegion(
                origin = self.cpu.mem_map["sram"],
                size   = 2 * GIGABYTE)
            )
            self.bus.add_region("rom", SoCRegion(
                origin = self.cpu.mem_map["rom"],
                size   = 512 * MEGABYTE // 8,
                linker = True)
            )
            self.constants["CONFIG_CLOCK_FREQUENCY"] = 1333333008
            self.cpu.set_libxil({
                "STDIN_BASEADDRESS"                       : "0xFF010000",
                "STDOUT_BASEADDRESS"                      : "0xFF010000",
                "XPAR_PSU_DDR_0_S_AXI_BASEADDR"           : "0x00000000",
                "XPAR_PSU_DDR_0_S_AXI_HIGHADDR"           : "0x7FFFFFFF",
                "XPAR_PSU_DDR_1_S_AXI_BASEADDR"           : "0x800000000",
                "XPAR_PSU_DDR_1_S_AXI_HIGHADDR"           : "0x87FFFFFFF",
                "XPAR_CPU_CORTEXA53_0_TIMESTAMP_CLK_FREQ" : "99999001",
            })

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=xilinx_kr260.Platform, description="LiteX SoC on KR260.")
    parser.add_target_argument("--sys-clk-freq", default=100e6, type=float, help="System clock frequency.")
    parser.set_defaults(cpu_type="zynqmp")
    parser.set_defaults(no_uart=True)
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

if __name__ == "__main__":
    main()
