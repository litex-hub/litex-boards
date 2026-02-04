#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 Victor-zyy <gt7591665@gmail.com>
# Copyright (c) 2026 Matt Reverzani <mrev@posteo.de>
# SPDX-License-Identifier: BSD-2-Clause

# Note: For now with --toolchain=yosys+nextpnr:
# - DDR3 should be disabled: ex --integrated-main-ram-size=8192
# - Clk Freq should be lowered: ex --sys-clk-freq=50e6

from migen import *

from litex.gen import *

from litex_boards.platforms import microphase_a7_lite

from litex.soc.cores.clock import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.gpio import GPIOIn, GPIOTristate
from litex.soc.cores.xadc import XADC
from litex.soc.cores.dna import DNA

from litedram.modules import MT41K256M16
from litedram.phy import s7ddrphy

from liteeth.phy.s7rgmii import LiteEthPHYRGMII

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, speedgrade=-1, with_dram=True):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()
        if with_dram:
            self.cd_sys4x     = ClockDomain()
            self.cd_sys4x_dqs = ClockDomain()
            self.cd_idelay    = ClockDomain()

        # # #

        # Clk/Rst.
        clk50  = platform.request("clk50")
        rst_n  = platform.request("cpu_reset")

        # PLL.
        self.pll = pll = S7MMCM(speedgrade=speedgrade)
        self.comb += pll.reset.eq(~rst_n | self.rst)
        pll.register_clkin(clk50, 50e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.
        if with_dram:
            pll.create_clkout(self.cd_sys4x,     4*sys_clk_freq)
            pll.create_clkout(self.cd_sys4x_dqs, 4*sys_clk_freq, phase=90)
            pll.create_clkout(self.cd_idelay,    200e6)

        # IdelayCtrl.
        if with_dram:
            self.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, variant="200t", programmer="vivado", toolchain="vivado", sys_clk_freq=int(100e6), speedgrade=-1,
        with_xadc       = False,
        with_dna        = False,
        with_ethernet   = False,
        with_led_chaser = True,
        with_spi_flash  = False,
        with_i2c        = False,
        with_buttons    = False,
        with_sdcard     = False,
        with_spi_sdcard = False,
        **kwargs):
        platform = microphase_a7_lite.Platform(variant=variant, programmer=programmer, toolchain=toolchain)

        # CRG --------------------------------------------------------------------------------------
        with_dram = (kwargs.get("integrated_main_ram_size", 0) == 0)
        self.crg  = _CRG(platform, sys_clk_freq, speedgrade, with_dram)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Microphase A7-Lite", **kwargs)

        # XADC -------------------------------------------------------------------------------------
        if with_xadc:
            self.xadc = XADC()

        # DNA --------------------------------------------------------------------------------------
        if with_dna:
            self.dna = DNA()
            self.dna.add_timing_constraints(platform, sys_clk_freq, self.crg.cd_sys.clk)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.ddrphy = s7ddrphy.A7DDRPHY(platform.request("ddram"),
                memtype        = "DDR3",
                nphases        = 4,
                sys_clk_freq   = sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT41K256M16(sys_clk_freq, "1:4"),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Ethernet ---------------------------------------------------------------------------------
        if with_ethernet:
            self.ethphy = LiteEthPHYRGMII(
                clock_pads = self.platform.request("eth_clocks"),
                pads       = self.platform.request("eth"),
                tx_delay   = 2e-9,
                rx_delay   = 2e-9,
                iodelay_clk_freq = 200e6)
            self.add_ethernet(phy=self.ethphy)

        # SPI Flash --------------------------------------------------------------------------------
        if with_spi_flash:
            from litespi.modules import IS25LP128
            from litespi.opcodes import SpiNorFlashOpCodes as Codes
            self.add_spi_flash(mode="1x", module=IS25LP128(Codes.READ_1_1_1), with_master=True)

        # System I2C -------------------------------------------------------------------------------
        if with_i2c:
            from litex.soc.cores.bitbang import I2CMaster
            self.i2c = I2CMaster(platform.request("i2c"))

        # SD Card ----------------------------------------------------------------------------------
        if with_sdcard:
            self.add_sdcard()
        elif with_spi_sdcard:
            self.add_spi_sdcard()

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq,
            )

        # Buttons ----------------------------------------------------------------------------------
        if with_buttons:
            self.buttons = GPIOIn(
                pads     = platform.request_all("user_btn"),
                with_irq = self.irq.enabled
            )

# Build -------------------------------------------------------------------------------------------- 

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=microphase_a7_lite.Platform, description="LiteX SoC on Microphase A7-Lite")
    parser.add_target_argument("--flash",          action="store_true",       help="Flash bitstream.")
    parser.add_target_argument("--variant",        default="200t",            help="Board variant (35t, 100t or 200t).")
    parser.add_target_argument("--sys-clk-freq",   default=100e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--speedgrade",     default=-1, type=int,      help="FPGA speedgrade (-1 or -2).")
    parser.add_target_argument("--with-xadc",      action="store_true",       help="Enable 7-Series XADC.")
    parser.add_target_argument("--with-dna",       action="store_true",       help="Enable 7-Series DNA.")
    parser.add_target_argument("--with-buttons",   action="store_true",       help="Enable User Buttons.")
    parser.add_target_argument("--with-ethernet",  action="store_true",       help="Enable Ethernet support.")
    parser.add_target_argument("--with-i2c",       action="store_true",       help="Enable I2C.")
    parser.add_target_argument("--programmer",     default="vivado",          help="Programmer (vivado or openocd).")
    parser.add_target_argument("--with-sdcard",    action="store_true",       help="Enable SDCard support.")
    parser.add_target_argument("--with-spi-flash", action="store_true",       help="Enable SPI Flash.")
    parser.add_target_argument("--with-spi-sdcard",action="store_true",       help="Enable SPI-mode SDCard support.")
    args = parser.parse_args()

    soc = BaseSoC(
        variant        = args.variant,
        toolchain      = args.toolchain,
        sys_clk_freq   = args.sys_clk_freq,
        speedgrade     = args.speedgrade,
        with_xadc      = args.with_xadc,
        with_dna       = args.with_dna,
        with_buttons   = args.with_buttons,
        with_ethernet  = args.with_ethernet,
        with_i2c       = args.with_i2c,
        programmer     = args.programmer,
        with_sdcard    = args.with_sdcard,
        with_spi_flash = args.with_spi_flash,
        with_spi_sdcard= args.with_spi_sdcard,
        **parser.soc_argdict
    )

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.flash(0, builder.get_bitstream_filename(mode="flash"))

if __name__ == "__main__":
    main()
