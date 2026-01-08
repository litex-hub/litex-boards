#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Icenowy Zheng <uwu@icenowy.me>
# Copyright (c) 2022 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2025 Gwenhael Goavec-Merou <gwenhael.goavec-merou@trabucayre.com>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from litex.build.generic_platform import *

from litex.soc.cores.clock.gowin_gw5a import GW5APLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.video import *

from liteeth.phy.gw5rgmii import LiteEthPHYRGMII

from litepcie.phy.gw5apciephy import GW5APCIEPHY
from litepcie.software import *

from litedram.modules import AS4C32M16, MT41J256M16, W9825G6KH6
from litedram.phy import GENSDRPHY, HalfRateGENSDRPHY
from litedram.phy import GW5DDRPHY
from litex.build.io import DDROutput

from litex_boards.platforms import sipeed_tang_mega_138k

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, cpu_clk_freq=0,
        with_sdram     = False, sdram_rate="1:2",
        with_ddr3      = False,
        with_video_pll = False,
        with_pcie      = False,
        with_ethernet  = False,
        ):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()
        self.cd_por = ClockDomain()

        if cpu_clk_freq:
            self.cd_cpu = ClockDomain()

        if with_sdram:
            if sdram_rate == "1:2":
                self.cd_sys2x    = ClockDomain()
                self.cd_sys2x_ps = ClockDomain()
            else:
                self.cd_sys_ps = ClockDomain()

        if with_ddr3:
            self.cd_init    = ClockDomain()
            self.cd_sys2x   = ClockDomain()
            self.cd_sys2x_i = ClockDomain()
            self.stop       = Signal()
            self.reset      = Signal()

        if with_pcie:
            self.cd_crg_pcie = ClockDomain()

        # Clk
        clk50 = platform.request("clk50")

        # Power on reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += self.cd_por.clk.eq(clk50)
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # PLL
        self.pll = pll = GW5APLL(devicename=platform.devicename, device=platform.device)
        self.comb += pll.reset.eq(~por_done | self.rst)
        pll.register_clkin(clk50, 50e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq, with_reset=not with_ddr3)
        if cpu_clk_freq:
            pll.create_clkout(self.cd_cpu, cpu_clk_freq, with_reset=False)
        platform.toolchain.additional_cst_commands.append("INS_LOC \"PLL\" PLL_R[0]") # Magic incantation for Gowin-AE350 CPU :)

        # SDRAM clock
        if with_sdram:
            if sdram_rate == "1:2":
                pll.create_clkout(self.cd_sys2x,    2*sys_clk_freq)
                pll.create_clkout(self.cd_sys2x_ps, 2*sys_clk_freq, phase=180)
                sdram_clk = ClockSignal("sys2x_ps")
            else:
                pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=90)
                sdram_clk = ClockSignal("sys_ps")
            self.specials += DDROutput(1, 0, platform.request("sdram_clock"), sdram_clk)

        # DDR3 clock
        if with_ddr3:
            pll.create_clkout(self.cd_sys2x_i, 2*sys_clk_freq)
            self.specials += [
                Instance("DHCE",
                    i_CLKIN  = self.cd_sys2x_i.clk,
                    i_CEN    = self.stop,
                    o_CLKOUT = self.cd_sys2x.clk
                ),
                AsyncResetSynchronizer(self.cd_sys2x, ~pll.locked | self.reset),
            ]
            # Init clock domain
            self.comb += [
                self.cd_init.clk.eq(clk50),
                self.cd_init.rst.eq(pll.reset),
            ]

        # Video Clock
        if with_video_pll:
            self.cd_hdmi   = ClockDomain()
            self.cd_hdmi5x = ClockDomain()
            pll.create_clkout(self.cd_hdmi5x, 125e6, margin=1e-3)
            self.specials += Instance("CLKDIV",
                p_DIV_MODE = "5",
                i_HCLKIN   = self.cd_hdmi5x.clk,
                i_RESETN   = 1, # Disable reset signal.
                i_CALIB    = 0, # No calibration.
                o_CLKOUT   = self.cd_hdmi.clk
            )

        if with_pcie:
            pll.create_clkout(self.cd_crg_pcie, 100e6, with_reset=False)

        if with_ethernet:
            clk50_half = Signal()
            self.specials += Instance("CLKDIV",
                p_DIV_MODE = "2",
                i_HCLKIN   = platform.lookup_request("clk50"),
                i_RESETN   = 1,
                i_CALIB    = 0,
                o_CLKOUT   = clk50_half)
            self.specials += DDROutput(1, 0, platform.request("eth_ref_clk"), clk50_half)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=50e6,
        with_ethernet          = True,
        with_etherbone         = False,
        local_ip               = "192.168.1.50",
        remote_ip              = "",
        eth_dynamic_ip         = False,
        with_video_colorbars   = False,
        with_video_terminal    = False,
        with_video_framebuffer = False,
        with_ddr3              = False,
        with_sdram             = False,
        sdram_model            = "sipeed",
        sdram_rate             = "1:2",
        with_pcie              = False,
        with_led_chaser        = True,
        with_rgb_led           = False,
        with_buttons           = True,
        **kwargs):
        platform = sipeed_tang_mega_138k.Platform(toolchain="gowin")

        assert not with_sdram or (sdram_model in ["sipeed", "mister"])

        if with_sdram:
            platform.add_extension({
                "sipeed": sipeed_tang_mega_138k_pro.sipeedSDRAM(),
                "mister": sipeed_tang_mega_138k_pro.misterSDRAM()}[sdram_model]
            )

        # CRG --------------------------------------------------------------------------------------
        cpu_clk_freq = int(800e6) if kwargs["cpu_type"] == "gowin_ae350" else 0
        self.crg = _CRG(platform, sys_clk_freq, cpu_clk_freq,
            with_sdram     = with_sdram,
            with_ddr3      = with_ddr3,
            with_video_pll = with_video_terminal or with_video_framebuffer or with_video_colorbars,
            with_pcie      = with_pcie,
            with_ethernet  = with_ethernet or with_etherbone
        )

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Tang Mega 138K", **kwargs)
        if cpu_clk_freq:
            self.add_config("CPU_CLK_FREQ", cpu_clk_freq)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if with_ddr3 and not self.integrated_main_ram_size:
            self.ddrphy = GW5DDRPHY(
                pads         = platform.request("ddram"),
                sys_clk_freq = sys_clk_freq
            )
            self.ddrphy.settings.rtt_nom = "disabled"
            self.comb += self.crg.stop.eq(self.ddrphy.init.stop)
            self.comb += self.crg.reset.eq(self.ddrphy.init.reset)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT41J256M16(sys_clk_freq, "1:2"),
                l2_cache_size = 0#kwargs.get("l2_size", 8192)
            )

        # Video ------------------------------------------------------------------------------------
        if with_video_terminal or with_video_framebuffer or with_video_colorbars:
            hdmi_pads = platform.request("hdmi")
            self.comb += hdmi_pads.hdp.eq(1)
            self.videophy = VideoGowinHDMIPHY(hdmi_pads, clock_domain="hdmi")
            if with_video_colorbars:
                self.add_video_colorbars(phy=self.videophy, timings="640x480@60Hz", clock_domain="hdmi")
            if with_video_terminal:
                self.add_video_terminal(phy=self.videophy, timings="640x480@75Hz", clock_domain="hdmi")
            if with_video_framebuffer:
                self.add_video_framebuffer(phy=self.videophy, timings="640x480@75Hz", clock_domain="hdmi")

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("led"),
                sys_clk_freq = sys_clk_freq
            )

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            self.ethphy = LiteEthPHYRGMII(
                clock_pads = self.platform.request("eth_clocks"),
                pads       = self.platform.request("eth"))
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy,
                    ip_address  = local_ip,
                    with_ethmac = with_ethernet,
                    data_with   = 32
                )
            elif with_ethernet:
                self.add_ethernet(phy=self.ethphy,
                    dynamic_ip     = eth_dynamic_ip,
                    local_ip       = local_ip,
                    remote_ip      = remote_ip,
                    data_width     = 32,
                    software_debug = False)

        # SDR SDRAM --------------------------------------------------------------------------------
        if with_sdram and not self.integrated_main_ram_size:
            module_cls = {
                "sipeed": W9825G6KH6,
                "mister": AS4C32M16}[sdram_model]
            if sdram_rate == "1:2":
                sdrphy_cls = HalfRateGENSDRPHY
            else:
                sdrphy_cls = GENSDRPHY
            self.sdrphy = sdrphy_cls(platform.request("sdram"), sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.sdrphy,
                module        = module_cls(sys_clk_freq, sdram_rate),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # PCIe -------------------------------------------------------------------------------------
        if with_pcie:
            self.pcie_phy = GW5APCIEPHY(platform, platform.request("pcie"), nlanes=4, cd="sys")
            self.add_pcie(phy=self.pcie_phy, ndmas=1, data_width=256)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=sipeed_tang_mega_138k.Platform, description="LiteX SoC on Tang Mega 138K.")
    parser.add_target_argument("--flash",           action="store_true",      help="Flash Bitstream.")
    parser.add_target_argument("--sys-clk-freq",    default=50e6, type=float, help="System clock frequency.")

    # Memory.
    parser.add_target_argument("--with-ddr3",       action="store_true",      help="Enable optional DDR3 module.")
    parser.add_target_argument("--with-sdram",      action="store_true",      help="Enable optional SDRAM module.")
    parser.add_target_argument("--sdram-model",     default="sipeed",         help="SDRAM module model.",
        choices=[
            "sipeed",
            "mister"
    ])

    # Video.
    viopts = parser.add_mutually_exclusive_group()
    viopts.add_argument("--with-video-colorbars",   action="store_true",      help="Enable Video ColoBars (HDMI).")
    viopts.add_argument("--with-video-terminal",    action="store_true",      help="Enable Video Terminal (HDMI).")
    viopts.add_argument("--with-video-framebuffer", action="store_true",      help="Enable Video Framebuffer (HDMI).")

    # Ethernet.
    parser.add_target_argument("--with-ethernet",   action="store_true",      help="Enable Ethernet support.")
    parser.add_target_argument("--with-etherbone",  action="store_true",      help="Enable Etherbone support.")
    parser.add_target_argument("--eth-dynamic-ip",  action="store_true",      help="Enable dynamic Ethernet IP addresses setting.")
    parser.add_target_argument("--remote-ip",       default="192.168.1.100",  help="Remote IP address of TFTP server.")
    parser.add_target_argument("--local-ip",        default="192.168.1.50",   help="Local IP address.")

    # PCIe.
    parser.add_target_argument("--with-pcie",       action="store_true",      help="Enable PCIe support.")

    args = parser.parse_args()

    assert not (args.with_etherbone and args.eth_dynamic_ip)

    soc = BaseSoC(
        sys_clk_freq           = args.sys_clk_freq,
        with_video_colorbars   = args.with_video_colorbars,
        with_video_terminal    = args.with_video_terminal,
        with_video_framebuffer = args.with_video_framebuffer,
        with_ddr3              = args.with_ddr3,
        with_sdram             = args.with_sdram,
        sdram_model            = args.sdram_model,
        with_pcie              = args.with_pcie,
        with_ethernet          = args.with_ethernet,
        with_etherbone         = args.with_etherbone,
        local_ip               = args.local_ip,
        remote_ip              = args.remote_ip,
        eth_dynamic_ip         = args.eth_dynamic_ip,
        **parser.soc_argdict
    )

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.with_pcie:
        generate_litepcie_software_headers(soc, os.path.join(builder.output_dir, "driver"))

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.flash(0, builder.get_bitstream_filename(mode="flash", ext=".fs"), external=True)

if __name__ == "__main__":
    main()
