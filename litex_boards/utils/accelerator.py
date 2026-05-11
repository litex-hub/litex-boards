#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

import os

from litex.gen import LiteXModule

from litex.soc.integration.soc import SoCRegion
from litex.soc.interconnect.axi import AXILiteInterface, AXILite2AXI

# HBM ----------------------------------------------------------------------------------------------

HBM_NCHANNELS    = 32
HBM_CHANNEL_SIZE = 0x1000_0000 # 256MB.
HBM_DEFAULT_BASE = 0x4000_0000
HBM_HIGH_BASE    = 0x1_0000_0000

def parse_hbm_channels(channels):
    if isinstance(channels, str):
        channels = channels.strip().lower()
        if channels == "all":
            parsed_channels = list(range(HBM_NCHANNELS))
        else:
            parsed_channels = []
            for item in channels.split(","):
                item = item.strip()
                if not item:
                    raise ValueError("empty HBM channel entry")
                if "-" in item:
                    start, end = [int(v, 0) for v in item.split("-", 1)]
                    if end < start:
                        raise ValueError("HBM channel ranges must be increasing")
                    parsed_channels.extend(range(start, end + 1))
                else:
                    parsed_channels.append(int(item, 0))
    else:
        parsed_channels = list(channels)

    if not parsed_channels:
        raise ValueError("at least one HBM channel must be selected")
    if len(parsed_channels) != len(set(parsed_channels)):
        raise ValueError("HBM channels must be unique")
    for channel in parsed_channels:
        if not 0 <= channel < HBM_NCHANNELS:
            raise ValueError(f"HBM channel {channel} outside 0-{HBM_NCHANNELS - 1}")
    return tuple(parsed_channels)

def hbm_channel_origin(channel, hbm_base=HBM_DEFAULT_BASE, hbm_high_base=HBM_HIGH_BASE):
    origin = hbm_base + HBM_CHANNEL_SIZE*channel
    if hbm_base == HBM_DEFAULT_BASE and origin >= 0x8000_0000:
        origin = hbm_high_base + HBM_CHANNEL_SIZE*(channel - 4)
    return origin

def hbm_channel_origins(channels, hbm_base=HBM_DEFAULT_BASE, hbm_high_base=HBM_HIGH_BASE):
    return {
        channel: hbm_channel_origin(channel, hbm_base, hbm_high_base)
        for channel in channels
    }

def hbm_window_end(origins):
    return max(origin + HBM_CHANNEL_SIZE for origin in origins.values())

def ensure_hbm_xci(url, hbm_xci=os.path.join("ip", "hbm", "hbm_0.xci")):
    if not os.path.exists(hbm_xci):
        os.makedirs(os.path.dirname(hbm_xci), exist_ok=True)
        os.system(f"wget -O {hbm_xci} {url}")

class AXILiteAddressRemapper(LiteXModule):
    def __init__(self, master, slave, origin=0):
        self.comb += [
            slave.aw.valid.eq(master.aw.valid),
            master.aw.ready.eq(slave.aw.ready),
            slave.aw.first.eq(master.aw.first),
            slave.aw.last.eq(master.aw.last),
            slave.aw.addr.eq(master.aw.addr - origin),
            slave.aw.prot.eq(master.aw.prot),

            slave.w.valid.eq(master.w.valid),
            master.w.ready.eq(slave.w.ready),
            slave.w.first.eq(master.w.first),
            slave.w.last.eq(master.w.last),
            slave.w.data.eq(master.w.data),
            slave.w.strb.eq(master.w.strb),

            master.b.valid.eq(slave.b.valid),
            slave.b.ready.eq(master.b.ready),
            master.b.first.eq(slave.b.first),
            master.b.last.eq(slave.b.last),
            master.b.resp.eq(slave.b.resp),

            slave.ar.valid.eq(master.ar.valid),
            master.ar.ready.eq(slave.ar.ready),
            slave.ar.first.eq(master.ar.first),
            slave.ar.last.eq(master.ar.last),
            slave.ar.addr.eq(master.ar.addr - origin),
            slave.ar.prot.eq(master.ar.prot),

            master.r.valid.eq(slave.r.valid),
            slave.r.ready.eq(master.r.ready),
            master.r.first.eq(slave.r.first),
            master.r.last.eq(slave.r.last),
            master.r.data.eq(slave.r.data),
            master.r.resp.eq(slave.r.resp),
        ]

def add_hbm_pseudochannels(soc, hbm, channels, main_channel, origins,
    hbm_high_base    = HBM_HIGH_BASE,
    hbm_strip_origin = False):

    hbm_regions = {}
    for channel in channels:
        axi_hbm      = hbm.axi[channel]
        axi_lite_bus = AXILiteInterface(data_width=256, address_width=soc.bus.address_width)
        axi_lite_hbm = AXILiteInterface(data_width=256, address_width=33)
        origin       = origins[channel]
        soc.submodules += AXILiteAddressRemapper(
            master = axi_lite_bus,
            slave  = axi_lite_hbm,
            origin = origin if hbm_strip_origin else 0)
        soc.submodules += AXILite2AXI(axi_lite_hbm, axi_hbm)
        hbm_regions[channel] = origin
        soc.bus.add_slave(
            f"hbm{channel}",
            axi_lite_bus,
            SoCRegion(
                origin = origin,
                size   = HBM_CHANNEL_SIZE,
                cached = not (0x8000_0000 <= origin < 0x1_0000_0000)))

    soc.add_constant("HBM_CHANNELS", len(channels))
    soc.add_constant("HBM_MAIN_CHANNEL", main_channel)
    soc.add_constant("HBM_HIGH_BASE", hbm_high_base)
    soc.bus.add_region("main_ram", SoCRegion(
        origin = hbm_regions[main_channel],
        size   = HBM_CHANNEL_SIZE,
        linker = True))
    return hbm_regions
