#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

import os

from migen import *
from migen.genlib.cdc import PulseSynchronizer

from litex.gen import *

from liteiclink.serdes.gty_ultrascale import GTYQuadPLL

from liteeth.phy.usp_gty_10g_baser import USP_GTY_10G_BASER
from liteeth.phy.xgmii import LiteEthPHYXGMIIPads, LiteEthPHYXGMIITX, LiteEthPHYXGMIIRX

# Constants ----------------------------------------------------------------------------------------

USP_GTY_10GBASE_R_REFCLK_FREQ = 156.25e6
USP_GTY_10GBASE_R_LINERATE    = 10.3125e9

USP_GTY_10G_RTL_DIR = os.path.join(os.path.dirname(__file__), "rtl", "usp_gty_10g")
USP_GTY_10G_RTL_SOURCES = [
    "lfsr.v",
    "eth_phy_10g_tx_if.v",
    "eth_phy_10g_rx_if.v",
    "eth_phy_10g_rx_frame_sync.v",
    "eth_phy_10g_rx_ber_mon.v",
    "eth_phy_10g_rx_watchdog.v",
    "xgmii_baser_enc_64.v",
    "xgmii_baser_dec_64.v",
    "eth_phy_10g_tx.v",
    "eth_phy_10g_rx.v",
    "eth_phy_10g.v",
]

# Helpers ------------------------------------------------------------------------------------------

def gty_refclk_from_pads(module, refclk_pads):
    refclk = Signal()
    try:
        refclk_p = refclk_pads.p
        refclk_n = refclk_pads.n
    except AttributeError:
        refclk_p = refclk_pads.clk_p
        refclk_n = refclk_pads.clk_n
    module.specials += Instance("IBUFDS_GTE4",
        p_REFCLK_HROW_CK_SEL = 0,
        i_I   = refclk_p,
        i_IB  = refclk_n,
        i_CEB = 0,
        o_O   = refclk,
    )
    return refclk

def gty_data_pads_lane(module, data_pads, lane=None):
    if lane is None:
        return data_pads

    lane_pads = Record([("txp", 1), ("txn", 1), ("rxp", 1), ("rxn", 1)])
    module.comb += [
        lane_pads.rxp.eq(data_pads.rxp[lane]),
        lane_pads.rxn.eq(data_pads.rxn[lane]),
        data_pads.txp[lane].eq(lane_pads.txp),
        data_pads.txn[lane].eq(lane_pads.txn),
    ]
    return lane_pads

# 10GBASE-R PHY ------------------------------------------------------------------------------------

class LiteEthPHYUSPGTY10G(LiteXModule):
    dw          = 64
    tx_clk_freq = USP_GTY_10GBASE_R_REFCLK_FREQ
    rx_clk_freq = USP_GTY_10GBASE_R_REFCLK_FREQ
    integrated_ifg_inserter = True

    def __init__(self, platform, refclk, data_pads, sys_clk_freq,
        refclk_freq        = USP_GTY_10GBASE_R_REFCLK_FREQ,
        refclk_from_fabric = False):
        self.pll    = pll    = GTYQuadPLL(refclk, refclk_freq, USP_GTY_10GBASE_R_LINERATE, refclk_from_fabric=refclk_from_fabric)
        self.serdes = serdes = USP_GTY_10G_BASER(pll, data_pads=data_pads, sys_clk_freq=sys_clk_freq)
        self.cd_eth_tx = serdes.cd_eth_tx
        self.cd_eth_rx = serdes.cd_eth_rx

        xgmii = LiteEthPHYXGMIIPads()
        self.tx = ClockDomainsRenamer("eth_tx")(LiteEthPHYXGMIITX(xgmii, dw=64))
        self.rx = ClockDomainsRenamer("eth_rx")(LiteEthPHYXGMIIRX(xgmii, dw=64))
        self.sink, self.source = self.tx.sink, self.rx.source

        self.tx_bad_block      = Signal()
        self.rx_error_count    = Signal(7)
        self.rx_bad_block      = Signal()
        self.rx_sequence_error = Signal()
        self.rx_block_lock     = Signal()
        self.rx_high_ber       = Signal()
        self.rx_status         = Signal()
        self.link_up           = Signal()

        # # #

        platform.add_sources(USP_GTY_10G_RTL_DIR, *USP_GTY_10G_RTL_SOURCES)
        self.comb += self.link_up.eq(self.rx_status)

        rx_reset_req = Signal()
        rx_restart = PulseSynchronizer("eth_rx", "sys")
        self.submodules += rx_restart
        self.comb += [
            rx_restart.i.eq(rx_reset_req),
            serdes.rx_init.restart.eq(rx_restart.o),
        ]

        self.specials += Instance("eth_phy_10g",
            p_DATA_WIDTH           = 64,
            p_CTRL_WIDTH           = 8,
            p_HDR_WIDTH            = 2,
            i_tx_clk               = ClockSignal("eth_tx"),
            i_tx_rst               = ResetSignal("eth_tx"),
            i_rx_clk               = ClockSignal("eth_rx"),
            i_rx_rst               = ResetSignal("eth_rx"),
            i_xgmii_txd            = xgmii.tx_data,
            i_xgmii_txc            = xgmii.tx_ctl,
            o_xgmii_rxd            = xgmii.rx_data,
            o_xgmii_rxc            = xgmii.rx_ctl,
            o_serdes_tx_data       = serdes.tx_data,
            o_serdes_tx_hdr        = serdes.tx_header,
            i_serdes_rx_data       = serdes.rx_data,
            i_serdes_rx_hdr        = serdes.rx_header,
            o_serdes_rx_bitslip    = serdes.rx_slip,
            o_serdes_rx_reset_req  = rx_reset_req,
            o_tx_bad_block         = self.tx_bad_block,
            o_rx_error_count       = self.rx_error_count,
            o_rx_bad_block         = self.rx_bad_block,
            o_rx_sequence_error    = self.rx_sequence_error,
            o_rx_block_lock        = self.rx_block_lock,
            o_rx_high_ber          = self.rx_high_ber,
            o_rx_status            = self.rx_status,
            i_cfg_tx_prbs31_enable = 0,
            i_cfg_rx_prbs31_enable = 0,
        )
