#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2024-2026 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2024 Gwenhael Goavec-Merou <gwenhael@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause
#
# More complete Agilex 5 test project:
# https://github.com/enjoy-digital/litex_agilex5_test

from migen import *

from litex.gen import *

from litex_boards.platforms import altera_agilex5e_065b_premium_devkit

from litex.soc.integration.soc      import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder  import *

from litex.soc.cores.clock import Agilex5PLL
from litex.soc.cores.led   import LedChaser

# Helpers ------------------------------------------------------------------------------------------

def _patch_agilex_pll_register_clkin_compat():
    import inspect
    from litex.soc.cores.clock import intel_agilex

    register_clkin = intel_agilex.AgilexPLL.register_clkin
    if len(inspect.signature(register_clkin).parameters) != 3:
        return

    def register_clkin_compat(self, clkin, freq, name=None):
        if name is not None and isinstance(clkin, Signal) and clkin.name_override is None:
            clkin.name_override = name
        return register_clkin(self, clkin, freq)

    intel_agilex.AgilexPLL.register_clkin = register_clkin_compat

class _LiteEthPlatformProxy:
    def __init__(self, platform):
        self._platform = platform
        self.device    = platform.device[:-2] if platform.device.endswith("R0") else platform.device

    def __getattr__(self, name):
        return getattr(self._platform, name)

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()

        # # #

        # Clk / Rst.
        clk100 = platform.request("clk100", 0)
        rst_n  = platform.request("user_btn", 0)

        # Power on reset.
        ninit_done = Signal()
        self.specials += Instance("altera_agilex_config_reset_release_endpoint", o_conf_reset=ninit_done)

        # PLL.
        self.pll = pll = Agilex5PLL(platform, speedgrade=platform.speedgrade)
        self.comb += pll.reset.eq(ninit_done | ~rst_n | self.rst)
        pll.register_clkin(clk100, 100e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=100e6,
        variant         = "production",
        with_ethernet   = False,
        with_etherbone  = False,
        eth_ip          = "192.168.1.50",
        remote_ip       = None,
        eth_dynamic_ip  = False,
        with_sdcard     = False,
        with_spi_sdcard = False,
        with_led_chaser = True,
        **kwargs):
        kwargs.setdefault("integrated_main_ram_size", 64*KILOBYTE)

        platform = altera_agilex5e_065b_premium_devkit.Platform(variant=variant)
        with_eth = with_ethernet or with_etherbone

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident = "LiteX SoC on Altera Agilex 5E 065B Premium Development Kit",
            **kwargs)

        # SDCard -----------------------------------------------------------------------------------
        if with_sdcard or with_spi_sdcard:
            platform.add_extension(altera_agilex5e_065b_premium_devkit._sdcard_io)
            if with_sdcard:
                self.add_sdcard(software_debug=False)
            if with_spi_sdcard:
                self.add_spi_sdcard()

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_eth:
            _patch_agilex_pll_register_clkin_compat()
            from liteeth.phy import LiteEthAgilexPHYRGMII

            # Used by patched/newer BIOSes to tune the Marvell 88E1512 RX clock transition.
            self.add_constant("ETH_PHY_RX_CLOCK_TRANSITION")

            self.ethphy = LiteEthAgilexPHYRGMII(
                platform    = _LiteEthPlatformProxy(platform),
                clock_pads  = platform.request("eth_clocks", 2),
                pads        = platform.request("eth", 2),
                ref_tx_clk  = platform.request("clk125"),
            )

            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, ip_address=eth_ip, with_ethmac=with_ethernet)
            if with_ethernet:
                self.add_ethernet(
                    phy            = self.ethphy,
                    dynamic_ip     = eth_dynamic_ip,
                    local_ip       = eth_ip,
                    remote_ip      = remote_ip,
                    full_memory_we = True,
                    software_debug = False)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(
        platform    = altera_agilex5e_065b_premium_devkit.Platform,
        description = "LiteX SoC on Altera Agilex 5E 065B Premium Development Kit.")
    parser.add_target_argument("--sys-clk-freq", default=100e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--variant", default="production",
        choices = sorted(altera_agilex5e_065b_premium_devkit._variants),
        help    = "Board FPGA variant.")

    ethopts = parser.target_group.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",  action="store_true", help="Enable Ethernet support.")
    ethopts.add_argument("--with-etherbone", action="store_true", help="Enable Etherbone support.")
    parser.add_target_argument("--eth-ip",         default="192.168.1.50",  help="Ethernet/Etherbone IP address.")
    parser.add_target_argument("--remote-ip",      default="192.168.1.100", help="Remote IP address of TFTP server.")
    parser.add_target_argument("--eth-dynamic-ip", action="store_true",     help="Enable dynamic Ethernet IP assignment.")

    sdopts = parser.target_group.add_mutually_exclusive_group()
    sdopts.add_argument("--with-sdcard",     action="store_true", help="Enable SDCard support on J9 adapter.")
    sdopts.add_argument("--with-spi-sdcard", action="store_true", help="Enable SPI-mode SDCard support on J9 adapter.")

    # Overrides defaults synth/conv tools.
    parser.set_defaults(synth_tool="quartus_syn")
    parser.set_defaults(conv_tool="quartus_pfg")
    parser.set_defaults(integrated_main_ram_size=64*KILOBYTE)

    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq    = args.sys_clk_freq,
        variant         = args.variant,
        with_ethernet   = args.with_ethernet,
        with_etherbone  = args.with_etherbone,
        eth_ip          = args.eth_ip,
        remote_ip       = args.remote_ip,
        eth_dynamic_ip  = args.eth_dynamic_ip,
        with_sdcard     = args.with_sdcard,
        with_spi_sdcard = args.with_spi_sdcard,
        **parser.soc_argdict)

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
