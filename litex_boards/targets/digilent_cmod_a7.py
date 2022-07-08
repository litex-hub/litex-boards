#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Michael T. Mayers <michael@tweakoz.com>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.build.io import CRG
from litex.build.xilinx.vivado import vivado_build_args, vivado_build_argdict

from litex_boards.platforms import digilent_cmod_a7

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.interconnect import wishbone

from litex.soc.integration.soc import colorer

kB = 1024
mB = 1024*kB

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_sys = ClockDomain()

        # # #

        # Clk/Rst.
        clk12 = platform.request("clk12")
        rst   = platform.request("cpu_reset")

        # PLL.
        self.submodules.pll = pll = S7MMCM(speedgrade=-1)
        self.comb += pll.reset.eq(rst | self.rst)
        pll.register_clkin(clk12, 12e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

# AsyncSRAM ------------------------------------------------------------------------------------------

class AsyncSRAM(Module):
    def __init__(self, platform, size):
        addr_width = size//8
        data_width = 8
        self.bus = wishbone.Interface(data_width=data_width,adr_width=addr_width)
        issiram = platform.request("issiram")
        addr = issiram.addr
        data = issiram.data
        wen = issiram.wen
        cen = issiram.cen
        ########################
        tristate_data = TSTriple(data_width)
        self.specials += tristate_data.get_tristate(data)
        ########################
        chip_ena = self.bus.cyc & self.bus.stb & self.bus.sel[0]
        write_ena = (chip_ena & self.bus.we)
        ########################
        # external write enable, 
        # external chip enable, 
        # internal tristate write enable
        ########################
        self.comb += [
            cen.eq(~chip_ena),
            wen.eq(~write_ena),
            tristate_data.oe.eq(write_ena)
        ]
        ########################
        # address and data
        ########################
        self.comb += [
            addr.eq(self.bus.adr[:addr_width]),
            self.bus.dat_r.eq(tristate_data.i[:data_width]),
            tristate_data.o.eq(self.bus.dat_w[:data_width])
        ]
        ########################
        # generate ack
        ########################
        self.sync += [
            self.bus.ack.eq(self.bus.cyc & self.bus.stb & ~self.bus.ack),
        ]
        ########################

def addAsyncSram(soc, platform, name, origin, size):
    ram_bus = wishbone.Interface(data_width=soc.bus.data_width)
    ram     = AsyncSRAM(platform,size)
    soc.bus.add_slave(name, ram.bus, SoCRegion(origin=origin, size=size, mode="rw"))
    soc.check_if_exists(name)
    soc.logger.info("ISSIRAM {} {} {}.".format(
        colorer(name),
        colorer("added", color="green"),
        soc.bus.regions[name]))
    setattr(soc.submodules, name, ram)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self,  variant="a7-35",
        toolchain       = "vivado",
        sys_clk_freq    = int(100e6),
        with_led_chaser = True,
        with_spi_flash  = False,
        **kwargs):

        platform = digilent_cmod_a7.Platform(variant=variant, toolchain=toolchain)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Digilent CmodA7", **kwargs)

        # Async RAM --------------------------------------------------------------------------------
        addAsyncSram(self,platform,"main_ram", 0x40000000, 512*1024)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

        # SPI Flash --------------------------------------------------------------------------------
        if with_spi_flash:
            from litespi.modules import MX25U3235F
            from litespi.opcodes import SpiNorFlashOpCodes as Codes
            self.add_spi_flash(mode="4x", module=MX25U3235F(Codes.READ_1_1_4), with_master=True)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on CMOD A7")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--toolchain",    default="vivado",    help="FPGA toolchain (vivado or symbiflow).")
    target_group.add_argument("--build",        action="store_true", help="Build design.")
    target_group.add_argument("--load",         action="store_true", help="Load bitstream.")
    target_group.add_argument("--flash",        action="store_true", help="Flash bitstream.")
    target_group.add_argument("--variant",      default="a7-35",     help="Board variant (a7-35 or a7-100).")
    target_group.add_argument("--sys-clk-freq", default=48e6,        help="System clock frequency.")
    target_group.add_argument("--with-spi-flash", action="store_true", help="Enable SPI Flash (MMAPed).")


    builder_args(parser)
    soc_core_args(parser)
    vivado_build_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        variant           = args.variant,
        toolchain         = args.toolchain,
        sys_clk_freq      = int(float(args.sys_clk_freq)),
        with_spi_flash    = args.with_spi_flash,
        **soc_core_argdict(args)
    )

    builder_argd = builder_argdict(args)

    builder = Builder(soc, **builder_argd)
    builder_kwargs = vivado_build_argdict(args) if args.toolchain == "vivado" else {}
    if args.build:
        builder.build(**builder_kwargs)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.flash(0, builder.get_bitstream_filename(mode="flash"))

if __name__ == "__main__":
    main()
