#!/usr/bin/env python3

# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause
#
# Build/Use:
# ./ypcb_00338_1p1_target.py --uart-name=jtag_uart --with-pcie --build --load
# litex_term jtag --jtag-config=openocd_xc7_ft232.cfg

import os

from migen import *
from litex.gen import *

from litex_boards.platforms import ypcb_00338_1p1

from litex.soc.cores.clock          import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder  import *
from litex.soc.cores.led            import LedChaser

from litedram.modules import MT41J256M16
from litedram.phy     import s7ddrphy
from litedram.common import PHYPadsReducer

from litepcie.phy.s7pciephy import S7PCIEPHY
from litepcie.software import generate_litepcie_software

# CRG -------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst       = Signal()
        self.cd_sys    = ClockDomain()
        self.cd_sys4x  = ClockDomain()
        self.cd_sys4x_dqs = ClockDomain()
        self.cd_idelay = ClockDomain()

        # Clk/Rst.
        clk50 = platform.request("clk50")
        rst_n = platform.request("rst_n")

        # PLL.
        self.pll = pll = S7MMCM(speedgrade=-2)
        self.comb += pll.reset.eq(~rst_n | self.rst)
        pll.register_clkin(clk50, 50e6)
        pll.create_clkout(self.cd_sys,       sys_clk_freq)
        pll.create_clkout(self.cd_sys4x,     4*sys_clk_freq)
        pll.create_clkout(self.cd_sys4x_dqs, 4*sys_clk_freq, phase=135)
        pll.create_clkout(self.cd_idelay,    200e6)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        # IDelayCtrl.
        self.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=125e6,
        dram_channel    = 0,
        with_led_chaser = True,
        with_pcie       = False,
        **kwargs):

        # Platform ---------------------------------------------------------------------------------
        platform = ypcb_00338_1p1.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        if kwargs["uart_name"] == "serial":
            kwargs["uart_name"] = "jtag_uart"
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on YPCB-00338-1P1", **kwargs)

        # DDR3 SDRAM ------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            assert dram_channel in (0, 1), "dram_channel must be 0 or 1"
            self.ddrphy = s7ddrphy.A7DDRPHY( # FIXME: DDR3 on HR Bank so no ODELAY, use A7DDRPHY as workaround for now.
                pads         = PHYPadsReducer(platform.request("ddram", dram_channel), [0, 1, 2, 3]), # FIXME: Get all modules working.
                memtype      = "DDR3",
                nphases      = 4,
                sys_clk_freq = sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT41J256M16(sys_clk_freq, "1:4"),
                size          = 0x20000000,
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # PCIe -------------------------------------------------------------------------------------
        if with_pcie:
            self.pcie_phy = S7PCIEPHY(platform, platform.request("pcie_x8"),
                data_width = 128,
                bar0_size  = 0x20000)
            self.add_pcie(phy=self.pcie_phy, ndmas=1)
            platform.toolchain.pre_placement_commands.append("reset_property LOC [get_cells -hierarchical -filter {{NAME=~pcie_s7/*gtx_channel.gtxe2_channel_i}}]")
            platform.toolchain.pre_placement_commands.append("set_property LOC GTXE2_CHANNEL_X0Y23 [get_cells -hierarchical -filter {{NAME=~pcie_s7/*pipe_lane[0].gt_wrapper_i/gtx_channel.gtxe2_channel_i}}]")
            platform.toolchain.pre_placement_commands.append("set_property LOC GTXE2_CHANNEL_X0Y22 [get_cells -hierarchical -filter {{NAME=~pcie_s7/*pipe_lane[1].gt_wrapper_i/gtx_channel.gtxe2_channel_i}}]")
            platform.toolchain.pre_placement_commands.append("set_property LOC GTXE2_CHANNEL_X0Y21 [get_cells -hierarchical -filter {{NAME=~pcie_s7/*pipe_lane[2].gt_wrapper_i/gtx_channel.gtxe2_channel_i}}]")
            platform.toolchain.pre_placement_commands.append("set_property LOC GTXE2_CHANNEL_X0Y20 [get_cells -hierarchical -filter {{NAME=~pcie_s7/*pipe_lane[3].gt_wrapper_i/gtx_channel.gtxe2_channel_i}}]")

            platform.toolchain.pre_placement_commands.append("set_property LOC GTXE2_CHANNEL_X0Y19 [get_cells -hierarchical -filter {{NAME=~pcie_s7/*pipe_lane[4].gt_wrapper_i/gtx_channel.gtxe2_channel_i}}]")
            platform.toolchain.pre_placement_commands.append("set_property LOC GTXE2_CHANNEL_X0Y18 [get_cells -hierarchical -filter {{NAME=~pcie_s7/*pipe_lane[5].gt_wrapper_i/gtx_channel.gtxe2_channel_i}}]")
            platform.toolchain.pre_placement_commands.append("set_property LOC GTXE2_CHANNEL_X0Y17 [get_cells -hierarchical -filter {{NAME=~pcie_s7/*pipe_lane[6].gt_wrapper_i/gtx_channel.gtxe2_channel_i}}]")
            platform.toolchain.pre_placement_commands.append("set_property LOC GTXE2_CHANNEL_X0Y16 [get_cells -hierarchical -filter {{NAME=~pcie_s7/*pipe_lane[7].gt_wrapper_i/gtx_channel.gtxe2_channel_i}}]")


        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(platform.request_all("user_led"), sys_clk_freq)

# Build ------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=ypcb_00338_1p1.Platform, description="LiteX SoC on YPCB-00338-1P1.")
    parser.add_target_argument("--sys-clk-freq",   default=125e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-pcie",      action="store_true",       help="Enable PCIe support.")
    parser.add_target_argument("--driver",         action="store_true",       help="Generate PCIe driver.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq   = args.sys_clk_freq,
        with_pcie      = args.with_pcie,
        **parser.soc_argdict
    )
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.driver:
        generate_litepcie_software(soc, os.path.join(builder.output_dir, "driver"))

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
