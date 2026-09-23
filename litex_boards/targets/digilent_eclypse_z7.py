#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 Gwenhael Goavec-Merou <gwenhael.goavec-merou@trabucayre.com>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import *

from litex_boards.platforms import digilent_eclypse_z7

from litex.soc.cores.clock import *
from litex.soc.cores.gpio import GPIOIn
from litex.soc.cores.led import LedChaser
from litex.soc.integration.soc import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, use_ps7_clk=False):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()

        # # #

        if use_ps7_clk:
            self.comb += ClockSignal("sys").eq(ClockSignal("ps7"))
            self.comb += ResetSignal("sys").eq(ResetSignal("ps7") | self.rst)
        else:
            clk125 = platform.request("clk125")

            self.pll = pll = S7PLL(speedgrade=-1)
            self.comb += pll.reset.eq(self.rst)
            pll.register_clkin(clk125, 125e6)
            pll.create_clkout(self.cd_sys, sys_clk_freq)
            platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, toolchain="vivado", sys_clk_freq=125e6,
        with_buttons    = False,
        with_led_chaser = True,
        **kwargs):

        platform = digilent_eclypse_z7.Platform(toolchain=toolchain)

        # CRG --------------------------------------------------------------------------------------
        with_ps7 = (kwargs.get("cpu_type", None) == "zynq7000")
        if with_ps7:
            sys_clk_freq = 100e6

        self.crg = _CRG(platform, sys_clk_freq, with_ps7)

        # SoCCore ----------------------------------------------------------------------------------
        if kwargs.get("cpu_type", None) == "zynq7000":
            kwargs["integrated_sram_size"] = 0
            kwargs["with_uart"]            = False
        else:
            if kwargs.get("uart_name", None) == "crossover":
                kwargs["with_jtagbone"] = True
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Eclypse Z7", **kwargs)

        # Zynq7000 Integration ---------------------------------------------------------------------
        if with_ps7:
            ps7_pads_cfg = dict()
            # USB pads configuration
            usb_pads    = "MIO 28 .. 39"
            first, last = map(int, usb_pads.split()[1::2])
            direction   = ["inout", "in", "out", "in"] + ["inout"] * 4 + ["in"] + ["inout"] * 3
            for p,d in zip(range(first, last + 1), direction):
                ps7_pads_cfg.update({
                    f"PCW_MIO_{p}_PULLUP"    : "enabled",
                    f"PCW_MIO_{p}_IOTYPE"    : "LVCMOS 1.8V",
                    f"PCW_MIO_{p}_DIRECTION" : d,
                    f"PCW_MIO_{p}_SLEW"      : "fast",
                })

            self.cpu.set_ps7(name="Zynq",
                config={
                    **platform.ps7_config,
                    **ps7_pads_cfg,
                    "PCW_FPGA0_PERIPHERAL_FREQMHZ" : sys_clk_freq / 1e6,
                    "PCW_ENET0_RESET_ENABLE"       : "1",
                    "PCW_ENET0_RESET_IO"           : "MIO 9",
                }
            )

            self.bus.add_region("sram", SoCRegion(
                origin = self.cpu.mem_map["sram"],
                size   = 512 * MEGABYTE - self.cpu.mem_map["sram"])
            )
            self.bus.add_region("rom", SoCRegion(
                origin = self.cpu.mem_map["rom"],
                size   = 256 * MEGABYTE // 8,
                linker = True)
            )
            self.bus.add_region("flash", SoCRegion(
                origin = 0xFC00_0000,
                size   = 0x4_0000,
                mode   = "rwx")
            )

            self.constants["CONFIG_CLOCK_FREQUENCY"] = 666666687

            # Enable PS/MIO Ethernet.
            self.cpu.add_ethernet(0, "MIO 16 .. 27", "MIO 52 .. 53")

            # Enable UART0.
            self.cpu.add_uart(0, "MIO 14 .. 15")

            # Enable SDIO.
            self.cpu.add_sdio(0, "MIO 40 .. 45", "MIO 47", None, None)

            # Enable I2C1.
            self.cpu.add_i2c(1, "MIO 12 .. 13", iotype="LVCMOS 3.3V", slew="slow")

            self.cpu.set_libxil({
                "STDOUT_BASEADDRESS"            : "XPS_UART0_BASEADDR",
                "XPAR_PS7_DDR_0_S_AXI_BASEADDR" : "0x00100000",
                "XPAR_PS7_DDR_0_S_AXI_HIGHADDR" : "0x3FFFFFFF",
            })

        # Buttons ----------------------------------------------------------------------------------
        if with_buttons:
            self.buttons = GPIOIn(
                pads     = platform.request_all("user_btn"),
                with_irq = self.irq.enabled
            )
        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            led_pads = []
            for i in range(2):
                rgb_led_pads = platform.request("rgb_led", i)
                self.comb += [getattr(rgb_led_pads, n).eq(0) for n in "gb"] # Disable Green/Blue Leds.
                led_pads.append(rgb_led_pads.r)
            self.leds = LedChaser(
                pads         = Cat(led_pads),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=digilent_eclypse_z7.Platform, description="LiteX SoC on Eclypse Z7.")
    parser.add_target_argument("--sys-clk-freq", default=125e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-buttons", action="store_true",       help="Enable Buttons.")

    parser.set_defaults(cpu_type="zynq7000")
    parser.set_defaults(no_uart=True)
    args = parser.parse_args()

    soc = BaseSoC(
        toolchain    = args.toolchain,
        sys_clk_freq = args.sys_clk_freq,
        with_buttons = args.with_buttons,
        **parser.soc_argdict
    )

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"), device=1)

if __name__ == "__main__":
    main()
