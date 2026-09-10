import sys
from unittest.mock import Mock

import pytest

from migen import Module, run_simulation

from litex_boards.targets import (
    antmicro_datacenter_ddr4_test_board, berkeleylab_marble, lattice_crosslink_nx_evn,
)


@pytest.mark.parametrize("args, uart_name", [
    ([], "serial"),
    (["--serial", "serial_pmod0"], "serial_pmod0"),
    (["--uart-name", "serial_pmod1"], "serial_pmod1"),
    (["--serial", "serial_pmod0", "--uart-name", "stub"], "stub"),
    (["--uart-name", "stub", "--serial", "serial_pmod2"], "serial_pmod2"),
])
def test_crosslink_serial_alias(monkeypatch, args, uart_name):
    soc = Mock()
    monkeypatch.setattr(lattice_crosslink_nx_evn, "BaseSoC", soc)
    monkeypatch.setattr(lattice_crosslink_nx_evn, "Builder", Mock())
    monkeypatch.setattr(sys, "argv", ["lattice_crosslink_nx_evn", *args])
    lattice_crosslink_nx_evn.main()
    assert soc.call_args.kwargs["uart_name"] == uart_name


@pytest.mark.parametrize("target, args, keyword, value", [
    (berkeleylab_marble, [], "with_rts_reset", False),
    (berkeleylab_marble, ["--with-rts-reset"], "with_rts_reset", True),
    (antmicro_datacenter_ddr4_test_board, ["--eth-reset-time", "0.25"], "eth_reset_time", "0.25"),
])
def test_target_option_forwarding(monkeypatch, target, args, keyword, value):
    soc = Mock()
    monkeypatch.setattr(target, "BaseSoC", soc)
    monkeypatch.setattr(target, "Builder", Mock())
    monkeypatch.setattr(sys, "argv", [target.__name__, *args])
    target.main()
    assert soc.call_args.kwargs[keyword] == value


@pytest.mark.parametrize("uart_name", ["serial", "crossover"])
def test_marble_rts_and_software_reset(uart_name):
    soc = berkeleylab_marble.BaseSoC(
        with_rts_reset=True, uart_name=uart_name, integrated_main_ram_size=0x10000)
    serial = soc.platform.lookup_request("serial")
    soc._finalize_reset()
    dut = Module()
    dut.comb += soc._fragment.comb

    def stimulus():
        for rts, software in [(0, 0), (1, 0), (0, 1), (1, 1), (0, 0)]:
            yield serial.rts.eq(rts)
            yield soc.ctrl.soc_rst.eq(software)
            yield
            assert (yield soc.crg.rst) == (rts or software)

    run_simulation(dut, stimulus())
