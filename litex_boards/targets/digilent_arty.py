#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2015-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2020 Antmicro <www.antmicro.com>
# Copyright (c) 2022 Victor Suarez Rovere <suarezvictor@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

# Note: For now with --toolchain=yosys+nextpnr:
# - DDR3 should be disabled: ex --integrated-main-ram-size=8192
# - Clk Freq should be lowered: ex --sys-clk-freq=50e6

from migen import *

from litex.gen import *

from litex_boards.platforms import digilent_arty

from litex.soc.cores.clock import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.gpio import GPIOIn, GPIOTristate
from litex.soc.cores.xadc import XADC
from litex.soc.cores.dna  import DNA

from litedram.modules import MT41K128M16
from litedram.phy import s7ddrphy

from liteeth.phy.mii import LiteEthPHYMII

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_dram=True, with_rst=True):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()
        self.cd_eth = ClockDomain()
        if with_dram:
            self.cd_sys4x     = ClockDomain()
            self.cd_sys4x_dqs = ClockDomain()
            self.cd_idelay    = ClockDomain()

        # # #

        # Clk/Rst.
        clk100 = platform.request("clk100")
        rst    = ~platform.request("cpu_reset") if with_rst else 0

        # PLL.
        self.pll = pll = S7PLL(speedgrade=-1)
        self.comb += pll.reset.eq(rst | self.rst)
        pll.register_clkin(clk100, 100e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        pll.create_clkout(self.cd_eth, 25e6)
        self.comb += platform.request("eth_ref_clk").eq(self.cd_eth.clk)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.
        if with_dram:
            pll.create_clkout(self.cd_sys4x,     4*sys_clk_freq)
            pll.create_clkout(self.cd_sys4x_dqs, 4*sys_clk_freq, phase=90)
            pll.create_clkout(self.cd_idelay,    200e6)

        # IdelayCtrl.
        if with_dram:
            self.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, variant="a7-35", toolchain="vivado", sys_clk_freq=100e6,
        with_xadc       = False,
        with_dna        = False,
        with_ethernet   = False,
        with_etherbone  = False,
        eth_ip          = "192.168.1.50",
        remote_ip       = None,
        eth_dynamic_ip  = False,
        with_usb        = False,
        with_led_chaser = True,
        with_spi_flash  = False,
        with_buttons    = False,
        with_pmod_gpio  = False,
        with_can        = False,
        **kwargs):
        platform = digilent_arty.Platform(variant=variant, toolchain=toolchain)

        # CRG --------------------------------------------------------------------------------------
        with_dram = (kwargs.get("integrated_main_ram_size", 0) == 0)
        self.crg  = _CRG(platform, sys_clk_freq, with_dram)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Arty A7", **kwargs)

        # XADC -------------------------------------------------------------------------------------
        if with_xadc:
            self.xadc = XADC()

        # DNA --------------------------------------------------------------------------------------
        if with_dna:
            self.dna = DNA()
            self.dna.add_timing_constraints(platform, sys_clk_freq, self.crg.cd_sys.clk)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.ddrphy = s7ddrphy.A7DDRPHY(platform.request("ddram"),
                memtype        = "DDR3",
                nphases        = 4,
                sys_clk_freq   = sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT41K128M16(sys_clk_freq, "1:4"),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            self.ethphy = LiteEthPHYMII(
                clock_pads = self.platform.request("eth_clocks"),
                pads       = self.platform.request("eth"))
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, ip_address=eth_ip, with_ethmac=with_ethernet)
            elif with_ethernet:
                self.add_ethernet(phy=self.ethphy, dynamic_ip=eth_dynamic_ip, local_ip=eth_ip, remote_ip=remote_ip)

        # SPI Flash --------------------------------------------------------------------------------
        if with_spi_flash:
            from litespi.modules import S25FL128L
            from litespi.opcodes import SpiNorFlashOpCodes as Codes
            self.add_spi_flash(mode="4x", module=S25FL128L(Codes.READ_1_1_4), rate="1:2", with_master=True)

        # USB-OHCI ---------------------------------------------------------------------------------
        if with_usb:
            from litex.soc.cores.usb_ohci import USBOHCI
            from litex.build.generic_platform import Subsignal, Pins, IOStandard

            self.crg.cd_usb = ClockDomain()
            self.crg.pll.create_clkout(self.crg.cd_usb, 48e6, margin=0)

            # Machdyne PMOD (https://github.com/machdyne/usb_host_dual_socket_pmod)
            _usb_pmod_ios = [
                ("usb_pmoda", 0, # USB1 (top socket)
                    Subsignal("dp", Pins("pmoda:2")),
                    Subsignal("dm", Pins("pmoda:3")),
                    IOStandard("LVCMOS33"),
                ),
                ("usb_pmoda", 1, # USB2 (bottom socket)
                    Subsignal("dp", Pins("pmoda:0")),
                    Subsignal("dm", Pins("pmoda:1")),
                    IOStandard("LVCMOS33"),
                )
            ]
            self.platform.add_extension(_usb_pmod_ios)

            self.submodules.usb_ohci = USBOHCI(self.platform, self.platform.request("usb_pmoda", 0), usb_clk_freq=int(48e6))
            self.mem_map["usb_ohci"] = 0xc0000000
            self.bus.add_slave("usb_ohci_ctrl", self.usb_ohci.wb_ctrl, region=SoCRegion(origin=self.mem_map["usb_ohci"], size=0x100000, cached=False)) # FIXME: Mapping.
            self.dma_bus.add_master("usb_ohci_dma", master=self.usb_ohci.wb_dma)

            self.comb += self.cpu.interrupt[16].eq(self.usb_ohci.interrupt)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq,
            )

        # Buttons ----------------------------------------------------------------------------------
        if with_buttons:
            self.buttons = GPIOIn(
                pads     = platform.request_all("user_btn"),
                with_irq = self.irq.enabled
            )

        # GPIOs ------------------------------------------------------------------------------------
        if with_pmod_gpio:
            platform.add_extension(digilent_arty.raw_pmod_io("pmoda"))
            self.gpio = GPIOTristate(
                pads     = platform.request("pmoda"),
                with_irq = self.irq.enabled
            )

        # CAN --------------------------------------------------------------------------------------
        if with_can:
            from litex.soc.cores.can.ctu_can_fd import CTUCANFD
            self.platform.add_extension(digilent_arty.can_pmod_io("pmodc", 0))
            self.can0 = CTUCANFD(platform, platform.request("can", 0))
            self.bus.add_slave("can0", self.can0.bus, SoCRegion(origin=0xb0010000, size=0x10000, mode="rw", cached=False))
            self.irq.add("can0")

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=digilent_arty.Platform, description="LiteX SoC on Arty A7.")
    parser.add_target_argument("--flash",          action="store_true",       help="Flash bitstream.")
    parser.add_target_argument("--variant",        default="a7-35",           help="Board variant (a7-35 or a7-100).")
    parser.add_target_argument("--sys-clk-freq",   default=100e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-xadc",      action="store_true",       help="Enable 7-Series XADC.")
    parser.add_target_argument("--with-dna",       action="store_true",       help="Enable 7-Series DNA.")
    parser.add_target_argument("--with-usb",       action="store_true",       help="Enable USB Host.")
    parser.add_target_argument("--with-ethernet",  action="store_true",       help="Enable Ethernet support.")
    parser.add_target_argument("--with-etherbone", action="store_true",       help="Enable Etherbone support.")
    parser.add_target_argument("--eth-ip",         default="192.168.1.50",    help="Ethernet/Etherbone IP address.")
    parser.add_target_argument("--remote-ip",      default="192.168.1.100",   help="Remote IP address of TFTP server.")
    parser.add_target_argument("--eth-dynamic-ip", action="store_true",       help="Enable dynamic Ethernet IP addresses setting.")
    sdopts = parser.target_group.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-sdcard",       action="store_true",       help="Enable SPI-mode SDCard support.")
    sdopts.add_argument("--with-sdcard",           action="store_true",       help="Enable SDCard support.")
    parser.add_target_argument("--sdcard-adapter",                            help="SDCard PMOD adapter (digilent or numato).")
    parser.add_target_argument("--with-spi-flash", action="store_true",       help="Enable SPI Flash (MMAPed).")
    parser.add_target_argument("--with-pmod-gpio", action="store_true",       help="Enable GPIOs through PMOD.") # FIXME: Temporary test.
    parser.add_target_argument("--with-can",       action="store_true",       help="Enable CAN support (Through CTU-CAN-FD Core and SN65HVD230 'PMOD'.")
    args = parser.parse_args()

    assert not (args.with_etherbone and args.eth_dynamic_ip)

    soc = BaseSoC(
        variant        = args.variant,
        toolchain      = args.toolchain,
        sys_clk_freq   = args.sys_clk_freq,
        with_xadc      = args.with_xadc,
        with_dna       = args.with_dna,
        with_ethernet  = args.with_ethernet,
        with_etherbone = args.with_etherbone,
        eth_ip         = args.eth_ip,
        remote_ip      = args.remote_ip,
        eth_dynamic_ip = args.eth_dynamic_ip,
        with_usb       = args.with_usb,
        with_spi_flash = args.with_spi_flash,
        with_pmod_gpio = args.with_pmod_gpio,
        with_can       = args.with_can,
        **parser.soc_argdict
    )

    if args.sdcard_adapter == "numato":
        soc.platform.add_extension(digilent_arty._numato_sdcard_pmod_io)
    else:
        soc.platform.add_extension(digilent_arty._sdcard_pmod_io)
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

if __name__ == "__main__":
    main()
