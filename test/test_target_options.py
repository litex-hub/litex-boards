import sys
from unittest.mock import Mock

import pytest

from litex_boards.targets import (
    digilent_arty, lattice_crosslink_nx_evn, microsoft_catapult_v3,
    microsoft_storey_peak, mnt_rkx7, qmtech_wukong,
)


def run_target(monkeypatch, target, args):
    soc = Mock()
    builder = Mock()
    monkeypatch.setattr(target, "BaseSoC", soc)
    monkeypatch.setattr(target, "Builder", builder)
    monkeypatch.setattr(sys, "argv", [target.__name__, *args])
    target.main()
    return soc, builder


@pytest.mark.parametrize("args, spi, native, ethernet, etherbone", [
    ([], False, True, True, False),
    (["--with-spi-sdcard"], True, False, True, False),
    (["--with-sdcard"], False, True, True, False),
    (["--no-sdcard"], False, False, True, False),
    (["--with-etherbone"], False, True, False, True),
    (["--with-ethernet"], False, True, True, False),
    (["--no-ethernet"], False, True, False, False),
])
def test_rkx7_modes(monkeypatch, args, spi, native, ethernet, etherbone):
    soc, _ = run_target(monkeypatch, mnt_rkx7, args)
    assert soc.return_value.add_spi_sdcard.called == spi
    assert soc.return_value.add_sdcard.called == native
    assert soc.call_args.kwargs["with_ethernet"] == ethernet
    assert soc.call_args.kwargs["with_etherbone"] == etherbone


@pytest.mark.parametrize("args", [
    ["--with-spi-sdcard", "--with-sdcard"],
    ["--with-sdcard", "--no-sdcard"],
    ["--with-ethernet", "--with-etherbone"],
    ["--with-etherbone", "--no-ethernet"],
])
def test_rkx7_rejects_conflicting_modes(monkeypatch, args):
    with pytest.raises(SystemExit) as error:
        run_target(monkeypatch, mnt_rkx7, args)
    assert error.value.code == 2
    mnt_rkx7.BaseSoC.assert_not_called()


@pytest.mark.parametrize("target, flags, fields", [
    (mnt_rkx7, ["--no-spi-flash", "--no-usb-host"], ["with_spi_flash", "with_usb_host"]),
    (microsoft_catapult_v3, ["--no-led-chaser"], ["with_led_chaser"]),
    (microsoft_storey_peak, ["--no-led-chaser", "--no-i2c"], ["with_led_chaser", "with_i2c"]),
])
@pytest.mark.parametrize("enabled", [True, False])
def test_default_features_can_be_disabled(monkeypatch, target, flags, fields, enabled):
    soc, _ = run_target(monkeypatch, target, [] if enabled else flags)
    assert all(soc.call_args.kwargs[field] == enabled for field in fields)


def test_rkx7_preserves_csr_path(monkeypatch, tmp_path):
    path = str(tmp_path / "custom.csv")
    _, builder = run_target(monkeypatch, mnt_rkx7, ["--csr-csv", path])
    assert builder.call_args.kwargs["csr_csv"] == path


@pytest.mark.parametrize("target, flag", [
    (digilent_arty, "--eth-dynamic-ip"),
    (digilent_arty, "--eth-dhcp"),
    (mnt_rkx7, "--eth-dynamic-ip"),
])
def test_etherbone_rejects_dynamic_ip(monkeypatch, capsys, target, flag):
    with pytest.raises(SystemExit) as error:
        run_target(monkeypatch, target, ["--with-etherbone", flag])
    assert error.value.code == 2
    assert "requires a static IP" in capsys.readouterr().err
    target.BaseSoC.assert_not_called()


@pytest.mark.parametrize("target, kwargs", [
    (digilent_arty, {"eth_dynamic_ip": True}),
    (digilent_arty, {"eth_dhcp": True}),
    (mnt_rkx7, {"eth_dynamic_ip": True}),
])
def test_etherbone_constructor_rejects_dynamic_ip(target, kwargs):
    with pytest.raises(ValueError, match="static IP"):
        target.BaseSoC(with_etherbone=True, **kwargs)


@pytest.mark.parametrize("address", ["0x10000", "65536"])
def test_crosslink_flash_address_is_an_integer(monkeypatch, address):
    soc, builder = run_target(monkeypatch, lattice_crosslink_nx_evn,
        ["--load", "--programmer", "ecpprog", "--prog-target", "flash", "--address", address])
    soc.return_value.platform.create_programmer.return_value.flash.assert_called_once_with(
        65536, builder.return_value.get_bitstream_filename.return_value)


@pytest.mark.parametrize("revision", ["1", "2", "3"])
def test_wukong_revision(monkeypatch, revision):
    soc, _ = run_target(monkeypatch, qmtech_wukong, ["--revision", revision])
    assert soc.call_args.kwargs["revision"] == int(revision)


@pytest.mark.parametrize("target, args", [
    (qmtech_wukong, ["--revision", "4"]),
    (qmtech_wukong, ["--revision", "invalid"]),
    (lattice_crosslink_nx_evn, ["--address", "invalid"]),
])
def test_invalid_numeric_options(monkeypatch, target, args):
    with pytest.raises(SystemExit) as error:
        run_target(monkeypatch, target, args)
    assert error.value.code == 2
    target.BaseSoC.assert_not_called()
