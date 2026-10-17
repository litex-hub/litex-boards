#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 Samuele Baisi <samuele.baisi@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

# Notes:
# - default clock set to 100MHz, above that timings start to crap out

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from litex_boards.platforms import myir_myc_j7a100t

from litex.soc.cores.clock import *
from litex.soc.integration.soc import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.bitbang import I2CMaster
from litex.soc.cores.video import video_data_layout, video_framebuffer_size
from litex.soc.cores.video import VideoTimingGenerator, VideoFrameBuffer
from litex.soc.interconnect import stream
from litex.build.io import SDROutput, DDROutput

# DDR 3
from litedram.modules import MT41J128M16
from litedram.phy import s7ddrphy

# ETH
from liteeth.phy.s7rgmii import LiteEthPHYRGMII

#PCIe
from litepcie.phy.s7pciephy import S7PCIEPHY
from litepcie.software import generate_litepcie_software

from litespi.spi_nor_flash_module import SpiNorFlashModule
from litespi.opcodes import SpiNorFlashOpCodes as Codes
from litespi.ids import SpiNorFlashManufacturerIDs

#sfp+
from liteeth.phy.a7_gtp import QPLLSettings, QPLL
from liteeth.phy import A7_1000BASEX


# Video modes (CEA-861) ----------------------------------------------------------------------------

# LiteX's built-in "1280x720@60Hz" entry has front/back porch swapped (h_sync_offset=220): CEA-861
# 720p60 is front porch 110, sync 40, back porch 220. Both modes below were validated on hardware
# with a bench.
video_modes = {
    "720p": ("1280x720@60Hz", {
        "pix_clk"       : 74.25e6,
        "h_active"      : 1280,
        "h_blanking"    : 370,
        "h_sync_offset" : 110,
        "h_sync_width"  : 40,
        "v_active"      : 720,
        "v_blanking"    : 30,
        "v_sync_offset" : 5,
        "v_sync_width"  : 5,
    }),
    "1080p": ("1920x1080@60Hz", {
        "pix_clk"       : 148.5e6,
        "h_active"      : 1920,
        "h_blanking"    : 280,
        "h_sync_offset" : 88,
        "h_sync_width"  : 44,
        "v_active"      : 1080,
        "v_blanking"    : 45,
        "v_sync_offset" : 4,
        "v_sync_width"  : 5,
    }),
}

# SiI9022A HDMI transmitter ------------------------------------------------------------------------

class SiI9022PHY(LiteXModule):
    """Parallel 24-bit RGB to the SiI9022A. The pixel clock is forwarded through an ODDR, inverted
    so that data (registered in the IOBs on the rising edge) is stable at the rising edge the
    SiI9022A samples on (TPI 0x08[4] = 1)."""
    def __init__(self, pads, clock_domain="hdmi"):
        self.sink = sink = stream.Endpoint(video_data_layout)

        # # #

        cd = ClockSignal(clock_domain)
        self.comb += sink.ready.eq(1)
        self.specials += DDROutput(i1=0, i2=1, o=pads.clk, clk=cd)
        self.specials += SDROutput(i=sink.de,    o=pads.de,    clk=cd)
        self.specials += SDROutput(i=sink.hsync, o=pads.hsync, clk=cd)
        self.specials += SDROutput(i=sink.vsync, o=pads.vsync, clk=cd)
        for i in range(8):
            self.specials += SDROutput(i=sink.r[i] & sink.de, o=pads.r[i], clk=cd)
            self.specials += SDROutput(i=sink.g[i] & sink.de, o=pads.g[i], clk=cd)
            self.specials += SDROutput(i=sink.b[i] & sink.de, o=pads.b[i], clk=cd)

SII9022_I2C_ADDR = 0x3b # 7-bit (CI2CA pulled up on the carrier). 0x76 is the 8-bit form.

