#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Rakesh Peter <rakesh@stanproc.in>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex_boards.platforms import pynq_z1
from litex.build.xilinx.vivado import vivado_build_args, vivado_build_argdict

from litex.soc.interconnect import axi
from litex.soc.interconnect import wishbone

from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

from litex.soc.cores.clock import *
from litex.soc.cores.video import VideoS7HDMIPHY
from litex.soc.cores.led import LedChaser

# CRG ----------------------------------------------------------------------------------------------
class _CRG(Module):
    def __init__(self, platform, sys_clk_freq, toolchain, use_ps7_clk=False, with_video_pll=False):
        self.rst = Signal()
        self.clock_domains.cd_sys    = ClockDomain()
        self.clock_domains.cd_hdmi   = ClockDomain()
        self.clock_domains.cd_hdmi5x = ClockDomain()

        # # #

        # Clk
        clk125 = platform.request("sysclk")

        # PLL
        if use_ps7_clk:
            assert sys_clk_freq == 125e6
            self.comb += ClockSignal("sys").eq(ClockSignal("ps7"))
            self.comb += ResetSignal("sys").eq(ResetSignal("ps7") | self.rst)
        else:
            self.submodules.pll = pll = S7PLL(speedgrade=-1)
            self.comb += pll.reset.eq(self.rst)
            pll.register_clkin(clk125, 125e6)
            pll.create_clkout(self.cd_sys, sys_clk_freq)
            platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        # Video PLL.
        if with_video_pll:
            self.submodules.video_pll = video_pll = S7MMCM(speedgrade=-1)
            video_pll.reset.eq(self.rst)
            video_pll.register_clkin(clk125, 125e6)
            video_pll.create_clkout(self.cd_hdmi,   40e6)
            video_pll.create_clkout(self.cd_hdmi5x, 5*40e6)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, toolchain="vivado", sys_clk_freq=int(100e6), with_led_chaser=True,
                with_video_terminal=False, with_video_framebuffer=False, **kwargs):
        platform = pynq_z1.Platform()

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident = "LiteX SoC on PYNQ Z1",
            **kwargs)

        # Zynq7000 Integration ---------------------------------------------------------------------
        if kwargs.get("cpu_type", None) == "zynq7000":
            # Get and set the pre-generated .xci FIXME: change location? add it to the repository?
            os.system("wget https://github.com/litex-hub/litex-boards/files/8339591/zybo_z7_ps7.txt)")
            os.makedirs("xci", exist_ok=True)
            os.system("mv zybo_z7_ps7.txt xci/zybo_z7_ps7.xci")
            self.cpu.set_ps7_xci("xci/zybo_z7_ps7.xci")

            # Connect AXI GP0 to the SoC with base address of 0x43c00000 (default one)
            wb_gp0  = wishbone.Interface()
            self.submodules += axi.AXI2Wishbone(
                axi          = self.cpu.add_axi_gp_master(),
                wishbone     = wb_gp0,
                base_address = 0x43c00000)
            self.add_wb_master(wb_gp0)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq, toolchain, with_video_pll=with_video_terminal)

        # Video ------------------------------------------------------------------------------------
        if with_video_terminal:
            self.submodules.videophy = VideoS7HDMIPHY(platform.request("hdmi_tx"), clock_domain="hdmi")
            self.add_video_terminal(phy=self.videophy, timings="800x600@60Hz", clock_domain="hdmi")

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on PYNQ Z1")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",               action="store_true", help="Build bitstream.")
    target_group.add_argument("--load",                action="store_true", help="Load bitstream.")
    target_group.add_argument("--sys-clk-freq",        default=125e6,       help="System clock frequency.")
    target_group.add_argument("--with-video-terminal", action="store_true", help="Enable Video Terminal (HDMI).")

    builder_args(parser)
    soc_core_args(parser)
    vivado_build_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq        = int(float(args.sys_clk_freq)),
        with_video_terminal = args.with_video_terminal,
        **soc_core_argdict(args)
    )
    builder = Builder(soc, **builder_argdict(args))
    builder.build(**vivado_build_argdict(args), run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"), device=1)

if __name__ == "__main__":
    main()
