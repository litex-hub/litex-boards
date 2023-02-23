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
from litex.build import tools
from litex.build.xilinx import common as xil_common
from litex.build.tools import write_to_file

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
            **kwargs):
        platform = digilent_arty_z7.Platform(variant=variant, toolchain=toolchain)

        # CRG --------------------------------------------------------------------------------------
        use_ps7_clk = (kwargs.get("cpu_type", None) == "zynq7000")
        self.crg = _CRG(platform, sys_clk_freq, use_ps7_clk)

        # SoCCore ----------------------------------------------------------------------------------
        if kwargs.get("cpu_type", None) == "zynq7000":
            kwargs["integrated_sram_size"] = 0
            kwargs["with_uart"]            = False
            self.mem_map = {
                'csr': 0x4000_0000,  # Zynq GP0 default
            }
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Arty Z7", **kwargs)

        # Zynq7000 Integration ---------------------------------------------------------------------
        if kwargs.get("cpu_type", None) == "zynq7000":
            assert toolchain == "vivado", ' not tested / specific vivado cmds'

            self.cpu.set_ps7(name="Zynq",
                config={
                    **platform.ps7_config,
                    "PCW_FPGA0_PERIPHERAL_FREQMHZ" : sys_clk_freq / 1e6,
                })

            # Connect AXI GP0 to the SoC
            wb_gp0 = wishbone.Interface()
            self.submodules += axi.AXI2Wishbone(
                axi          = self.cpu.add_axi_gp_master(),
                wishbone     = wb_gp0,
                base_address = self.mem_map["csr"])
            self.bus.add_master(master=wb_gp0)

            self.bus.add_region("sram", SoCRegion(
                origin = self.cpu.mem_map["sram"],
                size   = 512 * 1024 * 1024 - self.cpu.mem_map["sram"])
            )
            self.bus.add_region("rom", SoCRegion(
                origin = self.cpu.mem_map["rom"],
                size   = 256 * 1024 * 1024 // 8,
                linker = True)
            )
            self.constants["CONFIG_CLOCK_FREQUENCY"] = 666666687
            self.bus.add_region("flash",  SoCRegion(origin=0xFC00_0000, size=0x4_0000, mode="rwx"))

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

    def finalize(self, *args, **kwargs):
        super(BaseSoC, self).finalize(*args, **kwargs)
        if self.cpu_type != "zynq7000":
            return

        libxil_path = os.path.join(self.builder.software_dir, 'libxil')
        os.makedirs(os.path.realpath(libxil_path), exist_ok=True)
        lib = os.path.join(libxil_path, 'embeddedsw')
        if not os.path.exists(lib):
            os.system("git clone --depth 1 https://github.com/Xilinx/embeddedsw {}".format(lib))

        os.makedirs(os.path.realpath(self.builder.include_dir), exist_ok=True)
        for header in [
            'XilinxProcessorIPLib/drivers/uartps/src/xuartps_hw.h',
            'lib/bsp/standalone/src/common/xil_types.h',
            'lib/bsp/standalone/src/common/xil_assert.h',
            'lib/bsp/standalone/src/common/xil_io.h',
            'lib/bsp/standalone/src/common/xil_printf.h',
            'lib/bsp/standalone/src/common/xstatus.h',
            'lib/bsp/standalone/src/common/xdebug.h',
            'lib/bsp/standalone/src/arm/cortexa9/xpseudo_asm.h',
            'lib/bsp/standalone/src/arm/cortexa9/xreg_cortexa9.h',
            'lib/bsp/standalone/src/arm/cortexa9/xil_cache.h',
            'lib/bsp/standalone/src/arm/cortexa9/xparameters_ps.h',
            'lib/bsp/standalone/src/arm/cortexa9/xil_errata.h',
            'lib/bsp/standalone/src/arm/cortexa9/xtime_l.h',
            'lib/bsp/standalone/src/arm/common/xil_exception.h',
            'lib/bsp/standalone/src/arm/common/gcc/xpseudo_asm_gcc.h',
        ]:
            shutil.copy(os.path.join(lib, header), self.builder.include_dir)
        write_to_file(os.path.join(self.builder.include_dir, 'bspconfig.h'),
                      '#define FPU_HARD_FLOAT_ABI_ENABLED 1')
        write_to_file(os.path.join(self.builder.include_dir, 'xparameters.h'), '''
#ifndef __XPARAMETERS_H
#define __XPARAMETERS_H

#include "xparameters_ps.h"

#define STDOUT_BASEADDRESS 0xE0000000
#define XPAR_PS7_DDR_0_S_AXI_BASEADDR 0x00100000
#define XPAR_PS7_DDR_0_S_AXI_HIGHADDR 0x1FFFFFFF

#endif
''')


# Build --------------------------------------------------------------------------------------------


def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=digilent_arty_z7.Platform, description="LiteX SoC on Arty Z7")
    parser.add_target_argument("--variant",      default="z7-20",           help="Board variant (z7-20 or z7-10).")
    parser.add_target_argument("--sys-clk-freq", default=125e6, type=float, help="System clock frequency.")
    parser.set_defaults(cpu_type="zynq7000")
    parser.set_defaults(no_uart=True)
    args = parser.parse_args()

    soc = BaseSoC(
        variant      = args.variant,
        toolchain    = args.toolchain,
        sys_clk_freq = args.sys_clk_freq,
        **parser.soc_argdict
    )
    builder = Builder(soc, **parser.builder_argdict)
    if args.cpu_type == "zynq7000":
        soc.builder = builder
        builder.add_software_package('libxil')
        builder.add_software_library('libxil')
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"), device=1)

if __name__ == "__main__":
    main()
