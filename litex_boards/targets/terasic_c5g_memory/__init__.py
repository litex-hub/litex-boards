# SPDX-License-Identifier: BSD-2-Clause

import math
import os
from pathlib import Path
import shutil
import subprocess

from migen import Cat, ClockDomain, ClockDomainsRenamer, FSM, If, Instance, Mux, NextState, NextValue, Signal
from migen.fhdl.specials import Tristate
from migen.genlib.cdc import MultiReg
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import LiteXModule
from litex.soc.interconnect import wishbone
from litex.soc.interconnect.csr import CSRStatus


class C5GSRAM(LiteXModule):
    size = 512 * 1024

    def __init__(self, pads, sys_clk_freq):
        self.bus = bus = wishbone.Interface(data_width=32, address_width=32)
        high = Signal()
        data_o, data_i = Signal(16), Signal(16)
        drive = Signal()
        # At least 20 ns for each setup, access, and write hold interval.
        cycles = math.ceil(20e-9 * sys_clk_freq)
        elapsed = Signal(max=max(2, cycles))
        done = elapsed == cycles - 1
        self.specials += Tristate(pads.dq, data_o, drive, data_i)
        self.comb += [
            pads.a.eq(Cat(high, bus.adr[:17])),
            data_o.eq(Mux(high, bus.dat_w[16:], bus.dat_w[:16])),
        ]
        select = Signal(2)
        self.comb += select.eq(Mux(high, bus.sel[2:], bus.sel[:2]))
        self.fsm = fsm = FSM(reset_state="IDLE")

        fsm.act("IDLE",
            NextValue(high, 0),
            If(bus.cyc & bus.stb, NextState("SETUP"))
        )
        self.comb += [
            pads.ce_n.eq(~(fsm.ongoing("SETUP") | fsm.ongoing("ACCESS") | fsm.ongoing("HOLD"))),
            pads.oe_n.eq(~(fsm.ongoing("ACCESS") & ~bus.we)),
            pads.we_n.eq(~(fsm.ongoing("ACCESS") & bus.we & (select != 0))),
            pads.lb_n.eq(pads.ce_n | (bus.we & ~select[0])),
            pads.ub_n.eq(pads.ce_n | (bus.we & ~select[1])),
            drive.eq(~pads.ce_n & bus.we),
        ]
        fsm.act("SETUP",
            If(done, NextValue(elapsed, 0), NextState("ACCESS"))
            .Else(NextValue(elapsed, elapsed + 1))
        )
        read_data = Signal(32)
        self.comb += bus.dat_r.eq(read_data)
        fsm.act("ACCESS",
            If(done,
                NextValue(elapsed, 0),
                If(~bus.we,
                    If(high, NextValue(read_data[16:], data_i))
                    .Else(NextValue(read_data[:16], data_i))
                ),
                NextState("HOLD")
            ).Else(NextValue(elapsed, elapsed + 1))
        )
        fsm.act("HOLD",
            If(done,
                NextValue(elapsed, 0),
                If(high, NextState("ACK"))
                .Else(NextValue(high, 1), NextState("SETUP"))
            ).Else(NextValue(elapsed, elapsed + 1))
        )
        fsm.act("ACK", bus.ack.eq(bus.cyc & bus.stb), NextState("IDLE"))


