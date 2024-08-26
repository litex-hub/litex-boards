#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Franck Jullien <franck.jullien@collshade.fr>
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from litex_boards.platforms import efinix_ti375_c529_dev_kit

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.interconnect import axi

from liteeth.phy.trionrgmii import LiteEthPHYRGMII

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        #self.rst    = Signal()
        self.cd_sys = ClockDomain()

        # # #

        clk100 = platform.request("clk100")
        rst_n = platform.request("user_btn", 0)

        # PLL
        self.pll = pll = TITANIUMPLL(platform)
        self.comb += pll.reset.eq(~rst_n)
        pll.register_clkin(clk100, 100e6)
        # You can use CLKOUT0 only for clocks with a maximum frequency of 4x
        # (integer) of the reference clock. If all your system clocks do not fall within
        # this range, you should dedicate one unused clock for CLKOUT0.
        pll.create_clkout(None, 100e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq, with_reset=True)


# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=100e6,
        **kwargs):
        platform = efinix_ti375_c529_dev_kit.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Efinix Ti375 C529 Dev Kit", **kwargs)

        # LPDDR4 SDRAM -----------------------------------------------------------------------------
        if None and not self.integrated_main_ram_size:
            # DRAM / PLL Blocks.
            # ------------------
            dram_pll_refclk = platform.request("dram_pll_refclk")
            platform.toolchain.excluded_ios.append(dram_pll_refclk)
            self.platform.toolchain.additional_sdc_commands.append(f"create_clock -period {1e9/100e6} dram_pll_refclk")

            from litex.build.efinix import InterfaceWriterBlock, InterfaceWriterXMLBlock
            import xml.etree.ElementTree as et

