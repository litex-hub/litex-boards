#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Franck Jullien <franck.jullien@collshade.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import *
from litex.gen.genlib.misc import WaitTimer

from litex_boards.platforms import efinix_ti60_f225_dev_kit

from litex.soc.cores.clock import *
from litex.soc.integration.soc import *
from litex.soc.integration.builder import *
from litex.soc.cores.gpio import GPIOIn
from litex.soc.cores.led import LedChaser

from liteeth.phy.titaniumrgmii import LiteEthPHYRGMII

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, hyperram=None):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()
        self.cd_rst = ClockDomain(reset_less=True)

        # # #

        clk25 = platform.request("clk25")
        rst_n = platform.request("user_btn_n", 0)

        self.comb += self.cd_rst.clk.eq(clk25)

        # A pulse is necessary to do a reset.
        self.rst_pulse = Signal()
        self.reset_timer = reset_timer = ClockDomainsRenamer("rst")(WaitTimer(25e-6*platform.default_clk_freq))
        self.comb += self.rst_pulse.eq(self.rst ^ reset_timer.done)
        self.comb += reset_timer.wait.eq(self.rst)

        # PLL Dynamic Phase Shift (HyperRAM DDR read capture calibration).
        self.shift_pads = None
        if hyperram == "ddr":
            self.shift_pads = {
                "shift_ena" : platform.add_iface_io("pll_shift_ena"),
                "shift"     : platform.add_iface_io("pll_shift", 3),
                "shift_sel" : platform.add_iface_io("pll_shift_sel", 5),
            }

        # PLL
        self.pll = pll = TITANIUMPLL(platform, dyn_phase_shift_pads=self.shift_pads)
        self.comb += pll.reset.eq(~rst_n | self.rst_pulse)
        pll.register_clkin(clk25, platform.default_clk_freq)
        if hyperram == "ddr":
            # HyperRAM DDR PHY clocks (sys = HyperRAM CK): sys90 for CK, sys_cap for read capture
            # (dynamic phase). Dynamic phase shift requires core feedback (25MHz on output 3).
            self.cd_sys90   = ClockDomain()
            self.cd_sys_cap = ClockDomain()
            pll.create_clkout(self.cd_sys,     sys_clk_freq,           with_reset=True, nclkout=0)
            pll.create_clkout(self.cd_sys90,   sys_clk_freq, phase=90, with_reset=True, nclkout=1)
            pll.create_clkout(self.cd_sys_cap, sys_clk_freq,           with_reset=True, nclkout=2, dyn_phase=True)
            pll.create_clkout(None, 25e6, nclkout=3, is_feedback=True)
            self.shift_sel = 1 << 2
            # Force VCO=3.2GHz/O=4: 45° dynamic phase steps at 200MHz, so the read calibration sweeps
            # the full capture clock period (Efinity's auto-config gives smaller steps).
            div = 800e6/sys_clk_freq
            if div == int(div) and int(div) % 2 == 0:
                div = int(div)
                pll.set_config(M=1, N=1, O=4,
                    dividers       = {0: div, 1: div, 2: div, 3: 32},
                    phase_settings = {0: 0, 1: div//2, 2: 0},
                )
        else:
            # You can use CLKOUT0 only for clocks with a maximum frequency of 4x
            # (integer) of the reference clock. If all your system clocks do not fall within
            # this range, you should dedicate one unused clock for CLKOUT0.
            pll.create_clkout(None, 25e6)
            pll.create_clkout(self.cd_sys, sys_clk_freq, with_reset=True)
        if hyperram == "sdr":
            self.cd_sys2x    = ClockDomain()
            self.cd_sys2x_ps = ClockDomain()
            pll.create_clkout(self.cd_sys2x,    2*sys_clk_freq,            with_reset=True)
            pll.create_clkout(self.cd_sys2x_ps, 2*sys_clk_freq, phase=270, with_reset=True) # 315° is rejected by Efinity's PLL rules.

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=200e6,
        with_spi_flash = False,
        with_hyperram  = False,
        hyperram_phy   = "ddr",
        with_ethernet  = False,
        with_etherbone = False,
        eth_phy        = 0,
        eth_ip         = "192.168.1.50",
        remote_ip      = None,
        eth_dynamic_ip = False,
        with_led_chaser = True,
        with_buttons   = False,
        with_switches  = False,
        with_cam_i2c   = False,
        **kwargs):
        platform = efinix_ti60_f225_dev_kit.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, hyperram=hyperram_phy if with_hyperram else None)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Efinix Titanium Ti60 F225 Dev Kit", **kwargs)

        # SPI Flash --------------------------------------------------------------------------------
        if with_spi_flash:
            from litespi.modules import W25Q64JW
            from litespi.opcodes import SpiNorFlashOpCodes as Codes
            self.add_spi_flash(mode="1x", module=W25Q64JW(Codes.READ_1_1_1), with_master=True)

        # Leds / Buttons / Switches ---------------------------------------------------------------
        if with_led_chaser:
            # RGB LEDs: request_all can't Cat Records, use the red channel of each LED.
            leds = [platform.request("user_led", i) for i in range(2)]
            self.leds = LedChaser(
                pads         = Cat(*[led.r for led in leds]),
                sys_clk_freq = sys_clk_freq,
            )
        if with_buttons:
            self.buttons = GPIOIn(Cat(platform.request_all("user_btn_n")[1:]))
        if with_switches:
            self.switches = GPIOIn(Cat(platform.request_all("user_sw")))

        # Camera I2C ------------------------------------------------------------------------------
        if with_cam_i2c:
            from litex.soc.cores.bitbang import I2CMaster
            cam_i2c = platform.request("cam_i2c")
            self.cam_i2c = I2CMaster(pads=cam_i2c)
            self.comb += cam_i2c.reset.eq(1)

        # HyperRAM ---------------------------------------------------------------------------------
        if with_hyperram:
            if hyperram_phy == "ddr":
                # DDR IOs, CK = sys_clk_freq (800MB/s peak at 200MHz), read calibration in gateware.
                from litex.soc.cores.hyperram import HyperRAMController
                from litex.soc.cores.hyperram.phy.titanium import TitaniumHyperRAMPHY
                phy = TitaniumHyperRAMPHY(platform, platform.request("hyperram"),
                    cd_sys     = "sys",
                    cd_90      = "sys90",
                    cd_cap     = "sys_cap",
                    shift_pads = self.crg.shift_pads,
                    shift_sel  = self.crg.shift_sel,
                )
                self.add_hyperram(
                    region_name   = "main_ram",
                    origin        = self.mem_map["main_ram"],
                    size          = 32*MEGABYTE,
                    l2_cache_size = 16*KILOBYTE,
                    module        = HyperRAMController(phy, clk_freq=sys_clk_freq, size=32*MEGABYTE),
                )
            else:
                # Fabric oversampling PHY, CK = sys_clk_freq/2.
                self.add_hyperram(
                    region_name   = "main_ram",
                    origin        = self.mem_map["main_ram"],
                    size          = 32*MEGABYTE,
                    l2_cache_size = 16*KILOBYTE,
                    latency       = 7,
                    latency_mode  = "variable",
                    clk_ratio     = "2:1",
                    dq_i_cd       = "sys2x_ps",
                )

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            platform.add_extension(efinix_ti60_f225_dev_kit.rgmii_ethernet_qse_ios("P1"))
            pads = platform.request("eth", eth_phy)
            self.ethphy = LiteEthPHYRGMII(
                platform           = platform,
                clock_pads         = platform.request("eth_clocks", eth_phy),
                pads               = pads,
                with_hw_init_reset = False)
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, ip_address=eth_ip, with_ethmac=with_ethernet)
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy, dynamic_ip=eth_dynamic_ip, local_ip=eth_ip, remote_ip=remote_ip, software_debug=False)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=efinix_ti60_f225_dev_kit.Platform, description="LiteX SoC on Efinix Titanium Ti60 F225 Dev Kit.")
    parser.add_target_argument("--flash",          action="store_true",       help="Flash bitstream.")
    parser.add_target_argument("--sys-clk-freq",   default=200e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-spi-flash", action="store_true",       help="Enable memory-mapped SPI flash.")
    parser.add_target_argument("--with-hyperram",  action="store_true",       help="Enable HyperRAM.")
    parser.add_target_argument("--hyperram-phy",   default="ddr", choices=["ddr", "sdr"], help="HyperRAM PHY: ddr (DDR IOs, CK=sys_clk) or sdr (fabric, CK=sys_clk/2).")
    parser.add_target_argument("--with-cam-i2c",   action="store_true",       help="Enable Camera I2C.")
    parser.add_target_argument("--with-buttons",   action="store_true",       help="Enable Buttons.")
    parser.add_target_argument("--with-switches",  action="store_true",       help="Enable Switches.")
    sdopts = parser.target_group.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-sdcard", action="store_true", help="Enable SPI-mode SDCard support.")
    sdopts.add_argument("--with-sdcard",     action="store_true", help="Enable SDCard support.")
    ethopts = parser.target_group.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",  action="store_true", help="Enable Ethernet support.")
    ethopts.add_argument("--with-etherbone", action="store_true", help="Enable Etherbone support.")
    parser.add_target_argument("--eth-ip",         default="192.168.1.50",  help="Ethernet/Etherbone IP address.")
    parser.add_target_argument("--eth-dynamic-ip", action="store_true",     help="Enable dynamic Ethernet IP assignment.")
    parser.add_target_argument("--remote-ip",      default="192.168.1.100", help="Remote IP address of TFTP server.")
    parser.add_target_argument("--eth-phy",        default=0, type=int,     help="Ethernet PHY: 0 (default) or 1.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq   = args.sys_clk_freq,
        with_spi_flash = args.with_spi_flash,
        with_hyperram  = args.with_hyperram,
        hyperram_phy   = args.hyperram_phy,
        with_ethernet  = args.with_ethernet,
        with_etherbone = args.with_etherbone,
        eth_ip         = args.eth_ip,
        eth_dynamic_ip = args.eth_dynamic_ip,
        remote_ip      = args.remote_ip,
        eth_phy        = args.eth_phy,
        with_buttons   = args.with_buttons,
        with_switches  = args.with_switches,
        with_cam_i2c   = args.with_cam_i2c,
         **parser.soc_argdict)
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
        from litex.build.openfpgaloader import OpenFPGALoader
        prog = OpenFPGALoader("titanium_ti60_f225")
        prog.flash(0, builder.get_bitstream_filename(mode="flash", ext=".hex")) # FIXME

if __name__ == "__main__":
    main()
