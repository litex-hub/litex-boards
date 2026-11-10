#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# Build/Use (as the KV260, same K26 SOM):
# LiteX BIOS on Cortex-A53 core #0 (default):
# ./xilinx_kr260.py --build --load
# then run it over JTAG with xsct (see xilinx_kv260.py).
#
# Soft CPU from the PL's 25 MHz clock (e.g. with Ethernet/Etherbone on the PL GEM2 port):
# ./xilinx_kr260.py --cpu-type=vexriscv --uart-name=jtag_uart --with-etherbone --build --load

from migen import *

from litex.gen import *

from litex_boards.platforms import xilinx_kr260

from litex.soc.cores.clock import *
from litex.soc.integration.soc import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from liteeth.phy.usrgmii import LiteEthPHYRGMII

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, use_ps_clk=False, with_idelay=False):
        self.rst       = Signal()
        self.cd_sys    = ClockDomain()
        self.cd_idelay = ClockDomain()

        # # #

        # PL clock: 25 MHz from the carrier.
        if (not use_ps_clk) or with_idelay:
            self.pll = pll = USPMMCM(speedgrade=-2)
            self.comb += pll.reset.eq(self.rst)
            pll.register_clkin(platform.request("clk25", 0), 25e6)
        if use_ps_clk:
            # sys_clk from the PS (pl_clk0).
            self.comb += ClockSignal("sys").eq(ClockSignal("ps"))
            self.comb += ResetSignal("sys").eq(ResetSignal("ps") | self.rst)
        else:
            # With the IDELAYCTRL, sys_rst is released by it (once the delays are calibrated).
            pll.create_clkout(self.cd_sys, sys_clk_freq, with_reset=not with_idelay)
            # Ignore sys_clk to pll.clkin path created by SoC's rst.
            platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin)

        # IDelayCtrl (RGMII delays).
        if with_idelay:
            pll.create_clkout(self.cd_idelay, 300e6)
            self.idelayctrl = USPIDELAYCTRL(cd_ref=self.cd_idelay, cd_sys=self.cd_sys)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=100e6,
        with_ethernet   = False,
        with_etherbone  = False,
        eth_ip          = "192.168.1.50",
        eth_dynamic_ip  = False,
        with_led_chaser = True,
        **kwargs):
        platform = xilinx_kr260.Platform()

        # CRG --------------------------------------------------------------------------------------
        use_ps_clk = (kwargs.get("cpu_type", None) == "zynqmp")
        self.crg = _CRG(platform, sys_clk_freq,
            use_ps_clk  = use_ps_clk,
            with_idelay = with_ethernet or with_etherbone)

        # SoCCore ----------------------------------------------------------------------------------
        if kwargs.get("cpu_type", None) == "zynqmp":
            # The console is the PS's UART1, the BIOS runs from the DDR.
            kwargs["integrated_sram_size"] = 0
            kwargs["with_uart"]            = False
        elif kwargs.get("uart_name", "serial") == "serial":
            kwargs["uart_name"] = "jtag_uart" # No UART pins on the PL.
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on KR260", **kwargs)

        # ZynqMP Integration -----------------------------------------------------------------------
        if kwargs.get("cpu_type", None) == "zynqmp":
            # UART1 on MIO 36/37 (the carrier's USB-UART).
            self.cpu.config.update({
                'PSU_MIO_36_DIRECTION'                   : 'out',
                'PSU_MIO_37_DIRECTION'                   : 'in',
                'PSU__UART1__BAUD_RATE'                  : 115200,
                'PSU__CRL_APB__UART1_REF_CTRL__DIVISOR0' : 10,
            })
            # From AMD's K26 SOM board presets (XilinxBoardStore k26c/kr260_som: DDR4-2400R), as on the
            # KV260 (same SOM); CWL 12: the presets' 14 is rejected by Vivado's PS validation at
            # DDR4-2400 (supported: 12, 16).
            self.cpu.config.update({
                'PSU__CRF_APB__ACPU_CTRL__FREQMHZ' : '1333.333',
                'PSU__DDRC__BANK_ADDR_COUNT'       : '2',
                'PSU__DDRC__BG_ADDR_COUNT'         : '1',
                'PSU__DDRC__BRC_MAPPING'           : 'ROW_BANK_COL',
                'PSU__DDRC__BUS_WIDTH'             : '64 Bit',
                'PSU__DDRC__CL'                    : '16',
                'PSU__DDRC__CLOCK_STOP_EN'         : '0',
                'PSU__DDRC__COL_ADDR_COUNT'        : '10',
                'PSU__DDRC__COMPONENTS'            : 'Components',
                'PSU__DDRC__CWL'                   : '12',
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
                'PSU__DDRC__SPEED_BIN'             : 'DDR4_2400R',
                'PSU__DDRC__STATIC_RD_MODE'        : '0',
                'PSU__DDRC__TRAIN_DATA_EYE'        : '1',
                'PSU__DDRC__TRAIN_READ_GATE'       : '1',
                'PSU__DDRC__TRAIN_WRITE_LEVEL'     : '1',
                'PSU__DDRC__T_FAW'                 : '30.0',
                'PSU__DDRC__T_RAS_MIN'             : '33',
                'PSU__DDRC__T_RC'                  : '47.06',
                'PSU__DDRC__T_RCD'                 : '16',
                'PSU__DDRC__T_RP'                  : '16',
                'PSU__DDRC__VREF'                  : '1',
                'PSU__FPGA_PL0_ENABLE'             : '1',
                'PSU__PMU__GPO4__ENABLE'           : '0',  # these 2 are disabled for uart1
                'PSU__PMU__GPO5__ENABLE'           : '0',
                'PSU__UART1__PERIPHERAL__ENABLE'   : '1',
                'PSU__UART1__PERIPHERAL__IO'       : 'MIO 36 .. 37',
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
            self.constants["CONFIG_CLOCK_FREQUENCY"] = 1333333008
            self.cpu.set_libxil({
                "STDIN_BASEADDRESS"                         : "0xFF010000",
                "STDOUT_BASEADDRESS"                        : "0xFF010000",
                "XPAR_PSU_DDR_0_S_AXI_BASEADDR"             : "0x00000000",
                "XPAR_PSU_DDR_0_S_AXI_HIGHADDR"             : "0x7FFFFFFF",
                "XPAR_PSU_DDR_1_S_AXI_BASEADDR"             : "0x800000000",
                "XPAR_PSU_DDR_1_S_AXI_HIGHADDR"             : "0x87FFFFFFF",
                "XPAR_CPU_CORTEXA53_0_TIMESTAMP_CLK_FREQ"   : "99999001",
            })

        # Ethernet / Etherbone (PL GEM2 port) ------------------------------------------------------
        if with_ethernet or with_etherbone:
            self.ethphy = LiteEthPHYRGMII(
                clock_pads       = self.platform.request("eth_clocks", 0),
                pads             = self.platform.request("eth", 0),
                # No delays on the FPGA side: assumes the PHY's internal RGMII delays (not
                # checked on hardware).
                tx_delay         = 0e-9,
                rx_delay         = 0e-9,
                iodelay_clk_freq = 300e6,
                usp              = True)
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, ip_address=eth_ip, with_ethmac=with_ethernet)
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy, dynamic_ip=eth_dynamic_ip, local_ip=eth_ip)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser           import LiteXArgumentParser
    from litex_boards.extensions.pmod import add_pmod_args, add_pmods
    parser = LiteXArgumentParser(platform=xilinx_kr260.Platform, description="LiteX SoC on KR260.")
    parser.add_target_argument("--sys-clk-freq",   default=100e6, type=float, help="System clock frequency.")
    ethopts = parser.target_group.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",        action="store_true",       help="Enable Ethernet support (PL GEM2 port).")
    ethopts.add_argument("--with-etherbone",       action="store_true",       help="Enable Etherbone support (PL GEM2 port).")
    parser.add_target_argument("--eth-ip",         default="192.168.1.50",    help="Ethernet/Etherbone IP address.")
    parser.add_target_argument("--eth-dynamic-ip", action="store_true",       help="Enable dynamic Ethernet IP addresses setting.")
    parser.set_defaults(cpu_type="zynqmp")
    add_pmod_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq   = args.sys_clk_freq,
        with_ethernet  = args.with_ethernet,
        with_etherbone = args.with_etherbone,
        eth_ip         = args.eth_ip,
        eth_dynamic_ip = args.eth_dynamic_ip,
        **parser.soc_argdict
    )
    add_pmods(soc, args.pmod)
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
