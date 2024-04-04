#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021-2024 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import *

from litex.build.generic_platform import Subsignal, Pins
from litex.build.io import DifferentialInput
from litex.build.openocd import OpenOCD

from litex_boards.platforms import sqrl_acorn

from litex.soc.interconnect.csr import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

from litex.soc.cores.clock import *
from litex.soc.cores.led import LedChaser

from litex.build.generic_platform import IOStandard, Subsignal, Pins

from litedram.modules import MT41K512M16
from litedram.phy import s7ddrphy

from liteeth.phy.a7_gtp import QPLLSettings, QPLL
from liteeth.phy.a7_1000basex import A7_1000BASEX

from litesata.phy import LiteSATAPHY

# Platform -----------------------------------------------------------------------------------------

class Platform(sqrl_acorn.Platform):
    def create_programmer(self, name="openocd"):
        return OpenOCD("openocd_xc7_ft2232.cfg", "bscan_spi_xc7a200t.bit")

_serial_io = [
    ("serial", 0,
        Subsignal("tx", Pins("G1"),  IOStandard("LVCMOS33")), # CLK_REQ
        Subsignal("rx", Pins("Y13"), IOStandard("LVCMOS18")), # SMB_ALERT_N
    ),
]

# CRG ----------------------------------------------------------------------------------------------

class CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_dram=False, with_eth=False, with_sata=False):
        self.rst          = Signal()
        self.cd_sys       = ClockDomain()
        self.cd_sys4x     = ClockDomain()
        self.cd_sys4x_dqs = ClockDomain()
        self.cd_idelay    = ClockDomain()

        # Clk/Rst.
        clk200    = platform.request("clk200")
        clk200_se = Signal()
        self.specials += DifferentialInput(clk200.p, clk200.n, clk200_se)

        # PLL.
        self.pll = pll = S7PLL()
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk200_se, 200e6)
        pll.create_clkout(self.cd_sys,       sys_clk_freq)
        if with_dram:
            pll.create_clkout(self.cd_sys4x,     4*sys_clk_freq)
            pll.create_clkout(self.cd_sys4x_dqs, 4*sys_clk_freq, phase=90)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        # IDelayCtrl.
        if with_dram:
            self.comb += self.cd_idelay.clk.eq(clk200_se)
            self.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

        # Eth PLL.
        if with_eth:
            self.cd_eth_ref = ClockDomain()
            self.eth_pll = eth_pll = S7PLL()
            self.comb += eth_pll.reset.eq(self.rst)
            eth_pll.register_clkin(clk200_se, 200e6)
            eth_pll.create_clkout(self.cd_eth_ref, 156.25e6, margin=0)

        # SATA PLL.
        if with_sata:
            self.cd_sata_ref = ClockDomain()
            self.sata_pll = sata_pll = S7PLL()
            self.comb += sata_pll.reset.eq(self.rst)
            sata_pll.register_clkin(clk200_se, 200e6)
            sata_pll.create_clkout(self.cd_sata_ref, 150e6, margin=0)

