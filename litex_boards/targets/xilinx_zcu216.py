#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Ilia Sergachev <ilia@sergachev.ch>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex_boards.platforms import xilinx_zcu216
from litex.build.xilinx.vivado import vivado_build_args, vivado_build_argdict
from litex.build.tools import write_to_file

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
            self.comb += ClockSignal("sys").eq(ClockSignal("ps"))
            self.comb += ResetSignal("sys").eq(ResetSignal("ps") | self.rst)
        else:
            self.submodules.pll = pll = S7PLL(speedgrade=-1)
            self.comb += pll.reset.eq(self.rst)
            pll.register_clkin(platform.request(platform.default_clk_name), platform.default_clk_freq)
            pll.create_clkout(self.cd_sys, sys_clk_freq)
            # Ignore sys_clk to pll.clkin path created by SoC's rst.
            platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    mem_map = {"csr": 0xA000_0000}  # default GP0 address on ZynqMP

    def __init__(self, sys_clk_freq, with_led_chaser=True, **kwargs):
        platform = xilinx_zcu216.Platform()

        if kwargs.get("cpu_type", None) == "zynqmp":
            kwargs['integrated_sram_size'] = 0

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident = "LiteX SoC on ZCU216",
            **kwargs)

        # ZynqMP Integration -----------------------------------------------------------------------
        if kwargs.get("cpu_type", None) == "zynqmp":
            # generated from board xml presets
            self.cpu.config.update({
                'PSU__CRF_APB__ACPU_CTRL__FREQMHZ': '1200',
                'PSU__DDRC__BANK_ADDR_COUNT': '2',
                'PSU__DDRC__BG_ADDR_COUNT': '1',
                'PSU__DDRC__BRC_MAPPING': 'ROW_BANK_COL',
                'PSU__DDRC__BUS_WIDTH': '64 Bit',
                'PSU__DDRC__CL': '15',
                'PSU__DDRC__CLOCK_STOP_EN': '0',
                'PSU__DDRC__COL_ADDR_COUNT': '10',
                'PSU__DDRC__COMPONENTS': 'UDIMM',
                'PSU__DDRC__CWL': '11',
                'PSU__DDRC__DDR4_ADDR_MAPPING': '0',
                'PSU__DDRC__DDR4_CAL_MODE_ENABLE': '0',
                'PSU__DDRC__DDR4_CRC_CONTROL': '0',
                'PSU__DDRC__DDR4_T_REF_MODE': '0',
                'PSU__DDRC__DDR4_T_REF_RANGE': 'Normal (0-85)',
                'PSU__DDRC__DEVICE_CAPACITY': '8192 MBits',
                'PSU__DDRC__DIMM_ADDR_MIRROR': '0',
                'PSU__DDRC__DM_DBI': 'DM_NO_DBI',
                'PSU__DDRC__DRAM_WIDTH': '16 Bits',
                'PSU__DDRC__ECC': 'Disabled',
                'PSU__DDRC__FGRM': '1X',
                'PSU__DDRC__LP_ASR': 'manual normal',
                'PSU__DDRC__MEMORY_TYPE': 'DDR 4',
                'PSU__DDRC__PARITY_ENABLE': '0',
                'PSU__DDRC__PER_BANK_REFRESH': '0',
                'PSU__DDRC__PHY_DBI_MODE': '0',
                'PSU__DDRC__RANK_ADDR_COUNT': '0',
                'PSU__DDRC__ROW_ADDR_COUNT': '16',
                'PSU__DDRC__SELF_REF_ABORT': '0',
                'PSU__DDRC__SPEED_BIN': 'DDR4_2133P',
                'PSU__DDRC__STATIC_RD_MODE': '0',
                'PSU__DDRC__TRAIN_DATA_EYE': '1',
                'PSU__DDRC__TRAIN_READ_GATE': '1',
                'PSU__DDRC__TRAIN_WRITE_LEVEL': '1',
                'PSU__DDRC__T_FAW': '30.0',
                'PSU__DDRC__T_RAS_MIN': '33',
                'PSU__DDRC__T_RC': '46.5',
                'PSU__DDRC__T_RCD': '15',
                'PSU__DDRC__T_RP': '15',
                'PSU__DDRC__VREF': '1',
                'PSU__UART0__PERIPHERAL__ENABLE': '1',
                'PSU__UART0__PERIPHERAL__IO': 'MIO 18 .. 19',
            })

            # Connect Zynq AXI master to the SoC
            wb_gp0 = wishbone.Interface()
            self.submodules += axi.AXI2Wishbone(
                axi          = self.cpu.add_axi_gp_master(),
                wishbone     = wb_gp0,
                base_address = self.mem_map["csr"])
            self.add_wb_master(wb_gp0)
            self.bus.add_region("sram", SoCRegion(
                origin=self.cpu.mem_map["sram"],
                size=2 * 1024 * 1024 * 1024)  # DDR
            )
            self.bus.add_region("rom", SoCRegion(
                origin=self.cpu.mem_map["rom"],
                size=512 * 1024 * 1024 // 8,
                linker=True)
            )
            self.constants['CONFIG_CLOCK_FREQUENCY'] = 1200000000

            use_ps7_clk = True
        else:
            use_ps7_clk = False

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq, use_ps7_clk)

        # LEDs -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

    def finalize(self, *args, **kwargs):
        super(BaseSoC, self).finalize(*args, **kwargs)
        if self.cpu_type != "zynqmp":
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
            'lib/bsp/standalone/src/arm/ARMv8/64bit/xpseudo_asm.h',
            'lib/bsp/standalone/src/arm/ARMv8/64bit/xreg_cortexa53.h',
            'lib/bsp/standalone/src/arm/ARMv8/64bit/xil_cache.h',
            'lib/bsp/standalone/src/arm/ARMv8/64bit/xil_errata.h',
            'lib/bsp/standalone/src/arm/ARMv8/64bit/platform/ZynqMP/xparameters_ps.h',
            'lib/bsp/standalone/src/arm/common/xil_exception.h',
            'lib/bsp/standalone/src/arm/common/gcc/xpseudo_asm_gcc.h',
        ]:
            shutil.copy(os.path.join(lib, header), self.builder.include_dir)

        write_to_file(os.path.join(self.builder.include_dir, 'bspconfig.h'), """
#ifndef BSPCONFIG_H
#define BSPCONFIG_H

#define EL3 1
#define EL1_NONSECURE 0

#endif
""")
        write_to_file(os.path.join(self.builder.include_dir, 'xparameters.h'), '''
#ifndef XPARAMETERS_H
#define XPARAMETERS_H

#include "xparameters_ps.h"

#define STDIN_BASEADDRESS 0xFF000000
#define STDOUT_BASEADDRESS 0xFF000000
#define XPAR_PSU_DDR_0_S_AXI_BASEADDR 0x00000000
#define XPAR_PSU_DDR_0_S_AXI_HIGHADDR 0x7FFFFFFF
#define XPAR_PSU_DDR_1_S_AXI_BASEADDR 0x800000000
#define XPAR_PSU_DDR_1_S_AXI_HIGHADDR 0x87FFFFFFF
#define XPAR_CPU_CORTEXA53_0_TIMESTAMP_CLK_FREQ 99999001

#endif
''')


# Build --------------------------------------------------------------------------------------------

def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on ZCU216")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",        action="store_true", help="Build bitstream.")
    target_group.add_argument("--load",         action="store_true", help="Load bitstream.")
    target_group.add_argument("--sys-clk-freq", default=100e6,       help="System clock frequency.")
    builder_args(parser)
    soc_core_args(parser)
    vivado_build_args(parser)
    parser.set_defaults(cpu_type="zynqmp")
    parser.set_defaults(no_uart=True)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq=int(float(args.sys_clk_freq)),
        **soc_core_argdict(args)
    )
    builder = Builder(soc, **builder_argdict(args))
    if args.cpu_type == "zynqmp":
        soc.builder = builder
        builder.add_software_package('libxil')
        builder.add_software_library('libxil')
    builder.build(**vivado_build_argdict(args), run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
