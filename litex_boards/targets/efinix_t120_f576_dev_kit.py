#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Franck Jullien <franck.jullien@collshade.fr>
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import *
from litex.gen.genlib.misc import WaitTimer

from litex_boards.platforms import efinix_t120_f576_dev_kit

from litex.build.generic_platform import Pins, Subsignal, IOStandard

from litex.soc.cores.clock import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.ram.efinix_ddr import EfinixTrionDDR, add_efinix_trion_ddr
from litex.soc.integration.soc import *
from litex.soc.integration.builder import *

from liteeth.phy.trionrgmii import LiteEthPHYRGMII

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()
        self.cd_rst = ClockDomain(reset_less=True)

        # # #

        clk40 = platform.request("clk40")
        rst_n = platform.request("user_btn_n", 0)

        self.comb += self.cd_rst.clk.eq(clk40)

        # A pulse is necessary to do a reset.
        self.rst_pulse = Signal()
        self.reset_timer = reset_timer = ClockDomainsRenamer("rst")(WaitTimer(25e-6*platform.default_clk_freq))
        self.comb += self.rst_pulse.eq(self.rst ^ reset_timer.done)
        self.comb += reset_timer.wait.eq(self.rst)

        # PLL.
        self.pll = pll = TRIONPLL(platform)
        self.comb += pll.reset.eq(~rst_n | self.rst_pulse)
        pll.register_clkin(clk40, platform.default_clk_freq)
        pll.create_clkout(self.cd_sys, sys_clk_freq, with_reset=True, name="axi_clk")


