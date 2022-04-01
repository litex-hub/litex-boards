#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# Build/Load bitstream:
# ./decklink_quad_hdmi_recorder.py --csr-csv=csr.csv --build --load
#
# Use:
# litex_server --jtag --jtag-config=openocd_xc7_ft232.cfg
# litex_term crossover

import os

from migen import *

from litex_boards.platforms import quad_hdmi_recorder

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

from litedram.common import PHYPadsReducer
from litedram.modules import MT41J256M16
from litedram.phy import usddrphy

from litepcie.phy.uspciephy import USPCIEPHY
from litepcie.software import generate_litepcie_software

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.clock_domains.cd_sys    = ClockDomain()
        self.clock_domains.cd_sys4x  = ClockDomain()
        self.clock_domains.cd_pll4x  = ClockDomain()
        self.clock_domains.cd_idelay = ClockDomain()

        # # #

        self.submodules.pll = pll = USMMCM(speedgrade=-2)
        pll.register_clkin(platform.request("clk200"), 200e6)
        pll.create_clkout(self.cd_pll4x, sys_clk_freq*4, buf=None, with_reset=False)
        pll.create_clkout(self.cd_idelay, 200e6)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.
        self.specials += [
            Instance("BUFGCE_DIV", name="main_bufgce_div",
                p_BUFGCE_DIVIDE=4,
                i_CE=1, i_I=self.cd_pll4x.clk, o_O=self.cd_sys.clk),
            Instance("BUFGCE", name="main_bufgce",
                i_CE=1, i_I=self.cd_pll4x.clk, o_O=self.cd_sys4x.clk),
        ]
        self.submodules.idelayctrl = USIDELAYCTRL(cd_ref=self.cd_idelay, cd_sys=self.cd_sys)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(200e6), with_pcie=False, pcie_lanes=4, **kwargs):
        platform = quad_hdmi_recorder.Platform()

        # SoCCore ----------------------------------------------------------------------------------
        kwargs["uart_name"] = "crossover"
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident = "LiteX SoC on Blackmagic Decklink Quad HDMI Recorder",
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # JTAGBone  --------------------------------------------------------------------------------
        self.add_jtagbone()

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.submodules.ddrphy = usddrphy.USDDRPHY(
                pads             = PHYPadsReducer(platform.request("ddram"), [0, 1, 2, 3]),
                memtype          = "DDR3",
                sys_clk_freq     = sys_clk_freq,
                iodelay_clk_freq = 200e6)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT41J256M16(sys_clk_freq, "1:4"),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # PCIe -------------------------------------------------------------------------------------
        # FIXME: Does not seem to be working when also enabling DRAM. Has been tested succesfully by
        # disabling DRAM with --integrated-main-ram-size=0x100.
        if with_pcie:
            data_width = {
                4 : 128,
                8 : 256,
            }[pcie_lanes]
            self.submodules.pcie_phy = USPCIEPHY(platform, platform.request(f"pcie_x{pcie_lanes}"),
                speed      = "gen3",
                data_width = data_width,
                bar0_size  = 0x20000)
            self.add_pcie(phy=self.pcie_phy, ndmas=1)
            # False Paths (FIXME: Improve integration).
            platform.toolchain.pre_placement_commands.append("set_false_path -from [get_clocks sys_clk] -to [get_clocks pcie_clk_1]")
            platform.toolchain.pre_placement_commands.append("set_false_path -from [get_clocks pcie_clk_1] -to [get_clocks sys_clk]")

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on Blackmagic Decklink Quad HDMI Recorder")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",        action="store_true", help="Build bitstream.")
    target_group.add_argument("--load",         action="store_true", help="Load bitstream.")
    target_group.add_argument("--sys-clk-freq", default=200e6,       help="System clock frequency.")
    target_group.add_argument("--with-pcie",    action="store_true", help="Enable PCIe support.")
    target_group.add_argument("--driver",       action="store_true", help="Generate PCIe driver.")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq   = int(float(args.sys_clk_freq)),
        with_pcie      = args.with_pcie,
        **soc_core_argdict(args)
	)
    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.driver:
        generate_litepcie_software(soc, os.path.join(builder.output_dir, "driver"))

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
