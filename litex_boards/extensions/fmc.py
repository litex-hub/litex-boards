#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

"""FMC modules, described once as Extensions and usable on any board exposing FMC connectors.

Canonical FMC connector (VITA 57.1 LPC/HPC, VITA 57.4 HSPC): a dict connector using the signal names
of the specification as keys:

- LAnn_P/LAnn_N (LA00-LA33), HAnn_P/HAnn_N (HA00-HA23), HBnn_P/HBnn_N (HB00-HB21): User IOs, with a
  _CC suffix on clock capable pairs (ex: LA00_CC_P, LA01_CC_P, LA17_CC_P, LA18_CC_P).
- CLKn_M2C_P/CLKn_M2C_N                      : Mezzanine to carrier clocks.
- DPn_C2M_P/DPn_C2M_N, DPn_M2C_P/DPn_M2C_N   : Transceiver lanes.
- GBTCLKn_M2C_P/GBTCLKn_M2C_N                : Transceiver reference clocks.

Only the signals routed on the board are present. Some boards use other keys (ex: LA00_P_CC on
xilinx_kcu116/efinix_tz170_j484_dev_kit, LA0_P on berkeleylab_marble, LA00_P on
berkeleylab_marblemini/numato_nereid, CLK0_P on alinx_axau15/lattice_crosslink_nx_evn,
GBTCLK0_M2C_C_P on xilinx_zc706/altera_agilex5e_065b_premium_devkit): modules using these signals
will not resolve on these boards until they expose canonical keys.

Usage:

    from litex_boards.extensions.fmc import FMCRAID
    platform.add_extension(FMCRAID("LPC"))
    sata_pads = platform.request("fmc2sata")
"""

from litex.build.generic_platform import Pins, Subsignal
from litex.build.extension import Extension

# FMC Extension ------------------------------------------------------------------------------------

class FMCExtension(Extension):
    slots          = {"fmc": None}
    connector_type = "fmc"

# SATA ---------------------------------------------------------------------------------------------

class FMCRAID(FMCExtension):
    """Design Gateway AB09-FMCRAID SATA FMC (first SATA port, on DP0 / GBTCLK0).

    https://www.dgway.com/AB09-FMCRAID_E.html
    """
    def define_io(self, platform):
        return [
            ("fmc2sata", 0,
                Subsignal("clk_p", Pins("fmc:GBTCLK0_M2C_P")),
                Subsignal("clk_n", Pins("fmc:GBTCLK0_M2C_N")),
                Subsignal("tx_p",  Pins("fmc:DP0_C2M_P")),
                Subsignal("tx_n",  Pins("fmc:DP0_C2M_N")),
                Subsignal("rx_p",  Pins("fmc:DP0_M2C_P")),
                Subsignal("rx_n",  Pins("fmc:DP0_M2C_N"))
            ),
        ]
