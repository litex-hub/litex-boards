#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
# Copyright (c) 2019 msloniewski <marcin.sloniewski@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

import os
import re
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory

from migen import Cat, ClockDomain, ClockDomainsRenamer, ClockSignal, If, Instance, Mux, Replicate, ResetSignal, Signal
from migen.genlib.cdc import MultiReg
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.build.io import DDRInput, DDROutput, DifferentialInput
from litex.gen import LiteXModule
from litex.soc.cores.bitbang import I2CMaster
from litex.soc.cores.clock import CycloneVPLL
from litex.soc.cores.led import LedChaser
from litex.soc.integration.builder import Builder
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.soc_core import SoCCore
from litex.soc.interconnect import csr_bus, stream, wishbone
from litex.soc.interconnect.csr import CSRStatus, CSRStorage

from litex_boards.platforms import altera_cyclonev_gt_devkit

# Native DDR3B -------------------------------------------------------------------------------------

_IP_PREFIX = "q_sys_smc_0_mem_if_ddr3_emif_0"
_IO_WRAPPERS = (
    "altdq_dqs2_acv_cyclonev.sv",
    "altera_mem_if_dll_cyclonev.sv",
    "altera_mem_if_oct_cyclonev.sv",
    f"{_IP_PREFIX}_pll0.sv",
    f"{_IP_PREFIX}_p0_addr_cmd_pads.v",
    f"{_IP_PREFIX}_p0_acv_ldc.v",
    f"{_IP_PREFIX}_p0_clock_pair_generator.v",
)


