#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

import os

from migen import *

from litex.gen import *

from litex_boards.platforms import sqrl_xcu1525
from litex_boards.targets.usp_gty_10g import LiteEthPHYUSPGTY10G

from litex.soc.cores.clock import *
from litex.soc.integration.soc import SoCIORegion, SoCRegion
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litedram.modules import MT40A512M8
from litedram.phy import usddrphy

from liteeth.phy.usp_gty_1000basex import USP_GTY_1000BASEX, USP_GTY_2500BASEX

from litepcie.phy.usppciephy import USPPCIEPHY
from litepcie.software import generate_litepcie_software

# QSFP ---------------------------------------------------------------------------------------------

QSFP_PORTS   = tuple(f"qsfp{qsfp}_sfp{sfp}"    for qsfp in range(2) for sfp in range(4))
QSFP_REFCLKS = tuple(f"qsfp{qsfp}_refclk{ref}" for qsfp in range(2) for ref in range(2))

ETHERNET_RATES  = ("1g", "2.5g", "10g")
ETHERBONE_RATES = ("1g", "2.5g")

QSFP_FABRIC_REFCLK_FREQ = 200e6
QSFP_156P25_REFCLK_FREQ = 156.25e6

DDRAM_CHANNELS          = tuple(range(4))
DDRAM_CHANNEL_SIZE      = 0x40000000
DDRAM_32BIT_WINDOW_SIZE = 0x20000000
DDRAM_ORIGINS           = {
    0: 0x40000000,
    1: 0x80000000,
    2: 0xc0000000,
    3: 0x1_0000_0000,
}
DDRAM_CSR_ORIGIN   = 0x20000000
DDRAM_DEBUG_ORIGIN = 0x20010000
DDRAM_FULL_MAP_PHYSICAL_WIDTH = 38
DDRAM_FULL_MAP_IO_REGIONS     = {
    DDRAM_CSR_ORIGIN : 0x02000000,
    0xf0000000       : 0x10000000,
}

def parse_qsfp_port(port):
    if port not in QSFP_PORTS:
        raise ValueError("QSFP port must be one of: " + ", ".join(QSFP_PORTS))
    qsfp, sfp = port.replace("qsfp", "").split("_sfp")
    return int(qsfp), int(sfp)

def get_qsfp_refclk_name(port, refclk):
    if refclk == "auto":
        qsfp, _ = parse_qsfp_port(port)
        return f"qsfp{qsfp}_refclk0"
    if refclk not in QSFP_REFCLKS:
        raise ValueError("QSFP refclk must be auto or one of: " + ", ".join(QSFP_REFCLKS))
    return refclk

def parse_qsfp_refclk(refclk):
    qsfp, refclk_id = refclk.replace("qsfp", "").split("_refclk")
    return int(qsfp), int(refclk_id)

def is_156p25mhz(freq):
    return abs(freq - QSFP_156P25_REFCLK_FREQ) < 1

def get_basex_phy(rate):
    return {
        "1g"   : USP_GTY_1000BASEX,
        "2.5g" : USP_GTY_2500BASEX,
    }[rate]

def parse_ddram_channels(channels):
    if isinstance(channels, int):
        parsed_channels = [channels]
    elif isinstance(channels, str):
        channels = channels.strip().lower()
        if channels == "all":
            parsed_channels = list(DDRAM_CHANNELS)
        else:
            parsed_channels = []
            for item in channels.split(","):
                item = item.strip()
                if not item:
                    raise ValueError("empty DDRAM channel entry")
                if "-" in item:
                    start, end = [int(v, 0) for v in item.split("-", 1)]
                    if end < start:
                        raise ValueError("DDRAM channel ranges must be increasing")
                    parsed_channels.extend(range(start, end + 1))
                else:
                    parsed_channels.append(int(item, 0))
    else:
        parsed_channels = list(channels)

    if not parsed_channels:
        raise ValueError("at least one DDRAM channel must be selected")
    if len(parsed_channels) != len(set(parsed_channels)):
        raise ValueError("DDRAM channels must be unique")
    for channel in parsed_channels:
        if channel not in DDRAM_CHANNELS:
            raise ValueError("DDRAM channel must be 0, 1, 2 or 3")
    return tuple(parsed_channels)

