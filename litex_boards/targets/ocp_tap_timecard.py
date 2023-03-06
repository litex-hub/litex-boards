#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2023 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# Build/Use ----------------------------------------------------------------------------------------
# Build/Load bitstream:
# ./ocp_tap_timecard.py --uart-name=crossover --with-pcie --with-smas --build --driver --load (or --flash)
#
#.Build the kernel and load it:
# cd build/<platform>/driver/kernel
# make
# sudo ./init.sh
#
# Test userspace utilities:
# cd build/<platform>/driver/user
# make
# ./litepcie_util info
# ./litepcie_util scratch_test
# ./litepcie_util dma_test
# ./litepcie_util uart_test

import os

from migen import *

from litex.gen import *

from litex_boards.platforms import ocp_tap_timecard

from litex.soc.interconnect.csr import *
from litex.soc.interconnect import stream
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

from litex.soc.cores.clock import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.xadc import XADC
from litex.soc.cores.dna  import DNA

from litedram.modules import MT41K256M16
from litedram.phy import s7ddrphy

from litepcie.phy.s7pciephy import S7PCIEPHY
from litepcie.software import generate_litepcie_software

# CRG ----------------------------------------------------------------------------------------------

class CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst          = Signal()
        self.cd_sys       = ClockDomain()
        self.cd_sys4x     = ClockDomain()
        self.cd_sys4x_dqs = ClockDomain()
        self.cd_idelay    = ClockDomain()

        # Clk/Rst
        clk200 = platform.request("clk200")

        # PLL
        self.pll = pll = S7PLL()
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk200, 200e6)
        pll.create_clkout(self.cd_sys,       sys_clk_freq)
        pll.create_clkout(self.cd_sys4x,     4*sys_clk_freq)
        pll.create_clkout(self.cd_sys4x_dqs, 4*sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_idelay,    200e6)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        self.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

