#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Gwenhael Goavec-Merou <gwenhael.goavec-merou@trabucayre.com>
# SPDX-License-Identifier: BSD-2-Clause

# Load bit/bios ------------------------------------------------------------------------------------

#
# 1/ tcl script:
# connect
# targets -set -filter {name =~ "ARM*#0"}
# rst
# stop
#
# source build/digilent_arty_z7/gateware/digilent_arty_z7.srcs/sources_1/ip/Zynq/ps7_init.tcl
# ps7_init
# ps7_post_config
#
# dow build/digilent_arty_z7/software/bios/bios.elf
# fpga build/digilent_arty_z7/gateware/digilent_arty_z7.bit
# con
#
# 2/ loading
# xsct -nodisp ps7_boot.tcl
# where ps7_boot.tcl is your script name

from migen import *

from litex.gen import *

from litex_boards.platforms import digilent_arty_z7

from litex.soc.cores.clock import *
from litex.soc.integration.soc import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.gpio import GPIOIn

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, use_ps7_clk=False):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()

        # # #

        if use_ps7_clk:
            self.comb += ClockSignal("sys").eq(ClockSignal("ps7"))
            self.comb += ResetSignal("sys").eq(ResetSignal("ps7") | self.rst)
        else:
            # Clk.
            clk125 = platform.request("clk125")

            # PLL.
            self.pll = pll = S7PLL(speedgrade=-1)
            self.comb += pll.reset.eq(self.rst)
            pll.register_clkin(clk125, 125e6)
            pll.create_clkout(self.cd_sys, sys_clk_freq)
            # Ignore sys_clk to pll.clkin path created by SoC's rst.
            platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, variant="z7-20", toolchain="vivado", sys_clk_freq=125e6,
            with_led_chaser = True,
            with_buttons    = False,
            with_switches   = False,
            **kwargs):
        platform = digilent_arty_z7.Platform(variant=variant, toolchain=toolchain)

        # CRG --------------------------------------------------------------------------------------
        use_ps7_clk = (kwargs.get("cpu_type", None) == "zynq7000")
        if use_ps7_clk:
            sys_clk_freq = 100e6

        self.crg = _CRG(platform, sys_clk_freq, use_ps7_clk)

        # SoCCore ----------------------------------------------------------------------------------
        if kwargs.get("cpu_type", None) == "zynq7000":
            kwargs["integrated_sram_size"] = 0
            kwargs["with_uart"]            = False
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Arty Z7", **kwargs)

        # Zynq7000 Integration ---------------------------------------------------------------------
        if kwargs.get("cpu_type", None) == "zynq7000":
            assert toolchain == "vivado", ' not tested / specific vivado cmds'

            self.cpu.set_ps7(name="Zynq",
                config={
                    **platform.ps7_config,
                    "PCW_FPGA0_PERIPHERAL_FREQMHZ" : sys_clk_freq / 1e6,
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
            self.bus.add_region("flash",  SoCRegion(origin=0xFC00_0000, size=0x4_0000, mode="rwx"))
            self.cpu.set_libxil({
                "STDOUT_BASEADDRESS"            : "0xE0000000",
                "XPAR_PS7_DDR_0_S_AXI_BASEADDR" : "0x00100000",
                "XPAR_PS7_DDR_0_S_AXI_HIGHADDR" : "0x1FFFFFFF",
            })

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

        # Buttons / Switches -----------------------------------------------------------------------
        if with_buttons:
            self.buttons = GPIOIn(Cat(platform.request_all("user_btn")))
        if with_switches:
            self.switches = GPIOIn(Cat(platform.request_all("user_sw")))

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=digilent_arty_z7.Platform, description="LiteX SoC on Arty Z7")
    parser.add_target_argument("--variant",      default="z7-20",           help="Board variant (z7-20 or z7-10).")
    parser.add_target_argument("--sys-clk-freq", default=125e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-buttons", action="store_true",       help="Enable Buttons.")
    parser.add_target_argument("--with-switches", action="store_true",      help="Enable Switches.")
    parser.set_defaults(cpu_type="zynq7000")
    parser.set_defaults(no_uart=True)
    args = parser.parse_args()

    soc = BaseSoC(
        variant      = args.variant,
        toolchain    = args.toolchain,
        sys_clk_freq = args.sys_clk_freq,
        with_buttons  = args.with_buttons,
        with_switches = args.with_switches,
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