def get_ddram_origins(channels, main_channel, window_size):
    main_ram_origin = SoCCore.mem_map["main_ram"]
    if window_size == DDRAM_CHANNEL_SIZE:
        return {
            channel: (DDRAM_ORIGINS[channel] if channel != main_channel else main_ram_origin)
            for channel in channels
        }
    return {
        channel: main_ram_origin + n*window_size
        for n, channel in enumerate(channels)
    }

def ddram_window_end(origins, window_size):
    return max(origin + window_size for origin in origins.values())

def ddram_windows_overlap(origins, window_size, origin, size):
    if origin is None:
        return False
    return any(
        (origin < ddram_origin + window_size) and (origin + size > ddram_origin)
        for ddram_origin in origins.values()
    )

def remap_ddram_origins_around_vexii_io(origins, main_channel):
    remapped = {}
    high_origin = 0x1_0000_0000
    for channel in sorted(origins):
        origin = origins[channel]
        if channel != main_channel and origin >= 0xc0000000:
            origin = high_origin
            high_origin += DDRAM_CHANNEL_SIZE
        remapped[channel] = origin
    return remapped

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, ddram_channel, with_qsfp=False):
        self.rst       = Signal()
        self.cd_sys    = ClockDomain()
        self.cd_sys4x  = ClockDomain()
        self.cd_pll4x  = ClockDomain()
        self.cd_idelay = ClockDomain()
        if with_qsfp:
            self.cd_eth = ClockDomain()

        # # #

        self.pll = pll = USPMMCM(speedgrade=-2)
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(platform.request("clk300", ddram_channel), 300e6)
        pll.create_clkout(self.cd_pll4x, sys_clk_freq*4, buf=None, with_reset=False)
        pll.create_clkout(self.cd_idelay, 500e6)
        if with_qsfp:
            pll.create_clkout(self.cd_eth, QSFP_FABRIC_REFCLK_FREQ, margin=0)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        self.specials += [
            Instance("BUFGCE_DIV",
                p_BUFGCE_DIVIDE=4,
                i_CE=1, i_I=self.cd_pll4x.clk, o_O=self.cd_sys.clk),
            Instance("BUFGCE",
                i_CE=1, i_I=self.cd_pll4x.clk, o_O=self.cd_sys4x.clk),
        ]

        self.idelayctrl = USPIDELAYCTRL(cd_ref=self.cd_idelay, cd_sys=self.cd_sys)
        platform.add_platform_command(
            "set_false_path -quiet "
            "-to [get_cells -quiet -hierarchical -filter {{NAME =~ *idelayctrl*ic_reset_reg*}}]"
        )
        platform.add_platform_command(
            "set_false_path -quiet "
            "-to [get_pins -quiet -of_objects "
            "[get_cells -quiet -hierarchical -filter {{REF_NAME == IDELAYCTRL}}] "
            "-filter {{REF_PIN_NAME == RST}}]"
        )

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=125e6, ddram_channel=0,
        ddram_channels        = None,
        with_led_chaser       = True,
        with_pcie             = False,
        pcie_lanes            = 4,
        pcie_ndmas            = 1,
        pcie_address_width    = 32,
        ddram_full_map        = False,
        with_pcie_dma_status  = False,
        with_pcie_dma_monitor = False,
        with_sdram_bist       = False,
        with_sata             = False,
        with_ethernet         = False,
        with_etherbone        = False,
        ethernet_port         = "qsfp0_sfp0",
        etherbone_port        = "qsfp0_sfp1",
        ethernet_rate         = "1g",
        etherbone_rate        = "1g",
        ethernet_refclk       = "auto",
        ethernet_refclk_freq  = QSFP_156P25_REFCLK_FREQ,
        eth_ip                = "192.168.1.50",
        eth_dynamic_ip        = False,
        remote_ip             = None,
        etherbone_ip          = "192.168.1.50",
        **kwargs):
        platform = sqrl_xcu1525.Platform()
        if ddram_channels is None:
            ddram_channels = (ddram_channel,)
        ddram_channels = parse_ddram_channels(ddram_channels)
        ddram_main_channel = 0 if 0 in ddram_channels else ddram_channels[0]
        bus_address_width = kwargs.get("bus_address_width", 32)
        ddram_window_size = DDRAM_CHANNEL_SIZE
        ddram_origins = get_ddram_origins(ddram_channels, ddram_main_channel, ddram_window_size)
        is_vexiiriscv = kwargs.get("cpu_type", "vexriscv") == "vexiiriscv"
        if ddram_full_map and is_vexiiriscv:
            ddram_origins = remap_ddram_origins_around_vexii_io(ddram_origins, ddram_main_channel)
        ddram_end = ddram_window_end(ddram_origins, ddram_window_size)
        if ddram_full_map:
            if bus_address_width <= 32:
                kwargs["bus_address_width"] = 64
                bus_address_width = 64
            if ddram_end > 2**bus_address_width:
                kwargs["bus_address_width"] = 64
            if is_vexiiriscv:
                from litex.soc.cores.cpu.vexiiriscv.core import VexiiRiscv
                VexiiRiscv.set_physical_width(max(DDRAM_FULL_MAP_PHYSICAL_WIDTH, ddram_end.bit_length()))
                if VexiiRiscv.io_regions == {0x8000_0000: 0x8000_0000}:
                    VexiiRiscv.io_regions = dict(DDRAM_FULL_MAP_IO_REGIONS)
        elif ddram_end > 2**bus_address_width and bus_address_width <= 32:
            ddram_window_size = DDRAM_32BIT_WINDOW_SIZE
            ddram_origins = get_ddram_origins(ddram_channels, ddram_main_channel, ddram_window_size)
            ddram_end = ddram_window_end(ddram_origins, ddram_window_size)
        if ddram_end > 2**bus_address_width:
            kwargs["bus_address_width"] = 64
        if with_pcie and ddram_end > 2**pcie_address_width:
            pcie_address_width = 64
        if with_ethernet and with_etherbone and ethernet_port == etherbone_port:
            raise ValueError("Ethernet and Etherbone QSFP ports must be different")
        if ethernet_rate not in ETHERNET_RATES:
            raise ValueError("Ethernet rate must be one of: " + ", ".join(ETHERNET_RATES))
        if etherbone_rate not in ETHERBONE_RATES:
            raise ValueError("Etherbone rate must be one of: " + ", ".join(ETHERBONE_RATES))

        # CRG --------------------------------------------------------------------------------------
        with_qsfp = with_ethernet or with_etherbone
        self.crg = _CRG(platform, sys_clk_freq, ddram_main_channel, with_qsfp=with_qsfp)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on XCU1525", **kwargs)
        relocated_io = False
        if ddram_windows_overlap(ddram_origins, ddram_window_size, self.mem_map.get("csr"), 2**(self.csr.address_width + 2)):
            self.mem_map["csr"] = DDRAM_CSR_ORIGIN
            relocated_io = True
        if ddram_windows_overlap(ddram_origins, ddram_window_size, self.mem_map.get("vexriscv_debug"), 0x100):
            self.mem_map["vexriscv_debug"] = DDRAM_DEBUG_ORIGIN
            relocated_io = True
        if relocated_io:
            self.bus.add_region("csr_io", SoCIORegion(origin=DDRAM_CSR_ORIGIN, size=0x20000))

        # DDR4 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.ddrphys = {}
            for channel in ddram_channels:
                phy_name = f"ddrphy{channel}"
                phy = usddrphy.USPDDRPHY(
                    pads             = platform.request("ddram", channel),
                    memtype          = "DDR4",
                    sys_clk_freq     = sys_clk_freq,
                    iodelay_clk_freq = 500e6)
                setattr(self, phy_name, phy)
                self.ddrphys[channel] = phy

                is_main    = channel == ddram_main_channel
                sdram_name = "sdram" if is_main else f"sdram{channel}"
                origin     = ddram_origins[channel]
                cached     = is_main if ddram_full_map else not (0x8000_0000 <= origin < 0x1_0000_0000)
                if ddram_full_map and not is_main:
                    ddram_io_region = SoCRegion(origin=origin, size=ddram_window_size, cached=False)
                    if not self.bus.check_region_is_io(ddram_io_region):
                        self.bus.add_region(f"ddram{channel}_io", SoCIORegion(origin=origin, size=ddram_window_size))
                self.add_sdram(sdram_name,
                    phy           = phy,
                    module        = MT40A512M8(sys_clk_freq, "1:4"),
                    origin        = origin,
                    size          = ddram_window_size,
                    region_name   = None if is_main else f"ddram{channel}",
                    main_ram      = is_main,
                    channel       = channel,
                    phy_name      = phy_name,
                    ddrctrl_name  = f"ddrctrl{channel}",
                    with_bist     = with_sdram_bist,
                    cached        = cached,
                    l2_cache_size = kwargs.get("l2_size", 8192)
                )
            self.add_constant("DDRAM_CHANNELS", len(ddram_channels))
            self.add_constant("DDRAM_MAIN_CHANNEL", ddram_main_channel)
            self.add_constant("DDRAM_WINDOW_SIZE", ddram_window_size)
            self.add_constant("DDRAM_FULL_MAP", int(ddram_full_map))
            # Workadound for Vivado 2018.2 DRC, can be ignored and probably fixed on newer Vivado versions.
            platform.add_platform_command("set_property SEVERITY {{Warning}} [get_drc_checks PDCN-2736]")

        # PCIe -------------------------------------------------------------------------------------
        if with_pcie:
            self.pcie_phy = USPPCIEPHY(platform, platform.request(f"pcie_x{pcie_lanes}"),
                data_width = {2: 64, 4: 128, 8: 256, 16: 512}[pcie_lanes],
                bar0_size  = 0x20000)
            self.add_pcie(
                phy              = self.pcie_phy,
                ndmas            = pcie_ndmas,
                address_width    = pcie_address_width,
                with_dma_status  = with_pcie_dma_status,
                with_dma_monitor = with_pcie_dma_monitor)

        # Ethernet / Etherbone ---------------------------------------------------------------------
        qsfp_in_use           = [False, False]
        qsfp_refclk_156p25mhz = [False, False]
        qsfp_refclks          = {}

        def get_qsfp_external_refclk(refclk_name, refclk_freq):
            if refclk_name not in qsfp_refclks:
                refclk = Signal()
                refclk_pads = platform.request(refclk_name)
                self.specials += Instance("IBUFDS_GTE4",
                    p_REFCLK_HROW_CK_SEL = 0,
                    i_I   = refclk_pads.p,
                    i_IB  = refclk_pads.n,
                    i_CEB = 0,
                    o_O   = refclk,
                )
                qsfp_refclks[refclk_name] = refclk
            qsfp_id, _ = parse_qsfp_refclk(refclk_name)
            qsfp_refclk_156p25mhz[qsfp_id] |= is_156p25mhz(refclk_freq)
            return qsfp_refclks[refclk_name]

        def get_qsfp_156p25mhz_refclk(qsfp_id):
            return get_qsfp_external_refclk(f"qsfp{qsfp_id}_refclk0", QSFP_156P25_REFCLK_FREQ)

        if with_ethernet:
            qsfp_id, sfp_lane = parse_qsfp_port(ethernet_port)
            data_pads = platform.request(f"qsfp{qsfp_id}_sfp{sfp_lane}")
            if ethernet_rate == "10g":
                refclk_name = get_qsfp_refclk_name(ethernet_port, ethernet_refclk)
                refclk = get_qsfp_external_refclk(refclk_name, ethernet_refclk_freq)
                self.ethphy = LiteEthPHYUSPGTY10G(
                    platform        = platform,
                    refclk          = refclk,
                    data_pads       = data_pads,
                    sys_clk_freq    = self.clk_freq,
                    refclk_freq     = ethernet_refclk_freq)
            else:
                basex_refclk      = self.crg.cd_eth.clk
                basex_refclk_freq = QSFP_FABRIC_REFCLK_FREQ
                basex_from_fabric = True
                if ethernet_rate == "2.5g":
                    basex_refclk      = get_qsfp_156p25mhz_refclk(qsfp_id)
                    basex_refclk_freq = QSFP_156P25_REFCLK_FREQ
                    basex_from_fabric = False
                self.ethphy = get_basex_phy(ethernet_rate)(basex_refclk,
                    data_pads          = data_pads,
                    sys_clk_freq       = self.clk_freq,
                    refclk_freq        = basex_refclk_freq,
                    refclk_from_fabric = basex_from_fabric)
            self.add_ethernet(
                phy        = self.ethphy,
                data_width = 32 if ethernet_rate == "10g" else 8,
                local_ip   = eth_ip if not eth_dynamic_ip else None,
                dynamic_ip = eth_dynamic_ip,
                remote_ip  = remote_ip)
            qsfp_in_use[qsfp_id] = True

        if with_etherbone:
            qsfp_id, sfp_lane = parse_qsfp_port(etherbone_port)
            basex_refclk      = self.crg.cd_eth.clk
            basex_refclk_freq = QSFP_FABRIC_REFCLK_FREQ
            basex_from_fabric = True
            if etherbone_rate == "2.5g":
                basex_refclk      = get_qsfp_156p25mhz_refclk(qsfp_id)
                basex_refclk_freq = QSFP_156P25_REFCLK_FREQ
                basex_from_fabric = False
            self.bonephy = get_basex_phy(etherbone_rate)(basex_refclk,
                data_pads          = platform.request(f"qsfp{qsfp_id}_sfp{sfp_lane}"),
                sys_clk_freq       = self.clk_freq,
                refclk_freq        = basex_refclk_freq,
                refclk_from_fabric = basex_from_fabric)
            self.add_etherbone(phy=self.bonephy, ip_address=etherbone_ip)
            qsfp_in_use[qsfp_id] = True

        # SATA -------------------------------------------------------------------------------------
        if with_sata:
            from litex.build.generic_platform import Subsignal, Pins
            from litesata.phy import LiteSATAPHY

            # IOs
            _sata_io = [
                # SFP 2 SATA Adapter / https://shop.trenz-electronic.de/en/TE0424-01-SFP-2-SATA-Adapter
                ("qsfp2sata", 0,
                    Subsignal("tx_p", Pins("N9")),
                    Subsignal("tx_n", Pins("N8")),
                    Subsignal("rx_p", Pins("N4")),
                    Subsignal("rx_n", Pins("N3")),
                ),
            ]
            platform.add_extension(_sata_io)

            # RefClk, Generate 150MHz from PLL.
            self.cd_sata_refclk = ClockDomain()
            self.crg.pll.create_clkout(self.cd_sata_refclk, 150e6)
            sata_refclk = ClockSignal("sata_refclk")

            # PHY
            self.sata_phy = LiteSATAPHY(platform.device,
                refclk     = sata_refclk,
                pads       = platform.request("qsfp2sata"),
                gen        = "gen2",
                clk_freq   = sys_clk_freq,
                data_width = 16)

            # Core
            self.add_sata(phy=self.sata_phy, mode="read+write")
            qsfp_in_use[0] = True

        for qsfp_id, in_use in enumerate(qsfp_in_use):
            if in_use:
                resetl = platform.request(f"qsfp{qsfp_id}_resetl")
                lpmode = platform.request(f"qsfp{qsfp_id}_lpmode")

                reset_cycles = int(sys_clk_freq*10e-3)
                reset_count  = Signal(max=reset_cycles + 1, reset=reset_cycles)
                self.sync += [
                    If(ResetSignal("sys"),
                        reset_count.eq(reset_cycles)
                    ).Elif(reset_count != 0,
                        reset_count.eq(reset_count - 1)
                    )
                ]
                self.comb += [
                    resetl.eq(~(ResetSignal("sys") | (reset_count != 0))),
                    lpmode.eq(0),
                ]
                if qsfp_refclk_156p25mhz[qsfp_id]:
                    self.comb += platform.request(f"qsfp{qsfp_id}_fs").eq(0b01)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=sqrl_xcu1525.Platform, description="LiteX SoC on XCU1525.")
    parser.add_target_argument("--sys-clk-freq",  default=125e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--ddram-channel",  default=0, type=lambda x: int(x, 0), choices=range(4), help="Legacy single DDRAM channel selector.")
    parser.add_target_argument("--ddram-channels", default=None, help="DDRAM channels to map (comma/range list or all).")
    parser.add_target_argument("--ddram-full-map", action="store_true", help="Map selected DDRAM channels at their full native address windows.")
    parser.add_target_argument("--with-pcie",     action="store_true",        help="Enable PCIe support.")
    parser.add_target_argument("--pcie-lanes",    default=4, type=int,        choices=[2, 4, 8, 16], help="PCIe lane count.")
    parser.add_target_argument("--pcie-ndmas",    default=1, type=int,        help="Number of PCIe DMA channels.")
    parser.add_target_argument("--pcie-address-width", default=32, type=int, choices=[32, 64], help="PCIe address width.")
    parser.add_target_argument("--pcie-with-dma-status",  action="store_true",       help="Enable PCIe DMA status CSRs.")
    parser.add_target_argument("--pcie-with-dma-monitor", action="store_true",       help="Enable PCIe DMA monitor CSRs.")
    parser.add_target_argument("--with-sdram-bist",       action="store_true",       help="Enable LiteDRAM BIST generator/checker on selected DDRAM channels.")
    parser.add_target_argument("--with-ethernet",         action="store_true",       help="Enable Ethernet support over QSFP/SFP.")
    parser.add_target_argument("--with-etherbone",        action="store_true",       help="Enable Etherbone support over QSFP/SFP.")
    parser.add_target_argument("--ethernet-port",        default="qsfp0_sfp0",             choices=QSFP_PORTS,       help="Ethernet QSFP/SFP port.")
    parser.add_target_argument("--etherbone-port",       default="qsfp0_sfp1",             choices=QSFP_PORTS,       help="Etherbone QSFP/SFP port.")
    parser.add_target_argument("--ethernet-rate",        default="1g",                     choices=ETHERNET_RATES,   help="Ethernet line rate.")
    parser.add_target_argument("--etherbone-rate",       default="1g",                     choices=ETHERBONE_RATES,  help="Etherbone line rate.")
    parser.add_target_argument("--ethernet-refclk",      default="auto",                   choices=("auto",) + QSFP_REFCLKS, help="QSFP refclk for 10G Ethernet.")
    parser.add_target_argument("--ethernet-refclk-freq", default=QSFP_156P25_REFCLK_FREQ,  type=float,               help="QSFP refclk frequency for 10G Ethernet.")
    parser.add_target_argument("--ethernet-ip",    default="192.168.1.50",    help="Ethernet IP address.")
    parser.add_target_argument("--remote-ip",      default="192.168.1.100",   help="Remote IP address of TFTP server.")
    parser.add_target_argument("--eth-dynamic-ip", action="store_true",       help="Enable dynamic Ethernet IP assignment.")
    parser.add_target_argument("--etherbone-ip",   default="192.168.1.50",    help="Etherbone IP address.")
    parser.add_target_argument("--driver",        action="store_true",        help="Generate PCIe driver.")
    parser.add_target_argument("--with-sata",     action="store_true",        help="Enable SATA support (over SFP2SATA on qsfp0_sfp0).")

    # VexiiRiscv exposes an AXI-Lite peripheral bus, so use AXI-Lite as the
    # default SoC bus for this CPU while still allowing explicit overrides.
    if (parser.get_value_from_key("--cpu-type", None) == "vexiiriscv" and
        parser.get_value_from_key("--bus-standard", None) is None):
        parser.set_defaults(bus_standard="axi-lite")

    args = parser.parse_args()
    if args.with_etherbone and args.eth_dynamic_ip:
        parser.error("--eth-dynamic-ip cannot be used with Etherbone.")
    if args.pcie_ndmas < 0:
        parser.error("--pcie-ndmas must be >= 0")
    if args.with_ethernet and args.with_etherbone and args.ethernet_port == args.etherbone_port:
        parser.error("Ethernet and Etherbone QSFP ports must be different.")
    if args.with_sata:
        for feature, port in [
            ("Ethernet",  args.ethernet_port  if args.with_ethernet  else None),
            ("Etherbone", args.etherbone_port if args.with_etherbone else None),
        ]:
            if port == "qsfp0_sfp0":
                parser.error(f"{feature} on qsfp0_sfp0 conflicts with SATA.")
    try:
        ddram_channels = parse_ddram_channels(args.ddram_channels if args.ddram_channels is not None else args.ddram_channel)
    except ValueError as e:
        parser.error(str(e))

    soc = BaseSoC(
        sys_clk_freq          = args.sys_clk_freq,
        ddram_channels        = ddram_channels,
        ddram_full_map        = args.ddram_full_map,
        with_pcie             = args.with_pcie,
        pcie_lanes            = args.pcie_lanes,
        pcie_ndmas            = args.pcie_ndmas,
        pcie_address_width    = args.pcie_address_width,
        with_pcie_dma_status  = args.pcie_with_dma_status,
        with_pcie_dma_monitor = args.pcie_with_dma_monitor,
        with_sdram_bist       = args.with_sdram_bist,
        with_sata             = args.with_sata,
        with_ethernet         = args.with_ethernet,
        with_etherbone        = args.with_etherbone,
        ethernet_port         = args.ethernet_port,
        etherbone_port        = args.etherbone_port,
        ethernet_rate         = args.ethernet_rate,
        etherbone_rate        = args.etherbone_rate,
        ethernet_refclk       = args.ethernet_refclk,
        ethernet_refclk_freq  = args.ethernet_refclk_freq,
        eth_ip                = args.ethernet_ip,
        eth_dynamic_ip        = args.eth_dynamic_ip,
        remote_ip             = args.remote_ip,
        etherbone_ip          = args.etherbone_ip,
        **parser.soc_argdict
    )
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.driver:
        generate_litepcie_software(soc, os.path.join(builder.output_dir, "driver"))

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
