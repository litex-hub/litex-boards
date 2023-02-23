#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019-2020 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2022 Oliver Szabo <16oliver16@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import *

from litex_boards.platforms import digilent_zybo_z7

from litex.soc.interconnect import axi
from litex.soc.interconnect import wishbone

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.integration.soc import SoCRegion

from litex.soc.cores import cpu
# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, use_ps7_clk=False):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()
        # # #

        if use_ps7_clk:
            self.comb   +=  ClockSignal("sys").eq(ClockSignal("ps7"))
            self.comb   +=  ResetSignal("sys").eq(ResetSignal("ps7") | self.rst)
        else:
            self.pll    =   pll = S7PLL(speedgrade=-1)
            self.comb   +=  pll.reset.eq(self.rst)
            pll.register_clkin(platform.request("clk125"), 125e6)
            pll.create_clkout(self.cd_sys, sys_clk_freq)
            platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=100e6, variant="z7-10", with_ps7=False, with_led_chaser=True, **kwargs):
        platform = digilent_zybo_z7.Platform(variant=variant)
        self.builder    = None
        # CRG --------------------------------------------------------------------------------------
        use_ps7_clk     = (kwargs.get("cpu_type", None) == "zynq7000")
        self.crg        = _CRG(platform, sys_clk_freq, use_ps7_clk)

        # SoCCore ----------------------------------------------------------------------------------
        if kwargs["uart_name"] == "serial":
            kwargs["uart_name"] = "usb_uart" # Use USB-UART Pmod on JB.
        if kwargs.get("cpu_type", None) == "zynq7000":
            kwargs["integrated_sram_size"] = 0x0
            kwargs["with_uart"] = False
            self.mem_map = {
                'csr': 0x4000_0000,  # Zynq GP0 default
            }
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Zybo Z7/original Zybo", **kwargs)

        # Zynq7000 Integration ---------------------------------------------------------------------
        if kwargs.get("cpu_type", None) == "zynq7000":
            self.cpu.use_rom = True
            if variant in ["z7-20", "original"]:
                # Get and set the pre-generated .xci FIXME: change location? add it to the repository? Make config
                os.makedirs("xci", exist_ok=True)
                os.system("wget https://github.com/litex-hub/litex-boards/files/8339591/zybo_z7_ps7.txt")
                os.system("mv zybo_z7_ps7.txt xci/zybo_z7_ps7.xci")
                self.cpu.set_ps7_xci("xci/zybo_z7_ps7.xci")
            else:
                self.cpu.set_ps7(name="ps", config = platform.ps7_config)

            # Connect AXI GP0 to the SoC with base address of 0x40000000 (default one)
            wb_gp0  = wishbone.Interface()
            self.submodules += axi.AXI2Wishbone(
                axi          = self.cpu.add_axi_gp_master(),
                wishbone     = wb_gp0,
                base_address = 0x40000000)
            self.bus.add_master(master=wb_gp0)
            #TODO memory size dependend on board variant
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
            self.bus.add_region("flash", SoCRegion(
                origin = 0xFC00_0000,
                size = 0x4_0000,
                mode = "rwx")
            )

        # PS7 as Slave Integration ---------------------------------------------------------------------
        elif with_ps7:
            if variant in ["z7-20", "original"]:
                cpu_cls = cpu.CPUS["zynq7000"]
                zynq    = cpu_cls(self.platform, "standard") # zynq7000 has no variants
                zynq.set_ps7(name="ps", config = platform.ps7_config)
                axi_gp_slave0   = zynq.add_axi_gp_slave(clock_domain = self.crg.cd_sys.name)
                self.submodules += zynq
                self.bus.add_slave(
                    name="ps",slave=axi_gp_slave0,
                    region=SoCRegion(
                        origin=0x2000_0000,
                        size=0x2000_0000,
                        mode="rwx"
                    )
                )
            else:
                #TODO: make config for zybo-z7-10
                raise NotImplementedError

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

#define STDOUT_BASEADDRESS            XPS_UART1_BASEADDR
#define XPAR_PS7_DDR_0_S_AXI_BASEADDR 0x00100000
#define XPAR_PS7_DDR_0_S_AXI_HIGHADDR 0x3FFFFFFF
#endif
''')

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=digilent_zybo_z7.Platform, description="LiteX SoC on Zybo Z7/original Zybo")
    parser.add_target_argument("--sys-clk-freq",    default=125e6, type=float,  help="System clock frequency.")
    parser.add_target_argument("--variant",         default="z7-10",            help="Board variant (z7-10, z7-20 or original).")
    parser.add_target_argument("--with-ps7",        action="store_true",        help="Add the PS7 as slave for soft CPUs.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq = args.sys_clk_freq,
        variant = args.variant,
        with_ps7 = args.with_ps7,
        **soc_core_argdict(args)
    )
    builder = Builder(soc, **builder_argdict(args))
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
