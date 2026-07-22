#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 David Corrigan <davidcorrigan714@gmail.com>
# Copyright (c) 2020 Alan Green <avg@google.com>
# Copyright (c) 2026 Myrtle Shah <gatecat@ds0.me>

# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from litex_boards.platforms import lattice_certus_nx_versa

from litex.soc.cores.ram import NXLRAM
from litex.soc.cores.clock import NXPLL
from litex.build.generic_platform import *

from litex.soc.cores.clock import *
from litex.soc.integration.soc import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser


from litedram.modules import MT41K64M16
from litedram.phy import NexusDDRPHY

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_ddr3=False):
        self.rst        = Signal()
        self.cd_init    = ClockDomain()
        self.cd_por     = ClockDomain()
        self.cd_sys     = ClockDomain()
        self.cd_sys2x   = ClockDomain()
        self.cd_sys2x_i = ClockDomain()

        # # #

        self.stop  = Signal()
        self.reset = Signal()

        # Clk / Rst
        clk100 = platform.request("clk100")
        rst_n  = platform.request("gsrn")

        clk100_clk_dis = platform.request("clk100_clk_dis")
        self.comb += clk100_clk_dis.eq(1)

        # Power on reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += self.cd_por.clk.eq(clk100)
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # PLL
        self.pll = pll = NXPLL(platform=platform, create_output_port_clocks=True)
        self.comb += pll.reset.eq(~por_done | ~rst_n | self.rst)
        pll.register_clkin(clk100, 100e6)
        if with_ddr3:
            pll.create_clkout(self.cd_sys2x_i, 2*sys_clk_freq)
            pll.create_clkout(self.cd_init, 25e6)
            self.specials += [
                Instance("ECLKSYNC",
                    p_STOP_EN = "ENABLE",
                    i_ECLKIN = self.cd_sys2x_i.clk,
                    i_STOP  = self.stop,
                    o_ECLKOUT = self.cd_sys2x.clk),
                Instance("ECLKDIV",
                    p_ECLK_DIV = "2",
                    i_SLIP     = 0,
                    i_ECLKIN   = self.cd_sys2x.clk,
                    i_DIVRST   = self.reset,
                    o_DIVOUT   = self.cd_sys.clk),
                AsyncResetSynchronizer(self.cd_init, ~pll.locked),
                AsyncResetSynchronizer(self.cd_sys, ~pll.locked | self.reset),
            ]
        else:
            pll.create_clkout(self.cd_sys, sys_clk_freq)
            self.specials += AsyncResetSynchronizer(self.cd_sys, ~pll.locked )


# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=75e6, toolchain="radiant",
        with_led_chaser = True,
        with_spi_flash  = False,
        with_ddr3       = False,
        **kwargs):
        platform = lattice_certus_nx_versa.Platform(toolchain=toolchain)

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, with_ddr3=with_ddr3)

        # SoCCore -----------------------------------------_----------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Certus-NX Versa Board", **kwargs)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if with_ddr3  and not self.integrated_main_ram_size:
            self.ddrphy = NexusDDRPHY(
                platform.request("ddram"),
                sys_clk_freq=sys_clk_freq)
            self.comb += self.crg.stop.eq(self.ddrphy.init.stop)
            self.comb += self.crg.reset.eq(self.ddrphy.init.reset)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT41K64M16(sys_clk_freq, "1:2"),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )
        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = Cat(*[platform.request("user_led", i) for i in range(8)]),
                sys_clk_freq = sys_clk_freq)

        # SPI Flash --------------------------------------------------------------------------------
        if with_spi_flash:
            from litespi.modules import MX25L12833F
            from litespi.opcodes import SpiNorFlashOpCodes as Codes
            self.add_spi_flash(mode="4x", clk_freq=100_000, module=MX25L12833F(Codes.READ_4_4_4), with_master=True)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=lattice_certus_nx_versa.Platform, description="LiteX SoC on Certus-NX Versa Board.")
    parser.add_target_argument("--sys-clk-freq",   default=75e6, type=float,   help="System clock frequency.")
    parser.add_target_argument("--programmer",     default="radiant",          help="Programmer (radiant or ecpprog or openocd).")
    parser.add_target_argument("--address",        default=0x0,                help="Flash address to program bitstream at.")
    parser.add_target_argument("--prog-target",    default="direct",           help="Programming Target (direct or flash).")
    parser.add_target_argument("--with-spi-flash", action="store_true",        help="Enable memory-mapped SPI flash.")
    parser.add_target_argument("--with-ddr3",      action="store_true",        help="Enable DDR3.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq   = args.sys_clk_freq,
        toolchain      = args.toolchain,
        with_spi_flash = args.with_spi_flash,
        with_ddr3      = args.with_ddr3,
        **parser.soc_argdict
    )
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer(args.prog_target, args.programmer)
        if args.programmer == "ecpprog" and args.prog_target == "flash":
            prog.flash(args.address, builder.get_bitstream_filename(mode="sram"))
        else:
            prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
