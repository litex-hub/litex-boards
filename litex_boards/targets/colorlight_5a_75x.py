#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# Build/Use ----------------------------------------------------------------------------------------
#
# 1) SoC with regular UART and optional Ethernet connected to the CPU:
# Connect a USB/UART to J19: TX of the FPGA is DATA_LED-, RX of the FPGA is KEY+.
# ./colorlight_5a_75x.py --revision=7.0 (or 6.1)  --build (--with-ethernet to add Ethernet capability)
# Note: on revision 6.1, add --uart-baudrate=9600 to lower the baudrate.
# ./colorlight_5a_75x.py --load
# You should see the LiteX BIOS and be able to interact with it.
#
# 2) SoC with UART in crossover mode over Etherbone:
# ./colorlight_5a_75x.py --revision=7.0 (or 6.1) --uart-name=crossover --with-etherbone --csr-csv=csr.csv --build
# ./colorlight_5a_75x.py --load
# ping 192.168.1.50
# Get and install wishbone tool from: https://github.com/litex-hub/wishbone-utils/releases
# wishbone-tool --ethernet-host 192.168.1.50 --server terminal --csr-csv csr.csv
# You should see the LiteX BIOS and be able to interact with it.
#
# 3) SoC with USB-ACM UART (on V7.0):
# - Replace U23 with a SN74CBT3245APWR or remove U23 and place jumper wires to make the ports bi-directional.
# - Place a 15K resistor between J4 pin 2 and J4 pin 4.
# - Place a 15K resistor between J4 pin 3 and J4 pin 4.
# - Place a 1.5K resistor between J4 pin 1 and J4 pin 3.
# - Connect USB DP (Green) to J4 pin 3, USB DN (White) to J4 pin 2.
# ./colorlight_5a_75x.py --revision=7.0 --uart-name=usb_acm  --build
# ./colorlight_5a_75x.py --load
# You should see the LiteX BIOS and be able to interact with it.
#
# Note that you can also use a 5A-75E board:
# ./colorlight_5a_75x.py --board=5a-75e --revision=7.1 (or 6.0) --build
#
# Disclaimer: SoC 2) is still a Proof of Concept with large timings violations on the IP/UDP and
# Etherbone stack that need to be optimized. It was initially just used to validate the reversed
# pinout but happens to work on hardware...
#
# Note you can also use the i5a-907 board:
# ./colorlight_5a_75x.py --board=i5a-907 --revision=7.0 --build


from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from litex.build.io import DDROutput

from litex_boards.platforms import colorlight_5a_75b, colorlight_5a_75e, colorlight_i5a_907

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litedram.modules import M12L16161A, M12L64322A
from litedram.phy import GENSDRPHY, HalfRateGENSDRPHY