# BaseSoC -----------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=100e6,
        with_led_chaser = True,
        with_pcie       = False,
        with_smas       = False,
        **kwargs):
        platform = ocp_tap_timecard.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        kwargs["uart_name"] = "crossover"
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on OCP-TAP TimeCard", **kwargs)

        # XADC -------------------------------------------------------------------------------------
        self.xadc = XADC()

        # DNA --------------------------------------------------------------------------------------
        self.dna = DNA()
        self.dna.add_timing_constraints(platform, sys_clk_freq, self.crg.cd_sys.clk)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq
            )

        # PCIe -------------------------------------------------------------------------------------
        if with_pcie:
            self.pcie_phy = S7PCIEPHY(platform, platform.request("pcie_x1"),
                data_width = 64,
                bar0_size  = 0x20000)
            self.add_pcie(phy=self.pcie_phy, ndmas=1, address_width=64)
            # FIXME: Apply it to all targets (integrate it in LitePCIe?).
            platform.add_period_constraint(self.crg.cd_sys.clk, 1e9/sys_clk_freq)
            platform.toolchain.pre_placement_commands.append("reset_property LOC [get_cells -hierarchical -filter {{NAME=~*gtp_channel.gtpe2_channel_i}}]")
            platform.toolchain.pre_placement_commands.append("set_property LOC GTPE2_CHANNEL_X0Y5 [get_cells -hierarchical -filter {{NAME=~*gtp_channel.gtpe2_channel_i}}]")

            # ICAP (For FPGA reload over PCIe).
            from litex.soc.cores.icap import ICAP
            self.icap = ICAP()
            self.icap.add_reload()
            self.icap.add_timing_constraints(platform, sys_clk_freq, self.crg.cd_sys.clk)

            # Flash (For SPIFlash update over PCIe).
            from litex.soc.cores.gpio import GPIOOut
            from litex.soc.cores.spi_flash import S7SPIFlash
            self.flash_cs_n = GPIOOut(platform.request("flash_cs_n"))
            self.flash      = S7SPIFlash(platform.request("flash"), sys_clk_freq, 25e6)

        # SMAs -------------------------------------------------------------------------------------
        if with_smas:
            # TODO:
            # - Use IO primitives to increase IO freqs (up to 800Mz would be fine) and PCIe Gen2 X1
            #   should be able to saturate it (~3.4Gbps of useful bandwidth).
            # - Allow IO freq configuration (through PLL/MMCM and/or dividers).

            class SMAIOs(LiteXModule):
                def __init__(self, pcie_data_width=64, io_data_width=4):
                    # Endpoints.
                    self.sink   = stream.Endpoint([("data", pcie_data_width)])
                    self.source = stream.Endpoint([("data", pcie_data_width)])

                    # CSRs.
                    self.control = CSRStorage(fields=[
                        CSRField("in_en",  size=io_data_width, description="Input  enable control (1bit per SMA)."),
                        CSRField("out_en", size=io_data_width, description="Output enable control (1bit per SMA)."),
                    ])
                    self.output  = CSRStorage(io_data_width, description="SMA Reg Output (1bit per SMA).")
                    self.input   = CSRStatus(io_data_width,  description="SMA Reg Input  (1bit per SMA).")

                    # # #

                    # SMA Pads.
                    sma_pads = [platform.request("sma", i) for i in range(io_data_width)]

                    # SMA Buffer Control.
                    for i in range(io_data_width):
                        self.sync += sma_pads[i].dat_in_en.eq( self.control.fields.in_en)
                        self.sync += sma_pads[i].dat_out_en.eq(self.control.fields.in_en)

                    # SMA TX Reg, allow direct (and slow...) control of SMA IOs.
                    for i in range(io_data_width):
                        self.sync += If(self.output.storage[i],
                            sma_pads[i].dat_out.eq(1)
                        )

                    # SMA TX Data Pipeline.
                    self.tx_converter = tx_converter = stream.Converter(pcie_data_width, io_data_width)
                    self.comb += self.sink.connect(self.tx_converter.sink)
                    self.comb += self.tx_converter.source.ready.eq(1)
                    for i in range(io_data_width):
                        self.sync += If(tx_converter.source.valid & tx_converter.source.data[i],
                            sma_pads[i].dat_out.eq(1)
                        )

                    # SMA RX Reg, allow direct (and slow...) visualization of SMA IOs.
                    for i in range(io_data_width):
                        self.sync += self.input.status[i].eq(sma_pads[i].dat_in)

                    # SMA RX Data Pipeline.
                    self.rx_converter = stream.Converter(io_data_width, pcie_data_width)
                    self.comb += self.rx_converter.sink.valid.eq(1)
                    for i in range(io_data_width):
                        self.sync += self.rx_converter.sink.data[i].eq(sma_pads[i].dat_in)
                    self.comb += self.rx_converter.source.connect(self.source)

            self.smas = SMAIOs(pcie_data_width=64, io_data_width=4)
            self.comb += self.pcie_dma0.source.connect(self.smas.sink)
            self.comb += self.smas.source.connect(self.pcie_dma0.sink)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=ocp_tap_timecard.Platform, description="LiteX SoC on OCP-TAP TimeCard.")
    parser.add_target_argument("--flash",        action="store_true",       help="Flash bitstream.")
    parser.add_target_argument("--sys-clk-freq", default=100e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-pcie",    action="store_true", help="Enable PCIe support.")
    parser.add_target_argument("--with-smas",    action="store_true", help="Enable SMAs support.")
    parser.add_target_argument("--driver",       action="store_true", help="Generate PCIe driver.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq = args.sys_clk_freq,
        with_pcie    = args.with_pcie,
        with_smas    = args.with_smas,
        **parser.soc_argdict
    )

    builder  = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.driver:
        generate_litepcie_software(soc, os.path.join(builder.output_dir, "driver"))

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.flash(0, builder.get_bitstream_filename(mode="flash"))

if __name__ == "__main__":
    main()
