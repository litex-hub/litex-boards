#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 Aria Węgrzyn <git@ariac.at>
# Copyright (c) 2026 Frank Zosso <f.zosso@resorix.ch>
# SPDX-License-Identifier: BSD-2-Clause

# Documentation and photos of the board can be found here:
# https://github.com/tommythorn/rk-xcku5p-f-v1.2/

import os
import math

from migen import *

from litex.gen import *

from litex_boards.platforms import aliexpress_rk_xcku5p

from litex.soc.integration.soc_core import *
from litex.soc.integration.builder  import *

from litex.soc.cores.clock import *
from litex.soc.cores.led   import LedChaser

from litedram.modules import MT40A512M16
from litedram.phy import usddrphy

from migen.genlib.misc      import WaitTimer
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.soc.interconnect.csr import CSRStorage

from liteeth.phy.common  import LiteEthPHYMDIO
from liteeth.phy.usrgmii import LiteEthPHYRGMIITX, LiteEthPHYRGMIIRX

from litespi.modules     import MX25U51245G
from litespi.opcodes     import SpiNorFlashOpCodes as Codes
from litespi.phy.generic import LiteSPIXilinxUSPHY

from litepcie.phy.usppciephy import USPPCIEPHY
from litepcie.software       import generate_litepcie_software

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()
        self.cd_eth = ClockDomain()
        # DDR4
        self.cd_sys4x  = ClockDomain()
        self.cd_pll4x  = ClockDomain()
        self.cd_idelay = ClockDomain()

        # Clk.
        clk200 = platform.request("clk200")

        # PLL.
        self.pll = pll = USPMMCM(speedgrade=-2)
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk200, 200e6)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        # DDR4
        pll.create_clkout(self.cd_pll4x, sys_clk_freq*4, buf=None, with_reset=False)
        pll.create_clkout(self.cd_idelay, 500e6)

        self.specials += [
            Instance("BUFGCE_DIV",
                p_BUFGCE_DIVIDE=4,
                i_CE=1, i_I=self.cd_pll4x.clk, o_O=self.cd_sys.clk),
            Instance("BUFGCE",
                i_CE=1, i_I=self.cd_pll4x.clk, o_O=self.cd_sys4x.clk),
        ]

        self.idelayctrl = USPIDELAYCTRL(cd_ref=self.cd_idelay, cd_sys=self.cd_sys)

# RGMII PHY ----------------------------------------------------------------------------------------