from liteeth.phy.ecp5rgmii import LiteEthPHYRGMII

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, use_internal_osc=False, with_usb_pll=False, with_rst=True, sdram_rate="1:1"):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()
        if sdram_rate == "1:2":
            self.cd_sys2x    = ClockDomain()
            self.cd_sys2x_ps = ClockDomain()
        else:
            self.cd_sys_ps = ClockDomain()

        # # #

        # Clk / Rst
        if not use_internal_osc:
            clk = platform.request("clk25")
            clk_freq = 25e6
        else:
            clk = Signal()
            div = 5
            self.specials += Instance("OSCG",
                                p_DIV = div,
                                o_OSC = clk)
            clk_freq = 310e6/div

        rst_n = 1 if not with_rst else platform.request("user_btn_n", 0)

        # PLL
        self.pll = pll = ECP5PLL()
        self.comb += pll.reset.eq(~rst_n | self.rst)
        pll.register_clkin(clk, clk_freq)
        pll.create_clkout(self.cd_sys,    sys_clk_freq)
        if sdram_rate == "1:2":
            pll.create_clkout(self.cd_sys2x,    2*sys_clk_freq)
            pll.create_clkout(self.cd_sys2x_ps, 2*sys_clk_freq, phase=180) # Idealy 90° but needs to be increased.
        else:
           pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=180) # Idealy 90° but needs to be increased.

        # USB PLL
        if with_usb_pll:
            self.usb_pll = usb_pll = ECP5PLL()
            self.comb += usb_pll.reset.eq(~rst_n | self.rst)
            usb_pll.register_clkin(clk, clk_freq)
            self.cd_usb_12 = ClockDomain()
            self.cd_usb_48 = ClockDomain()
            usb_pll.create_clkout(self.cd_usb_12, 12e6, margin=0)
            usb_pll.create_clkout(self.cd_usb_48, 48e6, margin=0)

        # SDRAM clock
        sdram_clk = ClockSignal("sys2x_ps" if sdram_rate == "1:2" else "sys_ps")
        self.specials += DDROutput(1, 0, platform.request("sdram_clock"), sdram_clk)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, board, revision, sys_clk_freq=60e6, toolchain="trellis",
        with_ethernet    = False,
        with_etherbone   = False,
        eth_ip           = "192.168.1.50",
        eth_phy          = 0,
        remote_ip        = None,
        eth_dynamic_ip   = False,
        with_led_chaser  = True,
        use_internal_osc = False,
        sdram_rate       = "1:1",
        with_spi_flash   = False,
        **kwargs):
        board = board.lower()
        assert board in ["5a-75b", "5a-75e", "i5a-907"]
        if board == "5a-75b":
            platform = colorlight_5a_75b.Platform(revision=revision, toolchain=toolchain)
        elif board == "5a-75e":
            platform = colorlight_5a_75e.Platform(revision=revision, toolchain=toolchain)
        elif board == "i5a-907":
            platform = colorlight_i5a_907.Platform(revision=revision, toolchain=toolchain)

        if board == "5a-75e" and revision == "6.0" and (with_etherbone or with_ethernet):
            assert use_internal_osc, "You cannot use the 25MHz clock as system clock since it is provided by the Ethernet PHY and will stop during PHY reset."

        # CRG --------------------------------------------------------------------------------------
        with_rst     = kwargs["uart_name"] not in ["serial", "crossover"] # serial_rx shared with user_btn_n.
        if board == "i5a-907":
            with_rst = True
        with_usb_pll = kwargs.get("uart_name", None) == "usb_acm"
        self.crg = _CRG(platform, sys_clk_freq,
            use_internal_osc = use_internal_osc,
            with_usb_pll     = with_usb_pll,
            with_rst         = with_rst,
            sdram_rate       = sdram_rate
        )

        # SoCCore ----------------------------------------------------------------------------------
        # Uartbone ---------------------------------------------------------------------------------
        if kwargs["with_uartbone"]:
            if board != "i5a-907":
                raise ValueError("uartbone only supported on i5a-907")

        SoCCore.__init__(self, platform, int(sys_clk_freq), ident="LiteX SoC on Colorlight " + board.upper(), **kwargs)

        # SDR SDRAM --------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            sdrphy_cls = HalfRateGENSDRPHY if sdram_rate == "1:2" else GENSDRPHY
            self.sdrphy = sdrphy_cls(platform.request("sdram"), sys_clk_freq)
            if (board == "5a-75e" and revision == "6.0") or (board == "5a-75b" and (revision == "8.0" or revision == "8.2")):
                sdram_cls  = M12L64322A
            else:
                sdram_cls  = M12L16161A
            self.add_sdram("sdram",
                phy                     = self.sdrphy,
                module                  = sdram_cls(sys_clk_freq, sdram_rate),
                l2_cache_size           = kwargs.get("l2_size", 8192),
                l2_cache_full_memory_we = False,

            )

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            self.ethphy = LiteEthPHYRGMII(
                clock_pads = self.platform.request("eth_clocks", eth_phy),
                pads       = self.platform.request("eth", eth_phy),
                tx_delay   = 0e-9)
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, ip_address=eth_ip, with_ethmac=with_ethernet, data_width=32)
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy, data_width=32, dynamic_ip=eth_dynamic_ip, local_ip=eth_ip, remote_ip=remote_ip)

        # Leds -------------------------------------------------------------------------------------
        # Disable leds when serial is used.
        if (platform.lookup_request("serial", loose=True) is None and with_led_chaser
            or board == "i5a-907"):
            self.leds = LedChaser(
                pads         = platform.request_all("user_led_n"),
                sys_clk_freq = sys_clk_freq)

        # SPI Flash --------------------------------------------------------------------------------
        if with_spi_flash:
            if board == "i5a-907":
                raise ValueError("SPI Flash chip is unknown on i5a-907, feel free to fix")
                # from litespi.modules import XXXXXX as SpiFlashModule
            elif board == "5a-75b" and revision == "6.0":
                raise ValueError("SPI Flash chip is unknown on 5A-75B v6.0, feel free to fix")
                # from litespi.modules import XXXXXX as SpiFlashModule
            elif board == "5a-75b" and revision == "6.1":
                # It's very possible that V6.0 uses this as well, but no documentation can be found for it
                from litespi.modules import GD25Q16C as SpiFlashModule
            # 5A-75B v7.0/v8.0 and all 5A-75Es seem to use W25Q32JV
            else:
                from litespi.modules import W25Q32JV as SpiFlashModule

            from litespi.opcodes import SpiNorFlashOpCodes
            self.mem_map["spiflash"] = 0x20000000
            self.add_spi_flash(mode="1x", module=SpiFlashModule(SpiNorFlashOpCodes.READ_1_1_1), with_master=False)


# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=colorlight_5a_75b.Platform, description="LiteX SoC on Colorlight 5A-75X.")
    parser.add_target_argument("--board",             default="5a-75b",         help="Board type (5a-75b, 5a-75e or i5a-907).")
    parser.add_target_argument("--revision",          default="7.0",            help="Board revision (6.0, 6.1, 7.0, 8.0, or 8.2).")
    parser.add_target_argument("--sys-clk-freq",      default=60e6, type=float, help="System clock frequency.")
    ethopts = parser.target_group.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",           action="store_true",    help="Enable Ethernet support.")
    ethopts.add_argument("--with-etherbone",          action="store_true",    help="Enable Etherbone support.")
    parser.add_target_argument("--eth-ip",            default="192.168.1.50", help="Ethernet/Etherbone IP address.")
    parser.add_target_argument("--eth-phy",           default=0, type=int,    help="Ethernet PHY (0 or 1).")
    parser.add_target_argument("--use-internal-osc",  action="store_true",    help="Use internal oscillator.")
    parser.add_target_argument("--sdram-rate",        default="1:1",          help="SDRAM Rate (1:1 Full Rate or 1:2 Half Rate).")
    parser.add_target_argument("--with-spi-flash",    action="store_true",    help="Add SPI flash support to the SoC")
    args = parser.parse_args()

    soc = BaseSoC(board=args.board, revision=args.revision,
        sys_clk_freq     = args.sys_clk_freq,
        toolchain        = args.toolchain,
        with_ethernet    = args.with_ethernet,
        with_etherbone   = args.with_etherbone,
        eth_ip           = args.eth_ip,
        eth_phy          = args.eth_phy,
        use_internal_osc = args.use_internal_osc,
        sdram_rate       = args.sdram_rate,
        with_spi_flash   = args.with_spi_flash,
        **parser.soc_argdict
    )
    builder = Builder(soc, **parser.builder_argdict)

    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram", ext=".svf")) # FIXME

if __name__ == "__main__":
    main()
