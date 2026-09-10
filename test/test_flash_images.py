import sys
from pathlib import Path
from unittest.mock import Mock, call

import pytest

from litex.soc.integration.builder import Builder
from litex_boards.targets import (
    alchitry_cu, icebreaker, kosagi_fomu, lattice_ice40up5k_evn, muselab_icesugar,
    signaloid_c0_microsd,
)


@pytest.fixture(params=[lattice_ice40up5k_evn, muselab_icesugar, icebreaker, alchitry_cu, kosagi_fomu])
def flash_target(request, tmp_path, monkeypatch):
    target = request.param
    soc = target.BaseSoC(bios_flash_offset=0x40000, cpu_variant="minimal", uart_name="stub")
    soc.build_name = "custom"
    builder = Builder(soc,
        output_dir=tmp_path / "output",
        gateware_dir=tmp_path / "gateware",
        software_dir=tmp_path / "software",
    )
    bitstream = Path(builder.get_bitstream_filename(mode="flash"))
    bios = Path(builder.get_bios_filename())
    bitstream.parent.mkdir(parents=True)
    bios.parent.mkdir(parents=True)
    bitstream.write_bytes(b"bitstream")
    bios.write_bytes(b"bios")
    programmer = Mock()
    if target is lattice_ice40up5k_evn:
        monkeypatch.setattr(target, "IceStormProgrammer", lambda: programmer)
    elif target in [icebreaker, alchitry_cu]:
        monkeypatch.setattr("litex.build.lattice.programmer.IceStormProgrammer", lambda: programmer)
    elif target is kosagi_fomu:
        monkeypatch.setattr("litex.build.dfu.DFUProg", lambda **kwargs: programmer)
    else:
        monkeypatch.setattr("litex.build.lattice.programmer.IceSugarProgrammer", lambda: programmer)
    return target, builder, bitstream, bios, programmer


@pytest.mark.parametrize("offset", [0x20000, 0x40000])
def test_flash_paths_and_bios_offset(flash_target, offset):
    target, builder, bitstream, bios, programmer = flash_target
    target.flash(builder, offset)
    if target in [lattice_ice40up5k_evn, kosagi_fomu]:
        image = Path(builder.output_dir) / "image.bin"
        bios_size = 0x8000 if target is kosagi_fomu else 0x10000
        assert image.read_bytes() == (
            b"bitstream" + b"\xff" * (offset - 9) + b"bios" + b"\xff" * (bios_size - 4)
        )
        if target is kosagi_fomu:
            programmer.load_bitstream.assert_called_once_with(str(image))
        else:
            programmer.flash.assert_called_once_with(0, str(image))
    else:
        assert programmer.flash.call_args_list == [
            call(offset, str(bios)), call(0, str(bitstream)),
        ]


@pytest.mark.parametrize("problem", ["overlap", "bios_size", "flash_size", "negative_offset", "missing_bios"])
def test_invalid_flash_image_does_not_program(flash_target, problem):
    target, builder, bitstream, bios, programmer = flash_target
    offset = 0x40000
    error = ValueError
    if problem == "overlap":
        bitstream.write_bytes(b"\x00" * (offset + 1))
    elif problem == "bios_size":
        bios.write_bytes(b"\x00" * (builder.soc.bus.regions["rom"].size + 1))
    elif problem == "flash_size":
        offset = builder.soc.bus.regions["spiflash"].size
    elif problem == "negative_offset":
        offset = -1
    elif problem == "missing_bios":
        bios.unlink()
        error = FileNotFoundError
    with pytest.raises(error):
        target.flash(builder, offset)
    programmer.flash.assert_not_called()
    programmer.load_bitstream.assert_not_called()
    assert not (Path(builder.output_dir) / "image.bin").exists()


def test_flash_without_build(flash_target, monkeypatch):
    target, builder, bitstream, bios, programmer = flash_target
    del builder.soc.build_name
    bitstream.rename(builder.get_bitstream_filename(mode="flash"))
    monkeypatch.setattr(sys, "argv", [target.__name__, "--flash",
        "--bios-flash-offset=0x40000",
        "--uart-name=stub",
        "--output-dir", builder.output_dir,
        "--gateware-dir", builder.gateware_dir,
        "--software-dir", builder.software_dir,
    ])
    target.main()
    if target is kosagi_fomu:
        programmer.load_bitstream.assert_called_once_with(str(Path(builder.output_dir) / "image.bin"))
    else:
        assert programmer.flash.called


def test_fomu_image_keeps_space_for_dfu_bootloader(tmp_path, monkeypatch):
    soc = kosagi_fomu.BaseSoC(bios_flash_offset=0x60000, uart_name="stub")
    builder = Builder(soc, output_dir=tmp_path)
    bitstream = Path(builder.get_bitstream_filename(mode="flash"))
    bios = Path(builder.get_bios_filename())
    bitstream.parent.mkdir(parents=True)
    bios.parent.mkdir(parents=True)
    bitstream.write_bytes(b"bitstream")
    bios.write_bytes(b"bios")
    programmer = Mock()
    monkeypatch.setattr("litex.build.dfu.DFUProg", lambda **kwargs: programmer)
    offset = soc.bus.regions["spiflash"].size - soc.bus.regions["rom"].size
    with pytest.raises(ValueError, match="DFU image exceeds"):
        kosagi_fomu.flash(builder, offset)
    programmer.load_bitstream.assert_not_called()


def test_signaloid_flash_instructions_without_build(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["signaloid_c0_microsd", "--flash",
        "--output-dir", str(tmp_path / "output"),
        "--gateware-dir", str(tmp_path / "gateware"),
        "--software-dir", str(tmp_path / "software"),
    ])
    signaloid_c0_microsd.main()
    output = capsys.readouterr().out
    assert str(tmp_path / "gateware" / "signaloid_c0_microsd.bin") in output
    assert str(tmp_path / "software" / "bios" / "bios.bin") in output
    assert "Programming is not supported" in output
