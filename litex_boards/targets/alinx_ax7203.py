#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 Aaron Hagan <amhagan@kent.edu>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import *

from litex_boards.platforms import alinx_ax7203

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litepcie.phy.s7pciephy import S7PCIEPHY
from litepcie.software import generate_litepcie_software

from litedram.modules import MT41J256M16
from litedram.phy import s7ddrphy

from litex.soc.cores.video import VideoDVIPHY
from litex.soc.cores.bitbang import I2CMaster

# CRG ----------------------------------------------------------------------------------------------
class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_video_pll=False):
        self.rst          = Signal()
        self.cd_sys       = ClockDomain()
        self.cd_sys4x     = ClockDomain()
        self.cd_sys4x_dqs = ClockDomain()
        self.cd_idelay    = ClockDomain()
        self.cd_hdmi      = ClockDomain(reset_less=True)

        # Clk/Rst.
        clk200 = platform.request("clk200")
        clk148p5 = platform.request("clk148p5")
        rst_n  = platform.request("cpu_reset_n")
        hdmi_reset = platform.request("hdmi_reset_n")

        # Main PLL.
        self.pll = pll = S7PLL(speedgrade=-2)
        self.comb += pll.reset.eq(~rst_n | ~hdmi_reset | self.rst)
        pll.register_clkin(clk200, 200e6)
        pll.create_clkout(self.cd_sys,       sys_clk_freq)
        pll.create_clkout(self.cd_sys4x,     4*sys_clk_freq)
        pll.create_clkout(self.cd_sys4x_dqs, 4*sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_idelay,    200e6)
        pll.create_clkout(self.cd_hdmi,      148.5e6, margin=2e-2)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin)
        
        # IDELAY Ctrl.
        self.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

# BaseSoC ------------------------------------------------------------------------------------------
class BaseSoC(SoCCore):
    def __init__(self,
                 sys_clk_freq           = int(200e6),
                 with_led_chaser        = True,
                 with_pcie              = False,
                 with_video_framebuffer = False,
                 **kwargs):

        platform = alinx_ax7203.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, with_video_pll=with_video_framebuffer)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on ALINX AX7203", **kwargs)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        self.ddrphy = s7ddrphy.A7DDRPHY(platform.request("ddram"),
            memtype          = "DDR3",
            nphases          = 4,
            sys_clk_freq     = sys_clk_freq,
            iodelay_clk_freq = 200e6)

        self.add_sdram("sdram",
            phy           = self.ddrphy,
            module        = MT41J256M16(sys_clk_freq, "1:4"),
            l2_cache_size = kwargs.get("l2_size", 8192)
        )

        # PCIe -------------------------------------------------------------------------------------
        if with_pcie:
            self.pcie_phy = S7PCIEPHY(platform, platform.request("pcie_x4"),
                data_width = 128,
                bar0_size  = 0x20000)
            self.add_pcie(phy=self.pcie_phy, ndmas=1, address_width=64)
            platform.add_period_constraint(self.crg.cd_sys.clk, 1e9/sys_clk_freq)

            # ICAP (For FPGA reload over PCIe).
            from litex.soc.cores.icap import ICAP
            self.icap = ICAP()
            self.icap.add_reload()
            self.icap.add_timing_constraints(platform, sys_clk_freq, self.crg.cd_sys.clk)

            # Flash (For SPIFlash update over PCIe).
            from litex.soc.cores.gpio import GPIOOut
            from litex.soc.cores.spi_flash import S7SPIFlash
            self.flash_cs_n = GPIOOut(platform.request("flash_cs_n"))
            self.flash      = S7SPIFlash(platform.request("flash"), sys_clk_freq, 25e6)

        # Video ------------------------------------------------------------------------------------
        if with_video_framebuffer:
            hdmi_pads = platform.request("hdmi")
            self.videophy = VideoDVIPHY(hdmi_pads, clock_domain="hdmi")
            self.videoi2c = I2CMaster(hdmi_pads)
            self.videoi2c.add_init(addr=0x72>>1, init_addr_len=1, init=[
                (0x0008, 0x35)
            ])

            self.videoi2c.add_init(addr=0x7A>>1, init_addr_len=1, init=[
                (0x002f, 0x00)
            ])

            self.videoi2c.add_init(addr=0x60>>1, init_addr_len=1, init=[
                (0x0005, 0x10),
                (0x0008, 0x05),
                (0x0009, 0x01),
                (0x0005, 0x04)
            ])
            self.add_video_colorbars(phy=self.videophy, timings="1920x1080@60Hz", clock_domain="hdmi")            

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
           self.leds = LedChaser(
               pads         = platform.request_all("user_led"),
               sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------
def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=alinx_ax7203.Platform, description="LiteX SoC on ALINX AX7203.")
    parser.add_target_argument("--flash",                  action="store_true",          help="Flash bitstream.")
    parser.add_target_argument("--sys-clk-freq",           default=50e6, type=float,     help="System clock frequency.")
    parser.add_target_argument("--with-pcie",              action="store_true",          help="Enable PCIe support.")
    parser.add_target_argument("--driver",                 action="store_true",          help="Generate drivers.")
    parser.add_target_argument("--with-video-framebuffer", action="store_true",          help="Enable Video Framebuffer (HDMI).")

    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq           = args.sys_clk_freq,
        with_led_chaser        = True,
        with_pcie              = args.with_pcie,
        with_video_framebuffer = args.with_video_framebuffer,
        **parser.soc_argdict
    )

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.driver:
        generate_litepcie_software(soc, os.path.join(builder.output_dir, "driver"))

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.flash(0, builder.get_bitstream_filename(mode="flash"))

if __name__ == "__main__":
    main()
