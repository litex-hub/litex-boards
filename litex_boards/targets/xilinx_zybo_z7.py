#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019-2020 Florent Kermarrec <florent@enjoy-digital.fr>,
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import LiteXModule

from litex_boards.platforms import digilent_zybo_z7

from litex.soc.interconnect import axi
from litex.soc.interconnect import wishbone

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.integration.soc import SoCRegion 
# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, use_ps7_clk=False):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()
        # # #

        if use_ps7_clk:
            self.comb += ClockSignal("sys").eq(ClockSignal("ps7"))
            self.comb += ResetSignal("sys").eq(ResetSignal("ps7") | self.rst)
        else:
            self.pll = pll = S7PLL(speedgrade=-1)
            self.comb += pll.reset.eq(self.rst)
            pll.register_clkin(platform.request("clk125"), 125e6)
            pll.create_clkout(self.cd_sys, sys_clk_freq)
            platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(100e6), variant="z7-10", with_ps7=False, with_led_chaser=True, **kwargs):
        platform = digilent_zybo_z7.Platform()
        self.builder = None
        # CRG --------------------------------------------------------------------------------------
        use_ps7_clk = (kwargs.get("cpu_type", None) == "zynq7000")
        self.crg = _CRG(platform, sys_clk_freq, use_ps7_clk)

        # SoCCore ----------------------------------------------------------------------------------
        if kwargs["uart_name"] == "serial":
            kwargs["uart_name"] = "usb_uart" # Use USB-UART Pmod on JB.
        if kwargs.get("cpu_type", None) == "zynq7000":
            kwargs["integrated_sram_size"] = 0x0
            kwargs["with_uart"] = False
            self.mem_map = {
                'csr': 0x4000_0000,  # Zynq GP0 default
            }
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Zybo Z7", **kwargs)
        
        # Zynq7000 Integration ---------------------------------------------------------------------
        if kwargs.get("cpu_type", None) == "zynq7000":
            self.cpu.use_rom = True
            
            if variant == "z7-10":
                # Get and set the pre-generated .xci FIXME: change location? add it to the repository? Make config
                os.makedirs("xci", exist_ok=True)
                os.system("wget https://github.com/litex-hub/litex-boards/files/8339591/zybo_z7_ps7.txt")
                os.system("mv zybo_z7_ps7.txt xci/zybo_z7_ps7.xci")
                self.cpu.set_ps7_xci("xci/zybo_z7_ps7.xci")
            else: 
                self.cpu.set_ps7(name="ps", config = platform.ps7_config)

            # Connect AXI GP0 to the SoC with base address of 0x40000000 (default one)
            wb_gp0  = wishbone.Interface()
            self.submodules += axi.AXI2Wishbone(
                axi          = self.cpu.add_axi_gp_master(),
                wishbone     = wb_gp0,
                base_address = 0x40000000)
            self.bus.add_master(master=wb_gp0)
            #TODO memory size dependend on board variant
            self.bus.add_region("sram", SoCRegion(
                origin = self.cpu.mem_map["sram"],
                size   = 512 * 1024 * 1024 - self.cpu.mem_map["sram"])
            )
            self.bus.add_region("rom", SoCRegion(
                origin = self.cpu.mem_map["rom"],
                size   = 256 * 1024 * 1024 // 8,
                linker = True)
            )
            self.constants["CONFIG_CLOCK_FREQUENCY"] = 666666687
            self.bus.add_region("flash",  SoCRegion(origin=0xFC00_0000, size=0x4_0000, mode="rwx"))
        # PS7 as Slave Integration ---------------------------------------------------------------------
        elif with_ps7:
            #TODO: ps7_slave for each variant
            if variant == "z7-20":
                self.add_ps7()
                self.add_axi_gp_slave()
        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

    def finalize(self, *args, **kwargs):
        super(BaseSoC, self).finalize(*args, **kwargs)
        if self.cpu_type != "zynq7000":
            return
        libxil_path = os.path.join(self.builder.software_dir, 'libxil')
        os.makedirs(os.path.realpath(libxil_path), exist_ok=True)
        lib = os.path.join(libxil_path, 'embeddedsw')
        if not os.path.exists(lib):
            os.system("git clone --depth 1 https://github.com/Xilinx/embeddedsw {}".format(lib))

        os.makedirs(os.path.realpath(self.builder.include_dir), exist_ok=True)
        for header in [
            'XilinxProcessorIPLib/drivers/uartps/src/xuartps_hw.h',
            'lib/bsp/standalone/src/common/xil_types.h',
            'lib/bsp/standalone/src/common/xil_assert.h',
            'lib/bsp/standalone/src/common/xil_io.h',
            'lib/bsp/standalone/src/common/xil_printf.h',
            'lib/bsp/standalone/src/common/xstatus.h',
            'lib/bsp/standalone/src/common/xdebug.h',
            'lib/bsp/standalone/src/arm/cortexa9/xpseudo_asm.h',
            'lib/bsp/standalone/src/arm/cortexa9/xreg_cortexa9.h',
            'lib/bsp/standalone/src/arm/cortexa9/xil_cache.h',
            'lib/bsp/standalone/src/arm/cortexa9/xparameters_ps.h',
            'lib/bsp/standalone/src/arm/cortexa9/xil_errata.h',
            'lib/bsp/standalone/src/arm/cortexa9/xtime_l.h',
            'lib/bsp/standalone/src/arm/common/xil_exception.h',
            'lib/bsp/standalone/src/arm/common/gcc/xpseudo_asm_gcc.h',
        ]:
            shutil.copy(os.path.join(lib, header), self.builder.include_dir)
        write_to_file(os.path.join(self.builder.include_dir, 'bspconfig.h'),
                      '#define FPU_HARD_FLOAT_ABI_ENABLED 1')
        write_to_file(os.path.join(self.builder.include_dir, 'xparameters.h'), '''
#ifndef __XPARAMETERS_H
#define __XPARAMETERS_H

#include "xparameters_ps.h"

#define STDOUT_BASEADDRESS            XPS_UART1_BASEADDR
#define XPAR_PS7_DDR_0_S_AXI_BASEADDR 0x00100000
#define XPAR_PS7_DDR_0_S_AXI_HIGHADDR 0x3FFFFFFF
#endif
''')


    def add_ps7(self):
        ps7_tcl = []
        ps7_name = "processing_system"
        ps7_tcl.append(f"set ps7 [create_ip -vendor xilinx.com -name processing_system7 -module_name {ps7_name}]")
        ps7_tcl.append("set_property -dict [list \\")
        for config, value in self.platform.ps7_config.items():
            ps7_tcl.append("CONFIG.{} {} \\".format(config, '{{' + str(value) + '}}'))
        ps7_tcl.append(f"] [get_ips {ps7_name}]")
        ps7_tcl += [
                f"upgrade_ip [get_ips {ps7_name}]",
                f"generate_target all [get_ips {ps7_name}]",
                f"synth_ip [get_ips {ps7_name}]"
            ]
        
        self.platform.toolchain.pre_synthesis_commands += ps7_tcl

    def add_axi_gp_slave(self):
        axi_gpn = axi.AXIInterface(data_width=32, address_width=32, id_width=12)
        
        #TODO: better mapping/ Different Regions for IOP and DDR
        aw_address = Signal(32)
        ar_address = Signal(32)
        #FIXME: define offsets with csr register?

        self.comb += If(axi_gpn.aw.addr < 0x1ffbffff,
            ## DDR
            aw_address.eq(axi_gpn.aw.addr + 0x0008_0000)
        ).Else(
                ## IOP Register
               aw_address.eq(axi_gpn.aw.addr  + 0xe000_0000))
        self.comb += If(axi_gpn.ar.addr < 0x1ffbffff,
            ## DDR
            ar_address.eq(axi_gpn.ar.addr  + 0x0008_0000)
        ).Else(
                ## IOP Register
               ar_address.eq(axi_gpn.ar.addr + 0xe000_0000))

        # generate instance of ps7 with ports for axi_s_gp0
        ps7_axi_s_gp0 = Instance("processing_system" ,
            #o_S_AXI_GP0_ARESETN = axi_gpn.a.resetn,
            o_S_AXI_GP0_ARREADY = axi_gpn.ar.ready,
            o_S_AXI_GP0_AWREADY = axi_gpn.aw.ready,
            o_S_AXI_GP0_BVALID = axi_gpn.b.valid,
            o_S_AXI_GP0_RLAST = axi_gpn.r.last,
            o_S_AXI_GP0_RVALID = axi_gpn.r.valid,
            o_S_AXI_GP0_WREADY = axi_gpn.w.ready,  
            o_S_AXI_GP0_BRESP = axi_gpn.b.resp,
            o_S_AXI_GP0_RRESP = axi_gpn.r.resp,
            o_S_AXI_GP0_RDATA = axi_gpn.r.data,
            o_S_AXI_GP0_BID = axi_gpn.b.id,
            o_S_AXI_GP0_RID = axi_gpn.r.id,
            
            i_S_AXI_GP0_ACLK = ClockSignal("sys"),
            i_S_AXI_GP0_ARVALID = axi_gpn.ar.valid,
            i_S_AXI_GP0_AWVALID = axi_gpn.aw.valid,
            i_S_AXI_GP0_BREADY = axi_gpn.b.ready,
            i_S_AXI_GP0_RREADY = axi_gpn.r.ready,
            i_S_AXI_GP0_WLAST = axi_gpn.w.last,
            i_S_AXI_GP0_WVALID = axi_gpn.w.valid,
            i_S_AXI_GP0_ARBURST = axi_gpn.ar.burst,
            i_S_AXI_GP0_ARLOCK = axi_gpn.ar.lock,
            i_S_AXI_GP0_ARSIZE = axi_gpn.ar.size,
            i_S_AXI_GP0_AWBURST = axi_gpn.aw.burst,
            i_S_AXI_GP0_AWLOCK = axi_gpn.aw.lock,
            i_S_AXI_GP0_AWSIZE = axi_gpn.aw.size,
            i_S_AXI_GP0_ARPROT = axi_gpn.ar.prot,
            i_S_AXI_GP0_AWPROT = axi_gpn.aw.prot,
            i_S_AXI_GP0_ARADDR = ar_address,
            i_S_AXI_GP0_AWADDR = aw_address,
            i_S_AXI_GP0_WDATA = axi_gpn.w.data,
            i_S_AXI_GP0_ARCACHE = axi_gpn.ar.cache,
            i_S_AXI_GP0_ARLEN = axi_gpn.ar.len,
            i_S_AXI_GP0_ARQOS = axi_gpn.ar.qos,
            i_S_AXI_GP0_AWCACHE = axi_gpn.aw.cache,
            i_S_AXI_GP0_AWLEN = axi_gpn.aw.len,
            i_S_AXI_GP0_AWQOS = axi_gpn.aw.qos,
            i_S_AXI_GP0_WSTRB = axi_gpn.w.strb,
            i_S_AXI_GP0_ARID = axi_gpn.ar.id,
            i_S_AXI_GP0_AWID = axi_gpn.aw.id,
            i_S_AXI_GP0_WID = axi_gpn.w.id,
        )

        self.specials += ps7_axi_s_gp0
        self.bus.add_slave(name="main_ram",slave=axi_gpn, region=SoCRegion(origin=0x4000_0000, size=0x2000_0000, mode="rwx"))


# Build --------------------------------------------------------------------------------------------

def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on Zybo Z7")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",        action="store_true", help="Build design.")
    target_group.add_argument("--load",         action="store_true", help="Load bitstream.")
    target_group.add_argument("--sys-clk-freq", default=125e6,       help="System clock frequency.")
    target_group.add_argument("--variant",      default="z7-10",     help="Board variant (z7-10 or z7-20).")
    target_group.add_argument("--with-ps7",     action="store_true", help="Add the PS as slave.")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq = int(float(args.sys_clk_freq)),
        variant = args.variant,
        with_ps7 = args.with_ps7,
        **soc_core_argdict(args)
    )
    builder = Builder(soc, **builder_argdict(args))
    if args.cpu_type == "zynq7000":
        soc.builder = builder
        builder.add_software_package('libxil')
        builder.add_software_library('libxil')
    if args.build:
        builder.build(**parser.toolchain_argdict)
    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"), device=1)

if __name__ == "__main__":
    main()
