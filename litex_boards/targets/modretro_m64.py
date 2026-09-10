#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause
#
# Uses the independent 50MHz oscillator, 64KiB ROM and 128KiB main RAM in block RAM.
# Build/load: python3 -m litex_boards.targets.modretro_m64 --build --load
# Hardware operation has not yet been tested. See the platform for schematics and JTAG wiring.
#
# JTAG UART uses USER1. For an OpenOCD-compatible 1.8V adapter, add this TAP definition
# to the adapter's configuration (m64.cfg), then run: litex_term jtag --jtag-config=m64.cfg
#   transport select jtag
#   adapter speed 10000
#   jtag newtap xcau15p tap -irlen 6 -ignore-version -expected-id 0x04ac2093
# --with-jtagbone uses USER1 for JTAGBone and selects a crossover UART.
# --uart-name=serial selects the 3.3V debug UART on J18.
#
# --with-psram enables all four devices in x16 mode at sys_clk_freq/8 (12.5MHz by default).
# The BIOS stays in block RAM. psram0..3 are uncached regions at 0xa0000000, 0xa4000000,
# 0xa8000000 and 0xac000000, with sizes 32, 32, 32 and 64MiB. Each psramN_status CSR reports
# ready (bit 0), initialization error (bit 1) and read timeout (bit 2); psramN_identification
# contains MR1/MR2. Initial BIOS tests can use:
#   mem_test 0xa0000000 0x1000
#   mem_test 0xa4000000 0x1000
#   mem_test 0xa8000000 0x1000
#   mem_test 0xac000000 0x1000

from migen import *

from litex.gen import *

from litex_boards.platforms import modretro_m64

from litex.soc.cores.clock import USPMMCM
from litex.soc.cores.gpio import GPIOTristate
from litex.soc.integration.soc import SoCRegion
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
    def __init__(self, sys_clk_freq=100e6, with_gpio=False, with_psram=False, **kwargs):
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

        # PSRAM ------------------------------------------------------------------------------------
        if with_psram:
            from litex.soc.cores.ram.apmemory import APMemory
            for n, size in enumerate([32*1024*1024]*3 + [64*1024*1024]):
                pads = platform.request("psram", n)
                psram = APMemory(pads, sys_clk_freq, size=size)
                setattr(self, f"psram{n}", psram)
                self.bus.add_slave(f"psram{n}", psram.bus,
                    SoCRegion(origin=0xa0000000 + n*0x04000000, size=size, cached=False))
                # Bound pad-to-sampler and output-register-to-pad delays for the sys/8 PHY.
                platform.add_platform_command(
                    "set_max_delay -datapath_only 5 -from [get_ports {{{dq}[*] {dqs}[*]}}]",
                    dq=pads.dq, dqs=pads.dqs)
                platform.add_platform_command(
                    "set_max_delay -datapath_only 5 -from [all_registers] "
                    "-to [get_ports {{{clk} {cs_n}}}]", clk=pads.clk, cs_n=pads.cs_n)
                # DQ/DM have two sys cycles of setup/hold, including tristate enable delays.
                platform.add_platform_command(
                    "set_max_delay -datapath_only 8 -from [all_registers] "
                    "-to [get_ports {{{dq}[*] {dqs}[*]}}]", dq=pads.dq, dqs=pads.dqs)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=modretro_m64.Platform, description="LiteX SoC on ModRetro M64.")
    parser.add_target_argument("--sys-clk-freq", default=100e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-gpio",    action="store_true",       help="Enable GPIO on the 1.8V J25 expansion connector.")
    parser.add_target_argument("--with-psram",   action="store_true",       help="Enable all four x16 PSRAMs (160MiB total, sys/8 clock).")
    parser.set_defaults(uart_name=None, integrated_rom_size=0x10000, integrated_main_ram_size=0x20000)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq = args.sys_clk_freq,
        with_gpio    = args.with_gpio,
        with_psram   = args.with_psram,
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
