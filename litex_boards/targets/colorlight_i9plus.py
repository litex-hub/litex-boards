#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2015-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2020 Antmicro <www.antmicro.com>
# Copyright (c) 2022 Victor Suarez Rovere <suarezvictor@gmail.com>
# Copyright (c) 2023 Charles-Henri Mousset <ch.mousset@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

# Connecting to the JTAG port can be done using the 4 headers on the i9+:
# J2: TDO
# J3: TDI
# J4: TMS
# J5: TCK
#
# ColorLight i9+ module and Ext-Board with onboard CH347 JTAG USB-C interface are available on AliExpress:
# See https://github.com/wuxx/Colorlight-FPGA-Projects/blob/master/colorlight_i9plus_v6.1.md
#     https://www.aliexpress.com/item/1005007847728268.html
# Use openFPGALoader -c ch347_jtag file.bit (-f)


from migen import *

from litex.gen import *

from litex.build.io import DDROutput

from litex_boards.platforms import colorlight_i9plus

from litex.soc.cores.clock import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser, WS2812
from litex.soc.cores.xadc import XADC
from litex.soc.cores.dna  import DNA

from litedram.modules import M12L64322A
from litedram.phy import GENSDRPHY

from liteeth.phy.s7rgmii import LiteEthPHYRGMII

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_dram=True, with_ethernet=True):
        self.rst       = Signal()
        self.cd_sys    = ClockDomain()
        self.cd_idelay = ClockDomain()
        if with_dram:
            self.cd_sys_ps = ClockDomain()

        # # #

        # Clk/Rst.
        clk25 = platform.request("clk25")

        # PLL.
        self.pll = pll = S7PLL(speedgrade=-1)
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk25, 25e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        pll.create_clkout(self.cd_idelay,    200e6)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.
        if with_dram:
            pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=27) # Tuned for reliable SDRAM operation.
            # SDRAM clock
            sdram_clk = ClockSignal("sys_ps")
            self.specials += DDROutput(1, 0, platform.request("sdram_clock"), sdram_clk)

        self.idelayctrl = S7IDELAYCTRL(self.cd_idelay)


# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, toolchain="vivado", sys_clk_freq=100e6,
        with_dna        = False,
        with_xadc       = False,
        with_pmod_uart  = False,
        with_ethernet   = False,
        with_etherbone  = False,
        eth_port        = 0,
        eth_ip          = "192.168.1.50",
        remote_ip       = "192.168.1.100",
        eth_dynamic_ip  = False,
        with_led_chaser = True,
        with_rgb_led    = False,
        with_spi_flash  = False,
        **kwargs):
        platform = colorlight_i9plus.Platform(toolchain=toolchain)

        # PMOD: uart on P2 (top) -------------------------------------------------------------------
        if with_pmod_uart or kwargs.get("uart_name", "") == "serial":
            platform.add_extension(colorlight_i9plus.pmod_uart())

        # CRG --------------------------------------------------------------------------------------
        with_dram = (kwargs.get("integrated_main_ram_size", 0) == 0)
        self.crg  = _CRG(platform, sys_clk_freq, with_dram)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on ColorLight-i9+", **kwargs)

        # XADC -------------------------------------------------------------------------------------
        if with_xadc:
            self.xadc = XADC()

        # DNA --------------------------------------------------------------------------------------
        if with_dna:
            self.dna = DNA()
            self.dna.add_timing_constraints(platform, sys_clk_freq, self.crg.cd_sys.clk)

        # SDRAM ------------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            sdrphy_cls = GENSDRPHY
            self.sdrphy = sdrphy_cls(platform.request("sdram"))
            self.add_sdram("sdram",
                phy           = self.sdrphy,
                module        = M12L64322A(sys_clk_freq, "1:1"),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )


        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            self.ethphy = LiteEthPHYRGMII(
                clock_pads = self.platform.request("eth_clocks", eth_port),
                pads       = self.platform.request("eth", eth_port),
                tx_delay = 0)
            if with_ethernet:
                self.add_ethernet(
                    phy        = self.ethphy,
                    dynamic_ip = eth_dynamic_ip,
                    local_ip   = None if eth_dynamic_ip else eth_ip,
                    remote_ip  = remote_ip,
                )
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, ip_address=eth_ip)

        # SPI Flash --------------------------------------------------------------------------------
        if with_spi_flash:
            from litespi.modules import MX25L12833F
            from litespi.opcodes import SpiNorFlashOpCodes as Codes
            self.add_spi_flash(mode="1x", module=MX25L12833F(Codes.READ_1_1_1))

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq,
            )

        # RGB Led ----------------------------------------------------------------------------------
        if with_rgb_led:
            self.rgb_led = WS2812(
                    pad = platform.request("serial_rgb_led_dout"),
                    nleds = 8,
                    sys_clk_freq = sys_clk_freq
            )
            self.bus.add_slave(name="rgb_led", slave=self.rgb_led.bus, region=SoCRegion(origin = 0x2000_0000, size=4*8))


# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=colorlight_i9plus.Platform, description="LiteX SoC on ColorLight-i9+.")
    parser.add_target_argument("--flash",          action="store_true",       help="Flash bitstream.")
    parser.add_target_argument("--sys-clk-freq",   default=100e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-dna",       action="store_true",       help="Enable 7-Series DNA.")
    parser.add_target_argument("--with-xadc",      action="store_true",       help="Enable 7-Series XADC.")
    parser.add_target_argument("--with-rgb-led",   action="store_true",       help="Enable WS2812 RGB LED on Ext-Board conn. P2, pin 26.")
    parser.add_target_argument("--with-pmod-uart", action="store_true",       help="Enable UART on Ext-Board conn. P2, pins 23=RX, 25=TX.")
    ethopts = parser.target_group.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",        action="store_true",       help="Enable Ethernet support.")
    ethopts.add_argument("--with-etherbone",       action="store_true",       help="Enable Etherbone support.")
    parser.add_target_argument("--eth-port",       default=0, type=int,       help="Ethernet port to use (0/1)")
    parser.add_target_argument("--eth-ip",         default="192.168.1.50",    help="Ethernet/Etherbone IP address.")
    parser.add_target_argument("--remote-ip",      default="192.168.1.100",   help="Remote IP address of TFTP server.")
    parser.add_target_argument("--eth-dynamic-ip", action="store_true",       help="Enable dynamic Ethernet IP address assignment.")
    parser.add_target_argument("--with-spi-flash", action="store_true",       help="Enable memory-mapped SPI Flash.")
    args = parser.parse_args()

    assert not (args.with_etherbone and args.eth_dynamic_ip)

    soc = BaseSoC(
        toolchain      = args.toolchain,
        sys_clk_freq   = args.sys_clk_freq,
        with_dna       = args.with_dna,
        with_xadc      = args.with_xadc,
        with_rgb_led   = args.with_rgb_led,
        with_pmod_uart = args.with_pmod_uart,
        with_ethernet  = args.with_ethernet,
        with_etherbone = args.with_etherbone,
        eth_port       = args.eth_port,
        eth_ip         = args.eth_ip,
        remote_ip      = args.remote_ip,
        eth_dynamic_ip = args.eth_dynamic_ip,
        with_spi_flash = args.with_spi_flash,
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
