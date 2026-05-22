#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019 Antti Lukats <antti.lukats@gmail.com>
# Copyright (c) 2019 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import *

from litex_boards.platforms import trenz_mf001_intel
from litex_boards.targets.microfpga.common import MFIOBasic, OnChipOscillator

from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform):
        self.rst    = Signal()
        self.cd_por = ClockDomain(reset_less=True)
        self.cd_sys = ClockDomain()

        # # #

        self.osc = osc = OnChipOscillator(device=platform.device)

        por_done = Signal()
        self.sync.por += por_done.eq(1)
        self.comb += [
            self.cd_por.clk.eq(osc.clkout),
            self.cd_sys.clk.eq(osc.clkout),
            self.cd_sys.rst.eq(~por_done | self.rst),
        ]

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=116e6,
        platform_id = 0,
        with_mfio   = True,
        **kwargs):
        platform = trenz_mf001_intel.Platform(platform_id)

        kwargs.setdefault("integrated_rom_size",      platform.rom_size*1024)
        kwargs.setdefault("integrated_main_ram_size", platform.ram_size*1024)

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident = f"LiteX SoC on MicroFPGA Intel ({platform.device})",
            **kwargs)

        # MFIO -------------------------------------------------------------------------------------
        if with_mfio:
            pads = platform.request("mfio")
            self.mfio = MFIOBasic(pads)
            self.bus.add_slave("mfio", slave=self.mfio.bus, region=SoCRegion(
                origin = 0x20000000,
                size   = 4*1024,
                mode   = "rw",
            ))
            self.add_constant("MFIO_PINS_COUNT", len(pads))

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=trenz_mf001_intel.Platform, description="LiteX SoC on MicroFPGA Intel.")
    parser.add_target_argument("--sys-clk-freq", default=116e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--platform-id",  default=0,     type=int,   help="Platform variant index.")
    parser.add_target_argument("--no-mfio",      action="store_true",      help="Disable MFIO Wishbone bridge.")
    parser.set_defaults(uart_name="jtag_uart")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq = args.sys_clk_freq,
        platform_id  = args.platform_id,
        with_mfio    = not args.no_mfio,
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
