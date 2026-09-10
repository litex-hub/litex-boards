import pytest

from litex_boards.targets import lambdaconcept_ecpix5, qmtech_wukong, terasic_deca


@pytest.mark.parametrize("target", [lambdaconcept_ecpix5, qmtech_wukong, terasic_deca])
@pytest.mark.parametrize("ethernet, etherbone", [(True, False), (False, True), (True, True)])
def test_ethernet_and_etherbone(target, ethernet, etherbone):
    soc = target.BaseSoC(
        with_ethernet=ethernet,
        with_etherbone=etherbone,
        uart_name="stub",
        integrated_main_ram_size=0x10000,
    )
    assert hasattr(soc, "ethmac") == ethernet
    assert hasattr(soc, "etherbone") == etherbone
    assert ("ethmac_rx" in soc.bus.slaves) == ethernet
    assert ("ethmac_tx" in soc.bus.slaves) == ethernet
    assert ("etherbone" in soc.bus.masters) == etherbone
    if ethernet and etherbone:
        assert soc.constants["LOCALIP4"] == 51