# BaseSoC -----------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, variant="cle-215+", sys_clk_freq=125.00e6,
        with_ethernet   = False,
        with_etherbone  = False,
        eth_ip          = "192.168.1.50",
        remote_ip       = None,
        eth_dynamic_ip  = False,
        with_led_chaser = True,
        with_sata       = False, sata_gen="gen2",
        **kwargs):
        platform = Platform(variant=variant)
        platform.add_extension(_serial_io, prepend=True)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Acorn CLE-101/215(+)", **kwargs)

        # CRG --------------------------------------------------------------------------------------
        with_eth = (with_ethernet or with_etherbone)
        self.crg = CRG(platform, sys_clk_freq,
            with_dram = not self.integrated_main_ram_size,
            with_eth  = with_eth,
            with_sata = with_sata,
        )

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.ddrphy = s7ddrphy.A7DDRPHY(platform.request("ddram"),
                memtype        = "DDR3",
                nphases        = 4,
                sys_clk_freq   = sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT41K512M16(sys_clk_freq, "1:4"),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Ethernet / SATA RefClk/Shared-QPLL -------------------------------------------------------

        # Ethernet QPLL Settings.
        qpll_eth_settings = QPLLSettings(
            refclksel  = 0b111,
            fbdiv      = 4,
            fbdiv_45   = 4,
            refclk_div = 1,
        )

        # SATA QPLL Settings.
        qpll_sata_settings = QPLLSettings(
            refclksel  = 0b111,
            fbdiv      = 5,
            fbdiv_45   = 4,
            refclk_div = 1,
        )

        # Shared QPLL.
        self.qpll = qpll = QPLL(
            gtgrefclk0    = Open() if not with_eth  else self.crg.cd_eth_ref.clk,
            qpllsettings0 = None   if not with_eth  else qpll_eth_settings,
            gtgrefclk1    = Open() if not with_sata else self.crg.cd_sata_ref.clk,
            qpllsettings1 = None   if not with_sata else qpll_sata_settings,
        )
        platform.add_platform_command("set_property SEVERITY {{Warning}} [get_drc_checks REQP-49]")

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            _eth_io = [
                ("sfp", 0,
                    Subsignal("txp", Pins("D5")),
                    Subsignal("txn", Pins("C5")),
                    Subsignal("rxp", Pins("D11")),
                    Subsignal("rxn", Pins("C11")),
                ),
            ]
            platform.add_extension(_eth_io)

            self.ethphy = A7_1000BASEX(
                qpll_channel = qpll.channels[0],
                data_pads    = self.platform.request("sfp"),
                sys_clk_freq = sys_clk_freq,
                rx_polarity  = 1,  # Inverted on Acorn.
                tx_polarity  = 0   # Inverted on Acorn and on baseboard.
            )

            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, ip_address=eth_ip, with_ethmac=with_ethernet)
            elif with_ethernet:
                self.add_ethernet(phy=self.ethphy, dynamic_ip=eth_dynamic_ip, local_ip=eth_ip, remote_ip=remote_ip)

        # SATA -------------------------------------------------------------------------------------
        if with_sata:
            # IOs
            _sata_io = [
                ("sata", 0,
                    # Inverted on Acorn.
                    Subsignal("tx_p",  Pins("B6")),
                    Subsignal("tx_n",  Pins("A6")),
                    # Inverted on Acorn.
                    Subsignal("rx_p",  Pins("B10")),
                    Subsignal("rx_n",  Pins("A10")),
                ),
            ]
            platform.add_extension(_sata_io)

            # PHY
            self.sata_phy = LiteSATAPHY(platform.device,
                refclk     = self.crg.cd_sata_ref.clk,
                pads       = platform.request("sata"),
                gen        = sata_gen,
                clk_freq   = sys_clk_freq,
                data_width = 16,
                qpll       = qpll.channels[1],
            )
            platform.add_platform_command("set_property SEVERITY {{WARNING}} [get_drc_checks REQP-49]")

            # Core
            self.add_sata(phy=self.sata_phy, mode="read+write")

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=sqrl_acorn.Platform, description="LiteX SoC on Acorn CLE-101/215(+).")
    parser.add_target_argument("--flash",          action="store_true",          help="Flash bitstream.")
    parser.add_target_argument("--variant",        default="cle-215+",           help="Board variant (cle-215+, cle-215 or cle-101).")
    parser.add_target_argument("--sys-clk-freq",   default=125.00e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-ethernet",  action="store_true",          help="Enable Ethernet support.")
    parser.add_target_argument("--with-etherbone", action="store_true",          help="Enable Etherbone support.")
    parser.add_target_argument("--eth-ip",         default="192.168.1.50",       help="Ethernet/Etherbone IP address.")
    parser.add_target_argument("--remote-ip",      default="192.168.1.100",      help="Remote IP address of TFTP server.")
    parser.add_target_argument("--eth-dynamic-ip", action="store_true",          help="Enable dynamic Ethernet IP addresses setting.")
    parser.add_target_argument("--with-sata",      action="store_true",          help="Enable SATA support (over FMCRAID).")
    parser.add_target_argument("--sata-gen",       default="2",                  help="SATA Gen.", choices=["1", "2"])
    args = parser.parse_args()

    soc = BaseSoC(
        variant        = args.variant,
        sys_clk_freq   = args.sys_clk_freq,
        with_ethernet  = args.with_ethernet,
        with_etherbone = args.with_etherbone,
        eth_ip         = args.eth_ip,
        remote_ip      = args.remote_ip,
        eth_dynamic_ip = args.eth_dynamic_ip,
        with_sata      = args.with_sata,
        sata_gen       = "gen" + args.sata_gen,
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
