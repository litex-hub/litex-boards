#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Gwenhael Goavec-Merou <gwenhael.goavec-merou@trabucayre.com>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex_boards.platforms import digilent_arty_z7
from litex.build import tools
from litex.build.xilinx import common as xil_common
from litex.build.xilinx.vivado import vivado_build_args, vivado_build_argdict

from litex.soc.interconnect import axi
from litex.soc.interconnect import wishbone

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

# CRG ----------------------------------------------------------------------------------------------


class _CRG(Module):
    def __init__(self, platform, sys_clk_freq, use_ps7_clk=False):
        self.rst = Signal()
        self.clock_domains.cd_sys = ClockDomain()

        # # #

        if use_ps7_clk:
            self.comb += ClockSignal("sys").eq(ClockSignal("ps7"))
            self.comb += ResetSignal("sys").eq(ResetSignal("ps7") | self.rst)
        else:
            # Clk.
            clk125 = platform.request("clk125")

            # PLL.
            self.submodules.pll = pll = S7PLL(speedgrade=-1)
            self.comb += pll.reset.eq(self.rst)
            pll.register_clkin(clk125, 125e6)
            pll.create_clkout(self.cd_sys, sys_clk_freq)
            # Ignore sys_clk to pll.clkin path created by SoC's rst.
            platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin)

# BaseSoC ------------------------------------------------------------------------------------------


class BaseSoC(SoCCore):
    def __init__(self, variant="z7-20", toolchain="vivado", sys_clk_freq=int(125e6),
                 with_led_chaser=True, **kwargs):
        platform = digilent_arty_z7.Platform(variant=variant, toolchain=toolchain)

        if kwargs.get("cpu_type", None) == "zynq7000":
            kwargs['integrated_sram_size'] = 0
            kwargs['with_uart'] = False
            self.mem_map = {
                'csr': 0x4000_0000,  # Zynq GP0 default
            }

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident = "LiteX SoC on Arty Z7",
            **kwargs)

        # Zynq7000 Integration ---------------------------------------------------------------------
        if kwargs.get("cpu_type", None) == "zynq7000":
            assert toolchain == "vivado", ' not tested / specific vivado cmds'

            preset_name = "arty_z7_20.tcl" if variant == "z7-20" else "arty_z7_10.tcl"

            os.system("wget http://kmf2.trabucayre.com/" + preset_name)
            self.cpu.set_ps7(preset=preset_name)

            # Connect AXI GP0 to the SoC
            wb_gp0 = wishbone.Interface()
            self.submodules += axi.AXI2Wishbone(
                axi          = self.cpu.add_axi_gp_master(),
                wishbone     = wb_gp0,
                base_address = self.mem_map['csr'])
            self.add_wb_master(wb_gp0)

            use_ps7_clk = True
        else:
            use_ps7_clk = False

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq, use_ps7_clk)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on Arty Z7")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--toolchain",    default="vivado",    help="FPGA toolchain (vivado, symbiflow or yosys+nextpnr).")
    target_group.add_argument("--build",        action="store_true", help="Build bitstream.")
    target_group.add_argument("--load",         action="store_true", help="Load bitstream.")
    target_group.add_argument("--variant",      default="z7-20",     help="Board variant (z7-20 or z7-10).")
    target_group.add_argument("--sys-clk-freq", default=125e6,       help="System clock frequency.")
    builder_args(parser)
    soc_core_args(parser)
    vivado_build_args(parser)
    parser.set_defaults(cpu_type="zynq7000")
    parser.set_defaults(no_uart=True)
    args = parser.parse_args()

    soc = BaseSoC(
        variant = args.variant,
        toolchain = args.toolchain,
        sys_clk_freq=int(float(args.sys_clk_freq)),
        **soc_core_argdict(args)
    )
    builder = Builder(soc, **builder_argdict(args))
    builder_kwargs = vivado_build_argdict(args) if args.toolchain == "vivado" else {}
    builder.build(**builder_kwargs, run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"), device=1)

if __name__ == "__main__":
    main()
