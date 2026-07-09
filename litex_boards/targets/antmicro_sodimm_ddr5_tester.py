#!/usr/bin/env python3
#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 LiteX-Hub community
# SPDX-License-Identifier: BSD-2-Clause

import importlib
import math

from migen import *

from litex.gen import *

from litex_boards.platforms import antmicro_sodimm_ddr5_tester

from litex.soc.cores.bitbang import I2CMaster
from litex.soc.cores.clock import *
from litex.soc.cores.gpio import GPIOIn, GPIOOut
from litex.soc.cores.led import LedChaser
from litex.soc.cores.video import VideoS7HDMIPHY
from litex.soc.integration.builder import *
from litex.soc.integration.soc import *

from liteeth.phy import LiteEthS7PHYRGMII

from litespi.modules import S25FL128S0
from litespi.opcodes import SpiNorFlashOpCodes as Codes

DDR5_LITEDRAM_ERROR = (
    "Antmicro DDR5 targets require a LiteDRAM checkout with litedram.phy.ddr5 "
    "and DDR5 module definitions. Antmicro's known DDR5-capable reference is "
    "https://github.com/antmicro/litedram/tree/0f1592b3534dc2b8ae74c9bf3151c777ba24b49a."
)


class DDR5DependencyError(ImportError):
    pass


def get_ddr5_support(module_name):
    try:
        ddr5 = importlib.import_module("litedram.phy.ddr5")
        modules = importlib.import_module("litedram.modules")
        module_cls = getattr(modules, module_name)
    except (AttributeError, ImportError) as e:
        raise DDR5DependencyError(DDR5_LITEDRAM_ERROR) from e
    return ddr5, module_cls


# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, iodelay_clk_freq, with_video_pll=False):
        self.rst              = Signal()
        self.cd_sys           = ClockDomain()
        self.cd_sys2x         = ClockDomain(reset_less=True)
        self.cd_idelay        = ClockDomain()
        self.cd_sys4x_raw     = ClockDomain(reset_less=True)
        self.cd_sys4x_90_raw  = ClockDomain(reset_less=True)
        self.cd_sys2x_rst     = ClockDomain()
        self.cd_sys2x_90_rst  = ClockDomain()

        # # #

        clk100 = platform.request("clk100")

        self.mmcm = mmcm = S7MMCM(speedgrade=-3)
        self.comb += mmcm.reset.eq(self.rst)
        mmcm.register_clkin(clk100, 100e6)
        mmcm.create_clkout(self.cd_sys4x_raw,    4*sys_clk_freq, buf=None, with_reset=False)
        mmcm.create_clkout(self.cd_sys4x_90_raw, 4*sys_clk_freq, phase=90, buf=None, with_reset=False)
        mmcm.create_clkout(self.cd_sys2x_rst,    2*sys_clk_freq, buf="bufr")
        mmcm.create_clkout(self.cd_sys2x_90_rst, 2*sys_clk_freq, phase=90, buf="bufr")
        mmcm.create_clkout(self.cd_sys,          sys_clk_freq)
        mmcm.create_clkout(self.cd_sys2x,        2*sys_clk_freq)

        self.pll_iodly = pll_iodly = S7PLL(speedgrade=-3)
        self.comb += pll_iodly.reset.eq(self.rst)
        pll_iodly.register_clkin(clk100, 100e6)
        pll_iodly.create_clkout(self.cd_idelay, iodelay_clk_freq)

        self.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

        if with_video_pll:
            self.cd_hdmi   = ClockDomain()
            self.cd_hdmi5x = ClockDomain()

            self.video_pll = video_pll = S7MMCM(speedgrade=-3)
            self.comb += video_pll.reset.eq(self.rst)
            video_pll.register_clkin(clk100, 100e6)
            video_pll.create_clkout(self.cd_hdmi,   40e6)
            video_pll.create_clkout(self.cd_hdmi5x, 5*40e6)


# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, *, sys_clk_freq=200e6, iodelay_clk_freq=200e6,
        with_ethernet          = False,
        with_etherbone         = False,
        eth_ip                 = "192.168.1.50",
        remote_ip              = None,
        eth_reset_time         = "10e-3",
        eth_dynamic_ip         = False,
        with_hyperram          = False,
        hyperram_init_latency  = 3,
        hyperram_init_drive_strength = 34,
        with_sdcard            = False,
        with_spi_flash         = False,
        with_led_chaser        = True,
        with_video_colorbars   = False,
        with_video_terminal    = False,
        with_video_framebuffer = False,
        **kwargs):
        platform = antmicro_sodimm_ddr5_tester.Platform()

        # CRG --------------------------------------------------------------------------------------
        with_video_pll = with_video_colorbars or with_video_terminal or with_video_framebuffer
        self.crg = _CRG(platform, sys_clk_freq,
            iodelay_clk_freq = iodelay_clk_freq,
            with_video_pll   = with_video_pll,
        )

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Antmicro SO-DIMM DDR5 Tester", **kwargs)

        # DDR5 SDRAM SO-DIMM -----------------------------------------------------------------------
        platform.add_platform_command("set_property CLOCK_BUFFER_TYPE BUFG [get_nets sys_rst]")
        platform.add_platform_command(
            "set_disable_timing -from WRCLK -to RST "
            "[get_cells -filter {{(REF_NAME == FIFO18E1 || REF_NAME == FIFO36E1) && EN_SYN == FALSE}}]"
        )
        platform.add_platform_command(
            "set_max_delay -quiet -to [get_pins -hierarchical -regexp BUFR.*/CLR] 10.0"
        )
        platform.add_platform_command(
            "set_max_delay -quiet "
            "-from [get_clocks -of_objects [get_pins rst_domain/O]] "
            "-to [list [get_pins -hierarchical -regexp .*CLR.*] "
            "[get_pins -hierarchical -regexp .*PRE.*]] 10.0"
        )
        platform.toolchain.pre_synthesis_commands.append(
            "set_property strategy Congestion_SpreadLogic_high [get_runs impl_1]"
        )

        if not self.integrated_main_ram_size:
            ddr5, module_cls = get_ddr5_support("MTC8C1084S1SC48BA1_BC")
            self.phycrg = phycrg = ddr5.S7PHYCRG(
                reset_clock_domain    = "sys2x_rst",
                reset_clock_90_domain = "sys2x_90_rst",
                source_4x             = ClockSignal("sys4x_raw"),
                source_4x_90          = ClockSignal("sys4x_90_raw"),
            )
            phycrg.create_clock_domains(
                clock_domains = ["sys_io", "sys2x_io", "sys2x_90_io", "sys4x_io", "sys4x_90_io"],
                io_banks      = ["bank32", "bank33", "bank34"],
            )
            self.ddrphy = ddr5.K7DDR5PHY(platform.request("ddr5"),
                crg                = phycrg,
                iodelay_clk_freq   = iodelay_clk_freq,
                sys_clk_freq       = sys_clk_freq,
                with_sub_channels  = True,
                direct_control     = False,
                with_per_dq_idelay = True,
                pin_domains        = self.get_ddr_pin_domains(),
                pin_banks          = platform.pin_bank_mapping()["ddr5"],
            )
            self.add_sdram("sdram",
                phy                     = self.ddrphy,
                module                  = module_cls(sys_clk_freq, "1:4"),
                l2_cache_size           = kwargs.get("l2_size", 8192),
                l2_cache_min_data_width = 256,
                size                    = 0x40000000,
            )

        # HyperRAM ---------------------------------------------------------------------------------
        if with_hyperram:
            self.add_hyperram(
                origin = 0x20000000,
                size   = 8*MEGABYTE,
            )
            self.add_config("HYPERRAM_INIT_LATENCY", hyperram_init_latency)
            self.add_config("HYPERRAM_INIT_DRIVE_STRENGTH", hyperram_init_drive_strength)

        # SD Card ----------------------------------------------------------------------------------
        if with_sdcard:
            self.add_sdcard()

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            self.ethphy = LiteEthS7PHYRGMII(
                clock_pads      = self.platform.request("eth_clocks"),
                pads            = self.platform.request("eth"),
                rx_delay        = 0.8e-9,
                hw_reset_cycles = math.ceil(float(eth_reset_time) * self.sys_clk_freq),
            )
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, ip_address=eth_ip, with_ethmac=with_ethernet)
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy, dynamic_ip=eth_dynamic_ip, local_ip=eth_ip, remote_ip=remote_ip)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq,
            )

        # Video ------------------------------------------------------------------------------------
        if with_video_colorbars or with_video_terminal or with_video_framebuffer:
            self.videophy = VideoS7HDMIPHY(platform.request("hdmi_out"), clock_domain="hdmi")
            if with_video_colorbars:
                self.add_video_colorbars(phy=self.videophy, timings="800x600@60Hz", clock_domain="hdmi")
            if with_video_terminal:
                self.add_video_terminal(phy=self.videophy, timings="800x600@60Hz", clock_domain="hdmi")
            if with_video_framebuffer:
                self.add_video_framebuffer(phy=self.videophy, timings="800x600@60Hz", clock_domain="hdmi")

        # SPI Flash --------------------------------------------------------------------------------
        if with_spi_flash:
            self.add_spi_flash(mode="4x", module=S25FL128S0(Codes.READ_1_1_4), with_master=True)

        # I2C --------------------------------------------------------------------------------------
        self.i2c          = I2CMaster(platform.request("i2c_ddr"), default_dev=True)
        self.platform_i2c = I2CMaster(platform.request("i2c_platform"))

        # SO-DIMM control --------------------------------------------------------------------------
        sodimm_gpio_in = Signal(3)
        self.comb += [
            sodimm_gpio_in[0].eq(platform.request("pwr_good")),
            sodimm_gpio_in[1].eq(platform.request("tb_detect")),
            sodimm_gpio_in[2].eq(platform.request("ddr_presence_n")),
        ]
        self.sodimm_gpio_in = GPIOIn(sodimm_gpio_in)

        sodimm_gpio_out = Signal(4)
        self.comb += [
            platform.request("pwr_en").eq(sodimm_gpio_out[0]),
            platform.request("LED_yellow").eq(sodimm_gpio_out[1]),
            platform.request("LED_red").eq(sodimm_gpio_out[2]),
            platform.request("LED_green").eq(sodimm_gpio_out[3]),
        ]
        self.sodimm_gpio_out = GPIOOut(sodimm_gpio_out)

    def get_ddr_pin_domains(self):
        return dict(
            A_ck_t  = (("sys2x_io",    "sys4x_io"),    None),
            A_ck_c  = (("sys2x_io",    "sys4x_io"),    None),
            B_ck_t  = (("sys2x_io",    "sys4x_io"),    None),
            B_ck_c  = (("sys2x_io",    "sys4x_io"),    None),
            A_ca    = (("sys2x_io",    "sys4x_io"),    None),
            A_cs_n  = (("sys2x_io",    "sys4x_io"),    None),
            B_ca    = (("sys2x_io",    "sys4x_io"),    None),
            B_cs_n  = (("sys2x_io",    "sys4x_io"),    None),
            reset_n = (("sys2x_io",    "sys4x_io"),    None),
            alert_n = (None,                              ("sys_io", "sys4x_io")),
            A_dq    = (("sys2x_90_io", "sys4x_90_io"), ("sys_io", "sys4x_io")),
            A_dm_n  = (("sys2x_90_io", "sys4x_90_io"), ("sys_io", "sys4x_io")),
            A_dqs_t = (("sys2x_io",    "sys4x_io"),    ("sys_io", "sys4x_io")),
            A_dqs_c = (("sys2x_io",    "sys4x_io"),    ("sys_io", "sys4x_io")),
            B_dq    = (("sys2x_90_io", "sys4x_90_io"), ("sys_io", "sys4x_io")),
            B_dm_n  = (("sys2x_90_io", "sys4x_90_io"), ("sys_io", "sys4x_io")),
            B_dqs_t = (("sys2x_io",    "sys4x_io"),    ("sys_io", "sys4x_io")),
            B_dqs_c = (("sys2x_io",    "sys4x_io"),    ("sys_io", "sys4x_io")),
        )


