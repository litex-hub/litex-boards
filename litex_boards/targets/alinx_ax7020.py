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
        pll.register_clkin(platform.request("clk50"), platform.default_clk_freq)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=100e6, hp_data_width=32,
        with_ps_ddr     = False,
        with_buttons    = True,
        with_led_chaser = True,
        **kwargs):

        platform = alinx_ax7020.Platform()

        assert not (with_ps_ddr and kwargs.get("cpu_type", None) == "zynq7000")

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Alinx AX7020", **kwargs)

        # PS DDR (Zynq7000 Integration) ------------------------------------------------------------
        if with_ps_ddr:
            self.ps = ps = zynq7000.Zynq7000(platform=platform, variant="standard")
            ps.set_ps7(name="Zynq", config=platform.ps7_config)
            axi_hp0 = ps.add_axi_hp_slave(clock_domain="sys", data_width=hp_data_width)

            axi_hp0_region  = SoCRegion(origin=0x100000,                     size=0x2000_0000)
            main_ram_region = SoCRegion(origin=self.cpu.mem_map["main_ram"], size=axi_hp0_region.size)

            wb           = self.bus.add_adapter("axi_hp0", axi_hp0, direction="s2m")
            remap_module = wishbone.Interface(data_width=32, address_width=32)

            self.submodules += wishbone.Remapper(
                master      = remap_module,
                slave       = wb,
                src_regions = [main_ram_region],
                dst_regions = [axi_hp0_region]
            )
            self.bus.add_slave("main_ram", remap_module, main_ram_region)

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

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=alinx_ax7020.Platform, description="LiteX SoC on Alinx AX7020.")
    parser.add_target_argument("--sys-clk-freq", default=100e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-ps-ddr",  action="store_true",       help="Uses PS DDR via HP0 as Main RAM.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq = args.sys_clk_freq,
        with_ps_ddr  = args.with_ps_ddr,
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
