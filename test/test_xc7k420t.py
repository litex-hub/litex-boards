import sys
from unittest.mock import Mock

from litex_boards.targets import aliexpress_xc7k420t


def test_spi_flash_constructor():
    soc = aliexpress_xc7k420t.BaseSoC(with_spi_flash=True, uart_name="stub")
    assert soc.bus.regions["spiflash"].size == 32 * 1024 * 1024
    assert soc.constants["SPIFLASH_MODULE_NAME"] == "w25q256"
    assert soc.spiflash.phy.flash.addr_bits == 32


def test_spi_flash_option_and_load(monkeypatch, tmp_path):
    soc = Mock()
    builder = Mock()
    bitstream = str(tmp_path / "custom.bit")
    builder.return_value.get_bitstream_filename.return_value = bitstream
    monkeypatch.setattr(aliexpress_xc7k420t, "BaseSoC", soc)
    monkeypatch.setattr(aliexpress_xc7k420t, "Builder", builder)
    monkeypatch.setattr(sys, "argv", ["aliexpress_xc7k420t", "--with-spi-flash", "--load"])
    aliexpress_xc7k420t.main()
    assert soc.call_args.kwargs["with_spi_flash"] is True
    builder.return_value.get_bitstream_filename.assert_called_once_with(mode="sram")
    soc.return_value.platform.create_programmer.return_value.load_bitstream.assert_called_once_with(bitstream)