#             class PLLDRAMBlock(InterfaceWriterBlock):
#                 @staticmethod
#                 def generate():
#                     return """
# design.create_block("dram_pll", block_type="PLL")
# design.set_property("dram_pll", {"REFCLK_FREQ":"100.0"}, block_type="PLL")
# design.gen_pll_ref_clock("dram_pll", pll_res="PLL_BL0", refclk_src="EXTERNAL", refclk_name="dram_pll_clkin", ext_refclk_no="0")
# design.set_property("dram_pll","LOCKED_PIN","dram_pll_locked", block_type="PLL")
# design.set_property("dram_pll","RSTN_PIN","dram_pll_rst_n", block_type="PLL")
# design.set_property("dram_pll", {"CLKOUT0_PIN" : "dram_pll_CLKOUT0"}, block_type="PLL")
# design.set_property("dram_pll","CLKOUT0_PHASE","0","PLL")
# calc_result = design.auto_calc_pll_clock("dram_pll", {"CLKOUT0_FREQ": "400.0"})
# """
#             platform.toolchain.ifacewriter.blocks.append(PLLDRAMBlock())

            class DRAMXMLBlock(InterfaceWriterXMLBlock):
                @staticmethod
                def generate(root, namespaces):
                    # CHECKME: Switch to DDRDesignService?
                    ddr_info = root.find("efxpt:ddr_info", namespaces)

                    ddr = et.SubElement(ddr_info, "efxpt:ddr",
                        name            = "ddr_inst1",
                        ddr_def         = "DDR_0",
                                        clkin_sel="0",
                                        data_width="32",
                                        physical_rank="1",
                                        mem_type="LPDDR4x",
                                        mem_density="8G"
                        # cs_preset_id    = "173",
                        # cs_mem_type     = "LPDDR3",
                        # cs_ctrl_width   = "x32",
                        # cs_dram_width   = "x32",
                        # cs_dram_density = "8G",
                        # cs_speedbin     = "800",
                        # target0_enable  = "true",
                        # target1_enable  = "true",
                        # ctrl_type       = "none"
                    )

                    axi_target0 = et.SubElement(ddr, "efxpt:axi_target0",is_axi_width_256="false", is_axi_enable="true")
                    gen_pin_target0 = et.SubElement(axi_target0, "efxpt:gen_pin_axi")
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="ddr0_clk",     type_name=f"ACLK_0",   is_bus="false", is_clk="true", is_clk_invert="false")
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="ddr0_ar_apcmd", type_name="ARAPCMD_0", is_bus="false")
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="ddr0_ar_ready", type_name="ARREADY_0", is_bus="false")
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="ddr0_ar_valid", type_name="ARVALID_0", is_bus="false")
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="ddr0_ar_qos", type_name="ARQOS_0", is_bus="false")
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="ddr0_aw_apcmd", type_name="AWAPCMD_0", is_bus="false")
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="ddr0_aw_allstrb", type_name="AWALLSTRB_0", is_bus="false")
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="ddr0_awcobuf", type_name="AWCOBUF_0", is_bus="false")
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="ddr0_aw_ready", type_name="AWREADY_0", is_bus="false")
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="ddr0_aw_valid", type_name="AWVALID_0", is_bus="false")
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="ddr0_aw_lock", type_name="AWLOCK_0", is_bus="false")
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="ddr0_aw_qos", type_name="AWQOS_0", is_bus="false")
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="ddr0_b_ready", type_name="BREADY_0", is_bus="false")
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="ddr0_b_valid", type_name="BVALID_0", is_bus="false")
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="ddr0_r_last", type_name="RLAST_0", is_bus="false")
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="ddr0_r_ready", type_name="RREADY_0", is_bus="false")
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="ddr0_r_valid", type_name="RVALID_0", is_bus="false")
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="ddr0_w_last", type_name="WLAST_0", is_bus="false")
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="ddr0_w_ready", type_name="WREADY_0", is_bus="false")
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="ddr0_w_valid", type_name="WVALID_0", is_bus="false")
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="ddr0_ar_addr", type_name="ARADDR_0", is_bus="true")
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="ddr0_ar_burst", type_name="ARBURST_0", is_bus="true")
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="ddr0_ar_id", type_name="ARID_0", is_bus="true")
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="ddr0_ar_len", type_name="ARLEN_0", is_bus="true")
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="ddr0_ar_size", type_name="ARSIZE_0", is_bus="true")
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="ddr0_ar_lock", type_name="ARLOCK_0", is_bus="false")
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="ddr0_aw_addr", type_name="AWADDR_0", is_bus="true")
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="ddr0_aw_burst", type_name="AWBURST_0", is_bus="true")
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="ddr0_aw_id", type_name="AWID_0", is_bus="true")
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="ddr0_aw_len", type_name="AWLEN_0", is_bus="true")
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="ddr0_aw_size", type_name="AWSIZE_0", is_bus="true")
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="ddr0_aw_cache", type_name="AWCACHE_0", is_bus="true")
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="ddr0_b_id", type_name="BID_0", is_bus="true")
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="ddr0_b_resp", type_name="BRESP_0", is_bus="true")
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="ddr0_r_data", type_name="RDATA_0", is_bus="true")
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="ddr0_r_id", type_name="RID_0", is_bus="true")
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="ddr0_r_resp", type_name="RRESP_0", is_bus="true")
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="ddr0_w_data", type_name="WDATA_0", is_bus="true")
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="ddr0_w_strb", type_name="WSTRB_0", is_bus="true")
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="ddr0_resetn", type_name="ARSTN_0", is_bus="false")

                    gen_pin_config = et.SubElement(ddr, "efxpt:gen_pin_controller")
                    et.SubElement(gen_pin_config, name="", type_name="CTRL_CLK", is_bus="false", is_clk="true", is_clk_invert="false")
                    et.SubElement(gen_pin_config, name="", type_name="CTRL_INT", is_bus="false")
                    et.SubElement(gen_pin_config, name="", type_name="CTRL_MEM_RST_VALID", is_bus="false")
                    et.SubElement(gen_pin_config, name="", type_name="CTRL_REFRESH", is_bus="false")
                    et.SubElement(gen_pin_config, name="", type_name="CTRL_BUSY", is_bus="false")
                    et.SubElement(gen_pin_config, name="", type_name="CTRL_CMD_Q_ALMOST_FULL", is_bus="false")
                    et.SubElement(gen_pin_config, name="", type_name="CTRL_DP_IDLE", is_bus="false")
                    et.SubElement(gen_pin_config, name="", type_name="CTRL_CKE", is_bus="true")
                    et.SubElement(gen_pin_config, name="", type_name="CTRL_PORT_BUSY", is_bus="true")

                    gen_pin_cfg_ctrl = et.SubElement(ddr, "efxpt:gen_pin_cfg_ctrl")
                    et.SubElement(gen_pin_cfg_ctrl, name="cfg_done", type_name="CFG_DONE", is_bus="false")
                    et.SubElement(gen_pin_cfg_ctrl, name="cfg_start", type_name="CFG_START", is_bus="false")
                    et.SubElement(gen_pin_cfg_ctrl, name="cfg_reset", type_name="CFG_RESET", is_bus="false")
                    et.SubElement(gen_pin_cfg_ctrl, name="cfg_sel", type_name="CFG_SEL", is_bus="false")

                    ctrl_reg_inf = et.SubElement(ddr, "efxpt:ctrl_reg_inf")


                    cs_memory = et.SubElement(ddr, "efxpt:cs_memory")
                    et.SubElement(cs_memory, "efxpt:param", name="RTT_NOM",   value="RZQ/2",     value_type="str")
                    et.SubElement(cs_memory, "efxpt:param", name="MEM_OTERM", value="40",        value_type="str")
                    et.SubElement(cs_memory, "efxpt:param", name="CL",        value="RL=6/WL=3", value_type="str")

                    timing = et.SubElement(ddr, "efxpt:cs_memory_timing")
                    et.SubElement(timing, "efxpt:param", name="tRAS",  value="42.000",  value_type="float")
                    et.SubElement(timing, "efxpt:param", name="tRC",   value="60.000",  value_type="float")
                    et.SubElement(timing, "efxpt:param", name="tRP",   value="18.000",  value_type="float")
                    et.SubElement(timing, "efxpt:param", name="tRCD",  value="18.000",  value_type="float")
                    et.SubElement(timing, "efxpt:param", name="tREFI", value="3.900",   value_type="float")
                    et.SubElement(timing, "efxpt:param", name="tRFC",  value="210.000", value_type="float")
                    et.SubElement(timing, "efxpt:param", name="tRTP",  value="10.000",  value_type="float")
                    et.SubElement(timing, "efxpt:param", name="tWTR",  value="10.000",  value_type="float")
                    et.SubElement(timing, "efxpt:param", name="tRRD",  value="10.000",  value_type="float")
                    et.SubElement(timing, "efxpt:param", name="tFAW",  value="50.000",  value_type="float")

                    cs_control = et.SubElement(ddr, "efxpt:cs_control")
                    et.SubElement(cs_control, "efxpt:param", name="AMAP",             value="ROW-COL_HIGH-BANK-COL_LOW", value_type="str")
                    et.SubElement(cs_control, "efxpt:param", name="EN_AUTO_PWR_DN",   value="Off",                       value_type="str")
                    et.SubElement(cs_control, "efxpt:param", name="EN_AUTO_SELF_REF", value="No",                        value_type="str")

                    cs_gate_delay = et.SubElement(ddr, "efxpt:cs_gate_delay")
                    et.SubElement(cs_gate_delay, "efxpt:param", name="EN_DLY_OVR", value="No", value_type="str")
                    et.SubElement(cs_gate_delay, "efxpt:param", name="GATE_C_DLY", value="3",  value_type="int")
                    et.SubElement(cs_gate_delay, "efxpt:param", name="GATE_F_DLY", value="0",  value_type="int")

            platform.toolchain.ifacewriter.xml_blocks.append(DRAMXMLBlock())

            # DRAM Rst.
            # ---------
            dram_pll_rst_n = platform.add_iface_io("dram_pll_rst_n")
            self.comb += dram_pll_rst_n.eq(platform.request("user_btn", 1))

            # DRAM AXI-Ports.
            # --------------
            for n, data_width in {
                0: 256, # target0: 256-bit.
                1: 128, # target1: 128-bit
            }.items():
                axi_port = axi.AXIInterface(data_width=data_width, address_width=28, id_width=8) # 256MB.
                ios = [(f"axi{n}", 0,
                    Subsignal("wdata",   Pins(data_width)),
                    Subsignal("wready",  Pins(1)),
                    Subsignal("wid",     Pins(8)),
                    Subsignal("bready",  Pins(1)),
                    Subsignal("rdata",   Pins(data_width)),
                    Subsignal("aid",     Pins(8)),
                    Subsignal("bvalid",  Pins(1)),
                    Subsignal("rlast",   Pins(1)),
                    Subsignal("bid",     Pins(8)),
                    Subsignal("asize",   Pins(3)),
                    Subsignal("atype",   Pins(1)),
                    Subsignal("aburst",  Pins(2)),
                    Subsignal("wvalid",  Pins(1)),
                    Subsignal("aaddr",   Pins(32)),
                    Subsignal("rid",     Pins(8)),
                    Subsignal("avalid",  Pins(1)),
                    Subsignal("rvalid",  Pins(1)),
                    Subsignal("alock",   Pins(2)),
                    Subsignal("rready",  Pins(1)),
                    Subsignal("rresp",   Pins(2)),
                    Subsignal("wstrb",   Pins(data_width//8)),
                    Subsignal("aready",  Pins(1)),
                    Subsignal("alen",    Pins(8)),
                    Subsignal("wlast",   Pins(1)),
                )]
                io   = platform.add_iface_ios(ios)
                rw_n = axi_port.ar.valid
                self.comb += [
                    # Pseudo AW/AR Channels.
                    io.atype.eq(~rw_n),
                    io.aaddr.eq(  Mux(rw_n,   axi_port.ar.addr,  axi_port.aw.addr)),
                    io.aid.eq(    Mux(rw_n,     axi_port.ar.id,    axi_port.aw.id)),
                    io.alen.eq(   Mux(rw_n,    axi_port.ar.len,   axi_port.aw.len)),
                    io.asize.eq(  Mux(rw_n,   axi_port.ar.size,  axi_port.aw.size)),
                    io.aburst.eq( Mux(rw_n,  axi_port.ar.burst, axi_port.aw.burst)),
                    io.alock.eq(  Mux(rw_n,   axi_port.ar.lock,  axi_port.aw.lock)),
                    io.avalid.eq( Mux(rw_n,  axi_port.ar.valid, axi_port.aw.valid)),
                    axi_port.aw.ready.eq(~rw_n & io.aready),
                    axi_port.ar.ready.eq( rw_n & io.aready),

                    # R Channel.
                    axi_port.r.id.eq(io.rid),
                    axi_port.r.data.eq(io.rdata),
                    axi_port.r.last.eq(io.rlast),
                    axi_port.r.resp.eq(io.rresp),
                    axi_port.r.valid.eq(io.rvalid),
                    io.rready.eq(axi_port.r.ready),

                    # W Channel.
                    io.wid.eq(axi_port.w.id),
                    io.wstrb.eq(axi_port.w.strb),
                    io.wdata.eq(axi_port.w.data),
                    io.wlast.eq(axi_port.w.last),
                    io.wvalid.eq(axi_port.w.valid),
                    axi_port.w.ready.eq(io.wready),

                    # B Channel.
                    axi_port.b.id.eq(io.bid),
                    axi_port.b.valid.eq(io.bvalid),
                    io.bready.eq(axi_port.b.ready),
                ]

                # Connect AXI interface to the main bus of the SoC.
                axi_lite_port = axi.AXILiteInterface(data_width=data_width, address_width=28)
                self.submodules += axi.AXILite2AXI(axi_lite_port, axi_port)
                self.bus.add_slave(f"target{n}", axi_lite_port, SoCRegion(origin=0x4000_0000 + 0x1000_0000*n, size=0x1000_0000)) # 256MB.

            # Use DRAM's target0 port as Main Ram  -----------------------------------------------------
            self.bus.add_region("main_ram", SoCRegion(
                origin = 0x4000_0000,
                size   = 0x1000_0000, # 256MB.
                linker = True)
            )

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=efinix_ti375_c529_dev_kit.Platform, description="LiteX SoC on Efinix Ti375 C529 Dev Kit.")
    args = parser.parse_args()

    soc = BaseSoC(
        **parser.soc_argdict)
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    # if args.flash:
    #     from litex.build.openfpgaloader import OpenFPGALoader
    #     prog = OpenFPGALoader("titanium_ti375_c529")
    #     prog.flash(0, builder.get_bitstream_filename(mode="flash", ext=".hex")) # FIXME

if __name__ == "__main__":
    main()
