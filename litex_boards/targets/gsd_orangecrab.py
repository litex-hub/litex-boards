#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) Greg Davill <greg.davill@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause


from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *
from litex.gen.genlib.misc import WaitTimer

from litex_boards.platforms import gsd_orangecrab

from litex.soc.cores.clock import *
from litex.soc.integration.soc import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litedram.modules import MT41K64M16, MT41K128M16, MT41K256M16, MT41K512M16
from litedram.phy import ECP5DDRPHY

# CRG ---------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_usb_pll=False, with_dfu_rst=True):
        self.rst    = Signal()
        self.cd_por = ClockDomain()
        self.cd_sys = ClockDomain()

        # # #

        # Clk / Rst
        clk48 = platform.request("clk48")
        rst_n = platform.request("usr_btn", loose=True)
        if (rst_n is None) or (not with_dfu_rst): rst_n = 1

        # Power on reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += self.cd_por.clk.eq(clk48)
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # PLL
        self.pll = pll = ECP5PLL()
        self.comb += pll.reset.eq(~por_done | ~rst_n | self.rst)
        pll.register_clkin(clk48, 48e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)

        # USB PLL
        if with_usb_pll:
            self.cd_usb_12 = ClockDomain()
            self.cd_usb_48 = ClockDomain()
            usb_pll = ECP5PLL()
            self.submodules += usb_pll
            self.comb += usb_pll.reset.eq(~por_done)
            usb_pll.register_clkin(clk48, 48e6)
            usb_pll.create_clkout(self.cd_usb_48, 48e6)
            usb_pll.create_clkout(self.cd_usb_12, 12e6)

        # FPGA Reset (press usr_btn for 1 second to fallback to bootloader)
        if with_dfu_rst:
            reset_timer = WaitTimer(48e6)
            reset_timer = ClockDomainsRenamer("por")(reset_timer)
            self.submodules += reset_timer
            self.comb += reset_timer.wait.eq(~rst_n)
            self.comb += platform.request("rst_n").eq(~reset_timer.done)


