#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Ilia Sergachev <ilia@sergachev.ch>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import *

from litex_boards.platforms import digilent_zedboard

from litex.soc.cores.clock import *
from litex.soc.integration.soc import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.gpio import GPIOIn

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
            # Clk.
            clk100 = platform.request("clk100")

            # PLL.
            self.pll = pll = S7PLL(speedgrade=-1)
            self.comb += pll.reset.eq(self.rst)
            pll.register_clkin(clk100, 100e6)
            pll.create_clkout(self.cd_sys, sys_clk_freq)
            # Ignore sys_clk to pll.clkin path created by SoC's rst.
            platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, toolchain="vivado", sys_clk_freq=100e6, with_led_chaser=True,
        with_buttons=False, with_switches=False, **kwargs):
        platform = digilent_zedboard.Platform(toolchain)

        assert not (toolchain != "vivado" and kwargs.get("cpu_type", None) == "zynq7000")

        if kwargs.get("cpu_type", None) != "zynq7000":
            from litex_boards.platforms.digilent_arty import usb_pmod_io
            platform.add_extension(usb_pmod_io("pmodb"))
            if kwargs.get("uart_name", "serial") == "serial": kwargs["uart_name"] = "usb_uart"
        else:
            kwargs["with_uart"] = False

        # CRG --------------------------------------------------------------------------------------
        use_ps7_clk = (kwargs.get("cpu_type", None) == "zynq7000")
        self.crg = _CRG(platform, sys_clk_freq, use_ps7_clk)

        # SoCCore ----------------------------------------------------------------------------------
        if kwargs.get("cpu_type", None) == "zynq7000":
            kwargs["integrated_sram_size"] = 0
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Zedboard", **kwargs)

        # Zynq7000 Integration ---------------------------------------------------------------------
        if kwargs.get("cpu_type", None) == "zynq7000":
            self.cpu.set_ps7(name="Zynq",
                             preset="ZedBoard",
                             config={'PCW_FPGA0_PERIPHERAL_FREQMHZ': sys_clk_freq / 1e6})

            self.bus.add_region("sram", SoCRegion(
                origin = self.cpu.mem_map["sram"],
                size   = 512 * MEGABYTE - self.cpu.mem_map["sram"])
            )
            self.bus.add_region("rom", SoCRegion(
                origin = self.cpu.mem_map["rom"],
                size   = 256 * MEGABYTE // 8,
                linker = True)
            )
            self.constants["CONFIG_CLOCK_FREQUENCY"] = 666666687
            self.cpu.set_libxil({
                "STDOUT_BASEADDRESS"            : "0xE0001000",
                "XPAR_PS7_DDR_0_S_AXI_BASEADDR" : "0x00100000",
                "XPAR_PS7_DDR_0_S_AXI_HIGHADDR" : "0x3FFFFFFF",
            })

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

        # Buttons / Switches -----------------------------------------------------------------------
        if with_buttons:
            self.buttons = GPIOIn(Cat(
                platform.request("user_btn_c"),
                platform.request("user_btn_d"),
                platform.request("user_btn_l"),
                platform.request("user_btn_r"),
                platform.request("user_btn_u"),
            ))
        if with_switches:
            self.switches = GPIOIn(Cat(platform.request_all("user_sw")))

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=digilent_zedboard.Platform, description="LiteX SoC on Zedboard.")
    parser.add_target_argument("--sys-clk-freq",        default=100e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-buttons",  action="store_true", help="Enable Buttons.")
    parser.add_target_argument("--with-switches", action="store_true", help="Enable Switches.")
    parser.set_defaults(cpu_type="zynq7000")
    args = parser.parse_args()

    soc = BaseSoC(
        toolchain     = args.toolchain,
        sys_clk_freq  = args.sys_clk_freq,
        with_buttons  = args.with_buttons,
        with_switches = args.with_switches,
        **parser.soc_argdict
    )
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
