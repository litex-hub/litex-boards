#!/usr/bin/env python3

# This file is Copyright (c) 2018-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# This file is Copyright (c) 2018-2019 David Shah <dave@ds0.me>
# License: BSD

import os
import argparse

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex_boards.platforms import crosslink_nx_eval

from litex.soc.cores.lifcllram import LIFCLLRAM
from litex.soc.cores.spi_flash import SpiFlash
from litex.build.io import CRG
from litex.build.generic_platform import *

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

kB = 1024
mB = 1024*kB


# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.clock_domains.cd_sys = ClockDomain()
        self.clock_domains.cd_por = ClockDomain()

        # TODO: replace with PLL
        # Clocking
        self.submodules.sys_clk = sys_osc = CrossLinkNXOSCA()
        sys_osc.create_clkout(self.cd_sys, sys_clk_freq)
        platform.add_period_constraint(self.cd_sys.clk, 1e9/sys_clk_freq)
        rst_n = platform.request("gsrn")

        # Power On Reset
        por_cycles  = 4096
        por_counter = Signal(log2_int(por_cycles), reset=por_cycles-1)
        self.comb += self.cd_por.clk.eq(self.cd_sys.clk)
        self.sync.por += If(por_counter != 0, por_counter.eq(por_counter - 1))
        self.specials += AsyncResetSynchronizer(self.cd_por, ~rst_n)
        self.specials += AsyncResetSynchronizer(self.cd_sys, (por_counter != 0))


# TODO: remove this
class ClockOut(Module):
    """Outputs clock/1000 for easy measurement of clock frequency"""
    def __init__(self, pin=None):
        counter = Signal(9)
        self.sync += [
            counter.eq(counter + 1),
            If(counter == 499,
                pin.eq(~pin),
                counter.eq(0)
            ),
        ]

_ckout = [
        ("clkout", 0, Pins("PMOD2:0"), IOStandard("LVCMOS33")),
]

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    SoCCore.mem_map = {
        "rom":              0x00000000,
        "sram":             0x10000000,
        "spiflash":         0x20000000,
        "main_ram":         0x40000000,
        "csr":              0xf0000000,
    }
    def __init__(self, sys_clk_freq, **kwargs):

        platform = crosslink_nx_eval.Platform()

        # Make serial_pmods available 
        platform.add_extension(crosslink_nx_eval.serial_pmods)

        # SoCCore -----------------------------------------_----------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident          = "LiteX SoC on Crosslink-NX",
            ident_version  = True,
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # Debugging: TODO Remove
        self.add_uartbone(name="serial_pmod1", baudrate=115200)
        platform.add_extension(_ckout)
        self.submodules.clockout = ClockOut(platform.request("clkout"))

        if hasattr(self, "cpu") and self.cpu.name == "vexriscv":
            self.register_mem("vexriscv_debug", 0xf00f0000, self.cpu.debug_bus, 0x100)

        # 128KB LRAM (used as SRAM) ---------------------------------------------------------------
        size = 128*kB
        self.submodules.spram = LIFCLLRAM(32, size)
        self.register_mem("main_ram", self.mem_map["main_ram"], self.spram.bus, size)

        # SPI Flash --------------------------------------------------------------------------------
        self.submodules.spiflash = SpiFlash(platform.request("spiflash"), dummy=8, endianness="little", div=4)
        self.register_mem("spiflash", self.mem_map["spiflash"], self.spiflash.bus, size=16*mB)
        self.add_csr("spiflash")

        # Leds -------------------------------------------------------------------------------------
        self.submodules.leds = LedChaser(
            pads         = Cat(*[platform.request("user_led", i) for i in range(14)]),
            sys_clk_freq = sys_clk_freq)
        self.add_csr("leds")


# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on Crosslink-NX Eval Board")
    parser.add_argument("--build", action="store_true", help="Build bitstream")
    parser.add_argument("--load",  action="store_true", help="Load bitstream")
    parser.add_argument("--sys-clk-freq",  default=75e6, help="System clock frequency (default=75MHz)")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(sys_clk_freq=int(float(args.sys_clk_freq)), **soc_core_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder_kargs = {}
    builder.build(**builder_kargs, run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".svf"))

if __name__ == "__main__":
    main()
