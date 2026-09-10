from pathlib import Path
from unittest.mock import Mock, call

import pytest

from litex.soc.integration.builder import Builder
from litex_boards.targets import lattice_ice40up5k_evn, muselab_icesugar


@pytest.fixture(params=[lattice_ice40up5k_evn, muselab_icesugar])
def flash_target(request, tmp_path, monkeypatch):
    target = request.param
    soc = target.BaseSoC(bios_flash_offset=0x40000, cpu_variant="minimal")
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
    else:
        monkeypatch.setattr("litex.build.lattice.programmer.IceSugarProgrammer", lambda: programmer)
    return target, builder, bitstream, bios, programmer


@pytest.mark.parametrize("offset", [0x20000, 0x40000])
def test_flash_paths_and_bios_offset(flash_target, offset):
    target, builder, bitstream, bios, programmer = flash_target
    target.flash(builder, offset)
    if target is lattice_ice40up5k_evn:
        image = Path(builder.output_dir) / "image.bin"
        assert image.read_bytes() == (
            b"bitstream" + b"\xff" * (offset - 9) + b"bios" + b"\xff" * (0x10000 - 4)
        )
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
    assert not (Path(builder.output_dir) / "image.bin").exists()
