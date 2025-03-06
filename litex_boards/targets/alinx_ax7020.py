#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 Neil Liu <wetone.liu@gmail.com>,
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import *

from litex_boards.platforms import alinx_ax7020

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litex.soc.cores.gpio import GPIOIn

from litex.soc.integration.soc import SoCRegion
from litex.soc.cores.cpu import zynq7000
from litex.soc.interconnect import wishbone, axi

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()

        self.pll = pll = S7PLL(speedgrade=-2)
        #self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(platform.request("clk50"), platform.default_clk_freq)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.
        
# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=100e6, with_led_chaser=False, with_ps_ddr=False, hp_data_width=32, **kwargs):
        with_buttons    = False,
        
        platform = alinx_ax7020.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        #if kwargs["uart_name"] == "serial": kwargs["uart_name"] = "usb_uart" # Use USB-UART Pmod on JB.
        kwargs["uart_name"] = "serial"
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Alinx AX7020", **kwargs)

        # Zynq7000 Integration ---------------------------------------------------------------------
        #if kwargs.get("cpu_type", None) == "zynq7000":

        if with_ps_ddr:
            self.wb_ddr_base = 0x4000_0000
            self.ddr_size = 0x2000_0000
            self.ps_ddr_start = 0x100000
            self.add_ps_module(platform, hp_data_width=hp_data_width)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)


        # Buttons ----------------------------------------------------------------------------------
        if with_buttons:
            self.buttons = GPIOIn(
                pads     = platform.request_all("user_btn"),
                with_irq = self.irq.enabled
            )

    def add_ps_module(self, platform, hp_data_width):
        ddr_name = 'main_ram'
        ps = zynq7000.Zynq7000(platform=platform, variant="standard")
        ps.set_ps7(name="Zynq", config=platform.ps7_config)
        axi_hp0 = ps.add_axi_hp_slave(clock_domain="sys", data_width=hp_data_width)
        self.submodules += ps
        self.bus.add_slave(ddr_name, axi_hp0, SoCRegion(origin=self.wb_ddr_base, size=self.ddr_size))

        remap_module = wishbone.Interface(data_width=32, address_width=32)
        self.submodules += wishbone.Remapper(master=remap_module, slave=self.bus.slaves[ddr_name],
                          src_regions=[SoCRegion(origin=self.wb_ddr_base, size=self.ddr_size)],
                          dst_regions=[SoCRegion(origin=self.ps_ddr_start, size=self.ddr_size)])
        self.bus.slaves[ddr_name] = remap_module
        

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=alinx_ax7020.Platform, description="LiteX SoC on zynq xc7z020.")
    parser.add_target_argument("--sys-clk-freq", default=100e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-ps-ddr", action="store_true", help="Enable PS DDR.")
    parser.add_target_argument("--hp-data-width", default=32, help="Enable LED chaser.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq = args.sys_clk_freq,
        with_ps_ddr=args.with_ps_ddr,
        hp_data_width=args.hp_data_width,
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
