#!/usr/bin/env python3
"""
---------------------------
 LiteX SoC on Obsidian A35
---------------------------
with support for DDR3 RAM chip, ethernet, SPI flash and UART.
To synthesize, add --build, to configure the FPGA over jtag, add --load.

-----------------
 Example configs
-----------------
lightweight config
  ./berkeleylab_obsidian.py --integrated-main-ram-size 1024 --cpu-type serv

with ethernet and DDR3 (including self test), default IP: 192.168.1.50/24
  ./berkeleylab_obsidian.py --with-ethernet --with-ddr3 --with-bist

etherbone: access wishbone over ethernet
  ./berkeleylab_obsidian.py --with-etherbone --csr-csv build/csr.csv

make sure reset is not asserted (RTS signal), set PC IP to 192.168.1.100/24,
then test and benchmark the etherbone link:
  cd build
  litex/liteeth/bench/test_etherbone.py --udp --ident --access --sram --speed
"""
from migen import Signal, Instance, ClockDomain, reduce, or_
from litex.gen import LiteXModule
from litex.soc.cores.clock import S7MMCM, S7IDELAYCTRL
from litex.soc.integration.soc_core import SoCCore
from litex.soc.integration.builder import Builder
from litex.soc.cores.led import LedChaser
from litex.soc.cores.bitbang import I2CMaster
from litedram.modules import AS4C256M16D3A
from litedram.phy.s7ddrphy import A7DDRPHY
from liteeth.phy.s7rgmii import LiteEthPHYRGMII
from liteiclink.serdes.gtp_7series import GTPQuadPLL, GTP
from litex_boards.platforms import berkeleylab_obsidian
from litex_boards.platforms.berkeleylab_obsidian import raw_pmod_io


# ---------------------------
#  Clock and reset generator
# ---------------------------
class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, resets=[]):
        self.rst = Signal()
        self.cd_sys = ClockDomain()
        self.cd_sys4x = ClockDomain()
        self.cd_sys4x_dqs = ClockDomain()
        self.cd_idelay = ClockDomain()

        # # #

        # Transceiver clock routing. See UG482.
        clk125 = platform.request("clk125")

        # GTP reference clock to be used with GTPQuadPLL
        self.clk125_gtp = Signal()
        clk125_bufh = Signal()

        self.specials += Instance("IBUFDS_GTE2", i_I=clk125.p, i_IB=clk125.n, i_CEB=0, o_O=self.clk125_gtp)
        self.specials += Instance("BUFH", i_I=self.clk125_gtp, o_O=clk125_bufh)

        self.pll = pll = S7MMCM(speedgrade=-2)
        pll.register_clkin(clk125_bufh, 125e6)

        resets.append(self.rst)
        self.comb += pll.reset.eq(reduce(or_, resets))

        pll.create_clkout(self.cd_sys, sys_clk_freq)
        pll.create_clkout(self.cd_sys4x, 4 * sys_clk_freq)
        pll.create_clkout(self.cd_sys4x_dqs, 4 * sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_idelay, 200e6)

        # Ignore sys_clk to pll.clkin path created by SoC's rst.
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin)

        self.idelayctrl = S7IDELAYCTRL(self.cd_idelay)


