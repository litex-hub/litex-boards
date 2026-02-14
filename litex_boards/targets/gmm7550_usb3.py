#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 Anton Kuzmin <ak@gmm7550.dev>
#
# based on litex_boards/targets/colognechip_gatemate_evb.py
# Copyright (c) 2023 Gwenhael Goavec-merou<gwenhael.goavec-merou@trabucayre.com>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import *

from litex_boards.platforms import gmm7550

from litex.build.io import CRG

from litex.soc.cores.clock.colognechip import GateMatePLL

from litex.soc.interconnect import wishbone

from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.integration.soc import SoCRegion

from litex.build.generic_platform import Pins, Subsignal

from litex.soc.cores.led import LedChaser

# USB 3 Adapter board IOs -------------------------------------------------------

# P4/J4 (South IO)
p4 = [
    # LEDs (green)
    ("user_led_n", 0, Pins("P4:5" )), # D10
    ("user_led_n", 1, Pins("P4:9" )), # D9
    ("user_led_n", 2, Pins("P4:6" )), # D8
    ("user_led_n", 3, Pins("P4:10")), # D7

    # Buttons
    ("btn_n", 0, Pins("P4:3")), # SW2, A
    ("btn_n", 1, Pins("P4:4")), # SW3, B

    # USB-C Power Delivery Controller (OnSemi FUSB303B)
    ("pd", 0,
     Subsignal("en_n", Pins("P4:15")),
     Subsignal("scl",  Pins("P4:11")),
     Subsignal("sda",  Pins("P4:12")),
     Subsignal("alert_n",  Pins("P4:16")),
     # Power Delivery Switch control
     Subsignal("pd_src_en", Pins("P4:21")),
     Subsignal("pd_disc",   Pins("P4:22")),
     ),

    # USB 1.1 (STmicro STUSB303E transceiver)
    ("usb1", 0,
     Subsignal("vp",     Pins("P4:50")),
     Subsignal("vm",     Pins("P4:52")),
     Subsignal("rcv",    Pins("P4:51")),
     Subsignal("busdet", Pins("P4:55")),
     Subsignal("oe_n",   Pins("P4:57")),
     Subsignal("con",    Pins("P4:56")),
     Subsignal("sus",    Pins("P4:58")),
     ),

    # USB 2.0 (ULPI, Microchip USB3340 PHY)
    ("ulpi", 0,
     Subsignal("clk",   Pins("P4:23")), # CLK 1, 60 MHz
     Subsignal("stp",   Pins("P4:28")),
     Subsignal("dir",   Pins("P4:30")),
     Subsignal("nxt",   Pins("P4:37")),
     Subsignal("rst_n", Pins("P4:24")),
     Subsignal("data",  Pins("P4:39", # 0
                             "P4:43", # 1
                             "P4:45", # 2
                             "P4:49", # 3
                             "P4:38", # 4
                             "P4:40", # 5
                             "P4:44", # 6
                             "P4:46", # 7
                             )),
     ),
]

# Clock/Reset Generator ---------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        usr_rst_n   = Signal()
        btn_rst_n   = Signal()
        self.cd_sys = ClockDomain()

        # Reference Clock
        ref_clk = platform.request(platform.default_clk_name)

        # User Reset (button B)
        btn_rst_n = platform.request("btn_n", 1)

        self.specials += Instance("CC_USR_RSTN", o_USR_RSTN = usr_rst_n)

        # PLL
        self.pll = pll = GateMatePLL(perf_mode="speed")
        self.comb += pll.reset.eq(~usr_rst_n | ~btn_rst_n)

        pll.register_clkin(ref_clk, 1e9/platform.default_clk_period)
        pll.create_clkout(self.cd_sys, sys_clk_freq)

        platform.add_period_constraint(self.cd_sys.clk, 1e9/sys_clk_freq)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=25e6, toolchain="peppercorn",
        with_l2_cache   = False,
        with_led_chaser = True,
        with_spi_flash  = False,
        **kwargs):
        platform = gmm7550.Platform(toolchain)

        platform.add_extension(p4)

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on GMM-7550/USB 3", **kwargs)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led_n"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=gmm7550.Platform, description="LiteX SoC on GMM-7550 and USB 3 Adapter")
    parser.add_target_argument("--sys-clk-freq",   default=25e6, type=float, help="System clock frequency.")

    parser.set_defaults(cpu_type = "vexriscv", cpu_variant = "lite")

    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq   = args.sys_clk_freq,
        toolchain      = "peppercorn", # args.toolchain,
        #with_spi_flash = args.with_spi_flash,
        **parser.soc_argdict)

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    # if args.load:
    #     prog = soc.platform.create_programmer()
    #     prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    # if args.flash:
    #     from litex.build.openfpgaloader import OpenFPGALoader
    #     prog = OpenFPGALoader("gatemate_evb_spi")
    #     prog.flash(0, builder.get_bitstream_filename(mode="flash"))

if __name__ == "__main__":
    main()
