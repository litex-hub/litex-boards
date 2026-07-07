import pytest

from litex.soc.cores.ram.xilinx_usp_hbm2 import (
    USPHBM2_HIGH_BASE,
    parse_usphbm2_channels,
    usphbm2_channel_origin,
)
from litex_boards.targets.alibaba_vu13p import QSFP_PORTS as ALIBABA_QSFP_PORTS
from litex_boards.targets.alibaba_vu13p import parse_qsfp_port as parse_alibaba_qsfp_port
from litex_boards.targets.sqrl_xcu1525 import QSFP_PORTS, parse_qsfp_port


def test_fk33_hbm_channel_parser_accepts_lists_ranges_and_all():
    assert parse_usphbm2_channels("0,1,2,3") == (0, 1, 2, 3)
    assert parse_usphbm2_channels("0-3,8") == (0, 1, 2, 3, 8)
    assert parse_usphbm2_channels("all") == tuple(range(32))


@pytest.mark.parametrize("channels", ["", "3-1", "0,0", "32"])
def test_fk33_hbm_channel_parser_rejects_invalid_channels(channels):
    with pytest.raises(ValueError):
        parse_usphbm2_channels(channels)


def test_fk33_hbm_origin_map_keeps_low_window_and_moves_upper_channels_high():
    assert usphbm2_channel_origin(0) == 0x4000_0000
    assert usphbm2_channel_origin(3) == 0x7000_0000
    assert usphbm2_channel_origin(4) == USPHBM2_HIGH_BASE


def test_xcu1525_qsfp_port_parser_covers_all_lanes():
    assert len(QSFP_PORTS) == 8
    assert parse_qsfp_port("qsfp0_sfp0") == (0, 0)
    assert parse_qsfp_port("qsfp1_sfp3") == (1, 3)


def test_xcu1525_qsfp_port_parser_rejects_invalid_port():
    with pytest.raises(ValueError):
        parse_qsfp_port("qsfp2_sfp0")


def test_alibaba_qsfp_port_parser_uses_sfp_lane_names():
    assert len(ALIBABA_QSFP_PORTS) == 8
    assert parse_alibaba_qsfp_port("qsfp0_sfp0") == (0, 0)
    assert parse_alibaba_qsfp_port("qsfp1_sfp3") == (1, 3)


def test_alibaba_qsfp_port_parser_rejects_old_short_names():
    with pytest.raises(ValueError):
        parse_alibaba_qsfp_port("qsfp0_0")
