#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019-2020 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2022 Oliver Szabo <16oliver16@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import *

from litex_boards.platforms import digilent_zybo_z7


from litex.soc.cores.clock import *
from litex.soc.integration.soc import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.integration.soc import SoCRegion

from litex.soc.cores import cpu
# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, use_ps7_clk=False):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()
        # # #

        if use_ps7_clk:
            self.comb   +=  ClockSignal("sys").eq(ClockSignal("ps7"))
            self.comb   +=  ResetSignal("sys").eq(ResetSignal("ps7") | self.rst)
        else:
            self.pll    =   pll = S7PLL(speedgrade=-1)
            self.comb   +=  pll.reset.eq(self.rst)
            pll.register_clkin(platform.request("clk125"), 125e6)
            pll.create_clkout(self.cd_sys, sys_clk_freq)
            platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=100e6, variant="z7-10", with_ps7=False, with_led_chaser=True, **kwargs):
        platform = digilent_zybo_z7.Platform(variant=variant)
        self.builder    = None
        # CRG --------------------------------------------------------------------------------------
        use_ps7_clk     = (kwargs.get("cpu_type", None) == "zynq7000")
        self.crg        = _CRG(platform, sys_clk_freq, use_ps7_clk)

        # SoCCore ----------------------------------------------------------------------------------
        if kwargs["uart_name"] == "serial":
            if kwargs.get("uart_name", "serial") == "serial": kwargs["uart_name"] = "usb_uart" # Use USB-UART Pmod on JB.
        if kwargs.get("cpu_type", None) == "zynq7000":
            kwargs["integrated_sram_size"] = 0x0
            kwargs["with_uart"] = False
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Zybo Z7/original Zybo", **kwargs)

        # Zynq7000 Integration ---------------------------------------------------------------------
        if kwargs.get("cpu_type", None) == "zynq7000":
            self.cpu.use_rom = True
            if variant in ["z7-20", "original"]:
                # Get and set the pre-generated .xci FIXME: change location? add it to the repository? Make config
                os.makedirs("xci", exist_ok=True)
                os.system("wget https://github.com/litex-hub/litex-boards/files/8339591/zybo_z7_ps7.txt")
                os.system("mv zybo_z7_ps7.txt xci/zybo_z7_ps7.xci")
                self.cpu.set_ps7_xci("xci/zybo_z7_ps7.xci")
            else:
                self.cpu.set_ps7(name="ps", config = platform.ps7_config)

            #TODO memory size dependend on board variant
            self.bus.add_region("sram", SoCRegion(
                origin = self.cpu.mem_map["sram"],
                size   = 512 * MEGABYTE - self.cpu.mem_map["sram"])
            )
            self.bus.add_region("rom", SoCRegion(
                origin = self.cpu.mem_map["rom"],
                size   = 256 * MEGABYTE // 8,
                linker = True)
            )
            self.constants["CONFIG_CLOCK_FREQUENCY"] = 666666687
            self.bus.add_region("flash", SoCRegion(
                origin = 0xFC00_0000,
                size = 0x4_0000,
                mode = "rwx")
            )
            self.cpu.set_libxil({
                "STDOUT_BASEADDRESS"            : "XPS_UART1_BASEADDR",
                "XPAR_PS7_DDR_0_S_AXI_BASEADDR" : "0x00100000",
                "XPAR_PS7_DDR_0_S_AXI_HIGHADDR" : "0x3FFFFFFF",
            })

        # PS7 as Slave Integration ---------------------------------------------------------------------
        elif with_ps7:
            if variant in ["z7-20", "original"]:
                cpu_cls = cpu.CPUS["zynq7000"]
                zynq    = cpu_cls(self.platform, "standard") # zynq7000 has no variants
                zynq.set_ps7(name="ps", config = platform.ps7_config)
                axi_S_GP0   = zynq.add_axi_gp_slave(clock_domain = self.crg.cd_sys.name)
                axi_S_GP1   = zynq.add_axi_gp_slave(clock_domain = self.crg.cd_sys.name)
                axi_ddr = axi.AXIInterface(axi_S_GP0.data_width, axi_S_GP0.address_width, axi_S_GP0.id_width)
                map_fct_ddr = lambda sig : sig - 0x4000_0000 + 0x0008_0000
                self.comb += axi_ddr.connect_mapped(axi_S_GP0, map_fct_ddr)
                self.bus.add_slave(
                    name="main_ram",slave=axi_ddr,
                    region=SoCRegion(
                        origin=0x4000_0000,
                        size=0x2000_0000,
                        mode="rwx"
                    )
                )
                axi_io = axi.AXIInterface(axi_S_GP1.data_width, axi_S_GP1.address_width, axi_S_GP1.id_width)
                map_fct_io = lambda sig : sig - 0x6000_0000 + 0xE000_0000
                self.comb += axi_io.connect_mapped(axi_S_GP1, map_fct_io)
                self.bus.add_slave(
                    name="ps_io",slave=axi_io,
                    region=SoCRegion(
                        origin=0x6000_0000,
                        size=0x0030_0000,
                        mode="rw",
                        linker=False
                    )
                )
                self.submodules += zynq
            else:
                #TODO: make config for zybo-z7-10
                raise NotImplementedError

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=digilent_zybo_z7.Platform, description="LiteX SoC on Zybo Z7/original Zybo")
    parser.add_target_argument("--sys-clk-freq", default=125e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--variant",      default="z7-10",           help="Board variant (z7-10, z7-20 or original).")
    parser.add_target_argument("--with-ps7",     action="store_true",       help="Add the PS7 as slave for soft CPUs.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq = args.sys_clk_freq,
        variant      = args.variant,
        with_ps7     = args.with_ps7,
        **soc_core_argdict(args)
    )
    builder = Builder(soc, **builder_argdict(args))
    if args.build:
        builder.build(**parser.toolchain_argdict)
    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"), device=1)

if __name__ == "__main__":
    main()
