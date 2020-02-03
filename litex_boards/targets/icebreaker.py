#!/usr/bin/env python3

# This file is Copyright (c) 2019 Sean Cross <sean@xobs.io>
# This file is Copyright (c) 2018 David Shah <dave@ds0.me>
# This file is Copyright (c) 2020 Piotr Esden-Tempski <piotr@esden.net>
# License: BSD

# This target was originally based on the Fomu target.

import argparse

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.soc.cores import up5kspram
from litex.soc.integration.soc_core import SoCCore
from litex.soc.integration.builder import Builder, builder_argdict, builder_args
from litex.soc.integration.soc_core import soc_core_argdict, soc_core_args
from litex.soc.integration.doc import AutoDoc

from litex_boards.partner.platforms.icebreaker import Platform

import os, shutil, subprocess

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module, AutoDoc):
    """Fomu Clock Resource Generator

    Fomu is a USB device, which means it must have a 12 MHz clock.  Valentyusb
    oversamples the clock by 4x, which drives the requirement for a 48 MHz clock.
    The ICE40UP5k is a relatively low speed grade of FPGA that is incapable of
    running the entire design at 48 MHz, so the majority of the logic is placed
    in the 12 MHz domain while only critical USB logic is placed in the fast
    48 MHz domain.

    Fomu has a 48 MHz crystal on it, which provides the raw clock input.  This
    signal is fed through the ICE40 PLL in order to divide it down into a 12 MHz
    signal and keep the clocks within 1ns of phase.  Earlier designs used a simple
    flop, however this proved unreliable when the FPGA became very full.

    The following clock domains are available on this design:

    +---------+------------+---------------------------------+
    | Name    | Frequency  | Description                     |
    +=========+============+=================================+
    | usb_48  | 48 MHz     | Raw USB signals and pulse logic |
    +---------+------------+---------------------------------+
    | usb_12  | 12 MHz     | USB control logic               |
    +---------+------------+---------------------------------+
    | sys     | 12 MHz     | System CPU and wishbone bus     |
    +---------+------------+---------------------------------+
    """
    def __init__(self, platform):
        pass
        # clk12 = platform.request("clk12")
        # clk12 = Signal()

        # reset_delay = Signal(12, reset=4095)
        # self.clock_domains.cd_por = ClockDomain()
        # self.reset = Signal()

        # self.clock_domains.cd_sys = ClockDomain()
        # self.clock_domains.cd_usb_12 = ClockDomain()
        # self.clock_domains.cd_usb_48 = ClockDomain()

        # platform.add_period_constraint(self.cd_usb_48.clk, 1e9/48e6)
        # platform.add_period_constraint(self.cd_sys.clk, 1e9/12e6)
        # platform.add_period_constraint(self.cd_usb_12.clk, 1e9/12e6)
        # platform.add_period_constraint(clk48_raw, 1e9/48e6)

        # # POR reset logic- POR generated from sys clk, POR logic feeds sys clk
        # # reset.
        # self.comb += [
        #     self.cd_por.clk.eq(self.cd_sys.clk),
        #     self.cd_sys.rst.eq(reset_delay != 0),
        #     self.cd_usb_12.rst.eq(reset_delay != 0),
        # ]

        # # POR reset logic- POR generated from sys clk, POR logic feeds sys clk
        # # reset.
        # self.comb += [
        #     self.cd_usb_48.rst.eq(reset_delay != 0),
        # ]

        # self.comb += self.cd_usb_48.clk.eq(clk48_raw)

        # self.specials += Instance(
        #     "SB_PLL40_CORE",
        #     # Parameters
        #     p_DIVR = 0,
        #     p_DIVF = 15,
        #     p_DIVQ = 5,
        #     p_FILTER_RANGE = 1,
        #     p_FEEDBACK_PATH = "SIMPLE",
        #     p_DELAY_ADJUSTMENT_MODE_FEEDBACK = "FIXED",
        #     p_FDA_FEEDBACK = 15,
        #     p_DELAY_ADJUSTMENT_MODE_RELATIVE = "FIXED",
        #     p_FDA_RELATIVE = 0,
        #     p_SHIFTREG_DIV_MODE = 1,
        #     p_PLLOUT_SELECT = "GENCLK_HALF",
        #     p_ENABLE_ICEGATE = 0,
        #     # IO
        #     i_REFERENCECLK = clk48_raw,
        #     o_PLLOUTCORE = clk12,
        #     # o_PLLOUTGLOBAL = clk12,
        #     #i_EXTFEEDBACK,
        #     #i_DYNAMICDELAY,
        #     #o_LOCK,
        #     i_BYPASS = 0,
        #     i_RESETB = 1,
        #     #i_LATCHINPUTVALUE,
        #     #o_SDO,
        #     #i_SDI,
        # )

        # self.comb += self.cd_sys.clk.eq(clk12)
        # self.comb += self.cd_usb_12.clk.eq(clk12)

        # self.sync.por += \
        #     If(reset_delay != 0,
        #         reset_delay.eq(reset_delay - 1)
        #     )
        # self.specials += AsyncResetSynchronizer(self.cd_por, self.reset)


# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    """A SoC on iCEBreaker, optionally with a softcore CPU"""

    # Create a default CSR map to prevent values from getting reassigned.
    # This increases consistency across litex versions.
    SoCCore.csr_map = {
        "ctrl":           0,  # provided by default (optional)
        "crg":            1,  # user
        "uart_phy":       2,  # provided by default (optional)
        "uart":           3,  # provided by default (optional)
        "identifier_mem": 4,  # provided by default (optional)
        "timer0":         5,  # provided by default (optional)
        "cpu_or_bridge":  8,
        "usb":            9,
        "picorvspi":      10,
        "touch":          11,
        "reboot":         12,
        "rgb":            13,
        "version":        14,
    }

    # Statically-define the memory map, to prevent it from shifting across
    # various litex versions.
    SoCCore.mem_map = {
        "rom":      0x00000000,  # (default shadow @0x80000000)
        "sram":     0x10000000,  # (default shadow @0xa0000000)
        "spiflash": 0x20000000,  # (default shadow @0xa0000000)
        "main_ram": 0x40000000,  # (default shadow @0xc0000000)
        "csr":      0xe0000000,  # (default shadow @0x60000000)
    }

    def __init__(self,
                 pnr_placer="heap", pnr_seed=0, usb_core="dummyusb", usb_bridge=False,
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

        kwargs["integrated_sram_size"] = 0
        SoCCore.__init__(self, platform, clk_freq,
                         with_uart=True,
                         with_ctrl=True,
                         **kwargs)

        self.submodules.crg = _CRG(platform)

        # UP5K has single port RAM, which is a dedicated 128 kilobyte block.
        # Use this as CPU RAM.
        spram_size = 128 * 1024
        self.submodules.spram = up5kspram.Up5kSPRAM(size=spram_size)
        self.register_mem("sram", self.mem_map["sram"], self.spram.bus, spram_size)

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

def add_dfu_suffix(fn):
    fn_base, _ext = os.path.splitext(fn)
    fn_dfu = fn_base + '.dfu'
    shutil.copyfile(fn, fn_dfu)
    subprocess.check_call(['dfu-suffix', '--pid', '1209', '--vid', '5bf0', '--add', fn_dfu])


def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on iCEBreaker")
    parser.add_argument(
        "--seed", default=0, help="seed to use in nextpnr"
    )
    parser.add_argument(
        "--placer", default="heap", choices=["sa", "heap"], help="which placer to use in nextpnr"
    )
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(pnr_placer=args.placer, pnr_seed=args.seed,
                  debug=True, **soc_core_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder.build()


if __name__ == "__main__":
    main()
