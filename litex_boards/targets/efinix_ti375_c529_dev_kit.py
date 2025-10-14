#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2024 Dolu1990 <charles.papon.90@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *
from litex.gen.genlib.misc import WaitTimer

from litex.build.io import DDROutput, DDRInput, SDROutput, SDRTristate
from litex.build.generic_platform import Subsignal, Pins, Misc, IOStandard

from litex_boards.platforms import efinix_ti375_c529_dev_kit

from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *

from litex.soc.interconnect import axi

from litex.soc.cores.clock.efinix import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.bitbang import I2CMaster
from litex.soc.cores.pwm import PWM

from litex.soc.cores.usb_ohci import USBOHCI

# Full stream debian demo :
# --cpu-type=vexiiriscv --cpu-variant=debian --update-repo=no --with-jtag-tap --with-sdcard --with-coherent-dma --with-ohci --vexii-video "name=video"
# --vexii-args="--fetch-l1-hardware-prefetch=nl --fetch-l1-refill-count=2 --fetch-l1-mem-data-width-min=128 --lsu-l1-mem-data-width-min=128 --lsu-software-prefetch --lsu-hardware-prefetch rpt --performance-counters 9 --lsu-l1-store-buffer-ops=32 --lsu-l1-refill-count 4 --lsu-l1-writeback-count 4 --lsu-l1-store-buffer-slots=4 --relaxed-div"
# --l2-bytes=524288 --sys-clk-freq 100000000 --cpu-clk-freq 200000000 --with-cpu-clk --bus-standard axi-lite --cpu-count=4 --build

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, cpu_clk_freq):
        self.rst    = Signal()
        self.cd_sys    = ClockDomain()
        self.cd_usb    = ClockDomain()
        self.cd_video  = ClockDomain()
        self.cd_cpu    = ClockDomain()
        self.cd_rst   = ClockDomain(reset_less=True)

        # # #

        # Clk/Rst.
        clk100 = platform.request("clk100")
        rst_n  = platform.request("user_btn", 0)

        self.comb += self.cd_rst.clk.eq(clk100)

        # A pulse is necessary to do a reset.
        self.rst_pulse = Signal()
        last_rst = Signal()

        self.sync.rst += last_rst.eq(self.rst)
        self.sync.rst += self.rst_pulse.eq(~last_rst & self.rst)

        # PLL.
        self.pll = pll = TITANIUMPLL(platform)
        self.comb += pll.reset.eq(~rst_n | self.rst_pulse)
        pll.register_clkin(clk100, platform.default_clk_freq)
        # You can use CLKOUT0 only for clocks with a maximum frequency of 4x
        # (integer) of the reference clock. If all your system clocks do not fall within
        # this range, you should dedicate one unused clock for CLKOUT0.
        pll.create_clkout(self.cd_sys, sys_clk_freq, with_reset=True)
        pll.create_clkout(self.cd_cpu, cpu_clk_freq)
        pll.create_clkout(self.cd_usb,         60e6, margin=0)
        pll.create_clkout(None,               800e6) # LPDDR4 ctrl
        pll.create_clkout(self.cd_video,       40e6)

        
        platform.add_false_path_constraints(self.cd_cpu.clk, self.cd_usb.clk)
        platform.add_false_path_constraints(self.cd_cpu.clk, self.cd_sys.clk)
        platform.add_false_path_constraints(self.cd_cpu.clk, self.cd_video.clk)
        platform.add_false_path_constraints(self.cd_sys.clk, self.cd_usb.clk)


