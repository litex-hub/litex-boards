#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# Build/Use
# ---------
# 1) Update CH552 firmware: https://qiita.com/ciniml/items/05ac7fd2515ceed3f88d
# 2) Build/Load design: ./sipeed_tang_nano.py --csr-csv=csr.csv --build --load
# 3) Patch litex_server (CH552 firmware seems to require receiving a few bytes before
# operating correctly...):
#diff --git a/litex/tools/remote/comm_uart.py b/litex/tools/remote/comm_uart.py
#index bb124fb3..d5a075fd 100644
#--- a/litex/tools/remote/comm_uart.py
#+++ b/litex/tools/remote/comm_uart.py
#@@ -29,6 +29,8 @@ class CommUART(CSRBuilder):
#         if hasattr(self, "port"):
#             return
#         self.port.open()
#+        for i in range(256):
#+            self.port.write(0)
#
#     def close(self):
#         if not hasattr(self, "port"):
# 4) Start litex_server at 1MBps (CH552 does not seem to work at traditional baudrates...):
# litex_server --uart --uart-port=/dev/ttyUSBX --uart-baudrate=1000000
# 5) Test UARTBone ex: litex_cli --regs

from migen import *

from litex_boards.platforms import sipeed_tang_nano

from litex.soc.cores.clock.gowin_gw1n import  GW1NPLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_sys   = ClockDomain()

        # # #

        # Clk / Rst.
        clk24 = platform.request("clk24")
        rst_n = platform.request("user_btn", 0)

        # PLL.
        self.submodules.pll = pll = GW1NPLL(devicename=platform.devicename, device=platform.device)
        self.comb += pll.reset.eq(~rst_n)
        pll.register_clkin(clk24, 24e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCMini):
    def __init__(self, sys_clk_freq=int(48e6), with_led_chaser=True, **kwargs):
        platform = sipeed_tang_nano.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # SoCMini ----------------------------------------------------------------------------------
        kwargs["uart_name"] = "crossover"
        SoCMini.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Tang Nano", **kwargs)

        # UARTBone ---------------------------------------------------------------------------------
        self.add_uartbone(baudrate=int(1e6)) # CH552 firmware does not support traditional baudrates.

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on Tang Nano")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",       action="store_true", help="Build design.")
    target_group.add_argument("--load",        action="store_true", help="Load bitstream.")
    target_group.add_argument("--flash",       action="store_true", help="Flash Bitstream.")
    target_group.add_argument("--sys-clk-freq",default=48e6,        help="System clock frequency.")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq      = int(float(args.sys_clk_freq)),
        **soc_core_argdict(args)
    )

    builder = Builder(soc, **builder_argdict(args))
    if args.build:
        builder.build()

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.flash(0, builder.get_bitstream_filename(mode="flash", ext=".fs")) # FIXME

if __name__ == "__main__":
    main()
