#!/usr/bin/env python3

# This file is Copyright (c) 2019 Sean Cross <sean@xobs.io>
# This file is Copyright (c) 2018 David Shah <dave@ds0.me>
# License: BSD

import argparse

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.soc.cores import up5kspram
from litex.soc.integration import SoCCore
from litex.soc.integration.builder import Builder, builder_argdict, builder_args
from litex.soc.integration.soc_core import soc_core_argdict, soc_core_args

from valentyusb.usbcore import io as usbio
from valentyusb.usbcore.cpu import dummyusb, epfifo

import os, shutil, subprocess

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform):
        clk48_raw = platform.request("clk48")
        clk12 = Signal()

        reset_delay = Signal(12, reset=4095)
        self.clock_domains.cd_por = ClockDomain()
        self.reset = Signal()

        self.clock_domains.cd_sys = ClockDomain()
        self.clock_domains.cd_usb_12 = ClockDomain()
        self.clock_domains.cd_usb_48 = ClockDomain()

        platform.add_period_constraint(self.cd_usb_48.clk, 1e9/48e6)
        platform.add_period_constraint(self.cd_sys.clk, 1e9/12e6)
        platform.add_period_constraint(self.cd_usb_12.clk, 1e9/12e6)
        platform.add_period_constraint(clk48_raw, 1e9/48e6)

        # POR reset logic- POR generated from sys clk, POR logic feeds sys clk
        # reset.
        self.comb += [
            self.cd_por.clk.eq(self.cd_sys.clk),
            self.cd_sys.rst.eq(reset_delay != 0),
            self.cd_usb_12.rst.eq(reset_delay != 0),
        ]

        # POR reset logic- POR generated from sys clk, POR logic feeds sys clk
        # reset.
        self.comb += [
            self.cd_usb_48.rst.eq(reset_delay != 0),
        ]

        self.comb += self.cd_usb_48.clk.eq(clk48_raw)

        self.specials += Instance(
            "SB_PLL40_CORE",
            # Parameters
            p_DIVR = 0,
            p_DIVF = 15,
            p_DIVQ = 5,
            p_FILTER_RANGE = 1,
            p_FEEDBACK_PATH = "SIMPLE",
            p_DELAY_ADJUSTMENT_MODE_FEEDBACK = "FIXED",
            p_FDA_FEEDBACK = 15,
            p_DELAY_ADJUSTMENT_MODE_RELATIVE = "FIXED",
            p_FDA_RELATIVE = 0,
            p_SHIFTREG_DIV_MODE = 1,
            p_PLLOUT_SELECT = "GENCLK_HALF",
            p_ENABLE_ICEGATE = 0,
            # IO
            i_REFERENCECLK = clk48_raw,
            o_PLLOUTCORE = clk12,
            # o_PLLOUTGLOBAL = clk12,
            #i_EXTFEEDBACK,
            #i_DYNAMICDELAY,
            #o_LOCK,
            i_BYPASS = 0,
            i_RESETB = 1,
            #i_LATCHINPUTVALUE,
            #o_SDO,
            #i_SDI,
        )

        self.comb += self.cd_sys.clk.eq(clk12)
        self.comb += self.cd_usb_12.clk.eq(clk12)

        self.sync.por += \
            If(reset_delay != 0,
                reset_delay.eq(reset_delay - 1)
            )
        self.specials += AsyncResetSynchronizer(self.cd_por, self.reset)


# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    """A SoC on Fomu, optionally with a softcore CPU"""

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
        "csr":      0x60000000,  # (default shadow @0xe0000000)
    }

    interrupt_map = {
        "usb": 3,
    }
    interrupt_map.update(SoCCore.interrupt_map)

    def __init__(self, board,
        pnr_placer=None, pnr_seed=0, usb_core="dummyusb", usb_bridge=False,
        **kwargs):
        """Create a basic SoC for Fomu.

        Create a basic SoC for Fomu, including a 48 MHz and 12 MHz clock
        domain called `usb_48` and `usb_12`.  The `sys` frequency will
        run at 12 MHz.

        The USB core will optionally have a bridge to the Wishbone bus.

        Args:
            board (str): Which Fomu board to build for: pvt, evt, or hacker
            pnr_placer (str): Which placer to use in nextpnr
            pnr_seed (int): Which seed to use in nextpnr
            usb_core (str): The name of the USB core to use, if any: dummyusb, epfifo
            usb_bridge (bool): Whether to include a USB-to-Wishbone bridge
        Raises:
            ValueError: If either the `usb_core` or `board` are unrecognized
        Returns:
            Newly-constructed SoC
        """
        if board == "pvt":
            from litex_boards.partner.platforms.fomu_pvt import Platform
        elif board == "hacker":
            from litex_boards.partner.platforms.fomu_hacker import Platform
        elif board == "evt":
            from litex_boards.partner.platforms.fomu_evt import Platform
        else:
            raise ValueError("unrecognized fomu board: {}".format(board))
        platform = Platform()

        clk_freq = int(12e6)

        SoCCore.__init__(self, platform, clk_freq,
                cpu_type=None,
                cpu_variant=None,
                integrated_sram_size=0,
                with_uart=False,
                with_ctrl=False,
                **kwargs)

        self.submodules.crg = _CRG(platform)

        # UP5K has single port RAM, which is a dedicated 128 kilobyte block.
        # Use this as CPU RAM.
        spram_size = 128*1024
        self.submodules.spram = up5kspram.Up5kSPRAM(size=spram_size)
        self.register_mem("sram", 0x10000000, self.spram.bus, spram_size)

        if usb_core is not None:
            # Add USB pads.  We use DummyUsb, which simply enumerates as a USB
            # device.  Then all interaction is done via the wishbone bridge.
            usb_pads = platform.request("usb")
            usb_iobuf = usbio.IoBuf(usb_pads.d_p, usb_pads.d_n, usb_pads.pullup)
            if usb_core == "dummyusb":
                self.submodules.usb = dummyusb.DummyUsb(usb_iobuf, debug=usb_bridge)
            elif usb_core == "epfifo":
                self.submodules.usb = epfifo.PerEndpointFifo(usb_iobuf, debug=usb_bridge)
            else:
                raise ValueError("unrecognized usb_core: {}".args(usb_core))
            if usb_bridge:
                self.add_wb_master(self.usb.debug_bridge.wishbone)

        # Add "-relut -dffe_min_ce_use 4" to the synth_ice40 command.
        # "-reult" adds an additional LUT pass to pack more stuff in, and
        # "-dffe_min_ce_use 4" flag prevents Yosys from generating a
        # Clock Enable signal for a LUT that has fewer than 4 flip-flops.
        # This increases density, and lets us use the FPGA more efficiently.
        platform.toolchain.nextpnr_yosys_template[2] += " -relut -dffe_min_ce_use 4"

        # Allow us to set the nextpnr seed, because some values don't meet timing.
        platform.toolchain.nextpnr_build_template[1] += " --seed " + str(pnr_seed)

        # Different placers can improve packing efficiency, however not all placers
        # are enabled on all builds of nextpnr-ice40.  Let the user override which
        # placer they want to use.
        if pnr_placer is not None:
            platform.toolchain.nextpnr_build_template[1] += " --placer {}".format(pnr_placer)


# Build --------------------------------------------------------------------------------------------

def add_dfu_suffix(fn):
    fn_base, _ext = os.path.splitext(fn)
    fn_dfu = fn_base + '.dfu'
    shutil.copyfile(fn, fn_dfu)
    subprocess.check_call(['dfu-suffix', '--pid', '1209', '--vid', '5bf0', '--add', fn_dfu])

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on Fomu")
    parser.add_argument(
        "--board", choices=["evt", "pvt", "hacker"], required=True,
        help="build for a particular hardware board"
    )
    parser.add_argument(
        "--seed", default=0, help="seed to use in nextpnr"
    )
    parser.add_argument(
        "--placer", default="heap", choices=["sa", "heap"], help="which placer to use in nextpnr"
    )
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(board=args.board, pnr_placer=args.placer, pnr_seed=args.seed,
                debug=True, **soc_core_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder.build()

if __name__ == "__main__":
    main()
