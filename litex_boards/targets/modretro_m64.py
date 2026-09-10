#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause
#
# Initial support: internal RAM and JTAG UART. See docs/modretro_m64.md.

from migen import *

from litex.gen import *

from litex_boards.platforms import modretro_m64

from litex.soc.cores.clock import USPMMCM
from litex.soc.cores.gpio import GPIOTristate
from litex.soc.integration.soc_core import SoCCore
from litex.soc.integration.builder import Builder

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()

        # Clk / Rst.
        clk50       = platform.request("clk50")
        cpu_reset_n = platform.request("cpu_reset_n")

        # Buffer the MMCM input, which also clocks its reset delay registers.
        clk50_buf = Signal()
        self.specials += Instance("BUFG", i_I=clk50, o_O=clk50_buf)

        # PLL.
        self.pll = pll = USPMMCM(speedgrade=-2)
        self.comb += pll.reset.eq(~cpu_reset_n | self.rst)
        pll.register_clkin(clk50_buf, 50e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.
        platform.add_platform_command("set_false_path -from [get_ports {cpu_reset_n}]", cpu_reset_n=cpu_reset_n)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=100e6, with_gpio=False, **kwargs):
        platform = modretro_m64.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        kwargs.setdefault("integrated_rom_size",      0x10000)
        kwargs.setdefault("integrated_main_ram_size", 0x20000)
        if kwargs.get("uart_name") is None:
            kwargs["uart_name"] = "crossover" if kwargs.get("with_jtagbone", False) else "jtag_uart"
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on ModRetro M64", **kwargs)

        # JTAG UART / JTAGBone ---------------------------------------------------------------------
        for phy_name in ["uart_phy", "jtagbone_phy"]:
            phy = getattr(self, phy_name, None)
            if hasattr(phy, "cd_jtag"):
                # Include the BSCAN TDO register in JTAG timing analysis.
                platform.add_platform_command(
                    "create_clock -name jtag_clk -period 100 "
                    "[get_pins -hierarchical -filter {{REF_PIN_NAME == INTERNAL_TCK}}]")
                platform.add_false_path_constraints(phy.cd_jtag.clk, self.crg.cd_sys.clk)

        # GPIO -------------------------------------------------------------------------------------
        if with_gpio:
            self.gpio = GPIOTristate(platform.request("gpio"))

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=modretro_m64.Platform, description="LiteX SoC on ModRetro M64.")
    parser.add_target_argument("--sys-clk-freq", default=100e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-gpio",    action="store_true",       help="Enable GPIO on the 1.8V J25 expansion connector.")
    parser.set_defaults(uart_name=None, integrated_rom_size=0x10000, integrated_main_ram_size=0x20000)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq = args.sys_clk_freq,
        with_gpio    = args.with_gpio,
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