def sii9022_init_sequence(timings):
    """TPI write sequence (validated on hardware), executed by the BIOS at boot via I2CMaster.add_init.
    DVI mode (no AVI InfoFrame needed)."""
    t       = timings[1]
    pclk    = int(round(t["pix_clk"]/10e3))   # Pixel clock / 10kHz.
    vfreq   = 6000                             # Vertical frequency (vendor convention, x0.01Hz).
    h_total = t["h_active"] + t["h_blanking"]
    v_total = t["v_active"] + t["v_blanking"]
    return [
        (0xc7, 0x00),                                       # TPI mode (must be the first write).
        (0x1e, 0x00),                                       # Power state D0.
        (0xbc, 0x01), (0xbd, 0x82), (0xbe, 0x25),           # Source termination (0x24 after reset | 1).
        (0x1a, 0x10),                                       # TMDS off, DVI mode.
        (0x09, 0x00),                                       # Input format: RGB.
        (0x0a, 0x00),                                       # Output format: RGB.
        *[(reg, 0x00) for reg in range(0x0c, 0x1a)],        # AVI InfoFrame cleared (DVI).
        (0x00, pclk & 0xff),    (0x01, pclk >> 8),          # Video mode (committed on 0x07 write).
        (0x02, vfreq & 0xff),   (0x03, vfreq >> 8),
        (0x04, h_total & 0xff), (0x05, h_total >> 8),
        (0x06, v_total & 0xff), (0x07, v_total >> 8),
        (0x1a, 0x00),                                       # TMDS on, DVI mode.
        (0x08, 0x70),                                       # x1, full pixel, rising edge (after 0x1A[4] 1->0).
    ]

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_dram=True, with_video_pll=False, with_video_in_pll=False, with_rst=True,
        video_pix_clk = 74.25e6):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()
        #self.cd_eth = ClockDomain()
        if with_dram:
            self.cd_sys4x     = ClockDomain()
            self.cd_sys4x_dqs = ClockDomain()
            self.cd_idelay    = ClockDomain()

        # # #

        # Clk/Rst.
        clk200 = platform.request("clk200")

        rst    = ~platform.request("rst_n") if with_rst else 0

        # PLL.
        self.pll = pll = S7PLL(speedgrade=-2)
        self.comb += pll.reset.eq(rst | self.rst)
        pll.register_clkin(clk200, 200e6)
        if with_video_pll:
            # SiI9022A power-on reset: the chip does not answer on I2C unless RESETn is pulsed with
            # supplies stable (RESETn only has a pull-up on the carrier). Pulse it low for 10ms after
            # configuration and keep the SoC (CPU/BIOS, which runs the I2C init) in reset for 50ms
            # more, from a free-running reset-less domain.
            pll.create_clkout(self.cd_sys, sys_clk_freq, with_reset=False)
            self.cd_por = ClockDomain(reset_less=True)
            pll.create_clkout(self.cd_por, 25e6, with_reset=False)
            por_rst_cycles  = int(25e6*10e-3)
            por_done_cycles = int(25e6*60e-3)
            por_count       = Signal(max=por_done_cycles + 1)
            por_done        = Signal()
            self.hdmi_rst_n = Signal()
            self.sync.por += If(por_count != por_done_cycles, por_count.eq(por_count + 1))
            self.comb += [
                self.hdmi_rst_n.eq(por_count >= por_rst_cycles),
                por_done.eq(por_count == por_done_cycles),
            ]
            self.specials += AsyncResetSynchronizer(self.cd_sys, ~pll.locked | ~por_done)
        else:
            pll.create_clkout(self.cd_sys, sys_clk_freq)

        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.
        if with_dram:
            self.dram_pll = dram_pll = S7PLL(speedgrade=-2)
            dram_pll.register_clkin(self.cd_sys.clk, sys_clk_freq)
            dram_pll.create_clkout(self.cd_sys4x,     4*sys_clk_freq)
            dram_pll.create_clkout(self.cd_sys4x_dqs, 4*sys_clk_freq, phase=90)
            dram_pll.create_clkout(self.cd_idelay,    200e6)

            # IdelayCtrl.
            self.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

        # Video PLL (MMCM with fractional multiplier: exact 74.25/148.5MHz from 200MHz).
        if with_video_pll:
            self.cd_hdmi = ClockDomain()
            self.video_pll = video_pll = S7MMCM(speedgrade=-2)
            self.comb += video_pll.reset.eq(rst | self.rst)
            video_pll.register_clkin(pll.clkin, 200e6)
            video_pll.create_clkout(self.cd_hdmi, video_pix_clk, margin=0)
            platform.add_false_path_constraints(self.cd_sys.clk, self.cd_hdmi.clk)

