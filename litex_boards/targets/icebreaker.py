#!/usr/bin/env python3

# This file is Copyright (c) 2019 Sean Cross <sean@xobs.io>
# This file is Copyright (c) 2018 David Shah <dave@ds0.me>
# This file is Copyright (c) 2020 Piotr Esden-Tempski <piotr@esden.net>
# License: BSD

# This target was originally based on the Fomu target.

import argparse

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.soc.cores import up5kspram, spi_flash
from litex.soc.integration.soc_core import SoCCore
from litex.soc.integration.builder import Builder, builder_argdict, builder_args
from litex.soc.integration.soc_core import soc_core_argdict, soc_core_args
from litex.soc.integration.doc import AutoDoc

from litex_boards.partner.platforms.icebreaker import Platform

from litex.soc.cores.uart import UARTWishboneBridge
import litex.soc.cores.cpu

import os, shutil, subprocess

from litex.soc.interconnect import wishbone
class JumpToAddressROM(wishbone.SRAM):
    def __init__(self, size, addr):
        data = [
            0x00000537 | ((addr & 0xfffff000) << 0 ), # lui   a0,%hi(addr)
            0x00052503 | ((addr & 0x00000fff) << 20), # lw    a0,%lo(addr)(a0)
            0x000500e7,                               # jalr  a0
        ]
        wishbone.SRAM.__init__(self, size, read_only=True, init=data)

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module, AutoDoc):
    """Icebreaker Clock Resource Generator

    The following clock domains are available on this design:

    +---------+------------+---------------------------------+
    | Name    | Frequency  | Description                     |
    +=========+============+=================================+
    +---------+------------+---------------------------------+
    | clk_12  | 12 MHz     | Main control logic              |
    +---------+------------+---------------------------------+
    | sys     | 12 MHz     | System CPU and wishbone bus     |
    +---------+------------+---------------------------------+
    """
    def __init__(self, platform):
        clk12 = platform.request("clk12")

        reset_delay = Signal(12, reset=4095)
        self.clock_domains.cd_por = ClockDomain()
        self.reset = Signal()

        self.clock_domains.cd_sys = ClockDomain()
        self.clock_domains.cd_clk_12 = ClockDomain()

        platform.add_period_constraint(self.cd_sys.clk, 1e9/12e6)
        platform.add_period_constraint(self.cd_clk_12.clk, 1e9/12e6)

        # POR reset logic- POR generated from sys clk, POR logic feeds sys clk
        # reset.
        self.comb += [
            self.cd_por.clk.eq(self.cd_sys.clk),
            self.cd_sys.rst.eq(reset_delay != 0),
            self.cd_clk_12.rst.eq(reset_delay != 0),
        ]

        self.comb += self.cd_sys.clk.eq(clk12)
        self.comb += self.cd_clk_12.clk.eq(clk12)

        self.sync.por += \
            If(reset_delay != 0,
                reset_delay.eq(reset_delay - 1)
            )
        self.specials += AsyncResetSynchronizer(self.cd_por, self.reset)


# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    """A SoC on iCEBreaker, optionally with a softcore CPU"""

    # Statically-define the memory map, to prevent it from shifting across
    # various litex versions.
    SoCCore.mem_map = {
        "rom":              0x00000000,  # (default shadow @0x80000000)
        "sram":             0x10000000,  # (default shadow @0xa0000000)
        "spiflash":         0x20000000,  # (default shadow @0xa0000000)
        "csr":              0xe0000000,  # (default shadow @0x60000000)
        "vexriscv_debug":   0xf00f0000,
    }

    def __init__(self, pnr_placer="heap", pnr_seed=0, debug=True,
                 boot_vector = 0x2001a000,
                **kwargs):
        """Create a basic SoC for iCEBraker.

        Create a basic SoC for iCEBraker.  The `sys` frequency will run at 12 MHz.

        Args:
            pnr_placer (str): Which placer to use in nextpnr
            pnr_seed (int): Which seed to use in nextpnr
        Returns:
            Newly-constructed SoC
        """
        platform = Platform()

        if "cpu_type" not in kwargs:
            kwargs["cpu_type"] = None
            kwargs["cpu_variant"] = None

        clk_freq = int(12e6)

        # Force the SRAM size to 0, because we add our own SRAM with SPRAM
        kwargs["integrated_sram_size"] = 0
        kwargs["integrated_rom_size"] = 0

        if debug:
            kwargs["uart_name"] = "crossover"
            if kwargs["cpu_type"] == "vexriscv":
                kwargs["cpu_variant"] = kwargs["cpu_variant"] + "+debug"

        SoCCore.__init__(self, platform, clk_freq,
                         with_uart=True,
                         with_ctrl=True,
                         **kwargs)

        # If there is a VexRiscv CPU, add a fake ROM that simply tells the CPU
        # to jump to the given address.
        if hasattr(self, "cpu") and self.cpu.name == "vexriscv":
            self.add_memory_region("rom", 0, 16)
            self.submodules.rom = JumpToAddressROM(16, boot_vector)

        self.submodules.crg = _CRG(platform)

        # UP5K has single port RAM, which is a dedicated 128 kilobyte block.
        # Use this as CPU RAM.
        spram_size = 128 * 1024
        self.submodules.spram = up5kspram.Up5kSPRAM(size=spram_size)
        self.register_mem("sram", self.mem_map["sram"], self.spram.bus, spram_size)

        # The litex SPI module supports memory-mapped reads, as well as a bit-banged mode
        # for doing writes.
        spi_pads = platform.request("spiflash4x")
        self.submodules.lxspi = spi_flash.SpiFlashDualQuad(spi_pads, dummy=6, endianness="little")
        self.register_mem("spiflash", self.mem_map["spiflash"], self.lxspi.bus, size=16 * 1024 * 1024)
        self.add_csr("lxspi")

        # In debug mode, add a UART bridge.  This takes over from the normal UART bridge,
        # however you can use the "crossover" UART to communicate with this over the bridge.
        if debug:
            self.submodules.uart_bridge = UARTWishboneBridge(platform.request("serial"), clk_freq, baudrate=115200)
            self.add_wb_master(self.uart_bridge.wishbone)
            if hasattr(self, "cpu") and self.cpu.name == "vexriscv":
                self.register_mem("vexriscv_debug", 0xf00f0000, self.cpu.debug_bus, 0x100)

        # Override default LiteX's yosys/build templates
        assert hasattr(platform.toolchain, "yosys_template")
        assert hasattr(platform.toolchain, "build_template")
        platform.toolchain.yosys_template = [
            "{read_files}",
            "attrmap -tocase keep -imap keep=\"true\" keep=1 -imap keep=\"false\" keep=0 -remove keep=0",
            "synth_ice40 -json {build_name}.json -top {build_name}",
        ]
        platform.toolchain.build_template = [
            "yosys -q -l {build_name}.rpt {build_name}.ys",
            "nextpnr-ice40 --json {build_name}.json --pcf {build_name}.pcf --asc {build_name}.txt \
            --pre-pack {build_name}_pre_pack.py --{architecture} --package {package}",
            "icepack {build_name}.txt {build_name}.bin"
        ]

        # Add "-relut -dffe_min_ce_use 4" to the synth_ice40 command.
        # The "-reult" adds an additional LUT pass to pack more stuff in,
        # and the "-dffe_min_ce_use 4" flag prevents Yosys from generating a
        # Clock Enable signal for a LUT that has fewer than 4 flip-flops.
        # This increases density, and lets us use the FPGA more efficiently.
        platform.toolchain.yosys_template[2] += " -relut -abc2 -dffe_min_ce_use 4 -relut"
        #if use_dsp:
        #    platform.toolchain.yosys_template[2] += " -dsp"

        # Disable final deep-sleep power down so firmware words are loaded
        # onto softcore's address bus.
        platform.toolchain.build_template[2] = "icepack -s {build_name}.txt {build_name}.bin"

        # Allow us to set the nextpnr seed
        platform.toolchain.build_template[1] += " --seed " + str(pnr_seed)

        if pnr_placer is not None:
            platform.toolchain.build_template[1] += " --placer {}".format(pnr_placer)


# Build --------------------------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on iCEBreaker")
    parser.add_argument(
        "--seed", default=0, help="seed to use in nextpnr"
    )
    parser.add_argument(
        "--placer", default="heap", choices=["sa", "heap"], help="which placer to use in nextpnr"
    )
    parser.add_argument(
        "--cpu", action="store_true", help="Add a CPU to the build"
    )
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    kwargs = builder_argdict(args)

    if args.cpu:
        kwargs["cpu_type"] = "vexriscv"
        kwargs["cpu_variant"] = "min"

    soc = BaseSoC(pnr_placer=args.placer, pnr_seed=args.seed,
                  debug=True, **kwargs)

    kwargs = builder_argdict(args)

    # Don't build software -- we don't include it since we just jump
    # to SPI flash.
    kwargs["compile_software"] = False
    builder = Builder(soc, **kwargs)
    builder.build()


if __name__ == "__main__":
    main()