class C5GLPDDR2(LiteXModule):
    size = 512 * 1024 * 1024

    def __init__(self, platform, ref_clk, reset_n):
        pads = platform.request("lpddr2")
        rzq = platform.request("lpddr2_rzq")
        self.cd_lpddr2_por = ClockDomain("lpddr2_por", reset_less=True)
        self.cd_lpddr2 = ClockDomain("lpddr2")
        por = Signal(4, reset_less=True)
        reset_released = Signal(reset_less=True, name="lpddr2_por_done")
        afi_reset_n = Signal()
        self.comb += self.cd_lpddr2_por.clk.eq(ref_clk)
        self.sync.lpddr2_por += If(~reset_released,
            por.eq(por + 1),
            reset_released.eq(por == 15),
        )
        self.specials += AsyncResetSynchronizer(self.cd_lpddr2, ~afi_reset_n)

        self.bus = wishbone.Interface(data_width=32, address_width=32)
        local_bus = wishbone.Interface(data_width=32, address_width=32)
        self.cdc = wishbone.ClockDomainCrossing(self.bus, local_bus, cd_to="lpddr2")

        init, success, fail = Signal(), Signal(), Signal()
        status = Signal(3)
        status_meta = Signal(3, name="lpddr2_status_meta", attr={"no_retiming"})
        self.sync.lpddr2 += [status_meta.eq(Cat(init, success, fail)), status.eq(status_meta)]
        self.calibration = CSRStatus(3, description="HMC init done, calibration success, calibration failure.")
        self.specials += MultiReg(status, self.calibration.status)

        ready, valid, read, write, begin = (Signal() for _ in range(5))
        read_data = Signal(32)
        self.fsm = fsm = ClockDomainsRenamer("lpddr2")(FSM(reset_state="IDLE"))
        fsm.act("IDLE",
            If(local_bus.cyc & local_bus.stb,
                If(status[2], local_bus.err.eq(1))
                .Elif(status == 3, NextState("ISSUE"))
            )
        )
        for state in ("ISSUE", "STALL"):
            fsm.act(state,
                begin.eq(state == "ISSUE"),
                read.eq(~local_bus.we),
                write.eq(local_bus.we),
                If(ready,
                    If(local_bus.we,
                        local_bus.ack.eq(1),
                        NextState("IDLE")
                    ).Else(NextState("READ"))
                ).Else(NextState("STALL"))
            )
        fsm.act("READ",
            If(valid, local_bus.dat_r.eq(read_data), local_bus.ack.eq(1), NextState("IDLE"))
        )

        port_clk = self.cd_lpddr2.clk
        port_reset_n = ~self.cd_lpddr2.rst
        cke, cs_n = Signal(), Signal()
        self.comb += [pads.cke.eq(cke), pads.cs_n.eq(Cat(cs_n, 1))]
        self.specials += Instance("c5g_lpddr2",
            i_pll_ref_clk=ref_clk, i_global_reset_n=reset_released & reset_n,
            i_soft_reset_n=1, o_afi_half_clk=port_clk, o_afi_reset_n=afi_reset_n,
            i_mp_cmd_clk_0_clk=port_clk, i_mp_cmd_reset_n_0_reset_n=port_reset_n,
            i_mp_rfifo_clk_0_clk=port_clk, i_mp_rfifo_reset_n_0_reset_n=port_reset_n,
            i_mp_wfifo_clk_0_clk=port_clk, i_mp_wfifo_reset_n_0_reset_n=port_reset_n,
            i_oct_rzqin=rzq, o_local_init_done=init, o_local_cal_success=success, o_local_cal_fail=fail,
            o_avl_ready_0=ready, i_avl_burstbegin_0=begin, i_avl_addr_0=local_bus.adr[:27],
            i_avl_size_0=1, i_avl_read_req_0=read, i_avl_write_req_0=write,
            i_avl_wdata_0=local_bus.dat_w, i_avl_be_0=Mux(local_bus.we, local_bus.sel, 15),
            o_avl_rdata_valid_0=valid, o_avl_rdata_0=read_data,
            o_mem_ca=pads.ca, o_mem_ck=pads.ck_p, o_mem_ck_n=pads.ck_n,
            o_mem_cke=cke, o_mem_cs_n=cs_n, o_mem_dm=pads.dm,
            io_mem_dq=pads.dq, io_mem_dqs=pads.dqs_p, io_mem_dqs_n=pads.dqs_n,
        )

        # The Wishbone bridge uses asynchronous FIFOs and calibration status
        # uses synchronizers. The HMC also synchronizes its own global reset.
        platform.toolchain.additional_sdc_commands += [
            "set_false_path -to [get_registers {*lpddr2_status_meta*}]",
            "set_clock_groups -asynchronous -group [get_clocks {clk501 *ALTPLL*}]",
            "set_false_path -from [get_registers {*lpddr2_por_done*}] "
            "-to [get_registers {*c5g_lpddr2*|*}]",
        ]

        for field in ("ca", "ck_p", "ck_n", "dm", "dq", "dqs_p", "dqs_n", "cke", "cs_n"):
            pad = getattr(pads, field)
            suffix = "[0]" if field in ("cke", "cs_n") else "[*]" if len(pad) > 1 else ""
            platform.add_platform_command(
                f'set_instance_assignment -name OUTPUT_TERMINATION "SERIES 34 OHM WITH CALIBRATION" -to {{pad}}{suffix}',
                pad=pad)
            platform.add_platform_command(
                f"set_instance_assignment -name PACKAGE_SKEW_COMPENSATION OFF -to {{pad}}{suffix}", pad=pad)


def generate_lpddr2_ip(platform, output_dir):
    """Generate the C5G UniPHY/HMC QIP using the installed Quartus toolchain."""
    quartus_root = os.environ.get("QUARTUS_ROOTDIR")
    if quartus_root is None:
        quartus_map = shutil.which("quartus_map")
        if quartus_map is None:
            raise OSError("Put Quartus on PATH or set QUARTUS_ROOTDIR to generate C5G LPDDR2 IP")
        quartus_root = Path(quartus_map).resolve().parent.parent
    generator = Path(quartus_root).resolve() / "sopc_builder/bin/ip-generate"
    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    # Terasic C5G System CD reference design: 32-bit, one rank, 50 MHz reference.
    parameters = {
        "HARD_EMIF": "true", "HARD_PHY": "true", "RATE": "Full", "SPEED_GRADE": 7,
        "MEM_CLK_FREQ": 300.0, "REF_CLK_FREQ": 50.0, "MEM_DQ_WIDTH": 32,
        "MEM_ROW_ADDR_WIDTH": 14, "MEM_COL_ADDR_WIDTH": 10, "MEM_BANKADDR_WIDTH": 3,
        "MEM_TCL": 7, "MEM_TRFC_NS": 130.0, "MEM_TREFI_US": 3.9,
        "AVL_DATA_WIDTH_PORT": "32 32 32 32 32 32", "EXPORT_AFI_HALF_CLK": "true",
        "USER_DEBUG_LEVEL": 0,
    }
    subprocess.run([
        str(generator), "--component-name=altera_mem_if_lpddr2_emif",
        "--file-set=QUARTUS_SYNTH", "--standard-reports", f"--part={platform.device}",
        "--output-name=c5g_lpddr2", f"--output-directory={output}",
        *(f"--component-parameter={name}={value}" for name, value in parameters.items()),
    ], cwd=output, check=True)
    return output / "c5g_lpddr2.qip"
