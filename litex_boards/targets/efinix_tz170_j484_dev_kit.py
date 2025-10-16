#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 Fin Maaß <f.maass@vogl-electronic.com>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import *

from litex.build.generic_platform import Subsignal, Pins

from litex_boards.platforms import efinix_tz170_j484_dev_kit

from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *

from litex.soc.interconnect import axi

from litex.soc.cores.clock.efinix import *

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, cpu_clk_freq):
        self.rst      = Signal()
        self.cd_sys   = ClockDomain()
        self.cd_cpu   = ClockDomain()
        self.cd_rst   = ClockDomain(reset_less=True)

        # # #

        # Clk/Rst.
        default_clk = platform.request(platform.default_clk_name)
        rst_n  = platform.request("user_btn", 0)

        self.comb += self.cd_rst.clk.eq(default_clk)

        # A pulse is necessary to do a reset.
        self.rst_pulse = Signal()
        last_rst = Signal()

        self.sync.rst += last_rst.eq(self.rst)
        self.sync.rst += self.rst_pulse.eq(~last_rst & self.rst)

        # PLL.
        self.pll = pll = TITANIUMPLL(platform)
        self.comb += pll.reset.eq(~rst_n | self.rst_pulse)
        pll.register_clkin(default_clk, platform.default_clk_freq)
        # You can use CLKOUT0 only for clocks with a maximum frequency of 4x
        # (integer) of the reference clock. If all your system clocks do not fall within
        # this range, you should dedicate one unused clock for CLKOUT0.
        pll.create_clkout(self.cd_sys, sys_clk_freq, with_reset=True)
        pll.create_clkout(self.cd_cpu, cpu_clk_freq)

        platform.add_false_path_constraints(self.cd_cpu.clk, self.cd_sys.clk)

class _CRG_DDR(LiteXModule):
    def __init__(self, platform):
        clk33 = platform.request("clk33")
        freq = 33.33e6

        # PLL.
        self.pll = pll = TITANIUMPLL(platform)
        self.comb += pll.reset.eq(ResetSignal())
        pll.register_clkin(clk33, freq)
        # You can use CLKOUT0 only for clocks with a maximum frequency of 4x
        # (integer) of the reference clock. If all your system clocks do not fall within
        # this range, you should dedicate one unused clock for CLKOUT0.
        pll.create_clkout(None,         freq)
        pll.create_clkout(None,         600e6, nclkout=4, margin=1e-02) # LPDDR4 ctrl

class EfinixLPDDR4(LiteXModule):
    def __init__(self, soc, axi_clk, own_crg=True):
        platform = soc.platform
        data_width = 512

        # DRAM Blocks.
        # ------------------
        from litex.build.efinix import InterfaceWriterBlock

        self.bus = axi_bus = axi.AXIInterface(data_width=data_width, address_width=33, id_width=8)

        if own_crg:
            self.ddr_crg = _CRG_DDR(platform)

        class EfinixDRAMBlock(InterfaceWriterBlock):
            @staticmethod
            def generate():
                name          = "ddr_inst1"
                ddr_def       = "DDR_0"
                clkin_sel     = "CLKIN 2"
                data_width    = "32"
                physical_rank = "1"
                mem_type      = "LPDDR4"
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
    def __init__(self, sys_clk_freq=100e6, cpu_clk_freq=175e6, with_spi_flash=False, spi_flash_number=0, spi_flash_rate="1:1", with_led_chaser=True, **kwargs):
        platform = efinix_tz170_j484_dev_kit.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, cpu_clk_freq)


        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Efinix Tz170 J484 Dev Kit", **kwargs)
        if hasattr(self.cpu, "cpu_clk"):
            self.comb += self.cpu.cpu_clk.eq(self.crg.cd_cpu.clk)


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
                mode   ="rwx",
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
            from litespi.modules import MX25U25645G
            from litespi.opcodes import SpiNorFlashOpCodes as Codes

            self.add_spi_flash(mode="4x",
                            clk_freq=133e6,
                            number=spi_flash_number,
                            module=MX25U25645G(Codes.READ_1_1_4_4B),
                            with_master=True,
                            extra_latency=0.5,
                            rate=spi_flash_rate,
            )

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            from litex.soc.cores.led import LedChaser
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)


# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=efinix_tz170_j484_dev_kit.Platform, description="LiteX SoC on Efinix Tz170 J484 Dev Kit.")
    parser.add_target_argument("--flash",               action="store_true",        help="Flash bitstream.")
    parser.add_target_argument("--sys-clk-freq",        default=100e6, type=float,  help="System clock frequency.")
    parser.add_target_argument("--cpu-clk-freq",        default=175e6, type=float,  help="CPU clock frequency.")
    sdopts = parser.target_group.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-sdcard",            action="store_true",        help="Enable SPI-mode SDCard support.")
    sdopts.add_argument("--with-sdcard",                action="store_true",        help="Enable SDCard support.")
    sdopts.add_argument("--with-sdcard-emulator",       action="store_true",        help="Enable SDCard (emulator) support.")
    parser.add_target_argument("--with-spi-flash",      action="store_true",        help="Enable SPI Flash.")
    parser.add_target_argument("--spi-flash-number",    default=0,     type=int,    help="SPI Flash number.", choices=[0, 1])
    parser.add_target_argument("--spi-flash-rate",      default="1:2", type=str,    help="SPI Flash rate.",   choices=["1:1", "1:2"])
    parser.add_target_argument("--with-led-chaser",     action="store_true",      help="Enable LED Chaser.")
    args = parser.parse_args()

    soc = BaseSoC(args.sys_clk_freq, args.cpu_clk_freq, args.with_spi_flash,
                  args.spi_flash_number, args.spi_flash_rate, args.with_led_chaser, **parser.soc_argdict)

    if args.with_spi_sdcard:
        soc.add_spi_sdcard()
    if args.with_sdcard:
        soc.add_sdcard()
    if args.with_sdcard_emulator:
        soc.add_sdcard(use_emulator=True)

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.flash(0, builder.get_bitstream_filename(mode="flash", ext=".hex"), device_id=0x00699A79)

if __name__ == "__main__":
    main()