class _CRGSDRAM(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_usb_pll=False, with_dfu_rst=True, sdram_rate="1:2"):
        self.rst = Signal()
        self.cd_init     = ClockDomain()
        self.cd_por      = ClockDomain()
        self.cd_sys      = ClockDomain()
        self.cd_sys2x    = ClockDomain()
        self.cd_sys2x_i  = ClockDomain()
        if sdram_rate == "1:4":
            self.cd_sys4x   = ClockDomain()
            self.cd_sys4x_i = ClockDomain()

        # # #

        self.stop  = Signal()
        self.reset = Signal()

        # Clk / Rst
        clk48 = platform.request("clk48")
        rst_n = platform.request("usr_btn", loose=True)
        if (rst_n is None) or (not with_dfu_rst): rst_n = 1

        # Power on reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += self.cd_por.clk.eq(clk48)
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # PLL
        sys2x_clk_ecsout = Signal()
        self.pll = pll = ECP5PLL()
        self.comb += pll.reset.eq(~por_done | ~rst_n | self.rst)
        pll.register_clkin(clk48, 48e6)
        if sdram_rate == "1:2":
            # sys2x: DDR edge clock (ECLKBRIDGECS + ECLKSYNCB), sys = sys2x/2 (CLKDIVF).
            pll.create_clkout(self.cd_sys2x_i, 2*sys_clk_freq)
            pll.create_clkout(self.cd_init, 24e6)
            self.specials += [
                Instance("ECLKBRIDGECS",
                    i_CLK0   = self.cd_sys2x_i.clk,
                    i_SEL    = 0,
                    o_ECSOUT = sys2x_clk_ecsout),
                Instance("ECLKSYNCB",
                    i_ECLKI = sys2x_clk_ecsout,
                    i_STOP  = self.stop,
                    o_ECLKO = self.cd_sys2x.clk),
                Instance("CLKDIVF",
                    p_DIV     = "2.0",
                    i_ALIGNWD = 0,
                    i_CLKI    = self.cd_sys2x.clk,
                    i_RST     = self.reset,
                    o_CDIVX   = self.cd_sys.clk),
                AsyncResetSynchronizer(self.cd_sys, ~pll.locked | self.reset),
            ]
        else:
            # sys4x: DDR edge clock (ECLKSYNCB), sys2x = sys4x/2 (CLKDIVF, PHY clock). sys
            # (controller clock) must be phase aligned with sys2x (DFI rate converter): generated
            # through the second edge clock synchronizer/divider of the DDR bank (bank 6) from a 2x sys
            # PLL output (same structural path as sys2x, both realigned by the PHY init stop/reset
            # sequence).
            eclksync1_bel, clkdiv1_bel = {
                "25F": ("X0/Y26/ECLKSYNC1_BK6", "X0/Y25/CLKDIV1"),
                "85F": ("X0/Y47/ECLKSYNC1_BK6", "X0/Y46/CLKDIV1"),
            }["25F" if "25F" in platform.device else "85F"]
            pll.create_clkout(self.cd_sys4x_i, 4*sys_clk_freq)
            pll.create_clkout(self.cd_sys2x_i, 2*sys_clk_freq)
            pll.create_clkout(self.cd_init, 24e6)
            sys4x_clk_ecsout = Signal()
            sys2x_e = Signal()
            self.specials += [
                # The DDR3 pads span both device sides (DQ/DQS left, A/BA right): the edge clock
                # crosses through the bridge as at 1:2.
                Instance("ECLKBRIDGECS",
                    i_CLK0   = self.cd_sys4x_i.clk,
                    i_SEL    = 0,
                    o_ECSOUT = sys4x_clk_ecsout),
                Instance("ECLKSYNCB",
                    i_ECLKI = sys4x_clk_ecsout,
                    i_STOP  = self.stop,
                    o_ECLKO = self.cd_sys4x.clk),
                Instance("CLKDIVF",
                    p_DIV     = "2.0",
                    i_ALIGNWD = 0,
                    i_CLKI    = self.cd_sys4x.clk,
                    i_RST     = self.reset,
                    o_CDIVX   = self.cd_sys2x.clk),
                Instance("ECLKSYNCB",
                    i_ECLKI = self.cd_sys2x_i.clk,
                    i_STOP  = self.stop,
                    o_ECLKO = sys2x_e,
                    attr    = {("BEL", eclksync1_bel)}),
                Instance("CLKDIVF",
                    p_DIV     = "2.0",
                    i_ALIGNWD = 0,
                    i_CLKI    = sys2x_e,
                    i_RST     = self.reset,
                    o_CDIVX   = self.cd_sys.clk,
                    attr      = {("BEL", clkdiv1_bel)}),
                AsyncResetSynchronizer(self.cd_sys4x, ~pll.locked | self.reset),
                AsyncResetSynchronizer(self.cd_sys,   ~pll.locked | self.reset),
            ]
            # sys2x reset released from sys (deterministic phase of the DFI rate converter).
            sys2x_rst = Signal(reset=1, reset_less=True)
            self.sync.sys2x += sys2x_rst.eq(ResetSignal("sys"))
            self.comb += self.cd_sys2x.rst.eq(sys2x_rst)

        # USB PLL
        if with_usb_pll:
            self.cd_usb_12 = ClockDomain()
            self.cd_usb_48 = ClockDomain()
            usb_pll = ECP5PLL()
            self.submodules += usb_pll
            self.comb += usb_pll.reset.eq(~por_done)
            usb_pll.register_clkin(clk48, 48e6)
            usb_pll.create_clkout(self.cd_usb_48, 48e6)
            usb_pll.create_clkout(self.cd_usb_12, 12e6)

        # FPGA Reset (press usr_btn for 1 second to fallback to bootloader)
        if with_dfu_rst:
            reset_timer = WaitTimer(48e6)
            reset_timer = ClockDomainsRenamer("por")(reset_timer)
            self.submodules += reset_timer
            self.comb += reset_timer.wait.eq(~rst_n)
            self.comb += platform.request("rst_n").eq(~reset_timer.done)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, revision="0.2", device="25F", sys_clk_freq=48e6, toolchain="trellis",
        sdram_device    = "MT41K64M16",
        sdram_rate      = "1:2",
        with_dfu_rst    = True,
        with_led_chaser = True,
        **kwargs):
        platform = gsd_orangecrab.Platform(revision=revision, device=device ,toolchain=toolchain)

        # Default to USB ACM through LUNA, but allow explicit override.
        uart_name = kwargs.get("uart_name", "serial")
        if uart_name == "serial":
            uart_name = "usb_acm"
        kwargs["uart_name"] = uart_name

        # CRG --------------------------------------------------------------------------------------
        crg_cls      = _CRGSDRAM if kwargs.get("integrated_main_ram_size", 0) == 0 else _CRG
        crg_kwargs   = {"sdram_rate": sdram_rate} if crg_cls is _CRGSDRAM else {}
        self.crg = crg_cls(platform, sys_clk_freq, with_usb_pll=(uart_name == "usb_acm"), with_dfu_rst=with_dfu_rst, **crg_kwargs)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on OrangeCrab", **kwargs)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            available_sdram_modules = {
                "MT41K64M16":  MT41K64M16,
                "MT41K128M16": MT41K128M16,
                "MT41K256M16": MT41K256M16,
                "MT41K512M16": MT41K512M16,
            }
            sdram_module = available_sdram_modules.get(sdram_device)

            ddram_pads = platform.request("ddram")
            # 1:2: DDR3 at 2x sys. 1:4: DDR3 at 4x sys.
            if sdram_rate == "1:2":
                phy_cls = ECP5DDRPHY
            else:
                from litedram.phy.ecp5ddrphy import ecp5ddrphy_with_ratio
                phy_cls = ecp5ddrphy_with_ratio(2)
            self.ddrphy = phy_cls(
                pads         = ddram_pads,
                sys_clk_freq = sys_clk_freq,
                dm_remapping = {0:1, 1:0},
                cmd_delay    = 0 if sys_clk_freq > 64e6 else 100)
            self.ddrphy.settings.rtt_nom = "disabled"
            if hasattr(ddram_pads, "vccio"):
                self.comb += ddram_pads.vccio.eq(0b111111)
            if hasattr(ddram_pads, "gnd"):
                self.comb += ddram_pads.gnd.eq(0)
            self.comb += self.crg.stop.eq(self.ddrphy.init.stop)
            self.comb += self.crg.reset.eq(self.ddrphy.init.reset)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = sdram_module(sys_clk_freq, sdram_rate),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=gsd_orangecrab.Platform, description="LiteX SoC on OrangeCrab.")
    parser.add_target_argument("--sys-clk-freq",    default=48e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--revision",        default="0.2",            help="Board Revision (0.1 or 0.2).")
    parser.add_target_argument("--device",          default="25F",            help="ECP5 device (25F, 45F or 85F).")
    parser.add_target_argument("--sdram-device",    default="MT41K64M16",     help="SDRAM device (MT41K64M16, MT41K128M16, MT41K256M16 or MT41K512M16).")
    parser.add_target_argument("--sdram-rate",      default="1:2", choices=["1:2", "1:4"], help="SDRAM controller:DRAM clock ratio.")
    parser.add_target_argument("--with-spi-sdcard", action="store_true",      help="Enable SPI-mode SDCard support.")
    parser.add_target_argument("--without-dfu-rst", action="store_true",      help="Disable DFU Reset when pressing Button for 1s.")
    args = parser.parse_args()

    soc = BaseSoC(
        toolchain    = args.toolchain,
        revision     = args.revision,
        device       = args.device,
        sdram_device = args.sdram_device,
        sdram_rate   = args.sdram_rate,
        sys_clk_freq = args.sys_clk_freq,
        with_dfu_rst = not args.without_dfu_rst,
        **parser.soc_argdict)
    if args.with_spi_sdcard:
        soc.add_spi_sdcard()
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