class EfinixLPDDR4(LiteXModule):
    def __init__(self, soc, axi_clk):
        platform = soc.platform
        data_width = 512

        # DRAM Blocks.
        # ------------------
        from litex.build.efinix import InterfaceWriterBlock

        self.bus = axi_bus = axi.AXIInterface(data_width=data_width, address_width=33, id_width=8)

        class EfinixDRAMBlock(InterfaceWriterBlock):
            @staticmethod
            def generate():
                name          = "ddr_inst1"
                ddr_def       = "DDR_0"
                clkin_sel     = "CLKIN 0"
                data_width    = "32"
                physical_rank = "1"
                mem_type      = "LPDDR4x"
                mem_density   = "8G"

                cmd = []
                cmd.append('design.create_block("{}", "DDR")'.format(name))
                cmd.append('design.set_property("{}", "MEMORY_TYPE",    "{}", "DDR")'.format(name, mem_type))
                cmd.append('design.set_property("{}", "DQ_WIDTH",       "{}", "DDR")'.format(name, data_width))
                cmd.append('design.set_property("{}", "MEMORY_DENSITY", "{}", "DDR")'.format(name, mem_density))
                cmd.append('design.set_property("{}", "PHYSICAL_RANK",  "{}", "DDR")'.format(name, physical_rank))
                cmd.append('design.set_property("{}", "CLKIN_SEL",      "{}", "DDR")'.format(name, clkin_sel))

                cmd.append('design.set_property("{}","TARGET0_EN",      "1", "DDR")'.format(name))
                cmd.append('design.set_property("{}","TARGET1_EN",      "0", "DDR")'.format(name))

                cmd.append('design.set_property("{}","AXI0_ARADDR_BUS","ddr0_araddr", "DDR")'.format(name))
                cmd.append('design.set_property("{}","AXI0_ARAPCMD_PIN","ddr0_arapcmd", "DDR")'.format(name))
                cmd.append('design.set_property("{}","AXI0_ARBURST_BUS","ddr0_arburst", "DDR")'.format(name))
                cmd.append('design.set_property("{}","AXI0_ARID_BUS","ddr0_arid", "DDR")'.format(name))
                cmd.append('design.set_property("{}","AXI0_ARLEN_BUS","ddr0_arlen", "DDR")'.format(name))
                cmd.append('design.set_property("{}","AXI0_ARLOCK_PIN","ddr0_arlock", "DDR")'.format(name))
                cmd.append('design.set_property("{}","AXI0_ARQOS_PIN","ddr0_arqos", "DDR")'.format(name))
                cmd.append('design.set_property("{}","AXI0_ARREADY_PIN","ddr0_arready", "DDR")'.format(name))
                cmd.append('design.set_property("{}","AXI0_ARSIZE_BUS","ddr0_arsize", "DDR")'.format(name))
                cmd.append('design.set_property("{}","AXI0_ARSTN_PIN","ddr0_resetn", "DDR")'.format(name))
                cmd.append('design.set_property("{}","AXI0_ARVALID_PIN","ddr0_arvalid", "DDR")'.format(name))
                cmd.append('design.set_property("{}","AXI0_AWADDR_BUS","ddr0_awaddr", "DDR")'.format(name))
                cmd.append('design.set_property("{}","AXI0_AWALLSTRB_PIN","ddr0_awallstrb", "DDR")'.format(name))
                cmd.append('design.set_property("{}","AXI0_AWAPCMD_PIN","ddr0_awapcmd", "DDR")'.format(name))
                cmd.append('design.set_property("{}","AXI0_AWBURST_BUS","ddr0_awburst", "DDR")'.format(name))
                cmd.append('design.set_property("{}","AXI0_AWCACHE_BUS","ddr0_awcache", "DDR")'.format(name))
                cmd.append('design.set_property("{}","AXI0_AWCOBUF_PIN","ddr0_awcobuf", "DDR")'.format(name))
                cmd.append('design.set_property("{}","AXI0_AWID_BUS","ddr0_awid", "DDR")'.format(name))
                cmd.append('design.set_property("{}","AXI0_AWLEN_BUS","ddr0_awlen", "DDR")'.format(name))
                cmd.append('design.set_property("{}","AXI0_AWLOCK_PIN","ddr0_awlock", "DDR")'.format(name))
                cmd.append('design.set_property("{}","AXI0_AWQOS_PIN","ddr0_awqos", "DDR")'.format(name))
                cmd.append('design.set_property("{}","AXI0_AWREADY_PIN","ddr0_awready", "DDR")'.format(name))
                cmd.append('design.set_property("{}","AXI0_AWSIZE_BUS","ddr0_awsize", "DDR")'.format(name))
                cmd.append('design.set_property("{}","AXI0_AWVALID_PIN","ddr0_awvalid", "DDR")'.format(name))
                cmd.append('design.set_property("{}","AXI0_BID_BUS","ddr0_bid", "DDR")'.format(name))
                cmd.append('design.set_property("{}","AXI0_BREADY_PIN","ddr0_bready", "DDR")'.format(name))
                cmd.append('design.set_property("{}","AXI0_BRESP_BUS","ddr0_bresp", "DDR")'.format(name))
                cmd.append('design.set_property("{}","AXI0_BVALID_PIN","ddr0_bvalid", "DDR")'.format(name))
                cmd.append('design.set_property("{}","AXI0_CLK_INPUT_PIN","{}", "DDR")'.format(name, axi_clk))
                cmd.append('design.set_property("{}","AXI0_CLK_INVERT_EN","0", "DDR")'.format(name))
                cmd.append('design.set_property("{}","AXI0_DATA_WIDTH","512", "DDR")'.format(name))
                cmd.append('design.set_property("{}","AXI0_RDATA_BUS","ddr0_rdata", "DDR")'.format(name))
                cmd.append('design.set_property("{}","AXI0_RID_BUS","ddr0_rid", "DDR")'.format(name))
                cmd.append('design.set_property("{}","AXI0_RLAST_PIN","ddr0_rlast", "DDR")'.format(name))
                cmd.append('design.set_property("{}","AXI0_RREADY_PIN","ddr0_rready", "DDR")'.format(name))
                cmd.append('design.set_property("{}","AXI0_RRESP_BUS","ddr0_rresp", "DDR")'.format(name))
                cmd.append('design.set_property("{}","AXI0_RVALID_PIN","ddr0_rvalid", "DDR")'.format(name))
                cmd.append('design.set_property("{}","AXI0_WDATA_BUS","ddr0_wdata", "DDR")'.format(name))
                cmd.append('design.set_property("{}","AXI0_WLAST_PIN","ddr0_wlast", "DDR")'.format(name))
                cmd.append('design.set_property("{}","AXI0_WREADY_PIN","ddr0_wready", "DDR")'.format(name))
                cmd.append('design.set_property("{}","AXI0_WSTRB_BUS","ddr0_wstrb", "DDR")'.format(name))
                cmd.append('design.set_property("{}","AXI0_WVALID_PIN","ddr0_wvalid", "DDR")'.format(name))

                cmd.append('design.set_property("{}","CFG_DONE_PIN",   "cfg_done", "DDR")'.format(name))
                cmd.append('design.set_property("{}","CFG_RESET_PIN",  "cfg_reset", "DDR")'.format(name))
                cmd.append('design.set_property("{}","CFG_SEL_PIN",    "cfg_sel", "DDR")'.format(name))
                cmd.append('design.set_property("{}","CFG_START_PIN",  "cfg_start", "DDR")'.format(name))

                cmd.append('design.set_property("{}","CTRL_BUSY_PIN","", "DDR")'.format(name))
                cmd.append('design.set_property("{}","CTRL_CKE_PIN","", "DDR")'.format(name))
                cmd.append('design.set_property("{}","CTRL_CLK_INVERT_EN","0", "DDR")'.format(name))
                cmd.append('design.set_property("{}","CTRL_CLK_PIN","", "DDR")'.format(name))
                cmd.append('design.set_property("{}","CTRL_CMD_Q_ALMOST_FULL_PIN","", "DDR")'.format(name))
                cmd.append('design.set_property("{}","CTRL_DP_IDLE_PIN","", "DDR")'.format(name))
                cmd.append('design.set_property("{}","CTRL_INT_PIN","", "DDR")'.format(name))
                cmd.append('design.set_property("{}","CTRL_MEM_RST_VALID_PIN","", "DDR")'.format(name))
                cmd.append('design.set_property("{}","CTRL_PORT_BUSY_PIN","", "DDR")'.format(name))
                cmd.append('design.set_property("{}","CTRL_REFRESH_PIN","", "DDR")'.format(name))

                cmd.append('design.set_property("{}","PIN_SWIZZLE_CA","CA[0],CA[1],CA[2],CA[3],CA[4],CA[5]", "DDR")'.format(name))
                cmd.append('design.set_property("{}","PIN_SWIZZLE_DQM0","DQ[3],DQ[6],DQ[4],DQ[5],DQ[0],DQ[1],DQ[7],DQ[2],DM[0]", "DDR")'.format(name))
                cmd.append('design.set_property("{}","PIN_SWIZZLE_DQM1","DQ[15],DQ[9],DQ[12],DQ[11],DQ[8],DQ[10],DQ[13],DQ[14],DM[1]", "DDR")'.format(name))
                cmd.append('design.set_property("{}","PIN_SWIZZLE_DQM2","DQ[22],DQ[17],DQ[18],DQ[19],DQ[16],DQ[20],DQ[21],DQ[23],DM[2]", "DDR")'.format(name))
                cmd.append('design.set_property("{}","PIN_SWIZZLE_DQM3","DQ[29],DQ[31],DQ[28],DQ[30],DQ[25],DQ[27],DQ[26],DQ[24],DM[3]", "DDR")'.format(name))
                cmd.append('design.set_property("{}","PIN_SWIZZLE_EN","1", "DDR")'.format(name))

                cmd.append('design.assign_resource("{}", "{}","DDR")\n'.format(name, ddr_def))

                return '\n'.join(cmd) + '\n'

        platform.toolchain.ifacewriter.blocks.append(EfinixDRAMBlock())

        # DRAM AXI-Ports.
        # --------------
        axi_io = platform.add_iface_ios(axi_bus.get_ios("ddr0"))
        self.comb += axi_bus.connect_to_pads(axi_io, mode="master")

        ios = [(f"ddr0", 0,
            Subsignal("arapcmd",   Pins(1)),
            Subsignal("awallstrb", Pins(1)),
            Subsignal("awapcmd",   Pins(1)),
            Subsignal("awcobuf",    Pins(1)),
            Subsignal("resetn",     Pins(1)),
        )]

        io   = platform.add_iface_ios(ios)
        self.comb += [
            io.arapcmd.eq(0),
            io.awallstrb.eq(getattr(soc.cpu, "mBus_awallStrb", 0)),
            io.awapcmd.eq(0),
            io.awcobuf.eq(0),
            io.resetn.eq(~ResetSignal()),
        ]
            
        cfgs = [(f"cfg", 0,
            Subsignal("start",  Pins(1)),
            Subsignal("reset",  Pins(1)),
            Subsignal("sel",    Pins(1)),
            Subsignal("done",   Pins(1)),
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

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    mem_map = {**SoCCore.mem_map, **{
        "usb_ohci": 0xe0000000,
    }}

    def __init__(self,
            sys_clk_freq   = 100e6,
            cpu_clk_freq   = 100e6,
            with_spi_flash = False,
            spi_flash_number = 0,
            spi_flash_rate = "1:1",
            with_ethernet  = False,
            with_etherbone = False,
            eth_phy        = "rgmii",
            eth_ip         = "192.168.1.50",
            remote_ip      = None,
            with_ohci      = False,
            **kwargs):
        platform = efinix_ti375_c529_dev_kit.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, cpu_clk_freq)


        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Efinix Ti375 C529 Dev Kit", **kwargs)
        if hasattr(self.cpu, "cpu_clk"):
            self.comb += self.cpu.cpu_clk.eq(self.crg.cd_cpu.clk)

        # Fan --------------------------------------------------------------------------------------
        self.fan_pwm = PWM(
            pwm=platform.request("fan_speed_control", 0),
            with_csr       = True,
            default_enable = 1,
            default_width  = 0x800,
            default_period = 0xfff,
        )

        # USB OHCI ---------------------------------------------------------------------------------
        if with_ohci:
            _usb_pmod_ios = [
               ("usb_pmod1", 0,
                   Subsignal("dp", Pins("pmod1:0", "pmod1:1", "pmod1:2", "pmod1:3")),
                   Subsignal("dm", Pins("pmod1:4", "pmod1:5", "pmod1:6", "pmod1:7")),
                   IOStandard("3.3_V_LVCMOS"), Misc("DRIVE_STRENGTH=8"),
               )
            ]
            platform.add_extension(_usb_pmod_ios)
            self.submodules.usb_ohci = USBOHCI(platform, platform.request("usb_pmod1"), usb_clk_freq=int(60e6))
            self.bus.add_slave("usb_ohci_ctrl", self.usb_ohci.wb_ctrl, region=SoCRegion(origin=self.mem_map["usb_ohci"], size=0x100000, cached=False))
            self.dma_bus.add_master("usb_ohci_dma", master=self.usb_ohci.wb_dma)
            self.comb += self.cpu.interrupt[16].eq(self.usb_ohci.interrupt)

        # JTAG -------------------------------------------------------------------------------------
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
            self.comb += [
                self.cpu.jtag_clk.eq(jtag_pads.tck),
                self.cpu.jtag_tms.eq(jtag_pads.tms),
                self.cpu.jtag_tdi.eq(jtag_pads.tdi),
                jtag_pads.tdo.eq(self.cpu.jtag_tdo),
            ]
            platform.add_false_path_constraints(self.crg.cd_sys.clk, jtag_pads.tck)

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            # RGMII PHY.
            if eth_phy in ["rgmii"]:
                from liteeth.phy.titaniumrgmii import LiteEthPHYRGMII
                self.ethphy = LiteEthPHYRGMII(
                    platform           = platform,
                    clock_pads         = platform.request("eth_clocks"),
                    pads               = platform.request("eth"),
                    with_hw_init_reset = False,
                )

            # SFP / 1000 BaseX PHY.
            if eth_phy in ["sfp0", "sfp1"]:
                from liteeth.phy.titanium_lvds_1000basex import EfinixTitaniumLVDS_1000BASEX
                _sfp_lpc_ios = [
                    # SFP0.
                    ("sfp_lpc1", 0,
                        Subsignal("tx_enable", Pins("LPC:LA32_N")),
                        Subsignal("tx_p",      Pins("LPC:LA09_P")),
                        Subsignal("tx_n",      Pins("LPC:LA09_N")),
                        Subsignal("rx_p",      Pins("LPC:LA05_P LPC:LA06_P LPC:LA07_P LPC:LA08_P")),
                        Subsignal("rx_n",      Pins("LPC:LA05_N LPC:LA06_N LPC:LA07_N LPC:LA08_N")),
                        Subsignal("scl",       Pins("LPC:LA30_N")),
                        Subsignal("sda",       Pins("LPC:LA32_P")),

                    ),

                    # SFP1.
                    ("sfp_lpc1", 1,
                        Subsignal("tx_enable", Pins("LPC:LA16_P")),
                        Subsignal("tx_p",      Pins("LPC:LA01_CC_P")),
                        Subsignal("tx_n",      Pins("LPC:LA01_CC_N")),
                        Subsignal("rx_p",      Pins("LPC:LA00_CC_P LPC:LA02_P LPC:LA03_P LPC:LA04_P")),
                        Subsignal("rx_n",      Pins("LPC:LA00_CC_N LPC:LA02_N LPC:LA03_N LPC:LA04_N")),
                        Subsignal("scl",       Pins("LPC:LA19_P")),
                        Subsignal("sda",       Pins("LPC:LA19_N")),
                    )
                ]
                platform.add_extension(_sfp_lpc_ios)

                # 1000 BaseX PHY.
                ethphy_pads = platform.request("sfp_lpc1", int(eth_phy[-1]))
                self.ethphy = EfinixTitaniumLVDS_1000BASEX(
                    pads        = ethphy_pads,
                    refclk      = self.crg.cd_sys.clk,
                    refclk_freq = sys_clk_freq,
                    rx_delay    = [0, 0, 2, 2], # FIXME: Explain/Adjust.
                )
                self.comb += ethphy_pads.tx_enable.eq(1)

                # Link Up LED for Debug.
                self.comb += platform.request("user_led", 0).eq(self.ethphy.link_up)

                # # IRQ (if enabled).
                if hasattr(self.ethphy, "ev") and self.irq.enabled:
                    self.irq.add("ethphy", use_loc_if_exists=True)

            # Timing Constraints.
            platform.add_false_path_constraints(
                self.crg.cd_sys.clk,
                self.ethphy.crg.cd_eth_rx.clk,
                self.ethphy.crg.cd_eth_tx.clk,
            )
            if with_etherbone:
                self.add_etherbone(
                    phy                     = self.ethphy,
                    ip_address              = eth_ip,
                    with_timing_constraints = False,
                    with_ethmac            =  with_ethernet,
                )
            elif with_ethernet:
                self.add_ethernet(
                    phy                     = self.ethphy,
                    local_ip                = eth_ip,
                    remote_ip               = remote_ip,
                    software_debug          = False,
                    with_timing_constraints = False,
                )

        # HDMI -------------------------------------------------------------------------------------
        if hasattr(self.cpu, "video_clk"):
            _hdmi_io = efinix_ti375_c529_dev_kit.hdmi_px("p1")
            self.platform.add_extension(_hdmi_io)
            self.submodules.videoi2c = I2CMaster(platform.request("hdmi_i2c"))

            self.videoi2c.add_init(addr=0x72>>1, init=[
                # # video input/output mode
                (0xD6, 0xC0),
                (0x15, 0x01),
                (0x16, 0x38),
                (0x18, 0xE7),
                (0x19, 0x34),
                (0x1A, 0x04),
                (0x1B, 0xAD),
                (0x1C, 0x00),
                (0x1D, 0x00),
                (0x1E, 0x1C),
                (0x1F, 0x1B),
                (0x20, 0x1D),
                (0x21, 0xDC),
                (0x22, 0x04),
                (0x23, 0xAD),
                (0x24, 0x1F),
                (0x25, 0x24),
                (0x26, 0x01),
                (0x27, 0x35),
                (0x28, 0x00),
                (0x29, 0x00),
                (0x2A, 0x04),
                (0x2B, 0xAD),
                (0x2C, 0x08),
                (0x2D, 0x7C),
                (0x2E, 0x1B),
                (0x2F, 0x77),
                (0x41, 0x10),
                (0x48, 0x08), # (right justified
                (0x55, 0x00),
                (0x56, 0x28),
                (0x96, 0xC0),
                (0x98, 0x03),
                (0x9A, 0xE0),
                (0x9C, 0x30),
                (0x9D, 0x61),
                (0xA2, 0xA4),
                (0xA3, 0xA4),
                (0xAF, 0x06),
                (0xBA, 0x60),
                (0xD6, 0xC0),
                (0xE0, 0xD0),
                (0xDF, 0x01),
                (0x9A, 0xE0),
                (0xFD, 0xE0),
                (0xFE, 0x80),
                (0xF9, 0x00),
                (0x7F, 0x00),
                (0x94, 0x00),
                (0xE2, 0x01),
                (0x41, 0x10),
            ])

            clk_video = self.crg.cd_video.clk
            self.comb += self.cpu.video_clk.eq(self.crg.cd_video.clk)
            video_data = platform.request("hdmi_data")
            self.specials += DDROutput(i1=Signal(reset=0b0),       i2=Signal(reset=0b1),        o=video_data.clk, clk=clk_video)
            self.specials += DDROutput(i1=self.cpu.video_color_en, i2=self.cpu.video_color_en,  o=video_data.de,  clk=clk_video)
            for i in range(self.cpu.video_color.nbits):
                self.specials += DDROutput(i1=self.cpu.video_color[i], i2=self.cpu.video_color[i],  o=video_data.d[i], clk=clk_video)

            video_sync = platform.request("hdmi_sync")
            self.specials += SDRTristate(io=video_sync.vsync, o=Signal(reset=0b0), oe=self.cpu.video_vsync, i=Signal(), clk=clk_video)
            self.specials += SDRTristate(io=video_sync.hsync, o=Signal(reset=0b0), oe=self.cpu.video_hsync, i=Signal(), clk=clk_video)

 		# Debug pins -----------------------------------------------------------------------------
        if hasattr(self.cpu, "tracer_payload"):
            _debug_io = [
                ("debug_io", 0,
                 Subsignal("p0", Pins("pmod2:0")),
                 Subsignal("p1", Pins("pmod2:1")),
                 Subsignal("p2", Pins("pmod2:2")),
                 Subsignal("p3", Pins("pmod2:3")),
                 Subsignal("p4", Pins("pmod2:4")),
                 Subsignal("p5", Pins("pmod2:5")),
                 Subsignal("p6", Pins("pmod2:6")),
                 Subsignal("p7", Pins("pmod2:7")),
                 IOStandard("3.3_V_LVCMOS"),
                 Misc("SLEWRATE=1"), Misc("DRIVE_STRENGTH=8")
                 )
            ]
            
            self.platform.add_extension(_debug_io)
            debug_io = platform.request("debug_io")

            self.comb += debug_io.p0.eq(self.cpu.tracer_payload[0])
            self.comb += debug_io.p1.eq(self.cpu.tracer_payload[1])
            self.comb += debug_io.p2.eq(self.cpu.tracer_payload[2])
            self.comb += debug_io.p3.eq(self.cpu.tracer_payload[3])
            self.comb += debug_io.p4.eq(self.cpu.tracer_payload[4])
            self.comb += debug_io.p5.eq(self.cpu.tracer_payload[5])
            self.comb += debug_io.p6.eq(self.cpu.tracer_payload[6])
            self.comb += debug_io.p7.eq(self.cpu.tracer_payload[7])

        # CPU-ETH -----------------------------------------------------------------------------
        if hasattr(self.cpu, "eth_tx_ref_clk"):
            self.cd_eth    = ClockDomain()
            self.cd_eth_90 = ClockDomain()
            self.cd_eth_rx = ClockDomain()

            clk25  = platform.request("clk25")

            # PLL eth tx
            self.pll2 = pll2 = TITANIUMPLL(platform)
            self.comb += pll2.reset.eq(ResetSignal())
            pll2.register_clkin(clk25, 25e6)
            # You can use CLKOUT0 only for clocks with a maximum frequency of 4x
            # (integer) of the reference clock. If all your system clocks do not fall within
            # this range, you should dedicate one unused clock for CLKOUT0.
            pll2.create_clkout(None, 25e6, with_reset=True)
            pll2.create_clkout(self.cd_eth, 125e6)
            pll2.create_clkout(self.cd_eth_90, 125e6, phase=90)

            # PLL eth rx
            self.pll3 = pll3 = TITANIUMPLL(platform)
            self.comb += pll3.reset.eq(ResetSignal())
            self.eth_clocks = eth_clocks = platform.request("eth_clocks")
            pll3.register_clkin(eth_clocks.rx, 125e6)
            # You can use CLKOUT0 only for clocks with a maximum frequency of 4x
            # (integer) of the reference clock. If all your system clocks do not fall within
            # this range, you should dedicate one unused clock for CLKOUT0.
            pll3.create_clkout(None, 125e6, with_reset=True)
            pll3.create_clkout(self.cd_eth_rx, 125e6,phase =270)

            platform.add_false_path_constraints(self.crg.cd_sys.clk, self.cd_eth.clk)

            eth = platform.request("eth")
            # eth_clocks = platform.request("eth_clocks")

            self.comb += self.cpu.eth_tx_ref_clk .eq(self.cd_eth.clk)
            self.specials += DDROutput(i1=self.cpu.eth_tx_clk[0], i2=self.cpu.eth_tx_clk[1],  o=eth_clocks.tx, clk=self.cd_eth_90.clk)
            self.specials += DDROutput(i1=self.cpu.eth_tx_ctl[0], i2=self.cpu.eth_tx_ctl[1],  o=eth.tx_ctl, clk=self.cd_eth.clk)
            for i in range(4):
                self.specials += DDROutput(i1=self.cpu.eth_tx_d[0+i], i2=self.cpu.eth_tx_d[4+i], o=eth.tx_data[i], clk=self.cd_eth.clk)

            # Rx using pll
            self.comb += self.cpu.eth_rx_clk .eq(self.cd_eth_rx.clk)
            self.specials += DDRInput(o1=self.cpu.eth_rx_ctl[0], o2=self.cpu.eth_rx_ctl[1],  i=eth.rx_ctl, clk=self.cd_eth_rx.clk)
            for i in range(4):
                self.specials += DDRInput(o1=self.cpu.eth_rx_d[0+i], o2=self.cpu.eth_rx_d[4+i], i=eth.rx_data[i], clk=self.cd_eth_rx.clk)

            # self.specials += DDROutput(i1=self.cpu.eth_rx_d[0], i2=self.cpu.eth_rx_d[4], o=debug_io.p0, clk=self.cd_eth_rx.clk)
            # self.specials += DDROutput(i1=self.cpu.eth_rx_d[1], i2=self.cpu.eth_rx_d[5], o=debug_io.p1, clk=self.cd_eth_rx.clk)
            # self.specials += DDROutput(i1=self.cpu.eth_rx_d[2], i2=self.cpu.eth_rx_d[6], o=debug_io.p2, clk=self.cd_eth_rx.clk)
            # self.specials += DDROutput(i1=self.cpu.eth_rx_d[3], i2=self.cpu.eth_rx_d[7], o=debug_io.p3, clk=self.cd_eth_rx.clk)
            # self.specials += DDROutput(i1=Signal(reset=1), i2=Signal(reset=0), o=debug_io.p4, clk=self.cd_eth_rx.clk)
            # self.specials += DDROutput(i1=self.cpu.eth_rx_ctl[0], i2=self.cpu.eth_rx_ctl[1], o=debug_io.p5, clk=self.cd_eth_rx.clk)


        # LPDDR4 SDRAM -----------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            if hasattr(self.cpu, "add_memory_buses") and hasattr(self.cpu, "cpu_clk"):
                axi_clk = self.crg.cd_cpu.clk.name_override
            else:
                axi_clk = self.crg.cd_sys.clk.name_override

            self.ddr = EfinixLPDDR4(self, axi_clk)
            axi_bus = self.ddr.bus

            soc_region = SoCRegion(
                origin = self.mem_map.get("main_ram", None),
                size   = 0x4000_0000, # 1GB.
                mode   = "rwx",
            )
            # Use DRAM's target0 port as Main Ram.
            if hasattr(self.cpu, "add_memory_buses"):
                self.cpu.add_memory_buses(address_width = 32, data_width = axi_bus.data_width)

                assert len(self.cpu.memory_buses) == 1
                mbus = self.cpu.memory_buses[0]
                self.comb +=mbus.connect(axi_bus)
                self.bus.add_region("main_ram", soc_region)
            else:
                axi_lite_bus = axi.AXILiteInterface(data_width=axi_bus.data_width, address_width=axi_bus.address_width)
                self.submodules += axi.AXILite2AXI(axi_lite_bus, axi_bus)
                self.bus.add_slave("main_ram", axi_lite_bus, soc_region)
        
        # SPI Flash --------------------------------------------------------------------------------
        if with_spi_flash:
            from litespi.modules import IS25WP512M
            from litespi.opcodes import SpiNorFlashOpCodes as Codes

            self.add_spi_flash(mode="4x",
                            clk_freq=112e6,
                            number=spi_flash_number,
                            module=IS25WP512M(Codes.READ_1_1_4_4B),
                            with_master=True,
                            extra_latency=0.5,
                            rate=spi_flash_rate,
            )

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=efinix_ti375_c529_dev_kit.Platform, description="LiteX SoC on Efinix Ti375 C529 Dev Kit.")
    parser.add_target_argument("--flash",         action="store_true",       help="Flash bitstream.")
    parser.add_target_argument("--sys-clk-freq",  default=100e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--cpu-clk-freq",  default=100e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-spi-flash",      action="store_true",        help="Enable SPI Flash.")
    parser.add_target_argument("--spi-flash-number",    default=0,     type=int,    help="SPI Flash number.", choices=[0, 1])
    parser.add_target_argument("--spi-flash-rate",      default="1:2", type=str,    help="SPI Flash rate.",   choices=["1:1", "1:2"])
    parser.add_target_argument("--with-ohci",     action="store_true",       help="Enable USB OHCI.")
    parser.add_target_argument("--with-emmc",     action="store_true",       help="Enable SDCard support (use eMMC).")
    sdopts = parser.target_group.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-sdcard",      action="store_true", help="Enable SPI-mode SDCard support.")
    sdopts.add_argument("--with-sdcard",          action="store_true", help="Enable SDCard support.")
    parser.add_target_argument("--with-ethernet",   action="store_true",     help="Enable Ethernet support.")
    parser.add_target_argument("--with-etherbone",  action="store_true",     help="Enable Etherbone support.")
    parser.add_target_argument("--eth-phy",   default="rgmii", type=str, help="Ethernet PHY.", choices=["rgmii", "sfp0", "sfp1"])
    parser.add_target_argument("--eth-ip",    default="192.168.1.50",    help="Ethernet/Etherbone IP address.")
    parser.add_target_argument("--remote-ip", default="192.168.1.100",   help="Remote IP address of TFTP server.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq   = args.sys_clk_freq,
        cpu_clk_freq   = args.cpu_clk_freq,
        with_ohci      = args.with_ohci,
        with_ethernet  = args.with_ethernet,
        with_etherbone = args.with_etherbone,
        eth_phy        = args.eth_phy,
        eth_ip         = args.eth_ip,
        remote_ip      = args.remote_ip,
        **parser.soc_argdict)
    if args.with_spi_sdcard:
        soc.add_spi_sdcard()
    if args.with_sdcard:
        soc.add_sdcard()
    if args.with_emmc:
        soc.add_sdcard(name="mmc", sdcard_name="emmc")

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.flash(0, builder.get_bitstream_filename(mode="flash", ext=".hex"), device_id=0x006A0A79)

if __name__ == "__main__":
    main()