class _RGMIICRG(LiteXModule):
    """RGMII clocks from the PHY's RX clock through an MMCM: the RTL8211F adds the RGMII delays on
    TXC and RXC (strapped), TX data leaves edge aligned with TXC, RX data arrives centered. With
    ZHOLD compensation (feedback through a BUFG) the RX sampling does not depend on the clock tree
    delay, which with a plain BUFG changes with the load of eth_rx (0.6..1.5 ns seen)."""
    def __init__(self, clock_pads, sys_clk_freq, rx_phase=45.0):
        self._reset = CSRStorage(description="PHY reset.")
        self.cd_eth_rx = ClockDomain()
        self.cd_eth_tx = ClockDomain()

        # # #

        rx_clk = Signal()
        fb     = Signal()
        fb_buf = Signal()
        clk_rx = Signal()
        clk_tx = Signal()
        locked = Signal()
        reset  = Signal()
        self.specials += [
            Instance("IBUF", i_I=clock_pads.rx, o_O=rx_clk),
            Instance("MMCME4_ADV",
                p_COMPENSATION     = "ZHOLD",
                p_CLKIN1_PERIOD    = 8.0,
                p_DIVCLK_DIVIDE    = 1,
                p_CLKFBOUT_MULT_F  = 8.0,
                p_CLKOUT0_DIVIDE_F = 8.0,
                p_CLKOUT0_PHASE    = rx_phase,
                p_CLKOUT1_DIVIDE   = 8,
                p_CLKOUT1_PHASE    = 0.0,
                i_CLKIN1  = rx_clk,
                i_CLKFBIN = fb_buf,
                o_CLKFBOUT = fb,
                o_CLKOUT0  = clk_rx,
                o_CLKOUT1  = clk_tx,
                o_LOCKED   = locked,
                i_RST      = reset,
                i_PWRDWN   = 0,
                i_CLKINSEL = 1,
            ),
            Instance("BUFG", i_I=fb,     o_O=fb_buf),
            Instance("BUFG", i_I=clk_rx, o_O=self.cd_eth_rx.clk),
            Instance("BUFG", i_I=clk_tx, o_O=self.cd_eth_tx.clk),
            AsyncResetSynchronizer(self.cd_eth_rx, ~locked),
            AsyncResetSynchronizer(self.cd_eth_tx, ~locked),
        ]

        # Reset the MMCM (CSR, or 1 ms without lock: the PHY clock stops without link).
        self.relock = relock = WaitTimer(int(1e-3*sys_clk_freq))
        self.comb += [
            relock.wait.eq(~locked & ~relock.done),
            reset.eq(self._reset.storage | relock.done),
        ]

        # TX clock to the PHY (edge aligned with the data, the PHY adds the delay).
        tx_clk = Signal()
        self.specials += [
            Instance("ODDRE1", i_C=ClockSignal("eth_tx"), i_SR=0, i_D1=1, i_D2=0, o_Q=tx_clk),
            Instance("OBUF", i_I=tx_clk, o_O=clock_pads.tx),
        ]

