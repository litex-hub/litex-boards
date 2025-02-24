#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 Enjoy-Digital <enjoy-digital.fr>
#
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from litex_boards.platforms import lattice_certuspro_nx_versa

from litex.soc.cores.clock import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

from litex.soc.cores.led import LedChaser

from litepcie.software          import *
from litepcie.phy.lfcpnxpciephy import LFCPNXPCIEPHY

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()
        self.cd_por = ClockDomain()

        # # #

        # Clk / Rst
        self.rst_n = platform.request("gsrn", 0)

        # Clocking
        self.sys_clk = sys_osc = NXOSCA()
        sys_osc.create_hf_clk(self.cd_sys, sys_clk_freq)
        platform.add_period_constraint(self.cd_sys.clk, 1e9/sys_clk_freq)

        # Power on reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += self.cd_por.clk.eq(self.cd_sys.clk)
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))
        self.specials += [
           AsyncResetSynchronizer(self.cd_por, ~self.rst_n),
           AsyncResetSynchronizer(self.cd_sys, ~por_done | self.rst),
        ]

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=75e6, toolchain="radiant",
        with_pcie       = False,
        with_led_chaser = True,
        **kwargs):
        platform = lattice_certuspro_nx_versa.Platform(toolchain=toolchain)

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on CertusPro-NX Versa Eval Board", **kwargs)

        # PCIe -------------------------------------------------------------------------------------
        if with_pcie:
            self.pcie_phy = LFCPNXPCIEPHY(platform, platform.request("pcie_x4"), cd="sys")
            self.add_pcie(phy=self.pcie_phy, ndmas=1, data_width=128, with_msi=True) # FIXME: MSI not connected in PHY!

            self.pcie_ctrl = platform.request("pcie_ctrl")
            self.comb += [
                self.pcie_ctrl.sw_sel.eq(0),
                self.pcie_ctrl.clk_sel.eq(1),
                self.pcie_ctrl.sw1_pd.eq(0),
                self.pcie_ctrl.sw2_pd.eq(0),
            ]

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=lattice_certuspro_nx_versa.Platform, description="LiteX SoC on CertusPro-NX Versa Board.")
    parser.add_target_argument("--flash",        action="store_true",      help="Flash bitstream to SPI Flash.")
    parser.add_target_argument("--sys-clk-freq", default=75e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-pcie",    action="store_true",      help="Enable PCIe support.")
    parser.add_target_argument("--driver",       action="store_true",      help="Generate PCIe driver from LitePCIe (override local version).")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq = args.sys_clk_freq,
        with_pcie    = args.with_pcie,
        **parser.soc_argdict
    )

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.with_pcie:
        if args.driver:
            generate_litepcie_software(soc, "software")
        else:
            generate_litepcie_software_headers(soc, os.path.join("software", "kernel"))

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.flash(0, builder.get_bitstream_filename(mode="flash"))

if __name__ == "__main__":
    main()
