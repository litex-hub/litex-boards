#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# Build/Use:
# ./limesdr_mini_v2.py --csr-csv=csr.csv --build --load
# litex_server --jtag --jtag-config=openocd_limesdr_mini_v2.cfg
# litex_term crossover

from migen import *

from litex.gen import *

from litex_boards.platforms import limesdr_mini_v2

from litex.soc.cores.clock import *
from litex.soc.interconnect.csr import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.interconnect import stream

from litex.soc.cores.led import LedChaser
from litex.soc.cores.bitbang import I2CMaster
from litex.soc.cores.usb_fifo import FT245PHYSynchronous

from litescope import LiteScopeAnalyzer

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()
        self.cd_usb = ClockDomain()

        # # #

        # Clk.
        clk40 = platform.request("clk40")

        # PLL.
        self.pll = pll = ECP5PLL()
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk40, 40e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)

        # USB.
        self.comb += self.cd_usb.clk.eq(platform.request("usb_fifo_clk"))

# BoardInfo ----------------------------------------------------------------------------------------

class BoardInfo(LiteXModule, AutoCSR):
    def __init__(self, revision_pads):
        self.revision = CSRStorage(fields=[
            CSRField("hardware", size=4, description="Hardware Revision."),
            CSRField("bom",      size=4, description="Bill of Material Revision."),
        ])

        # # #

        self.comb += self.revision.fields.hardware.eq(revision_pads.hardware)
        self.comb += self.revision.fields.bom     .eq(revision_pads.bom)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=80e6, toolchain="trellis",
        with_usb_fifo   = True, with_usb_fifo_loopback=False,
        with_led_chaser = True,
        **kwargs):
        platform = limesdr_mini_v2.Platform(toolchain=toolchain)

        # SoCCore ----------------------------------------------------------------------------------
        kwargs["uart_name"] = "crossover"
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on LimeSDR-Mini-V2", **kwargs)

        # JTAGBone ---------------------------------------------------------------------------------
        self.add_jtagbone()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # Info -------------------------------------------------------------------------------------
        self.info = BoardInfo(platform.request("revision"))

        # I2C Bus ----------------------------------------------------------------------------------
        # - Temperature Sensor (LM72   @ 0x48).
        # - Eeprom             (M24128 @ 0x50) / Not populated.
        self.i2c = I2CMaster(platform.request("i2c"))

        # USB-FIFO ---------------------------------------------------------------------------------
        if with_usb_fifo:
            usb_pads = platform.request("usb_fifo")
            self.usb_phy = usb_phy = FT245PHYSynchronous(
                pads       = usb_pads,
                clk_freq   = sys_clk_freq,
                fifo_depth = 8,
                read_time  = 128,
                write_time = 128,
            )
            if with_usb_fifo_loopback:
                usb_loopback = stream.SyncFIFO([("data", 32)], 2048, buffered=True)
                self.submodules += usb_loopback
                self.comb += [
                    usb_phy.source.connect(usb_loopback.sink),
                    usb_loopback.source.connect(usb_phy.sink),
                ]
            else:
                self.comb += usb_phy.source.ready.eq(1) # Accept incoming stream to validate Host -> FPGA.

            analyzer_probes = usb_phy.get_litescope_probes()
            self.analyzer = LiteScopeAnalyzer(analyzer_probes,
                depth        = 512,
                clock_domain = "usb",
                samplerate   = sys_clk_freq,
                csr_csv      = "analyzer.csv"
            )

        # Debug -------------------------------------------------------------------------------
        egpio_pads = platform.request("egpio")
        self.comb += egpio_pads[0].eq(ClockSignal("sys"))
        self.comb += egpio_pads[1].eq(ClockSignal("usb"))

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            leds_g = Signal(4)
            leds_r = Signal(4)
            self.comb += platform.request_all("led_g_n").eq(~leds_g)
            self.comb += platform.request_all("led_r_n").eq(~leds_r)
            self.leds = LedChaser(Cat(leds_g, leds_r), sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=limesdr_mini_v2.Platform, description="LiteX SoC on LimeSDR-Mini-V2.")
    parser.add_target_argument("--sys-clk-freq", default=80e6, type=float, help="System clock frequency.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq = args.sys_clk_freq,
        toolchain    = args.toolchain,
        **parser.soc_argdict
    )
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram", ext=".svf")) # FIXME

if __name__ == "__main__":
    main()