class _RGMIIPHY(LiteXModule):
    dw          = 8
    tx_clk_freq = 125e6
    rx_clk_freq = 125e6
    def __init__(self, clock_pads, pads, sys_clk_freq, rx_phase=45.0):
        self.crg = _RGMIICRG(clock_pads, sys_clk_freq, rx_phase)
        self.tx  = ClockDomainsRenamer("eth_tx")(LiteEthPHYRGMIITX(pads))
        self.rx  = ClockDomainsRenamer("eth_rx")(LiteEthPHYRGMIIRX(pads, rx_delay=0, iodelay_clk_freq=500e6, usp=True))
        self.sink, self.source = self.tx.sink, self.rx.source
        self.mdio = LiteEthPHYMDIO(pads)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=100e6,
        with_ethernet   = False,
        with_etherbone  = False,
        eth_ip          = "192.168.1.50",
        remote_ip       = None,
        eth_dynamic_ip  = False,
        eth_rx_phase    = 45.0,
        with_led_chaser = True,
        with_spi_flash  = False,
        with_sdcard     = False,
        with_spi_sdcard = False,
        with_pcie       = False,
        **kwargs):
        platform = aliexpress_rk_xcku5p.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on RK-XCKU5P Board", **kwargs)

        # DDR4 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.ddrphy = usddrphy.USPDDRPHY(
                pads             = platform.request("ddram"),
                memtype          = "DDR4",
                sys_clk_freq     = sys_clk_freq,
                iodelay_clk_freq = 500e6)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT40A512M16(sys_clk_freq, "1:4"),
                # there is 0x80000000 of main ram but we don't want to take all of the upper address space
                # for default configurations. All targets use smaller sizes.
                size          = 0x40000000,
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            self.ethphy = _RGMIIPHY(
                clock_pads   = self.platform.request("eth_clocks"),
                pads         = self.platform.request("eth"),
                sys_clk_freq = sys_clk_freq,
                rx_phase     = eth_rx_phase)
            # TX_D1 (L22) is BITSLICE_0 of a byte calibrated for the RX IDELAYs (only at startup).
            platform.add_platform_command("set_property UNAVAILABLE_DURING_CALIBRATION TRUE [get_ports {{eth_tx_data[1]}}]")
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, ip_address=eth_ip, with_ethmac=with_ethernet)
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy, dynamic_ip=eth_dynamic_ip, local_ip=eth_ip, remote_ip=remote_ip)

        # SPI Flash --------------------------------------------------------------------------------
        if with_spi_flash:
            # Configuration flash, clock/data through STARTUPE3.
            spiflash_module  = MX25U51245G(Codes.READ_1_1_4_4B, program_cmd=Codes.PP_1_1_1_4B)  # no 1-1-4 page program
            spiflash_divisor = math.ceil(sys_clk_freq/20e6)
            spiflash_divisor += spiflash_divisor % 2
            self.add_spi_flash(mode="4x",
                module      = spiflash_module,
                phy         = LiteSPIXilinxUSPHY(spiflash_module, default_divisor=spiflash_divisor),
                with_master = True)

        # SDCard -----------------------------------------------------------------------------------
        if with_sdcard:
            self.add_sdcard()
        if with_spi_sdcard:
            self.add_spi_sdcard()

        # PCIe -------------------------------------------------------------------------------------
        if with_pcie:
            self.pcie_phy = USPPCIEPHY(platform, platform.request("pcie_x4"),
                speed      = "gen3",
                data_width = 128,
                bar0_size  = 0x20000)
            self.pcie_phy.update_config({
                "mode_selection"   : "Advanced",
                "en_gt_selection"  : "true",
                "select_quad"      : "GTY_Quad_224",
                "pcie_blk_locn"    : "X0Y0",
                "gen_x0y0"         : "true",
            })
            self.add_pcie(phy=self.pcie_phy, ndmas=1)

        # Fan --------------------------------------------------------------------------------------
        self.comb += platform.request("fan").eq(1)

        # LEDs -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=aliexpress_rk_xcku5p.Platform, description="LiteX SoC on RK-XCKU5P Board.")
    parser.add_target_argument("--sys-clk-freq",   default=100e6,  type=float, help="System clock frequency.")
    ethopts = parser.target_group.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",        action="store_true",        help="Enable Ethernet support.")
    ethopts.add_argument("--with-etherbone",       action="store_true",        help="Enable Etherbone support.")
    parser.add_target_argument("--eth-ip",         default="192.168.1.50",     help="Ethernet/Etherbone IP address.")
    parser.add_target_argument("--remote-ip",      default="192.168.1.100",    help="Remote IP address of TFTP server.")
    parser.add_target_argument("--eth-dynamic-ip", action="store_true",        help="Enable dynamic Ethernet IP addresses setting.")
    parser.add_target_argument("--eth-rx-phase",   default=45.0,    type=float, help="Ethernet RGMII RX sampling phase (degrees).")
    parser.add_target_argument("--with-spi-flash", action="store_true",        help="Enable SPI Flash (MMAPed).")
    sdopts = parser.target_group.add_mutually_exclusive_group()
    sdopts.add_argument("--with-sdcard",           action="store_true",        help="Enable SDCard support.")
    sdopts.add_argument("--with-spi-sdcard",       action="store_true",        help="Enable SPI-mode SDCard support.")
    parser.add_target_argument("--with-pcie",      action="store_true",        help="Enable PCIe support.")
    parser.add_target_argument("--driver",         action="store_true",        help="Generate PCIe driver.")
    args = parser.parse_args()

    assert not (args.with_etherbone and args.eth_dynamic_ip)

    soc = BaseSoC(
        sys_clk_freq    = args.sys_clk_freq,
        with_ethernet   = args.with_ethernet,
        with_etherbone  = args.with_etherbone,
        eth_ip          = args.eth_ip,
        remote_ip       = args.remote_ip,
        eth_dynamic_ip  = args.eth_dynamic_ip,
        eth_rx_phase    = args.eth_rx_phase,
        with_spi_flash  = args.with_spi_flash,
        with_sdcard     = args.with_sdcard,
        with_spi_sdcard = args.with_spi_sdcard,
        with_pcie       = args.with_pcie,
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

if __name__ == "__main__":
    main()
