import pytest

from litex.soc.cores.uart import UART, UARTCrossover
from litex_boards.targets import (
    limesdr_mini_v2, microsoft_catapult_v3, microsoft_storey_peak, terasic_deca, xilinx_zc706,
)


TARGETS = [limesdr_mini_v2, microsoft_catapult_v3, microsoft_storey_peak, terasic_deca, xilinx_zc706]
JTAG_UART_TARGETS = [microsoft_catapult_v3, microsoft_storey_peak, terasic_deca]


@pytest.mark.parametrize("target", TARGETS)
def test_default_constructor(target, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    soc = target.BaseSoC()
    with_jtagbone = target not in JTAG_UART_TARGETS
    assert isinstance(soc.uart, UARTCrossover if with_jtagbone else UART)
    assert hasattr(soc, "jtagbone") == with_jtagbone


@pytest.mark.parametrize("target", TARGETS)
def test_explicit_uart_is_preserved(target, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    soc = target.BaseSoC(uart_name="crossover")
    assert isinstance(soc.uart, UARTCrossover)


@pytest.mark.parametrize("target", JTAG_UART_TARGETS)
def test_jtagbone_selects_crossover_uart(target, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    soc = target.BaseSoC(with_jtagbone=True)
    assert isinstance(soc.uart, UARTCrossover)
    assert hasattr(soc, "jtagbone")


def test_limesdr_jtag_uart_disables_default_jtagbone(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    soc = limesdr_mini_v2.BaseSoC(uart_name="jtag_uart")
    assert isinstance(soc.uart, UART)
    assert not hasattr(soc, "jtagbone")


def test_zc706_etherbone_disables_default_jtagbone(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    soc = xilinx_zc706.BaseSoC(with_etherbone=True)
    assert hasattr(soc, "etherbone")
    assert not hasattr(soc, "jtagbone")
