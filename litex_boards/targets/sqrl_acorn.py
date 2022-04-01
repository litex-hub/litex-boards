#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# Build/Use ----------------------------------------------------------------------------------------
# Build/Load bitstream:
# ./sqrl_acorn.py --uart-name=crossover --with-pcie --build --driver --load (or --flash)
#
#.Build the kernel and load it:
# cd build/<platform>/driver/kernel
# make
# sudo ./init.sh
#
# Test userspace utilities:
# cd build/<platform>/driver/user
# make
# ./litepcie_util info
# ./litepcie_util scratch_test
# ./litepcie_util dma_test
# ./litepcie_util uart_test

import os

from migen import *

from litex_boards.platforms import acorn

from litex.soc.interconnect.csr import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

from litex.soc.cores.clock import *
from litex.soc.cores.led import LedChaser

from litedram.modules import MT41K512M16
from litedram.phy import s7ddrphy

from litepcie.phy.s7pciephy import S7PCIEPHY
from litepcie.software import generate_litepcie_software

# CRG ----------------------------------------------------------------------------------------------

class CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_sys       = ClockDomain()
        self.clock_domains.cd_sys4x     = ClockDomain()
        self.clock_domains.cd_sys4x_dqs = ClockDomain()
        self.clock_domains.cd_idelay    = ClockDomain()

        # Clk/Rst
        clk200 = platform.request("clk200")

        # PLL
        self.submodules.pll = pll = S7PLL()
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk200, 200e6)
        pll.create_clkout(self.cd_sys,       sys_clk_freq)
        pll.create_clkout(self.cd_sys4x,     4*sys_clk_freq)
        pll.create_clkout(self.cd_sys4x_dqs, 4*sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_idelay,    200e6)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        self.submodules.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

# BaseSoC -----------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, variant="cle-215+", sys_clk_freq=int(100e6), with_led_chaser=True,
                 with_pcie=False, with_sata=False, **kwargs):
        platform = acorn.Platform(variant=variant)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident = "LiteX SoC on Acorn CLE-101/215(+)",
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = CRG(platform, sys_clk_freq)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.submodules.ddrphy = s7ddrphy.A7DDRPHY(platform.request("ddram"),
                memtype          = "DDR3",
                nphases          = 4,
                sys_clk_freq     = sys_clk_freq,
                iodelay_clk_freq = 200e6)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT41K512M16(sys_clk_freq, "1:4"),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # PCIe -------------------------------------------------------------------------------------
        if with_pcie:
            self.submodules.pcie_phy = S7PCIEPHY(platform, platform.request("pcie_x4"),
                data_width = 128,
                bar0_size  = 0x20000)
            self.add_pcie(phy=self.pcie_phy, ndmas=1)
            # FIXME: Apply it to all targets (integrate it in LitePCIe?).
            platform.add_period_constraint(self.crg.cd_sys.clk, 1e9/sys_clk_freq)
            platform.toolchain.pre_placement_commands.add("set_clock_groups -group [get_clocks {sys_clk}] -group [get_clocks userclk2] -asynchronous", sys_clk=self.crg.cd_sys.clk)
            platform.toolchain.pre_placement_commands.add("set_clock_groups -group [get_clocks {sys_clk}] -group [get_clocks clk_125mhz] -asynchronous", sys_clk=self.crg.cd_sys.clk)
            platform.toolchain.pre_placement_commands.add("set_clock_groups -group [get_clocks {sys_clk}] -group [get_clocks clk_250mhz] -asynchronous", sys_clk=self.crg.cd_sys.clk)
            platform.toolchain.pre_placement_commands.add("set_clock_groups -group [get_clocks clk_125mhz] -group [get_clocks clk_250mhz] -asynchronous")

            # ICAP (For FPGA reload over PCIe).
            from litex.soc.cores.icap import ICAP
            self.submodules.icap = ICAP()
            self.icap.add_reload()
            self.icap.add_timing_constraints(platform, sys_clk_freq, self.crg.cd_sys.clk)

            # Flash (For SPIFlash update over PCIe).
            from litex.soc.cores.gpio import GPIOOut
            from litex.soc.cores.spi_flash import S7SPIFlash
            self.submodules.flash_cs_n = GPIOOut(platform.request("flash_cs_n"))
            self.submodules.flash      = S7SPIFlash(platform.request("flash"), sys_clk_freq, 25e6)

        # SATA -------------------------------------------------------------------------------------
        if with_sata:
            from litex.build.generic_platform import Subsignal, Pins
            from litesata.phy import LiteSATAPHY

            # IOs
            _sata_io = [
                 # PCIe 2 SATA Custom Adapter (With PCIe Riser / SATA cable mod).
                ("pcie2sata", 0,
                    Subsignal("tx_p",  Pins("B6")),
                    Subsignal("tx_n",  Pins("A6")),
                    Subsignal("rx_p",  Pins("B10")),
                    Subsignal("rx_n",  Pins("A10")),
                ),
            ]
            platform.add_extension(_sata_io)

            # RefClk, Generate 150MHz from PLL.
            self.clock_domains.cd_sata_refclk = ClockDomain()
            self.crg.pll.create_clkout(self.cd_sata_refclk, 150e6)
            sata_refclk = ClockSignal("sata_refclk")
            platform.add_platform_command("set_property SEVERITY {{Warning}} [get_drc_checks REQP-49]")

            # PHY
            self.submodules.sata_phy = LiteSATAPHY(platform.device,
                refclk     = sata_refclk,
                pads       = platform.request("pcie2sata"),
                gen        = "gen1",
                clk_freq   = sys_clk_freq,
                data_width = 16)

            # Core
            self.add_sata(phy=self.sata_phy, mode="read+write")

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on Acorn CLE-101/215(+)")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",           action="store_true", help="Build bitstream.")
    target_group.add_argument("--load",            action="store_true", help="Load bitstream.")
    target_group.add_argument("--flash",           action="store_true", help="Flash bitstream.")
    target_group.add_argument("--variant",         default="cle-215+",  help="Board variant (cle-215+, cle-215 or cle-101).")
    target_group.add_argument("--sys-clk-freq",    default=100e6,       help="System clock frequency.")
    pcieopts = target_group.add_mutually_exclusive_group()
    pcieopts.add_argument("--with-pcie",     action="store_true", help="Enable PCIe support.")
    target_group.add_argument("--driver",          action="store_true", help="Generate PCIe driver.")
    target_group.add_argument("--with-spi-sdcard", action="store_true", help="Enable SPI-mode SDCard support (requires SDCard adapter on P2).")
    pcieopts.add_argument("--with-sata",     action="store_true", help="Enable SATA support (over PCIe2SATA).")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        variant      = args.variant,
        sys_clk_freq = int(float(args.sys_clk_freq)),
        with_pcie    = args.with_pcie,
        with_sata    = args.with_sata,
        **soc_core_argdict(args)
    )
    if args.with_spi_sdcard:
        soc.add_spi_sdcard()

    builder  = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.driver:
        generate_litepcie_software(soc, os.path.join(builder.output_dir, "driver"))

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.flash(0, builder.get_bitstream_filename(mode="flash"))

if __name__ == "__main__":
    main()
