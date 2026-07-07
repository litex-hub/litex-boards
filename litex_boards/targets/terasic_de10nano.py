#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Paul Sajna <sajattack@gmail.com>
# Copyright (c) 2026 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# Cyclone V HPS (MiSTer) use:
# ./terasic_de10nano.py --cpu-type=cyclonev_hps --build [--with-mister-sdram] [--with-f2h-sdram]
# Copy the bitstream to the MiSTer and load it:
#  scp build/terasic_de10nano/gateware/terasic_de10nano.rbf root@<mister-ip>:/media/fat/litex.rbf
#  ssh root@<mister-ip> "echo load_core /media/fat/litex.rbf > /dev/MiSTer_cmd"
# LiteX CSRs are then accessible from the HPS at 0xff20_0000 (addresses in csr.csv), ex:
#  devmem <ctrl_scratch_addr> -> 0x12345678.

from migen import *

from litex.gen import *

from litex.build.io import DDROutput

from litex_boards.platforms import terasic_de10nano

from litex.soc.cores.clock import CycloneVPLL
from litex.soc.integration.soc import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.video import VideoVGAPHY
from litex.soc.cores.led import LedChaser

from litedram.modules import AS4C32M16
from litedram.phy import GENSDRPHY, HalfRateGENSDRPHY

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_sdram=False, sdram_rate="1:1"):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()
        if sdram_rate == "1:2":
            self.cd_sys2x    = ClockDomain()
            self.cd_sys2x_ps = ClockDomain()
        else:
            self.cd_sys_ps = ClockDomain()
        self.cd_vga    = ClockDomain()

        # # #

        # Clk / Rst
        clk50 = platform.request("clk50")

        # PLL
        self.pll = pll = CycloneVPLL(speedgrade="-I7")
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk50, 50e6)
        pll.create_clkout(self.cd_sys,    sys_clk_freq)
        if sdram_rate == "1:2":
            pll.create_clkout(self.cd_sys2x,    2*sys_clk_freq)
            pll.create_clkout(self.cd_sys2x_ps, 2*sys_clk_freq, phase=90)
        else:
            pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_vga, 40e6)

        # SDRAM clock
        if with_sdram:
            sdram_clk = ClockSignal("sys2x_ps" if sdram_rate == "1:2" else "sys_ps")
            self.specials += DDROutput(1, 0, platform.request("sdram_clock"), sdram_clk)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=50e6,
        with_led_chaser            = True,
        with_mister_sdram          = True,
        with_mister_video_terminal = False,
        with_h2f_bridge            = False,
        with_f2h_sdram             = False,
        sdram_rate                 = "1:1",
        **kwargs):
        platform = terasic_de10nano.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, with_sdram=with_mister_sdram, sdram_rate=sdram_rate)

        # SoCCore ----------------------------------------------------------------------------------
        if kwargs.get("cpu_type", None) == "cyclonev_hps":
            kwargs["with_uart"]            = False # Console is on HPS UART0 (Linux on MiSTer).
            kwargs["integrated_sram_size"] = 0     # SRAM region is in HPS DDR3 (Linker-only).
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on DE10-Nano", **kwargs)

        # Cyclone V HPS Integration ----------------------------------------------------------------
        if kwargs.get("cpu_type", None) == "cyclonev_hps":
            # HPS DDR3 Regions (Linker-only, enable BIOS compilation as on Zynq targets).
            self.bus.add_region("sram", SoCRegion(
                origin = self.cpu.mem_map["sram"],
                size   = 15 * MEGABYTE,
            ))
            self.bus.add_region("rom", SoCRegion(
                origin = self.cpu.mem_map["rom"],
                size   = 8 * MEGABYTE,
                linker = True,
            ))
            # H2F Bridge (LiteX bus/Fabric SDRAM visible to the ARM at 0xc000_0000).
            if with_h2f_bridge or with_mister_sdram:
                self.bus.add_master(name="h2f", master=self.cpu.add_axi_h2f_master())
            # F2SDRAM Port 1 (64-bit): first 256MB of HPS DDR3 visible on the LiteX bus at
            # 0xd000_0000 (non-coherent with the ARM caches; useful for Fabric DMAs and as a
            # F2SDRAM smoke test from the ARM through the H2F bridge).
            if with_f2h_sdram:
                from litex.soc.interconnect.avalon import Wishbone2AvalonMM
                f2h_sdram_region = SoCRegion(origin=0xd000_0000, size=256 * MEGABYTE)
                self.f2h_sdram = Wishbone2AvalonMM(
                    data_width           = 64,
                    avalon_address_width = 29,
                    avalon_base_address  = f2h_sdram_region.origin >> 3,
                )
                self.comb += self.f2h_sdram.w2a_avl.connect(self.cpu.add_fpga2sdram_port(n=1))
                self.bus.add_slave(name="f2h_sdram", slave=self.f2h_sdram.w2a_wb, region=f2h_sdram_region)

        # SDR SDRAM --------------------------------------------------------------------------------
        if with_mister_sdram and not self.integrated_main_ram_size:
            sdrphy_cls = HalfRateGENSDRPHY if sdram_rate == "1:2" else GENSDRPHY
            self.sdrphy = sdrphy_cls(platform.request("sdram"), sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.sdrphy,
                module        = AS4C32M16(sys_clk_freq, sdram_rate),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Video Terminal ---------------------------------------------------------------------------
        if with_mister_video_terminal:
            self.videophy = VideoVGAPHY(platform.request("vga"), clock_domain="vga")
            self.add_video_terminal(phy=self.videophy, timings="800x600@60Hz", clock_domain="vga")

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=terasic_de10nano.Platform, description="LiteX SoC on DE10-Nano.")
    parser.add_target_argument("--sys-clk-freq",               default=50e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-mister-sdram",          action="store_true",      help="Enable SDRAM with MiSTer expansion board.")
    parser.add_target_argument("--with-mister-video-terminal", action="store_true",      help="Enable Video Terminal with Mister expansion board.")
    parser.add_target_argument("--with-h2f-bridge",            action="store_true",      help="Enable H2F bridge (with cyclonev_hps CPU).")
    parser.add_target_argument("--with-f2h-sdram",             action="store_true",      help="Enable F2SDRAM port (with cyclonev_hps CPU).")
    parser.add_target_argument("--sdram-rate",                 default="1:1",            help="SDRAM Rate (1:1 Full Rate or 1:2 Half Rate).")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq               = args.sys_clk_freq,
        with_mister_sdram          = args.with_mister_sdram,
        with_mister_video_terminal = args.with_mister_video_terminal,
        with_h2f_bridge            = args.with_h2f_bridge,
        with_f2h_sdram             = args.with_f2h_sdram,
        sdram_rate                 = args.sdram_rate,
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
