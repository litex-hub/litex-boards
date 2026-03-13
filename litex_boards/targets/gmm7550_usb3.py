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
from litex.soc.cores.gpio import GPIOOut

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

# Memory Module (SRAM and SPI) on P2 (North) ------------------------------------

p2 = [
    ("spiflash", 0,
        Subsignal("cs_n", Pins("P2:3")),
        Subsignal("clk",  Pins("P2:6")),
        Subsignal("mosi", Pins("P2:11")), # D0
        Subsignal("miso", Pins("P2:5")),  # D1
        Subsignal("wp",   Pins("P2:9")),  # D2
        Subsignal("hold", Pins("P2:4")),  # D3
    ),
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("P2:3")),
        Subsignal("clk",  Pins("P2:6")),
        Subsignal("dq",   Pins("P2:11 P2:5 P2:9 P2:4")),
    ),

    ("async_sram", 0,
        Subsignal("ce", Pins("P2:24")),
        Subsignal("oe", Pins("P2:27")),
        Subsignal("we", Pins("P2:44")),
        Subsignal("adr", Pins("P2:10 P2:12 P2:16 P2:18", # A0, A1, A2, A3
                              "P2:22 P2:46 P2:50 P2:52", # A4, A5, A6, A7
                              "P2:56 P2:58 P2:57 P2:55", # A8, A9, A10, A11
                              "P2:51 P2:49 P2:45 P2:23", # A12, A13, A14, A15
                              "P2:21 P2:17 P2:15")),
        Subsignal("dat", Pins("P2:28 P2:30 P2:38 P2:40",   # D0, D1, D1, D3
                              "P2:43 P2:39 P2:37 P2:29")), # D4, D5, D6, D7
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

# AsyncSRAM ------------------------------------------------------------------------------------------

class AsyncSRAM(LiteXModule):

    def __init__(self, platform, clk, rst, wb, size, pins):
        self.bus = wb
        self.data_width = 32
        self.size = size
        self.specials += Instance("issiram",
                                  i_clk = clk,
                                  i_rst = rst,
                                  i_wbs_stb_i = self.bus.stb,
                                  i_wbs_cyc_i = self.bus.cyc,
                                  i_wbs_adr_i = self.bus.adr,
                                  i_wbs_we_i  = self.bus.we,
                                  i_wbs_sel_i = self.bus.sel,
                                  i_wbs_dat_i = self.bus.dat_w,
                                  o_wbs_ack_o = self.bus.ack,
                                  o_wbs_dat_o = self.bus.dat_r,
                                  o_mem_ce_n = pins.ce,
                                  o_mem_oe_n = pins.oe,
                                  o_mem_we_n = pins.we,
                                  o_mem_adr  = pins.adr,
                                  io_mem_dat = pins.dat,
                                  )
        hdl_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                               "gmm7550")
        platform.add_source(os.path.join(hdl_dir, "issiram.v"))

def add_async_ram(soc, platform, name, origin, size):
    ram_bus = wishbone.Interface(data_width=soc.bus.data_width)
    clk     = ClockSignal()
    rst     = ResetSignal()
    ram     = AsyncSRAM(platform, clk, rst, ram_bus, 512 * 1024,
                        platform.request("async_sram"))

    soc.bus.add_slave(name, ram.bus, SoCRegion(origin=origin, size=size, mode="rwx"))
    soc.check_if_exists(name)
    soc.logger.info("AsyncSRAM {} {} {}.".format(
        colorer(name),
        colorer("added", color="green"),
        soc.bus.regions[name]))
    setattr(soc.submodules, name, ram)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=25e6, toolchain="peppercorn",
        with_l2_cache   = False,
        with_led_chaser = True,
        with_spi_flash  = False,
        with_async_ram  = False,
        **kwargs):
        platform = gmm7550.Platform(toolchain)

        platform.add_extension(p4)

        if with_spi_flash or with_async_ram:
            platform.add_extension(p2)

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on GMM-7550/USB 3", **kwargs)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led_n"),
                sys_clk_freq = sys_clk_freq)

        led_red_n = platform.request("led_red_n")
        led_green = platform.request("led_green")
        gpo = Signal(2)
        self.gpio = GPIOOut(gpo)
        self.comb += [led_red_n.eq(~gpo[0]), led_green.eq(gpo[1])]

        # Asynchronous SRAM ------------------------------------------------------------------------
        if with_async_ram:
            add_async_ram(self, platform, "main_ram", 0x40000000, 512 * KILOBYTE)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=gmm7550.Platform, description="LiteX SoC on GMM-7550 and USB 3 Adapter")
    parser.add_target_argument("--sys-clk-freq",   default=25e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-spi-flash", action="store_true", help="Enable SPI Flash")
    parser.add_target_argument("--with-async-ram", action="store_true", help="Enable Asynchronous SRAM")

    parser.set_defaults(cpu_type = "vexriscv", cpu_variant = "lite")

    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq   = args.sys_clk_freq,
        toolchain      = "peppercorn", # args.toolchain,
        with_spi_flash = args.with_spi_flash,
        with_async_ram = args.with_async_ram,
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
