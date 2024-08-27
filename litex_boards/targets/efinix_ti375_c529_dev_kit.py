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
from litex.build.generic_platform import Subsignal, Pins, Misc, IOStandard

# python3 -m litex_boards.targets.efinix_ti375_c529_dev_kit --cpu-type=vexiiriscv --cpu-variant=debian --update-repo=no --with-jtag-tap --with-sdcard --with-coherent-dma
# python3 -m litex.tools.litex_json2dts_linux build/efinix_ti375_c529_dev_kit/csr.json --root-device=mmcblk0p2 > build/efinix_ti375_c529_dev_kit/linux.dts


# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        #self.rst    = Signal()
        self.cd_sys = ClockDomain()
        self.cd_usb       = ClockDomain()

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
        pll.create_clkout(self.cd_sys, sys_clk_freq, with_reset=True, name="cd_sys_clkout")
        pll.create_clkout(self.cd_usb, 60e6, margin=0)
        pll.create_clkout(None, 800e6, name="dram_clk") # LPDDR4 ctrl


# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    mem_map = {**SoCCore.mem_map, **{
        "usb_ohci":     0xE0000000,
    }}

    def __init__(self, sys_clk_freq=100e6,
                 with_ohci=False,
        **kwargs):
        platform = efinix_ti375_c529_dev_kit.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Efinix Ti375 C529 Dev Kit", **kwargs)

        # OHCI
        if with_ohci:
            from litex.soc.cores.usb_ohci import USBOHCI
            from litex.build.generic_platform import Subsignal, Pins, IOStandard
            from litex.soc.integration.soc import SoCRegion
            _usb_pmod_ios = [
               ("usb_pmod1", 0,
                   Subsignal("dp", Pins("pmod1:0", "pmod1:1", "pmod1:2", "pmod1:3")),
                   Subsignal("dm", Pins("pmod1:4", "pmod1:5", "pmod1:6", "pmod1:7")),
                   IOStandard("3.3_V_LVCMOS"),
               )
            ]
            platform.add_extension(_usb_pmod_ios)
            self.submodules.usb_ohci = USBOHCI(platform, platform.request("usb_pmod1"), usb_clk_freq=int(60e6))
            self.bus.add_slave("usb_ohci_ctrl", self.usb_ohci.wb_ctrl, region=SoCRegion(origin=self.mem_map["usb_ohci"], size=0x100000, cached=False))
            self.dma_bus.add_master("usb_ohci_dma", master=self.usb_ohci.wb_dma)
            self.comb += self.cpu.interrupt[16].eq(self.usb_ohci.interrupt)

        # JTAG
        if hasattr(self.cpu, "jtag_clk"):
            _jtag_io = [
                ("jtag", 0,
                 Subsignal("tck", Pins("pmod0:0")),
                 Subsignal("tdi", Pins("pmod0:1")),
                 Subsignal("tdo", Pins("pmod0:2")),
                 Subsignal("tms", Pins("pmod0:3")),
                 IOStandard("3.3_V_LVCMOS"),
                 )
            ]
            self.platform.add_extension(_jtag_io)
            jtag_pads = platform.request("jtag")
            self.comb += self.cpu.jtag_clk.eq(jtag_pads.tck)
            self.comb += self.cpu.jtag_tms.eq(jtag_pads.tms)
            self.comb += self.cpu.jtag_tdi.eq(jtag_pads.tdi)
            self.comb += jtag_pads.tdo.eq(self.cpu.jtag_tdo)
            platform.add_false_path_constraints(self.crg.cd_sys.clk, jtag_pads.tck)

        # LPDDR4 SDRAM -----------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            # DRAM / PLL Blocks.
            # ------------------
            dram_pll_refclk = platform.request("dram_pll_refclk")
            platform.toolchain.excluded_ios.append(dram_pll_refclk)
            self.platform.toolchain.additional_sdc_commands.append(f"create_clock -period {1e9/100e6} dram_pll_refclk")

            from litex.build.efinix import InterfaceWriterBlock, InterfaceWriterXMLBlock
            import xml.etree.ElementTree as et

            data_width = 512
            axi_bus = axi.AXIInterface(data_width=data_width, address_width=30, id_width=8) # 256MB.
            class DRAMXMLBlock(InterfaceWriterXMLBlock):
                @staticmethod
                def generate(root, namespaces):
                    # CHECKME: Switch to DDRDesignService?
                    ddr_info = root.find("efxpt:ddr_info", namespaces)

                    ddr = et.SubElement(ddr_info, "efxpt:adv_ddr",
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
                    et.SubElement(gen_pin_target0, "efxpt:pin", name="cd_sys_clkout",     type_name=f"ACLK_0",   is_bus="false", is_clk="true", is_clk_invert="false")
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

                    axi_target1 = et.SubElement(ddr, "efxpt:axi_target1",is_axi_width_256="false", is_axi_enable="false")
                    gen_pin_target1 = et.SubElement(axi_target1, "efxpt:gen_pin_axi")
                    et.SubElement(gen_pin_target1, "efxpt:pin", name="cd_sys_clkout",     type_name=f"ACLK_1",   is_bus="false", is_clk="true", is_clk_invert="false")
                    et.SubElement(gen_pin_target1, "efxpt:pin", name="ddr1_ar_apcmd", type_name="ARAPCMD_1", is_bus="false")
                    et.SubElement(gen_pin_target1, "efxpt:pin", name="ddr1_ar_ready", type_name="ARREADY_1", is_bus="false")
                    et.SubElement(gen_pin_target1, "efxpt:pin", name="ddr1_ar_valid", type_name="ARVALID_1", is_bus="false")
                    et.SubElement(gen_pin_target1, "efxpt:pin", name="ddr1_ar_qos", type_name="ARQOS_1", is_bus="false")
                    et.SubElement(gen_pin_target1, "efxpt:pin", name="ddr1_aw_apcmd", type_name="AWAPCMD_1", is_bus="false")
                    et.SubElement(gen_pin_target1, "efxpt:pin", name="ddr1_aw_allstrb", type_name="AWALLSTRB_1", is_bus="false")
                    et.SubElement(gen_pin_target1, "efxpt:pin", name="ddr1_awcobuf", type_name="AWCOBUF_1", is_bus="false")
                    et.SubElement(gen_pin_target1, "efxpt:pin", name="ddr1_aw_ready", type_name="AWREADY_1", is_bus="false")
                    et.SubElement(gen_pin_target1, "efxpt:pin", name="ddr1_aw_valid", type_name="AWVALID_1", is_bus="false")
                    et.SubElement(gen_pin_target1, "efxpt:pin", name="ddr1_aw_lock", type_name="AWLOCK_1", is_bus="false")
                    et.SubElement(gen_pin_target1, "efxpt:pin", name="ddr1_aw_qos", type_name="AWQOS_1", is_bus="false")
                    et.SubElement(gen_pin_target1, "efxpt:pin", name="ddr1_b_ready", type_name="BREADY_1", is_bus="false")
                    et.SubElement(gen_pin_target1, "efxpt:pin", name="ddr1_b_valid", type_name="BVALID_1", is_bus="false")
                    et.SubElement(gen_pin_target1, "efxpt:pin", name="ddr1_r_last", type_name="RLAST_1", is_bus="false")
                    et.SubElement(gen_pin_target1, "efxpt:pin", name="ddr1_r_ready", type_name="RREADY_1", is_bus="false")
                    et.SubElement(gen_pin_target1, "efxpt:pin", name="ddr1_r_valid", type_name="RVALID_1", is_bus="false")
                    et.SubElement(gen_pin_target1, "efxpt:pin", name="ddr1_w_last", type_name="WLAST_1", is_bus="false")
                    et.SubElement(gen_pin_target1, "efxpt:pin", name="ddr1_w_ready", type_name="WREADY_1", is_bus="false")
                    et.SubElement(gen_pin_target1, "efxpt:pin", name="ddr1_w_valid", type_name="WVALID_1", is_bus="false")
                    et.SubElement(gen_pin_target1, "efxpt:pin", name="ddr1_ar_addr", type_name="ARADDR_1", is_bus="true")
                    et.SubElement(gen_pin_target1, "efxpt:pin", name="ddr1_ar_burst", type_name="ARBURST_1", is_bus="true")
                    et.SubElement(gen_pin_target1, "efxpt:pin", name="ddr1_ar_id", type_name="ARID_1", is_bus="true")
                    et.SubElement(gen_pin_target1, "efxpt:pin", name="ddr1_ar_len", type_name="ARLEN_1", is_bus="true")
                    et.SubElement(gen_pin_target1, "efxpt:pin", name="ddr1_ar_size", type_name="ARSIZE_1", is_bus="true")
                    et.SubElement(gen_pin_target1, "efxpt:pin", name="ddr1_ar_lock", type_name="ARLOCK_1", is_bus="false")
                    et.SubElement(gen_pin_target1, "efxpt:pin", name="ddr1_aw_addr", type_name="AWADDR_1", is_bus="true")
                    et.SubElement(gen_pin_target1, "efxpt:pin", name="ddr1_aw_burst", type_name="AWBURST_1", is_bus="true")
                    et.SubElement(gen_pin_target1, "efxpt:pin", name="ddr1_aw_id", type_name="AWID_1", is_bus="true")
                    et.SubElement(gen_pin_target1, "efxpt:pin", name="ddr1_aw_len", type_name="AWLEN_1", is_bus="true")
                    et.SubElement(gen_pin_target1, "efxpt:pin", name="ddr1_aw_size", type_name="AWSIZE_1", is_bus="true")
                    et.SubElement(gen_pin_target1, "efxpt:pin", name="ddr1_aw_cache", type_name="AWCACHE_1", is_bus="true")
                    et.SubElement(gen_pin_target1, "efxpt:pin", name="ddr1_b_id", type_name="BID_1", is_bus="true")
                    et.SubElement(gen_pin_target1, "efxpt:pin", name="ddr1_b_resp", type_name="BRESP_1", is_bus="true")
                    et.SubElement(gen_pin_target1, "efxpt:pin", name="ddr1_r_data", type_name="RDATA_1", is_bus="true")
                    et.SubElement(gen_pin_target1, "efxpt:pin", name="ddr1_r_id", type_name="RID_1", is_bus="true")
                    et.SubElement(gen_pin_target1, "efxpt:pin", name="ddr1_r_resp", type_name="RRESP_1", is_bus="true")
                    et.SubElement(gen_pin_target1, "efxpt:pin", name="ddr1_w_data", type_name="WDATA_1", is_bus="true")
                    et.SubElement(gen_pin_target1, "efxpt:pin", name="ddr1_w_strb", type_name="WSTRB_1", is_bus="true")
                    et.SubElement(gen_pin_target1, "efxpt:pin", name="ddr1_resetn", type_name="ARSTN_1", is_bus="false")

                    gen_pin_controller = et.SubElement(ddr, "efxpt:gen_pin_controller")
                    et.SubElement(gen_pin_controller,"efxpt:pin", name="", type_name="CTRL_CLK", is_bus="false", is_clk="true", is_clk_invert="false")
                    et.SubElement(gen_pin_controller,"efxpt:pin", name="", type_name="CTRL_INT", is_bus="false")
                    et.SubElement(gen_pin_controller,"efxpt:pin", name="", type_name="CTRL_MEM_RST_VALID", is_bus="false")
                    et.SubElement(gen_pin_controller,"efxpt:pin", name="", type_name="CTRL_REFRESH", is_bus="false")
                    et.SubElement(gen_pin_controller,"efxpt:pin", name="", type_name="CTRL_BUSY", is_bus="false")
                    et.SubElement(gen_pin_controller,"efxpt:pin", name="", type_name="CTRL_CMD_Q_ALMOST_FULL", is_bus="false")
                    et.SubElement(gen_pin_controller,"efxpt:pin", name="", type_name="CTRL_DP_IDLE", is_bus="false")
                    et.SubElement(gen_pin_controller,"efxpt:pin", name="", type_name="CTRL_CKE", is_bus="true")
                    et.SubElement(gen_pin_controller,"efxpt:pin", name="", type_name="CTRL_PORT_BUSY", is_bus="true")

                    gen_pin_cfg_ctrl = et.SubElement(ddr, "efxpt:gen_pin_cfg_ctrl")
                    et.SubElement(gen_pin_cfg_ctrl,"efxpt:pin", name="cfg_done", type_name="CFG_DONE", is_bus="false")
                    et.SubElement(gen_pin_cfg_ctrl,"efxpt:pin", name="cfg_start", type_name="CFG_START", is_bus="false")
                    et.SubElement(gen_pin_cfg_ctrl,"efxpt:pin", name="cfg_reset", type_name="CFG_RESET", is_bus="false")
                    et.SubElement(gen_pin_cfg_ctrl,"efxpt:pin", name="cfg_sel", type_name="CFG_SEL", is_bus="false")

                    ctrl_reg_inf = et.SubElement(ddr, "efxpt:ctrl_reg_inf", is_reg_ena= "false")
                    gen_pin_ctrl_reg_inf = et.SubElement(ctrl_reg_inf, "efxpt:gen_pin_ctrl_reg_inf")
                    et.SubElement(gen_pin_ctrl_reg_inf,"efxpt:pin", name="axi0_ACLK", type_name="CR_ACLK", is_bus="false", is_clk="true", is_clk_invert="false")
                    et.SubElement(gen_pin_ctrl_reg_inf,"efxpt:pin", name="regARESETn", type_name="CR_ARESETN", is_bus="false")
                    et.SubElement(gen_pin_ctrl_reg_inf,"efxpt:pin", name="regARVALID", type_name="CR_ARVALID", is_bus="false")
                    et.SubElement(gen_pin_ctrl_reg_inf,"efxpt:pin", name="regARREADY", type_name="CR_ARREADY", is_bus="false")
                    et.SubElement(gen_pin_ctrl_reg_inf,"efxpt:pin", name="regAWVALID", type_name="CR_AWVALID", is_bus="false")
                    et.SubElement(gen_pin_ctrl_reg_inf,"efxpt:pin", name="regAWREADY", type_name="CR_AWREADY", is_bus="false")
                    et.SubElement(gen_pin_ctrl_reg_inf,"efxpt:pin", name="regBVALID", type_name="CR_BVALID", is_bus="false")
                    et.SubElement(gen_pin_ctrl_reg_inf,"efxpt:pin", name="regBREADY", type_name="CR_BREADY", is_bus="false")
                    et.SubElement(gen_pin_ctrl_reg_inf,"efxpt:pin", name="regRLAST", type_name="CR_RLAST", is_bus="false")
                    et.SubElement(gen_pin_ctrl_reg_inf,"efxpt:pin", name="regRVALID", type_name="CR_RVALID", is_bus="false")
                    et.SubElement(gen_pin_ctrl_reg_inf,"efxpt:pin", name="regRREADY", type_name="CR_RREADY", is_bus="false")
                    et.SubElement(gen_pin_ctrl_reg_inf,"efxpt:pin", name="regWLAST", type_name="CR_WLAST", is_bus="false")
                    et.SubElement(gen_pin_ctrl_reg_inf,"efxpt:pin", name="regWVALID", type_name="CR_WVALID", is_bus="false")
                    et.SubElement(gen_pin_ctrl_reg_inf,"efxpt:pin", name="regWREADY", type_name="CR_WREADY", is_bus="false")
                    et.SubElement(gen_pin_ctrl_reg_inf,"efxpt:pin", name="regARADDR", type_name="CR_ARADDR", is_bus="true")
                    et.SubElement(gen_pin_ctrl_reg_inf,"efxpt:pin", name="regARID", type_name="CR_ARID", is_bus="true")
                    et.SubElement(gen_pin_ctrl_reg_inf,"efxpt:pin", name="regARLEN", type_name="CR_ARLEN", is_bus="true")
                    et.SubElement(gen_pin_ctrl_reg_inf,"efxpt:pin", name="regARSIZE", type_name="CR_ARSIZE", is_bus="true")
                    et.SubElement(gen_pin_ctrl_reg_inf,"efxpt:pin", name="regARBURST", type_name="CR_ARBURST", is_bus="true")
                    et.SubElement(gen_pin_ctrl_reg_inf,"efxpt:pin", name="regAWADDR", type_name="CR_AWADDR", is_bus="true")
                    et.SubElement(gen_pin_ctrl_reg_inf,"efxpt:pin", name="regAWID", type_name="CR_AWID", is_bus="true")
                    et.SubElement(gen_pin_ctrl_reg_inf,"efxpt:pin", name="regAWLEN", type_name="CR_AWLEN", is_bus="true")
                    et.SubElement(gen_pin_ctrl_reg_inf,"efxpt:pin", name="regAWSIZE", type_name="CR_AWSIZE", is_bus="true")
                    et.SubElement(gen_pin_ctrl_reg_inf,"efxpt:pin", name="regAWBURST", type_name="CR_AWBURST", is_bus="true")
                    et.SubElement(gen_pin_ctrl_reg_inf,"efxpt:pin", name="regBID", type_name="CR_BID", is_bus="true")
                    et.SubElement(gen_pin_ctrl_reg_inf,"efxpt:pin", name="regBRESP", type_name="CR_BRESP", is_bus="true")
                    et.SubElement(gen_pin_ctrl_reg_inf,"efxpt:pin", name="regRDATA", type_name="CR_RDATA", is_bus="true")
                    et.SubElement(gen_pin_ctrl_reg_inf,"efxpt:pin", name="regRID", type_name="CR_RID", is_bus="true")
                    et.SubElement(gen_pin_ctrl_reg_inf,"efxpt:pin", name="regRRESP", type_name="CR_RRESP", is_bus="true")
                    et.SubElement(gen_pin_ctrl_reg_inf,"efxpt:pin", name="regWDATA", type_name="CR_WDATA", is_bus="true")
                    et.SubElement(gen_pin_ctrl_reg_inf,"efxpt:pin", name="regWSTRB", type_name="CR_WSTRB", is_bus="true")
                    et.SubElement(gen_pin_ctrl_reg_inf,"efxpt:pin", name="" ,type_name="CFG_PHY_RSTN", is_bus="false")
                    et.SubElement(gen_pin_ctrl_reg_inf,"efxpt:pin", name="" ,type_name="CTRL_RSTN", is_bus="false")

                    cs_fpga = et.SubElement(ddr, "efxpt:cs_fpga")
                    et.SubElement(cs_fpga,"efxpt:param", name="DQ_PULLDOWN_DRV", value="34.3", value_type="str")
                    et.SubElement(cs_fpga,"efxpt:param", name="DQ_PULLDOWN_ODT", value="60", value_type="str")
                    et.SubElement(cs_fpga,"efxpt:param", name="DQ_PULLUP_DRV", value="34.3", value_type="str")
                    et.SubElement(cs_fpga,"efxpt:param", name="DQ_PULLUP_ODT", value="Hi-Z", value_type="str")
                    et.SubElement(cs_fpga,"efxpt:param", name="FPGA_VREF_RANGE0", value="22.040", value_type="float")
                    et.SubElement(cs_fpga,"efxpt:param", name="FPGA_VREF_RANGE1", value="23.000", value_type="float")
                    et.SubElement(cs_fpga,"efxpt:param", name="MEM_FPGA_VREF_RANGE", value="Range 1", value_type="str")

                    cs_memory = et.SubElement(ddr, "efxpt:cs_memory")
                    et.SubElement(cs_memory,"efxpt:param", name="BLEN", value="BL=16 Sequential", value_type="str")
                    et.SubElement(cs_memory,"efxpt:param", name="CA_ODT_CS0", value="RZQ/4", value_type="str")
                    et.SubElement(cs_memory,"efxpt:param", name="CA_ODT_CS1", value="Disable", value_type="str")
                    et.SubElement(cs_memory,"efxpt:param", name="CA_VREF_RANGE0", value="27.200", value_type="float")
                    et.SubElement(cs_memory,"efxpt:param", name="CA_VREF_RANGE1", value="22.000", value_type="float")
                    et.SubElement(cs_memory,"efxpt:param", name="DQ_ODT_CS0", value="RZQ/4", value_type="str")
                    et.SubElement(cs_memory,"efxpt:param", name="DQ_ODT_CS1", value="Disable", value_type="str")
                    et.SubElement(cs_memory,"efxpt:param", name="DQ_VREF_RANGE0", value="20.000", value_type="float")
                    et.SubElement(cs_memory,"efxpt:param", name="DQ_VREF_RANGE1", value="27.200", value_type="float")
                    et.SubElement(cs_memory,"efxpt:param", name="MEM_CA_RANGE", value="RANGE[1]", value_type="str")
                    et.SubElement(cs_memory,"efxpt:param", name="MEM_DQ_RANGE", value="RANGE[1]", value_type="str")
                    et.SubElement(cs_memory,"efxpt:param", name="NWR", value="nWR=6", value_type="str")
                    et.SubElement(cs_memory,"efxpt:param", name="ODTD_CA_CS0", value="Obeys ODT_CA Bond Pad", value_type="str")
                    et.SubElement(cs_memory,"efxpt:param", name="ODTD_CA_CS1", value="Obeys ODT_CA Bond Pad", value_type="str")
                    et.SubElement(cs_memory,"efxpt:param", name="ODTE_CK_CS0", value="Override Disabled" ,value_type="str")
                    et.SubElement(cs_memory,"efxpt:param", name="ODTE_CK_CS1", value="Override Disabled" ,value_type="str")
                    et.SubElement(cs_memory,"efxpt:param", name="ODTE_CS_CS0", value="Override Disabled" ,value_type="str")
                    et.SubElement(cs_memory,"efxpt:param", name="ODTE_CS_CS1", value="Override Disabled" ,value_type="str")
                    et.SubElement(cs_memory,"efxpt:param", name="PDDS_CS0", value="RZQ/6", value_type="str")
                    et.SubElement(cs_memory,"efxpt:param", name="PDDS_CS1", value="RFU", value_type="str")
                    et.SubElement(cs_memory,"efxpt:param", name="RL_DBI_READ", value="Yes", value_type="str")
                    et.SubElement(cs_memory,"efxpt:param", name="RL_DBI_READ_DISABLED", value="RL=6,nRTP=8", value_type="str")
                    et.SubElement(cs_memory,"efxpt:param", name="RL_DBI_READ_ENABLED", value="RL=6,nRTP=8", value_type="str")
                    et.SubElement(cs_memory,"efxpt:param", name="RL_DBI_WRITE", value="Yes", value_type="str")
                    et.SubElement(cs_memory,"efxpt:param", name="WL_SET", value="Set A" ,value_type="str")
                    et.SubElement(cs_memory,"efxpt:param", name="WL_SET_A", value="WL=4", value_type="str")
                    et.SubElement(cs_memory,"efxpt:param", name="WL_SET_B", value="WL=4", value_type="str")

                    cs_memory_timing = et.SubElement(ddr, "efxpt:cs_memory_timing")
                    et.SubElement(cs_memory_timing,"efxpt:param", name="tCCD", value="8", value_type="int")
                    et.SubElement(cs_memory_timing,"efxpt:param", name="tCCDMW", value="32", value_type="int")
                    et.SubElement(cs_memory_timing,"efxpt:param", name="tFAW", value="40.000", value_type="float")
                    et.SubElement(cs_memory_timing,"efxpt:param", name="tPPD", value="4", value_type="int")
                    et.SubElement(cs_memory_timing,"efxpt:param", name="tRAS", value="42.000", value_type="float")
                    et.SubElement(cs_memory_timing,"efxpt:param", name="tRCD", value="18.000", value_type="float")
                    et.SubElement(cs_memory_timing,"efxpt:param", name="tRPab", value="21.000", value_type="float")
                    et.SubElement(cs_memory_timing,"efxpt:param", name="tRPpb", value="18.000", value_type="float")
                    et.SubElement(cs_memory_timing,"efxpt:param", name="tRRD", value="10.000", value_type="float")
                    et.SubElement(cs_memory_timing,"efxpt:param", name="tRTP", value="7.500", value_type="float")
                    et.SubElement(cs_memory_timing,"efxpt:param", name="tSR", value="15.000", value_type="float")
                    et.SubElement(cs_memory_timing,"efxpt:param", name="tWR", value="18.000", value_type="float")
                    et.SubElement(cs_memory_timing,"efxpt:param", name="tWTR", value="10.000", value_type="float")


                    pin_swap = et.SubElement(ddr, "efxpt:pin_swap")
                    et.SubElement(pin_swap,"efxpt:param", name="CA[0]", value="CA[0]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="CA[1]", value="CA[1]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="CA[2]", value="CA[2]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="CA[3]", value="CA[3]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="CA[4]", value="CA[4]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="CA[5]", value="CA[5]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="DM[0]", value="DM[0]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="DM[1]", value="DM[1]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="DM[2]", value="DM[2]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="DM[3]", value="DM[3]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="DQ[0]", value="DQ[3]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="DQ[10]", value="DQ[12]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="DQ[11]", value="DQ[11]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="DQ[12]", value="DQ[8]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="DQ[13]", value="DQ[10]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="DQ[14]", value="DQ[13]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="DQ[15]", value="DQ[14]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="DQ[16]", value="DQ[22]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="DQ[17]", value="DQ[17]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="DQ[18]", value="DQ[18]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="DQ[19]", value="DQ[19]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="DQ[1]", value="DQ[6]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="DQ[20]", value="DQ[16]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="DQ[21]", value="DQ[20]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="DQ[22]", value="DQ[21]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="DQ[23]", value="DQ[23]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="DQ[24]", value="DQ[29]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="DQ[25]", value="DQ[31]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="DQ[26]", value="DQ[28]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="DQ[27]", value="DQ[30]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="DQ[28]", value="DQ[25]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="DQ[29]", value="DQ[27]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="DQ[2]", value="DQ[4]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="DQ[30]", value="DQ[26]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="DQ[31]", value="DQ[24]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="DQ[3]", value="DQ[5]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="DQ[4]", value="DQ[0]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="DQ[5]", value="DQ[1]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="DQ[6]", value="DQ[7]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="DQ[7]", value="DQ[2]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="DQ[8]", value="DQ[15]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="DQ[9]", value="DQ[9]", value_type="str")
                    et.SubElement(pin_swap,"efxpt:param", name="ENABLE_PIN_SWAP", value="true", value_type="bool")

            platform.toolchain.ifacewriter.xml_blocks.append(DRAMXMLBlock())

            # DRAM AXI-Ports.
            # --------------
            ios = [(f"ddr0", 0,
                Subsignal("ar_valid",           Pins(1)), #
                Subsignal("ar_ready",           Pins(1)), #
                Subsignal("ar_addr",    Pins(33)), #32:0] 
                Subsignal("ar_id",      Pins(6)), #5:0] 
                Subsignal("ar_len",     Pins(8)), #7:0] 
                Subsignal("ar_size",    Pins(3)), #2:0] 
                Subsignal("ar_burst",   Pins(2)), #1:0] 
                Subsignal("ar_lock",    Pins(1)), #
                Subsignal("ar_apcmd",           Pins(1)), #
                Subsignal("ar_qos",     Pins(1)), #
                Subsignal("aw_valid",           Pins(1)), #
                Subsignal("aw_ready",           Pins(1)), #
                Subsignal("aw_addr",    Pins(33)), #32:0] 
                Subsignal("aw_id",      Pins(6)), #5:0] 
                Subsignal("aw_len",     Pins(8)), #7:0] 
                Subsignal("aw_size",    Pins(3)), #2:0] 
                Subsignal("aw_burst",   Pins(2)), #1:0] 
                Subsignal("aw_lock",    Pins(1)), #
                Subsignal("aw_cache",   Pins(4)), #3:0] 
                Subsignal("aw_qos",     Pins(1)), #
                Subsignal("aw_allstrb", Pins(1)), #
                Subsignal("aw_apcmd",           Pins(1)), #
                Subsignal("awcobuf",            Pins(1)), #
                Subsignal("w_valid",            Pins(1)), #
                Subsignal("w_ready",            Pins(1)), #
                Subsignal("w_data",     Pins(data_width)), #512-1:0] 
                Subsignal("w_strb",     Pins(data_width//8)), #64-1:0]
                Subsignal("w_last",     Pins(1)), #
                Subsignal("b_valid",            Pins(1)), #
                Subsignal("b_ready",            Pins(1)), #
                Subsignal("b_resp",     Pins(1)), #1:0] 
                Subsignal("b_id",       Pins(6)), #5:0] 
                Subsignal("r_valid",            Pins(1)), #
                Subsignal("r_ready",            Pins(1)), #
                Subsignal("r_data",     Pins(data_width)), #512-1:0] 
                Subsignal("r_id",       Pins(6)), #5:0] 
                Subsignal("r_resp",     Pins(2)), #1:0] 
                Subsignal("r_last",     Pins(1)), #
                Subsignal("resetn",     Pins(1)),
            )]

            io   = platform.add_iface_ios(ios)
            self.comb += [
                io.ar_valid.eq(axi_bus.ar.valid),
                axi_bus.ar.ready.eq(io.ar_ready),
                io.ar_addr.eq(axi_bus.ar.addr),
                io.ar_id.eq(axi_bus.ar.id),
                io.ar_len.eq(axi_bus.ar.len),
                io.ar_size.eq(axi_bus.ar.size),
                io.ar_burst.eq(axi_bus.ar.burst),
                io.ar_lock.eq(axi_bus.ar.lock),
                io.ar_apcmd.eq(0),
                io.ar_qos.eq(axi_bus.ar.qos),
                io.aw_valid.eq(axi_bus.aw.valid),
                axi_bus.aw.ready.eq(io.aw_ready),
                io.aw_addr.eq(axi_bus.aw.addr),
                io.aw_id.eq(axi_bus.aw.id),
                io.aw_len.eq(axi_bus.aw.len),
                io.aw_size.eq(axi_bus.aw.size),
                io.aw_burst.eq(axi_bus.aw.burst),
                io.aw_lock.eq(axi_bus.aw.lock),
                io.aw_cache.eq(axi_bus.aw.cache),
                io.aw_qos.eq(axi_bus.aw.qos),
                io.aw_allstrb.eq(0),
                io.aw_apcmd.eq(0),
                io.awcobuf.eq(0),
                io.w_valid.eq(axi_bus.w.valid),
                axi_bus.w.ready.eq(io.w_ready),
                io.w_data.eq(axi_bus.w.data),
                io.w_strb.eq(axi_bus.w.strb),
                io.w_last.eq(axi_bus.w.last),
                axi_bus.b.valid.eq(io.b_valid),
                io.b_ready.eq(axi_bus.b.ready),
                axi_bus.b.resp.eq(io.b_resp),
                axi_bus.b.id.eq(io.b_id),
                axi_bus.r.valid.eq(io.r_valid),
                io.r_ready.eq(axi_bus.r.ready),
                axi_bus.r.data.eq(io.r_data),
                axi_bus.r.id.eq(io.r_id),
                axi_bus.r.resp.eq(io.r_resp),
                axi_bus.r.last.eq(io.r_last),
                io.resetn.eq(~self.crg.cd_sys.rst),
            ]

            if hasattr(self.cpu, "add_memory_buses"):
                self.cpu.add_memory_buses(address_width = 32, data_width = data_width)

                assert len(self.cpu.memory_buses) == 1
                mbus = self.cpu.memory_buses[0]
                self.comb +=mbus.connect(axi_bus)
                
            cfgs = [(f"cfg", 0,
                Subsignal("start",  Pins(1)),
                Subsignal("reset",   Pins(1)),
                Subsignal("sel",    Pins(1)),
                Subsignal("done",    Pins(1)),
            )]

            cfg = platform.add_iface_ios(cfgs)
            self.cfg_state = Signal(1, reset=0)
            self.cfg_count = Signal(8, reset=0)

            self.comb += [
                cfg.sel.eq(0),
                cfg.reset.eq(self.cfg_state == 0),
                cfg.start.eq(self.cfg_state != 0),
            ]

            self.sync += self.cfg_count.eq(self.cfg_count + (self.cfg_count != 0xFF))
            self.sync += self.cfg_state.eq(self.cfg_state | (self.cfg_count == 0xFF))

            # Use DRAM's target0 port as Main Ram  -----------------------------------------------------
            self.bus.add_region("main_ram", SoCRegion(
                origin = 0x4000_0000,
                size   = 0x4000_0000, # 1GB.
                mode="rwx",
            ))

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=efinix_ti375_c529_dev_kit.Platform, description="LiteX SoC on Efinix Ti375 C529 Dev Kit.")
    parser.add_target_argument("--with-ohci",  action="store_true",       help="Enable USB OHCI.")
    sdopts = parser.target_group.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-sdcard",      action="store_true", help="Enable SPI-mode SDCard support.")
    sdopts.add_argument("--with-sdcard",          action="store_true", help="Enable SDCard support.")
    args = parser.parse_args()

    soc = BaseSoC(
        with_ohci  = args.with_ohci,
        **parser.soc_argdict)
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

    # if args.flash:
    #     from litex.build.openfpgaloader import OpenFPGALoader
    #     prog = OpenFPGALoader("titanium_ti375_c529")
    #     prog.flash(0, builder.get_bitstream_filename(mode="flash", ext=".hex")) # FIXME

if __name__ == "__main__":
    main()