# ---------------------------
#  BaseSoC
# ---------------------------
class BaseSoC(SoCCore):
    def __init__(
        self,
        sys_clk_freq=125e6,
        with_ethernet=False,
        with_etherbone=False,
        with_rts_reset=False,
        with_ddr3=False,
        with_bist=False,
        with_led_chaser=False,
        with_spi_flash=False,
        **kwargs,
    ):
        self.n_serdes = 0
        platform = berkeleylab_obsidian.Platform()

        # CRG, resettable over USB serial RTS signal
        resets = []
        if with_rts_reset:
            resets.append(platform.request("serial_rts"))
        self.crg = _CRG(platform, sys_clk_freq, resets)

        SoCCore.__init__(
            self,
            platform,
            sys_clk_freq,
            ident="LiteX SoC on Berkeley-Lab Obsidian",
            **kwargs,
        )

        # DDR3 SDRAM
        if with_ddr3:
            self.ddrphy = A7DDRPHY(
                platform.request("ddram"),
                memtype="DDR3",
                sys_clk_freq=sys_clk_freq,
            )

            self.add_sdram(
                "sdram",
                phy=self.ddrphy,
                module=AS4C256M16D3A(sys_clk_freq, "1:4"),
                l2_cache_size=kwargs.get("l2_size", 8192),
                with_bist=with_bist,
            )

        # Ethernet
        if with_ethernet or with_etherbone:
            self.ethphy = LiteEthPHYRGMII(
                clock_pads=self.platform.request("eth_clocks"),
                pads=self.platform.request("eth"),
                rx_delay=0.4e-9,  # These values were determined empirically,
                tx_delay=2e-9,  # see utils/board_test/eth_test.py
                hw_reset_cycles=2000000,  # 10 ms
            )

        if with_ethernet:
            self.add_ethernet(phy=self.ethphy, dynamic_ip=True, software_debug=False)

        if with_etherbone:
            self.add_etherbone(phy=self.ethphy, buffer_depth=255)

        # SPI Flash
        # 4x mode is not possible on this board since WP and HOLD pins are not connected to the FPGA
        if with_spi_flash:
            from litespi.modules import S25FL128L
            from litespi.opcodes import SpiNorFlashOpCodes as Codes

            self.add_spi_flash(
                mode="1x", clk_freq=40e6, module=S25FL128L(Codes.READ_1_1_1), rate="1:1", with_master=True
            )

        # System I2C (4x SFPs, Si5351A and 24AA256UID)
        i2c_pads = platform.request("i2c_fpga")
        self.i2c = I2CMaster(i2c_pads, default_dev=True)

        # Led chaser on PMODF (add LED extension board)
        if with_led_chaser:
            self.platform.add_extension(raw_pmod_io("pmodf"))
            self.leds = LedChaser(
                pads=platform.request("pmodf"),
                sys_clk_freq=sys_clk_freq,
            )

    def add_gtp_sfp(self, sfp_id_tx=0, sfp_id_rx=0, gtp_quad_pll=None, linerate=2.5e9, **kwargs):
        """Adds a GTP transceiver (connected to one of the SFP ports) to the design

        Function can be called multiple times to add multiple transceivers.

        sfp_id_tx / _rx selects the SFP port to connect to (0 - 4)

        gtp_quad_pll can be the `GTPQuadPLL` object to use for clocking or None to internally add one

        linerate is the raw bit-rate in [bits / s] for the internally generated GTPQuadPLL
            (only used if gtp_quad_pll is None)

        All other keyword arguments are forwarded to the liteiclink.serdes.gtp_7series.GTP object

        returns the GTP object, which is also added as a litex submodule

        Defines the `rx` and `tx` clock-domains.
        If there are multiple transceivers, the clock domains are called
        `serdes{i}_rx` and `serdes{i}_tx`, where {i} is the transceiver index
        """
        # GTP PLL ----------------------------------------------------------------------------------
        if gtp_quad_pll is None:
            if not hasattr(self, "gtp_quad_pll"):
                self.submodules.gtp_quad_pll = GTPQuadPLL(self.crg.clk125_gtp, 125e6, linerate)
                print(self.gtp_quad_pll)
            gtp_quad_pll = self.gtp_quad_pll

        # GTP --------------------------------------------------------------------------------------
        tx_pads = self.platform.request("sfp_tx", sfp_id_tx)
        rx_pads = self.platform.request("sfp_rx", sfp_id_rx)

        serdes = GTP(
            gtp_quad_pll,
            tx_pads,
            rx_pads,
            self.sys_clk_freq,
            **kwargs,
        )

        # Add the serdes<N> submodule
        setattr(self.submodules, f"serdes{self.n_serdes}", serdes)
        self.n_serdes += 1

        self.platform.add_period_constraint(serdes.cd_tx.clk, 1e9 / serdes.tx_clk_freq)
        self.platform.add_period_constraint(serdes.cd_rx.clk, 1e9 / serdes.rx_clk_freq)
        self.platform.add_false_path_constraints(self.crg.cd_sys.clk, serdes.cd_tx.clk, serdes.cd_rx.clk)

        return serdes


# ---------------------------
#  CLI examples
# ---------------------------
def main():
    from litex.build.parser import LiteXArgumentParser

    parser = LiteXArgumentParser(
        platform=berkeleylab_obsidian.Platform,
        description="LiteX SoC on LBL Obsidian.",
    )
    parser.add_target_argument("--sys-clk-freq", default=125e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-ethernet", action="store_true", help="Enable Ethernet support.")
    parser.add_target_argument("--with-etherbone", action="store_true", help="Enable Etherbone support.")
    parser.add_target_argument("--with-rts-reset", action="store_true", help="Connect UART RTS line to sys_clk reset.")
    parser.add_target_argument("--with-ddr3", action="store_true", help="Add DDR3 dynamic RAM to the SOC")
    parser.add_target_argument("--with-bist", action="store_true", help="Add DDR3 BIST Generator/Checker.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq=args.sys_clk_freq,
        with_ethernet=args.with_ethernet,
        with_etherbone=args.with_etherbone,
        with_rts_reset=args.with_rts_reset,
        with_ddr3=args.with_ddr3,
        with_bist=args.with_bist,
        **parser.soc_argdict,
    )
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))


if __name__ == "__main__":
    main()