# Build --------------------------------------------------------------------------------------------

def ddr5_build_argdict(toolchain_argdict):
    build_kwargs = dict(toolchain_argdict)
    defaults = {
        "vivado_place_directive"               : ("default", "AltSpreadLogic_high"),
        "vivado_post_place_phys_opt_directive" : (None,      "AggressiveExplore"),
        "vivado_route_directive"               : ("default", "AggressiveExplore"),
        "vivado_post_route_phys_opt_directive" : ("default", "AggressiveExplore"),
    }
    for name, (default, value) in defaults.items():
        if build_kwargs.get(name) == default:
            build_kwargs[name] = value
    return build_kwargs


def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=antmicro_sodimm_ddr5_tester.Platform, description="LiteX SoC on Antmicro SO-DIMM DDR5 Tester.")
    parser.add_target_argument("--flash",            action="store_true",                  help="Flash bitstream.")
    parser.add_target_argument("--programmer",       default="openfpgaloader",             help="Programmer to use (openfpgaloader or openocd).")
    parser.add_target_argument("--cable",            default="ft4232",                     help="openFPGALoader cable.")
    parser.add_target_argument("--sys-clk-freq",     default=200e6,            type=float, help="System clock frequency.")
    parser.add_target_argument("--iodelay-clk-freq", default=200e6,            type=float, help="IODELAYCTRL frequency.")
    ethopts = parser.target_group.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",  action="store_true", help="Enable Ethernet support.")
    ethopts.add_argument("--with-etherbone", action="store_true", help="Enable Etherbone support.")
    parser.add_target_argument("--eth-ip",                 default="192.168.1.50",  help="Ethernet/Etherbone IP address.")
    parser.add_target_argument("--remote-ip",              default="192.168.1.100", help="Remote IP address of TFTP server.")
    parser.add_target_argument("--eth-dynamic-ip",         action="store_true",     help="Enable dynamic Ethernet IP assignment.")
    parser.add_target_argument("--eth-reset-time",         default="10e-3",         help="Duration of Ethernet PHY reset.")
    parser.add_target_argument("--with-hyperram",          action="store_true",     help="Add HyperRAM.")
    parser.add_target_argument("--hyperram-init-latency",        default=3,  type=int, choices=[3, 4, 5, 6, 7],               help="BIOS HyperRAM initial latency in clocks.")
    parser.add_target_argument("--hyperram-init-drive-strength", default=34, type=int, choices=[34, 115, 67, 46, 27, 22, 19], help="BIOS HyperRAM output drive strength in ohms.")
    parser.add_target_argument("--with-sdcard",            action="store_true",     help="Add SDCard.")
    parser.add_target_argument("--with-spi-flash",         action="store_true",     help="Enable memory-mapped SPI flash.")
    parser.add_target_argument("--with-video-colorbars",   action="store_true",     help="Enable Video Colorbars (HDMI).")
    parser.add_target_argument("--with-video-terminal",    action="store_true",     help="Enable Video Terminal (HDMI).")
    parser.add_target_argument("--with-video-framebuffer", action="store_true",     help="Enable Video Framebuffer (HDMI).")
    args = parser.parse_args()

    assert not (args.with_etherbone and args.eth_dynamic_ip)
    assert sum([args.with_video_colorbars, args.with_video_terminal, args.with_video_framebuffer]) <= 1

    try:
        soc = BaseSoC(
            sys_clk_freq           = args.sys_clk_freq,
            iodelay_clk_freq       = args.iodelay_clk_freq,
            with_ethernet          = args.with_ethernet,
            with_etherbone         = args.with_etherbone,
            eth_ip                 = args.eth_ip,
            remote_ip              = args.remote_ip,
            eth_reset_time         = args.eth_reset_time,
            eth_dynamic_ip         = args.eth_dynamic_ip,
            with_hyperram          = args.with_hyperram,
            hyperram_init_latency  = args.hyperram_init_latency,
            hyperram_init_drive_strength = args.hyperram_init_drive_strength,
            with_sdcard            = args.with_sdcard,
            with_spi_flash         = args.with_spi_flash,
            with_video_colorbars   = args.with_video_colorbars,
            with_video_terminal    = args.with_video_terminal,
            with_video_framebuffer = args.with_video_framebuffer,
            **parser.soc_argdict,
        )
    except DDR5DependencyError as e:
        raise SystemExit(str(e))
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**ddr5_build_argdict(parser.toolchain_argdict))

    if args.load:
        prog = soc.platform.create_programmer(programmer=args.programmer, cable=args.cable)
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer(programmer=args.programmer, cable=args.cable)
        prog.flash(0, builder.get_bitstream_filename(mode="flash"))


if __name__ == "__main__":
    main()