def generate_native_lane_sources(output_dir):
    """Generate the standalone wrappers with the installed Quartus toolchain."""
    quartus_root = os.environ.get("QUARTUS_ROOTDIR")
    if quartus_root is None:
        quartus_map = shutil.which("quartus_map")
        if quartus_map is None:
            raise OSError("Put Quartus on PATH, set QUARTUS_ROOTDIR, or pass --ddr3b-ip-dir")
        quartus_root = Path(quartus_map).resolve().parent.parent
    generator = Path(quartus_root).resolve() / "sopc_builder" / "bin" / "ip-generate"
    output_dir = Path(output_dir).resolve()
    with TemporaryDirectory(prefix="cyclonev-ddr3b-") as temp:
        # Quartus emits the wrappers as part of its DDR3 IP generation.
        # Keep the I/O wrappers used by the native PHY.
        subprocess.run([
            str(generator), "--component-name=altera_mem_if_ddr3_emif",
            "--file-set=QUARTUS_SYNTH", "--part=5CGTFD9E5F35C7",
            f"--output-name={_IP_PREFIX}", f"--output-directory={temp}",
            "--preset=MICRON MT41J128M16HA-125",
            "--component-parameter=SPEED_GRADE=7",
            "--component-parameter=MEM_CLK_FREQ=300.0",
            "--component-parameter=REF_CLK_FREQ=100.0",
            "--component-parameter=MEM_DQ_WIDTH=64",
            "--component-parameter=MEM_TCL=6",
            "--component-parameter=MEM_WTCL=5",
        ], cwd=temp, check=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        for name in _IO_WRAPPERS:
            shutil.copyfile(Path(temp) / "submodules" / name, output_dir / name)


def add_write_leveling_ports(source, output):
    # Keep the hard DDR clocking and allow the PHY to hold DQS low
    # between write-leveling pulses.
    text = source.read_text()
    edits = (
        ("\n\tread_data_out,", "\n\tread_data_out,\n\tlevel_enable, level_strobe,"),
        ("output [fpga_width_out-1:0] read_data_out;",
         "output [fpga_width_out-1:0] read_data_out;\n"
         "input level_enable;\ninput [1:0] level_strobe;"),
        ("assign clk_gate_hi = 1'b1;", "assign clk_gate_hi = level_enable ? level_strobe[0] : 1'b1;"),
        ("assign clk_gate_lo = 1'b1;", "assign clk_gate_lo = level_enable ? level_strobe[1] : 1'b1;"),
    )
    for old, new in edits:
        if text.count(old) != 1:
            raise ValueError(f"Unexpected ALTDQ_DQS2 source for write leveling: {old}")
        text = text.replace(old, new)
    output.write_text(text)


def add_native_lane_sources(platform, ip_dir, gateware_dir, *, with_ddr3a):
    """Add the generated I/O wrappers and constrain DDR3B on the GT kit."""
    for name in _IO_WRAPPERS:
        source = Path(ip_dir).resolve() / name
        if not source.is_file():
            raise FileNotFoundError(f"Missing generated Cyclone V DDR3B wrapper: {source}")
        if name == _IO_WRAPPERS[0]:
            output = Path(gateware_dir).resolve() / "cyclonev_ddr3b_io.sv"
            output.parent.mkdir(parents=True, exist_ok=True)
            add_write_leveling_ports(source, output)
            source = output
        platform.add_source(str(source))

    # Match the reference PLL feedback assignment and declare the incoming
    # read strobe as a source-synchronous clock for the hard read FIFO.
    platform.add_platform_command(
        f"set_instance_assignment -name PLL_COMPENSATION_MODE DIRECT -to {_IP_PREFIX}_pll0|fbout")
    phy_prefix = "basesoc_" if with_ddr3a else ""
    # Place the northmost LFIFO capture beside its I/O lane, and
    # center each reset release flop within its four-byte FIFO group.
    platform.toolchain.additional_qsf_commands += [
        f'set_location_assignment FF_X120_Y89_N4 -to "{phy_prefix}cyclonevddrphy_cyclonevddr3lane_captured_valid[7]"',
        "set_location_assignment FF_X120_Y48_N13 -to ars_cd_lfifo_reset0_ff1",
        "set_location_assignment FF_X120_Y48_N46 -to ars_cd_vfifo_reset0_ff1",
        "set_location_assignment FF_X120_Y77_N17 -to ars_cd_lfifo_reset1_ff1",
        "set_location_assignment FF_X120_Y77_N43 -to ars_cd_vfifo_reset1_ff1",
        "set_instance_assignment -name REMOVE_DUPLICATE_REGISTERS OFF -to ars_cd_lfifo_reset*",
        "set_instance_assignment -name REMOVE_DUPLICATE_REGISTERS OFF -to ars_cd_vfifo_reset*",
    ]
    platform.toolchain.additional_sdc_commands += [
        # TimeQuest collection order is independent of the port bit index.
        "for {set lane 0} {$lane < 8} {incr lane} { "
        "set dqs [get_ports [format {ddram_dqs_p[%d]} $lane]]; "
        "create_clock -name ddr3b_read_dqs_$lane -period 3.333 $dqs }",
        # The returning DQS burst has no fixed phase to the PLL. The reference
        # EMIF excludes this hard postamble arc from generic STA and checks
        # its margin separately against the SDRAM round-trip timing.
        "set_false_path "
        "-from [get_registers {altdq_dqs2_acv_cyclonev:ddr3b_lane*|dqs_enable_ctrl~DQSENABLEOUT_DFF}] "
        "-to [get_registers {altdq_dqs2_acv_cyclonev:ddr3b_lane*|dqs_delay_chain~POSTAMBLE_DFF}]",
        # The FIFO write clock is a returning burst strobe. The startup
        # sequencer releases reset while DQS is idle, before enabling reads.
        # The lock synchronizer clears before the release register can rise.
        "set_false_path -from [get_registers {*cyclonevddr3lane_rfifo_release* ars_cd_dll_init_ff1}] "
        "-to [get_registers {altdq_dqs2_acv_cyclonev:ddr3b_lane*|input_path_gen*.read_fifo~WRITE_ADDRESS_DFF}]",
        "create_generated_clock -name ddr_sys -divide_by 2 "
        "-source [get_pins {sys_clk|clk}] [get_registers {sys_clk}]",
        "set_multicycle_path -setup -end 2 -from [get_clocks ddr_sys] -to [get_registers {*afi_frame_*}]",
        "set_multicycle_path -hold -end 1 -from [get_clocks ddr_sys] -to [get_registers {*afi_frame_*}]",
        # Calibration status is launched only on the AFI edge that raises
        # ddr_sys. The destination samples it on the next ddr_sys edge.
        "set cal_launch [get_registers {*afi_cal_snapshot*}]",
        "set cal_capture [get_registers {*sys_cal_first*}]",
        "set_multicycle_path -setup -start 2 -from $cal_launch -to $cal_capture",
        "set_multicycle_path -hold -start 1 -from $cal_launch -to $cal_capture",
        # Match UniPHY's half-rate to full-rate LFIFO configuration timing.
        "set lfifo_cfg [get_registers {*cyclonevddr3lane_settings_cdc_o*}]",
        "set lfifo_latency [get_registers {altdq_dqs2_acv_cyclonev:ddr3b_lane*|lfifo~RD_LATENCY_DFF*}]",
        "set_multicycle_path -setup -end 2 -from $lfifo_cfg -to $lfifo_latency",
        "set_multicycle_path -hold -end 1 -from $lfifo_cfg -to $lfifo_latency",
        # The reference EMIF excludes hard phase-mux select arcs. Match the
        # PLL output pin specifically so AFI fabric data remains timed.
        "set phy_mux_clk [get_pins -compatibility_mode {*pll1_phy~PLL_OUTPUT_COUNTER|divclk}]",
        "set phy_mux_out [get_registers {"
        "altdq_dqs2_acv_cyclonev:ddr3b_lane*|os_oe_reg "
        "altdq_dqs2_acv_cyclonev:ddr3b_lane*|phase_align_os~DFF* "
        "altdq_dqs2_acv_cyclonev:ddr3b_lane*|os_oct_ddio_oe~DFF "
        "altdq_dqs2_acv_cyclonev:ddr3b_lane*|lfifo~LFIFO_IN_READ_EN_DFF "
        "altdq_dqs2_acv_cyclonev:ddr3b_lane*|vfifo~QVLD_IN_DFF}]",
        "set_false_path -from $phy_mux_clk -to $phy_mux_out",
        # Same dedicated hard FIFO arc excluded by the reference EMIF.
        "set lfifo_read_en [get_registers {altdq_dqs2_acv_cyclonev:ddr3b_lane*|lfifo~LFIFO_OUT_RDEN_DFF}]",
        "set rfifo_read_addr [get_registers {altdq_dqs2_acv_cyclonev:ddr3b_lane*|input_path_gen*.read_fifo~READ_ADDRESS_DFF}]",
        "set_false_path -from $lfifo_read_en -to $rfifo_read_addr",
        # Toggle-based CDC terminates at stage zero of the Migen MultiReg.
        # Leave subsequent stages and the bundled data bus timed.
        "set_false_path "
        "-from [get_registers {*cyclonevddr3lane_vfifo_increment_toggle_i *cyclonevddr3lane_*_cdc_*_toggle_i}] "
        "-to [get_registers -nowarn {*multiregimpl*0 *multiregimpl*0~*}]",
        # Write-leveling mode and trigger cross into AFI. The latched
        # feedback returns to sys and remains steady until the next strobe.
        "set_false_path "
        "-from [get_registers -nowarn {*cyclonevddrphy_wlevel_en_storage* "
        "*cyclonevddr3lane_level_strobe_cdc_toggle_i *cyclonevddr3lane_feedback[*]}] "
        "-to [get_registers -nowarn {*multiregimpl*0 *multiregimpl*0~* *multiregimpl*0[*]}]",
        # The request synchronizer and its extra destination register
        # give the bundled data a full clock of margin. Limit its route
        # delay to less than one AFI period, independent of clock skew.
        "set lane_cdc_data [get_registers {*cyclonevddr3lane_*_cdc_ibuffer*}]",
        "set lane_cdc_stage [get_registers {*multiregimpl*}]",
        "set_false_path -from $lane_cdc_data -to $lane_cdc_stage",
        "set_net_delay -max 5.000 -from $lane_cdc_data -to $lane_cdc_stage",
        "set fifo_gray [get_registers {*cyclonevddrphy*graycounter*_q*}]",
        "set fifo_sync [get_registers {*multiregimpl*0*}]",
        "set_false_path -from $fifo_gray -to $fifo_sync",
        "set_net_delay -max 6.666 -from $fifo_gray -to $fifo_sync",
        # Only the asynchronous assertion pins of the reset synchronizers
        # are exempt. Time the stage-to-stage and FIFO release paths.
        "set fifo_reset_async [get_pins -compatibility_mode "
        "{ars_cd_lfifo_reset*_ff*|clrn ars_cd_vfifo_reset*_ff*|clrn}]",
        "set_false_path -to $fifo_reset_async",
        "set_false_path -to [get_registers {*ars_cd_sys_ff* *ars_cd_afi_ff*}]",
    ]

    # DDR3B drive and termination assignments for the GT kit.
    pads = platform.lookup_request("ddram", number=0)
    data = ("dq", "dqs_p", "dqs_n")
    clocks = ("clk_p", "clk_n")
    command = ("a", "ba", "cs_n", "we_n", "ras_n", "cas_n", "odt", "cke", "reset_n")
    for kind, setting, fields in (
        ("INPUT_TERMINATION", '"PARALLEL 50 OHM WITH CALIBRATION"', data),
        ("OUTPUT_TERMINATION", '"SERIES 50 OHM WITH CALIBRATION"', (*data, "dm")),
        ("OUTPUT_TERMINATION", '"SERIES 50 OHM WITHOUT CALIBRATION"', clocks),
        ("CURRENT_STRENGTH_NEW", '"MAXIMUM CURRENT"', command),
        ("PACKAGE_SKEW_COMPENSATION", "OFF", (*data, "dm", *clocks, *command)),
    ):
        for field in fields:
            pad = getattr(pads, field)
            indices = range(len(pad)) if len(pad) > 1 else (None,)
            for index in indices:
                suffix = f"[{index}]" if index is not None else ""
                platform.add_platform_command(
                    f"set_instance_assignment -name {kind} {setting} -to {{pad}}{suffix}", pad=pad)

# DDR3A --------------------------------------------------------------------------------------------

class _WriteBurstPacker(LiteXModule):
    """Group adjacent native writes into aligned Avalon bursts of up to eight beats."""

    def __init__(self, cmd, data, enable):
        self.descriptors = stream.SyncFIFO([("addr", len(cmd.addr)), ("we", 1), ("size", 4)], 4)
        self.data = stream.SyncFIFO(data.description, 32, buffered=True)
        desc = self.descriptors.sink
        payload = self.data.sink

        count = Signal(4)
        base = Signal.like(cmd.addr)
        next_addr = Signal.like(cmd.addr)
        write = cmd.valid & cmd.we & data.valid
        append = (count == 0) | (cmd.addr == next_addr)
        end = ~enable | cmd.last | (cmd.addr[:3] == 7)
        take = write & append & payload.ready & (~end | desc.ready)
        flush = (count != 0) & (~cmd.valid | ~cmd.we | ~append)
        read = (count == 0) & cmd.valid & ~cmd.we
        self.comb += [
            cmd.ready.eq(take | (read & desc.ready)),
            data.ready.eq(take),
            payload.valid.eq(take),
            payload.payload.eq(data.payload),
            desc.valid.eq(flush | read | (take & end)),
            desc.addr.eq(Mux(count == 0, cmd.addr, base)),
            desc.we.eq(~read),
            desc.size.eq(Mux(read, 1, count + (take & end))),
        ]
        self.sync += If(desc.valid & desc.ready,
            count.eq(0),
        ).Elif(take,
            If(count == 0, base.eq(cmd.addr)),
            next_addr.eq(cmd.addr + 1),
            count.eq(count + 1),
        )


class DDR3AHardController(LiteXModule):
    """Board reference DDR3A HMC with a Wishbone window and optional native BIST."""

    size = 256 * 1024 * 1024
    clock_frequency = 100_000_000

    def __init__(self, pads, ref_clk, rzq, oct_series, oct_parallel,
                 origin, with_bist=False, bank_interleave=False):
        from litedram.common import LiteDRAMNativePort
        from litedram.frontend.bist import LiteDRAMBISTChecker, LiteDRAMBISTGenerator
        from litedram.frontend.wishbone import LiteDRAMWishbone2Native

        width = 256
        address_width = 24  # Vendor Avalon address is in 32-byte words.
        depth = 64

        self.cd_ddr3a_por = ClockDomain("ddr3a_por", reset_less=True)
        self.cd_ddr3a = ClockDomain("ddr3a")
        por = Signal(4, name="hmc_por_counter", reset_less=True)
        reset_n = por == 15
        afi_clk = Signal()
        port_clk = self.cd_ddr3a.clk
        port_locked = Signal()
        port_reset_n = ~self.cd_ddr3a.rst
        self.comb += self.cd_ddr3a_por.clk.eq(ref_clk)
        self.sync.ddr3a_por += If(~reset_n, por.eq(por + 1))
        # Match the reference design: derive the 100 MHz MPFE clock from its
        # own 400 MHz AFI clock and release the fabric reset after lock.
        self.specials += [
            Instance("altera_pll", name="hmc_avalon_pll",
                p_fractional_vco_multiplier="false", p_reference_clock_frequency="400.0 MHz",
                p_operation_mode="normal", p_number_of_clocks=Instance.PreformattedParam("1"),
                p_output_clock_frequency0="100.0 MHz", p_phase_shift0="0 ps", p_duty_cycle0=Instance.PreformattedParam("50"),
                p_pll_type="General", p_pll_subtype="General",
                i_refclk=afi_clk, i_rst=~reset_n, i_fbclk=0, o_outclk=port_clk, o_locked=port_locked),
            AsyncResetSynchronizer(self.cd_ddr3a, ~port_locked),
        ]

        self.bus = wishbone.Interface(data_width=32, address_width=32, addressing="word")
        local_bus = wishbone.Interface(data_width=32, address_width=32, addressing="word")
        self.bus_cdc = wishbone.ClockDomainCrossing(self.bus, local_bus, cd_to="ddr3a")
        cpu = LiteDRAMNativePort("both", address_width, width, clock_domain="ddr3a")
        self.bridge = ClockDomainsRenamer("ddr3a")(
            LiteDRAMWishbone2Native(local_bus, cpu, base_address=origin))
        port = LiteDRAMNativePort("both", address_width, width, clock_domain="ddr3a")

        burst_enable = Signal(reset=1)
        if with_bist:
            writer = LiteDRAMNativePort("write", address_width, width, clock_domain="ddr3a")
            reader = LiteDRAMNativePort("read", address_width, width, clock_domain="ddr3a")
            self.generator = LiteDRAMBISTGenerator(writer)
            self.checker = LiteDRAMBISTChecker(reader, fifo_depth=depth)
            self.mode = CSRStorage(2, description="Port owner: 0 CPU, 1 BIST writer, 2 BIST reader. Change only when idle.")
            self.write_bursts = CSRStorage(reset=1, description="Group consecutive DDR3A writes into Avalon bursts.")
            self.specials += MultiReg(self.write_bursts.storage, burst_enable, odomain="ddr3a", reset=1)
            mode = Signal(2)
            # Firmware changes the owner only between transactions. The BIST
            # control FIFOs synchronize start/reset separately from this CSR.
            self.specials += MultiReg(self.mode.storage, mode, odomain="ddr3a")
            self.comb += If(mode == 1,
                writer.cmd.connect(port.cmd),
                writer.wdata.connect(port.wdata),
            ).Elif(mode == 2,
                reader.cmd.connect(port.cmd),
                port.rdata.connect(reader.rdata),
            ).Else(
                cpu.cmd.connect(port.cmd),
                cpu.wdata.connect(port.wdata),
                port.rdata.connect(cpu.rdata),
            )
        else:
            self.comb += [
                burst_enable.eq(1),
                cpu.cmd.connect(port.cmd),
                cpu.wdata.connect(port.wdata),
                port.rdata.connect(cpu.rdata),
            ]

        # Wishbone may send the write command before its data. Queue the two
        # streams independently, then present them together to Avalon.
        self.commands = ClockDomainsRenamer("ddr3a")(stream.SyncFIFO(port.cmd.description, 4))
        self.writes = ClockDomainsRenamer("ddr3a")(stream.SyncFIFO(port.wdata.description, 4))
        self.responses = ClockDomainsRenamer("ddr3a")(stream.SyncFIFO(port.rdata.description, depth, buffered=True))
        self.packer = ClockDomainsRenamer("ddr3a")(
            _WriteBurstPacker(self.commands.source, self.writes.source, burst_enable))
        cmd, data = self.packer.descriptors.source, self.packer.data.source
        response = self.responses.sink
        self.comb += [
            port.cmd.connect(self.commands.sink),
            port.wdata.connect(self.writes.sink),
            self.responses.source.connect(port.rdata),
        ]

        init, success, fail = Signal(), Signal(), Signal()
        self.calibration = CSRStatus(3, description="HMC init done, calibration success and failure.")
        status = Signal(3)
        status_first = Signal(3, name="hmc_status_first", reset_less=True, attr={"no_retiming"})
        self.sync.ddr3a += [status_first.eq(Cat(init, success, fail)), status.eq(status_first)]
        self.specials += MultiReg(status, self.calibration.status)

        ready, held, read, write = (Signal() for _ in range(4))
        remaining = Signal(4)
        pending = Signal(max=depth + 1)
        pop = port.rdata.valid & port.rdata.ready
        accepted_read = read & ready
        accepted_write = write & ready
        begin = (read | (write & (remaining == 0))) & ~held
        self.comb += [
            read.eq((status == 3) & cmd.valid & ~cmd.we & (pending < depth)),
            write.eq((status == 3) & cmd.valid & cmd.we & data.valid),
            cmd.ready.eq(accepted_read | (accepted_write &
                ((remaining == 1) | ((remaining == 0) & (cmd.size == 1))))),
            data.ready.eq(accepted_write),
        ]
        # Begin is a one-cycle pulse, including when the first beat stalls.
        # Keep the descriptor at the FIFO head until the last beat is accepted.
        self.sync.ddr3a += [
            held.eq((read | write) & ~ready),
            If(accepted_write,
                remaining.eq(Mux(remaining == 0, cmd.size - 1, remaining - 1))),
            If(accepted_read & ~pop, pending.eq(pending + 1))
            .Elif(pop & ~accepted_read, pending.eq(pending - 1)),
        ]

        if with_bist:
            measuring = Signal()
            self.sync.ddr3a += measuring.eq(mode == 1)
            for name, event in (
                ("write_beats", accepted_write),
                ("write_commands", begin & write),
                ("write_wait_cycles", write & ~ready),
            ):
                count = Signal(32)
                csr = CSRStatus(32, name=name,
                    description="DDR3A BIST write counter. Read after switching out of writer mode.")
                setattr(self, name, csr)
                self.sync.ddr3a += If(mode == 1,
                    If(~measuring, count.eq(0)).Elif(event, count.eq(count + 1)))
                self.specials += MultiReg(count, csr.status)

        self.read_overflow = CSRStatus(description="An Avalon read response arrived with no FIFO space.")
        overflow = Signal()
        self.sync.ddr3a += If(response.valid & ~response.ready, overflow.eq(1))
        self.specials += MultiReg(overflow, self.read_overflow.status)

        port_clocks = dict(i_mp_cmd_clk_0_clk=port_clk, i_mp_cmd_reset_n_0_reset_n=port_reset_n)
        for lane in range(4):
            for fifo in ("rfifo", "wfifo"):
                port_clocks[f"i_mp_{fifo}_clk_{lane}_clk"] = port_clk
                port_clocks[f"i_mp_{fifo}_reset_n_{lane}_reset_n"] = port_reset_n

        # The reference uses row/bank/column addressing and 10 column bits.
        # BL8 consumes three column bits. Swap the next three column bits
        # above the burst with the bank bits to stripe 256-byte chunks.
        address = cmd.addr
        if bank_interleave:
            address = Cat(cmd.addr[:3], cmd.addr[7:10], cmd.addr[6],
                          cmd.addr[3:6], cmd.addr[10:])

        self.specials += Instance("q_sys_hmc_0_fpga_sdram",
            i_pll_ref_clk=ref_clk, i_global_reset_n=reset_n, i_soft_reset_n=1, o_afi_clk=afi_clk,
            i_oct_rzqin=rzq, o_seriesterminationcontrol=oct_series,
            o_parallelterminationcontrol=oct_parallel,
            o_local_init_done=init, o_local_cal_success=success, o_local_cal_fail=fail,
            i_csr_clk=port_clk, i_csr_reset_n=port_reset_n,
            i_csr_addr=0, i_csr_read_req=0, i_csr_write_req=0, i_csr_wdata=0, i_csr_be=0,
            o_avl_ready_0=ready, i_avl_burstbegin_0=begin,
            i_avl_addr_0=address, i_avl_size_0=cmd.size,
            i_avl_read_req_0=read, i_avl_write_req_0=write,
            i_avl_wdata_0=data.data,
            i_avl_be_0=Replicate(read, width // 8) | data.we,
            o_avl_rdata_valid_0=response.valid, o_avl_rdata_0=response.data,
            o_mem_a=pads.a, o_mem_ba=pads.ba, o_mem_ck=pads.clk_p, o_mem_ck_n=pads.clk_n,
            o_mem_cke=pads.cke, o_mem_cs_n=pads.cs_n, o_mem_dm=pads.dm,
            o_mem_ras_n=pads.ras_n, o_mem_cas_n=pads.cas_n, o_mem_we_n=pads.we_n,
            o_mem_reset_n=pads.reset_n, io_mem_dq=pads.dq,
            io_mem_dqs=pads.dqs_p, io_mem_dqs_n=pads.dqs_n, o_mem_odt=pads.odt,
            **port_clocks,
        )


def add_ddr3a_sources(platform, gateware_dir, *, with_ddr3b):
    quartus_root = os.environ.get("QUARTUS_ROOTDIR")
    if quartus_root is None:
        quartus_map = shutil.which("quartus_map")
        if quartus_map is None:
            raise OSError("Put Quartus on PATH or set QUARTUS_ROOTDIR")
        quartus_root = Path(quartus_map).resolve().parent.parent
    generator = Path(quartus_root).resolve() / "sopc_builder/bin/ip-generate"
    output = Path(gateware_dir).resolve() / "ddr3a"
    output.mkdir(parents=True, exist_ok=True)
    hmc = "q_sys_hmc_0_fpga_sdram"
    # Five byte lanes carry 32 data bits plus ECC. The full-rate PHY
    # feeds a 256-bit Avalon port clocked separately at 100 MHz.
    parameters = {
        "HARD_EMIF": "true", "HARD_PHY": "true", "RATE": "Full", "SPEED_GRADE": 7,
        "MEM_CLK_FREQ": 400.0, "REF_CLK_FREQ": 100.0, "MEM_DQ_WIDTH": 40,
        "MEM_ROW_ADDR_WIDTH": 14, "MEM_TCL": 6, "MEM_WTCL": 5,
        "MEM_BL": "OTF", "MEM_RTT_NOM": "RZQ/6", "CTL_ECC_ENABLED": "true",
        "MEM_TFAW_NS": 40.0, "MEM_TRRD_NS": 10.0, "MEM_TRTP_NS": 10.0, "MEM_TWTR": 4,
        "CTL_CSR_ENABLED": "true", "CTL_CSR_CONNECTION": "EXPORT",
        "OCT_SHARING_MODE": "Master", "USER_DEBUG_LEVEL": 0,
        "AVL_DATA_WIDTH_PORT": "256 32 32 32 32 32", "AVL_MAX_SIZE": 128,
    }
    subprocess.run([
        str(generator), "--component-name=altera_mem_if_ddr3_emif",
        "--file-set=QUARTUS_SYNTH", "--standard-reports", f"--part={platform.device}",
        f"--output-name={hmc}", f"--output-directory={output}",
        "--preset=MICRON MT41J128M16HA-125",
        *(f"--component-parameter={name}={value}" for name, value in parameters.items()),
    ], cwd=output, check=True)

    # The hard PHY emits a PLL status probe even with toolkit debugging off.
    # LiteX owns the JTAG TAP, so omit that optional probe from the generated HDL.
    phy_csr = output / "submodules" / f"{hmc}_p0_phy_csr.sv"
    contents = re.sub(rf"(?ms)^{hmc}_p0_iss_probe pll_probe \(.*?^\);", "",
        phy_csr.read_text())
    phy_csr.write_text(contents)

    # Register synthesis inputs directly so the two DDR banks share the
    # vendor primitive wrappers, and keep the HMC out of the JTAG hub.
    sources = set()
    for line in (output / f"{hmc}.qip").read_text().splitlines():
        match = re.search(
            r'-name (SYSTEMVERILOG_FILE|VERILOG_FILE|VHDL_FILE|HEX_FILE|MIF_FILE|SDC_FILE|QIP_FILE|SOURCE_FILE) '
            r'\[file join \$::quartus\(qip_path\) "([^"]+)"\]', line)
        if not match:
            continue
        kind, path = match.groups()
        name = Path(path).name
        if kind == "SOURCE_FILE":
            kind = {".hex": "HEX_FILE", ".mif": "MIF_FILE"}.get(Path(path).suffix)
            if kind is None:
                continue
        if path in sources or (with_ddr3b and name in _IO_WRAPPERS):
            continue
        sources.add(path)
        platform.add_platform_command(f'set_global_assignment -name {kind} "{output / path}"')
    if f"{hmc}.v" not in sources:
        raise ValueError("The generated DDR3A QIP did not list the controller HDL")

    pads = platform.lookup_request("ddram", number=1)
    command = ("a", "ba", "cas_n", "cke", "cs_n", "odt", "ras_n", "reset_n", "we_n")
    data = ("dq", "dqs_n", "dqs_p")
    clocks = ("clk_n", "clk_p")
    for kind, setting, fields in (
        ("CURRENT_STRENGTH_NEW", '"MAXIMUM CURRENT"', command),
        ("INPUT_TERMINATION", '"PARALLEL 50 OHM WITH CALIBRATION"', data),
        ("OUTPUT_TERMINATION", '"SERIES 50 OHM WITH CALIBRATION"', (*data, "dm")),
        ("OUTPUT_TERMINATION", '"SERIES 50 OHM WITHOUT CALIBRATION"', clocks),
        ("PACKAGE_SKEW_COMPENSATION", "OFF", (*command, *data, *clocks, "dm")),
    ):
        for field in fields:
            pad = getattr(pads, field)
            index = "[*]" if len(pad) > 1 else ""
            platform.add_platform_command(
                f"set_instance_assignment -name {kind} {setting} -to {{pad}}{index}", pad=pad)
    platform.toolchain.additional_sdc_commands += [
        "set_clock_groups -asynchronous "
        "-group [get_clocks {ddr3a_refclk *q_sys_hmc_0_fpga_sdram*|pll0|* *hmc_avalon_pll*}]",
        "set_false_path -to [get_registers {*hmc_status_first* *ars_cd_ddr3a_ff*}]",
        "set_false_path -from [get_registers {*hmc_por_counter*}] "
        "-to [get_registers {*q_sys_hmc_0_fpga_sdram* *hmc_avalon_pll*}]",
    ]


# Ethernet -----------------------------------------------------------------------------------------

class CycloneVGTGigabitPHY(LiteXModule):
    """Fixed gigabit RGMII for the kit's 88E1111 with PHY-side clock delays."""

    dw = 8
    tx_clk_freq = rx_clk_freq = 125e6

    def __init__(self, platform, sys_clk_freq):
        from liteeth.common import eth_phy_description
        from liteeth.phy.common import LiteEthPHYHWReset, LiteEthPHYMDIO
        from litex.soc.interconnect.stream import Endpoint

        pads = platform.request("eth")
        clocks = platform.request("eth_clocks")
        oscillator = platform.request("clk125")
        self.cd_eth_tx = ClockDomain()
        self.cd_eth_rx = ClockDomain()
        self.specials += DifferentialInput(oscillator.p, oscillator.n, self.cd_eth_tx.clk)
        self.comb += self.cd_eth_rx.clk.eq(clocks.rx)
        platform.add_period_constraint(oscillator.p, 8, name="rgmii_tx")

        self._reset = CSRStorage(description="Reset the Marvell PHY and RGMII datapath.")
        self.hw_reset = LiteEthPHYHWReset(cycles=int(sys_clk_freq / 1000))
        reset = Signal()
        self.comb += [
            reset.eq(self._reset.storage | self.hw_reset.reset | ResetSignal("sys")),
            pads.rst_n.eq(~reset),
        ]
        self.specials += [
            AsyncResetSynchronizer(self.cd_eth_tx, reset),
            AsyncResetSynchronizer(self.cd_eth_rx, reset),
        ]

        self.mdio = LiteEthPHYMDIO(pads)
        self.sink = sink = Endpoint(eth_phy_description(8))
        self.source = source = Endpoint(eth_phy_description(8))

        tx_clock = ClockSignal("eth_tx")
        self.specials += [
            DDROutput(1, 0, clocks.tx, tx_clock),
            DDROutput(sink.valid, sink.valid, pads.tx_en, tx_clock),
            DDROutput(sink.data[:4], sink.data[4:], pads.tx_data, tx_clock),
        ]
        self.comb += sink.ready.eq(1)

        rx_clock = ClockSignal("eth_rx")
        rise, fall, rise_d = Signal(4), Signal(4), Signal(4)
        ctl_rise, ctl_fall, rx_dv = Signal(), Signal(), Signal()
        self.specials += [
            DDRInput(pads.rx_data, rise, fall, rx_clock),
            DDRInput(pads.rx_dv, ctl_rise, ctl_fall, rx_clock),
        ]
        # Cyclone V ALTDDIO exposes the falling half on the next rising
        # edge. Delay the rising half to pair the two samples of each byte.
        self.sync.eth_rx += [
            rise_d.eq(rise),
            rx_dv.eq(ctl_rise),
            source.valid.eq(rx_dv),
            source.data.eq(Cat(rise_d, fall)),
            source.error.eq(rx_dv ^ ctl_fall),
        ]
        self.comb += [
            source.last.eq(source.valid & ~rx_dv),
            source.be.eq(1),
        ]


def add_rgmii_constraints(platform):
    # RX phase and external skew follow the GT kit Board Update Portal's
    # rgmii_clocks.sdc and rgmii_input.sdc (board traces plus PHY skew).
    # AM10 is a GPIO rather than a dedicated clock input. Keep its route
    # local to meet the DDR input hold checks on this board.
    platform.add_platform_command(
        'set_instance_assignment -name GLOBAL_SIGNAL OFF -to eth_clocks_rx')
    platform.add_platform_command('set_global_assignment -name OPTIMIZE_HOLD_TIMING "ALL PATHS"')
    platform.add_platform_command('set_global_assignment -name ENABLE_ADVANCED_IO_DELAY_CHAIN_OPTIMIZATION ON')
    platform.add_platform_command('set_instance_assignment -name FAST_INPUT_REGISTER ON -to eth_rx_dv')
    platform.add_platform_command('set_instance_assignment -name FAST_INPUT_REGISTER ON -to eth_rx_data[*]')
    sdc = platform.toolchain.additional_sdc_commands
    sdc += [
        # Reference both the data launch and forwarded clock to the same
        # clock-control output. The pin-to-global delay is common to both.
        "set rgmii_tx_source [get_pins -nowarn -compatibility_mode {*eth_tx_clk*|outclk}]",
        "if {[get_collection_size $rgmii_tx_source] == 1} { "
        "create_generated_clock -name rgmii_tx_internal -source [get_ports clk125_p] "
        "-divide_by 1 $rgmii_tx_source "
        "} else { set rgmii_tx_source [get_ports clk125_p] }",
        "create_generated_clock -name rgmii_tx_sample -source $rgmii_tx_source "
        "-edges {1 2 3} -edge_shift {2 2 2} [get_ports eth_clocks_tx]",
        "create_clock -name rgmii_rx -period 8 -waveform {2 6} [get_ports eth_clocks_rx]",
        "create_clock -name rgmii_rx_phy -period 8",
        "set rgmii_rx_pins [get_ports {eth_rx_dv eth_rx_data[*]}]",
        "set rgmii_tx_pins [get_ports {eth_tx_en eth_tx_data[*]}]",
        "set_input_delay -clock rgmii_rx_phy -min -0.45 $rgmii_rx_pins",
        "set_input_delay -clock rgmii_rx_phy -max 0.45 $rgmii_rx_pins",
        "set_input_delay -clock rgmii_rx_phy -clock_fall -add_delay -min -0.45 $rgmii_rx_pins",
        "set_input_delay -clock rgmii_rx_phy -clock_fall -add_delay -max 0.45 $rgmii_rx_pins",
        "set_false_path -setup -rise_from [get_clocks rgmii_rx_phy] -fall_to [get_clocks rgmii_rx]",
        "set_false_path -setup -fall_from [get_clocks rgmii_rx_phy] -rise_to [get_clocks rgmii_rx]",
        "set_false_path -hold -rise_from [get_clocks rgmii_rx_phy] -rise_to [get_clocks rgmii_rx]",
        "set_false_path -hold -fall_from [get_clocks rgmii_rx_phy] -fall_to [get_clocks rgmii_rx]",
        "set_output_delay -clock rgmii_tx_sample -min -0.8 $rgmii_tx_pins",
        "set_output_delay -clock rgmii_tx_sample -max 0.8 $rgmii_tx_pins",
        "set_output_delay -clock rgmii_tx_sample -clock_fall -add_delay -min -0.8 $rgmii_tx_pins",
        "set_output_delay -clock rgmii_tx_sample -clock_fall -add_delay -max 0.8 $rgmii_tx_pins",
        "set_clock_groups -asynchronous -group [get_clocks {rgmii_rx rgmii_rx_phy}]",
        "set_clock_groups -asynchronous -group [get_clocks -nowarn {rgmii_tx rgmii_tx_internal rgmii_tx_sample}]",
    ]


# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.cd_sys = ClockDomain()
        self.pll = pll = CycloneVPLL(speedgrade="-I7")
        pll.register_clkin(platform.request("clk50"), 50e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)


# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=None, with_led_chaser=True, with_ddr3a=False, with_ddr3b=False,
                 with_ethernet=False, with_etherbone=False, eth_ip="192.168.1.50",
                 remote_ip="192.168.1.100", etherbone_ip="192.168.1.51", with_pcie=False, **kwargs):
        platform = altera_cyclonev_gt_devkit.Platform()
        if sys_clk_freq is None:
            sys_clk_freq = 75e6 if with_ddr3b else 50e6

        oct_series, oct_parallel = Signal(16), Signal(16)
        if with_ddr3b:
            from litedram.frontend.bist import LiteDRAMBISTChecker, LiteDRAMBISTGenerator
            from litedram.modules import MT41K64M16
            from litedram.phy.c5ddrphy import CycloneVDDRPHY
            from litedram.phy.c5ddrphy_native import CycloneVDDR3Lane

            if sys_clk_freq != 75e6:
                raise ValueError("The native DDR3B PHY requires a 75 MHz system clock")
            ref_clk = platform.request("ddr_refclk")
            platform.add_period_constraint(ref_clk, 10)
            ddr3b_pads = platform.request("ddram")

            def shared_oct_lane(**ports):
                lane = CycloneVDDR3Lane(**ports)
                # DDR3A and DDR3B share the physical RZQ calibration pad.
                specials = lane._fragment.specials
                oct = next(s for s in specials if isinstance(s, Instance) and
                           s.of == "altera_mem_if_oct_cyclonev")
                specials.remove(oct)
                lane.comb += [
                    oct.get_io("seriesterminationcontrol").eq(oct_series),
                    oct.get_io("parallelterminationcontrol").eq(oct_parallel),
                ]
                return lane

            ddrphy = CycloneVDDRPHY(ddr3b_pads, ref_clk, ResetSignal("por"),
                cl=6, cwl=5, on_the_fly=True, io_backend=shared_oct_lane if with_ddr3a else CycloneVDDR3Lane)
        else:
            self.crg = _CRG(platform, sys_clk_freq)

        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Cyclone V GT", **kwargs)

        if with_ddr3b:
            self.cd_por = ClockDomain()
            por = Signal(4, reset_less=True)
            self.comb += [self.cd_por.clk.eq(ref_clk), self.cd_por.rst.eq(por != 15)]
            self.sync.por += If(por != 15, por.eq(por + 1))
            self.ddrphy = ddrphy
            self.add_sdram("sdram", phy=self.ddrphy, module=MT41K64M16(sys_clk_freq, "1:4"))
            self.sdram_generator = LiteDRAMBISTGenerator(self.sdram.crossbar.get_port())
            # Cover the fixed PHY return latency plus controller and DMA latency.
            self.sdram_checker = LiteDRAMBISTChecker(self.sdram.crossbar.get_port(), fifo_depth=64)
            self.add_constant("MEMTEST_DATA_SIZE", 64*1024)
        else:
            # DDR3B is soldered down. The stock BIOS probes for SPD if I2C is present.
            self.i2c = I2CMaster(platform.request("lcd"))

        if with_ddr3a:
            ref_clk_a = platform.request("ddr3a_refclk")
            platform.add_period_constraint(ref_clk_a, 10)
            rzq = ddr3b_pads.rzq if with_ddr3b else platform.request("ddr_rzq")
            origin = 0x90000000
            self.ddr3a = DDR3AHardController(platform.request("ddram", 1), ref_clk_a,
                rzq, oct_series, oct_parallel, origin, with_bist=True)
            self.bus.add_slave(name="ddr3a", slave=self.ddr3a.bus,
                region=SoCRegion(origin=origin, size=self.ddr3a.size, cached=False))

        if with_ethernet or with_etherbone:
            self.ethphy = CycloneVGTGigabitPHY(platform, sys_clk_freq)
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, data_width=32, ip_address=etherbone_ip,
                    with_ethmac=with_ethernet, ethmac_local_ip=eth_ip, ethmac_remote_ip=remote_ip,
                    with_timing_constraints=False)
            else:
                self.add_ethernet(phy=self.ethphy, data_width=32, local_ip=eth_ip, remote_ip=remote_ip,
                    with_timing_constraints=False)
            add_rgmii_constraints(platform)

        if with_pcie:
            from litepcie.core import LitePCIeEndpoint, LitePCIeMSI
            from litepcie.frontend.dma import LitePCIeDMA
            from litepcie.frontend.wishbone import LitePCIeWishboneMaster
            from litepcie.phy.c5pciephy import C5PCIEPHY

            pads = platform.request("pcie_x4")
            platform.add_period_constraint(pads.clk_p, 10)
            clk50 = platform.lookup_request("clk50", loose=True)
            if clk50 is None:
                clk50 = platform.request("clk50")
            self.pcie_phy = C5PCIEPHY(platform, pads, data_width=128, cd="pcie", dedicated_refclk=True,
                reconfig_clk=clk50, reconfig_rst=~pads.perst_n)
            self.pcie_endpoint = LitePCIeEndpoint(self.pcie_phy, max_pending_requests=8,
                address_width=64, endianness=self.pcie_phy.endianness)
            self.pcie_mmap = LitePCIeWishboneMaster(self.pcie_endpoint, base_address=self.mem_map["csr"])
            bar = self.pcie_mmap.wishbone
            sys_master = wishbone.Interface.like(bar)
            self.bus.add_master(name="pcie_mmap", master=sys_master)
            self.pcie_bar_cdc = wishbone.ClockDomainCrossing(bar, sys_master, cd_from="pcie")
            self.pcie_dma0 = LitePCIeDMA(self.pcie_phy, self.pcie_endpoint, address_width=64,
                with_loopback=True, with_buffering=True, buffering_depth=1024)
            self.pcie_msi = LitePCIeMSI()
            for module in (self.pcie_endpoint, self.pcie_mmap, self.pcie_dma0, self.pcie_msi):
                ClockDomainsRenamer("pcie")(module)
            self.comb += [
                self.pcie_msi.source.connect(self.pcie_phy.msi),
                self.pcie_msi.irqs[0].eq(self.pcie_dma0.reader.irq),
                self.pcie_msi.irqs[1].eq(self.pcie_dma0.writer.irq),
            ]
            self.add_constant("PCIE_DMA0_READER_INTERRUPT", 0)
            self.add_constant("PCIE_DMA0_WRITER_INTERRUPT", 1)
            self.add_constant("DMA_CHANNELS", 1)
            self.add_constant("DMA_ADDR_WIDTH", 64)
            platform.toolchain.additional_sdc_commands += [
                "set_clock_groups -asynchronous -group [get_clocks {*pcie_phy*|coreclkout}]",
            ]

        if with_led_chaser:
            self.leds = LedChaser(platform.request_all("user_led"), sys_clk_freq=sys_clk_freq)


    def add_csr_bridge(self, name="csr", origin=None, with_register=False):
        super().add_csr_bridge(name=name, origin=origin, with_register=with_register)
        if name == "csr" and hasattr(self, "pcie_phy"):
            assert self.bus.slaves[name] is self.csr_bridge.wishbone
            self.bus.slaves[name] = wishbone.Interface.like(self.csr_bridge.wishbone)

    def _finalize_csr(self):
        super()._finalize_csr()
        if not hasattr(self, "pcie_phy"):
            return

        # Replace the default single-domain CSR interconnect before Migen finalizes it.
        self._submodules.remove(("csr_interconnect", self.csr_interconnect))

        # The CSR bank owns the storage and strobes, so clock it with its PCIe
        # peripheral and cross whole Wishbone transactions from the system bus.
        pcie_names = {"pcie_dma0", "pcie_msi"}
        pcie_banks = []
        sys_buses = [mmap.bus for mmap in self.csr_bankarray.get_mmaps()]
        for name, _, page, bank in self.csr_bankarray.banks:
            if name in pcie_names:
                ClockDomainsRenamer("pcie")(bank)
                pcie_banks.append((page, bank.bus))
            else:
                sys_buses.append(bank.bus)

        sys_csr = self.csr_bridge.wishbone
        pcie_csr = wishbone.Interface.like(sys_csr)
        pcie_bridge = wishbone.Wishbone2CSR(wishbone.Interface.like(sys_csr), csr_bus.Interface(
            data_width=self.csr.data_width, address_width=self.csr.address_width,
            alignment=self.csr.alignment))
        self.pcie_csr_bridge = ClockDomainsRenamer("pcie")(pcie_bridge)
        self.pcie_csr_cdc = wishbone.ClockDomainCrossing(pcie_csr, pcie_bridge.wishbone, cd_to="pcie")

        page_shift = (self.csr.paging // (sys_csr.data_width // 8)).bit_length() - 1
        base_page = (self.bus.regions["csr"].origin // self.csr.paging)

        def select_pcie(address):
            return Cat(*[(address >> page_shift) == base_page + page for page, _ in pcie_banks]) != 0

        self.csr_decoder = wishbone.Decoder(self.bus.slaves["csr"], [
            (select_pcie, pcie_csr),
            (lambda address: ~select_pcie(address), sys_csr),
        ])
        self.csr_interconnect = csr_bus.InterconnectShared(list(self.csr.masters.values()), sys_buses)
        self.pcie_csr_interconnect = ClockDomainsRenamer("pcie")(
            csr_bus.InterconnectShared([pcie_bridge.csr], [bus for _, bus in pcie_banks]))


# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser

    parser = LiteXArgumentParser(platform=altera_cyclonev_gt_devkit.Platform, description="LiteX SoC on Cyclone V GT.")
    parser.add_target_argument("--sys-clk-freq",      default=None, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-ddr3a",        action="store_true",                     help="Enable the DDR3A hard memory controller.")
    parser.add_target_argument("--without-ddr3a",     action="store_false", dest="with_ddr3a", help="Disable DDR3A.")
    parser.add_target_argument("--with-ddr3b", "--with-native-ddr3b", action="store_true", help="Enable the native 64-bit DDR3B PHY.")
    parser.add_target_argument("--without-ddr3b",     action="store_false", dest="with_ddr3b", help="Disable DDR3B.")
    parser.add_target_argument("--ddr3b-ip-dir",      type=Path,                help="Use pre-generated native DDR3B Quartus wrappers.")
    parser.add_target_argument("--with-ethernet",    action="store_true",      help="Enable the 32-bit LiteEth MAC.")
    parser.add_target_argument("--with-etherbone",   action="store_true",      help="Enable the 32-bit Etherbone core.")
    parser.add_target_argument("--eth-ip",           default="192.168.1.50",   help="Local IP address for the Ethernet MAC.")
    parser.add_target_argument("--remote-ip",        default="192.168.1.100",  help="Remote IP address for the Ethernet MAC.")
    parser.add_target_argument("--etherbone-ip",     default="192.168.1.51",   help="IP address for Etherbone.")
    parser.add_target_argument("--with-pcie",        action="store_true",      help="Enable the onboard Gen2 x4 PCIe endpoint.")
    args = parser.parse_args()

    if args.ddr3b_ip_dir is not None and not args.with_ddr3b:
        parser.error("--ddr3b-ip-dir requires --with-ddr3b")

    soc = BaseSoC(
        sys_clk_freq   = args.sys_clk_freq,
        with_ddr3a     = args.with_ddr3a,
        with_ddr3b     = args.with_ddr3b,
        with_ethernet  = args.with_ethernet,
        with_etherbone = args.with_etherbone,
        eth_ip         = args.eth_ip,
        remote_ip      = args.remote_ip,
        etherbone_ip   = args.etherbone_ip,
        with_pcie      = args.with_pcie,
        **parser.soc_argdict)
    builder = Builder(soc, **parser.builder_argdict)

    if args.build:
        if args.with_ddr3b:
            ip_dir = args.ddr3b_ip_dir
            if ip_dir is None:
                ip_dir = Path(builder.gateware_dir)
                generate_native_lane_sources(ip_dir)
            add_native_lane_sources(soc.platform, ip_dir, builder.gateware_dir,
                                    with_ddr3a=args.with_ddr3a)
        if args.with_ddr3a:
            add_ddr3a_sources(soc.platform, builder.gateware_dir,
                             with_ddr3b=args.with_ddr3b)
        if args.with_pcie:
            soc.pcie_phy.generate_hard_ip(Path(builder.gateware_dir) / "pcie")
        if args.with_ethernet or args.with_etherbone:
            soc.platform.toolchain.additional_qsf_commands += [
                'set_global_assignment -name FITTER_EFFORT "STANDARD FIT"',
                "set_global_assignment -name SEED 3",
            ]
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))


if __name__ == "__main__":
    main()