class _CRG_DDR(LiteXModule):
    def __init__(self, platform):
        clk50 = platform.request("dram_pll_refclk")
        rst_n = platform.request("user_btn_n", 1)

        # PLL.
        self.pll = pll = TRIONPLL(platform)
        self.comb += pll.reset.eq(~rst_n)
        pll.register_clkin(clk50, 50e6)
        pll.create_clkout(None, 400e6)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=75e6,
        with_spi_flash  = False,
        with_ethernet   = False,
        with_etherbone  = False,
        eth_phy         = 0,
        eth_rgmii_phy   = False,
        eth_ip          = "192.168.1.50",
        remote_ip       = None,
        eth_dynamic_ip  = False,
        with_led_chaser = True,
        with_i2c        = False,
        **kwargs):
        platform = efinix_t120_f576_dev_kit.Platform()

        # USB-UART PMOD as Serial ------------------------------------------------------------------
        platform.add_extension(efinix_t120_f576_dev_kit.usb_pmod_io("pmod_e"))
        if kwargs.get("uart_name", "serial") == "serial":
            kwargs["uart_name"] = "usb_uart"

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Efinix Trion T120 BGA576 Dev Kit", **kwargs)

        # LPDDR3 SDRAM -----------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.ddr_crg = _CRG_DDR(platform)
            self.ddr = EfinixTrionDDR(platform=platform, **platform.ddr_config)
            add_efinix_trion_ddr(self, self.ddr, size=platform.ddr_size)

        # SPI Flash --------------------------------------------------------------------------------
        if with_spi_flash:
            from litespi.modules import W25Q128JV
            from litespi.opcodes import SpiNorFlashOpCodes as Codes
            self.add_spi_flash(mode="4x", module=W25Q128JV(Codes.READ_1_1_4), with_master=True)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

        # I2C --------------------------------------------------------------------------------------
        if with_i2c:
            from litex.soc.cores.bitbang import I2CMaster
            platform.add_extension(efinix_t120_f576_dev_kit.i2c_pmod_io("pmod_a"))
            self.i2c = I2CMaster(pads=platform.request("i2c"))

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            # Use board's Ethernet PHYs.
            if eth_rgmii_phy:
                msg =  "\n"
                msg += "rx_ctl/tx_ctl pads location aren't compatible with DDIO mode.\n"
                msg += "An hardware modification must be done:\n"
                msg += "- rx_ctl: a wire must be soldered between R120 and R174\n"
                msg += "- tx_ctl: a wire must be soldered between ETH1_TXEN (Pad 30) and R173\n"
                print(msg)
                self.ethphy = LiteEthPHYRGMII(
                    platform           = platform,
                    clock_pads         = platform.request("eth_clocks", eth_phy),
                    pads               = platform.request("eth", eth_phy),
                    with_hw_init_reset = False)
            # Use Ethernet RMII PMOD.
            else:
                def eth_lan8720_rmii_pmod_io(pmod):
                    # Lan8020 RMII PHY "PMOD": To be used as a PMOD, MDIO should be disconnected and TX1 connected to PMOD8 IO.
                    return [
                        ("eth_rmii_clocks", 0,
                            Subsignal("ref_clk", Pins(f"{pmod}:6")),
                            IOStandard("3.3_V_LVTTL_/_LVCMOS"),
                        ),
                        ("eth_rmii", 0,
                            Subsignal("rx_data", Pins(f"{pmod}:5 {pmod}:1")),
                            Subsignal("crs_dv",  Pins(f"{pmod}:2")),
                            Subsignal("tx_en",   Pins(f"{pmod}:4")),
                            Subsignal("tx_data", Pins(f"{pmod}:0 {pmod}:7")),
                            IOStandard("3.3_V_LVTTL_/_LVCMOS")
                        ),
                    ]
                platform.add_extension(eth_lan8720_rmii_pmod_io("pmod_d"))

                from liteeth.phy.rmii import LiteEthPHYRMII
                self.ethphy = LiteEthPHYRMII(
                    clock_pads = platform.request("eth_rmii_clocks"),
                    pads       = platform.request("eth_rmii"),
                    refclk_cd  = None
                )

            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, ip_address=eth_ip, with_ethmac=with_ethernet)
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy, dynamic_ip=eth_dynamic_ip, local_ip=eth_ip, remote_ip=remote_ip, software_debug=False)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=efinix_t120_f576_dev_kit.Platform, description="LiteX SoC on Efinix Trion T120 BGA576 Dev Kit.")
    parser.add_target_argument("--flash",          action="store_true",      help="Flash bitstream.")
    parser.add_target_argument("--sys-clk-freq",   default=75e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-spi-flash", action="store_true",      help="Enable memory-mapped SPI flash.")
    parser.add_target_argument("--with-i2c",       action="store_true",      help="Enable I2C on PMOD A.")
    ethopts = parser.target_group.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",  action="store_true", help="Enable Ethernet support.")
    ethopts.add_argument("--with-etherbone", action="store_true", help="Enable Etherbone support.")
    parser.add_target_argument("--eth-ip",         default="192.168.1.50",  help="Ethernet/Etherbone IP address.")
    parser.add_target_argument("--eth-dynamic-ip", action="store_true",     help="Enable dynamic Ethernet IP assignment.")
    parser.add_target_argument("--remote-ip",      default="192.168.1.100", help="Remote IP address of TFTP server.")
    parser.add_target_argument("--eth-rgmii-phy",  action="store_true",     help="Uses onboard RGMII Phy instead of RMII PMOD.")
    parser.add_target_argument("--eth-phy",        default=0, type=int, choices=[0, 1], help="Ethernet PHY (only available with --eth-rgmii-phy).")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq   = args.sys_clk_freq,
        with_spi_flash = args.with_spi_flash,
        with_i2c       = args.with_i2c,
        with_ethernet  = args.with_ethernet,
        with_etherbone = args.with_etherbone,
        eth_ip         = args.eth_ip,
        eth_dynamic_ip = args.eth_dynamic_ip,
        remote_ip      = args.remote_ip,
        eth_phy        = args.eth_phy,
        eth_rgmii_phy  = args.eth_rgmii_phy,
        **parser.soc_argdict)
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        from litex.build.openfpgaloader import OpenFPGALoader
        prog = OpenFPGALoader("trion_t120_bga576")
        prog.flash(0, builder.get_bitstream_filename(mode="flash", ext=".hex")) # FIXME

if __name__ == "__main__":
    main()
