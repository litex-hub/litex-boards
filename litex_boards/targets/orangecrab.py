#!/usr/bin/env python3

# This file is Copyright (c) Greg Davill <greg.davill@gmail.com>
# License: BSD

import os
import argparse

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex_boards.platforms import orangecrab

from litex.build.lattice.trellis import trellis_args, trellis_argdict

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc_sdram import *
from litex.soc.integration.builder import *

from litedram.modules import MT41K64M16, MT41K128M16, MT41K256M16
from litedram.phy import ECP5DDRPHY

# _CRG ---------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq, with_usb_pll=False):
        self.clock_domains.cd_init     = ClockDomain()
        self.clock_domains.cd_por      = ClockDomain(reset_less=True)
        self.clock_domains.cd_sys      = ClockDomain()
        self.clock_domains.cd_sys2x    = ClockDomain()
        self.clock_domains.cd_sys2x_i  = ClockDomain(reset_less=True)
        self.clock_domains.cd_sys2x_eb = ClockDomain(reset_less=True)


        # # #

        self.stop = Signal()

        # Clk / Rst
        clk48 = platform.request("clk48")

        # Power on reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += self.cd_por.clk.eq(ClockSignal())
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # PLL
        sys2x_clk_ecsout = Signal()
        self.submodules.pll = pll = ECP5PLL()
        pll.register_clkin(clk48, 48e6)
        pll.create_clkout(self.cd_sys2x_i, 2*sys_clk_freq)
        pll.create_clkout(self.cd_init, 24e6)
        self.specials += [
            Instance("ECLKBRIDGECS",
                i_CLK0   = self.cd_sys2x_i.clk,
                i_SEL    = 0,
                o_ECSOUT = sys2x_clk_ecsout),
            Instance("ECLKSYNCB",
                i_ECLKI = sys2x_clk_ecsout,
                i_STOP  = self.stop,
                o_ECLKO = self.cd_sys2x.clk),
            Instance("CLKDIVF",
                p_DIV     = "2.0",
                i_ALIGNWD = 0,
                i_CLKI    = self.cd_sys2x.clk,
                i_RST     = self.cd_sys2x.rst,
                o_CDIVX   = self.cd_sys.clk),
            AsyncResetSynchronizer(self.cd_init, ~por_done | ~pll.locked),
            AsyncResetSynchronizer(self.cd_sys,  ~por_done | ~pll.locked)
        ]

        # USB PLL
        if with_usb_pll:
            self.clock_domains.cd_usb_12 = ClockDomain()
            self.clock_domains.cd_usb_48 = ClockDomain()
            usb_pll = ECP5PLL()
            self.submodules += usb_pll
            usb_pll.register_clkin(clk48, 48e6)
            usb_pll.create_clkout(self.cd_usb_48, 48e6)
            usb_pll.create_clkout(self.cd_usb_12, 12e6)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, revision = "0.2", device = "25F", sdram_device = "MT41K64M16",
                 sys_clk_freq=int(48e6), toolchain="trellis", **kwargs):
        platform = orangecrab.Platform(revision=revision, device=device ,toolchain=toolchain)

        # Serial -----------------------------------------------------------------------------------
        platform.add_extension(orangecrab.feather_serial)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, clk_freq=sys_clk_freq, **kwargs)

        # CRG --------------------------------------------------------------------------------------
        with_usb_pll = kwargs.get("uart_name", None) == "usb_acm"
        self.submodules.crg = _CRG(platform, sys_clk_freq, with_usb_pll)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            available_sdram_modules = {
                'MT41K64M16': MT41K64M16,
                'MT41K128M16': MT41K128M16,
                'MT41K256M16': MT41K256M16,
#                'MT41K512M16': MT41K512M16
            }
            sdram_module = available_sdram_modules.get(sdram_device)

            self.submodules.ddrphy = ECP5DDRPHY(
                platform.request("ddram"),
                sys_clk_freq=sys_clk_freq)
            self.add_csr("ddrphy")
            self.comb += self.crg.stop.eq(self.ddrphy.init.stop)
            self.add_sdram("sdram",
                phy                     = self.ddrphy,
                module                  = sdram_module(sys_clk_freq, "1:2"),
                origin                  = self.mem_map["main_ram"],
                size                    = kwargs.get("max_sdram_size", 0x40000000),
                l2_cache_size           = kwargs.get("l2_size", 8192),
                l2_cache_min_data_width = kwargs.get("min_l2_data_width", 128),
                l2_cache_reverse        = True
            )

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on OrangeCrab")
    parser.add_argument("--build", action="store_true", help="Build bitstream")
    parser.add_argument("--gateware-toolchain", dest="toolchain", default="trellis", help="Gateware toolchain to use, trellis (default) or diamond")
    builder_args(parser)
    soc_sdram_args(parser)
    trellis_args(parser)
    parser.add_argument("--sys-clk-freq", default=48e6,         help="System clock frequency (default=48MHz)")
    parser.add_argument("--revision",     default="0.2",        help="Board Revision {0.1, 0.2} (default=0.2)")
    parser.add_argument("--device",       default="25F",        help="ECP5 device (default=25F)")
    parser.add_argument("--sdram-device", default="MT41K64M16", help="ECP5 device (default=MT41K64M16)")
    args = parser.parse_args()

    soc = BaseSoC(toolchain=args.toolchain,
                  revision=args.revision,
                  device=args.device,
                  sdram_device=args.sdram_device,
                  sys_clk_freq=int(float(args.sys_clk_freq)),
                  **soc_sdram_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder_kargs = trellis_argdict(args) if args.toolchain == "trellis" else {}
    builder.build(**builder_kargs, run=args.build)

if __name__ == "__main__":
    main()