# SPI Flash ----------------------------------------------------------------------------------------

class MX25L25673G(SpiNorFlashModule):
    # Macronix 256Mbit (32MB) Flash, the part the Vivado programmer uses (mx25l25673g-spi-x1_x2_x4).
    # Not in litespi's module list: same family as MX25L25645G, but with the 4-byte Quad Output
    # read (0x6C) so the full 32MB is reachable in 4x mode.
    manufacturer_id = SpiNorFlashManufacturerIDs.MACRONIX
    device_id       = 0x2019
    name            = "mx25l25673g"

    total_size  = 33554432 # bytes
    page_size   =      256 # bytes
    total_pages =   131072

    supported_opcodes = [
        Codes.READ_1_1_1,
        Codes.READ_1_1_1_FAST,
        Codes.READ_1_1_4,
        Codes.PP_1_1_1,
        Codes.READ_1_1_1_4B,
        Codes.READ_1_1_1_FAST_4B,
        Codes.READ_1_1_4_4B,
        Codes.PP_1_1_1_4B,
    ]
    erase_commands = [
        (Codes.SE_4B,    64*1024, 32),
        (Codes.BE_4K_4B,  4*1024, 32),
    ]
    dummy_bits  = 8
    quad_enable = "wrsr_sr1_bit6" # QE is SR1 bit 6; already set when Vivado programs the Flash in x4.

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, toolchain="vivado", sys_clk_freq=100e6,
        with_ethernet   = False,
        with_etherbone  = False,
        eth_ip          = "192.168.1.50",
        remote_ip       = None,
        eth_dynamic_ip  = False,
        with_led_chaser = True,
        with_spi_flash  = False,
        with_sdram_256  = False,
        with_pcie       = False,
        with_sfp        = False,
        sfp_autoneg     = True,
        with_video_colorbars   = False,
        with_video_terminal    = False,
        with_video_framebuffer = False,
        video_mode             = "720p",
        **kwargs):
        platform = myir_myc_j7a100t.Platform(toolchain=toolchain)

        # CRG --------------------------------------------------------------------------------------
        with_dram = (kwargs.get("integrated_main_ram_size", 0) == 0)
        with_video = with_video_colorbars or with_video_terminal or with_video_framebuffer
        video_timings = video_modes[video_mode]
        self.crg  = _CRG(platform, sys_clk_freq, with_dram,
            with_video_pll = with_video,
            video_pix_clk  = video_timings[1]["pix_clk"],
        )

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on MYiR MYC-J7A100T.", **kwargs)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            if (with_sdram_256):
                self.ddrphy = s7ddrphy.A7DDRPHY(platform.request("ddram", 0),
                    memtype        = "DDR3",
                    nphases        = 4,
                    sys_clk_freq   = sys_clk_freq)
            else:
                self.ddrphy = s7ddrphy.A7DDRPHY(platform.request("ddram", 1),
                    memtype        = "DDR3",
                    nphases        = 4,
                    sys_clk_freq   = sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT41J128M16(sys_clk_freq, "1:4"),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # SPI Flash --------------------------------------------------------------------------------
        if with_spi_flash:
            self.add_spi_flash(mode="4x", module=MX25L25673G(Codes.READ_1_1_4_4B), rate="1:1", with_master=True)

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            self.ethphy = LiteEthPHYRGMII(
                clock_pads = self.platform.request("eth_clocks", 0),
                pads       = self.platform.request("eth", 0))
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, ip_address=eth_ip, with_ethmac=with_ethernet)
            elif with_ethernet:
                self.add_ethernet(phy=self.ethphy, dynamic_ip=eth_dynamic_ip, local_ip=eth_ip, remote_ip=remote_ip)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq,
            )
        
        # PCIe -------------------------------------------------------------------------------------
        if with_pcie:
            assert self.csr_data_width == 32

            self.pcie_phy = S7PCIEPHY(platform, platform.request("pcie_x2"),
                data_width  = 64,
                refclk_freq = 100e6,
            )
            self.pcie_phy.add_gt_loc_constraints(["GTPE2_CHANNEL_X0Y4", "GTPE2_CHANNEL_X0Y5"], by_pipe_lane=True)
            self.pcie_phy.update_config({"PCIe_Blk_Locn": "X0Y0"})

            self.add_pcie(phy=self.pcie_phy,
                          ndmas=1,
             )

        # GTP Quad / QPLL (PCIe & SFP shared GTPE2_COMMON) -----------------------------------------
        if with_pcie or with_sfp:
            # SFP QPLL settings (125MHz RefClk -> 2.5GHz VCO -> 1.25Gbps line rate).
            if with_sfp:
                qpll_sfp_settings = QPLLSettings(
                    refclksel  = 0b010, # Select GTREFCLK1 (F10/E10).
                    fbdiv      = 4,
                    fbdiv_45   = 5,
                    refclk_div = 1,
                )
                refclk125    = platform.request("gtp_refclk", 1)
                refclk125_se = Signal()
                self.specials += Instance("IBUFDS_GTE2",
                    i_CEB          = 0,
                    i_I            = refclk125.p,
                    i_IB           = refclk125.n,
                    o_O            = refclk125_se,
                    p_CLKSWING_CFG = 0b11,
                )

            # PCIe QPLL settings (100MHz RefClk -> 2.5GHz VCO).
            if with_pcie:
                qpll_pcie_settings = QPLLSettings(
                    refclksel  = 0b001, # Select GTREFCLK0 (F6/E6).
                    fbdiv      = 5,
                    fbdiv_45   = 5,
                    refclk_div = 1,
                )

            # Quad 216 has a single GTPE2_COMMON_X0Y1 block shared by all 4 channels:
            # - Channel 0 (X0Y4): PCIe Lane 0
            # - Channel 1 (X0Y5): PCIe Lane 1
            # - Channel 2 (X0Y6): SFP 0
            # - Channel 3 (X0Y7): SFP 1
            if with_pcie and with_sfp:
                # Both PCIe and SFP active: share the single GTPE2_COMMON.
                # PLL0 is dedicated to PCIe, PLL1 is dedicated to SFP.
                self.qpll = qpll = QPLL(
                    gtrefclk0     = self.pcie_phy.pcie_refclk,
                    qpllsettings0 = qpll_pcie_settings,
                    gtrefclk1     = refclk125_se,
                    qpllsettings1 = qpll_sfp_settings,
                )
                self.pcie_phy.use_external_qpll(qpll_channel=qpll.channels[0])
                sfp_qpll_channel = qpll.channels[1]
            elif with_sfp:
                # SFP standalone: PLL0 clocked from GTREFCLK1.
                self.qpll = qpll = QPLL(
                    gtrefclk1     = refclk125_se,
                    qpllsettings0 = qpll_sfp_settings,
                )
                sfp_qpll_channel = qpll.channels[0]

        # SFP Ethernet -----------------------------------------------------------------------------
        if with_sfp:
            sfp_pads = platform.request("sfp", 0)

            # PCS status CSR (sfpethphy_pcs_status): bit 0 link_up, bit 1 is_sgmii, bits 16-31 link
            # partner config word (0 if the partner does not autonegotiate).
            pcs_kwargs = {"with_csr": True, "sys_clk_freq": sys_clk_freq}
            if not sfp_autoneg:
                # 1000BASE-X without Clause 37 autoneg, for partners with a forced 1G SerDes.
                pcs_kwargs.update(with_autoneg=False, sgmii=False)
            self.sfpethphy = A7_1000BASEX(
                qpll_channel = sfp_qpll_channel,
                data_pads    = sfp_pads,
                sys_clk_freq = sys_clk_freq,
                pcs_kwargs   = pcs_kwargs,
            )

            # Transceiver location constraints (SFP 0 -> Channel 2 / X0Y6).
            platform.add_platform_command("set_property LOC GTPE2_CHANNEL_X0Y6 [get_cells -hierarchical -filter {{NAME =~ *sfpethphy* && (ORIG_REF_NAME == GTPE2_CHANNEL || REF_NAME == GTPE2_CHANNEL)}}]")
            platform.add_platform_command("set_property LOC GTPE2_COMMON_X0Y1 [get_cells -hierarchical -filter {{ORIG_REF_NAME == GTPE2_COMMON || REF_NAME == GTPE2_COMMON}}]")

            self.add_ethernet(phy=self.sfpethphy, dynamic_ip=eth_dynamic_ip, local_ip=eth_ip, remote_ip=remote_ip)


        # Video (HDMI out, SiI9022A) ---------------------------------------------------------------
        if with_video:
            hdmi_pads = platform.request("hdmi_out")
            self.comb += hdmi_pads.rst_n.eq(self.crg.hdmi_rst_n) # Power-on reset pulse (see _CRG).
            self.videophy = SiI9022PHY(hdmi_pads, clock_domain="hdmi")
            self.videoi2c = I2CMaster(hdmi_pads)
            self.videoi2c.add_init(addr=SII9022_I2C_ADDR, init=sii9022_init_sequence(video_timings))
            if with_video_colorbars:
                self.add_video_colorbars(phy=self.videophy, timings=video_timings, clock_domain="hdmi")
            if with_video_terminal:
                self.add_video_terminal(phy=self.videophy, timings=video_timings, clock_domain="hdmi")
            if with_video_framebuffer:
                self.add_video_framebuffer_wide_cdc(phy=self.videophy, timings=video_timings, clock_domain="hdmi")

    def add_video_framebuffer_wide_cdc(self, phy, timings, clock_domain, name="video_framebuffer", format="rgb888"):
        # Same as SoC.add_video_framebuffer, but always crosses to the video domain at the DRAM port
        # width (8 pixels per FIFO entry) and converts to pixels there. LiteX only does this when
        # pix_clk >= sys_clk; otherwise it converts in sys and crosses one pixel per entry through a
        # 4-entry AsyncFIFO, whose round-trip latency caps it below 1 pixel per pix_clk (~0.84 at
        # 74.25MHz/100MHz in simulation). The pipe then underflows during active video, the VTG
        # stalls, hsync/vsync become irregular and the monitor reports no signal.
        _, hres, vres = parse_video_timing_resolution(timings)
        region  = self._get_video_framebuffer_region(name=name, size=video_framebuffer_size(hres, vres, format))
        port, _ = self._get_video_framebuffer_dma_port()
        vtg = VideoTimingGenerator(default_video_timings=timings[1])
        vtg = ClockDomainsRenamer(clock_domain)(vtg)
        vfb = VideoFrameBuffer(port,
            hres                  = hres,
            vres                  = vres,
            base                  = region.origin,
            format                = format,
            clock_domain          = clock_domain,
            clock_faster_than_sys = True,
        )
        self.bus.add_region(name, region)
        self.add_module(name=f"{name}_vtg", module=vtg)
        self.add_module(name=name, module=vfb)
        self.comb += vtg.source.connect(vfb.vtg_sink)
        self.comb += vfb.source.connect(phy.sink)
        self.add_constant("VIDEO_FRAMEBUFFER_BASE",  region.origin)
        self.add_constant("VIDEO_FRAMEBUFFER_HRES",  hres)
        self.add_constant("VIDEO_FRAMEBUFFER_VRES",  vres)
        self.add_constant("VIDEO_FRAMEBUFFER_DEPTH", vfb.depth)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=myir_myc_j7a100t.Platform, description="LiteX SoC on MYiR MYC-J7A100T.")
    parser.add_target_argument("--flash",          action="store_true",       help="Flash bitstream.")
    parser.add_target_argument("--sys-clk-freq",   default=100e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-ethernet",  action="store_true",       help="Enable Ethernet support.")
    parser.add_target_argument("--with-etherbone", action="store_true",       help="Enable Etherbone support.")
    parser.add_target_argument("--eth-ip",         default="192.168.1.50",    help="Ethernet/Etherbone IP address.")
    parser.add_target_argument("--remote-ip",      default="192.168.1.100",   help="Remote IP address of TFTP server.")
    parser.add_target_argument("--eth-dynamic-ip", action="store_true",       help="Enable dynamic Ethernet IP assignment.")
    parser.add_target_argument("--with-spi-flash", action="store_true",       help="Enable SPI Flash (MMAPed).")
    parser.add_target_argument("--with-sdram-256", action="store_true",       help="Enable a single DDR chip only (256MB)")
    sdopts = parser.target_group.add_mutually_exclusive_group()
    sdopts.add_argument(       "--with-spi-sdcard",action="store_true",       help="Enable SPI-mode SDCard support.")
    sdopts.add_argument(       "--with-sdcard",    action="store_true",       help="Enable SDCard support.")
    parser.add_target_argument("--driver",         action="store_true",       help="Generate PCIe driver.")
    parser.add_target_argument("--with-pcie",      action="store_true",       help="Enable basic PCIe DMA")
    parser.add_target_argument("--sfp-no-autoneg", action="store_true",       help="SFP Ethernet: 1000BASE-X without autonegotiation.")
    parser.add_target_argument("--with-sfp",      action="store_true",       help="Enable SFP Ethernet support.")
    viopts = parser.target_group.add_mutually_exclusive_group()
    viopts.add_argument("--with-video-colorbars",   action="store_true", help="Enable HDMI out color bars.")
    viopts.add_argument("--with-video-terminal",    action="store_true", help="Enable HDMI out video terminal.")
    viopts.add_argument("--with-video-framebuffer", action="store_true", help="Enable HDMI out video framebuffer.")
    parser.add_target_argument("--video-mode",     default="720p", choices=["720p", "1080p"], help="HDMI out video mode.")
    args = parser.parse_args()

    #assert not (args.with_etherbone and args.eth_dynamic_ip)

    soc = BaseSoC(
        toolchain      = args.toolchain,
        sys_clk_freq   = args.sys_clk_freq,
        with_ethernet  = args.with_ethernet,
        with_etherbone = args.with_etherbone,
        eth_ip         = args.eth_ip,
        remote_ip      = args.remote_ip,
        eth_dynamic_ip = args.eth_dynamic_ip,
        with_sdram_256 = args.with_sdram_256,
        with_spi_flash = args.with_spi_flash,
        with_pcie      = args.with_pcie,
        with_sfp       = args.with_sfp,
        sfp_autoneg    = not args.sfp_no_autoneg,
        with_video_colorbars   = args.with_video_colorbars,
        with_video_terminal    = args.with_video_terminal,
        with_video_framebuffer = args.with_video_framebuffer,
        video_mode             = args.video_mode,
        **parser.soc_argdict
    )

    if args.with_spi_sdcard:
        soc.add_spi_sdcard()
    if args.with_sdcard:
        soc.add_sdcard()

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.flash(0, builder.get_bitstream_filename(mode="flash"))
    
    if args.with_pcie and args.driver:
        generate_litepcie_software(soc, os.path.join(builder.output_dir, "driver"))

if __name__ == "__main__":
    main()
