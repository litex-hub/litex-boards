#!/usr/bin/env python3

# This file is Copyright (c) 2020 Paul Sajna <sajattack@gmail.com>
# License: BSD

import os
import argparse

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.build.io import DDROutput

from litex_boards.platforms import de10nano

from litex.soc.cores.clock import CycloneVPLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc_sdram import *
from litex.soc.integration.builder import *

# de10nano specific
from litex.soc.cores.led import LedChaser

# de10nano 128MB sdram
from litedram.modules import SDRAMModule
from litedram.modules import _TechnologyTimings
from litedram.modules import _SpeedgradeTimings
from litedram.phy import GENSDRPHY

# de10nano buses
from litex.soc.interconnect.axi import *
from litex.soc.interconnect import wishbone

# VGA terminal
from litevideo.terminal.core import Terminal

# MiSTer I/O definitions

# Light up the top user leds on the mister i/o board
class MiSTerOutputs(Module):
    def __init__(self, pads):
        if hasattr(pads, 'led_power'):
            led_power_pin = Signal()
            self.comb += pads.led_power.eq(0)
        if hasattr(pads, 'led_user'):
            led_user_pin = Signal()
            self.comb += pads.led_user.eq(0)
        if hasattr(pads, 'led_hdd'):
            led_hdd_pin = Signal()
            self.comb += pads.led_hdd.eq(0)

        led_power_pin.eq(1)
        led_user_pin.eq(0)
        led_hdd_pin.eq(0)

# MiSTer 128MB SDRAM
class MiSTer128SDRAM(SDRAMModule):                                                                                          #4 x AS4C32M16 32MB=4*8192*512 (hopefully 128MB=4*32768*512 or 16*8192*512)
    memtype = "SDR"
    # geometry
    nbanks = 4
    nrows  = 16384
    ncols  = 1024
    # timings
    technology_timings = _TechnologyTimings(tREFI=64e6/8192, tWTR=(2, None), tCCD=(1, None), tRRD=None)
    speedgrade_timings = {"default": _SpeedgradeTimings(tRP=18, tRCD=18, tWR=12, tRFC=(None, 60), tFAW=None, tRAS=None)}

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq, with_sdram=False):
        self.clock_domains.cd_sys    = ClockDomain()
        self.clock_domains.cd_sys_ps = ClockDomain(reset_less=True)
        self.clock_domains.cd_vga    = ClockDomain(reset_less=True)
        # # #

        # Clk / Rst
        clk50 = platform.request("clk50")

        # PLL
        self.submodules.pll = pll = CycloneVPLL(speedgrade="-I7")
        pll.register_clkin(clk50, 50e6)
        pll.create_clkout(self.cd_sys,    sys_clk_freq)
        pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_vga,    25e6)
        
        # SDRAM clock
        if with_sdram:
            self.specials += DDROutput(1, 0, platform.request("sdram_clock"), ClockSignal("sys_ps"))

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(50e6), **kwargs):
        platform = de10nano.Platform()

        # SoCCore ---------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, clk_freq=sys_clk_freq, **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # Leds -------------------------------------------------------------------------------------
        self.submodules.leds = LedChaser(
            pads         = Cat(*[platform.request("user_led", i) for i in range(8)]),
            sys_clk_freq = sys_clk_freq)
        self.add_csr("leds")

# MiSTerSDRAMSoC -----------------------------------------------------------------------------------

class MiSTerSDRAMSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(50e6), **kwargs):
        platform = de10nano.Platform()

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, clk_freq=sys_clk_freq, **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq, with_sdram=True)

        # Leds -------------------------------------------------------------------------------------
        self.submodules.leds = LedChaser(
            pads         = Cat(*[platform.request("user_led", i) for i in range(8)]),
            sys_clk_freq = sys_clk_freq)
        self.add_csr("leds")

        # mister user leds
        self.submodules.mister_outputs = mister_outputs = MiSTerOutputs(platform.request("mister_outputs",0))
        self.add_csr("mister_outputs")
        
        # SDR SDRAM --------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.submodules.sdrphy = GENSDRPHY(platform.request("sdram"))
            self.add_sdram("sdram",
                phy                     = self.sdrphy,
                module                  = MiSTer128SDRAM(self.clk_freq, "1:1"),
                origin                  = self.mem_map["main_ram"],
                size                    = kwargs.get("max_sdram_size", 0x40000000),
                l2_cache_size           = kwargs.get("l2_size", 8192),
                l2_cache_min_data_width = kwargs.get("min_l2_data_width", 128),
                l2_cache_reverse        = True
            )

        # VGA terminal
        self.mem_map["terminal"] = 0x30000000
        self.submodules.terminal = terminal = Terminal()
        self.add_wb_slave(self.mem_map["terminal"], self.terminal.bus, 8896)
        self.add_memory_region("terminal", self.mem_map["terminal"], 8896, type="cached+linker")        

        # Connect VGA pins
        vga = platform.request("vga", 0)
        self.comb += [
            vga.vsync.eq(terminal.vsync),
            vga.hsync.eq(terminal.hsync),
            vga.red.eq(terminal.red[2:8]),
            vga.green.eq(terminal.green[2:8]),
            vga.blue.eq(terminal.blue[2:8])
        ]
        vga.en.eq(1)

#        self.add_csr("terminal")
     
         # AXI Bus
#        axibus = AXILiteInterface()

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on DE10 Nano")
    parser.add_argument("--build", action="store_true", help="Build bitstream")
    parser.add_argument("--load",  action="store_true", help="Load bitstream")
    builder_args(parser)
    soc_sdram_args(parser)
    parser.add_argument("--with-mister-sdram", action="store_true", help="Enable MiSTer SDRAM expansion board")
    args = parser.parse_args()
    if args.with_mister_sdram:
        soc = MiSTerSDRAMSoC(**soc_sdram_argdict(args))
    else:
        soc = BaseSoC(**soc_sdram_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".sof"))

if __name__ == "__main__":
    main()
