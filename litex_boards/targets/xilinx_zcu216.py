#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Ilia Sergachev <ilia@sergachev.ch>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import *

from litex_boards.platforms import xilinx_zcu216

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
            self.comb += ClockSignal("sys").eq(ClockSignal("ps"))
            self.comb += ResetSignal("sys").eq(ResetSignal("ps") | self.rst)
        else:
            self.pll = pll = S7PLL(speedgrade=-1)
            self.comb += pll.reset.eq(self.rst)
            pll.register_clkin(platform.request(platform.default_clk_name), platform.default_clk_freq)
            pll.create_clkout(self.cd_sys, sys_clk_freq)
            # Ignore sys_clk to pll.clkin path created by SoC's rst.
            platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=100e6, with_led_chaser=True,
        with_buttons=False, with_switches=False, **kwargs):
        platform = xilinx_zcu216.Platform()

        # CRG --------------------------------------------------------------------------------------
        use_ps7_clk = (kwargs.get("cpu_type", None) == "zynqmp")
        self.crg = _CRG(platform, sys_clk_freq, use_ps7_clk)

        # SoCCore ----------------------------------------------------------------------------------
        if kwargs.get("cpu_type", None) == "zynqmp":
            kwargs["integrated_sram_size"] = 0
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on ZCU216", **kwargs)

        # ZynqMP Integration -----------------------------------------------------------------------
        if kwargs.get("cpu_type", None) == "zynqmp":
            # generated from board xml presets
            self.cpu.config.update({
                'PSU__CRF_APB__ACPU_CTRL__FREQMHZ' : '1200',
                'PSU__DDRC__BANK_ADDR_COUNT'       : '2',
                'PSU__DDRC__BG_ADDR_COUNT'         : '1',
                'PSU__DDRC__BRC_MAPPING'           : 'ROW_BANK_COL',
                'PSU__DDRC__BUS_WIDTH'             : '64 Bit',
                'PSU__DDRC__CL'                    : '15',
                'PSU__DDRC__CLOCK_STOP_EN'         : '0',
                'PSU__DDRC__COL_ADDR_COUNT'        : '10',
                'PSU__DDRC__COMPONENTS'            : 'UDIMM',
                'PSU__DDRC__CWL'                   : '11',
                'PSU__DDRC__DDR4_ADDR_MAPPING'     : '0',
                'PSU__DDRC__DDR4_CAL_MODE_ENABLE'  : '0',
                'PSU__DDRC__DDR4_CRC_CONTROL'      : '0',
                'PSU__DDRC__DDR4_T_REF_MODE'       : '0',
                'PSU__DDRC__DDR4_T_REF_RANGE'      : 'Normal (0-85)',
                'PSU__DDRC__DEVICE_CAPACITY'       : '8192 MBits',
                'PSU__DDRC__DIMM_ADDR_MIRROR'      : '0',
                'PSU__DDRC__DM_DBI'                : 'DM_NO_DBI',
                'PSU__DDRC__DRAM_WIDTH'            : '16 Bits',
                'PSU__DDRC__ECC'                   : 'Disabled',
                'PSU__DDRC__FGRM'                  : '1X',
                'PSU__DDRC__LP_ASR'                : 'manual normal',
                'PSU__DDRC__MEMORY_TYPE'           : 'DDR 4',
                'PSU__DDRC__PARITY_ENABLE'         : '0',
                'PSU__DDRC__PER_BANK_REFRESH'      : '0',
                'PSU__DDRC__PHY_DBI_MODE'          : '0',
                'PSU__DDRC__RANK_ADDR_COUNT'       : '0',
                'PSU__DDRC__ROW_ADDR_COUNT'        : '16',
                'PSU__DDRC__SELF_REF_ABORT'        : '0',
                'PSU__DDRC__SPEED_BIN'             : 'DDR4_2133P',
                'PSU__DDRC__STATIC_RD_MODE'        : '0',
                'PSU__DDRC__TRAIN_DATA_EYE'        : '1',
                'PSU__DDRC__TRAIN_READ_GATE'       : '1',
                'PSU__DDRC__TRAIN_WRITE_LEVEL'     : '1',
                'PSU__DDRC__T_FAW'                 : '30.0',
                'PSU__DDRC__T_RAS_MIN'             : '33',
                'PSU__DDRC__T_RC'                  : '46.5',
                'PSU__DDRC__T_RCD'                 : '15',
                'PSU__DDRC__T_RP'                  : '15',
                'PSU__DDRC__VREF'                  : '1',
                'PSU__UART0__PERIPHERAL__ENABLE'   : '1',
                'PSU__UART0__PERIPHERAL__IO'       : 'MIO 18 .. 19',
            })

            self.bus.add_region("sram", SoCRegion(
                origin = self.cpu.mem_map["sram"],
                size   = 2 * GIGABYTE)  # DDR
            )
            self.bus.add_region("rom", SoCRegion(
                origin = self.cpu.mem_map["rom"],
                size   = 512 * MEGABYTE // 8,
                linker = True)
            )
            self.constants["CONFIG_CLOCK_FREQUENCY"] = 1200000000
            self.cpu.set_libxil({
                "STDIN_BASEADDRESS"                         : "0xFF000000",
                "STDOUT_BASEADDRESS"                        : "0xFF000000",
                "XPAR_PSU_DDR_0_S_AXI_BASEADDR"             : "0x00000000",
                "XPAR_PSU_DDR_0_S_AXI_HIGHADDR"             : "0x7FFFFFFF",
                "XPAR_PSU_DDR_1_S_AXI_BASEADDR"             : "0x800000000",
                "XPAR_PSU_DDR_1_S_AXI_HIGHADDR"             : "0x87FFFFFFF",
                "XPAR_CPU_CORTEXA53_0_TIMESTAMP_CLK_FREQ"   : "99999001",
            })

        # LEDs -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

        # Buttons / Switches -----------------------------------------------------------------------
        if with_buttons:
            self.buttons = GPIOIn(Cat(
                platform.request("user_btn_c"),
                platform.request("user_btn_e"),
                platform.request("user_btn_n"),
                platform.request("user_btn_s"),
                platform.request("user_btn_w"),
            ))
        if with_switches:
            self.switches = GPIOIn(Cat(platform.request_all("user_dip")))

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=xilinx_zcu216.Platform, description="LiteX SoC on ZCU216.")
    parser.add_target_argument("--sys-clk-freq",        default=100e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-buttons",        action="store_true",      help="Enable Buttons.")
    parser.add_target_argument("--with-switches",       action="store_true",      help="Enable Switches.")
    parser.set_defaults(cpu_type="zynqmp")
    parser.set_defaults(no_uart=True)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq  = args.sys_clk_freq,
        with_buttons  = args.with_buttons,
        with_switches = args.with_switches,
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
